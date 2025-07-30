"""Framework-agnostic web utilities for error tracking."""

import logging
from typing import Dict, Any, Optional, Protocol, Union

logger = logging.getLogger(__name__)


class WebRequest(Protocol):
    """Protocol for web framework request objects."""

    method: str
    path: str
    args: Dict[str, Any]
    form: Dict[str, Any]
    content_length: Optional[int]

    def get_json(self) -> Dict[str, Any]: ...
    def is_json(self) -> bool: ...


class WebResponse(Protocol):
    """Protocol for web framework response objects."""

    status_code: int

    def get_json(self) -> Dict[str, Any]: ...
    def get_data(self, as_text: bool = False) -> Union[bytes, str]: ...
    def is_json(self) -> bool: ...


def extract_error_message(response: WebResponse, max_length: int = 500) -> str:
    """Extract meaningful error message from response (framework-agnostic)."""
    try:
        if hasattr(response, "is_json") and response.is_json():
            data = response.get_json()
            if data:
                return (
                    data.get("message")
                    or data.get("error")
                    or data.get("detail")
                    or str(data)
                )
        elif hasattr(response, "get_data"):
            text = response.get_data(as_text=True)
            if text and len(text) < max_length:
                return text
    except Exception as e:
        logger.debug(f"Could not extract error message: {e}")

    return f"HTTP {response.status_code} error"


def build_request_data(
    request: WebRequest,
    path: str,
    max_body_size: int = 1000,
    max_field_length: int = 300,
) -> Dict[str, Any]:
    """Build request data for error tracking (framework-agnostic)."""
    data = {
        "method": request.method,
        "path": path,
        "query_params": (
            dict(request.args) if hasattr(request, "args") and request.args else None
        ),
    }

    # Add form/JSON data for POST/PUT requests (but limit size)
    if request.method in ["POST", "PUT", "PATCH"]:
        try:
            if (
                hasattr(request, "is_json")
                and request.is_json()
                and hasattr(request, "content_length")
                and request.content_length
                and request.content_length < max_body_size
            ):
                json_data = str(request.get_json())[:max_field_length]
                data["json_data"] = json_data
            elif (
                hasattr(request, "form")
                and request.form
                and len(str(request.form)) < max_body_size
            ):
                form_data = str(dict(request.form))[:max_field_length]
                data["form_data"] = form_data
        except Exception as e:
            data["body_error"] = f"Could not parse request body: {e}"

    return data


# Common error filtering presets
COMMON_BOT_ENDPOINTS = [
    # Infrastructure/monitoring endpoints
    "/health*",
    "/metrics*",
    "/favicon.ico",
    "/robots.txt",
    "/sitemap.xml",
    # Common bot/crawler paths
    "/.well-known/*",
    "/wp-admin/*",
    "/admin/*",
    "/login",
    "/phpmyadmin/*",
    "/xmlrpc.php",
    "/.env",
    "/config/*",
    "/backup/*",
    # Development/testing paths
    "/test*",
    "/debug*",
    "/internal/*",
    # Common 404 noise from legitimate but misguided traffic
    "/apple-touch-icon*",
    "/android-chrome*",
    "/mstile*",
    "/browserconfig.xml",
    "/manifest.json",
]

COMMON_BOT_ERROR_CODES = [
    401,  # Unauthorized (often bots, wrong auth, etc.)
    405,  # Method not allowed (bots trying wrong methods)
    418,  # I'm a teapot (joke responses)
    429,  # Too many requests (rate limiting, not application bugs)
]
