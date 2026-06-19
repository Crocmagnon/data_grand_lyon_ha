"""Count entries in alertes.json grouped by `ligne_com`."""

import json
from collections import Counter
from pathlib import Path

ALERTES_PATH = Path(__file__).parent / "alertes.json"


def main() -> None:
    """Print the number of entries grouped by `ligne_com`, sorted by count."""
    data = json.loads(ALERTES_PATH.read_text(encoding="utf-8"))
    counts = Counter(entry.get("ligne_com") for entry in data["values"])

    print(f"{'ligne_com':<15} count")
    print("-" * 25)
    for ligne_com, count in counts.most_common():
        print(f"{ligne_com!s:<15} {count}")

    print("-" * 25)
    print(f"{'TOTAL':<15} {sum(counts.values())}")


if __name__ == "__main__":
    main()
