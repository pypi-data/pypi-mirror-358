"""Slack notifications (optional dependency)."""

import json
import logging
import os
import time
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

try:
    from slack_sdk import WebClient
    from slack_sdk.errors import SlackApiError

    SLACK_AVAILABLE = True
except ImportError:
    SLACK_AVAILABLE = False


class SlackNotifier:
    """Send notifications to Slack."""

    def __init__(self, token: str = None, channel: str = None):
        if not SLACK_AVAILABLE:
            logger.warning("slack-sdk not installed, notifications disabled")
            self.client = None
            return

        self.token = token or os.getenv("SLACK_APP_TOKEN")
        self.channel = channel or os.getenv("SLACK_ALERTS_CHANNEL", "C072D4XPLJ0")
        self.client = WebClient(token=self.token) if self.token else None

        if not self.client:
            logger.warning("No Slack token provided, notifications disabled")

    def send_error_alert(self, error_data: Dict[str, Any]) -> bool:
        """Send error alert to Slack."""
        if not self.client:
            return False

        try:
            context = error_data.get("context", {})

            message = f"🚨 *{error_data['service']}* - {error_data['error_code']} Error"

            fields = [
                {
                    "title": "Function",
                    "value": f"`{context.get('function', 'unknown')}`",
                    "short": True,
                },
                {
                    "title": "File",
                    "value": f"`{context.get('file', 'unknown')}`",
                    "short": True,
                },
                {
                    "title": "Git Hash",
                    "value": f"`{error_data.get('git_hash', 'unknown')}`",
                    "short": True,
                },
                {
                    "title": "Time",
                    "value": time.strftime(
                        "%H:%M:%S UTC", time.gmtime(error_data["timestamp"])
                    ),
                    "short": True,
                },
            ]

            if error_data.get("endpoint"):
                fields.append(
                    {
                        "title": "Endpoint",
                        "value": f"`{error_data['endpoint']}`",
                        "short": False,
                    }
                )

            self.client.chat_postMessage(
                channel=self.channel,
                text=message,
                attachments=[{"color": "warning", "fields": fields}],
            )
            return True

        except Exception as e:
            logger.error(f"Failed to send Slack alert: {e}")
            return False

    def send_lifecycle_alert(self, service: str, event: str, git_hash: str) -> bool:
        """Send service lifecycle alert."""
        if not self.client:
            return False

        try:
            emoji = "🟢" if event == "startup" else "🔴"
            action = "Started" if event == "startup" else "Stopped"

            self.client.chat_postMessage(
                channel=self.channel,
                text=f"{emoji} *{service}* {action} (`{git_hash}`)",
            )
            return True

        except Exception as e:
            logger.error(f"Failed to send lifecycle alert: {e}")
            return False
