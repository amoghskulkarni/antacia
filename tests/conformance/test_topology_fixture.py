import json
from pathlib import Path

from tests.conformance.tables import topology_tables

FIXTURE = Path(__file__).parent / "topology.json"


def test_topology_matches_fixture() -> None:
    # A failure means board ids changed: that breaks replays and trained models.
    # Only regenerate (see regenerate.py) for an intentional, ADR-backed change.
    assert topology_tables() == json.loads(FIXTURE.read_text())
