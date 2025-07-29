"""Error tracking functionality."""

import hashlib
import inspect
import json
import os
import subprocess
import time
from typing import Dict, Any, Optional
from functools import wraps

from .cache import QuarkleCache


class ErrorTracker:
    """Track and rate-limit error alerts."""

    def __init__(self, cache: QuarkleCache, service_name: str = None):
        self.cache = cache
        self.service_name = service_name or os.getenv("APP_NAME", "unknown")
        self._git_hash = self._get_git_hash()

    def _get_git_hash(self) -> str:
        """Get git commit hash."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return os.getenv("GIT_HASH", "unknown")

    def _get_call_context(self) -> Dict[str, Any]:
        """Get function call context."""
        try:
            frame = inspect.currentframe()
            # Skip internal frames
            for _ in range(5):
                frame = frame.f_back
                if frame and "track_error" not in frame.f_code.co_name:
                    break

            if frame:
                return {
                    "function": frame.f_code.co_name,
                    "file": os.path.basename(frame.f_code.co_filename),
                    "line": frame.f_lineno,
                }
        except Exception:
            pass
        return {"function": "unknown", "file": "unknown", "line": 0}

    def track_error(
        self,
        error_code: int,
        endpoint: str = None,
        user_id: str = None,
        extra: Dict = None,
    ) -> tuple[bool, str]:
        """Track error and return (should_alert, error_hash)."""
        if not (400 <= error_code < 500):
            return False, ""

        context = self._get_call_context()

        # Create unique error signature
        signature_parts = [
            self.service_name,
            str(error_code),
            context["function"],
            context["file"],
            str(context["line"]),
            endpoint or "no-endpoint",
        ]

        error_sig = ":".join(signature_parts)
        error_hash = hashlib.md5(error_sig.encode()).hexdigest()[:12]

        # Rate limit (4 hours)
        if not self.cache.rate_limit(f"error:{error_hash}", 1, 14400):
            return False, error_hash  # Rate limited

        # Store error details
        error_data = {
            "service": self.service_name,
            "error_code": error_code,
            "context": context,
            "endpoint": endpoint,
            "user_id": user_id,
            "git_hash": self._git_hash,
            "timestamp": time.time(),
            "extra": extra or {},
        }

        self.cache.set(
            f"error_detail:{error_hash}", json.dumps(error_data), 86400  # 24 hours
        )

        return True, error_hash  # Should send alert

    def _get_error_hash(self, error_code: int, endpoint: str = None) -> str:
        """Get the error hash for a given error (for retrieval purposes)"""
        context = self._get_call_context()

        # Create the same signature as in track_error
        signature_parts = [
            self.service_name,
            str(error_code),
            context["function"],
            context["file"],
            str(context["line"]),
            endpoint or "no-endpoint",
        ]

        error_sig = ":".join(signature_parts)
        return hashlib.md5(error_sig.encode()).hexdigest()[:12]


def track_errors(error_tracker: ErrorTracker):
    """Decorator to automatically track errors."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                status = getattr(e, "status_code", 500)
                if 400 <= status < 500:
                    should_alert, error_hash = error_tracker.track_error(
                        status, endpoint=func.__name__, extra={"exception": str(e)}
                    )
                    if should_alert:
                        # Here you'd send the actual alert
                        # This is separated to keep minimal dependencies
                        pass
                raise

        return wrapper

    return decorator
