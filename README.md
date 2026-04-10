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
import asyncio
import aiohttp
from transports_commun_lyon import TCLClient, PassageType

async def main():
    async with aiohttp.ClientSession() as session:
        client = TCLClient(session)
        # Or with authentication:
        # client = TCLClient(session, username="user", password="pass")

        passages = await client.get_passages("A", 30101, PassageType.THEORETICAL)
        for p in passages:
            print(f"{p.ligne} → {p.direction} in {p.delai_passage}")

asyncio.run(main())
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
