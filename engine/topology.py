"""Static board topology of the base game: coordinates, dense ids, adjacency.

ADR 0007 (coordinates): pointy-top hexes in axial (q, r); r grows downwards.
A vertex is `(q, r, Corner)`, the top (N) or bottom (S) corner of exactly one
hex; an edge is `(q, r, Side)`, the NE, NW or W side of exactly one hex. The
owning hex may be sea; only vertices and edges touching land are enumerated.

ADR 0008 (ids): hexes, vertices and edges get dense ids 0..N-1 in row-major
order of their on-screen position (top to bottom, then left to right). All
tables below are immutable and computed once at import; nothing here changes
during a game. Adjacency lists are sorted by id, except `HEX_VERTICES`, which
is clockwise from the top corner.

Positions are exact integers in half-units: x in steps of sqrt(3)/2 * size,
y in steps of size/2. A hex centre is (2q + r, 3r). Edge positions are the sum
of their two endpoints (twice the midpoint), so they stay integers too.
"""

from collections.abc import Mapping
from enum import IntEnum
from types import MappingProxyType

from engine.types import EdgeId, HexId, VertexId


class Corner(IntEnum):
    N = 0
    S = 1


class Side(IntEnum):
    NE = 0
    NW = 1
    W = 2


type Hex = tuple[int, int]
type Vertex = tuple[int, int, Corner]
type Edge = tuple[int, int, Side]
type Point = tuple[int, int]

RADIUS = 2
"""Land hexes are those with cube distance <= RADIUS from the centre."""

DIRECTIONS: tuple[Hex, ...] = ((1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1))
"""Axial neighbour offsets E, NE, NW, W, SW, SE: counterclockwise on screen."""


# --- Geometry (pure functions on coordinates) -------------------------------


def hex_center(h: Hex) -> Point:
    q, r = h
    return (2 * q + r, 3 * r)


def vertex_point(v: Vertex) -> Point:
    q, r, corner = v
    x, y = hex_center((q, r))
    return (x, y - 2) if corner is Corner.N else (x, y + 2)


def hex_corners(h: Hex) -> tuple[Vertex, ...]:
    """The 6 corners of `h`, clockwise from the top: N, NE, SE, S, SW, NW."""
    q, r = h
    return (
        (q, r, Corner.N),
        (q + 1, r - 1, Corner.S),  # bottom of the NE neighbour
        (q, r + 1, Corner.N),  # top of the SE neighbour
        (q, r, Corner.S),
        (q - 1, r + 1, Corner.N),  # top of the SW neighbour
        (q, r - 1, Corner.S),  # bottom of the NW neighbour
    )


def hex_sides(h: Hex) -> tuple[Edge, ...]:
    """The 6 sides of `h`, clockwise from the top right: NE, E, SE, SW, W, NW."""
    q, r = h
    return (
        (q, r, Side.NE),
        (q + 1, r, Side.W),  # W side of the E neighbour
        (q, r + 1, Side.NW),  # NW side of the SE neighbour
        (q - 1, r + 1, Side.NE),  # NE side of the SW neighbour
        (q, r, Side.W),
        (q, r, Side.NW),
    )


def edge_endpoints(e: Edge) -> tuple[Vertex, Vertex]:
    q, r, side = e
    if side is Side.NE:
        return ((q, r, Corner.N), (q + 1, r - 1, Corner.S))
    if side is Side.NW:
        return ((q, r - 1, Corner.S), (q, r, Corner.N))
    return ((q, r - 1, Corner.S), (q - 1, r + 1, Corner.N))


def is_land(h: Hex) -> bool:
    q, r = h
    return max(abs(q), abs(r), abs(q + r)) <= RADIUS


def _row_major(p: Point) -> tuple[int, int]:
    return (p[1], p[0])


def _edge_point(e: Edge) -> Point:
    (ax, ay), (bx, by) = (vertex_point(v) for v in edge_endpoints(e))
    return (ax + bx, ay + by)


# --- Canonical ids ----------------------------------------------------------

HEXES: tuple[Hex, ...] = tuple(
    sorted(
        (
            (q, r)
            for q in range(-RADIUS, RADIUS + 1)
            for r in range(-RADIUS, RADIUS + 1)
            if is_land((q, r))
        ),
        key=lambda h: _row_major(hex_center(h)),
    )
)

VERTICES: tuple[Vertex, ...] = tuple(
    sorted({v for h in HEXES for v in hex_corners(h)}, key=lambda v: _row_major(vertex_point(v)))
)
EDGES: tuple[Edge, ...] = tuple(
    sorted({e for h in HEXES for e in hex_sides(h)}, key=lambda e: _row_major(_edge_point(e)))
)

NUM_HEXES = len(HEXES)
NUM_VERTICES = len(VERTICES)
NUM_EDGES = len(EDGES)

HEX_ID: Mapping[Hex, HexId] = MappingProxyType({h: i for i, h in enumerate(HEXES)})
VERTEX_ID: Mapping[Vertex, VertexId] = MappingProxyType({v: i for i, v in enumerate(VERTICES)})
EDGE_ID: Mapping[Edge, EdgeId] = MappingProxyType({e: i for i, e in enumerate(EDGES)})

HEX_POS: tuple[Point, ...] = tuple(hex_center(h) for h in HEXES)
VERTEX_POS: tuple[Point, ...] = tuple(vertex_point(v) for v in VERTICES)
EDGE_POS: tuple[Point, ...] = tuple(_edge_point(e) for e in EDGES)


# --- Adjacency tables -------------------------------------------------------

HEX_VERTICES: tuple[tuple[VertexId, ...], ...] = tuple(
    tuple(VERTEX_ID[v] for v in hex_corners(h)) for h in HEXES
)
HEX_NEIGHBORS: tuple[tuple[HexId, ...], ...] = tuple(
    tuple(sorted(HEX_ID[(q + dq, r + dr)] for dq, dr in DIRECTIONS if is_land((q + dq, r + dr))))
    for q, r in HEXES
)
VERTEX_HEXES: tuple[tuple[HexId, ...], ...] = tuple(
    tuple(h for h in range(NUM_HEXES) if v in HEX_VERTICES[h]) for v in range(NUM_VERTICES)
)
EDGE_VERTICES: tuple[tuple[VertexId, VertexId], ...] = tuple(
    (min(a, b), max(a, b))
    for a, b in ((VERTEX_ID[x], VERTEX_ID[y]) for x, y in (edge_endpoints(e) for e in EDGES))
)
EDGE_HEXES: tuple[tuple[HexId, ...], ...] = tuple(
    tuple(h for h in range(NUM_HEXES) if EDGES[e] in hex_sides(HEXES[h])) for e in range(NUM_EDGES)
)
VERTEX_EDGES: tuple[tuple[EdgeId, ...], ...] = tuple(
    tuple(e for e in range(NUM_EDGES) if v in EDGE_VERTICES[e]) for v in range(NUM_VERTICES)
)
VERTEX_VERTICES: tuple[tuple[VertexId, ...], ...] = tuple(
    tuple(sorted(a if b == v else b for a, b in (EDGE_VERTICES[e] for e in VERTEX_EDGES[v])))
    for v in range(NUM_VERTICES)
)
EDGE_EDGES: tuple[tuple[EdgeId, ...], ...] = tuple(
    tuple(sorted({o for v in EDGE_VERTICES[e] for o in VERTEX_EDGES[v]} - {e}))
    for e in range(NUM_EDGES)
)


# --- Coast -----------------------------------------------------------------


def _walk_coast() -> tuple[EdgeId, ...]:
    """Coastal edges (touching one land hex) in clockwise order.

    Starts at the top-left coastal edge (the lowest coastal id, since ids are
    row-major) and leaves it through its right-hand endpoint, i.e. moving right
    along the top of the board, which is clockwise on screen.
    """
    coastal = {e for e in range(NUM_EDGES) if len(EDGE_HEXES[e]) == 1}
    start = min(coastal)
    a, b = EDGE_VERTICES[start]
    forward = a if VERTEX_POS[a][0] > VERTEX_POS[b][0] else b
    ring = [start]
    current = start
    while True:
        (nxt,) = (e for e in VERTEX_EDGES[forward] if e in coastal and e != current)
        if nxt == start:
            return tuple(ring)
        ring.append(nxt)
        a, b = EDGE_VERTICES[nxt]
        forward = b if a == forward else a
        current = nxt


COAST: tuple[EdgeId, ...] = _walk_coast()

# --- Board symmetries (ADR 0015) --------------------------------------------
#
# The board has 12 symmetries: 6 rotations and 6 mirror images. Each one is a
# relabelling of ids that preserves every adjacency table, so the game played
# on a transformed board is the same game. Symmetry `s` is:
#   s = 0..5:   rotate by 60 * s degrees counterclockwise (on screen)
#   s = 6..11:  mirror left-right, then rotate by 60 * (s - 6) degrees
# Tables are indexed [s][id] -> id of the image.
#
# WARNING: these are plain tuples, so table[-1] silently means symmetry 11.
# Call check_symmetry(s) before indexing in the same function (CI enforces it,
# tests/unit/test_symmetry_index_guard.py), or use engine.symmetry / apply_symmetry.

NUM_SYMMETRIES = 12


def check_symmetry(s: int) -> int:
    """Return `s` if it is a symmetry index (an int in 0..11), else raise ValueError.

    Without this, tuple indexing would silently accept negative indices (`-1` acts
    like `11`), and `apply_symmetry` would treat `12` like `6`.
    """
    if not isinstance(s, int) or not 0 <= s < NUM_SYMMETRIES:
        raise ValueError(f"symmetry must be an int in 0..{NUM_SYMMETRIES - 1}, got {s!r}")
    return s


def rotate_hex(h: Hex) -> Hex:
    """Rotate 60 degrees counterclockwise about the centre: cube (q, r, s) -> (-s, -q, -r)."""
    q, r = h
    return (q + r, -q)


def mirror_hex(h: Hex) -> Hex:
    """Mirror left-right about the vertical axis through the centre (x -> -x)."""
    q, r = h
    return (-q - r, r)


def apply_symmetry(s: int, h: Hex) -> Hex:
    """Image of hex coordinates `h` (land or sea) under symmetry `s` (0..11, else ValueError)."""
    check_symmetry(s)
    if s >= 6:
        h = mirror_hex(h)
    for _ in range(s % 6):
        h = rotate_hex(h)
    return h


def _vertex_hexes3(v: Vertex) -> frozenset[Hex]:
    """The 3 hexes (land or sea) meeting at vertex `v`: a name-free identity for it."""
    q, r, corner = v
    if corner is Corner.N:
        return frozenset({(q, r), (q, r - 1), (q + 1, r - 1)})
    return frozenset({(q, r), (q - 1, r + 1), (q, r + 1)})


def _edge_hexes2(e: Edge) -> frozenset[Hex]:
    """The 2 hexes (land or sea) on either side of edge `e`."""
    q, r, side = e
    other = {Side.NE: (q + 1, r - 1), Side.NW: (q, r - 1), Side.W: (q - 1, r)}[side]
    return frozenset({(q, r), other})


def _symmetry_tables() -> tuple[
    tuple[tuple[HexId, ...], ...],
    tuple[tuple[VertexId, ...], ...],
    tuple[tuple[EdgeId, ...], ...],
]:
    # Vertex and edge names are tied to an owning hex, so they don't transform
    # directly; the sets of hexes around them do.
    vertex_by_hexes = {_vertex_hexes3(v): i for i, v in enumerate(VERTICES)}
    edge_by_hexes = {_edge_hexes2(e): i for i, e in enumerate(EDGES)}
    hexes, vertices, edges = [], [], []
    for s in range(NUM_SYMMETRIES):
        hexes.append(tuple(HEX_ID[apply_symmetry(s, h)] for h in HEXES))
        vertices.append(
            tuple(
                vertex_by_hexes[frozenset(apply_symmetry(s, h) for h in _vertex_hexes3(v))]
                for v in VERTICES
            )
        )
        edges.append(
            tuple(
                edge_by_hexes[frozenset(apply_symmetry(s, h) for h in _edge_hexes2(e))]
                for e in EDGES
            )
        )
    return tuple(hexes), tuple(vertices), tuple(edges)


HEX_SYMMETRIES, VERTEX_SYMMETRIES, EDGE_SYMMETRIES = _symmetry_tables()

INVERSE_SYMMETRY: tuple[int, ...] = tuple(
    next(
        b
        for b in range(NUM_SYMMETRIES)
        if all(HEX_SYMMETRIES[b][HEX_SYMMETRIES[a][h]] == h for h in range(NUM_HEXES))
    )
    for a in range(NUM_SYMMETRIES)
)
"""INVERSE_SYMMETRY[s] undoes symmetry s."""


# --- Harbor frames (ADR 0015) -----------------------------------------------
#
# The rulebook frame has 9 harbor edges. Only 6 of the 12 symmetries keep them
# in place; the other 6 move them to a second, disjoint set: the same frame
# turned by 60 degrees. A legal board uses one of these two frames.

_RULEBOOK_HARBOR_EDGES = frozenset({0, 3, 17, 18, 38, 49, 61, 66, 69})  # verified (ADR 0009)

_FRAME_0 = tuple(sorted(_RULEBOOK_HARBOR_EDGES, key=COAST.index))

HARBOR_FRAMES: tuple[tuple[EdgeId, ...], ...] = (
    _FRAME_0,
    tuple(EDGE_SYMMETRIES[1][e] for e in _FRAME_0),
)
"""HARBOR_FRAMES[f][i] is the edge of harbor slot i in frame f.

Frame 0 is the rulebook frame, slots clockwise from edge 0. Frame 1 is frame 0
rotated 60 degrees counterclockwise, slot by slot (also clockwise).
"""

HARBOR_SLOT_OF_EDGE: Mapping[EdgeId, tuple[int, int]] = MappingProxyType(
    {e: (f, i) for f, frame in enumerate(HARBOR_FRAMES) for i, e in enumerate(frame)}
)
"""Edge id -> (frame, slot), for the 18 edges that can hold a harbor."""
