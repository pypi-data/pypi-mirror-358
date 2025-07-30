# pyw-core 🌐
[![PyPI](https://img.shields.io/pypi/v/pyw-core.svg)](https://pypi.org/project/pyw-core/)
[![CI](https://github.com/pythonWoods/pyw-core/actions/workflows/ci.yml/badge.svg)](https://github.com/pythonWoods/pyw-core/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
> Namespace seed & common utilities for the **pythonWoods** ecosystem.

## Ecosystem Overview

| Package | Description | Status |
|---------|-------------|--------|
| **pyw-core** | Namespace & common utilities | placeholder `0.0.0` |
| **pyw-logger** | Structured logging (rich + structlog) | placeholder `0.0.0` |
| **pyw-fs** | Unified filesystem (local/S3/GCS) | placeholder `0.0.0` |
| **pyw-secret** | Secret backends (.env, Vault, SSM) | placeholder `0.0.0` |
| **pyw-cli** | Typer CLI scaffolding | placeholder `0.0.0` |
| **pyw-config** | Configuration utilities | placeholder `0.0.0` |
| **pyw-vision** | Vision utilities & helpers | placeholder `0.0.0` |
| **pyw-motion** | Motion detection & tracking | placeholder `0.0.0` |
| **pyw-music21** | Music21 stubs & helpers | placeholder `0.0.0` |
| **pyw-musicparser** | Parse MIDI/Lilypond | placeholder `0.0.0` |

## Bundle Packages

| Bundle | Description | Includes |
|--------|-------------|----------|
| **pyw-devtools** | Developer toolkit | logger, fs, cli, secret |
| **pyw-music** | Music processing | music21, musicparser |
| **pyw-cv** | Computer vision | vision, motion |

## Philosophy

* **Namespace package** – `import pyw.*` per evitare conflitti.
* **Small, composable modules** – scegli solo ciò che ti serve.
* **Typed APIs** – Pydantic / dataclass per zero sorprese.
* **No heavy deps by default** – le librerie "costose" (Torch, OpenCV) sono extra.

## Installation (nothing to use yet)

```bash
pip install pyw-core
```

*(Core è quasi vuoto: fornisce solo il namespace e helper comuni.)*

## Usage

```python
from pyw.core import BaseConfig, TypedDict
from pyw.core.utils import ensure_list, deep_merge

# Common utilities available across all pyw modules
config = BaseConfig()
data = ensure_list("single_item")  # → ["single_item"]
merged = deep_merge(dict1, dict2)
```

## Bundle Installation

Per installare gruppi di moduli correlati:

```bash
pip install pyw-devtools  # logger + fs + cli + secret
pip install pyw-music     # music21 + musicparser  
pip install pyw-cv        # vision + motion
```

## Roadmap

- 🏗️ **Core utilities**: Config base classes, type helpers
- 📦 **Namespace management**: Plugin discovery, module registry
- 🔧 **Development tools**: Testing utilities, debugging helpers
- 📚 **Documentation**: Sphinx integration, API reference
- 🎯 **Quality**: Type stubs, linting rules, best practices

## Contributing

1. Fork il repo del modulo che ti interessa (`pyw-fs`, ecc.).
2. Crea virtual-env via Poetry: `poetry install && poetry shell`.
3. Lancia linter e mypy: `ruff check . && mypy`.
4. Apri la PR: CI esegue lint, type-check, build.

Felice coding nella foresta di **pythonWoods**! 🌲🐾

## Links utili
Documentazione dev (work-in-progress) → https://pythonwoods.dev/docs/pyw-core/latest/

Issue tracker → https://github.com/pythonWoods/pyw-core/issues

Changelog → https://github.com/pythonWoods/pyw-core/releases

© pythonWoods — MIT License