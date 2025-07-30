"""Tests for orchestrator module."""

import pytest
from unittest.mock import Mock, patch
from quarkle_monitoring.orchestrator import QuarkleMonitoring
from quarkle_monitoring.cache import QuarkleCache
from quarkle_monitoring.errors import ErrorTracker, MemoryCache
from quarkle_monitoring.notifications import SlackNotifier


class TestQuarkleMonitoring:
    """Test QuarkleMonitoring orchestrator."""

    def test_init_with_redis(self):
        """Test initialization with Redis cache."""
        with patch.object(QuarkleCache, "_connect"), patch.object(
            ErrorTracker, "_get_version_info", return_value="abc123"
        ):

            monitoring = QuarkleMonitoring(
                stage="test",
                service_name="test-service",
                slack_token="test-token",
                slack_channel="test-channel",
                use_redis=True,
            )

            assert isinstance(monitoring.cache, QuarkleCache)
            assert isinstance(monitoring.error_tracker, ErrorTracker)
            assert isinstance(monitoring.slack, SlackNotifier)
            assert monitoring.service_name == "test-service"

    def test_init_with_memory_cache(self):
        """Test initialization with in-memory cache."""
        with patch.object(ErrorTracker, "_get_version_info", return_value="abc123"):

            monitoring = QuarkleMonitoring(
                service_name="test-service",
                use_redis=False,
            )

            assert isinstance(monitoring.cache, MemoryCache)
            assert isinstance(monitoring.error_tracker, ErrorTracker)
            assert isinstance(monitoring.slack, SlackNotifier)

    def test_track_error_with_slack_alert(self):
        """Test error tracking with Slack alert."""
        with patch.object(ErrorTracker, "_get_version_info", return_value="abc123"):

            monitoring = QuarkleMonitoring(use_redis=False)
            monitoring.error_tracker = Mock()
            monitoring.slack = Mock()

            # Mock successful error tracking
            error_data = {"error_code": 404, "service": "test"}
            monitoring.error_tracker.track_error.return_value = (True, error_data)
            monitoring.slack.send_error_alert.return_value = True

            should_alert, returned_error_data = monitoring.track_error(
                error_code=404,
                endpoint="/api/test",
                user_id="123",
                extra={"key": "value"},
                send_slack_alert=True,
            )

            assert should_alert is True
            assert returned_error_data == error_data
            monitoring.error_tracker.track_error.assert_called_once_with(
                error_code=404,
                endpoint="/api/test",
                user_id="123",
                extra={"key": "value"},
                error_message=None,
                request_data=None,
            )
            monitoring.slack.send_error_alert.assert_called_once_with(error_data)

    def test_track_error_no_slack_alert(self):
        """Test error tracking without Slack alert."""
        with patch.object(ErrorTracker, "_get_version_info", return_value="abc123"):

            monitoring = QuarkleMonitoring(use_redis=False)
            monitoring.error_tracker = Mock()
            monitoring.slack = Mock()

            error_data = {"error_code": 404, "service": "test"}
            monitoring.error_tracker.track_error.return_value = (True, error_data)

            should_alert, returned_error_data = monitoring.track_error(
                error_code=404,
                send_slack_alert=False,
            )

            assert should_alert is True
            assert returned_error_data == error_data
            monitoring.slack.send_error_alert.assert_not_called()

    def test_track_error_rate_limited(self):
        """Test error tracking when rate limited."""
        with patch.object(ErrorTracker, "_get_version_info", return_value="abc123"):

            monitoring = QuarkleMonitoring(use_redis=False)
            monitoring.error_tracker = Mock()
            monitoring.slack = Mock()

            # Mock rate limited error tracking
            monitoring.error_tracker.track_error.return_value = (False, {})

            should_alert, returned_error_data = monitoring.track_error(error_code=404)

            assert should_alert is False
            assert returned_error_data == {}
            monitoring.slack.send_error_alert.assert_not_called()

    def test_send_lifecycle_alert(self):
        """Test sending lifecycle alert."""
        with patch.object(ErrorTracker, "_get_version_info", return_value="abc123"):

            monitoring = QuarkleMonitoring(service_name="test-service", use_redis=False)
            monitoring.slack = Mock()
            monitoring.slack.send_lifecycle_alert.return_value = True

            result = monitoring.send_lifecycle_alert("startup", "abc123")

            assert result is True
            monitoring.slack.send_lifecycle_alert.assert_called_once_with(
                service="test-service",
                event="startup",
                git_hash="abc123",
            )

    def test_track_errors_decorator(self):
        """Test the track_errors decorator."""
        with patch.object(ErrorTracker, "_get_version_info", return_value="abc123"):

            monitoring = QuarkleMonitoring(use_redis=False)
            monitoring.track_error = Mock(return_value=(True, {"error": "test"}))

            @monitoring.track_errors_decorator(send_slack_alert=False)
            def test_function():
                error = Exception("Test error")
                error.status_code = 404
                raise error

            with pytest.raises(Exception, match="Test error"):
                test_function()

            monitoring.track_error.assert_called_once_with(
                error_code=404,
                endpoint="test_function",
                error_message="Test error",
                extra={"exception": "Test error", "exception_type": "Exception"},
                send_slack_alert=False,
            )

    def test_track_errors_decorator_success(self):
        """Test the track_errors decorator with successful execution."""
        with patch.object(ErrorTracker, "_get_version_info", return_value="abc123"):

            monitoring = QuarkleMonitoring(use_redis=False)
            monitoring.track_error = Mock()

            @monitoring.track_errors_decorator()
            def test_function():
                return "success"

            result = test_function()

            assert result == "success"
            monitoring.track_error.assert_not_called()

    def test_property_access(self):
        """Test access to individual components via properties."""
        with patch.object(QuarkleCache, "_connect"), patch.object(
            ErrorTracker, "_get_version_info", return_value="abc123"
        ):

            monitoring = QuarkleMonitoring(use_redis=True)

            assert monitoring.cache_client is monitoring.cache
            assert monitoring.error_client is monitoring.error_tracker
            assert monitoring.slack_client is monitoring.slack

    def test_send_lifecycle_alert_prevents_duplicates(self):
        """Test lifecycle alert caching prevents duplicates."""
        with patch.object(ErrorTracker, "_get_version_info", return_value="abc123"):
            monitoring = QuarkleMonitoring(service_name="test-service", use_redis=False)
            monitoring.cache = Mock()
            monitoring.slack = Mock()

            # First call allowed
            monitoring.cache.rate_limit.return_value = True
            monitoring.slack.send_lifecycle_alert.return_value = True

            result1 = monitoring.send_lifecycle_alert("startup", "v1.2.3")
            assert result1 is True

            # Second call blocked by cache
            monitoring.cache.rate_limit.return_value = False
            result2 = monitoring.send_lifecycle_alert("startup", "v1.2.3")
            assert result2 is False

            # Verify cache key format
            monitoring.cache.rate_limit.assert_called_with(
                "lifecycle:test-service:startup:v1.2.3", limit=1, window=300
            )

    def test_send_lifecycle_alert_with_custom_ttl(self):
        """Test lifecycle alert with custom cache TTL."""
        with patch.object(ErrorTracker, "_get_version_info", return_value="abc123"):
            monitoring = QuarkleMonitoring(service_name="test-service", use_redis=False)
            monitoring.cache = Mock()
            monitoring.slack = Mock()

            monitoring.cache.rate_limit.return_value = True
            monitoring.slack.send_lifecycle_alert.return_value = True

            monitoring.send_lifecycle_alert("startup", cache_ttl=600)

            # Verify custom TTL is used
            monitoring.cache.rate_limit.assert_called_with(
                "lifecycle:test-service:startup:abc123", limit=1, window=600
            )

    def test_send_lifecycle_alert_backwards_compatibility(self):
        """Test that existing lifecycle alert behavior still works."""
        with patch.object(ErrorTracker, "_get_version_info", return_value="abc123"):
            monitoring = QuarkleMonitoring(service_name="test-service", use_redis=False)
            monitoring.cache = Mock()
            monitoring.slack = Mock()

            monitoring.cache.rate_limit.return_value = True
            monitoring.slack.send_lifecycle_alert.return_value = True

            # Old way of calling should still work
            result = monitoring.send_lifecycle_alert("startup", "v1.2.3")

            assert result is True
            monitoring.slack.send_lifecycle_alert.assert_called_once_with(
                service="test-service", event="startup", git_hash="v1.2.3"
            )

    def test_init_with_filters(self):
        """Test QuarkleMonitoring initialization with error filters."""
        with patch.object(ErrorTracker, "_get_version_info", return_value="abc123"):
            monitoring = QuarkleMonitoring(
                service_name="test-service",
                use_redis=False,
                ignored_error_codes=[404, "4*"],
                ignored_files=["*_test.py", "health_check.py"],
                ignored_endpoints=["/health", "/metrics", "/internal/*"],
            )

            # Check that filters were passed to ErrorTracker
            assert monitoring.error_tracker.ignored_error_codes == [404, "4*"]
            assert monitoring.error_tracker.ignored_files == [
                "*_test.py",
                "health_check.py",
            ]
            assert monitoring.error_tracker.ignored_endpoints == [
                "/health",
                "/metrics",
                "/internal/*",
            ]
