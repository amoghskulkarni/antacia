"""Top-level engine API: the only entry points other packages should call.

`legal_actions` is the single source of legality: `step` must accept exactly
the actions it returns and reject everything else.
"""

from engine.actions import Action
from engine.state import GameState
from engine.types import PlayerId


def legal_actions(state: GameState) -> tuple[Action, ...]:
    """All actions the acting player may take in `state`."""
    raise NotImplementedError


def step(state: GameState, action: Action) -> GameState:
    """Apply `action` and return the new state; `state` is left unchanged."""
    raise NotImplementedError


def is_terminal(state: GameState) -> bool:
    """True once a player has won."""
    raise NotImplementedError


def winner(state: GameState) -> PlayerId | None:
    """The winning player, or None if the game is not over."""
    raise NotImplementedError
