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
