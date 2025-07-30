"""Orchestrator to connect independent monitoring components."""

import logging
from typing import Optional, Dict, Any, List, Union, Callable
from functools import wraps

from .cache import QuarkleCache
from .errors import ErrorTracker, MemoryCache
from .notifications import SlackNotifier
from .web_utils import (
    extract_error_message,
    build_request_data,
    COMMON_BOT_ENDPOINTS,
    COMMON_BOT_ERROR_CODES,
)
from .auto_wrap import auto_wrap_modules

logger = logging.getLogger(__name__)


class QuarkleMonitoring:
    """Thin wrapper that orchestrates cache, error tracking, and notifications."""

    def __init__(
        self,
        stage: str = None,
        service_name: str = None,
        slack_token: str = None,
        slack_channel: str = None,
        use_redis: bool = True,
        version: str = None,
        ignored_error_codes: Optional[List[Union[int, str]]] = None,
        ignored_files: Optional[List[str]] = None,
        ignored_endpoints: Optional[List[str]] = None,
        tracked_endpoints: Optional[List[str]] = None,
    ):
        """
        Initialize QuarkleMonitoring orchestrator.

        Args:
            stage: Deployment stage for cache discovery
            service_name: Service name for tracking
            slack_token: Slack bot token (optional)
            slack_channel: Slack channel ID (optional)
            use_redis: Whether to use Redis cache (vs in-memory)
            version: Version string (optional, defaults to env vars)
            ignored_error_codes: List of error codes to ignore (supports wildcards like "4*" for all 4xx)
            ignored_files: List of file patterns to ignore (supports wildcards like "*_test.py")
            ignored_endpoints: List of endpoint patterns to ignore (supports wildcards like "/health*")
            tracked_endpoints: List of endpoint patterns to track exclusively (whitelist, supports wildcards like "/api/*")
                              If provided, ONLY errors from matching endpoints will be tracked.
                              Takes precedence over ignored_endpoints for endpoint filtering.
        """
        self.service_name = service_name
        self.stage = stage

        # Initialize cache (Redis or in-memory)
        if use_redis:
            self.cache = QuarkleCache(stage=stage, service_name=service_name)
        else:
            self.cache = MemoryCache()

        # Initialize error tracker with cache, version info, and filters
        # ErrorTracker handles all filtering logic
        self.error_tracker = ErrorTracker(
            cache=self.cache,
            service_name=service_name,
            version=version,
            ignored_error_codes=ignored_error_codes,
            ignored_files=ignored_files,
            ignored_endpoints=ignored_endpoints,
            tracked_endpoints=tracked_endpoints,
        )

        # Initialize notifications (optional) - now includes stage
        self.slack = SlackNotifier(
            token=slack_token, channel=slack_channel, stage=stage
        )

    def track_error(
        self,
        error_code: int,
        endpoint: str = None,
        user_id: str = None,
        extra: Dict = None,
        error_message: str = None,
        request_data: Dict = None,
        send_slack_alert: bool = True,
    ) -> tuple[bool, Dict[str, Any]]:
        """Track error and optionally send Slack alert."""
        # Let ErrorTracker handle all filtering logic
        should_alert, error_data = self.error_tracker.track_error(
            error_code=error_code,
            endpoint=endpoint,
            user_id=user_id,
            extra=extra,
            error_message=error_message,
            request_data=request_data,
        )

        if should_alert and send_slack_alert and error_data:
            try:
                self.slack.send_error_alert(error_data)
                logger.info(
                    f"Sent Slack alert for error {error_data.get('error_hash')}"
                )
            except Exception as e:
                logger.error(f"Failed to send Slack alert: {e}")

        return should_alert, error_data

    def send_lifecycle_alert(
        self, event: str, version: str = None, cache_ttl: int = 300
    ) -> bool:
        """
        Send service lifecycle alert to Slack with caching to prevent duplicates.

        Args:
            event: Lifecycle event (e.g., "startup", "shutdown")
            version: Version string (optional, defaults to tracked version)
            cache_ttl: Cache TTL in seconds to prevent duplicate alerts (default: 5 minutes)
        """
        service = self.service_name or "unknown"
        git_hash = version or self.error_tracker._git_hash

        # Create cache key for this specific lifecycle event
        cache_key = f"lifecycle:{service}:{event}:{git_hash}"

        # Check if we've already sent this alert recently
        if not self.cache.rate_limit(cache_key, limit=1, window=cache_ttl):
            logger.info(
                f"Skipping duplicate lifecycle alert: {service} {event} ({git_hash})"
            )
            return False

        try:
            success = self.slack.send_lifecycle_alert(
                service=service,
                event=event,
                git_hash=git_hash,
            )

            if success:
                logger.info(f"Sent lifecycle alert: {service} {event} ({git_hash})")
            else:
                # If Slack send failed, remove the cache entry so it can be retried
                logger.warning(
                    f"Failed to send lifecycle alert, clearing cache for retry"
                )
                # Note: We could implement a cache delete method if needed for this case

            return success

        except Exception as e:
            logger.error(f"Failed to send lifecycle alert: {e}")
            return False

    def track_errors_decorator(self, send_slack_alert: bool = True):
        """Decorator to automatically track errors with optional Slack alerts."""

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    status = getattr(e, "status_code", 500)
                    if 400 <= status < 600:  # Track both 4xx and 5xx errors
                        self.track_error(
                            error_code=status,
                            endpoint=func.__name__,
                            error_message=str(e),
                            extra={
                                "exception": str(e),
                                "exception_type": type(e).__name__,
                            },
                            send_slack_alert=send_slack_alert,
                        )
                    raise

            return wrapper

        return decorator

    def track_web_error(
        self,
        response,
        request,
        user_id_getter=None,
        extra_context=None,
        send_slack_alert: bool = True,
    ) -> tuple[bool, Dict[str, Any]]:
        """
        Track web framework error with automatic request/response parsing.
        """
        status_code = response.status_code
        if not (400 <= status_code < 600):
            return False, {}

        try:
            path = request.path
            endpoint = f"{request.method} {path}"

            error_message = extract_error_message(response)
            request_data = build_request_data(request, path)

            user_id = None
            if user_id_getter:
                try:
                    user_id = user_id_getter()
                except Exception:
                    pass

            extra = {
                "source": "web_middleware",
                "response_size": (
                    len(response.get_data()) if hasattr(response, "get_data") else 0
                ),
                **(extra_context or {}),
            }

            # Let ErrorTracker handle all filtering including tracked_endpoints
            return self.track_error(
                error_code=status_code,
                endpoint=endpoint,
                user_id=user_id,
                error_message=error_message,
                request_data=request_data,
                extra=extra,
                send_slack_alert=send_slack_alert,
            )
        except Exception as e:
            logger.error(f"Error in track_web_error: {e}")
            return False, {}

    def setup_auto_tracking(
        self, module_names: List[str], context_getter: Optional[Callable] = None
    ) -> int:
        """Set up automatic error tracking for business logic modules."""

        def track_func(**kwargs):
            return self.track_error(send_slack_alert=True, **kwargs)

        return auto_wrap_modules(
            module_names=module_names,
            error_tracker_func=track_func,
            context_getter=context_getter,
        )

    @classmethod
    def create_with_common_web_filters(
        cls,
        stage: str = None,
        service_name: str = None,
        additional_ignored_endpoints: List[str] = None,
        additional_ignored_codes: List[int] = None,
        **kwargs,
    ):
        """Create QuarkleMonitoring with common web app error filters."""
        ignored_endpoints = COMMON_BOT_ENDPOINTS.copy()
        if additional_ignored_endpoints:
            ignored_endpoints.extend(additional_ignored_endpoints)

        ignored_codes = COMMON_BOT_ERROR_CODES.copy()
        if additional_ignored_codes:
            ignored_codes.extend(additional_ignored_codes)

        return cls(
            stage=stage,
            service_name=service_name,
            ignored_endpoints=ignored_endpoints,
            ignored_error_codes=ignored_codes,
            **kwargs,
        )

    @classmethod
    def create_with_tracked_endpoints(
        cls,
        tracked_endpoints: List[str],
        stage: str = None,
        service_name: str = None,
        additional_ignored_codes: List[int] = None,
        **kwargs,
    ):
        """
        Create QuarkleMonitoring with endpoint whitelist (only track specified endpoints).

        Args:
            tracked_endpoints: List of endpoint patterns to track (supports wildcards like "/api/*")
            stage: Deployment stage
            service_name: Service name
            additional_ignored_codes: Additional error codes to ignore
            **kwargs: Other QuarkleMonitoring parameters

        Example:
            # Only track errors from API endpoints
            monitoring = QuarkleMonitoring.create_with_tracked_endpoints([
                "/api/users/*",
                "/api/books/*",
                "POST /api/orders",
            ])
        """
        ignored_codes = COMMON_BOT_ERROR_CODES.copy()
        if additional_ignored_codes:
            ignored_codes.extend(additional_ignored_codes)

        return cls(
            stage=stage,
            service_name=service_name,
            tracked_endpoints=tracked_endpoints,
            ignored_error_codes=ignored_codes,
            **kwargs,
        )

    # Expose individual components for advanced usage
    @property
    def cache_client(self):
        """Access to the underlying cache client."""
        return self.cache

    @property
    def error_client(self):
        """Access to the underlying error tracker."""
        return self.error_tracker

    @property
    def slack_client(self):
        """Access to the underlying Slack client."""
        return self.slack

    # Expose tracked_endpoints for tests/debugging
    @property
    def tracked_endpoints(self):
        """Access to tracked endpoints (from ErrorTracker)."""
        return self.error_tracker.tracked_endpoints
