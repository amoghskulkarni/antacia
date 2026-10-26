"""Builds the language-neutral fixture data from the engine."""

from typing import Any

from engine import topology as t


def topology_tables() -> dict[str, Any]:
    """Every id table from engine.topology, as plain JSON-compatible lists."""
    return {
        "hexes": [list(h) for h in t.HEXES],
        "vertices": [[q, r, c.name] for q, r, c in t.VERTICES],
        "edges": [[q, r, s.name] for q, r, s in t.EDGES],
        "hex_vertices": [list(x) for x in t.HEX_VERTICES],
        "hex_neighbors": [list(x) for x in t.HEX_NEIGHBORS],
        "vertex_hexes": [list(x) for x in t.VERTEX_HEXES],
        "vertex_vertices": [list(x) for x in t.VERTEX_VERTICES],
        "vertex_edges": [list(x) for x in t.VERTEX_EDGES],
        "edge_vertices": [list(x) for x in t.EDGE_VERTICES],
        "edge_hexes": [list(x) for x in t.EDGE_HEXES],
        "edge_edges": [list(x) for x in t.EDGE_EDGES],
        "coast": list(t.COAST),
        "harbor_frames": [list(f) for f in t.HARBOR_FRAMES],
        "hex_symmetries": [list(x) for x in t.HEX_SYMMETRIES],
        "vertex_symmetries": [list(x) for x in t.VERTEX_SYMMETRIES],
        "edge_symmetries": [list(x) for x in t.EDGE_SYMMETRIES],
        "inverse_symmetry": list(t.INVERSE_SYMMETRY),
    }
