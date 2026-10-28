"""Antacia rules engine: deterministic, immutable, copy-on-step.

Public API (see engine/CLAUDE.md):
    new_game(seed, num_players, layout) -> state
    step(state, action) -> new_state
    legal_actions(state) -> tuple of actions
    is_terminal(state), winner(state)
"""

from engine.actions import Action
from engine.game import is_terminal, legal_actions, new_game, step, winner
from engine.state import GameState

__all__ = [
    "Action",
    "GameState",
    "is_terminal",
    "legal_actions",
    "new_game",
    "step",
    "winner",
]
