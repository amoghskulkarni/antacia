"""Small shared types: resources, terrains, development cards, player ids.

Enum values are explicit integers, never `auto()`, because they become part of
the observation encoding, the action ids and the golden replays (and must match
the future Rust port exactly).
"""

from dataclasses import dataclass
from enum import IntEnum

type PlayerId = int
"""Seat index, 0 .. num_players - 1, in turn order."""

# Dense board ids, 0 .. N-1, in a fixed canonical order defined by engine/board.py.
# Actions and observations use these; coordinates are only used to build topology.
type HexId = int
type VertexId = int
type EdgeId = int


class Resource(IntEnum):
    BRICK = 0
    LUMBER = 1
    ORE = 2
    GRAIN = 3
    WOOL = 4


class Terrain(IntEnum):
    HILLS = 0  # brick
    FOREST = 1  # lumber
    MOUNTAINS = 2  # ore
    FIELDS = 3  # grain
    PASTURE = 4  # wool
    DESERT = 5  # produces nothing


class Harbor(IntEnum):
    """Harbor tile type. 2:1 harbors share their value with the matching Resource."""

    BRICK = 0
    LUMBER = 1
    ORE = 2
    GRAIN = 3
    WOOL = 4
    GENERIC = 5  # 3:1, any resource


class DevCard(IntEnum):
    KNIGHT = 0
    VICTORY_POINT = 1
    ROAD_BUILDING = 2
    YEAR_OF_PLENTY = 3
    MONOPOLY = 4


@dataclass(frozen=True, slots=True)
class ResourceCounts:
    """A count per resource, e.g. one side of a trade offer."""

    brick: int = 0
    lumber: int = 0
    ore: int = 0
    grain: int = 0
    wool: int = 0

    def as_tuple(self) -> tuple[int, int, int, int, int]:
        """Counts in `Resource` order."""
        return (self.brick, self.lumber, self.ore, self.grain, self.wool)


@dataclass(frozen=True, slots=True)
class Offer:
    """A domestic trade offer from the acting player's point of view.

    The proposer is not stored: it is whoever acts (docs/trade-protocol.md section 2).
    Validity (non-empty sides, no shared resource, affordability) is checked by
    legal_actions, not here.
    """

    give: ResourceCounts
    want: ResourceCounts
