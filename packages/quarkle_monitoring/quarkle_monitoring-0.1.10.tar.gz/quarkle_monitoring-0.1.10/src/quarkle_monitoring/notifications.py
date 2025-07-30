"""Slack notifications (optional dependency)."""

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
    """Send simple, clean notifications to Slack."""

    def __init__(self, token: str = None, channel: str = None, stage: str = None):
        if not SLACK_AVAILABLE:
            logger.warning("slack-sdk not installed, notifications disabled")
            self.client = None
            return

        self.token = token or os.getenv("SLACK_APP_TOKEN")
        self.channel = channel or os.getenv("SLACK_ALERTS_CHANNEL", "C072D4XPLJ0")
        self.stage = stage or os.getenv("STAGE", "production")
        self.client = WebClient(token=self.token) if self.token else None

        if not self.client:
            logger.warning("No Slack token provided, notifications disabled")

    def send_error_alert(self, error_data: Dict[str, Any]) -> bool:
        """Send a clean, simple error alert to Slack."""
        if not self.client:
            return False

        try:
            # Build main message
            stage_suffix = (
                f" [{self.stage.upper()}]" if self.stage != "production" else ""
            )
            service = error_data.get("service", "Unknown Service")
            error_code = error_data.get("error_code", "Unknown")

            message = f"🚨 *{service}*{stage_suffix} - {error_code} Error"

            # Add error message if available
            error_message = error_data.get("error_message")
            if error_message:
                message += f"\n```{error_message[:200]}```"

            # Build fields from key data points
            fields = []

            # Essential fields
            essential_fields = {
                "endpoint": error_data.get("endpoint"),
                "user_id": error_data.get("user_id"),
                "git_hash": error_data.get("git_hash", "unknown"),
                "timestamp": time.strftime(
                    "%H:%M:%S UTC",
                    time.gmtime(error_data.get("timestamp", time.time())),
                ),
            }

            for key, value in essential_fields.items():
                if value:
                    fields.append(
                        {
                            "title": key.replace("_", " ").title(),
                            "value": f"`{value}`",
                            "short": True,
                        }
                    )

            # Business logic context (if available)
            extra = error_data.get("extra", {})
            if extra.get("function"):
                fields.append(
                    {
                        "title": "Function",
                        "value": f"🎯 `{extra['function']}()`",
                        "short": True,
                    }
                )

            if extra.get("business_logic_file"):
                fields.append(
                    {
                        "title": "File",
                        "value": f"🎯 `{extra['business_logic_file']}`",
                        "short": True,
                    }
                )

            # Exception type
            if extra.get("exception_type"):
                fields.append(
                    {
                        "title": "Exception",
                        "value": f"`{extra['exception_type']}`",
                        "short": True,
                    }
                )

            # Send the message
            self.client.chat_postMessage(
                channel=self.channel,
                text=message,
                attachments=[{"color": "danger", "fields": fields}],
            )
            return True

        except Exception as e:
            logger.error(f"Failed to send Slack alert: {e}")
            return False

    def send_lifecycle_alert(self, service: str, event: str, git_hash: str) -> bool:
        """Send a simple service lifecycle alert."""
        if not self.client:
            return False

        try:
            emoji = "🟢" if event == "startup" else "🔴"
            action = "Started" if event == "startup" else "Stopped"
            stage_suffix = (
                f" [{self.stage.upper()}]" if self.stage != "production" else ""
            )

            self.client.chat_postMessage(
                channel=self.channel,
                text=f"{emoji} *{service}*{stage_suffix} {action} (`{git_hash}`)",
            )
            return True

        except Exception as e:
            logger.error(f"Failed to send lifecycle alert: {e}")
            return False

    def send_custom_alert(
        self,
        title: str,
        message: str,
        fields: Dict[str, Any] = None,
        color: str = "warning",
    ) -> bool:
        """Send a custom alert with any data - completely general."""
        if not self.client:
            return False

        try:
            stage_suffix = (
                f" [{self.stage.upper()}]" if self.stage != "production" else ""
            )
            full_title = f"{title}{stage_suffix}"

            slack_fields = []
            if fields:
                for key, value in fields.items():
                    slack_fields.append(
                        {
                            "title": key.replace("_", " ").title(),
                            "value": (
                                f"`{value}`"
                                if isinstance(value, (str, int, float))
                                else str(value)
                            ),
                            "short": True,
                        }
                    )

            attachment = {"color": color}
            if slack_fields:
                attachment["fields"] = slack_fields

            self.client.chat_postMessage(
                channel=self.channel,
                text=f"{full_title}\n{message}",
                attachments=[attachment] if slack_fields else None,
            )
            return True

        except Exception as e:
            logger.error(f"Failed to send custom alert: {e}")
            return False
