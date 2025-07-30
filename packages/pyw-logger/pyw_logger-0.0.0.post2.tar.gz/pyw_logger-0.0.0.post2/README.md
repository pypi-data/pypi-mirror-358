# pyw-logger 📝

[![PyPI](https://img.shields.io/pypi/v/pyw-logger.svg)](https://pypi.org/project/pyw-logger/)
[![CI](https://github.com/pythonWoods/pyw-logger/actions/workflows/ci.yml/badge.svg)](https://github.com/pythonWoods/pyw-logger/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Logger strutturato con **structlog** e output colorato **rich** per il **pythonWoods** ecosystem.  
(campo JSON pronto per log aggregator, tracing OpenTelemetry opzionale).

## Installation (nothing to use yet)

```bash
pip install pyw-logger
```

## Usage

```python
from pyw.logger import get_logger
log = get_logger()
log.info("hello", user="alice")
```

Questo installerà automaticamente:
- `pyw-core` (namespace comune)
- `rich>=13` (output colorato e formattato)
- `structlog>=24` (logging strutturato)

### Extras per observability:

```bash
pip install pyw-logger[otel]    # + OpenTelemetry tracing
pip install pyw-logger[json]    # + JSON formatter per production
pip install pyw-logger[full]    # tutto incluso
```

## Philosophy

* **Structured logging** – JSON-ready per aggregatori (ELK, Grafana).
* **Beautiful output** – Rich formatting per development.
* **Zero config** – funziona out-of-the-box con defaults sensati.
* **Observability ready** – OpenTelemetry integration opzionale.

## Roadmap

- 📝 **Structured logging**: JSON output, custom formatters
- 🎨 **Rich integration**: Colorized console, progress bars
- 🔍 **OpenTelemetry**: Distributed tracing, metrics export
- 📊 **Log aggregation**: ELK stack, Grafana Loki helpers
- ⚡ **Performance**: Async logging, buffering strategies

## Contributing

1. Fork il repo: `pyw-logger`.
2. Crea virtual-env via Poetry: `poetry install && poetry shell`.
3. Lancia linter e mypy: `ruff check . && mypy`.
4. Apri la PR: CI esegue lint, type-check, build.
Felice logging nella foresta di **pythonWoods**! 🌲📝

## Links utili
Documentazione dev (work-in-progress) → https://pythonwoods.dev/docs/pyw-logger/latest/

Issue tracker → https://github.com/pythonWoods/pyw-logger/issues

Changelog → https://github.com/pythonWoods/pyw-logger/releases

© pythonWoods — MIT License