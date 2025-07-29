"""Quarkle monitoring package for shared caching and error tracking."""

from .cache import QuarkleCache
from .errors import track_errors, ErrorTracker
from .notifications import SlackNotifier

__version__ = "0.1.0"
__all__ = ["QuarkleCache", "track_errors", "ErrorTracker", "SlackNotifier"]
