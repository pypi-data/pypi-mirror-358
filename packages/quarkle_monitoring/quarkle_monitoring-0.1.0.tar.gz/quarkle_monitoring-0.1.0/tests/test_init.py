"""Tests for package initialization."""


def test_package_imports():
    """Test that main package imports work correctly."""
    from quarkle_monitoring import (
        QuarkleCache,
        track_errors,
        ErrorTracker,
        SlackNotifier,
    )
    from quarkle_monitoring import __version__, __all__

    # Test that all expected exports are available
    assert QuarkleCache is not None
    assert track_errors is not None
    assert ErrorTracker is not None
    assert SlackNotifier is not None

    # Test version and __all__
    assert __version__ == "0.1.0"
    assert set(__all__) == {
        "QuarkleCache",
        "track_errors",
        "ErrorTracker",
        "SlackNotifier",
    }


def test_cache_class():
    """Test that QuarkleCache can be instantiated."""
    from quarkle_monitoring import QuarkleCache
    from unittest.mock import patch

    with patch.object(QuarkleCache, "_connect"):
        cache = QuarkleCache()
        assert cache is not None


def test_error_tracker_class():
    """Test that ErrorTracker can be instantiated."""
    from quarkle_monitoring import ErrorTracker, QuarkleCache
    from unittest.mock import Mock, patch

    mock_cache = Mock(spec=QuarkleCache)
    with patch.object(ErrorTracker, "_get_git_hash", return_value="test"):
        tracker = ErrorTracker(mock_cache)
        assert tracker is not None


def test_slack_notifier_class():
    """Test that SlackNotifier can be instantiated."""
    from quarkle_monitoring import SlackNotifier

    # Should work even without slack-sdk installed
    notifier = SlackNotifier()
    assert notifier is not None
