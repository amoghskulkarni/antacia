"""Top-level engine API: the only entry points other packages should call.

`legal_actions` is the single source of legality: `step` must accept exactly
the actions it returns and reject everything else.
"""

from engine import topology as t
from engine.actions import Action
from engine.board import Layout, generate_board
from engine.rng import seed_rng
from engine.state import GameState, PlayerState
from engine.types import Phase, PlayerId

MIN_PLAYERS = 3
MAX_PLAYERS = 4


def new_game(seed: int, num_players: int, layout: Layout = Layout.RANDOM) -> GameState:
    """A fresh game in the setup phase; seat 0 starts (ADR 0016).

    Callers (server, eval, env) shuffle who sits in which seat.
    """
    if not MIN_PLAYERS <= num_players <= MAX_PLAYERS:
        raise ValueError(f"the base game needs 3 or 4 players, got {num_players}")
    board, rng = generate_board(layout, seed_rng(seed))
    return GameState(
        board=board,
        rng=rng,
        phase=Phase.SETUP,
        current_player=0,
        players=(PlayerState(),) * num_players,
        vertex_owner=(None,) * t.NUM_VERTICES,
        road_owner=(None,) * t.NUM_EDGES,
        pending_road_vertex=None,
    )


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
