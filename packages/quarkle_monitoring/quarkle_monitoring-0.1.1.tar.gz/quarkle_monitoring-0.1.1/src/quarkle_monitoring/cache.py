"""Minimal Redis cache client with AWS SSM discovery."""

import json
import logging
import os
import time
from typing import Optional, Dict, Any

try:
    import redis
except ImportError:
    redis = None

try:
    import boto3
except ImportError:
    boto3 = None

logger = logging.getLogger(__name__)


class QuarkleCache:
    """Minimal shared cache client with AWS discovery."""

    def __init__(self, stage: str = None, service_name: str = None):
        self.stage = stage or os.getenv("STAGE", "production")
        self.service_name = service_name or os.getenv("APP_NAME", "unknown")
        self._client = None
        self._connect()

    def _connect(self):
        """Connect to Redis via SSM or environment variables."""
        if not redis:
            logger.error("redis package not installed")
            return

        try:
            # Try direct connection first (for local dev)
            host = os.getenv("REDIS_HOST")
            port = int(os.getenv("REDIS_PORT", "6379"))

            if host:
                self._client = redis.Redis(
                    host=host,
                    port=port,
                    decode_responses=True,
                    socket_connect_timeout=5,
                )
                self._client.ping()
                logger.info(f"Connected to Redis: {host}:{port}")
                return
        except Exception:
            pass

        # Fallback to SSM discovery
        try:
            if not boto3:
                logger.error("boto3 package not installed for SSM discovery")
                return

            region = os.getenv("AWS_DEFAULT_REGION") or os.getenv(
                "AWS_REGION", "us-east-1"
            )
            logger.info(f"Using AWS region: {region}")

            ssm = boto3.client("ssm", region_name=region)

            endpoint = ssm.get_parameter(Name=f"/quarkle/{self.stage}/cache/endpoint")[
                "Parameter"
            ]["Value"]
            port = int(
                ssm.get_parameter(Name=f"/quarkle/{self.stage}/cache/port")[
                    "Parameter"
                ]["Value"]
            )

            self._client = redis.Redis(
                host=endpoint,
                port=port,
                decode_responses=True,
                socket_connect_timeout=5,
            )
            self._client.ping()
            logger.info(f"Connected via SSM: {endpoint}:{port}")

        except Exception as e:
            logger.error(f"Failed to connect to cache: {e}")

    def get(self, key: str) -> Optional[str]:
        """Get value from cache."""
        if not self._client:
            return None
        try:
            return self._client.get(key)
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None

    def set(self, key: str, value: str, ttl: int = 3600) -> bool:
        """Set value in cache with TTL."""
        if not self._client:
            return False
        try:
            return self._client.setex(key, ttl, value)
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False

    def exists(self, key: str) -> bool:
        """Check if key exists."""
        if not self._client:
            return False
        try:
            return bool(self._client.exists(key))
        except Exception as e:
            logger.error(f"Cache exists error: {e}")
            return False

    def rate_limit(self, key: str, limit: int, window: int = 3600) -> bool:
        """Simple rate limiting. Returns True if action is allowed."""
        cache_key = f"rate_limit:{key}"

        if self.exists(cache_key):
            return False  # Rate limited

        self.set(cache_key, str(int(time.time())), window)
        return True  # Allowed
