"""Tests for cache module."""

import os
import pytest
from unittest.mock import Mock, patch
from quarkle_monitoring.cache import QuarkleCache


class TestQuarkleCache:
    """Test QuarkleCache functionality."""

    def test_init_with_defaults(self):
        """Test initialization with default values."""
        with patch("quarkle_monitoring.cache.redis"), patch.object(
            QuarkleCache, "_connect"
        ):
            cache = QuarkleCache()
            assert cache.stage == "test"  # From conftest.py
            assert cache.service_name == "test-service"

    def test_init_with_custom_values(self):
        """Test initialization with custom values."""
        with patch("quarkle_monitoring.cache.redis"), patch.object(
            QuarkleCache, "_connect"
        ):
            cache = QuarkleCache(stage="production", service_name="my-service")
            assert cache.stage == "production"
            assert cache.service_name == "my-service"

    def test_connect_direct_redis(self, mock_redis):
        """Test direct Redis connection via environment variables."""
        with patch("quarkle_monitoring.cache.redis") as mock_redis_module:
            mock_redis_module.Redis.return_value = mock_redis

            with patch.dict(
                os.environ, {"REDIS_HOST": "localhost", "REDIS_PORT": "6379"}
            ):
                cache = QuarkleCache()

                mock_redis_module.Redis.assert_called_once_with(
                    host="localhost",
                    port=6379,
                    decode_responses=True,
                    socket_connect_timeout=5,
                )
                mock_redis.ping.assert_called_once()
                assert cache._client is mock_redis

    def test_connect_via_ssm(self, mock_redis, mock_boto3):
        """Test SSM-based connection."""
        with patch("quarkle_monitoring.cache.redis") as mock_redis_module:
            mock_redis_module.Redis.return_value = mock_redis

            # No direct Redis env vars
            with patch.dict(os.environ, {}, clear=True):
                os.environ["STAGE"] = "test"
                os.environ["APP_NAME"] = "test-service"

                cache = QuarkleCache()

                mock_redis_module.Redis.assert_called_with(
                    host="test-cache.aws.com",
                    port=6379,
                    decode_responses=True,
                    socket_connect_timeout=5,
                )

    def test_connect_redis_not_available(self):
        """Test behavior when redis package not available."""
        with patch("quarkle_monitoring.cache.redis", None):
            cache = QuarkleCache()
            assert cache._client is None

    def test_connect_boto3_not_available(self):
        """Test behavior when boto3 package not available."""
        with patch("quarkle_monitoring.cache.redis"), patch(
            "quarkle_monitoring.cache.boto3", None
        ):
            # No direct Redis env vars
            with patch.dict(os.environ, {}, clear=True):
                os.environ["STAGE"] = "test"
                os.environ["APP_NAME"] = "test-service"

                cache = QuarkleCache()
                assert cache._client is None

    def test_get_success(self, mock_redis):
        """Test successful get operation."""
        mock_redis.get.return_value = "test_value"

        with patch("quarkle_monitoring.cache.redis") as mock_redis_module:
            mock_redis_module.Redis.return_value = mock_redis

            with patch.dict(os.environ, {"REDIS_HOST": "localhost"}):
                cache = QuarkleCache()
                result = cache.get("test_key")

                assert result == "test_value"
                mock_redis.get.assert_called_once_with("test_key")

    def test_get_no_client(self):
        """Test get operation when no client available."""
        with patch("quarkle_monitoring.cache.redis", None):
            cache = QuarkleCache()
            result = cache.get("test_key")
            assert result is None

    def test_get_exception(self, mock_redis):
        """Test get operation with exception."""
        mock_redis.get.side_effect = Exception("Redis error")

        with patch("quarkle_monitoring.cache.redis") as mock_redis_module:
            mock_redis_module.Redis.return_value = mock_redis

            with patch.dict(os.environ, {"REDIS_HOST": "localhost"}):
                cache = QuarkleCache()
                result = cache.get("test_key")
                assert result is None

    def test_set_success(self, mock_redis):
        """Test successful set operation."""
        mock_redis.setex.return_value = True

        with patch("quarkle_monitoring.cache.redis") as mock_redis_module:
            mock_redis_module.Redis.return_value = mock_redis

            with patch.dict(os.environ, {"REDIS_HOST": "localhost"}):
                cache = QuarkleCache()
                result = cache.set("test_key", "test_value", 1800)

                assert result is True
                mock_redis.setex.assert_called_once_with("test_key", 1800, "test_value")

    def test_exists_success(self, mock_redis):
        """Test successful exists operation."""
        mock_redis.exists.return_value = 1

        with patch("quarkle_monitoring.cache.redis") as mock_redis_module:
            mock_redis_module.Redis.return_value = mock_redis

            with patch.dict(os.environ, {"REDIS_HOST": "localhost"}):
                cache = QuarkleCache()
                result = cache.exists("test_key")

                assert result is True
                mock_redis.exists.assert_called_once_with("test_key")

    def test_rate_limit_allowed(self, mock_redis):
        """Test rate limiting when action is allowed."""
        mock_redis.exists.return_value = 0  # Key doesn't exist
        mock_redis.setex.return_value = True

        with patch("quarkle_monitoring.cache.redis") as mock_redis_module:
            mock_redis_module.Redis.return_value = mock_redis

            with patch.dict(os.environ, {"REDIS_HOST": "localhost"}):
                cache = QuarkleCache()
                result = cache.rate_limit("test_action", 5, 3600)

                assert result is True
                mock_redis.exists.assert_called_with("rate_limit:test_action")

    def test_rate_limit_blocked(self, mock_redis):
        """Test rate limiting when action is blocked."""
        mock_redis.exists.return_value = 1  # Key exists

        with patch("quarkle_monitoring.cache.redis") as mock_redis_module:
            mock_redis_module.Redis.return_value = mock_redis

            with patch.dict(os.environ, {"REDIS_HOST": "localhost"}):
                cache = QuarkleCache()
                result = cache.rate_limit("test_action", 5, 3600)

                assert result is False
