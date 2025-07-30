# pyw-cli 🖥️
[![PyPI](https://img.shields.io/pypi/v/pyw-cli.svg)](https://pypi.org/project/pyw-cli/)
[![CI](https://github.com/pythonWoods/pyw-cli/actions/workflows/ci.yml/badge.svg)](https://github.com/pythonWoods/pyw-cli/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> Typer CLI scaffolding and utilities for the **pythonWoods** ecosystem.

## Overview

**pyw-cli** fornisce un generatore di CLI moderne basate su [Typer](https://typer.tiangolo.com/), con scaffolding automatico, integrazione rich/logger e utilities per il rapido sviluppo di command-line tools.

## Philosophy

* **Typer-first** – scaffolding completo con best practices integrate
* **Rich integration** – colori, progress bars, tabelle out-of-the-box
* **Auto-completion** – supporto nativo per bash, zsh, fish
* **Logger-ready** – integrazione con `pyw-logger` per structured logging
* **Template-driven** – genera progetti CLI completi con un comando

## Installation

```bash
pip install pyw-cli
```

Per funzionalità avanzate:

```bash
pip install pyw-cli[rich]     # + Rich per output colorato
pip install pyw-cli[logger]   # + pyw-logger integration
pip install pyw-cli[full]     # tutto incluso
```

## Quick Start

### Generare una nuova CLI

```bash
# Crea un nuovo progetto CLI
pyw new-cli mytool

# Entra nella directory e testa
cd mytool && python -m mytool --help
```

### Struttura generata

```
mytool/
├── mytool/
│   ├── __init__.py
│   ├── __main__.py        # Entry point
│   ├── cli.py            # Typer app principale
│   ├── commands/         # Comandi organizzati
│   │   ├── __init__.py
│   │   └── hello.py
│   └── utils.py          # Utilities comuni
├── tests/
├── pyproject.toml        # Poetry/pip configuration
└── README.md
```

### Esempio di utilizzo

```python
from pyw.cli import TyperApp, rich_print, with_logger
from pyw.cli.decorators import command, option
import typer

# App principale con rich integration
app = TyperApp(
    name="mytool",
    help="Il mio fantastico CLI tool",
    rich_markup_mode="rich"
)

@app.command()
@with_logger  # Auto-inject logger
def hello(
    name: str = option("--name", "-n", help="Nome da salutare"),
    count: int = option("--count", "-c", default=1, help="Quante volte salutare"),
    logger=None  # Injected by @with_logger
):
    """Saluta qualcuno con stile! 👋"""
    for i in range(count):
        rich_print(f"[bold green]Ciao {name}![/bold green] ({i+1}/{count})")
        logger.info("Saluto inviato", name=name, iteration=i+1)

if __name__ == "__main__":
    app()
```

## Features

### 🎨 Rich Integration

Output colorato e formattato automaticamente:

```python
from pyw.cli import (
    rich_print, rich_table, rich_progress,
    console, status_spinner
)

# Print colorato
rich_print("[bold red]Errore![/bold red] Qualcosa è andato storto")

# Tabelle
table = rich_table("Nome", "Età", "Città")
table.add_row("Alice", "30", "Milano")
console.print(table)

# Progress bar
with rich_progress() as progress:
    task = progress.add_task("Processing...", total=100)
    for i in range(100):
        progress.update(task, advance=1)
        time.sleep(0.01)
```

### 🔧 CLI Scaffolding

Templates pre-configurati per diversi tipi di CLI:

```bash
# CLI semplice (single command)
pyw new-cli myapp --template=simple

# CLI multi-comando
pyw new-cli myapp --template=multi

# CLI con subcomandi annidati
pyw new-cli myapp --template=nested

# CLI per data processing
pyw new-cli myapp --template=data
```

### 📝 Logger Integration

Integrazione automatica con `pyw-logger`:

```python
from pyw.cli import command_with_logger

@command_with_logger
def process_data(file_path: str, logger=None):
    """Processa un file di dati."""
    logger.info("Inizio processing", file=file_path)
    
    try:
        # ... processing logic
        logger.info("Processing completato", records_processed=1234)
    except Exception as e:
        logger.error("Errore durante processing", error=str(e))
        raise typer.Exit(1)
```

### 🐚 Auto-completion

Setup automatico per shell completion:

```bash
# Installa completion per la shell corrente
mytool --install-completion

# Oppure manualmente
mytool --show-completion >> ~/.bashrc  # bash
mytool --show-completion >> ~/.zshrc   # zsh
```

## Advanced Usage

### Custom Commands

```python
from pyw.cli import TyperApp, CommandGroup

app = TyperApp()

# Gruppo di comandi
db_group = CommandGroup(name="db", help="Database operations")

@db_group.command()
def migrate():
    """Esegui migrazioni database."""
    pass

@db_group.command() 
def seed():
    """Popola database con dati di test."""
    pass

app.add_typer(db_group.typer, name="db")
```

### Configuration Support

```python
from pyw.cli import config_option, load_config
from pyw.core import BaseConfig

class MyConfig(BaseConfig):
    api_key: str
    debug: bool = False

@app.command()
def deploy(
    config: MyConfig = config_option("--config", "-c")
):
    """Deploy con configurazione."""
    if config.debug:
        rich_print("[yellow]Debug mode enabled[/yellow]")
```

### Plugin System

```python
from pyw.cli import plugin_command

@plugin_command("myapp.commands")
def my_plugin_command():
    """Comando fornito da plugin."""
    pass
```

## Templates Available

| Template | Description | Use Case |
|----------|-------------|----------|
| `simple` | Single command CLI | Scripts, utilities |
| `multi` | Multi-command CLI | Tools con più funzioni |
| `nested` | Nested subcommands | Complex applications |
| `data` | Data processing CLI | ETL, analysis tools |
| `api` | API client CLI | REST/GraphQL clients |
| `git` | Git-like CLI | Version control tools |

## Roadmap

- 🏗️ **Template expansion**: Più templates per casi d'uso specifici
- 🔌 **Plugin system**: Caricamento dinamico di comandi
- 📊 **Analytics**: Metriche di utilizzo built-in
- 🌐 **I18n support**: Internazionalizzazione
- 🧪 **Testing utilities**: Helper per testare CLI
- 📚 **Documentation generation**: Auto-generate docs da commands

## Contributing

1. Fork il repo: `git clone https://github.com/pythonWoods/pyw-cli.git`
2. Crea virtual-env: `poetry install && poetry shell`
3. Lancia tests: `pytest`
4. Lancia linter: `ruff check . && mypy`
5. Apri la PR: CI esegue tutti i check

Felice coding nella foresta di **pythonWoods**! 🌲🖥️

## Links utili

Documentazione dev (work-in-progress) → https://pythonwoods.dev/docs/pyw-cli/latest/

Issue tracker → https://github.com/pythonWoods/pyw-cli/issues

Changelog → https://github.com/pythonWoods/pyw-cli/releases

© pythonWoods — MIT License