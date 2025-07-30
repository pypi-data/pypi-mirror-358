"""Tests for errors module."""

import json
import pytest
from unittest.mock import Mock, patch, MagicMock
from quarkle_monitoring.errors import ErrorTracker, track_errors
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

    def test_track_error_non_4xx(self, error_tracker):
        """Test ignoring non-4xx errors."""
        should_alert, error_data = error_tracker.track_error(500, "/api/test")
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

    def test_track_error_stores_correct_data(self, error_tracker):
        """Test that error data is stored correctly."""
        with patch("time.time", return_value=1640995200.0):
            error_tracker.track_error(404, "/api/test", "user123", {"key": "value"})

        # Verify set was called with correct data structure
        error_tracker.cache.set.assert_called_once()
        call_args = error_tracker.cache.set.call_args[0]

        # First arg should be key starting with "error_detail:"
        assert call_args[0].startswith("error_detail:")

        # Second arg should be JSON with error data
        error_data = json.loads(call_args[1])
        assert error_data["service"] == "test-service"
        assert error_data["error_code"] == 404
        assert error_data["endpoint"] == "/api/test"
        assert error_data["user_id"] == "user123"
        assert error_data["git_hash"] == "abc123"
        assert error_data["timestamp"] == 1640995200.0
        assert error_data["extra"] == {"key": "value"}


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
        """Test decorator with non-4xx exception."""

        @track_errors(mock_tracker)
        def test_function():
            error = Exception("Server error")
            error.status_code = 500
            raise error

        with pytest.raises(Exception, match="Server error"):
            test_function()

        mock_tracker.track_error.assert_not_called()

    def test_decorator_exception_no_status(self, mock_tracker):
        """Test decorator with exception that has no status_code."""

        @track_errors(mock_tracker)
        def test_function():
            raise ValueError("Some error")

        with pytest.raises(ValueError, match="Some error"):
            test_function()

        mock_tracker.track_error.assert_not_called()
