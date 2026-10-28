"""GameState: the complete, immutable state of one game.

Frozen, slotted dataclass built from tuples and other frozen values, so a
state can be hashed, shared between steps and never mutated (ADR 0002, 0004).

Fields arrive with the rules that need them. Anything that can be computed
from other fields (the bank, pieces left, the setup round) is computed, not
stored, so it can never disagree with the board.
"""

from dataclasses import dataclass

from engine.board import Board
from engine.rng import Rng
from engine.types import Phase, PlayerId, ResourceCounts, VertexId


@dataclass(frozen=True, slots=True)
class PlayerState:
    hand: ResourceCounts = ResourceCounts()


@dataclass(frozen=True, slots=True)
class GameState:
    board: Board
    rng: Rng
    phase: Phase
    current_player: PlayerId
    players: tuple[PlayerState, ...]
    """One entry per seat, in turn order."""
    vertex_owner: tuple[PlayerId | None, ...]
    """Owner of the settlement on each VertexId, or None."""
    road_owner: tuple[PlayerId | None, ...]
    """Owner of the road on each EdgeId, or None."""
    pending_road_vertex: VertexId | None
    """Setup only: the settlement just placed, which the next road must touch.
    None means the current player places a settlement next."""
