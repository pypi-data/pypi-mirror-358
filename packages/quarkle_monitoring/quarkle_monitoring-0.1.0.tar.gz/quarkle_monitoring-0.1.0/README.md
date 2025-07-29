# Quarkle Monitoring

Minimal shared monitoring and caching for Quarkle services. Provides error tracking, rate limiting, and Slack notifications with automatic AWS discovery.

## Features

- 🚀 **Zero-config**: Auto-discovers Redis cache via AWS SSM
- 📊 **Error tracking**: Deep function call tracking with rate limiting
- 💬 **Slack alerts**: Optional Slack notifications for errors and lifecycle events
- ⚡ **Minimal deps**: Only `redis` + `boto3` core, `slack-sdk` optional
- 🔧 **Flexible**: Works locally (direct Redis) and in AWS (SSM discovery)

## Quick Start

### Installation

```bash
# Minimal installation
uv add quarkle-monitoring

# With Slack support
uv add "quarkle-monitoring[slack]"
```

### Basic Usage

```python
from quarkle_monitoring import QuarkleCache, ErrorTracker, SlackNotifier

# Initialize components
cache = QuarkleCache(stage="production", service_name="my-service")
error_tracker = ErrorTracker(cache)
slack = SlackNotifier()  # Optional

# Track errors automatically
@error_tracker.track_errors
def my_api_function():
    # Your code here
    if something_wrong:
        raise HTTPException(status_code=404, detail="Not found")

# Manual error tracking
def handle_request():
    try:
        # Your logic
        pass
    except Exception as e:
        if error_tracker.track_error(404, endpoint="/api/users", user_id="123"):
            # Send alert only if not rate-limited
            error_data = {
                "service": "my-service",
                "error_code": 404,
                "context": {"function": "handle_request"},
                "git_hash": "abc123",
                "timestamp": time.time()
            }
            slack.send_error_alert(error_data)

# Service lifecycle tracking
slack.send_lifecycle_alert("my-service", "startup", "abc123")
```

### Configuration

#### Environment Variables

```bash
# Redis Connection (for local development)
REDIS_HOST=localhost
REDIS_PORT=6379

# AWS/Production (uses SSM discovery)
STAGE=production
APP_NAME=my-service

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

## API Reference

### QuarkleCache

```python
cache = QuarkleCache(stage="production", service_name="my-service")

# Basic operations
cache.get("key")                           # Get value
cache.set("key", "value", ttl=3600)       # Set with TTL
cache.exists("key")                        # Check existence
cache.rate_limit("action", 1, 3600)       # Rate limiting
```

### ErrorTracker

```python
tracker = ErrorTracker(cache, service_name="my-service")

# Track errors (returns True if alert should be sent)
should_alert = tracker.track_error(
    error_code=404,
    endpoint="/api/users",
    user_id="123",
    extra={"custom": "data"}
)
```

### SlackNotifier

```python
slack = SlackNotifier(token="xoxb-...", channel="C072D4XPLJ0")

# Send error alert
slack.send_error_alert(error_data)

# Send lifecycle alert
slack.send_lifecycle_alert("my-service", "startup", "git-hash")
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
