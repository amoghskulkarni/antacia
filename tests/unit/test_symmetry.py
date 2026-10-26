"""Board symmetries (ADR 0015): topology tables, harbor frames, board and action transforms."""

import dataclasses

import pytest

from engine import topology as t
from engine.actions import (
    BuildCity,
    BuildRoad,
    BuildSettlement,
    EndTurn,
    MoveRobber,
    PlayMonopoly,
    ProposeTrade,
)
from engine.board import Layout, generate_board, vertex_harbors
from engine.rng import seed_rng
from engine.symmetry import transform_action, transform_board
from engine.types import Harbor, Offer, Resource, ResourceCounts

SYMS = range(t.NUM_SYMMETRIES)
TABLES = (t.HEX_SYMMETRIES, t.VERTEX_SYMMETRIES, t.EDGE_SYMMETRIES)


def _compose(table: tuple[tuple[int, ...], ...], a: int, b: int) -> tuple[int, ...]:
    """Apply symmetry a, then b."""
    return tuple(table[b][table[a][x]] for x in range(len(table[a])))


# --- Topology tables --------------------------------------------------------


def test_there_are_12_distinct_permutations_of_each_kind() -> None:
    assert t.NUM_SYMMETRIES == 12
    for table, n in zip(TABLES, (t.NUM_HEXES, t.NUM_VERTICES, t.NUM_EDGES), strict=True):
        assert len(table) == 12
        assert len(set(table)) == 12
        for perm in table:
            assert sorted(perm) == list(range(n))


def test_symmetry_0_is_the_identity() -> None:
    for table in TABLES:
        assert table[0] == tuple(range(len(table[0])))


def test_every_symmetry_preserves_all_adjacency() -> None:
    # The key property: each symmetry relabels the board without changing what touches what.
    H, V, E = t.HEX_SYMMETRIES, t.VERTEX_SYMMETRIES, t.EDGE_SYMMETRIES
    for s in SYMS:
        for h in range(t.NUM_HEXES):
            assert {H[s][n] for n in t.HEX_NEIGHBORS[h]} == set(t.HEX_NEIGHBORS[H[s][h]])
            assert {V[s][v] for v in t.HEX_VERTICES[h]} == set(t.HEX_VERTICES[H[s][h]])
        for v in range(t.NUM_VERTICES):
            assert {V[s][n] for n in t.VERTEX_VERTICES[v]} == set(t.VERTEX_VERTICES[V[s][v]])
            assert {E[s][e] for e in t.VERTEX_EDGES[v]} == set(t.VERTEX_EDGES[V[s][v]])
        for e in range(t.NUM_EDGES):
            assert {V[s][v] for v in t.EDGE_VERTICES[e]} == set(t.EDGE_VERTICES[E[s][e]])
            assert {H[s][h] for h in t.EDGE_HEXES[e]} == set(t.EDGE_HEXES[E[s][e]])
        assert {E[s][e] for e in t.COAST} == set(t.COAST)


def test_symmetries_0_to_5_are_rotations_by_60_degrees_counterclockwise() -> None:
    east, north_east = t.HEX_ID[(2, 0)], t.HEX_ID[(2, -2)]
    assert t.HEX_SYMMETRIES[1][east] == north_east  # up = counterclockwise on screen
    for table in TABLES:
        for k in range(6):
            assert _compose(table, k, 1) == table[(k + 1) % 6]


def test_symmetry_6_is_the_left_right_mirror() -> None:
    for table, pos in zip(TABLES, (t.HEX_POS, t.VERTEX_POS, t.EDGE_POS), strict=True):
        for x, (px, py) in enumerate(pos):
            assert pos[table[6][x]] == (-px, py)
        assert _compose(table, 6, 6) == table[0]


def test_symmetries_6_to_11_are_mirror_then_rotate() -> None:
    for table in TABLES:
        for k in range(6):
            assert _compose(table, 6, k) == table[6 + k]


def test_inverse_symmetry_undoes_each_symmetry() -> None:
    for table in TABLES:
        for s in SYMS:
            assert _compose(table, s, t.INVERSE_SYMMETRY[s]) == table[0]


# --- Harbor frames ----------------------------------------------------------


def test_frame_0_is_the_rulebook_frame_clockwise_from_edge_0() -> None:
    assert t.HARBOR_FRAMES[0] == (0, 3, 17, 38, 61, 69, 66, 49, 18)


def test_frame_1_is_frame_0_rotated_60_degrees_slot_by_slot() -> None:
    assert t.HARBOR_FRAMES[1] == tuple(t.EDGE_SYMMETRIES[1][e] for e in t.HARBOR_FRAMES[0])
    assert not set(t.HARBOR_FRAMES[0]) & set(t.HARBOR_FRAMES[1])


def test_every_symmetry_maps_a_frame_onto_a_frame() -> None:
    for s in SYMS:
        for frame in t.HARBOR_FRAMES:
            image = {t.EDGE_SYMMETRIES[s][e] for e in frame}
            assert image in ({*t.HARBOR_FRAMES[0]}, {*t.HARBOR_FRAMES[1]})


def test_harbor_slot_of_edge_inverts_the_frames() -> None:
    assert len(t.HARBOR_SLOT_OF_EDGE) == 18
    for f, frame in enumerate(t.HARBOR_FRAMES):
        for i, e in enumerate(frame):
            assert t.HARBOR_SLOT_OF_EDGE[e] == (f, i)


def test_documented_slot_formulas() -> None:
    # docs/board-symmetry.md: rotation by 60k degrees and the left-right mirror on (frame, slot).
    def image(s: int, f: int, i: int) -> tuple[int, int]:
        return t.HARBOR_SLOT_OF_EDGE[t.EDGE_SYMMETRIES[s][t.HARBOR_FRAMES[f][i]]]

    for f in (0, 1):
        for i in range(9):
            for k in range(6):
                assert image(k, f, i) == ((f + k) % 2, (i - 3 * ((f + k) // 2)) % 9)
            assert image(6, f, i) == (1 - f, (3 - i) % 9)


# --- Boards -----------------------------------------------------------------


def test_generated_boards_use_frame_0() -> None:
    assert generate_board(Layout.BEGINNER, seed_rng(0))[0].frame == 0
    assert generate_board(Layout.RANDOM, seed_rng(7))[0].frame == 0


def test_vertex_harbors_lists_both_ends_of_each_harbor_edge() -> None:
    board, _ = generate_board(Layout.BEGINNER, seed_rng(0))
    harbors = vertex_harbors(board)
    assert len(harbors) == t.NUM_VERTICES
    assert sum(h is not None for h in harbors) == 18
    a, b = t.EDGE_VERTICES[17]
    assert harbors[a] is harbors[b] is Harbor.ORE


@pytest.mark.parametrize("s", SYMS)
def test_transform_board_moves_everything_with_the_symmetry(s: int) -> None:
    board, _ = generate_board(Layout.RANDOM, seed_rng(11))
    image = transform_board(board, s)
    for h in range(t.NUM_HEXES):
        g = t.HEX_SYMMETRIES[s][h]
        assert image.terrains[g] is board.terrains[h]
        assert image.tokens[g] == board.tokens[h]
    before, after = vertex_harbors(board), vertex_harbors(image)
    for v in range(t.NUM_VERTICES):
        assert after[t.VERTEX_SYMMETRIES[s][v]] is before[v]
    assert image.frame == (s % 2 if s < 6 else 1 - s % 2)


@pytest.mark.parametrize("s", SYMS)
def test_transform_board_inverse_round_trips(s: int) -> None:
    board, _ = generate_board(Layout.BEGINNER, seed_rng(0))
    assert transform_board(transform_board(board, s), t.INVERSE_SYMMETRY[s]) == board


# --- Actions ----------------------------------------------------------------


def test_transform_action_relabels_board_locations() -> None:
    s = 3
    assert transform_action(BuildRoad(edge=5), s) == BuildRoad(edge=t.EDGE_SYMMETRIES[s][5])
    assert transform_action(BuildSettlement(vertex=8), s) == BuildSettlement(
        vertex=t.VERTEX_SYMMETRIES[s][8]
    )
    assert transform_action(BuildCity(vertex=8), s) == BuildCity(vertex=t.VERTEX_SYMMETRIES[s][8])
    robber = transform_action(MoveRobber(hex=4, victim=2), s)
    assert robber == MoveRobber(hex=t.HEX_SYMMETRIES[s][4], victim=2)  # players don't move


def test_transform_action_leaves_non_board_actions_alone() -> None:
    offer = Offer(give=ResourceCounts(brick=1), want=ResourceCounts(ore=1))
    for action in (EndTurn(), PlayMonopoly(resource=Resource.ORE), ProposeTrade(offer=offer)):
        for s in SYMS:
            assert transform_action(action, s) is action


@pytest.mark.parametrize("s", SYMS)
def test_transform_action_inverse_round_trips(s: int) -> None:
    for action in (BuildRoad(edge=70), BuildSettlement(vertex=0), MoveRobber(hex=18, victim=None)):
        image = transform_action(action, s)
        assert transform_action(image, t.INVERSE_SYMMETRY[s]) == action
        assert dataclasses.is_dataclass(image)


# --- Invalid symmetry indices -----------------------------------------------

BAD_SYMMETRIES = [-1, -12, 12, 13, 100]


@pytest.mark.parametrize("s", BAD_SYMMETRIES)
def test_out_of_range_symmetry_is_rejected_everywhere(s: int) -> None:
    board, _ = generate_board(Layout.BEGINNER, seed_rng(0))
    with pytest.raises(ValueError, match=str(s)):
        transform_board(board, s)
    with pytest.raises(ValueError, match=str(s)):
        t.apply_symmetry(s, (0, 0))
    # Even actions that no symmetry would change must not accept a bad index.
    for action in (BuildRoad(edge=3), MoveRobber(hex=4, victim=None), EndTurn()):
        with pytest.raises(ValueError, match=str(s)):
            transform_action(action, s)


@pytest.mark.parametrize("s", [0.0, 1.5, "3", None])
def test_non_integer_symmetry_is_rejected(s: object) -> None:
    board, _ = generate_board(Layout.BEGINNER, seed_rng(0))
    with pytest.raises(ValueError):
        transform_board(board, s)  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        transform_action(EndTurn(), s)  # type: ignore[arg-type]


def test_every_valid_symmetry_is_still_accepted() -> None:
    board, _ = generate_board(Layout.BEGINNER, seed_rng(0))
    for s in SYMS:
        transform_board(board, s)
        transform_action(EndTurn(), s)
        t.apply_symmetry(s, (0, 0))
