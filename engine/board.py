"""Board geometry: hexes, vertices, edges, adjacency, harbors, seeded layout.

Planned for Week 1. The static topology (which vertices touch which hexes and
edges) is computed once and shared by every GameState; only the per-game
layout (terrains, number tokens, harbors) varies with the seed.

Rules: docs/rules-spec.md sections 1 (components) and 2 (layout).
"""

# TODO(ADR): choose the hex coordinate system (axial / cube / offset) before
# adding any types here. This is the first Week 1 decision.
