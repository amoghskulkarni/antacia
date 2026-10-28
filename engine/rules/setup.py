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
from engine.state import GameState
from engine.types import Phase, PlayerId


def snake_seat(turn: int, num_players: int) -> PlayerId:
    """The seat that places setup pair number `turn` (0 .. 2N-1)."""
    return turn if turn < num_players else 2 * num_players - 1 - turn


def setup_actions(state: GameState) -> tuple[Action, ...]:
    """Legal setup placements, in id order."""
    if state.pending_road_vertex is None:
        return tuple(
            BuildSettlement(v) for v in range(t.NUM_VERTICES) if _distance_rule_ok(state, v)
        )
    return tuple(BuildRoad(e) for e in range(t.NUM_EDGES) if state.road_owner[e] is None)


def apply_setup_action(state: GameState, action: Action) -> GameState:
    """Apply a placement that `setup_actions` listed."""
    seat = state.current_player
    match action:
        case BuildSettlement(vertex=v):
            return replace(
                state,
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


def _distance_rule_ok(state: GameState, vertex: int) -> bool:
    """The vertex and all its neighbours are free of settlements (any owner, own included).

    Normal building (rules-spec 5) needs this too; move it to engine/ when it does.
    """
    owners = state.vertex_owner
    return owners[vertex] is None and all(owners[n] is None for n in t.VERTEX_VERTICES[vertex])


def _replace_at[T](items: tuple[T, ...], index: int, value: T) -> tuple[T, ...]:
    return items[:index] + (value,) + items[index + 1 :]
