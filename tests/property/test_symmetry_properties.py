from hypothesis import given
from hypothesis import strategies as st

from engine import topology as t
from engine.board import Layout, generate_board, red_numbers_adjacent, vertex_harbors
from engine.game import legal_actions, new_game, step
from engine.rng import seed_rng
from engine.symmetry import transform_action, transform_board, transform_state
from engine.types import Phase

seeds = st.integers(min_value=0, max_value=2**64 - 1)
syms = st.integers(min_value=0, max_value=t.NUM_SYMMETRIES - 1)


@given(seeds, syms)
def test_transformed_boards_keep_every_component(seed: int, s: int) -> None:
    board, _ = generate_board(Layout.RANDOM, seed_rng(seed))
    image = transform_board(board, s)
    assert sorted(image.terrains) == sorted(board.terrains)
    assert sorted(image.harbors) == sorted(board.harbors)
    assert sorted(x for x in image.tokens if x is not None) == sorted(
        x for x in board.tokens if x is not None
    )


@given(seeds, syms)
def test_transformed_boards_never_put_red_numbers_side_by_side(seed: int, s: int) -> None:
    board, _ = generate_board(Layout.RANDOM, seed_rng(seed))
    assert not red_numbers_adjacent(transform_board(board, s))


@given(seeds, syms)
def test_harbor_vertices_of_a_transformed_board_are_the_transformed_vertices(
    seed: int, s: int
) -> None:
    board, _ = generate_board(Layout.RANDOM, seed_rng(seed))
    before, after = vertex_harbors(board), vertex_harbors(transform_board(board, s))
    assert [after[t.VERTEX_SYMMETRIES[s][v]] for v in range(t.NUM_VERTICES)] == list(before)


@given(seeds, syms, syms)
def test_transforming_twice_is_transforming_by_the_composition(seed: int, a: int, b: int) -> None:
    board, _ = generate_board(Layout.RANDOM, seed_rng(seed))
    composed = next(
        s
        for s in range(t.NUM_SYMMETRIES)
        if all(
            t.HEX_SYMMETRIES[s][h] == t.HEX_SYMMETRIES[b][t.HEX_SYMMETRIES[a][h]]
            for h in range(t.NUM_HEXES)
        )
    )
    assert transform_board(transform_board(board, a), b) == transform_board(board, composed)


# --- Equivariance of the rules (ADR 0015) -----------------------------------
# Turning or mirroring the board must give the same game: the transformed state
# offers exactly the transformed actions, and stepping commutes with the symmetry.

player_counts = st.sampled_from([3, 4])


@given(st.data(), seeds, player_counts, syms)
def test_setup_legal_actions_are_equivariant(
    data: st.DataObject, seed: int, num_players: int, s: int
) -> None:
    state = new_game(seed=seed, num_players=num_players)
    while state.phase is Phase.SETUP:
        legal = legal_actions(state)
        image = transform_state(state, s)
        assert set(legal_actions(image)) == {transform_action(a, s) for a in legal}
        state = step(state, data.draw(st.sampled_from(legal)))


@given(st.data(), seeds, player_counts, syms)
def test_setup_step_commutes_with_every_symmetry(
    data: st.DataObject, seed: int, num_players: int, s: int
) -> None:
    state = new_game(seed=seed, num_players=num_players)
    while state.phase is Phase.SETUP:
        action = data.draw(st.sampled_from(legal_actions(state)))
        after = step(state, action)
        assert step(transform_state(state, s), transform_action(action, s)) == transform_state(
            after, s
        )
        state = after
