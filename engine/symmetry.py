"""Board symmetries applied to game data (ADR 0015).

The 12 symmetries (6 rotations, 6 mirror images; tables in engine/topology.py)
relabel hexes, vertices and edges without changing any adjacency, so a game on
a transformed board, with transformed actions, is the same game. That turns one
recorded game into 12 equivalent training games:

    for s in range(NUM_SYMMETRIES):
        board_s = transform_board(board, s)
        actions_s = [transform_action(a, s) for a in actions]

Only board locations move. Players, resources, dice and cards never do.
GameState and observation transforms follow when those types exist (Week 2, 6).
"""

from typing import assert_never

from engine import topology as t
from engine.actions import (
    AcceptTrade,
    Action,
    BankTrade,
    BuildCity,
    BuildRoad,
    BuildSettlement,
    BuyDevCard,
    CancelTrade,
    ConfirmTrade,
    CounterTrade,
    DiscardOne,
    EndTurn,
    MoveRobber,
    PlayKnight,
    PlayMonopoly,
    PlayRoadBuilding,
    PlayYearOfPlenty,
    ProposeTrade,
    RejectTrade,
    RollDice,
)
from engine.board import Board
from engine.types import Harbor, Terrain


def transform_board(board: Board, s: int) -> Board:
    """The same board seen under symmetry `s`: hex h's tile moves to HEX_SYMMETRIES[s][h].

    Raises ValueError unless `s` is an int in 0..11.
    """
    hexes = t.HEX_SYMMETRIES[t.check_symmetry(s)]
    terrains: list[Terrain] = [Terrain.DESERT] * t.NUM_HEXES
    tokens: list[int | None] = [None] * t.NUM_HEXES
    for h in range(t.NUM_HEXES):
        terrains[hexes[h]] = board.terrains[h]
        tokens[hexes[h]] = board.tokens[h]

    # A symmetry maps the whole harbor frame onto one frame (maybe the other one)
    # and permutes its slots.
    harbors: list[Harbor] = list(board.harbors)
    frames = set()
    for i, edge in enumerate(t.HARBOR_FRAMES[board.frame]):
        frame, slot = t.HARBOR_SLOT_OF_EDGE[t.EDGE_SYMMETRIES[s][edge]]
        frames.add(frame)
        harbors[slot] = board.harbors[i]
    (frame,) = frames
    return Board(tuple(terrains), tuple(tokens), tuple(harbors), frame=frame)


def transform_action(action: Action, s: int) -> Action:
    """The same action under symmetry `s`: board locations move, everything else stays.

    Raises ValueError unless `s` is an int in 0..11, even for actions no symmetry changes.
    """
    t.check_symmetry(s)
    match action:
        case BuildRoad(edge=e):
            return BuildRoad(edge=t.EDGE_SYMMETRIES[s][e])
        case BuildSettlement(vertex=v):
            return BuildSettlement(vertex=t.VERTEX_SYMMETRIES[s][v])
        case BuildCity(vertex=v):
            return BuildCity(vertex=t.VERTEX_SYMMETRIES[s][v])
        case MoveRobber(hex=h, victim=victim):
            return MoveRobber(hex=t.HEX_SYMMETRIES[s][h], victim=victim)
        case (
            RollDice()
            | EndTurn()
            | BuyDevCard()
            | DiscardOne()
            | PlayKnight()
            | PlayRoadBuilding()
            | PlayYearOfPlenty()
            | PlayMonopoly()
            | BankTrade()
            | ProposeTrade()
            | AcceptTrade()
            | RejectTrade()
            | CounterTrade()
            | ConfirmTrade()
            | CancelTrade()
        ):
            return action
        case _:
            assert_never(action)
