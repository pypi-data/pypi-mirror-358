# pyw-core 🌐
[![PyPI](https://img.shields.io/pypi/v/pyw-core.svg)](https://pypi.org/project/pyw-core/)
[![CI](https://github.com/pythonWoods/pyw-core/actions/workflows/ci.yml/badge.svg)](https://github.com/pythonWoods/pyw-core/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> Namespace seed & common utilities for the **pythonWoods** ecosystem.

## Overview

**pyw-core** è il cuore dell'ecosistema pythonWoods, fornendo il namespace condiviso, utilities comuni e le basi architetturali per tutti i moduli. Anche se minimalista per design, è il fondamento che garantisce coerenza e interoperabilità tra tutti i package.

## Ecosystem Overview

| Package | Description | Status |
|---------|-------------|--------|
| **pyw-core** | Namespace & common utilities | `0.0.0` |
| **pyw-logger** | Structured logging (rich + structlog) | `0.0.0` |
| **pyw-fs** | Unified filesystem (local/S3/GCS) | `0.0.0` |
| **pyw-secret** | Secret backends (.env, Vault, SSM) | `0.0.0` |
| **pyw-cli** | Typer CLI scaffolding | `0.0.0` |
| **pyw-config** | Configuration utilities | `0.0.0` |
| **pyw-vision** | Vision utilities & helpers | `0.0.0` |
| **pyw-motion** | Motion detection & tracking | `0.0.0` |
| **pyw-music21** | Music21 stubs & helpers | `0.0.0` |
| **pyw-musicparser** | Parse MIDI/Lilypond | `0.0.0` |

## Bundle Packages

| Bundle | Description | Includes |
|--------|-------------|----------|
| **pyw-devtools** | Developer toolkit | logger, fs, cli, secret, config |
| **pyw-music** | Music processing | music21, musicparser |
| **pyw-cv** | Computer vision | vision, motion |

## Philosophy

* **Namespace package** – `import pyw.*` per evitare conflitti e garantire coerenza
* **Small, composable modules** – scegli solo ciò che ti serve, zero bloat
* **Typed APIs** – Pydantic models e type hints per zero sorprese
* **No heavy deps by default** – librerie "pesanti" (Torch, OpenCV) come extras opzionali
* **Interoperability-first** – tutti i moduli condividono pattern e utilities comuni

## Installation

```bash
pip install pyw-core
```

**pyw-core** è intenzionalmente minimalista: fornisce solo il namespace e utilities fondamentali condivise dall'ecosistema.

## Core Features

### 🏗️ Base Classes

```python
from pyw.core import BaseConfig, BaseModel
from pyw.core.types import PathLike, JsonDict

class MyConfig(BaseConfig):
    """Configurazione con validazione type-safe."""
    name: str
    debug: bool = False
    paths: list[PathLike] = []

class DataModel(BaseModel):
    """Modello dati con serializzazione automatica."""
    id: int
    metadata: JsonDict = {}
```

### 🔧 Common Utilities

```python
from pyw.core.utils import (
    ensure_list, deep_merge, safe_import,
    classproperty, deprecated
)

# List normalization
items = ensure_list("single_item")  # → ["single_item"]
items = ensure_list(["already", "list"])  # → ["already", "list"]

# Deep dictionary merging
config = deep_merge(
    {"db": {"host": "localhost", "port": 5432}},
    {"db": {"port": 3306, "ssl": True}}
)
# → {"db": {"host": "localhost", "port": 3306, "ssl": True}}

# Safe imports con fallback
requests = safe_import("requests", fallback_message="pip install requests")

# Class properties
class MyClass:
    @classproperty
    def version(cls):
        return "1.0.0"

# Deprecation warnings
@deprecated("Use new_function() instead", version="2.0.0")
def old_function():
    pass
```

### 📦 Plugin Discovery

```python
from pyw.core.plugins import discover_plugins, load_plugin

# Trova tutti i plugin pyw installati
plugins = discover_plugins("pyw.*")

# Carica plugin specifico
logger_plugin = load_plugin("pyw.logger")
```

### 🔍 Type Utilities

```python
from pyw.core.types import (
    PathLike, JsonDict, OptionalStr,
    Singleton, classproperty
)
from typing import Any

# Type aliases comuni
def process_file(path: PathLike) -> JsonDict:
    """Accetta str, Path, o file-like objects."""
    pass

# Singleton pattern
class DatabaseConnection(Singleton):
    def __init__(self):
        self.connected = False

# Sempre la stessa istanza
db1 = DatabaseConnection()
db2 = DatabaseConnection()
assert db1 is db2
```

### ⚡ Performance Utilities

```python
from pyw.core.performance import (
    timer, cache_result, rate_limit,
    memory_usage
)
import time

# Timing decorator
@timer
def slow_function():
    time.sleep(1)
    return "done"

result = slow_function()  # Logs: "slow_function took 1.002s"

# Result caching
@cache_result(ttl=300)  # Cache for 5 minutes
def expensive_computation(x: int) -> int:
    return x ** 2

# Rate limiting
@rate_limit(calls=10, period=60)  # Max 10 calls/minute
def api_call():
    pass

# Memory monitoring
with memory_usage() as mem:
    big_list = list(range(1000000))
print(f"Memory used: {mem.peak_mb:.1f} MB")
```

## Integration Patterns

### 🔗 Module Integration

```python
# Pattern per moduli pyw
from pyw.core import BaseModule

class MyModule(BaseModule):
    """Template per nuovi moduli pyw."""
    
    name = "my-module"
    version = "1.0.0"
    dependencies = ["pyw-core>=0.1.0"]
    
    def __init__(self, config=None):
        super().__init__()
        self.config = config or self.default_config()
    
    @classmethod
    def default_config(cls):
        return {"enabled": True}
```

### 🧪 Testing Support

```python
from pyw.core.testing import (
    temporary_directory, mock_environment,
    assert_type_safe, benchmark
)

def test_my_function():
    with temporary_directory() as tmpdir:
        # Test con directory temporanea
        pass
    
    with mock_environment({"DEBUG": "true"}):
        # Test con environment variables mock
        pass
    
    # Type safety testing
    result = my_typed_function("input")
    assert_type_safe(result, MyExpectedType)
    
    # Performance benchmarking
    with benchmark("my_operation") as b:
        expensive_operation()
    assert b.elapsed < 1.0  # Max 1 second
```

## Bundle Installation

Per installare gruppi di moduli correlati:

```bash
# Developer toolkit completo
pip install pyw-devtools  # logger + fs + cli + secret + config

# Music processing
pip install pyw-music     # music21 + musicparser  

# Computer vision
pip install pyw-cv        # vision + motion
```

## Advanced Usage

### 🔌 Custom Extensions

```python
from pyw.core.extensions import register_extension

@register_extension("mycompany.custom")
class CustomExtension:
    """Estensione personalizzata per pyw."""
    
    def setup(self):
        # Inizializzazione custom
        pass

# Auto-discovered da pyw.core.plugins
```

### 📊 Ecosystem Stats

```python
from pyw.core import ecosystem_info

# Info sull'ecosistema installato
info = ecosystem_info()
print(f"Installed pyw modules: {len(info.modules)}")
for module in info.modules:
    print(f"  {module.name} v{module.version}")
```

### 🎯 Quality Assurance

```python
from pyw.core.qa import (
    validate_module, check_compatibility,
    run_ecosystem_tests
)

# Valida un modulo pyw
issues = validate_module("pyw.mymodule")
if issues:
    for issue in issues:
        print(f"⚠️  {issue}")

# Check compatibilità tra moduli
compat = check_compatibility(["pyw-logger==1.0", "pyw-fs==2.0"])
assert compat.compatible
```

## Development Tools

### 🏗️ Module Scaffolding

```bash
# Crea nuovo modulo pyw
pyw-core scaffold my-module --type=utility
cd pyw-my-module/

# Struttura generata:
# pyw-my-module/
# ├── pyw/
# │   └── my_module/
# │       ├── __init__.py
# │       └── core.py
# ├── tests/
# ├── pyproject.toml
# └── README.md
```

### 📋 Quality Checks

```bash
# Linting ecosystem-wide
pyw-core lint --all-modules

# Type checking
pyw-core mypy --strict

# Run all tests
pyw-core test --coverage

# Check dependencies
pyw-core deps --check-conflicts
```

## Roadmap

- 🏗️ **Enhanced utilities**: Async helpers, concurrency utilities
- 📦 **Plugin system**: Hot-reloading, dependency injection
- 🔧 **Dev experience**: Better debugging, profiling integration  
- 📚 **Documentation**: Auto-generated API docs, examples
- 🎯 **Quality tools**: Advanced linting, security scanning
- 🌐 **Ecosystem**: Package discovery, compatibility matrix
- ⚡ **Performance**: Caching strategies, optimization helpers

## Contributing

**pyw-core** è il cuore dell'ecosistema - ogni contributo deve essere attentamente valutato:

1. **Fork & Clone**: `git clone https://github.com/pythonWoods/pyw-core.git`
2. **Development setup**: `poetry install && poetry shell`
3. **Quality checks**: `ruff check . && mypy && pytest`
4. **Documentation**: Aggiorna docs per ogni modifica API
5. **Compatibility**: Assicurati che le modifiche non rompano altri moduli
6. **Pull Request**: CI esegue test completi dell'ecosistema

## Architecture Notes

```
pyw-core (namespace + utilities)
├── pyw/__init__.py          # Namespace package
├── pyw/core/
│   ├── __init__.py         # Public API exports
│   ├── base.py             # BaseConfig, BaseModel
│   ├── utils.py            # Common utilities  
│   ├── types.py            # Type aliases & helpers
│   ├── plugins.py          # Plugin discovery
│   ├── performance.py      # Performance tools
│   ├── testing.py          # Test utilities
│   └── exceptions.py       # Common exceptions
└── tests/                  # Comprehensive test suite
```

Felice coding nella foresta di **pythonWoods**! 🌲🐾

## Links utili

Documentazione dev (work-in-progress) → https://pythonwoods.dev/docs/pyw-core/latest/

Issue tracker → https://github.com/pythonWoods/pyw-core/issues

Changelog → https://github.com/pythonWoods/pyw-core/releases

© pythonWoods — MIT License