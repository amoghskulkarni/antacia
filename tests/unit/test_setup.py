"""Setup phase rules (rules-spec 2). States are built through new_game and step only."""

import pytest

from engine import topology as t
from engine.actions import BuildRoad, BuildSettlement, RollDice
from engine.board import Layout
from engine.game import IllegalActionError, legal_actions, new_game, step
from engine.state import GameState
from engine.types import Phase, ResourceCounts


def first_settlement(state: GameState) -> BuildSettlement:
    return next(a for a in legal_actions(state) if isinstance(a, BuildSettlement))


def first_road(state: GameState) -> BuildRoad:
    return next(a for a in legal_actions(state) if isinstance(a, BuildRoad))


def place_pair(state: GameState) -> GameState:
    """The current player places the lowest-id legal settlement, then the lowest-id road."""
    state = step(state, first_settlement(state))
    return step(state, first_road(state))


def place_pair_at(state: GameState, vertex: int) -> GameState:
    """The current player places a settlement on `vertex`, then the lowest-id legal road."""
    state = step(state, BuildSettlement(vertex))
    return step(state, first_road(state))


def test_the_first_settlement_may_go_on_any_vertex() -> None:
    # rules-spec 2: placement; an empty board has no other restriction.
    state = new_game(seed=1, num_players=4)
    assert legal_actions(state) == tuple(BuildSettlement(v) for v in range(t.NUM_VERTICES))


def test_placing_a_settlement_records_it_and_asks_the_same_player_for_a_road() -> None:
    # rules-spec 2: each player places a pair, settlement then road.
    state = step(new_game(seed=1, num_players=4), BuildSettlement(20))
    assert state.vertex_owner[20] == 0
    assert state.current_player == 0
    assert state.pending_road_vertex == 20
    assert legal_actions(state)
    assert all(isinstance(a, BuildRoad) for a in legal_actions(state))


def test_placing_the_road_records_it_and_passes_to_the_next_seat() -> None:
    state = step(new_game(seed=1, num_players=4), BuildSettlement(20))
    road = first_road(state)
    state = step(state, road)
    assert state.road_owner[road.edge] == 0
    assert state.current_player == 1
    assert state.pending_road_vertex is None
    assert all(isinstance(a, BuildSettlement) for a in legal_actions(state))


@pytest.mark.parametrize(
    ("num_players", "order"),
    [(3, [0, 1, 2, 2, 1, 0]), (4, [0, 1, 2, 3, 3, 2, 1, 0])],
)
def test_setup_follows_the_snake_order(num_players: int, order: list[int]) -> None:
    # rules-spec 2: forward for the first pair, reverse for the second; the last seat
    # places both of its pairs back to back.
    state = new_game(seed=1, num_players=num_players)
    seen = []
    for _ in order:
        seen.append(state.current_player)
        state = place_pair(state)
    assert seen == order


@pytest.mark.parametrize("num_players", [3, 4])
def test_setup_ends_with_two_pairs_each_and_seat_0_to_roll(num_players: int) -> None:
    # rules-spec 2; ADR 0016: seat 0 starts the first turn.
    state = new_game(seed=1, num_players=num_players)
    for _ in range(2 * num_players):
        state = place_pair(state)
    assert state.phase is Phase.PRE_ROLL
    assert state.current_player == 0
    assert state.pending_road_vertex is None
    for seat in range(num_players):
        assert state.vertex_owner.count(seat) == 2
        assert state.road_owner.count(seat) == 2


def test_a_settlement_cannot_go_on_an_occupied_vertex() -> None:
    state = place_pair(new_game(seed=1, num_players=3))
    taken = state.vertex_owner.index(0)
    assert BuildSettlement(taken) not in legal_actions(state)
    with pytest.raises(IllegalActionError):
        step(state, BuildSettlement(taken))


def test_a_road_cannot_go_on_an_occupied_edge() -> None:
    state = place_pair(new_game(seed=1, num_players=3))
    taken = state.road_owner.index(0)
    state = step(state, first_settlement(state))
    assert BuildRoad(taken) not in legal_actions(state)
    with pytest.raises(IllegalActionError):
        step(state, BuildRoad(taken))


def test_step_rejects_the_wrong_kind_of_action() -> None:
    state = new_game(seed=1, num_players=3)
    with pytest.raises(IllegalActionError):
        step(state, BuildRoad(0))  # a settlement must come first
    with pytest.raises(IllegalActionError):
        step(state, RollDice())  # no rolling during setup
    state = step(state, BuildSettlement(20))
    with pytest.raises(IllegalActionError):
        step(state, BuildSettlement(40))  # the road must come first


def test_step_leaves_the_input_state_unchanged() -> None:
    # ADR 0002: copy-on-step.
    before = new_game(seed=1, num_players=3)
    snapshot = new_game(seed=1, num_players=3)
    step(before, BuildSettlement(20))
    assert before == snapshot


def test_a_settlement_cannot_go_next_to_another_players_settlement() -> None:
    # rules-spec 2: distance rule; no two settlements on the two ends of one edge.
    state = place_pair_at(new_game(seed=1, num_players=3), 20)
    for neighbour in t.VERTEX_VERTICES[20]:
        assert BuildSettlement(neighbour) not in legal_actions(state)
        with pytest.raises(IllegalActionError):
            step(state, BuildSettlement(neighbour))


def test_the_distance_rule_also_applies_to_your_own_settlements() -> None:
    # rules-spec 2: "including of one's own". Seat 2 of 3 places both pairs in a row.
    state = place_pair(place_pair(new_game(seed=1, num_players=3)))
    state = place_pair_at(state, 20)
    assert state.current_player == 2
    for neighbour in t.VERTEX_VERTICES[20]:
        assert BuildSettlement(neighbour) not in legal_actions(state)


def test_a_settlement_two_edges_away_is_allowed() -> None:
    state = place_pair_at(new_game(seed=1, num_players=3), 20)
    two_away = {w for n in t.VERTEX_VERTICES[20] for w in t.VERTEX_VERTICES[n]}
    two_away -= {20, *t.VERTEX_VERTICES[20]}
    assert two_away
    for v in two_away:
        assert BuildSettlement(v) in legal_actions(state)


def test_the_setup_road_must_touch_the_settlement_just_placed() -> None:
    # rules-spec 2: connection rule.
    state = step(new_game(seed=1, num_players=3), BuildSettlement(20))
    assert set(legal_actions(state)) == {BuildRoad(e) for e in t.VERTEX_EDGES[20]}
    far_edge = next(e for e in range(t.NUM_EDGES) if 20 not in t.EDGE_VERTICES[e])
    with pytest.raises(IllegalActionError):
        step(state, BuildRoad(far_edge))


def test_a_coastal_settlement_with_two_edges_offers_two_roads() -> None:
    state = step(new_game(seed=1, num_players=3), BuildSettlement(0))
    assert set(legal_actions(state)) == {BuildRoad(0), BuildRoad(1)}


def test_the_second_setup_road_cannot_attach_to_the_first_settlement() -> None:
    # rules-spec 2: in round 2 the road touches the second settlement only (ADR 0011).
    # Seat 2 of 3 places both pairs in a row, so its first settlement is right there.
    state = place_pair(place_pair(new_game(seed=1, num_players=3)))
    state = place_pair_at(state, 20)
    first_road_edge = state.road_owner.index(2)
    second = first_settlement(state)
    state = step(state, second)
    assert state.current_player == 2
    assert set(legal_actions(state)) == {
        BuildRoad(e) for e in t.VERTEX_EDGES[second.vertex] if state.road_owner[e] is None
    }
    for e in t.VERTEX_EDGES[20]:
        assert BuildRoad(e) not in legal_actions(state)
    for e in t.EDGE_EDGES[first_road_edge]:
        if second.vertex not in t.EDGE_VERTICES[e]:
            assert BuildRoad(e) not in legal_actions(state)


def test_the_first_settlement_grants_no_resources() -> None:
    # rules-spec 2: only the second settlement grants starting resources.
    state = new_game(seed=1, num_players=3, layout=Layout.BEGINNER)
    state = place_pair_at(state, 22)
    assert state.players[0].hand == ResourceCounts()


def test_the_second_settlement_grants_one_card_per_adjacent_hex() -> None:
    # rules-spec 2: one card per hex next to the second settlement. Beginner board:
    #   v41 fields, pasture, pasture  (same terrain twice gives two cards)
    #   v23 hills, forest, desert     (the desert gives nothing)
    #   v0  mountains only            (coastal vertex, one hex)
    state = new_game(seed=1, num_players=3, layout=Layout.BEGINNER)
    for vertex in (22, 2, 9):  # first settlements: seats 0, 1, 2
        state = place_pair_at(state, vertex)
    assert all(p.hand == ResourceCounts() for p in state.players)

    state = step(state, BuildSettlement(41))  # seat 2
    assert state.players[2].hand == ResourceCounts(grain=1, wool=2)  # on placement, before the road
    state = step(state, first_road(state))
    state = place_pair_at(state, 23)  # seat 1
    state = place_pair_at(state, 0)  # seat 0

    assert state.players[0].hand == ResourceCounts(ore=1)
    assert state.players[1].hand == ResourceCounts(brick=1, lumber=1)
    assert state.players[2].hand == ResourceCounts(grain=1, wool=2)
