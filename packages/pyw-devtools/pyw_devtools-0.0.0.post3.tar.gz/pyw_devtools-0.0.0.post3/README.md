# pyw-devtools 🛠️
[![PyPI](https://img.shields.io/pypi/v/pyw-devtools.svg)](https://pypi.org/project/pyw-devtools/)
[![CI](https://github.com/pythonWoods/pyw-devtools/actions/workflows/ci.yml/badge.svg)](https://github.com/pythonWoods/pyw-devtools/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Bundle "ready-to-hack" per sviluppatori nel **pythonWoods** ecosystem.  
(tutto quello che serve per CLI apps, config, logging, secrets).

## Components

| Package | Description | Status |
|---------|-------------|--------|
| **pyw-core** | Namespace & common utilities | placeholder `0.0.0` |
| **pyw-logger** | Structured logging (rich + structlog) | placeholder `0.0.0` |
| **pyw-fs** | Filesystem abstraction (local/S3/GCS) | placeholder `0.0.0` |
| **pyw-secret** | Secret backends (.env, Vault, SSM) | placeholder `0.0.0` |
| **pyw-cli** | Typer CLI scaffolding | placeholder `0.0.0` |
| **pyw-devtools** | Meta-package: developer bundle | `0.0.1` |

## Installation (nothing to use yet)

```bash
pip install pyw-devtools
```

Questo installerà automaticamente tutto il necessario per development:
- `pyw-core` (namespace comune)
- `pyw-logger` (rich + structlog)
- `pyw-fs` (fsspec per S3/GCS)
- `pyw-secret` (python-dotenv + extras)
- `pyw-cli` (typer[all])

## Usage

```python
from pyw.logger import get_logger
from pyw.fs import FileSystem
from pyw.secret import get_secret
from pyw.cli import create_app

log = get_logger()
fs = FileSystem("s3://bucket")
api_key = get_secret("API_KEY")
app = create_app()
```

## Philosophy

* **Batteries included** – tutto per sviluppare CLI apps moderne.
* **Cloud-native** – S3, secrets manager, structured logging.
* **Type-safe** – API completamente typed con Pydantic.
* **Zero config** – defaults sensati, personalizzabile quando serve.

## Roadmap

- 📝 **Logging**: JSON output, OpenTelemetry tracing
- 📁 **Filesystem**: Multi-cloud support, caching, sync
- 🔐 **Secrets**: Vault, AWS SSM, Azure KeyVault
- 🖥️ **CLI**: Interactive prompts, progress bars, subcommands
- ⚙️ **Config**: YAML/TOML parsing, validation, environments

## Contributing

1. Fork il repo del modulo che ti interessa (`pyw-logger`, `pyw-fs`, etc.).
2. Crea virtual-env via Poetry: `poetry install && poetry shell`.
3. Lancia linter e mypy: `ruff check . && mypy`.
4. Apri la PR: CI esegue lint, type-check, build.

Felice sviluppo nella foresta di **pythonWoods**! 🌲🛠️

## Links utili
Documentazione dev (work-in-progress) → https://pythonwoods.dev/docs/pyw-devtools/latest/

Issue tracker → https://github.com/pythonWoods/pyw-devtools/issues

Changelog → https://github.com/pythonWoods/pyw-devtools/releases

© pythonWoods — MIT License