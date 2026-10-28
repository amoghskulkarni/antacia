"""Setup phase: initial settlement and road placement, starting resources.

Rules: docs/rules-spec.md section 2. Placements use the normal build actions
and are free in this phase (ADR 0011).

Each setup turn places one settlement, then one road. Turns follow the snake
order: seats 0..N-1, then N-1..0. The setup round is never stored; it is the
number of settlements on the board, because every turn places exactly one.
"""

from dataclasses import replace

from engine import topology as t
from engine.actions import Action, BuildRoad, BuildSettlement
from engine.state import GameState, PlayerState
from engine.types import Phase, PlayerId, terrain_resource


def snake_seat(turn: int, num_players: int) -> PlayerId:
    """The seat that places setup pair number `turn` (0 .. 2N-1)."""
    return turn if turn < num_players else 2 * num_players - 1 - turn


def setup_actions(state: GameState) -> tuple[Action, ...]:
    """Legal setup placements, in id order."""
    if state.pending_road_vertex is None:
        return tuple(
            BuildSettlement(v) for v in range(t.NUM_VERTICES) if _distance_rule_ok(state, v)
        )
    # Connection rule: the road touches the settlement just placed, not any other piece.
    edges = t.VERTEX_EDGES[state.pending_road_vertex]
    return tuple(BuildRoad(e) for e in edges if state.road_owner[e] is None)


def apply_setup_action(state: GameState, action: Action) -> GameState:
    """Apply a placement that `setup_actions` listed."""
    seat = state.current_player
    match action:
        case BuildSettlement(vertex=v):
            turn = t.NUM_VERTICES - state.vertex_owner.count(None)
            players = state.players
            if turn >= len(players):  # second round: this is the seat's second settlement
                players = _replace_at(
                    players, seat, _with_starting_resources(players[seat], state, v)
                )
            return replace(
                state,
                players=players,
                vertex_owner=_replace_at(state.vertex_owner, v, seat),
                pending_road_vertex=v,
            )
        case BuildRoad(edge=e):
            state = replace(
                state,
                road_owner=_replace_at(state.road_owner, e, seat),
                pending_road_vertex=None,
            )
            turns_done = t.NUM_VERTICES - state.vertex_owner.count(None)
            num_players = len(state.players)
            if turns_done == 2 * num_players:
                return replace(state, phase=Phase.PRE_ROLL, current_player=0)
            return replace(state, current_player=snake_seat(turns_done, num_players))
        case _:
            raise AssertionError(f"not a setup action: {action!r}")


def _with_starting_resources(player: PlayerState, state: GameState, vertex: int) -> PlayerState:
    """One card per hex next to `vertex`; the desert gives nothing.

    The bank can't run short here: at most 3 cards per seat, 12 per resource < 19.
    """
    hand = player.hand
    for h in t.VERTEX_HEXES[vertex]:
        resource = terrain_resource(state.board.terrains[h])
        if resource is not None:
            hand = hand.add(resource)
    return replace(player, hand=hand)


def _distance_rule_ok(state: GameState, vertex: int) -> bool:
    """The vertex and all its neighbours are free of settlements (any owner, own included).

    Normal building (rules-spec 5) needs this too; move it to engine/ when it does.
    """
    owners = state.vertex_owner
    return owners[vertex] is None and all(owners[n] is None for n in t.VERTEX_VERTICES[vertex])


def _replace_at[T](items: tuple[T, ...], index: int, value: T) -> tuple[T, ...]:
    return items[:index] + (value,) + items[index + 1 :]
