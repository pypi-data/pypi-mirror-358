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
        with patch.object(ErrorTracker, "_get_git_hash", return_value="abc123"):
            return ErrorTracker(mock_cache, "test-service")

    def test_init(self, mock_cache):
        """Test ErrorTracker initialization."""
        with patch.object(ErrorTracker, "_get_git_hash", return_value="abc123"):
            tracker = ErrorTracker(mock_cache, "test-service")
            assert tracker.cache is mock_cache
            assert tracker.service_name == "test-service"
            assert tracker._git_hash == "abc123"

    def test_get_git_hash_success(self, mock_cache):
        """Test successful git hash retrieval."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "abc123def\n"

        with patch("subprocess.run", return_value=mock_result):
            tracker = ErrorTracker(mock_cache)
            assert tracker._git_hash == "abc123def"

    def test_get_git_hash_failure(self, mock_cache):
        """Test git hash fallback to environment variable."""
        with patch(
            "subprocess.run", side_effect=Exception("Git not found")
        ), patch.dict("os.environ", {"GIT_HASH": "env_hash"}):
            tracker = ErrorTracker(mock_cache)
            assert tracker._git_hash == "env_hash"

    def test_get_git_hash_no_fallback(self, mock_cache):
        """Test git hash with no fallback."""
        with patch(
            "subprocess.run", side_effect=Exception("Git not found")
        ), patch.dict("os.environ", {}, clear=True):
            tracker = ErrorTracker(mock_cache)
            assert tracker._git_hash == "unknown"

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
        result = error_tracker.track_error(
            404, "/api/test", "user123", {"extra": "data"}
        )

        assert result is True
        error_tracker.cache.rate_limit.assert_called_once()
        error_tracker.cache.set.assert_called_once()

    def test_track_error_non_4xx(self, error_tracker):
        """Test ignoring non-4xx errors."""
        result = error_tracker.track_error(500, "/api/test")
        assert result is False

        result = error_tracker.track_error(200, "/api/test")
        assert result is False

        error_tracker.cache.rate_limit.assert_not_called()

    def test_track_error_rate_limited(self, error_tracker):
        """Test rate limited error tracking."""
        error_tracker.cache.rate_limit.return_value = False

        result = error_tracker.track_error(404, "/api/test")
        assert result is False
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
        tracker.track_error.return_value = True
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
