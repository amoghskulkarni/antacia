# 0008: Dense board ids and precomputed topology tables

Status: Accepted (2026-10-25)

## Context
Actions (`BuildRoad(edge)`, `MoveRobber(hex, ...)`), the state, observation arrays (ADR 0006) and the RL action ids (ADR 0005) all need to refer to board locations. Those references end up in golden replays, so their numbering must be fixed forever (or versioned) and identical in the Rust port. The topology itself (which vertex touches which hex and edge) never changes between games of the base game.

## Decision
- **Dense integer ids:** `HexId` 0..18, `VertexId` 0..53, `EdgeId` 0..71 (aliases in `engine/types.py`). Harbor slots are numbered 0..8.
- **Canonical order: row-major, top to bottom, then left to right**, by the position of the hex centre, vertex or edge midpoint on the printed board. Ties broken by a documented rule in `board.py`. It's easy to read on the ASCII board and in test failures.
- **Topology is computed once at import time from the coordinates (ADR 0007) and stored as module-level tuples of tuples:** `hex_vertices`, `hex_neighbors`, `vertex_hexes`, `vertex_vertices`, `vertex_edges`, `edge_vertices`, `edge_edges`. These are immutable constants, not mutable globals, so they don't break the engine's "no globals" rule.
- **Per-game layout (terrains, number tokens, harbor types) is separate from topology** and lives in a frozen `Board` value referenced by `GameState`. It is created once per game (ADR 0009) and shared by every later state without copying.
- **A conformance fixture** (`tests/conformance/topology.json`) records the full id tables, so the Rust port can check it numbers everything identically.

## Options considered
- **Row-major ids (chosen):** readable and predictable.
- **Spiral order from the outside in** (matches the official token-placement spiral): convenient for the token-placement algorithm only; less readable elsewhere. The spiral can still be expressed as a list of hex ids.
- **Coordinates as ids** (tuples everywhere): no translation layer, but slow dict lookups, unusable as array indices, and harder to encode for RL.
- **Hand-written adjacency tables:** no geometry code, but 54 + 72 entries typed in by hand are an error magnet.

## Consequences
- Good: O(1) array lookups everywhere; observation arrays index directly by id; action ids are simple offsets; topology is tested once and shared.
- Bad: changing the numbering later invalidates golden replays and trained models; it must then be versioned. Debug output needs a helper to print ids as positions.

## Revisit when
Board shapes change (expansions), or a GNN encoder wants a different canonical ordering (it shouldn't, since GNNs are order-invariant).
