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
        """Send error alert to Slack."""
        if not self.client:
            return False

        try:
            context = error_data.get("context", {})
            error_message = error_data.get("error_message")
            request_data = error_data.get("request_data", {})

            # Include stage in the message
            stage_suffix = (
                f" [{self.stage.upper()}]" if self.stage != "production" else ""
            )
            message = f"🚨 *{error_data['service']}*{stage_suffix} - {error_data['error_code']} Error"

            # Add error message to the main message if available
            if error_message:
                message += (
                    f"\n```{error_message[:200]}```"  # Truncate very long messages
                )

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

            # Add stage field if not production
            if self.stage != "production":
                fields.append(
                    {
                        "title": "Stage",
                        "value": f"`{self.stage}`",
                        "short": True,
                    }
                )

            if error_data.get("endpoint"):
                fields.append(
                    {
                        "title": "Endpoint",
                        "value": f"`{error_data['endpoint']}`",
                        "short": False,
                    }
                )

            # Add stack trace if available
            stack_trace = context.get("stack_trace", [])
            full_stack_trace = error_data.get("extra", {}).get("full_stack_trace")
            source_file = error_data.get("extra", {}).get("source_file_detected")

            if full_stack_trace:
                # Show the complete stack trace (truncated for Slack)
                stack_lines = full_stack_trace.split("\n")
                # Get the last 10 lines for the most relevant part
                relevant_stack = "\n".join(stack_lines[-10:])
                fields.append(
                    {
                        "title": "Complete Stack Trace",
                        "value": f"```{relevant_stack[:500]}```",  # Truncate for Slack limits
                        "short": False,
                    }
                )

                # Highlight the detected source file if found
                if source_file:
                    fields.append(
                        {
                            "title": "Source File",
                            "value": f"🎯 `{source_file}` (Business Logic)",
                            "short": True,
                        }
                    )
            elif (
                stack_trace and len(stack_trace) > 1
            ):  # Fallback to existing stack trace logic
                stack_text = "\n".join(stack_trace[:3])  # Top 3 frames
                fields.append(
                    {
                        "title": "Stack Trace",
                        "value": f"```{stack_text}```",
                        "short": False,
                    }
                )

            # Add request details if available
            if request_data:
                request_summary = []
                if request_data.get("method"):
                    request_summary.append(f"Method: {request_data['method']}")
                if request_data.get("path"):
                    request_summary.append(f"Path: {request_data['path']}")
                if request_data.get("query_params"):
                    request_summary.append(
                        f"Query: {str(request_data['query_params'])[:100]}"
                    )
                if request_data.get("user_agent"):
                    request_summary.append(
                        f"User-Agent: {request_data['user_agent'][:50]}"
                    )

                if request_summary:
                    fields.append(
                        {
                            "title": "Request Details",
                            "value": f"```{chr(10).join(request_summary)}```",
                            "short": False,
                        }
                    )

            # Add user info if available
            if error_data.get("user_id"):
                fields.append(
                    {
                        "title": "User ID",
                        "value": f"`{error_data['user_id']}`",
                        "short": True,
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

            # Include stage in the message
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
