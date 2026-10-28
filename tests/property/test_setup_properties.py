"""Setup phase invariants for any seed, 3 or 4 players (rules-spec 2)."""

from hypothesis import given
from hypothesis import strategies as st

from engine import topology as t
from engine.actions import Action, BuildRoad, BuildSettlement
from engine.game import IllegalActionError, legal_actions, new_game, step
from engine.state import GameState
from engine.types import Phase, ResourceCounts, terrain_resource

seeds = st.integers(min_value=0, max_value=2**64 - 1)
player_counts = st.sampled_from([3, 4])
BANK = ResourceCounts.uniform(19)  # rules-spec 1


def play_random_setup(data: st.DataObject, seed: int, num_players: int) -> list[Action]:
    """A random agent plays setup to the end; returns the actions it took."""
    state = new_game(seed=seed, num_players=num_players)
    actions: list[Action] = []
    while state.phase is Phase.SETUP:
        legal = legal_actions(state)
        assert legal, "setup must never get stuck"
        action = data.draw(st.sampled_from(legal))
        actions.append(action)
        state = step(state, action)
    return actions


def replay(seed: int, num_players: int, actions: list[Action]) -> GameState:
    state = new_game(seed=seed, num_players=num_players)
    for action in actions:
        state = step(state, action)
    return state


@given(st.data(), seeds, player_counts)
def test_a_random_agent_completes_setup_and_seat_0_rolls_first(
    data: st.DataObject, seed: int, num_players: int
) -> None:
    actions = play_random_setup(data, seed, num_players)
    assert len(actions) == 4 * num_players  # 2 pairs per seat
    state = replay(seed, num_players, actions)
    assert state.phase is Phase.PRE_ROLL
    assert state.current_player == 0  # ADR 0016


@given(st.data(), seeds, player_counts)
def test_after_setup_every_seat_has_two_settlements_and_two_roads(
    data: st.DataObject, seed: int, num_players: int
) -> None:
    state = replay(seed, num_players, play_random_setup(data, seed, num_players))
    for seat in range(num_players):
        assert state.vertex_owner.count(seat) == 2
        assert state.road_owner.count(seat) == 2


@given(st.data(), seeds, player_counts)
def test_after_setup_the_distance_and_connection_rules_hold(
    data: st.DataObject, seed: int, num_players: int
) -> None:
    state = replay(seed, num_players, play_random_setup(data, seed, num_players))
    owners = state.vertex_owner
    for v in range(t.NUM_VERTICES):
        if owners[v] is not None:
            assert all(owners[n] is None for n in t.VERTEX_VERTICES[v])
    for e in range(t.NUM_EDGES):
        if state.road_owner[e] is not None:
            assert any(owners[v] == state.road_owner[e] for v in t.EDGE_VERTICES[e])


@given(st.data(), seeds, player_counts)
def test_hands_hold_exactly_the_cards_from_each_second_settlement(
    data: st.DataObject, seed: int, num_players: int
) -> None:
    actions = play_random_setup(data, seed, num_players)
    state = replay(seed, num_players, actions)
    settlements = [a.vertex for a in actions if isinstance(a, BuildSettlement)]
    second_round = settlements[num_players:]  # seats N-1 .. 0
    for seat, vertex in zip(reversed(range(num_players)), second_round, strict=True):
        expected = ResourceCounts()
        for h in t.VERTEX_HEXES[vertex]:
            resource = terrain_resource(state.board.terrains[h])
            if resource is not None:
                expected = expected.add(resource)
        assert state.players[seat].hand == expected
    in_hands = sum((p.hand for p in state.players), ResourceCounts())
    assert all(n >= 0 for n in (BANK - in_hands).as_tuple())


@given(st.data(), seeds, player_counts)
def test_step_accepts_every_listed_action_and_rejects_unlisted_ones(
    data: st.DataObject, seed: int, num_players: int
) -> None:
    state = new_game(seed=seed, num_players=num_players)
    candidates: list[Action] = [BuildSettlement(v) for v in range(t.NUM_VERTICES)]
    candidates += [BuildRoad(e) for e in range(t.NUM_EDGES)]
    while state.phase is Phase.SETUP:
        legal = legal_actions(state)
        for action in legal:
            step(state, action)  # must not raise
        illegal = [a for a in candidates if a not in legal]
        rejected = data.draw(st.sampled_from(illegal))
        try:
            step(state, rejected)
        except IllegalActionError:
            pass
        else:
            raise AssertionError(f"{rejected!r} was accepted but not listed")
        state = step(state, data.draw(st.sampled_from(legal)))


@given(st.data(), seeds, player_counts)
def test_setup_is_deterministic(data: st.DataObject, seed: int, num_players: int) -> None:
    actions = play_random_setup(data, seed, num_players)
    assert replay(seed, num_players, actions) == replay(seed, num_players, actions)
