# transports_commun_lyon

Python library to retrieve public transport data from the TCL/Sytral network in Lyon, France.

Intended for use as a [Home Assistant](https://www.home-assistant.io/) integration backend.

## Installation

```bash
pip install transports-commun-lyon
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv add transports-commun-lyon
```

## Usage

```python
from transports_commun_lyon import hello_world

print(hello_world())
```

## Development

This project uses [uv](https://docs.astral.sh/uv/) for dependency management.

```bash
# Run tests
uv run pytest

# Build the package
uv build
```

## License

MIT
