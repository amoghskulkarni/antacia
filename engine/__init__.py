"""Antacia rules engine: deterministic, immutable, copy-on-step.

Public API (see engine/CLAUDE.md):
    step(state, action) -> new_state
    legal_actions(state) -> tuple of actions
    is_terminal(state), winner(state)
"""

from engine.actions import Action
from engine.game import is_terminal, legal_actions, step, winner
from engine.state import GameState

__all__ = [
    "Action",
    "GameState",
    "is_terminal",
    "legal_actions",
    "step",
    "winner",
]
