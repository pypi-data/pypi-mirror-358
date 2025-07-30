"""Tests for errors module."""

import json
import pytest
from unittest.mock import Mock, patch, MagicMock
from quarkle_monitoring.errors import ErrorTracker, track_errors, MemoryCache
from quarkle_monitoring.cache import QuarkleCache


class TestErrorTracker:
    """Test ErrorTracker functionality."""

    @pytest.fixture
    def mock_cache(self):
        """Mock cache for testing."""
        cache = Mock(spec=QuarkleCache)
        cache.rate_limit.return_value = True
        cache.set.return_value = True
        return cache

    @pytest.fixture
    def error_tracker(self, mock_cache):
        """Create ErrorTracker instance."""
        with patch.object(ErrorTracker, "_get_version_info", return_value="abc123"):
            return ErrorTracker(mock_cache, "test-service")

    def test_init(self, mock_cache):
        """Test ErrorTracker initialization."""
        with patch.object(ErrorTracker, "_get_version_info", return_value="abc123"):
            tracker = ErrorTracker(mock_cache, "test-service")
            assert tracker.cache is mock_cache
            assert tracker.service_name == "test-service"
            assert tracker._git_hash == "abc123"

    def test_get_version_info_from_env_vars(self, mock_cache):
        """Test version info retrieval from environment variables."""
        # Test APP_VERSION
        with patch.dict("os.environ", {"APP_VERSION": "v1.2.3"}, clear=True):
            tracker = ErrorTracker(mock_cache)
            assert tracker._git_hash == "v1.2.3"

        # Test GIT_HASH
        with patch.dict("os.environ", {"GIT_HASH": "abc123def"}, clear=True):
            tracker = ErrorTracker(mock_cache)
            assert tracker._git_hash == "abc123def"

        # Test BUILD_ID
        with patch.dict("os.environ", {"BUILD_ID": "build456"}, clear=True):
            tracker = ErrorTracker(mock_cache)
            assert tracker._git_hash == "build456"

    def test_get_version_info_priority_order(self, mock_cache):
        """Test that APP_VERSION has priority over other env vars."""
        with patch.dict(
            "os.environ",
            {"APP_VERSION": "v1.0.0", "GIT_HASH": "abc123", "BUILD_ID": "build456"},
            clear=True,
        ):
            tracker = ErrorTracker(mock_cache)
            assert tracker._git_hash == "v1.0.0"

    def test_get_version_info_no_env_vars(self, mock_cache):
        """Test version info with no environment variables."""
        with patch.dict("os.environ", {}, clear=True):
            tracker = ErrorTracker(mock_cache)
            assert tracker._git_hash == "unknown"

    def test_get_version_info_truncation(self, mock_cache):
        """Test that version info is truncated to 12 characters."""
        with patch.dict(
            "os.environ", {"APP_VERSION": "very_long_version_string"}, clear=True
        ):
            tracker = ErrorTracker(mock_cache)
            assert tracker._git_hash == "very_long_ve"
            assert len(tracker._git_hash) == 12

    def test_get_call_context(self, error_tracker):
        """Test call context extraction."""

        def test_function():
            return error_tracker._get_call_context()

        context = test_function()
        assert "function" in context
        assert "file" in context
        assert "line" in context
        assert context["function"] == "test_function"

        # Test new stack trace functionality
        assert "stack_trace" in context
        assert isinstance(context["stack_trace"], list)
        assert len(context["stack_trace"]) > 0
        # Should contain the current function in the stack trace
        assert any(
            "test_function" in trace_entry for trace_entry in context["stack_trace"]
        )

    def test_track_error_4xx(self, error_tracker):
        """Test tracking 4xx errors."""
        should_alert, error_data = error_tracker.track_error(
            404, "/api/test", "user123", {"extra": "data"}
        )

        assert should_alert is True
        assert isinstance(error_data, dict)
        assert error_data["error_code"] == 404
        error_tracker.cache.rate_limit.assert_called_once()
        error_tracker.cache.set.assert_called_once()

    def test_track_error_5xx(self):
        """Test tracking 5xx errors."""
        cache = MemoryCache()
        error_tracker = ErrorTracker(cache=cache, service_name="test-service")

        should_alert, error_data = error_tracker.track_error(500, "/api/test")
        assert should_alert is True
        assert error_data["error_code"] == 500
        assert error_data["endpoint"] == "/api/test"
        assert "error_hash" in error_data

        # Test rate limiting works for 5xx errors too
        should_alert, error_data = error_tracker.track_error(500, "/api/test")
        assert should_alert is False  # Rate limited
        assert error_data == {}

    def test_track_error_non_4xx_non_5xx(self, error_tracker):
        """Test ignoring non-4xx/5xx errors (like 200, 300)."""
        # 200 success - should not be tracked
        should_alert, error_data = error_tracker.track_error(200, "/api/test")
        assert should_alert is False
        assert error_data == {}

        # 300 redirect - should not be tracked
        should_alert, error_data = error_tracker.track_error(301, "/api/test")
        assert should_alert is False
        assert error_data == {}

        should_alert, error_data = error_tracker.track_error(200, "/api/test")
        assert should_alert is False
        assert error_data == {}

        error_tracker.cache.rate_limit.assert_not_called()

    def test_track_error_rate_limited(self, error_tracker):
        """Test rate limited error tracking."""
        error_tracker.cache.rate_limit.return_value = False

        should_alert, error_data = error_tracker.track_error(404, "/api/test")
        assert should_alert is False
        assert error_data == {}
        error_tracker.cache.set.assert_not_called()

    def test_track_error_stores_correct_data(self):
        """Test that track_error stores all expected data."""
        cache = MemoryCache()
        error_tracker = ErrorTracker(cache=cache, service_name="test-service")

        should_alert, error_data = error_tracker.track_error(
            error_code=404,
            endpoint="/api/test",
            user_id="user123",
            extra={"custom": "data"},
            error_message="Test error message",
        )

        assert should_alert is True
        assert error_data["service"] == "test-service"
        assert error_data["error_code"] == 404
        assert error_data["endpoint"] == "/api/test"
        assert error_data["user_id"] == "user123"
        assert error_data["error_message"] == "Test error message"
        assert error_data["extra"] == {"custom": "data"}
        assert "error_hash" in error_data
        assert "timestamp" in error_data

    def test_track_error_with_different_messages_same_signature(self):
        """Test that errors with different messages are grouped together (same rate limiting signature)."""
        cache = MemoryCache()
        error_tracker = ErrorTracker(cache=cache, service_name="test-service")

        # First error
        should_alert1, error_data1 = error_tracker.track_error(
            error_code=404,
            endpoint="/api/users",
            error_message="User 123 not found",
        )

        # Second error with different message but same endpoint/error_code
        should_alert2, error_data2 = error_tracker.track_error(
            error_code=404,
            endpoint="/api/users",
            error_message="User 456 not found",
        )

        assert should_alert1 is True  # First error should alert
        assert (
            should_alert2 is False
        )  # Second error should be rate limited (same signature)

        # When rate limited, second error returns empty dict
        assert error_data1 != {}  # First has data
        assert error_data2 == {}  # Second is empty (rate limited)

        # The first error has all the data
        assert error_data1["error_message"] == "User 123 not found"
        assert error_data1["error_code"] == 404
        assert error_data1["endpoint"] == "/api/users"
        assert "error_hash" in error_data1

    def test_ignore_error_codes_exact_match(self):
        """Test ignoring specific error codes."""
        cache = MemoryCache()
        error_tracker = ErrorTracker(
            cache=cache, service_name="test-service", ignored_error_codes=[404, 403]
        )

        # 404 should be ignored
        should_alert, error_data = error_tracker.track_error(
            error_code=404,
            endpoint="/api/users",
        )
        assert should_alert is False
        assert error_data == {}

        # 403 should be ignored
        should_alert, error_data = error_tracker.track_error(
            error_code=403,
            endpoint="/api/users",
        )
        assert should_alert is False
        assert error_data == {}

        # 400 should not be ignored
        should_alert, error_data = error_tracker.track_error(
            error_code=400,
            endpoint="/api/users",
        )
        assert should_alert is True
        assert error_data != {}

    def test_ignore_error_codes_wildcard(self):
        """Test ignoring error codes with wildcards."""
        cache = MemoryCache()
        error_tracker = ErrorTracker(
            cache=cache,
            service_name="test-service",
            ignored_error_codes=["4*"],  # Ignore all 4xx errors
        )

        # All 4xx should be ignored
        for code in [400, 401, 403, 404, 422, 429]:
            should_alert, error_data = error_tracker.track_error(
                error_code=code,
                endpoint="/api/test",
            )
            assert should_alert is False, f"Error code {code} should be ignored"
            assert error_data == {}

        # 5xx should not be ignored and should be tracked now
        should_alert, error_data = error_tracker.track_error(
            error_code=500,
            endpoint="/api/test",
        )
        assert should_alert is True  # 5xx errors are now tracked
        assert error_data != {}  # Should have error data

    def test_ignore_endpoints(self):
        """Test ignoring specific endpoints."""
        cache = MemoryCache()
        error_tracker = ErrorTracker(
            cache=cache,
            service_name="test-service",
            ignored_endpoints=["/health", "/metrics", "/internal/*"],
        )

        # Exact matches should be ignored
        should_alert, error_data = error_tracker.track_error(
            error_code=404,
            endpoint="/health",
        )
        assert should_alert is False
        assert error_data == {}

        should_alert, error_data = error_tracker.track_error(
            error_code=404,
            endpoint="/metrics",
        )
        assert should_alert is False
        assert error_data == {}

        # Wildcard matches should be ignored
        should_alert, error_data = error_tracker.track_error(
            error_code=404,
            endpoint="/internal/status",
        )
        assert should_alert is False
        assert error_data == {}

        should_alert, error_data = error_tracker.track_error(
            error_code=404,
            endpoint="/internal/debug/info",
        )
        assert should_alert is False
        assert error_data == {}

        # Other endpoints should not be ignored
        should_alert, error_data = error_tracker.track_error(
            error_code=404,
            endpoint="/api/users",
        )
        assert should_alert is True
        assert error_data != {}

    def test_ignore_files(self):
        """Test ignoring errors from specific files."""
        cache = MemoryCache()
        error_tracker = ErrorTracker(
            cache=cache,
            service_name="test-service",
            ignored_files=["health_check.py", "*_test.py", "test_*.py"],
        )

        # Mock the context to return specific files
        def mock_get_call_context_with_file(filename):
            return {
                "function": "test_function",
                "file": filename,
                "line": 42,
                "stack_trace": [f"{filename}:test_function:42"],
            }

        # Test exact file match
        error_tracker._get_call_context = lambda: mock_get_call_context_with_file(
            "health_check.py"
        )
        should_alert, error_data = error_tracker.track_error(
            error_code=404,
            endpoint="/api/test",
        )
        assert should_alert is False
        assert error_data == {}

        # Test wildcard matches
        error_tracker._get_call_context = lambda: mock_get_call_context_with_file(
            "user_test.py"
        )
        should_alert, error_data = error_tracker.track_error(
            error_code=404,
            endpoint="/api/test",
        )
        assert should_alert is False
        assert error_data == {}

        error_tracker._get_call_context = lambda: mock_get_call_context_with_file(
            "test_utils.py"
        )
        should_alert, error_data = error_tracker.track_error(
            error_code=404,
            endpoint="/api/test",
        )
        assert should_alert is False
        assert error_data == {}

        # Test non-matching file
        error_tracker._get_call_context = lambda: mock_get_call_context_with_file(
            "main.py"
        )
        should_alert, error_data = error_tracker.track_error(
            error_code=404,
            endpoint="/api/test",
        )
        assert should_alert is True
        assert error_data != {}

    def test_combined_filters(self):
        """Test that all filters work together."""
        cache = MemoryCache()
        error_tracker = ErrorTracker(
            cache=cache,
            service_name="test-service",
            ignored_error_codes=[403],
            ignored_files=["*_test.py"],
            ignored_endpoints=["/health*"],
        )

        # Should be ignored due to error code
        should_alert, error_data = error_tracker.track_error(
            error_code=403,
            endpoint="/api/users",
        )
        assert should_alert is False

        # Should be ignored due to endpoint
        should_alert, error_data = error_tracker.track_error(
            error_code=404,
            endpoint="/health/check",
        )
        assert should_alert is False

        # Mock file context for file-based filtering
        error_tracker._get_call_context = lambda: {
            "function": "test_function",
            "file": "user_test.py",
            "line": 42,
            "stack_trace": ["user_test.py:test_function:42"],
        }

        # Should be ignored due to file
        should_alert, error_data = error_tracker.track_error(
            error_code=404,
            endpoint="/api/users",
        )
        assert should_alert is False

        # Reset context and test non-filtered error
        error_tracker._get_call_context = lambda: {
            "function": "api_function",
            "file": "main.py",
            "line": 42,
            "stack_trace": ["main.py:api_function:42"],
        }

        # Should not be ignored
        should_alert, error_data = error_tracker.track_error(
            error_code=404,
            endpoint="/api/users",
        )
        assert should_alert is True
        assert error_data != {}


class TestTrackErrorsDecorator:
    """Test the track_errors decorator."""

    @pytest.fixture
    def mock_tracker(self):
        """Mock error tracker."""
        tracker = Mock(spec=ErrorTracker)
        tracker.track_error.return_value = (True, {"error": "data"})
        return tracker

    def test_decorator_success(self, mock_tracker):
        """Test decorator with successful function execution."""

        @track_errors(mock_tracker)
        def test_function():
            return "success"

        result = test_function()
        assert result == "success"
        mock_tracker.track_error.assert_not_called()

    def test_decorator_4xx_exception(self, mock_tracker):
        """Test decorator with 4xx exception."""

        @track_errors(mock_tracker)
        def test_function():
            error = Exception("Test error")
            error.status_code = 404
            raise error

        with pytest.raises(Exception, match="Test error"):
            test_function()

        mock_tracker.track_error.assert_called_once_with(
            404, endpoint="test_function", extra={"exception": "Test error"}
        )

    def test_decorator_non_4xx_exception(self, mock_tracker):
        """Test decorator with 5xx exception."""

        @track_errors(mock_tracker)
        def test_function():
            error = Exception("Server error")
            error.status_code = 500
            raise error

        with pytest.raises(Exception, match="Server error"):
            test_function()

        mock_tracker.track_error.assert_called_once_with(
            500, endpoint="test_function", extra={"exception": "Server error"}
        )

    def test_decorator_exception_no_status(self, mock_tracker):
        """Test decorator with exception that has no status_code (defaults to 500)."""

        @track_errors(mock_tracker)
        def test_function():
            raise ValueError("Some error")

        with pytest.raises(ValueError, match="Some error"):
            test_function()

        mock_tracker.track_error.assert_called_once_with(
            500, endpoint="test_function", extra={"exception": "Some error"}
        )


class TestMemoryCache:
    """Test MemoryCache functionality."""

    def test_delete_existing_key(self):
        """Test deleting an existing key."""
        from quarkle_monitoring.errors import MemoryCache

        cache = MemoryCache()
        cache.set("test_key", "test_value", 3600)

        result = cache.delete("test_key")
        assert result is True
        assert "test_key" not in cache._data
        assert "test_key" not in cache._expiry

    def test_delete_non_existing_key(self):
        """Test deleting a non-existing key."""
        from quarkle_monitoring.errors import MemoryCache

        cache = MemoryCache()

        result = cache.delete("non_existing_key")
        assert result is False

    def test_delete_removes_expiry(self):
        """Test that delete removes both data and expiry entries."""
        from quarkle_monitoring.errors import MemoryCache

        cache = MemoryCache()
        cache.set("test_key", "test_value", 3600)

        # Verify the key exists before deletion
        assert "test_key" in cache._data
        assert "test_key" in cache._expiry

        cache.delete("test_key")

        # Verify both data and expiry are removed
        assert "test_key" not in cache._data
        assert "test_key" not in cache._expiry
