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
