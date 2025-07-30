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

    def test_error_alert_with_stack_trace(self, mock_slack_client):
        """Test that stack traces are properly formatted in fields."""
        error_data = {
            "service": "backend-service",
            "error_code": 404,
            "error_message": "Resource not found",
            "error_hash": "def456",
            "context": {
                "function": "get_resource",
                "file": "resource_api.py",
                "line": 78,
                "stack_trace": [
                    "resource_api.py:get_resource:78",
                    "validators.py:validate_id:23",
                    "database.py:find_resource:156",
                ],
            },
            "endpoint": "GET /api/resources/{id}",
            "git_hash": "test-def",
            "timestamp": 1640995200.0,
        }

        with patch("quarkle_monitoring.notifications.WebClient") as mock_webclient:
            mock_webclient.return_value = mock_slack_client
            notifier = SlackNotifier(token="test-token")

            result = notifier.send_error_alert(error_data)

            assert result is True
            call_args = mock_slack_client.chat_postMessage.call_args[1]

            # Check attachment fields
            fields = call_args["attachments"][0]["fields"]
            stack_field = next((f for f in fields if f["title"] == "Stack Trace"), None)

            assert stack_field is not None
            assert "resource_api.py:get_resource:78" in stack_field["value"]
            assert "validators.py:validate_id:23" in stack_field["value"]
            assert "database.py:find_resource:156" in stack_field["value"]

    def test_error_alert_with_request_details(self, mock_slack_client):
        """Test that request details are properly formatted."""
        error_data = {
            "service": "backend-service",
            "error_code": 400,
            "error_message": "Invalid request",
            "error_hash": "ghi789",
            "context": {"function": "create_user", "file": "user_api.py", "line": 45},
            "endpoint": "POST /api/users",
            "git_hash": "test-ghi",
            "timestamp": 1640995200.0,
            "request_data": {
                "method": "POST",
                "path": "/api/users",
                "query_params": {"include": "profile"},
                "user_agent": "Mozilla/5.0 (Test Browser)",
                "ip": "192.168.1.100",
            },
        }

        with patch("quarkle_monitoring.notifications.WebClient") as mock_webclient:
            mock_webclient.return_value = mock_slack_client
            notifier = SlackNotifier(token="test-token")

            result = notifier.send_error_alert(error_data)

            assert result is True
            call_args = mock_slack_client.chat_postMessage.call_args[1]

            # Check request details field
            fields = call_args["attachments"][0]["fields"]
            request_field = next(
                (f for f in fields if f["title"] == "Request Details"), None
            )

            assert request_field is not None
            assert "Method: POST" in request_field["value"]
            assert "Path: /api/users" in request_field["value"]
            assert "Mozilla/5.0 (Test Browser)" in request_field["value"]

    def test_error_alert_with_user_id(self, mock_slack_client):
        """Test that user ID is displayed when present."""
        error_data = {
            "service": "backend-service",
            "error_code": 403,
            "error_message": "Access denied",
            "error_hash": "jkl012",
            "context": {
                "function": "delete_resource",
                "file": "resource_api.py",
                "line": 90,
            },
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
            user_field = next((f for f in fields if f["title"] == "User ID"), None)

            assert user_field is not None
            assert "user_789" in user_field["value"]

    def test_error_alert_staging_environment(self, mock_slack_client):
        """Test that staging environment is properly indicated."""
        error_data = {
            "service": "backend-service",
            "error_code": 500,
            "error_message": "Internal server error",
            "error_hash": "mno345",
            "context": {
                "function": "process_data",
                "file": "processor.py",
                "line": 123,
            },
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

            # Check stage field is present
            fields = call_args["attachments"][0]["fields"]
            stage_field = next((f for f in fields if f["title"] == "Stage"), None)
            assert stage_field is not None
            assert "staging" in stage_field["value"]

    def test_error_alert_production_environment(self, mock_slack_client):
        """Test that production environment doesn't show stage suffix."""
        error_data = {
            "service": "backend-service",
            "error_code": 404,
            "error_message": "Not found",
            "error_hash": "pqr678",
            "context": {"function": "get_item", "file": "api.py", "line": 56},
            "endpoint": "GET /api/items/{id}",
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
            assert "[" not in call_args["text"] or "]" not in call_args["text"]

            # Check no stage field for production
            fields = call_args["attachments"][0]["fields"]
            stage_field = next((f for f in fields if f["title"] == "Stage"), None)
            assert stage_field is None

    def test_error_alert_long_message_truncation(self, mock_slack_client):
        """Test that very long error messages are truncated."""
        long_message = (
            "This is a very long error message that should be truncated. " * 10
        )  # 630+ chars

        error_data = {
            "service": "backend-service",
            "error_code": 400,
            "error_message": long_message,
            "error_hash": "stu901",
            "context": {
                "function": "validate_input",
                "file": "validator.py",
                "line": 23,
            },
            "endpoint": "POST /api/validate",
            "git_hash": "test-stu",
            "timestamp": 1640995200.0,
        }

        with patch("quarkle_monitoring.notifications.WebClient") as mock_webclient:
            mock_webclient.return_value = mock_slack_client
            notifier = SlackNotifier(token="test-token")

            result = notifier.send_error_alert(error_data)

            assert result is True
            call_args = mock_slack_client.chat_postMessage.call_args[1]

            # Check that message is truncated to 200 chars
            message_content = call_args["text"]
            error_part = (
                message_content.split("```")[1] if "```" in message_content else ""
            )
            assert len(error_part) <= 200

    def test_error_alert_missing_optional_fields(self, mock_slack_client):
        """Test that missing optional fields don't break the notification."""
        minimal_error_data = {
            "service": "backend-service",
            "error_code": 404,
            "error_hash": "min123",
            "context": {"function": "unknown", "file": "unknown", "line": 0},
            "git_hash": "test-min",
            "timestamp": 1640995200.0,
        }

        with patch("quarkle_monitoring.notifications.WebClient") as mock_webclient:
            mock_webclient.return_value = mock_slack_client
            notifier = SlackNotifier(token="test-token")

            result = notifier.send_error_alert(minimal_error_data)

            assert result is True
            call_args = mock_slack_client.chat_postMessage.call_args[1]

            # Should still work with minimal data
            assert "404 Error" in call_args["text"]
            assert "backend-service" in call_args["text"]

    def test_error_alert_complete_enhanced_data(self, mock_slack_client):
        """Test notification with all enhanced fields present."""
        complete_error_data = {
            "service": "backend-service",
            "error_code": 400,
            "error_message": "Validation failed: email format invalid",
            "error_hash": "full123",
            "context": {
                "function": "create_user",
                "file": "user_api.py",
                "line": 45,
                "stack_trace": [
                    "user_api.py:create_user:45",
                    "validators.py:validate_email:12",
                    "auth.py:check_permissions:89",
                ],
            },
            "endpoint": "POST /api/users",
            "user_id": "user_456",
            "git_hash": "test-full",
            "timestamp": 1640995200.0,
            "request_data": {
                "method": "POST",
                "path": "/api/users",
                "query_params": {"source": "web"},
                "user_agent": "PostmanRuntime/7.28.0",
                "ip": "10.0.1.100",
                "content_type": "application/json",
            },
            "extra": {"response_size": 256},
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

            # Verify all enhanced fields are present
            fields = call_args["attachments"][0]["fields"]
            field_titles = [f["title"] for f in fields]

            expected_fields = [
                "Function",
                "File",
                "Git Hash",
                "Time",
                "Stage",
                "Endpoint",
                "Stack Trace",
                "Request Details",
                "User ID",
            ]

            for expected_field in expected_fields:
                assert (
                    expected_field in field_titles
                ), f"Missing field: {expected_field}"

            # Verify specific field content
            function_field = next(f for f in fields if f["title"] == "Function")
            assert "create_user" in function_field["value"]

            stack_field = next(f for f in fields if f["title"] == "Stack Trace")
            assert "user_api.py:create_user:45" in stack_field["value"]

            request_field = next(f for f in fields if f["title"] == "Request Details")
            assert "Method: POST" in request_field["value"]
            assert "PostmanRuntime" in request_field["value"]

            user_field = next(f for f in fields if f["title"] == "User ID")
            assert "user_456" in user_field["value"]

    def test_error_alert_with_full_stack_trace(self, mock_slack_client):
        """Test notification with full stack trace and source file detection."""
        # Simulate a realistic full stack trace
        full_stack_trace = """Traceback (most recent call last):
  File "/app/main.py", line 45, in handle_request
    return process_user_data(request.json)
  File "/app/services/user_service.py", line 23, in process_user_data
    user = create_user_account(data)
  File "/app/models/user.py", line 89, in create_user_account
    validate_email(data['email'])
  File "/app/validators/email_validator.py", line 12, in validate_email
    if not re.match(EMAIL_REGEX, email):
ValueError: Invalid email format: not-an-email
  File "/usr/local/lib/python3.9/site-packages/flask/app.py", line 1563, in full_dispatch_request
    rv = self.dispatch_request()
  File "/usr/local/lib/python3.9/site-packages/flask/app.py", line 1549, in dispatch_request
    return self.ensure_sync(self.view_functions[rule.endpoint])(**values)
  File "/usr/local/lib/python3.9/site-packages/werkzeug/routing.py", line 2213, in __call__
    return f(*args, **kwargs)"""

        error_data = {
            "service": "user-service",
            "error_code": 400,
            "error_message": "Email validation failed",
            "error_hash": "email_val_123",
            "context": {
                "function": "validate_email",
                "file": "email_validator.py",
                "line": 12,
            },
            "endpoint": "POST /api/users",
            "user_id": "user_789",
            "git_hash": "full-trace-abc",
            "timestamp": 1640995200.0,
            "extra": {
                "full_stack_trace": full_stack_trace,
                "source_file_detected": "/app/validators/email_validator.py",
            },
        }

        with patch("quarkle_monitoring.notifications.WebClient") as mock_webclient:
            mock_webclient.return_value = mock_slack_client
            notifier = SlackNotifier(token="test-token", stage="development")

            result = notifier.send_error_alert(error_data)

            assert result is True
            call_args = mock_slack_client.chat_postMessage.call_args[1]

            # Verify main message
            text = call_args["text"]
            assert "[DEVELOPMENT]" in text
            assert "400 Error" in text
            assert "Email validation failed" in text

            # Verify fields are present
            fields = call_args["attachments"][0]["fields"]
            field_titles = [f["title"] for f in fields]

            # Should have both Complete Stack Trace and Source File fields
            assert "Complete Stack Trace" in field_titles
            assert "Source File" in field_titles

            # Verify Complete Stack Trace field content
            stack_field = next(
                f for f in fields if f["title"] == "Complete Stack Trace"
            )
            # Should show the last 10 lines of the stack trace
            assert "ValueError: Invalid email format" in stack_field["value"]
            assert (
                "flask/app.py" in stack_field["value"]
            )  # This should be in the last 10 lines
            assert "full_dispatch_request" in stack_field["value"]
            # Should be truncated to 500 chars max
            assert (
                len(stack_field["value"]) <= 510
            )  # A bit of buffer for markdown formatting

            # Verify Source File field content
            source_field = next(f for f in fields if f["title"] == "Source File")
            assert "🎯" in source_field["value"]  # Target emoji
            assert "/app/validators/email_validator.py" in source_field["value"]
            assert "(Business Logic)" in source_field["value"]

    def test_error_alert_with_full_stack_trace_no_source_file(self, mock_slack_client):
        """Test notification with full stack trace but no detected source file."""
        full_stack_trace = """Traceback (most recent call last):
  File "/app/api/routes.py", line 34, in handle_request
    return database.find_user(user_id)
  File "/usr/local/lib/python3.9/site-packages/sqlalchemy/orm/query.py", line 2890, in one
    raise NoResultFound("No row was found when one was required")
sqlalchemy.orm.exc.NoResultFound: No row was found when one was required"""

        error_data = {
            "service": "database-service",
            "error_code": 404,
            "error_message": "User not found",
            "error_hash": "user_404_xyz",
            "context": {
                "function": "find_user",
                "file": "database.py",
                "line": 156,
            },
            "git_hash": "db-trace-xyz",
            "timestamp": 1640995200.0,
            "extra": {
                "full_stack_trace": full_stack_trace,
                # No source_file_detected
            },
        }

        with patch("quarkle_monitoring.notifications.WebClient") as mock_webclient:
            mock_webclient.return_value = mock_slack_client
            notifier = SlackNotifier(token="test-token")

            result = notifier.send_error_alert(error_data)

            assert result is True
            call_args = mock_slack_client.chat_postMessage.call_args[1]

            fields = call_args["attachments"][0]["fields"]
            field_titles = [f["title"] for f in fields]

            # Should have Complete Stack Trace but not Source File
            assert "Complete Stack Trace" in field_titles
            assert "Source File" not in field_titles

            # Verify Complete Stack Trace content
            stack_field = next(
                f for f in fields if f["title"] == "Complete Stack Trace"
            )
            assert "NoResultFound: No row was found" in stack_field["value"]
            assert "sqlalchemy/orm/query.py" in stack_field["value"]
