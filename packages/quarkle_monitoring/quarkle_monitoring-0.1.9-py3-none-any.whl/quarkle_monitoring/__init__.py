"""Quarkle monitoring package for shared caching and error tracking."""

# Orchestrator for easy integration
from .orchestrator import QuarkleMonitoring

# Individual components for advanced usage
from .cache import QuarkleCache
from .errors import track_errors, ErrorTracker, MemoryCache, get_version_info
from .notifications import SlackNotifier

__version__ = "0.1.2"
__all__ = [
    # Main orchestrator
    "QuarkleMonitoring",
    # Individual components
    "QuarkleCache",
    "ErrorTracker",
    "MemoryCache",
    "SlackNotifier",
    "track_errors",
    # Utilities
    "get_version_info",
]
