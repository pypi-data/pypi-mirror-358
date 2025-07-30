# pyw-core 🌐
[![PyPI](https://img.shields.io/pypi/v/pyw-core.svg)](https://pypi.org/project/pyw-core/)
[![CI](https://github.com/pythonWoods/pyw-core/actions/workflows/ci.yml/badge.svg)](https://github.com/pythonWoods/pyw-core/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
> Namespace seed & common utilities for the **pythonWoods** ecosystem.

## Components

| Package | Description | Status |
|---------|-------------|--------|
| **pyw-core** | Structured + colorful logging | placeholder `0.0.0` |
| **pyw-fs** | Unified filesystem (local/S3/GCS) | 0.0.0 |
| **pyw-secret** | Secret back-ends (.env, Vault, SSM) | 0.0.0 |
| **pyw-cli** | Typer CLI scaffold | 0.0.0 |
| **pyw-music21** | Music21 stubs & helpers | 0.0.0 |
| **pyw-musicparser** | Parse MIDI/Lilypond | 0.0.0 |
| **pyw-core** | Meta-package: install everything | 0.0.0 |
| **pyw-devtools** | Bundle for devs (logger, fs, cli, secret) | 0.0.0 |

## Philosophy

* **Namespace package** – `import pyw.*` per evitare conflitti.
* **Small, composable modules** – scegli solo ciò che ti serve.
* **Typed APIs** – Pydantic / dataclass per zero sorprese.
* **No heavy deps by default** – le librerie “costose” (Torch, OpenCV) sono extra.

### Installation (nothing to use yet)

```bash
pip install pyw-core
```

*(Core è quasi vuoto: fornisce solo il namespace e helper comuni.)*

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