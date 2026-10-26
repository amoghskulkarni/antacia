# Board topology and coordinates

How the board is represented in `engine/topology.py`: how hexes are named and positioned, how vertices and edges get one unique name each, how they become dense integer ids, and how the adjacency tables are derived.

Decisions: ADR 0007 (coordinates), ADR 0008 (ids and tables), ADR 0009 (layout and harbors). This page explains the *how*; the ADRs explain the *why*. All example numbers below were printed from the code.

## 1. Overview: three layers

```
 coordinates              dense ids                 adjacency tables
 (q, r), (q, r, N/S),  ─►  0..18, 0..53, 0..71  ─►  HEX_VERTICES, VERTEX_EDGES, ...
 (q, r, NE/NW/W)
 used ONLY to build        used EVERYWHERE at        immutable tuples of tuples,
 the tables                runtime                   built once at import
```

- **Coordinates** give every hex, vertex and edge exactly one name. They are only used to *build* the tables (and to sort things into a readable order).
- **Ids** are dense integers: `HexId` 0..18, `VertexId` 0..53, `EdgeId` 0..71. Actions (`BuildRoad(edge=3)`), state, observations and replays only ever see ids.
- **Tables** answer "what touches what" with plain tuple lookups.

The static topology never changes during or between games. What changes per game (terrains, number tokens, harbor types) lives in `engine/board.py` and is indexed by these same ids.

## 2. Hexes: axial coordinates `(q, r)`

Hexes are **pointy-top** (a corner at the top, flat sides left and right). A hex is named `(q, r)`:

- `q` is the column: east is `q + 1`.
- `r` is the row: **down** is `r + 1`. Each row is shifted half a hex to the right of the row above, so `r + 1` also moves half a hex right.

Think of a square grid that has been sheared sideways.

The six neighbours are fixed offsets (`DIRECTIONS`, counterclockwise on screen starting from east):

```
      NW (0,-1)   NE (+1,-1)

  W (-1,0)    (q,r)    E (+1,0)

      SW (-1,+1)  SE (0,+1)
```

The same six offsets work for every hex. This is the reason for axial coordinates: "offset" coordinates (rows of a square array, every other row nudged) need different offsets on odd and even rows, a classic source of bugs.

The centre is `(0, 0)`. Land hexes are those within distance 2 of the centre, i.e. `max(|q|, |r|, |q + r|) <= 2`. That gives 19 hexes in rows of 3, 4, 5, 4, 3:

```
 hex id (q, r)

              0 ( 0,-2)    1 ( 1,-2)    2 ( 2,-2)
        3 (-1,-1)    4 ( 0,-1)    5 ( 1,-1)    6 ( 2,-1)
 7 (-2, 0)    8 (-1, 0)    9 ( 0, 0)   10 ( 1, 0)   11 ( 2, 0)
       12 (-2, 1)   13 (-1, 1)   14 ( 0, 1)   15 ( 1, 1)
              16 (-2, 2)   17 (-1, 2)   18 ( 0, 2)
```

Note that `r` is the row (it runs -2..2 downwards) and the leftmost `q` in each row shifts by one per row. Ids simply count 0, 1, 2, ... in reading order (section 6).

## 3. Positions: exact integer half-units

To sort things into reading order and to draw the board, every hex, vertex and edge has a position `(x, y)` in **half-units**, so everything stays an exact integer (no floats):

- 1 x-unit = half a hex width.
- 1 y-unit = half a hex side length.

A pointy-top hex is 2 x-units wide and 4 y-units tall (corner to corner). Rows overlap, so consecutive rows are 3 y-units apart. So:

| move | change in x | change in y |
|---|---|---|
| `q + 1` (east) | +2 | 0 |
| `r + 1` (down-right) | +1 | +3 |

Which gives the hex centre:

```
hex_center(q, r) = (2q + r, 3r)
```

| id | (q, r) | centre (x, y) |
|---|---|---|
| 0 | (0, -2) | (-2, -6) |
| 1 | (1, -2) | (0, -6) |
| 9 | (0, 0) | (0, 0) |
| 18 | (0, 2) | (2, 6) |

Positions are never stored in state. They exist for building the tables, sorting ids, and tests.

## 4. Anatomy of one hex

A hex has 6 **corners** (where settlements and cities go) and 6 **sides** (where roads go):

```
 corners                 sides
       N                       / \
      / \                 NW  /   \  NE
    NW   NE                  |     |
    |     |                W |     | E
    SW   SE                  |     |
      \ /                 SW  \   /  SE
       S                       \ /
```

In the half-unit grid, the corners of a hex centred at `(x, y)` are at:

| corner | position |
|---|---|
| N | (x, y - 2) |
| NE | (x + 1, y - 1) |
| SE | (x + 1, y + 1) |
| S | (x, y + 2) |
| SW | (x - 1, y + 1) |
| NW | (x - 1, y - 1) |

## 5. Naming vertices and edges: one canonical name each

The problem: a corner is shared by up to 3 hexes. "The NE corner of hex A" and "the NW corner of hex B" can be the very same point. We need one name per point so duplicates never have to be detected geometrically.

### Vertices: `(q, r, N or S)`

In a pointy-top hex grid, **every vertex is either the top (`N`) corner of exactly one hex, or the bottom (`S`) corner of exactly one hex**:

- A vertex with one hex above and two below is the `S` corner of the upper hex.
- A vertex with two hexes above and one below is the `N` corner of the lower hex.

So a vertex is `(q, r, Corner)` with `Corner` in `{N, S}`. The other four corners of a hex are *named from a neighbour*. For the hex `(q, r)`, clockwise from the top (`hex_corners`):

| corner | canonical name | because |
|---|---|---|
| N | `(q, r, N)` | its own top |
| NE | `(q+1, r-1, S)` | the bottom of the NE neighbour |
| SE | `(q, r+1, N)` | the top of the SE neighbour |
| S | `(q, r, S)` | its own bottom |
| SW | `(q-1, r+1, N)` | the top of the SW neighbour |
| NW | `(q, r-1, S)` | the bottom of the NW neighbour |

Two hexes that share a corner produce the **same tuple**, so putting all corners into a Python `set` de-duplicates for free.

### Edges: `(q, r, NE or NW or W)`

Likewise every edge is the `NE`, `NW` or `W` side of exactly one hex (the other three sides of a hex belong to neighbours). For hex `(q, r)`, clockwise from top right (`hex_sides`):

| side | canonical name |
|---|---|
| NE | `(q, r, NE)` |
| E | `(q+1, r, W)` (the W side of the E neighbour) |
| SE | `(q, r+1, NW)` (the NW side of the SE neighbour) |
| SW | `(q-1, r+1, NE)` (the NE side of the SW neighbour) |
| W | `(q, r, W)` |
| NW | `(q, r, NW)` |

An edge joins two vertices (`edge_endpoints`):

| edge | joins |
|---|---|
| `(q, r, NE)` | `(q, r, N)` and `(q+1, r-1, S)` |
| `(q, r, NW)` | `(q, r-1, S)` and `(q, r, N)` |
| `(q, r, W)` | `(q, r-1, S)` and `(q-1, r+1, N)` |

An edge's position is the **sum** of its two endpoints' positions (twice its midpoint), which keeps it an exact integer.

### The owning hex may be sea

A name belongs to one hex, but that hex does not have to be land. Along the coast, the owner of a vertex or edge can be a sea hex such as `(3, -2)`. That is fine: the engine only enumerates vertices and edges that touch at least one land hex.

- Vertex 3 is `(0, -3, S)`: the NW corner of land hex 0, named from the sea hex above it.
- Edge 9 is `(3, -2, W)`: the east side of land hex 2, named from the sea hex to its right.

16 of the 54 vertices and 15 of the 72 edges are owned by sea hexes. Never assume `is_land((q, r))` for a vertex or edge name.

### Counts

| thing | count | check |
|---|---|---|
| hexes | 19 | rows 3+4+5+4+3 |
| vertices | 54 | 24 touch 3 hexes, 12 touch 2, 18 touch 1 |
| edges | 72 | 42 inner, 30 coastal |

## 6. Dense ids

Each of the three sets is sorted by **position**, row first, then left to right (`(y, x)`). The index in that sorted order is the id. So:

- Hex ids read like text: left to right, top to bottom (the map in section 2).
- Vertex ids start at the top-left of the board and run along each row of corners.
- Edge ids follow the position of the edge midpoint in the same way.

Example, the top-left hex 0 `(0, -2)`:

| | ids |
|---|---|
| corners, clockwise from top | 0, 4, 8, 12, 7, 3 |
| sides, clockwise from top right | 1, 7, 12, 11, 6, 0 |

The ids are an interface: they appear in actions, replays and trained models, and the Rust port must number everything identically. `tests/conformance/topology.json` pins the numbering, and `test_topology_matches_fixture` fails if it ever changes. Regenerate it only for an intentional, ADR-backed change: `uv run python -m tests.conformance.regenerate`.

## 7. The adjacency tables

All tables are tuples (of tuples) indexed by id, built once at import. Lists are sorted by id except `HEX_VERTICES`, which is clockwise from the top corner.

| table | maps | typical size |
|---|---|---|
| `HEX_VERTICES[h]` | hex to its 6 corners | 6 |
| `HEX_NEIGHBORS[h]` | hex to adjacent land hexes | 3, 4 or 6 |
| `VERTEX_HEXES[v]` | vertex to the hexes it touches | 1, 2 or 3 |
| `EDGE_VERTICES[e]` | edge to its 2 endpoints | 2 |
| `EDGE_HEXES[e]` | edge to the hexes it borders | 1 or 2 |
| `VERTEX_EDGES[v]` | vertex to its incident edges | 2 or 3 |
| `VERTEX_VERTICES[v]` | vertex to adjacent vertices | 2 or 3 |
| `EDGE_EDGES[e]` | edge to edges sharing an endpoint | 2 to 4 |

### How they are derived

Nothing is typed in by hand. Each table is built from the previous ones:

1. **`HEX_VERTICES`**: apply the corner formulas (section 5) to each land hex and look up the ids.
2. **`VERTEX_HEXES`**: the **inverse** of `HEX_VERTICES`. For each vertex, collect the hexes whose corner list contains it.
3. **`EDGE_VERTICES`**: apply `edge_endpoints` to each edge.
4. **`VERTEX_EDGES`**: the inverse of `EDGE_VERTICES`.
5. **`VERTEX_VERTICES[v]`**: two vertices are neighbours exactly when an edge joins them. For each edge at `v`, take its *other* endpoint.
6. **`EDGE_EDGES[e]`**: for each endpoint of `e`, take that vertex's edges; union them and remove `e`.
7. **`HEX_NEIGHBORS`**: add each of the six `DIRECTIONS` offsets and keep the results that are land.

The pattern is "build one direction from geometry, get the opposite direction by inverting".

### Worked example

Take the centre hex 9 `(0, 0)`. Its corners (from the code):

| clockwise | id | name | position | touches hexes |
|---|---|---|---|---|
| N | 18 | `(0, 0, N)` | (0, -2) | 4, 5, 9 |
| NE | 24 | `(1, -1, S)` | (1, -1) | 5, 9, 10 |
| SE | 30 | `(0, 1, N)` | (1, 1) | 9, 10, 14 |
| S | 35 | `(0, 0, S)` | (0, 2) | 9, 13, 14 |
| SW | 29 | `(-1, 1, N)` | (-1, 1) | 8, 9, 13 |
| NW | 23 | `(0, -1, S)` | (-1, -1) | 4, 8, 9 |

Now vertex 24, the NE corner, named `(1, -1, S)` (the bottom of its NE neighbour, hex 5). It has three incident edges:

| edge id | name | joins |
|---|---|---|
| 28 | `(0, 0, NE)` | 18 and 24 |
| 29 | `(1, 0, NW)` | 19 and 24 |
| 36 | `(1, 0, W)` | 24 and 30 |

Edge 36 is the east side of the centre hex, named from its east neighbour (hex 10) as `(1, 0, W)`. Taking the other endpoint of each edge gives vertex 24's neighbours: **(18, 19, 30)**. This is `VERTEX_VERTICES[24]`.

Hex neighbours by the same idea: hex 0 `(0, -2)` has only 3 land neighbours, `(1, 3, 4)`, because the other three offsets fall outside the board. The centre hex has all six: `(4, 5, 8, 10, 13, 14)`.

## 8. The coast and harbor slots

- **`COAST`** is the ring of the 30 edges that border exactly one land hex, in clockwise order starting at the top-left. Consecutive edges share one vertex, and the last connects back to the first.
- **`HARBOR_SLOTS`** are 9 fixed positions on the coast (slot ids 0..8, clockwise from the top left). Slot `i` is the edge `HARBOR_SLOTS[i]`; both endpoints of that edge get the harbor's trade ratio. The board layout (`Board.harbors[i]`) decides which harbor type sits on slot `i`.

The harbor edges are 0, 3, 17, 18, 38, 49, 61, 66 and 69 (18 harbor vertices: 0, 1, 3, 5, 10, 11, 15, 16, 26, 32, 33, 38, 42, 46, 47, 49, 51, 52), verified against the rulebook frame with `render_topology()`. In clockwise slot order that is 0, 3, 17, 38, 61, 69, 66, 49, 18: gaps of 3, 4, 3 coastal edges, repeated three times. Because slots run clockwise and the pattern repeats every third slot, a 120-degree rotation of the board maps slot `i` to slot `i + 3`.

The edges are stored as a set in `topology.py`, and the beginner harbor types as a mapping from edge to type in `board.py`, so neither depends on remembering the slot order.

## 9. Using the module

```python
from engine import topology as t

h = t.HEX_ID[(0, 0)]  # coordinates to id: 9
t.HEXES[h]  # id to coordinates: (0, 0)

t.HEX_VERTICES[h]  # all 6 settlement spots of a hex
t.VERTEX_HEXES[v]  # hexes that produce for vertex v
t.VERTEX_VERTICES[v]  # for the distance rule
t.VERTEX_EDGES[v]  # roads touching a settlement
t.EDGE_VERTICES[e]  # both ends of a road

# distance rule: a vertex is free if it and all its neighbours are empty
free = all(not occupied[u] for u in (v, *t.VERTEX_VERTICES[v]))
```

Other ready-made things:

- `t.NUM_HEXES / NUM_VERTICES / NUM_EDGES`: 19, 54, 72.
- `t.HEX_POS / VERTEX_POS / EDGE_POS`: positions by id (section 3).
- `t.HEX_ID / VERTEX_ID / EDGE_ID`: read-only dicts from coordinates to ids.
- `engine.board.render_board(board)`: ASCII picture of a layout.
- `engine.board.render_topology()`: ASCII map with every hex (`H`), vertex (`v`) and edge (`e`) id drawn at its true position. Use it to find an id or to check a change to the numbering.

## 10. Gotchas

- **`r` grows downward.** This is screen convention, not maths convention. Anything "up" has a smaller `r`.
- **`DIRECTIONS` is counterclockwise on screen** (E, NE, NW, W, SW, SE), but `hex_corners` and `hex_sides` go **clockwise**. They are different lists for different jobs.
- **The owner of a vertex or edge name can be a sea hex** (section 5). Do not run `is_land` on vertex or edge names, and do not use the name to find "the" hex of a vertex; use `VERTEX_HEXES`.
- **Positions are half-units, not pixels.** Scale and offset them in a renderer; do not compare them to hex sizes.
- **Never hand-edit an id table.** Ids are derived. If the numbering must change, change the sort or formulas, bump the fixture deliberately, and write an ADR.
- **No dict ordering in game logic.** The `HEX_ID`/`VERTEX_ID`/`EDGE_ID` mappings are for lookup only; iterate the tuples (`HEXES`, ...), whose order is defined. This keeps the Rust port reproducible (`engine/CLAUDE.md`).

## 11. How it is tested

`tests/unit/test_topology.py`:

- counts (19/54/72) and row-major ordering of all three id sets;
- vertex names against **independent** corner offsets, so the naming formulas are not just checking themselves;
- edge endpoints are adjacent corners, and the edge position is the sum of its endpoints;
- symmetric adjacency, vertex and edge degree ranges, hex incidence counts (24/12/18);
- the coast is a closed clockwise ring of 30 edges; harbor slots are coastal and never share a vertex.

`tests/conformance/test_topology_fixture.py` compares every table to `topology.json`.
