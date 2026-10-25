"""GameState: the complete, immutable state of one game.

Frozen, slotted dataclass built from tuples and other frozen values, so a
state can be hashed, shared between steps and never mutated (ADR 0002, 0004).
"""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class GameState:
    """Placeholder; fields are added in Week 2.

    Expected contents (not final):
        board layout, piece placement per vertex/edge, robber position,
        per-player hands, dev cards and piece counts, bank, dev deck,
        current player, phase, pending trade, awards, rng state.
    """
