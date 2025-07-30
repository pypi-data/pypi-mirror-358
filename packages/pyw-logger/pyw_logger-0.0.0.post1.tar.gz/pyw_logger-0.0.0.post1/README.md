# pyw-logger 📝

[![PyPI](https://img.shields.io/pypi/v/pyw-logger.svg)](https://pypi.org/project/pyw-logger/)
[![CI](https://github.com/pythonWoods/pyw-logger/actions/workflows/ci.yml/badge.svg)](https://github.com/pythonWoods/pyw-logger/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)


Logger strutturato con **structlog** e output colorato **rich**  
(campo JSON pronto per log aggregator, tracing OpenTelemetry opzionale).

```bash
pip install pyw-logger
````

```python
from pyw.logger import get_logger
log = get_logger()
log.info("hello", user="alice")
```

* Dipendenze minime: `rich`, `structlog`
* Extra: `pyw-logger[otel]` → invia span OpenTelemetry.


## Links utili
Documentazione dev (work-in-progress) → https://pythonwoods.dev/docs/pyw-logger/latest/

Issue tracker → https://github.com/pythonWoods/pyw-logger/issues

Changelog → https://github.com/pythonWoods/pyw-logger/releases

© pythonWoods — MIT License