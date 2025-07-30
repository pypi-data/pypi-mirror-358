"""Error tracking functionality."""

import hashlib
import inspect
import json
import os
import time
from typing import Dict, Any, Optional, Protocol
from functools import wraps


class CacheInterface(Protocol):
    """Protocol for cache backends."""

    def rate_limit(self, key: str, limit: int, window: int = 3600) -> bool:
        """Simple rate limiting. Returns True if action is allowed."""
        ...

    def set(self, key: str, value: str, ttl: int = 3600) -> bool:
        """Set value in cache with TTL."""
        ...


class MemoryCache:
    """Simple in-memory cache for development/testing."""

    def __init__(self):
        self._data = {}
        self._expiry = {}

    def _cleanup_expired(self):
        """Remove expired keys."""
        now = time.time()
        expired = [k for k, exp in self._expiry.items() if exp < now]
        for key in expired:
            self._data.pop(key, None)
            self._expiry.pop(key, None)

    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        deleted = key in self._data
        self._data.pop(key, None)
        self._expiry.pop(key, None)
        return deleted

    def rate_limit(self, key: str, limit: int, window: int = 3600) -> bool:
        """Simple rate limiting. Returns True if action is allowed."""
        self._cleanup_expired()
        cache_key = f"rate_limit:{key}"

        if cache_key in self._data:
            return False  # Rate limited

        self.set(cache_key, str(int(time.time())), window)
        return True  # Allowed

    def set(self, key: str, value: str, ttl: int = 3600) -> bool:
        """Set value in cache with TTL."""
        self._data[key] = value
        self._expiry[key] = time.time() + ttl
        return True


def get_version_info(version: str = None) -> str:
    """
    Get version information (simplified).

    Priority:
    1. Explicit version parameter
    2. Common environment variables
    3. "unknown" fallback

    Args:
        version: Explicit version string

    Returns:
        Version string (max 12 chars)
    """
    if version:
        return version[:12]

    # Check common environment variables
    for env_var in [
        "APP_VERSION",  # Your app version
        "GIT_HASH",  # Git commit hash
        "BUILD_ID",  # Build identifier
        "IMAGE_TAG",  # Docker image tag
        "CI_COMMIT_SHA",  # GitLab CI
        "GITHUB_SHA",  # GitHub Actions
        "HOSTNAME",  # Container ID (Docker default)
    ]:
        value = os.getenv(env_var)
        if value:
            return value[:12]

    return "unknown"


class ErrorTracker:
    """Track and rate-limit error alerts."""

    def __init__(
        self,
        cache: Optional[CacheInterface] = None,
        service_name: str = None,
        version: str = None,
    ):
        """
        Initialize ErrorTracker.

        Args:
            cache: Cache backend (defaults to MemoryCache)
            service_name: Service name (defaults to APP_NAME env var)
            version: Version string (defaults to env vars or "unknown")
        """
        self.cache = cache or MemoryCache()
        self.service_name = service_name or os.getenv("APP_NAME", "unknown")
        self._git_hash = self._get_version_info(version)

    def _get_version_info(self, version: str = None) -> str:
        """Get version information - can be easily patched in tests."""
        return get_version_info(version)

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
    ) -> tuple[bool, Dict[str, Any]]:
        """Track error and return (should_alert, error_data)."""
        if not (400 <= error_code < 500):
            return False, {}

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
            return False, {}  # Rate limited

        # Create error details
        error_data = {
            "service": self.service_name,
            "error_code": error_code,
            "error_hash": error_hash,
            "context": context,
            "endpoint": endpoint,
            "user_id": user_id,
            "git_hash": self._git_hash,
            "timestamp": time.time(),
            "extra": extra or {},
        }

        # Store error details if cache supports it
        try:
            self.cache.set(
                f"error_detail:{error_hash}", json.dumps(error_data), 86400  # 24 hours
            )
        except AttributeError:
            # Cache doesn't support set operation, that's fine
            pass

        return True, error_data  # Should send alert

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
                    should_alert, error_data = error_tracker.track_error(
                        status, endpoint=func.__name__, extra={"exception": str(e)}
                    )
                    if should_alert:
                        # Here you'd send the actual alert
                        # This is separated to keep minimal dependencies
                        pass
                raise

        return wrapper

    return decorator
