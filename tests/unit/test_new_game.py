import dataclasses

import pytest

from engine import topology as t
from engine.board import Layout, generate_board
from engine.game import new_game
from engine.rng import seed_rng
from engine.types import Phase, ResourceCounts


@pytest.mark.parametrize("num_players", [3, 4])
def test_new_game_starts_in_setup_with_seat_0_and_an_empty_board(num_players: int) -> None:
    # rules-spec 2; ADR 0016: seat 0 always starts.
    state = new_game(seed=1, num_players=num_players)
    assert state.phase is Phase.SETUP
    assert state.current_player == 0
    assert state.pending_road_vertex is None
    assert len(state.players) == num_players
    assert all(p.hand == ResourceCounts() for p in state.players)
    assert state.vertex_owner == (None,) * t.NUM_VERTICES
    assert state.road_owner == (None,) * t.NUM_EDGES


@pytest.mark.parametrize("num_players", [0, 1, 2, 5, 6])
def test_new_game_rejects_player_counts_outside_3_to_4(num_players: int) -> None:
    # rules-spec title: base game, 3-4 players.
    with pytest.raises(ValueError, match="3 or 4 players"):
        new_game(seed=1, num_players=num_players)


def test_new_game_builds_the_board_from_the_seed() -> None:
    # ADR 0009: board generation makes the first RNG draws of every game.
    state = new_game(seed=7, num_players=4)
    board, rng = generate_board(Layout.RANDOM, seed_rng(7))
    assert state.board == board
    assert state.rng == rng


def test_new_game_supports_the_beginner_layout() -> None:
    state = new_game(seed=7, num_players=3, layout=Layout.BEGINNER)
    assert state.board == generate_board(Layout.BEGINNER, seed_rng(0))[0]


def test_new_game_is_deterministic() -> None:
    assert new_game(seed=42, num_players=4) == new_game(seed=42, num_players=4)
    assert new_game(seed=42, num_players=4) != new_game(seed=43, num_players=4)


def test_game_state_is_immutable() -> None:
    # ADR 0002: copy-on-step, never mutate.
    state = new_game(seed=1, num_players=3)
    with pytest.raises(dataclasses.FrozenInstanceError):
        state.current_player = 1  # type: ignore[misc]
