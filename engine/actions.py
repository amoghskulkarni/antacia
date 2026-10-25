"""Actions a player can take, and (later) their flat integer encoding.

Each action kind is a frozen dataclass; `Action` is the union of all kinds.
This mirrors a Rust enum, so the port can match on it exhaustively.

The flat id encoding and legality mask for RL arrive in Week 6 (ADR 0005).
"""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class EndTurn:
    """End the active player's turn."""


# Grows into a union as rules are added, e.g. `EndTurn | RollDice | BuildRoad`.
type Action = EndTurn
