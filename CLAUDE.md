# CLAUDE.md

## Project Overview

Python library to retrieve public transport data from the TCL/Sytral network in Lyon, France.
Intended for use as a Home Assistant integration backend.

## Development Commands

```bash
# Run all tests
uv run pytest

# Run a single test
uv run pytest tests/test_hello.py::test_hello_world

# Build the package
uv build
```

## Architecture

- **src layout**: Source code lives in `src/transports_commun_lyon/`
- **Build backend**: hatchling
- **Package manager**: uv
- **CI/CD**: Forgejo Actions (`.forgejo/workflows/ci.yml`)
  - Tests run on every push to main and on PRs
  - Publishing to PyPI happens on `v*` tag push

## Conventions

- Type annotations on all public functions
- Docstrings on all public modules and functions
- Tests in `tests/` directory, using pytest
