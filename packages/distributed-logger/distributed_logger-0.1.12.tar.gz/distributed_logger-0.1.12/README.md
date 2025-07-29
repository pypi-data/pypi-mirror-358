# Distributed Logger

A lightweight logging system with Kafka support for auditing and debugging. Provides middleware for request auditing that can be used with any WSGI/ASGI framework.

## Features

- Request auditing middleware
- Support for multiple logging backends:
  - Kafka
  - Simple console logging
  - (More backends coming soon)
- Simple environment-based configuration
- Framework agnostic (works with Django, Flask, FastAPI, etc.)

## Installation

```bash
pip install distributed-logger
```

## Quick Start

1. Add the middleware to your framework:

For Django:
```python
MIDDLEWARE = [
    ...
    'distributed_logger.middleware.log_middleware.AuditLogMiddleware',
]
```

2. Set environment variables for configuration:

```bash
# For Kafka logging
export BROKER_TYPE=KAFKA
export KAFKA_BOOTSTRAP_SERVERS=localhost:9092
export KAFKA_TOPIC=audit_logs
export KAFKA_CLIENT_ID=your_app_name

# For simple console logging
export BROKER_TYPE=SIMPLE
```

That's it! The middleware will automatically log all requests.

## Usage Examples

### Custom Logging

```python
from distributed_logger.loggers import KafkaLogger
from distributed_logger.models import LogInfo
from distributed_logger.models.config import KafkaConfig

# Create a logger instance
config = KafkaConfig(
    broker_type="KAFKA",
    bootstrap_servers=["localhost:9092"],
    topic="audit_logs"
)
logger = KafkaLogger(config=config)

# Log some information
log_info = LogInfo(
    ip_address="127.0.0.1",
    user_id="user123",
    request_time="2024-01-01 12:00:00",
    action="custom_action",
    request_data={"key": "value"}
)
logger.publish(log_info)
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| BROKER_TYPE | Type of logging backend ('KAFKA' or 'SIMPLE') | 'SIMPLE' |
| KAFKA_BOOTSTRAP_SERVERS | Comma-separated list of Kafka brokers | 'localhost:9092' |
| KAFKA_TOPIC | Kafka topic for logs | 'audit_logs' |
| KAFKA_CLIENT_ID | Client ID for Kafka producer | None |

## Development

To set up for development:

```bash
# Clone the repository
git clone https://github.com/arjun-navya/distributed-logger.git
cd distributed-logger

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. # logger
