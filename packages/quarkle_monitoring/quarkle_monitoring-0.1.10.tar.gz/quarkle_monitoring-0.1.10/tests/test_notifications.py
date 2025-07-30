"""Tests for notifications module."""

import pytest
from unittest.mock import Mock, patch
from quarkle_monitoring.notifications import SlackNotifier


class TestSlackNotifier:
    """Test SlackNotifier functionality."""

    def test_init_no_slack_sdk(self):
        """Test initialization when slack-sdk is not available."""
        with patch("quarkle_monitoring.notifications.SLACK_AVAILABLE", False):
            notifier = SlackNotifier()
            assert notifier.client is None

    def test_init_with_token(self, mock_slack_client):
        """Test initialization with explicit token."""
        with patch("quarkle_monitoring.notifications.WebClient") as mock_webclient:
            mock_webclient.return_value = mock_slack_client

            notifier = SlackNotifier(token="test-token", channel="test-channel")

            assert notifier.token == "test-token"
            assert notifier.channel == "test-channel"
            assert notifier.client is mock_slack_client
            mock_webclient.assert_called_once_with(token="test-token")

    def test_init_with_env_vars(self, mock_slack_client):
        """Test initialization with environment variables."""
        with patch(
            "quarkle_monitoring.notifications.WebClient"
        ) as mock_webclient, patch.dict(
            "os.environ",
            {"SLACK_APP_TOKEN": "env-token", "SLACK_ALERTS_CHANNEL": "env-channel"},
        ):
            mock_webclient.return_value = mock_slack_client

            notifier = SlackNotifier()

            assert notifier.token == "env-token"
            assert notifier.channel == "env-channel"
            mock_webclient.assert_called_once_with(token="env-token")

    def test_init_no_token(self):
        """Test initialization without token."""
        with patch("quarkle_monitoring.notifications.WebClient"), patch.dict(
            "os.environ", {}, clear=True
        ):
            notifier = SlackNotifier()
            assert notifier.client is None

    def test_send_error_alert_success(self, mock_slack_client, sample_error_data):
        """Test successful error alert sending."""
        with patch("quarkle_monitoring.notifications.WebClient") as mock_webclient:
            mock_webclient.return_value = mock_slack_client

            notifier = SlackNotifier(token="test-token")
            result = notifier.send_error_alert(sample_error_data)

            assert result is True
            mock_slack_client.chat_postMessage.assert_called_once()

            # Verify call arguments
            call_args = mock_slack_client.chat_postMessage.call_args
            assert call_args[1]["channel"] == "C072D4XPLJ0"  # Default channel
            assert "404 Error" in call_args[1]["text"]
            assert "test-service" in call_args[1]["text"]

    def test_send_error_alert_no_client(self, sample_error_data):
        """Test error alert when no client available."""
        notifier = SlackNotifier()
        notifier.client = None

        result = notifier.send_error_alert(sample_error_data)
        assert result is False

    def test_send_error_alert_exception(self, mock_slack_client, sample_error_data):
        """Test error alert with Slack API exception."""
        mock_slack_client.chat_postMessage.side_effect = Exception("Slack error")

        with patch("quarkle_monitoring.notifications.WebClient") as mock_webclient:
            mock_webclient.return_value = mock_slack_client

            notifier = SlackNotifier(token="test-token")
            result = notifier.send_error_alert(sample_error_data)

            assert result is False

    def test_send_lifecycle_alert_startup(self, mock_slack_client):
        """Test lifecycle alert for startup."""
        with patch("quarkle_monitoring.notifications.WebClient") as mock_webclient:
            mock_webclient.return_value = mock_slack_client

            notifier = SlackNotifier(token="test-token")
            result = notifier.send_lifecycle_alert("test-service", "startup", "abc123")

            assert result is True
            mock_slack_client.chat_postMessage.assert_called_once()

            call_args = mock_slack_client.chat_postMessage.call_args[1]
            assert "🟢" in call_args["text"]
            assert "Started" in call_args["text"]
            assert "test-service" in call_args["text"]
            assert "abc123" in call_args["text"]

    def test_send_lifecycle_alert_shutdown(self, mock_slack_client):
        """Test lifecycle alert for shutdown."""
        with patch("quarkle_monitoring.notifications.WebClient") as mock_webclient:
            mock_webclient.return_value = mock_slack_client

            notifier = SlackNotifier(token="test-token")
            result = notifier.send_lifecycle_alert("test-service", "shutdown", "abc123")

            assert result is True
            call_args = mock_slack_client.chat_postMessage.call_args[1]
            assert "🔴" in call_args["text"]
            assert "Stopped" in call_args["text"]

    def test_send_lifecycle_alert_no_client(self):
        """Test lifecycle alert when no client available."""
        notifier = SlackNotifier()
        notifier.client = None

        result = notifier.send_lifecycle_alert("test-service", "startup", "abc123")
        assert result is False


class TestEnhancedSlackNotifications:
    """Test enhanced Slack notification features."""

    def test_error_alert_with_error_message(self, mock_slack_client):
        """Test that error messages appear in the main notification text."""
        error_data = {
            "service": "backend-service",
            "error_code": 400,
            "error_message": "User not found with ID: 12345",
            "error_hash": "abc123",
            "context": {"function": "get_user", "file": "user_api.py", "line": 45},
            "endpoint": "GET /api/users/{id}",
            "git_hash": "test-abc",
            "timestamp": 1640995200.0,
        }

        with patch("quarkle_monitoring.notifications.WebClient") as mock_webclient:
            mock_webclient.return_value = mock_slack_client
            notifier = SlackNotifier(token="test-token")

            result = notifier.send_error_alert(error_data)

            assert result is True
            call_args = mock_slack_client.chat_postMessage.call_args[1]

            # Check that error message appears in main text
            assert "User not found with ID: 12345" in call_args["text"]
            assert "400 Error" in call_args["text"]

    def test_error_alert_with_business_logic_context(self, mock_slack_client):
        """Test that business logic context is properly displayed."""
        error_data = {
            "service": "backend-service",
            "error_code": 404,
            "error_message": "Resource not found",
            "error_hash": "def456",
            "endpoint": "GET /api/resources/{id}",
            "git_hash": "test-def",
            "timestamp": 1640995200.0,
            "extra": {
                "function": "get_resource",
                "business_logic_file": "resource_api.py",
                "exception_type": "ResourceNotFoundError",
            },
        }

        with patch("quarkle_monitoring.notifications.WebClient") as mock_webclient:
            mock_webclient.return_value = mock_slack_client
            notifier = SlackNotifier(token="test-token")

            result = notifier.send_error_alert(error_data)

            assert result is True
            call_args = mock_slack_client.chat_postMessage.call_args[1]

            # Check attachment fields
            fields = call_args["attachments"][0]["fields"]
            field_dict = {f["title"]: f["value"] for f in fields}

            assert "Function" in field_dict
            assert "🎯 `get_resource()`" in field_dict["Function"]
            assert "File" in field_dict
            assert "🎯 `resource_api.py`" in field_dict["File"]
            assert "Exception" in field_dict
            assert "`ResourceNotFoundError`" in field_dict["Exception"]

    def test_error_alert_without_business_logic_context(self, mock_slack_client):
        """Test error alert without business logic context (framework-level error)."""
        error_data = {
            "service": "backend-service",
            "error_code": 400,
            "error_message": "Invalid request",
            "error_hash": "ghi789",
            "endpoint": "POST /api/users",
            "git_hash": "test-ghi",
            "timestamp": 1640995200.0,
            # No extra field with business logic context
        }

        with patch("quarkle_monitoring.notifications.WebClient") as mock_webclient:
            mock_webclient.return_value = mock_slack_client
            notifier = SlackNotifier(token="test-token")

            result = notifier.send_error_alert(error_data)

            assert result is True
            call_args = mock_slack_client.chat_postMessage.call_args[1]

            # Check that essential fields are still present
            fields = call_args["attachments"][0]["fields"]
            field_titles = [f["title"] for f in fields]

            assert "Endpoint" in field_titles
            assert "Git Hash" in field_titles
            assert "Timestamp" in field_titles
            # But no business logic fields
            assert "Function" not in field_titles
            assert "File" not in field_titles

    def test_error_alert_with_user_id(self, mock_slack_client):
        """Test that user ID is displayed when present."""
        error_data = {
            "service": "backend-service",
            "error_code": 403,
            "error_message": "Access denied",
            "error_hash": "jkl012",
            "endpoint": "DELETE /api/resources/{id}",
            "user_id": "user_789",
            "git_hash": "test-jkl",
            "timestamp": 1640995200.0,
        }

        with patch("quarkle_monitoring.notifications.WebClient") as mock_webclient:
            mock_webclient.return_value = mock_slack_client
            notifier = SlackNotifier(token="test-token")

            result = notifier.send_error_alert(error_data)

            assert result is True
            call_args = mock_slack_client.chat_postMessage.call_args[1]

            # Check user ID field
            fields = call_args["attachments"][0]["fields"]
            user_field = next((f for f in fields if f["title"] == "User Id"), None)

            assert user_field is not None
            assert "`user_789`" in user_field["value"]

    def test_error_alert_staging_environment(self, mock_slack_client):
        """Test that staging environment is properly indicated."""
        error_data = {
            "service": "backend-service",
            "error_code": 500,
            "error_message": "Internal server error",
            "error_hash": "mno345",
            "endpoint": "POST /api/process",
            "git_hash": "staging-mno",
            "timestamp": 1640995200.0,
        }

        with patch("quarkle_monitoring.notifications.WebClient") as mock_webclient:
            mock_webclient.return_value = mock_slack_client
            notifier = SlackNotifier(token="test-token", stage="staging")

            result = notifier.send_error_alert(error_data)

            assert result is True
            call_args = mock_slack_client.chat_postMessage.call_args[1]

            # Check that staging is indicated in the message
            assert "[STAGING]" in call_args["text"]

    def test_error_alert_production_environment(self, mock_slack_client):
        """Test that production environment doesn't show stage suffix."""
        error_data = {
            "service": "backend-service",
            "error_code": 500,
            "error_message": "Internal server error",
            "error_hash": "pqr678",
            "endpoint": "POST /api/process",
            "git_hash": "prod-pqr",
            "timestamp": 1640995200.0,
        }

        with patch("quarkle_monitoring.notifications.WebClient") as mock_webclient:
            mock_webclient.return_value = mock_slack_client
            notifier = SlackNotifier(token="test-token", stage="production")

            result = notifier.send_error_alert(error_data)

            assert result is True
            call_args = mock_slack_client.chat_postMessage.call_args[1]

            # Check that no stage suffix appears for production
        assert "[PRODUCTION]" not in call_args["text"]
        assert "backend-service" in call_args["text"]
        assert "500 Error" in call_args["text"]

    def test_error_alert_long_message_truncation(self, mock_slack_client):
        """Test that very long error messages are truncated."""
        long_message = "Error details: " + "x" * 300  # Very long message

        error_data = {
            "service": "backend-service",
            "error_code": 400,
            "error_message": long_message,
            "error_hash": "stu901",
            "endpoint": "POST /api/test",
            "git_hash": "truncate-stu",
            "timestamp": 1640995200.0,
        }

        with patch("quarkle_monitoring.notifications.WebClient") as mock_webclient:
            mock_webclient.return_value = mock_slack_client
            notifier = SlackNotifier(token="test-token")

            result = notifier.send_error_alert(error_data)

            assert result is True
            call_args = mock_slack_client.chat_postMessage.call_args[1]

            # Check that message is truncated (first 200 chars)
            assert (
                len(call_args["text"]) < len(long_message) + 100
            )  # Some buffer for other text
            assert "Error details: xxx" in call_args["text"]

    def test_error_alert_missing_optional_fields(self, mock_slack_client):
        """Test that alerts work when optional fields are missing."""
        minimal_error_data = {
            "service": "backend-service",
            "error_code": 500,
            "git_hash": "minimal-abc",
            "timestamp": 1640995200.0,
        }

        with patch("quarkle_monitoring.notifications.WebClient") as mock_webclient:
            mock_webclient.return_value = mock_slack_client
            notifier = SlackNotifier(token="test-token")

            result = notifier.send_error_alert(minimal_error_data)

            assert result is True
            call_args = mock_slack_client.chat_postMessage.call_args[1]

            # Basic alert should still work
            assert "500 Error" in call_args["text"]
            assert "backend-service" in call_args["text"]

    def test_error_alert_complete_business_logic_data(self, mock_slack_client):
        """Test notification with complete business logic context."""
        complete_error_data = {
            "service": "backend-service",
            "error_code": 400,
            "error_message": "Validation failed: email format invalid",
            "error_hash": "full123",
            "endpoint": "POST /api/users",
            "user_id": "user_456",
            "git_hash": "test-full",
            "timestamp": 1640995200.0,
            "extra": {
                "function": "create_user",
                "business_logic_file": "user_api.py",
                "exception_type": "ValidationError",
            },
        }

        with patch("quarkle_monitoring.notifications.WebClient") as mock_webclient:
            mock_webclient.return_value = mock_slack_client
            notifier = SlackNotifier(token="test-token", stage="staging")

            result = notifier.send_error_alert(complete_error_data)

            assert result is True
            call_args = mock_slack_client.chat_postMessage.call_args[1]

            # Verify main message
            text = call_args["text"]
            assert "[STAGING]" in text
            assert "400 Error" in text
            assert "Validation failed: email format invalid" in text

            # Verify essential fields are present
            fields = call_args["attachments"][0]["fields"]
            field_titles = [f["title"] for f in fields]

            expected_fields = [
                "Endpoint",
                "User Id",
                "Git Hash",
                "Timestamp",
                "Function",
                "File",
                "Exception",
            ]

            for expected_field in expected_fields:
                assert (
                    expected_field in field_titles
                ), f"Missing field: {expected_field}"

    def test_send_custom_alert_basic(self, mock_slack_client):
        """Test sending a basic custom alert."""
        with patch("quarkle_monitoring.notifications.WebClient") as mock_webclient:
            mock_webclient.return_value = mock_slack_client
            notifier = SlackNotifier(token="test-token")

            result = notifier.send_custom_alert(
                title="🚀 Deployment Complete",
                message="Successfully deployed version 1.2.3",
                fields={"version": "1.2.3", "env": "production"},
                color="good",
            )

            assert result is True
            call_args = mock_slack_client.chat_postMessage.call_args[1]

            assert "🚀 Deployment Complete" in call_args["text"]
            assert "Successfully deployed version 1.2.3" in call_args["text"]

            # Check fields
            fields = call_args["attachments"][0]["fields"]
            field_dict = {f["title"]: f["value"] for f in fields}
            assert "Version" in field_dict
            assert "`1.2.3`" in field_dict["Version"]

    def test_send_custom_alert_with_stage(self, mock_slack_client):
        """Test custom alert includes stage suffix."""
        with patch("quarkle_monitoring.notifications.WebClient") as mock_webclient:
            mock_webclient.return_value = mock_slack_client
            notifier = SlackNotifier(token="test-token", stage="development")

            result = notifier.send_custom_alert(
                title="📊 Daily Report",
                message="System metrics summary",
            )

            assert result is True
            call_args = mock_slack_client.chat_postMessage.call_args[1]
            assert "[DEVELOPMENT]" in call_args["text"]
