"""Rewrite the conformance fixtures from the current engine.

Run only after an intentional, ADR-backed change to the numbering:
    uv run python -m tests.conformance.regenerate
"""

import json
from pathlib import Path

from tests.conformance.tables import topology_tables

HERE = Path(__file__).parent


def main() -> None:
    path = HERE / "topology.json"
    path.write_text(json.dumps(topology_tables(), indent=1) + "\n")
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
