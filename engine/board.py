"""Per-game board layout: terrains, number tokens, harbors (ADR 0009).

The static topology lives in engine/topology.py; this module only decides what
is printed on each hex and harbor slot. A `Board` is created once per game by
`generate_board` and shared, unchanged, by every later GameState. The robber's
position changes during play, so it belongs to GameState, not here.

Rules: docs/rules-spec.md sections 1 (components) and 2 (layout).
"""

from dataclasses import dataclass
from enum import StrEnum

from engine import topology as t
from engine.rng import Rng, randbelow, shuffle
from engine.types import Harbor, HexId, Terrain


class Layout(StrEnum):
    BEGINNER = "beginner"
    RANDOM = "random"


TERRAIN_TILES: tuple[Terrain, ...] = (
    (Terrain.HILLS,) * 3
    + (Terrain.FOREST,) * 4
    + (Terrain.MOUNTAINS,) * 3
    + (Terrain.FIELDS,) * 4
    + (Terrain.PASTURE,) * 4
    + (Terrain.DESERT,)
)

TOKEN_SEQUENCE: tuple[int, ...] = (5, 2, 6, 3, 8, 10, 9, 12, 11, 4, 8, 10, 9, 4, 5, 6, 3, 11)
"""Number tokens A..R, in the order they are laid along the spiral."""

HARBOR_TILES: tuple[Harbor, ...] = (Harbor.GENERIC,) * 4 + (
    Harbor.BRICK,
    Harbor.LUMBER,
    Harbor.ORE,
    Harbor.GRAIN,
    Harbor.WOOL,
)

RED_NUMBERS = frozenset({6, 8})


@dataclass(frozen=True, slots=True)
class Board:
    terrains: tuple[Terrain, ...]
    """Terrain per HexId."""
    tokens: tuple[int | None, ...]
    """Number token per HexId; None on the desert."""
    harbors: tuple[Harbor, ...]
    """Harbor type per slot; slot i sits on edge topology.HARBOR_SLOTS[i]."""

    def desert(self) -> HexId:
        return self.terrains.index(Terrain.DESERT)


def spiral(start_corner: int) -> tuple[HexId, ...]:
    """All hexes along the counterclockwise token spiral.

    Starts on the outer corner hex in direction `topology.DIRECTIONS[start_corner]`
    (0 = east, then counterclockwise), walks the outer ring, steps onto the inner
    ring next to the start, walks it, and ends in the centre.
    """
    path: list[HexId] = []
    for radius in range(t.RADIUS, 0, -1):
        dq, dr = t.DIRECTIONS[start_corner]
        q, r = dq * radius, dr * radius
        for side in range(6):
            step_q, step_r = t.DIRECTIONS[(start_corner + side + 2) % 6]
            for _ in range(radius):
                path.append(t.HEX_ID[(q, r)])
                q, r = q + step_q, r + step_r
    path.append(t.HEX_ID[(0, 0)])
    return tuple(path)


def _place_tokens(terrains: tuple[Terrain, ...], start_corner: int) -> tuple[int | None, ...]:
    tokens: list[int | None] = [None] * t.NUM_HEXES
    remaining = iter(TOKEN_SEQUENCE)
    for h in spiral(start_corner):
        if terrains[h] is not Terrain.DESERT:
            tokens[h] = next(remaining)
    return tuple(tokens)


# Rulebook starting board, rows top to bottom (HexId order).
_BEGINNER_TERRAINS = (
    (Terrain.MOUNTAINS, Terrain.PASTURE, Terrain.FOREST)
    + (Terrain.FIELDS, Terrain.HILLS, Terrain.PASTURE, Terrain.HILLS)
    + (Terrain.FIELDS, Terrain.FOREST, Terrain.DESERT, Terrain.FOREST, Terrain.MOUNTAINS)
    + (Terrain.FOREST, Terrain.MOUNTAINS, Terrain.FIELDS, Terrain.PASTURE)
    + (Terrain.HILLS, Terrain.FIELDS, Terrain.PASTURE)
)
_BEGINNER_TOKENS: tuple[int | None, ...] = (
    (10, 2, 9) + (12, 6, 4, 10) + (9, 11, None, 3, 8) + (8, 3, 4, 5) + (5, 6, 11)
)
# VERIFY: placeholder, not the rulebook's beginner harbor assignment.
_BEGINNER_HARBORS = (
    (Harbor.GENERIC, Harbor.GRAIN)
    + (Harbor.LUMBER, Harbor.ORE)
    + (Harbor.BRICK, Harbor.GENERIC)
    + (Harbor.GENERIC, Harbor.GENERIC, Harbor.WOOL)
)


def generate_board(layout: Layout, rng: Rng) -> tuple[Board, Rng]:
    """Create the layout for one game.

    `random` draws, in this order: terrain shuffle, spiral start corner,
    harbor shuffle. `beginner` draws nothing and returns `rng` unchanged.
    """
    if layout is Layout.BEGINNER:
        return Board(_BEGINNER_TERRAINS, _BEGINNER_TOKENS, _BEGINNER_HARBORS), rng
    terrains, rng = shuffle(rng, TERRAIN_TILES)
    corner, rng = randbelow(rng, 6)
    harbors, rng = shuffle(rng, HARBOR_TILES)
    return Board(terrains, _place_tokens(terrains, corner), harbors), rng


def red_numbers_adjacent(board: Board) -> bool:
    """True if two neighbouring hexes both carry a 6 or an 8."""
    return any(
        board.tokens[a] in RED_NUMBERS and board.tokens[b] in RED_NUMBERS
        for a in range(t.NUM_HEXES)
        for b in t.HEX_NEIGHBORS[a]
    )


# --- ASCII rendering (debugging and tests only) -----------------------------

_TERRAIN_ABBR = {
    Terrain.HILLS: "HI",
    Terrain.FOREST: "FO",
    Terrain.MOUNTAINS: "MO",
    Terrain.FIELDS: "FI",
    Terrain.PASTURE: "PA",
    Terrain.DESERT: "DE",
}
_SIDE_NAMES = ("NE", "E", "SE", "SW", "W", "NW")


def _harbor_label(harbor: Harbor) -> str:
    return "3:1" if harbor is Harbor.GENERIC else f"2:1 {harbor.name.lower()}"


def render_board(board: Board) -> str:
    """Hex rows with terrain and token, then one line per harbor slot."""
    lines: list[str] = []
    rows: dict[int, list[HexId]] = {}
    for h in range(t.NUM_HEXES):
        rows.setdefault(t.HEXES[h][1], []).append(h)
    for r in sorted(rows):
        cells = []
        for h in rows[r]:
            token = board.tokens[h]
            cells.append(f"[{_TERRAIN_ABBR[board.terrains[h]]}{'' if token is None else token:>2}]")
        lines.append(" " * (3 * abs(r)) + "".join(cells))
    lines.append("")
    for slot, (edge, harbor) in enumerate(zip(t.HARBOR_SLOTS, board.harbors, strict=True)):
        (h,) = t.EDGE_HEXES[edge]
        side = _SIDE_NAMES[t.hex_sides(t.HEXES[h]).index(t.EDGES[edge])]
        lines.append(f"harbor {slot}: hex {h:>2} {side:<2} side  {_harbor_label(harbor)}")
    return "\n".join(lines)


_MAP_COLS = 8  # characters per x half-unit
_MAP_ROWS = 4  # lines per y half-unit


def render_topology() -> str:
    """Draw the static board with every hex (H), vertex (v) and edge (e) id at its true position.

    Debugging aid for the numbering of ADR 0008. Each hex shows its id and axial
    (q, r); each edge label sits on its edge, joined to its endpoints by strokes.
    Positions come from `topology.*_POS`, so the picture is the numbering, not a
    separate description of it.
    """
    cells: dict[tuple[int, int], str] = {}

    def put(line: int, col: int, text: str) -> None:
        for i, ch in enumerate(text):
            cells[(line, col - len(text) // 2 + i)] = ch

    # Strokes first, so labels overwrite them.
    for e in range(t.NUM_EDGES):
        (x1, y1), (x2, y2) = sorted((t.VERTEX_POS[v] for v in t.EDGE_VERTICES[e]), key=_by_row)
        top, bottom = y1 * _MAP_ROWS, y2 * _MAP_ROWS
        mid = (top + bottom) // 2
        stroke = "|" if x1 == x2 else ("/" if x2 < x1 else "\\")
        c1, c2 = x1 * _MAP_COLS, x2 * _MAP_COLS
        for line in range(top + 1, bottom):
            if line != mid:
                put(line, c1 + (c2 - c1) * (line - top) // (bottom - top), stroke)

    for e, (x, y) in enumerate(t.EDGE_POS):  # twice the midpoint
        put(y * _MAP_ROWS // 2, x * _MAP_COLS // 2, f"e{e}")
    for v, (x, y) in enumerate(t.VERTEX_POS):
        put(y * _MAP_ROWS, x * _MAP_COLS, f"v{v}")
    for h, (x, y) in enumerate(t.HEX_POS):
        q, r = t.HEXES[h]
        put(y * _MAP_ROWS - 1, x * _MAP_COLS, f"H{h}")
        put(y * _MAP_ROWS + 1, x * _MAP_COLS, f"({q},{r})")

    first_line = min(line for line, _ in cells)
    last_line = max(line for line, _ in cells)
    first_col = min(col for _, col in cells)
    last_col = max(col for _, col in cells)
    return "\n".join(
        "".join(cells.get((line, col), " ") for col in range(first_col, last_col + 1)).rstrip()
        for line in range(first_line, last_line + 1)
    )


def _by_row(p: t.Point) -> tuple[int, int]:
    return (p[1], p[0])
