"""Top-level engine API: the only entry points other packages should call.

`legal_actions` is the single source of legality: `step` must accept exactly
the actions it returns and reject everything else.
"""

from typing import assert_never

from engine import topology as t
from engine.actions import Action
from engine.board import Layout, generate_board
from engine.rng import seed_rng
from engine.rules.setup import apply_setup_action, setup_actions
from engine.state import GameState, PlayerState
from engine.types import Phase, PlayerId

MIN_PLAYERS = 3
MAX_PLAYERS = 4


class IllegalActionError(ValueError):
    """`step` was given an action that `legal_actions` does not list."""


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
    match state.phase:
        case Phase.SETUP:
            return setup_actions(state)
        case Phase.PRE_ROLL:
            return ()  # RollDice arrives with rules-spec 3 (Week 3)
        case _:
            assert_never(state.phase)


def step(state: GameState, action: Action) -> GameState:
    """Apply `action` and return the new state; `state` is left unchanged.

    Raises IllegalActionError for any action `legal_actions` does not list.
    Checking membership in the full list is slow but can never drift from
    `legal_actions`; optimise only after profiling (Week 7).
    """
    if action not in legal_actions(state):
        raise IllegalActionError(f"{action!r} is not legal in phase {state.phase.name}")
    match state.phase:
        case Phase.SETUP:
            return apply_setup_action(state, action)
        case Phase.PRE_ROLL:
            raise AssertionError("no action is legal before the roll yet")
        case _:
            assert_never(state.phase)


def is_terminal(state: GameState) -> bool:
    """True once a player has won."""
    raise NotImplementedError


def winner(state: GameState) -> PlayerId | None:
    """The winning player, or None if the game is not over."""
    raise NotImplementedError
