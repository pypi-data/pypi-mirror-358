# Quarkle Monitoring

Minimal shared monitoring and caching for Quarkle services. Provides error tracking, rate limiting, and Slack notifications with automatic AWS discovery.

## Features

- 🚀 **Zero-config**: Auto-discovers Redis cache via AWS SSM
- 📊 **Error tracking**: Deep function call tracking with rate limiting
- 💬 **Slack alerts**: Optional Slack notifications for errors and lifecycle events
- ⚡ **Minimal deps**: Only `redis` + `boto3` core, `slack-sdk` optional
- 🔧 **Flexible**: Works locally (direct Redis) and in AWS (SSM discovery)
- 🧩 **Modular**: Use the orchestrator for simplicity or individual components for advanced control

## Quick Start

### Installation

```bash
# Minimal installation
uv add quarkle-monitoring

# With Slack support
uv add "quarkle-monitoring[slack]"
```

### Simple Usage (Recommended)

````python
from quarkle_monitoring import QuarkleMonitoring

# Initialize the orchestrator
monitoring = QuarkleMonitoring(
    stage="production",
    service_name="my-service",
    slack_token="xoxb-your-token",  # Optional
    slack_channel="C072D4XPLJ0",   # Optional
    version="v1.2.3",              # Optional version

    # Optional: Filter out noisy errors (supports wildcards)
    ignored_error_codes=[404, "4*"],          # Ignore 404s and all 4xx errors
    ignored_files=["*_test.py", "health_check.py"],  # Ignore test files and health checks
    ignored_endpoints=["/health", "/metrics", "/internal/*"],  # Ignore monitoring endpoints
)

# Track errors with automatic Slack alerts
@monitoring.track_errors_decorator()
def my_api_function():
    if something_wrong:
        raise HTTPException(status_code=404, detail="Not found")

# Manual error tracking
def handle_request():
    try:
        # Your logic
        pass
    except Exception as e:
        monitoring.track_error(
            error_code=404,
            endpoint="/api/users",
            user_id="123",
            extra={"custom": "data"}
        )

# Service lifecycle tracking
monitoring.send_lifecycle_alert("startup", "v1.2.3")

### Advanced Usage (Independent Components)

For advanced use cases where you need more control:

```python
from quarkle_monitoring import QuarkleCache, ErrorTracker, SlackNotifier, MemoryCache

# Use individual components
cache = QuarkleCache(stage="production", service_name="my-service")
# OR use in-memory cache for testing/development
# cache = MemoryCache()

error_tracker = ErrorTracker(
    cache=cache,
    service_name="my-service",
    version="v1.2.3",  # Optional

    # Optional: Error filtering (same as QuarkleMonitoring)
    ignored_error_codes=[404, "4*"],          # List of error codes to ignore
    ignored_files=["*_test.py", "health.py"], # List of file patterns to ignore
    ignored_endpoints=["/health", "/internal/*"], # List of endpoint patterns to ignore
)
# OR use without external cache
tracker = ErrorTracker()  # Uses built-in MemoryCache

# Track errors (returns (should_alert, error_data))
should_alert, error_data = tracker.track_error(
    error_code=404,
    endpoint="/api/users",
    user_id="123",
    extra={"custom": "data"}
)

if should_alert and error_data:
    slack.send_error_alert(error_data)

# Use cache directly
cache.set("key", "value", ttl=3600)
cache.rate_limit("user:123", limit=1, window=3600)

# Send lifecycle alerts
slack.send_lifecycle_alert("my-service", "startup", "v1.2.3")
````

### Configuration

#### Environment Variables

```bash
# Redis Connection (for local development)
REDIS_HOST=localhost
REDIS_PORT=6379

# AWS/Production (uses SSM discovery)
STAGE=production
APP_NAME=my-service

# Version (optional - will show "unknown" if not set)
APP_VERSION=v1.2.3
# OR
GIT_HASH=abc123
# OR
BUILD_ID=build-456

# Slack (optional)
SLACK_APP_TOKEN=xoxb-your-slack-bot-token
SLACK_ALERTS_CHANNEL=C072D4XPLJ0
```

#### AWS SSM Parameters

The package automatically discovers Redis cache using these SSM parameters:

```
/quarkle/{stage}/cache/endpoint
/quarkle/{stage}/cache/port
```

#### Version Handling

Version information is used for tracking which version had errors. It's completely optional:

```python
# Priority order:
# 1. Explicit version parameter
monitoring = QuarkleMonitoring(version="v1.2.3")

# 2. Environment variables (APP_VERSION, GIT_HASH, BUILD_ID)
# 3. Defaults to "unknown"
```

## API Reference

### QuarkleMonitoring (Orchestrator)

```python
monitoring = QuarkleMonitoring(
    stage="production",
    service_name="my-service",
    slack_token="xoxb-token",      # Optional
    slack_channel="C072D4XPLJ0",   # Optional
    use_redis=True,                # False for in-memory cache
    version="v1.2.3",              # Optional version

    # Optional: Error filtering (supports wildcards)
    ignored_error_codes=[404, "4*"],          # List of error codes to ignore
    ignored_files=["*_test.py", "health.py"], # List of file patterns to ignore
    ignored_endpoints=["/health", "/internal/*"], # List of endpoint patterns to ignore
)

# Track errors with automatic alerts
monitoring.track_error(404, endpoint="/api/users", send_slack_alert=True)

# Decorator for automatic error tracking
@monitoring.track_errors_decorator(send_slack_alert=True)
def my_function():
    pass

# Send lifecycle alerts
monitoring.send_lifecycle_alert("startup", "v1.2.3")

# Access individual components
monitoring.cache_client    # QuarkleCache or MemoryCache
monitoring.error_client    # ErrorTracker
monitoring.slack_client    # SlackNotifier
```

### Individual Components

#### QuarkleCache

```python
cache = QuarkleCache(stage="production", service_name="my-service")

# Basic operations
cache.get("key")                           # Get value
cache.set("key", "value", ttl=3600)       # Set with TTL
cache.exists("key")                        # Check existence
cache.rate_limit("action", 1, 3600)       # Rate limiting
```

#### ErrorTracker

```python
# Can use any cache that implements rate_limit() and set()
tracker = ErrorTracker(
    cache=cache,
    service_name="my-service",
    version="v1.2.3",  # Optional

    # Optional: Error filtering (same as QuarkleMonitoring)
    ignored_error_codes=[404, "4*"],          # List of error codes to ignore
    ignored_files=["*_test.py", "health.py"], # List of file patterns to ignore
    ignored_endpoints=["/health", "/internal/*"], # List of endpoint patterns to ignore
)
# OR use without external cache
tracker = ErrorTracker()  # Uses built-in MemoryCache

# Track errors (returns (should_alert, error_data))
should_alert, error_data = tracker.track_error(
    error_code=404,
    endpoint="/api/users",
    user_id="123",
    extra={"custom": "data"}
)
```

#### SlackNotifier

```python
slack = SlackNotifier(token="xoxb-...", channel="C072D4XPLJ0")

# Send error alert
slack.send_error_alert(error_data)

# Send lifecycle alert
slack.send_lifecycle_alert("my-service", "startup", "v1.2.3")
```

#### MemoryCache

```python
# Simple in-memory cache for development/testing
cache = MemoryCache()
cache.rate_limit("key", 1, 3600)
cache.set("key", "value", 3600)
```

#### Version Utility

```python
from quarkle_monitoring import get_version_info

# Get version from various sources
version = get_version_info("v1.2.3")  # Explicit
version = get_version_info()          # From env vars or "unknown"
```

## Development

```bash
# Install with dev dependencies
uv add "quarkle-monitoring[dev,slack]"

# Run tests
make test

# Format code
make format

# Lint
make lint

# Build package
make build

# Publish to PyPI
make publish
```

## License

MIT License
