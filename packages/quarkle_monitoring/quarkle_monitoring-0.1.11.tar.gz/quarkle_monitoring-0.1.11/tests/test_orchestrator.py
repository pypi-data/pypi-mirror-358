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

    def test_track_web_error_basic(self):
        """Test basic web error tracking."""
        with patch.object(ErrorTracker, "_get_version_info", return_value="abc123"):
            monitoring = QuarkleMonitoring(use_redis=False)
            monitoring.track_error = Mock(return_value=(True, {"error": "test"}))

            # Mock request and response with proper dict-like behavior
            request = Mock()
            request.method = "GET"
            request.path = "/api/test"
            request.args = {"param": "value"}  # Real dict, not Mock

            response = Mock()
            response.status_code = 404
            response.is_json.return_value = True
            response.get_json.return_value = {"message": "Not found"}
            response.get_data.return_value = b"Not found"

            # Mock user_id getter
            def get_user_id():
                return "user123"

            should_alert, error_data = monitoring.track_web_error(
                response=response,
                request=request,
                user_id_getter=get_user_id,
                extra_context={"custom": "data"},
            )

            assert should_alert is True
            assert error_data == {"error": "test"}

            # Verify track_error was called with correct parameters
            monitoring.track_error.assert_called_once()
            call_args = monitoring.track_error.call_args[1]
            assert call_args["error_code"] == 404
            assert call_args["endpoint"] == "GET /api/test"
            assert call_args["user_id"] == "user123"
            assert call_args["error_message"] == "Not found"
            assert call_args["extra"]["source"] == "web_middleware"
            assert call_args["extra"]["custom"] == "data"

    def test_track_web_error_non_error_status(self):
        """Test that non-error status codes are ignored."""
        with patch.object(ErrorTracker, "_get_version_info", return_value="abc123"):
            monitoring = QuarkleMonitoring(use_redis=False)

            request = Mock()
            response = Mock()
            response.status_code = 200  # Success status

            should_alert, error_data = monitoring.track_web_error(
                response=response, request=request
            )

            assert should_alert is False
            assert error_data == {}

    def test_track_web_error_user_id_getter_exception(self):
        """Test handling of user_id_getter exceptions."""
        with patch.object(ErrorTracker, "_get_version_info", return_value="abc123"):
            monitoring = QuarkleMonitoring(use_redis=False)
            monitoring.track_error = Mock(return_value=(True, {"error": "test"}))

            request = Mock()
            request.method = "POST"
            request.path = "/api/fail"
            request.args = {}  # Real dict, not Mock

            response = Mock()
            response.status_code = 500
            response.is_json.return_value = False
            response.get_data.return_value = "Server error"

            def failing_user_getter():
                raise Exception("User context error")

            should_alert, error_data = monitoring.track_web_error(
                response=response, request=request, user_id_getter=failing_user_getter
            )

            assert should_alert is True
            # Should still work even if user_id getter fails
            call_args = monitoring.track_error.call_args[1]
            assert call_args["user_id"] is None

    def test_setup_auto_tracking(self):
        """Test setup_auto_tracking method."""
        with patch.object(ErrorTracker, "_get_version_info", return_value="abc123"):
            monitoring = QuarkleMonitoring(use_redis=False)

            with patch(
                "quarkle_monitoring.orchestrator.auto_wrap_modules"
            ) as mock_wrap:
                mock_wrap.return_value = 5

                def mock_context():
                    return {"user_id": "test123"}

                result = monitoring.setup_auto_tracking(
                    module_names=["module1", "module2"], context_getter=mock_context
                )

                assert result == 5
                mock_wrap.assert_called_once()
                call_args = mock_wrap.call_args
                assert call_args[1]["module_names"] == ["module1", "module2"]
                assert call_args[1]["context_getter"] == mock_context

    def test_create_with_common_web_filters(self):
        """Test factory method with common web filters."""
        with patch.object(ErrorTracker, "_get_version_info", return_value="abc123"):
            monitoring = QuarkleMonitoring.create_with_common_web_filters(
                stage="test",
                service_name="test-service",
                additional_ignored_endpoints=["/custom/endpoint"],
                additional_ignored_codes=[418],
                use_redis=False,
            )

            # Check that common filters were applied
            error_codes = monitoring.error_tracker.ignored_error_codes
            assert 401 in error_codes  # From COMMON_BOT_ERROR_CODES
            assert 418 in error_codes  # Additional code

            endpoints = monitoring.error_tracker.ignored_endpoints
            assert "/health*" in endpoints  # From COMMON_BOT_ENDPOINTS
            assert "/custom/endpoint" in endpoints  # Additional endpoint

    def test_create_with_common_web_filters_no_additional(self):
        """Test factory method without additional filters."""
        with patch.object(ErrorTracker, "_get_version_info", return_value="abc123"):
            monitoring = QuarkleMonitoring.create_with_common_web_filters(
                service_name="test-service", use_redis=False
            )

            # Should only have common filters
            error_codes = monitoring.error_tracker.ignored_error_codes
            assert 401 in error_codes
            assert 405 in error_codes

            endpoints = monitoring.error_tracker.ignored_endpoints
            assert "/health*" in endpoints
            assert "/wp-admin/*" in endpoints

    def test_tracked_endpoints_whitelist_basic(self):
        """Test basic endpoint whitelisting functionality."""
        with patch.object(ErrorTracker, "_get_version_info", return_value="abc123"):
            monitoring = QuarkleMonitoring(
                use_redis=False,
                tracked_endpoints=["/api/users/*", "/api/orders", "POST /api/books"],
            )
            # Don't mock error_tracker - use the real one so filtering logic runs

            # Should track matching endpoints
            should_alert, error_data = monitoring.track_error(
                error_code=404, endpoint="/api/users/123"
            )
            assert should_alert is True
            assert error_data != {}

            # Should not track non-matching endpoints
            should_alert, error_data = monitoring.track_error(
                error_code=404, endpoint="/api/posts/123"
            )
            assert should_alert is False
            assert error_data == {}

    def test_tracked_endpoints_wildcard_patterns(self):
        """Test wildcard patterns work correctly."""
        with patch.object(ErrorTracker, "_get_version_info", return_value="abc123"):
            monitoring = QuarkleMonitoring(
                use_redis=False, tracked_endpoints=["*/api/v1/*", "GET /admin*"]
            )
            # Don't mock error_tracker - use the real one so filtering logic runs

            # Should match wildcard
            should_alert, _ = monitoring.track_error(404, "POST /api/v1/users")
            assert should_alert is True

            # Should match method-specific pattern
            should_alert, _ = monitoring.track_error(403, "GET /admin/settings")
            assert should_alert is True

            # Should not match different method
            should_alert, _ = monitoring.track_error(403, "POST /admin/settings")
            assert should_alert is False

    def test_no_tracked_endpoints_allows_all(self):
        """Test that no tracked_endpoints means track all (default behavior)."""
        with patch.object(ErrorTracker, "_get_version_info", return_value="abc123"):
            monitoring = QuarkleMonitoring(use_redis=False)
            # Don't mock error_tracker - use the real one

            # Should track any endpoint when no whitelist
            should_alert, _ = monitoring.track_error(404, "/any/endpoint")
            assert should_alert is True

    def test_create_with_tracked_endpoints_factory(self):
        """Test the factory method for tracked endpoints."""
        with patch.object(ErrorTracker, "_get_version_info", return_value="abc123"):
            monitoring = QuarkleMonitoring.create_with_tracked_endpoints(
                tracked_endpoints=["/api/*"],
                service_name="test-service",
                use_redis=False,
            )

            # tracked_endpoints should be accessible via the error_tracker
            assert monitoring.tracked_endpoints == ["/api/*"]
            assert monitoring.service_name == "test-service"

            # Should have common bot error codes
            assert 401 in monitoring.error_tracker.ignored_error_codes

    def test_track_web_error_respects_tracked_endpoints(self):
        """Test that track_web_error respects tracked_endpoints."""
        with patch.object(ErrorTracker, "_get_version_info", return_value="abc123"):
            monitoring = QuarkleMonitoring(
                use_redis=False,
                tracked_endpoints=["* /api/*"],  # Match any method + /api/* path
            )

            # Mock request and response
            request = Mock()
            request.method = "GET"
            request.path = "/api/users"
            request.args = {}

            response = Mock()
            response.status_code = 404
            response.is_json.return_value = True
            response.get_json.return_value = {"message": "Not found"}
            response.get_data.return_value = b"Not found"

            # Should track because matches whitelist (GET /api/users matches * /api/*)
            should_alert, error_data = monitoring.track_web_error(
                response=response,
                request=request,
            )
            assert should_alert is True

            # Should not track because doesn't match whitelist
            request.path = "/health"
            should_alert, error_data = monitoring.track_web_error(
                response=response,
                request=request,
            )
            assert should_alert is False
            assert error_data == {}

            # Should track POST because * /api/* matches any method
            request.method = "POST"
            request.path = "/api/users"
            should_alert, error_data = monitoring.track_web_error(
                response=response,
                request=request,
            )
            assert should_alert is True

    def test_tracked_endpoints_with_ignored_error_codes(self):
        """Test that tracked_endpoints works with ignored_error_codes."""
        with patch.object(ErrorTracker, "_get_version_info", return_value="abc123"):
            monitoring = QuarkleMonitoring(
                use_redis=False,
                tracked_endpoints=["/api/*"],  # Whitelist API endpoints
                ignored_error_codes=[403],  # But ignore 403 errors
            )

            # Should track 404 on whitelisted endpoint
            should_alert, error_data = monitoring.track_error(
                error_code=404, endpoint="/api/users"
            )
            assert should_alert is True
            assert error_data != {}

            # Should not track 403 on whitelisted endpoint (error code ignored)
            should_alert, error_data = monitoring.track_error(
                error_code=403, endpoint="/api/users"
            )
            assert should_alert is False
            assert error_data == {}

            # Should not track 404 on non-whitelisted endpoint
            should_alert, error_data = monitoring.track_error(
                error_code=404, endpoint="/health"
            )
            assert should_alert is False
            assert error_data == {}
