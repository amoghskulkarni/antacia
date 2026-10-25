from collections import Counter

from hypothesis import given
from hypothesis import strategies as st

from engine.board import (
    HARBOR_TILES,
    TERRAIN_TILES,
    TOKEN_SEQUENCE,
    Layout,
    generate_board,
    red_numbers_adjacent,
)
from engine.rng import seed_rng
from engine.types import Terrain

seeds = st.integers(min_value=0, max_value=2**64 - 1)


@given(seeds)
def test_random_board_uses_every_component_once(seed: int) -> None:
    board, _ = generate_board(Layout.RANDOM, seed_rng(seed))
    assert Counter(board.terrains) == Counter(TERRAIN_TILES)
    assert Counter(board.harbors) == Counter(HARBOR_TILES)
    assert sorted(x for x in board.tokens if x is not None) == sorted(TOKEN_SEQUENCE)


@given(seeds)
def test_only_the_desert_has_no_token(seed: int) -> None:
    board, _ = generate_board(Layout.RANDOM, seed_rng(seed))
    for terrain, token in zip(board.terrains, board.tokens, strict=True):
        assert (token is None) == (terrain is Terrain.DESERT)


@given(seeds)
def test_red_numbers_are_never_adjacent(seed: int) -> None:
    # ADR 0009: the official spiral keeps 6s and 8s apart.
    board, _ = generate_board(Layout.RANDOM, seed_rng(seed))
    assert not red_numbers_adjacent(board)


@given(seeds)
def test_generation_is_deterministic(seed: int) -> None:
    assert generate_board(Layout.RANDOM, seed_rng(seed)) == generate_board(
        Layout.RANDOM, seed_rng(seed)
    )
