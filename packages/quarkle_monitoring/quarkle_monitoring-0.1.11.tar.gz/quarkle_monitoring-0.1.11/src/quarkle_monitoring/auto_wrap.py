"""Automatic error tracking for modules."""

import sys
import logging
from functools import wraps
from typing import List, Callable, Any, Optional

logger = logging.getLogger(__name__)


def auto_wrap_modules(
    module_names: List[str],
    error_tracker_func: Callable,
    context_getter: Optional[Callable] = None,
    skip_private: bool = True,
    skip_patterns: Optional[List[str]] = None,
) -> int:
    """
    Automatically wrap functions in specified modules with error tracking.

    Args:
        module_names: List of module names to wrap (supports patterns like "app.*")
        error_tracker_func: Function to call for error tracking
        context_getter: Optional function to get current context (user_id, etc.)
        skip_private: Skip functions starting with underscore
        skip_patterns: List of function name patterns to skip

    Returns:
        Number of functions wrapped
    """
    skip_patterns = skip_patterns or []
    wrapped_count = 0

    def create_error_wrapper(original_func):
        @wraps(original_func)
        def wrapper(*args, **kwargs):
            try:
                return original_func(*args, **kwargs)
            except Exception as e:
                # Get context if available
                context = {}
                if context_getter:
                    try:
                        context = context_getter() or {}
                    except Exception:
                        pass

                # Extract error details
                status_code = getattr(e, "code", None) or getattr(e, "status_code", 500)

                # Track error with business logic context
                error_tracker_func(
                    error_code=status_code,
                    endpoint=original_func.__name__,
                    error_message=str(e),
                    extra={
                        "function": original_func.__name__,
                        "exception_type": type(e).__name__,
                        "module": original_func.__module__,
                        **context,
                    },
                )

                # Mark error as tracked (if using Flask-style context)
                if hasattr(context, "_error_already_tracked"):
                    context._error_already_tracked = True

                raise  # Re-raise the original exception

        return wrapper

    # Auto-wrap functions in business logic modules
    for module_name in module_names:
        possible_names = [module_name, f"app.{module_name}", f"{module_name}_api"]

        found_module = None
        for possible_name in possible_names:
            if possible_name in sys.modules:
                found_module = sys.modules[possible_name]
                break

        if found_module:
            for attr_name in dir(found_module):
                # Skip private functions if requested
                if skip_private and attr_name.startswith("_"):
                    continue

                # Skip if matches skip patterns
                if any(pattern in attr_name for pattern in skip_patterns):
                    continue

                attr = getattr(found_module, attr_name)
                if (
                    callable(attr)
                    and hasattr(attr, "__module__")
                    and attr.__module__ == found_module.__name__
                ):
                    # Wrap the function
                    wrapped_func = create_error_wrapper(attr)
                    setattr(found_module, attr_name, wrapped_func)
                    wrapped_count += 1

    logger.info(f"Auto-tracking enabled: wrapped {wrapped_count} functions")
    return wrapped_count
