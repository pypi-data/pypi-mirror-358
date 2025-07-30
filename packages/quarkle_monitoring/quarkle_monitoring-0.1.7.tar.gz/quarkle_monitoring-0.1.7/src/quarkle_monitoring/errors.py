"""Error tracking functionality."""

import fnmatch
import hashlib
import inspect
import json
import os
import time
from typing import Dict, Any, Optional, Protocol, List, Union
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
        ignored_error_codes: Optional[List[Union[int, str]]] = None,
        ignored_files: Optional[List[str]] = None,
        ignored_endpoints: Optional[List[str]] = None,
    ):
        """
        Initialize ErrorTracker.

        Args:
            cache: Cache backend (defaults to MemoryCache)
            service_name: Service name (defaults to APP_NAME env var)
            version: Version string (defaults to env vars or "unknown")
            ignored_error_codes: List of error codes to ignore (supports wildcards like "4*" for all 4xx)
            ignored_files: List of file patterns to ignore (supports wildcards like "*_test.py")
            ignored_endpoints: List of endpoint patterns to ignore (supports wildcards like "/health*")
        """
        self.cache = cache or MemoryCache()
        self.service_name = service_name or os.getenv("APP_NAME", "unknown")
        self._git_hash = self._get_version_info(version)

        # Initialize filters (convert to lists if None)
        self.ignored_error_codes = ignored_error_codes or []
        self.ignored_files = ignored_files or []
        self.ignored_endpoints = ignored_endpoints or []

    def _get_version_info(self, version: str = None) -> str:
        """Get version information - can be easily patched in tests."""
        return get_version_info(version)

    def _matches_any_pattern(self, value: str, patterns: List[Union[int, str]]) -> bool:
        """Check if a value matches any pattern in the list."""
        if not patterns:
            return False

        str_value = str(value)
        for pattern in patterns:
            pattern_str = str(pattern)
            # Support both exact matches and wildcard patterns
            if str_value == pattern_str or fnmatch.fnmatch(str_value, pattern_str):
                return True
        return False

    def _should_ignore_error(
        self, error_code: int, endpoint: str = None, context: Dict[str, Any] = None
    ) -> bool:
        """Check if error should be ignored based on configured filters."""
        # Check error code filters
        if self._matches_any_pattern(error_code, self.ignored_error_codes):
            return True

        # Check endpoint filters
        if endpoint and self._matches_any_pattern(endpoint, self.ignored_endpoints):
            return True

        # Check file filters
        if context and context.get("file"):
            if self._matches_any_pattern(context["file"], self.ignored_files):
                return True

        return False

    def _get_call_context(self) -> Dict[str, Any]:
        """Get function call context - return stack trace of the last 5 meaningful functions."""
        try:
            frame = inspect.currentframe()
            contexts = []  # Collect meaningful contexts

            # Walk up the stack to find meaningful contexts
            for i in range(25):  # Look up to 25 frames for Connexion/OpenAPI
                frame = frame.f_back
                if not frame:
                    break

                func_name = frame.f_code.co_name
                file_name = os.path.basename(frame.f_code.co_filename)
                full_file_path = frame.f_code.co_filename

                # Skip internal frames first
                if any(
                    skip in func_name
                    for skip in [
                        "track_error",
                        "_get_call_context",
                        "after_request",
                        "wrapper",
                        "__call__",
                        "dispatch_request",
                        "process_response",
                        "wsgi_app",
                        "application",
                    ]
                ):
                    continue

                # Skip framework files
                if any(
                    skip in file_name
                    for skip in [
                        "metrics.py",
                        "flask",
                        "werkzeug",
                        "threading",
                        "connexion",
                        "validation.py",
                        "operation.py",
                        "app.py",  # Skip generic app.py framework files
                    ]
                ):
                    continue

                # Skip if it's clearly a framework path
                if any(
                    framework in full_file_path
                    for framework in [
                        # Python package directories
                        "/site-packages/",
                        "/dist-packages/",
                        # Virtual environments (common patterns)
                        "/env/",
                        "/venv/",
                        "/.env/",
                        "/.venv/",
                        "/virtualenv/",
                        # Framework-specific paths
                        "/connexion/",
                        "/flask/",
                        "/werkzeug/",
                        "/jinja2/",
                        "/sqlalchemy/",
                        # Python installation paths
                        "/lib/python",  # e.g., /usr/lib/python3.9/
                        "/Library/Frameworks/Python.framework/",  # macOS
                        # Common CI/container paths that aren't business logic
                        "/.pyenv/",
                        "/opt/python/",
                        "/usr/local/lib/python",
                    ]
                ):
                    continue

                # This is a meaningful context - add it
                context = {
                    "function": func_name,
                    "file": file_name,
                    "line": frame.f_lineno,
                    "full_path": full_file_path,
                }

                contexts.append(context)

                # Stop after we have 5 meaningful contexts
                if len(contexts) >= 5:
                    break

            # Return the stack trace information
            if contexts:
                # Use the first (most recent) context as primary, but include full stack
                primary_context = contexts[0]

                # Create detailed stack trace
                stack_trace = []
                for i, ctx in enumerate(contexts):
                    stack_entry = f"{ctx['file']}:{ctx['function']}:{ctx['line']}"
                    stack_trace.append(stack_entry)

                return {
                    "function": primary_context["function"],
                    "file": primary_context["file"],
                    "line": primary_context["line"],
                    "stack_trace": stack_trace,
                    "full_contexts": contexts,  # Include full context details for debugging
                }

        except Exception:
            pass

        # Fallback
        return {
            "function": "unknown",
            "file": "unknown",
            "line": 0,
            "stack_trace": ["unknown"],
        }

    def track_error(
        self,
        error_code: int,
        endpoint: str = None,
        user_id: str = None,
        extra: Dict = None,
        error_message: str = None,
        request_data: Dict = None,
    ) -> tuple[bool, Dict[str, Any]]:
        """Track error and return (should_alert, error_data)."""
        if not (400 <= error_code < 600):
            return False, {}  # Track both 4xx and 5xx errors

        context = self._get_call_context()

        # Check if this error should be ignored based on filters
        if self._should_ignore_error(error_code, endpoint, context):
            return False, {}  # Ignore this error

        # Create unique error signature for rate limiting (simple approach)
        # Keep signature simple to group similar errors together
        signature_parts = [
            self.service_name,
            str(error_code),
            endpoint or "no-endpoint",
        ]

        error_sig = ":".join(signature_parts)
        error_hash = hashlib.md5(error_sig.encode()).hexdigest()[:12]

        # Rate limit (4 hours)
        if not self.cache.rate_limit(f"error:{error_hash}", 1, 14400):
            return False, {}  # Rate limited

        # Create error details with enhanced information (for storage & notifications)
        error_data = {
            "service": self.service_name,
            "error_code": error_code,
            "error_message": error_message,
            "error_hash": error_hash,
            "context": context,
            "endpoint": endpoint,
            "user_id": user_id,
            "git_hash": self._git_hash,
            "timestamp": time.time(),
            "request_data": request_data or {},
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
                if 400 <= status < 600:  # Track both 4xx and 5xx errors
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
