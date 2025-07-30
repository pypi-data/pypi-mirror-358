"""Test configuration and fixtures."""

import os
import pytest
from unittest.mock import Mock, patch
import redis

# Set test environment
os.environ["STAGE"] = "test"
os.environ["APP_NAME"] = "test-service"


@pytest.fixture
def mock_redis():
    """Mock Redis client."""
    mock_client = Mock(spec=redis.Redis)
    mock_client.ping.return_value = True
    mock_client.get.return_value = None
    mock_client.setex.return_value = True
    mock_client.exists.return_value = False
    return mock_client


@pytest.fixture
def mock_boto3():
    """Mock boto3 SSM client."""
    mock_ssm = Mock()
    mock_ssm.get_parameter.side_effect = [
        {"Parameter": {"Value": "test-cache.aws.com"}},  # endpoint
        {"Parameter": {"Value": "6379"}},  # port
    ]

    with patch("boto3.client") as mock_client:
        mock_client.return_value = mock_ssm
        yield mock_ssm


@pytest.fixture
def mock_slack_client():
    """Mock Slack WebClient."""
    mock_client = Mock()
    mock_client.chat_postMessage.return_value = {"ok": True}
    return mock_client


@pytest.fixture
def sample_error_data():
    """Sample error data for testing."""
    return {
        "service": "test-service",
        "error_code": 404,
        "context": {
            "function": "test_function",
            "file": "test.py",
            "line": 42,
        },
        "endpoint": "/api/test",
        "user_id": "user123",
        "git_hash": "abc123",
        "timestamp": 1640995200.0,
        "extra": {"key": "value"},
    }
