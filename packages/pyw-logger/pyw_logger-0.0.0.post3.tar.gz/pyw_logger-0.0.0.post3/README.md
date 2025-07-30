# pyw-logger 📝
[![PyPI](https://img.shields.io/pypi/v/pyw-logger.svg)](https://pypi.org/project/pyw-logger/)
[![CI](https://github.com/pythonWoods/pyw-logger/actions/workflows/ci.yml/badge.svg)](https://github.com/pythonWoods/pyw-logger/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> Structured logging con **structlog** e output colorato **rich** per il **pythonWoods** ecosystem.

## Overview

**pyw-logger** porta il logging strutturato nell'ecosistema pythonWoods, combinando la potenza di structlog per la strutturazione dei dati con la bellezza di rich per l'output console. Progettato per essere production-ready con supporto JSON nativo e integrazione OpenTelemetry opzionale.

## Installation

```bash
pip install pyw-logger
```

Questo installerà automaticamente:
- `pyw-core` (namespace comune)
- `rich>=13` (output colorato e formattato)  
- `structlog>=24` (logging strutturato)

### Extras per observability avanzata:

```bash
pip install pyw-logger[otel]    # + OpenTelemetry tracing
pip install pyw-logger[json]    # + JSON formatter per production
pip install pyw-logger[sentry]  # + Sentry integration
pip install pyw-logger[full]    # tutto incluso
```

## Quick Start

### 🚀 Basic Usage

```python
from pyw.logger import get_logger

# Logger con configurazione automatica
log = get_logger(__name__)

# Logging strutturato
log.info("User login", user_id=12345, ip="192.168.1.1")
log.warning("High memory usage", memory_percent=85.2, threshold=80)
log.error("Database connection failed", 
          host="db.example.com", 
          error="Connection timeout",
          retry_count=3)
```

### 🎨 Rich Console Output

```python
from pyw.logger import get_logger, configure_logger

# Console colorato per development
configure_logger(
    level="DEBUG",
    format="rich",  # rich, json, minimal
    show_time=True,
    show_level=True,
    show_path=True
)

log = get_logger("myapp")
log.debug("Debugging info", data={"key": "value"})
log.info("✨ Application started", version="1.2.3")
log.success("✅ Task completed", duration="2.3s")  # Custom level
```

### 📊 Production JSON Logging

```python
from pyw.logger import configure_logger, get_logger

# JSON output per production
configure_logger(
    format="json",
    level="INFO",
    include_extra=True,
    timestamp_format="iso"
)

log = get_logger("api")
log.info("Request processed", 
         method="POST", 
         endpoint="/users", 
         response_time=0.125,
         status_code=201)

# Output: {"timestamp": "2024-01-15T10:30:45Z", "level": "info", 
#          "message": "Request processed", "method": "POST", ...}
```

## Advanced Features

### 🔧 Custom Configuration

```python
from pyw.logger import LoggerConfig, setup_logging

config = LoggerConfig(
    # Output settings
    format="rich",              # rich, json, minimal, custom
    level="INFO",               # DEBUG, INFO, WARNING, ERROR
    
    # Console appearance
    show_time=True,
    show_level=True, 
    show_path=True,
    show_thread=False,
    
    # Structured data
    include_caller=True,
    include_process=True,
    include_extra=True,
    
    # Performance
    async_logging=False,
    buffer_size=1000,
    flush_interval=5.0,
    
    # File output
    file_path="logs/app.log",
    file_rotation="100MB",
    file_retention="30 days",
    
    # Filtering
    ignored_loggers=["urllib3", "requests"],
    rate_limit={"max_calls": 100, "period": 60}
)

setup_logging(config)
```

### 🏷️ Context & Correlation

```python
from pyw.logger import get_logger, LogContext

log = get_logger("service")

# Context persistente
with LogContext(request_id="req-123", user_id=456):
    log.info("Processing request")  # Include automaticamente request_id e user_id
    
    # Nested context
    with LogContext(operation="database_query"):
        log.debug("Executing query", table="users")
        # Include: request_id, user_id, operation

# Correlation IDs automatici
from pyw.logger.middleware import correlation_middleware

@correlation_middleware
def my_function():
    log = get_logger()
    log.info("Function called")  # Auto-include correlation_id
```

### 📈 Metrics & Performance

```python
from pyw.logger import get_logger, log_performance, log_metrics

log = get_logger("performance")

# Performance tracking
@log_performance(logger=log, threshold=1.0)
def slow_operation():
    import time
    time.sleep(2.0)

slow_operation()  # Logs: "slow_operation took 2.001s (exceeded threshold 1.0s)"

# Custom metrics
log_metrics(
    name="api_response_time",
    value=0.145,
    unit="seconds",
    tags={"endpoint": "/users", "method": "GET"}
)

# Memory usage tracking
from pyw.logger.utils import log_memory_usage

with log_memory_usage(log, "data_processing"):
    big_data = list(range(1000000))
    process_data(big_data)
```

### 🔍 OpenTelemetry Integration

```python
from pyw.logger import get_logger, configure_otel_logging
from opentelemetry import trace

# Setup OpenTelemetry
configure_otel_logging(
    service_name="my-service",
    service_version="1.0.0",
    endpoint="http://jaeger:14268/api/traces"
)

log = get_logger("traced")
tracer = trace.get_tracer(__name__)

# Automatic trace correlation
with tracer.start_as_current_span("user_operation") as span:
    span.set_attribute("user.id", 123)
    log.info("User operation started")  # Include trace_id e span_id automaticamente
```

### 🎯 Custom Processors & Formatters

```python
from pyw.logger import get_logger, add_processor, CustomFormatter
import structlog

# Custom processor
def add_hostname(logger, method_name, event_dict):
    import socket
    event_dict["hostname"] = socket.gethostname()
    return event_dict

add_processor(add_hostname)

# Custom formatter
class SlackFormatter(CustomFormatter):
    def format(self, record):
        if record.level >= logging.ERROR:
            return f"🚨 *ERROR*: {record.message}"
        return f"📝 {record.message}"

# Slack notifications per errori critici
from pyw.logger.handlers import SlackHandler

slack_handler = SlackHandler(
    webhook_url="https://hooks.slack.com/...",
    formatter=SlackFormatter(),
    level="ERROR"
)

log = get_logger("alerts")
log.add_handler(slack_handler)
```

## Integration Patterns

### 🌐 Web Framework Integration

```python
# FastAPI middleware
from pyw.logger.integrations import FastAPILoggingMiddleware

app = FastAPI()
app.add_middleware(FastAPILoggingMiddleware, 
                   logger_name="api",
                   include_request_body=True,
                   include_response_body=False)

# Django setup
# settings.py
LOGGING_CONFIG = None
from pyw.logger.integrations.django import setup_django_logging
setup_django_logging(level="INFO", format="json")

# Flask integration
from pyw.logger.integrations import FlaskLoggingHandler
from flask import Flask

app = Flask(__name__)
app.logger.addHandler(FlaskLoggingHandler(format="rich"))
```

### 🧪 Testing & Development

```python
from pyw.logger import get_logger
from pyw.logger.testing import LogCapture, assert_logged

log = get_logger("test")

def test_user_creation():
    with LogCapture() as captured:
        create_user("alice")
        
        # Assert sui log
        assert_logged(captured, level="INFO", message="User created")
        assert_logged(captured, user="alice", event="user_creation")
        
        # Pattern matching
        assert captured.contains_pattern(r"User \w+ created successfully")

# Mock logging per unit tests
from pyw.logger.testing import mock_logger

@mock_logger("mymodule.log")
def test_with_mocked_logging():
    # Logging è disabilitato durante il test
    pass
```

### 📦 Library Integration

```python
from pyw.logger import silence_logger, redirect_logger

# Silenzia logger rumorosi
silence_logger("urllib3.connectionpool")
silence_logger("requests.packages.urllib3")

# Redirect a pyw-logger
redirect_logger("sqlalchemy.engine", level="WARNING")

# Batch configuration
from pyw.logger import configure_third_party_loggers

configure_third_party_loggers({
    "requests": {"level": "WARNING"},
    "urllib3": {"level": "ERROR"},
    "boto3": {"level": "INFO", "format": "json"}
})
```

## Configuration Recipes

### 🏭 Production Setup

```python
from pyw.logger import ProductionConfig

# Configurazione production-ready
config = ProductionConfig(
    service_name="my-api",
    version="1.2.3",
    environment="production",
    
    # JSON logging per aggregatori
    format="json",
    level="INFO",
    
    # File rotation
    log_file="/var/log/myapp/app.log",
    max_file_size="100MB",
    backup_count=5,
    
    # Performance
    async_logging=True,
    buffer_size=10000,
    
    # Observability
    include_trace_id=True,
    include_span_id=True,
    
    # Security
    sanitize_sensitive_data=True,
    sensitive_fields=["password", "token", "secret"]
)

setup_logging(config)
```

### 🧑‍💻 Development Setup

```python
from pyw.logger import DevelopmentConfig

config = DevelopmentConfig(
    # Rich console output
    format="rich",
    level="DEBUG",
    
    # Verbose information
    show_caller=True,
    show_thread=True,
    show_process=True,
    
    # File logging opzionale
    also_log_to_file=True,
    file_path="debug.log"
)

setup_logging(config)
```

### 🐳 Container/Kubernetes Setup

```python
from pyw.logger import ContainerConfig

config = ContainerConfig(
    # Structured JSON per container logs
    format="json",
    level="INFO",
    
    # Kubernetes metadata
    include_pod_name=True,
    include_namespace=True,
    include_node_name=True,
    
    # Health checks
    health_check_endpoint="/health/logging",
    
    # Graceful shutdown
    flush_on_exit=True,
    shutdown_timeout=5.0
)
```

## CLI Tools

```bash
# Analyze log files
pyw-logger analyze logs/app.log --format=json --stats

# Real-time log monitoring
pyw-logger tail logs/app.log --filter="level>=WARNING" --follow

# Convert log formats
pyw-logger convert input.log --from=rich --to=json --output=structured.json

# Test logging configuration
pyw-logger test-config config.yaml --dry-run

# Performance benchmarks
pyw-logger benchmark --format=json --messages=10000 --concurrent=10
```

## Performance & Best Practices

### ⚡ Performance Tips

```python
from pyw.logger import get_logger, lazy_format

log = get_logger("performance")

# Lazy evaluation per expensive operations
log.debug(lazy_format("Complex data: {}", lambda: expensive_computation()))

# Conditional logging
if log.isEnabledFor(logging.DEBUG):
    complex_data = process_complex_data()
    log.debug("Debug info", data=complex_data)

# Batch logging per high-throughput
from pyw.logger import BatchLogger

batch_log = BatchLogger("batch", batch_size=100, flush_interval=1.0)
for i in range(1000):
    batch_log.info("Processing item", item_id=i)
```

### 🔒 Security Considerations

```python
from pyw.logger import SecureLogger

# Logger con sanitization automatica
secure_log = SecureLogger(
    "secure",
    sensitive_patterns=[
        r"password=\w+",
        r"token=[A-Za-z0-9]+",
        r"\d{4}-\d{4}-\d{4}-\d{4}"  # Credit card pattern
    ],
    replacement="[REDACTED]"
)

secure_log.info("User login", username="alice", password="secret123")
# Output: "User login", username="alice", password="[REDACTED]"
```

## Ecosystem Integration

**pyw-logger** integra nativamente con altri moduli pythonWoods:

```python
# Con pyw-config
from pyw.config import get_config
from pyw.logger import configure_from_config

config = get_config()
configure_from_config(config.logging)

# Con pyw-secret
from pyw.secret import get_secret
from pyw.logger.handlers import SlackHandler

slack_webhook = get_secret("SLACK_WEBHOOK_URL")
handler = SlackHandler(webhook_url=slack_webhook)

# Con pyw-fs per log remoti
from pyw.fs import get_filesystem
from pyw.logger.handlers import RemoteHandler

s3_fs = get_filesystem("s3://my-logs-bucket")
remote_handler = RemoteHandler(filesystem=s3_fs, path="logs/app-{date}.log")
```

## Troubleshooting

### 🐛 Common Issues

```python
from pyw.logger import diagnose_logging, LoggingHealthCheck

# Diagnosi automatica
issues = diagnose_logging()
for issue in issues:
    print(f"⚠️  {issue.message}")
    print(f"💡 {issue.suggestion}")

# Health check
health = LoggingHealthCheck()
status = health.check()
print(f"Logging status: {status.overall}")
for check in status.checks:
    print(f"  {check.name}: {check.status}")
```

### 📊 Monitoring & Alerts

```python
from pyw.logger import LoggingMetrics

metrics = LoggingMetrics()

# Metriche automatiche
print(f"Messages/sec: {metrics.messages_per_second}")
print(f"Error rate: {metrics.error_rate:.2%}")
print(f"Memory usage: {metrics.memory_usage_mb:.1f} MB")

# Alert su soglie
metrics.add_alert(
    condition="error_rate > 0.05",  # 5% error rate
    action="send_slack_notification",
    cooldown=300  # 5 minutes
)
```

## Philosophy

* **Structured first** – JSON-ready per aggregatori (ELK, Grafana, Datadog)
* **Beautiful development** – Rich formatting per console development
* **Zero config magic** – funziona out-of-the-box con defaults intelligenti
* **Observability native** – OpenTelemetry, metrics e tracing integrati
* **Performance conscious** – async logging, buffering, rate limiting
* **Security aware** – automatic data sanitization, sensitive field redaction

## Roadmap

- 📝 **Enhanced structuring**: Custom processors, dynamic fields
- 🎨 **Rich improvements**: Interactive console, log browser
- 🔍 **Advanced observability**: Custom metrics, health monitoring
- 📊 **Better aggregation**: Direct ELK/Grafana integrations
- ⚡ **Performance optimization**: Zero-copy logging, memory pools
- 🤖 **AI-powered insights**: Log anomaly detection, smart alerting
- 🔐 **Enhanced security**: Encryption at rest, compliance helpers

## Contributing

**pyw-logger** è un componente core dell'ecosistema pythonWoods:

1. **Fork & Clone**: `git clone https://github.com/pythonWoods/pyw-logger.git`
2. **Development setup**: `poetry install && poetry shell`
3. **Quality checks**: `ruff check . && mypy && pytest --cov`
4. **Integration tests**: Testa con altri moduli pyw
5. **Performance benchmarks**: `pytest benchmarks/ --benchmark-only`
6. **Documentation**: Aggiorna esempi e API docs
7. **Pull Request**: CI esegue test completi + performance regression

### Development Commands

```bash
# Linting completo
make lint

# Test con coverage
make test-coverage

# Performance benchmarks
make benchmark

# Documentation build
make docs-build

# Release preparation
make pre-release
```

## Architecture Notes

```
pyw-logger/
├── pyw/
│   └── logger/
│       ├── __init__.py          # Public API
│       ├── core.py              # Core logger setup
│       ├── config.py            # Configuration classes
│       ├── formatters/          # Rich, JSON, custom formatters
│       ├── handlers/            # File, remote, third-party handlers
│       ├── processors/          # Structlog processors
│       ├── integrations/        # Framework integrations
│       ├── testing.py           # Test utilities
│       ├── utils.py             # Helper functions
│       └── cli.py               # Command-line tools
├── benchmarks/                  # Performance tests
├── examples/                    # Usage examples
└── tests/                       # Test suite
```

Felice logging nella foresta di **pythonWoods**! 🌲📝

## Links utili

Documentazione dev (work-in-progress) → https://pythonwoods.dev/docs/pyw-logger/latest/

Issue tracker → https://github.com/pythonWoods/pyw-logger/issues

Changelog → https://github.com/pythonWoods/pyw-logger/releases

Performance benchmarks → https://pythonwoods.dev/benchmarks/pyw-logger/

© pythonWoods — MIT License