"""Small shared types: resources, terrains, development cards, player ids.

Enum values are explicit integers, never `auto()`, because they become part of
the observation encoding, the action ids and the golden replays (and must match
the future Rust port exactly).
"""

from enum import IntEnum

type PlayerId = int
"""Seat index, 0 .. num_players - 1, in turn order."""


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


class DevCard(IntEnum):
    KNIGHT = 0
    VICTORY_POINT = 1
    ROAD_BUILDING = 2
    YEAR_OF_PLENTY = 3
    MONOPOLY = 4
