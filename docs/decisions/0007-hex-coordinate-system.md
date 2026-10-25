# 0007: Hex coordinate system

Status: Accepted (2026-10-25)

## Context
The board is 19 land hexes in rows of 3-4-5-4-3, surrounded by sea. Settlements sit on vertices (hex corners) and roads on edges (hex sides), and each vertex or edge is shared by up to 3 or 2 hexes. I need coordinates that make neighbours, shared corners and shared sides easy and unambiguous to compute, so the adjacency tables (ADR 0008) can be generated rather than typed in by hand. The scheme must be simple to reproduce exactly in Rust.

Coordinates are only used to *build* the topology. Everything at runtime (actions, state, observations) uses dense integer ids (ADR 0008).

## Decision
- **Pointy-top hexes in axial coordinates `(q, r)`**, with the cube coordinate `s = -q - r` derived when needed (for distances and rotations). The centre hex is `(0, 0)`; the 19 land hexes are those with `max(|q|, |r|, |s|) <= 2`.
- **Vertices as `(q, r, corner)`, `corner ∈ {N, S}`.** Every vertex is the top (N) corner of exactly one hex or the bottom (S) corner of exactly one hex, so each vertex has exactly one name. There is no de-duplication step.
- **Edges as `(q, r, side)`, `side ∈ {NE, NW, W}`.** Every edge is one of these three sides of exactly one hex; the other three sides (SW, SE, E) belong to neighbours.
- The owning hex of a coastal vertex or edge may be a sea hex. That's fine: we only enumerate vertices and edges that touch at least one land hex (54 and 72).

## Options considered
- **Axial (chosen):** two numbers per hex; neighbour offsets are constant; converts to cube for free. Standard reference: Red Blob Games, "Hexagonal Grids".
- **Cube `(q, r, s)`:** the same thing with a redundant third coordinate. Nicest for distance and rotation formulas, but stores a value that must always satisfy `q + r + s = 0`.
- **Offset (odd-r / even-r rows):** matches the printed rows, but neighbour offsets depend on whether the row is odd or even, which is a classic source of bugs.
- **Doubled coordinates:** easy ASCII printing, but awkward for rotations.
- **Vertex naming by sets of touching hexes** (instead of `(q, r, corner)`): needs canonicalisation and breaks on the coast, where fewer than 3 hexes touch.

## Consequences
- Good: neighbour, corner and side relations are small constant tables; the 12 board symmetries (ADR 0006 augmentation) are simple rotations and reflections in cube coordinates; easy to port.
- Bad: axial coordinates are not what you see when you print the board, so the ASCII printer needs a small conversion to rows; coordinate code needs its own tests (property tests: 54 vertices, 72 edges, every vertex has 2-3 neighbours, every land hex has 6 vertices).

## Revisit when
Expansions with different board shapes (5-6 players, Seafarers) come into scope, or if the symmetry code turns out awkward.
