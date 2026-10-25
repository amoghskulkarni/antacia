import dataclasses
import inspect
import typing

import pytest

from engine import actions
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
from engine.types import Offer, Resource, ResourceCounts

OFFER = Offer(give=ResourceCounts(brick=1), want=ResourceCounts(ore=1))

# One example instance per action kind.
EXAMPLES: list[Action] = [
    RollDice(),
    EndTurn(),
    BuildRoad(edge=3),
    BuildSettlement(vertex=7),
    BuildCity(vertex=7),
    BuyDevCard(),
    DiscardOne(resource=Resource.WOOL),
    MoveRobber(hex=4, victim=2),
    PlayKnight(),
    PlayRoadBuilding(),
    PlayYearOfPlenty(first=Resource.GRAIN, second=Resource.ORE),
    PlayMonopoly(resource=Resource.BRICK),
    BankTrade(give=Resource.LUMBER, get=Resource.ORE),
    ProposeTrade(offer=OFFER),
    AcceptTrade(),
    RejectTrade(),
    CounterTrade(offer=OFFER),
    ConfirmTrade(responder=1),
    CancelTrade(),
]


def _union_members() -> set[type]:
    return set(typing.get_args(Action.__value__))


def _dataclasses_in_actions_module() -> set[type]:
    return {
        obj
        for _, obj in inspect.getmembers(actions, inspect.isclass)
        if obj.__module__ == actions.__name__ and dataclasses.is_dataclass(obj)
    }


def test_action_union_lists_every_action_class() -> None:
    # Forgetting to add a new action kind to `Action` would hide it from type checks.
    assert _union_members() == _dataclasses_in_actions_module()


def test_examples_cover_every_action_kind() -> None:
    assert {type(a) for a in EXAMPLES} == _union_members()


@pytest.mark.parametrize("action", EXAMPLES, ids=lambda a: type(a).__name__)
def test_action_is_frozen(action: Action) -> None:
    params = type(action).__dataclass_params__  # type: ignore[attr-defined]
    assert params.frozen
    assert hasattr(type(action), "__slots__")
    fields = dataclasses.fields(action)
    if fields:
        with pytest.raises(dataclasses.FrozenInstanceError):
            setattr(action, fields[0].name, None)


@pytest.mark.parametrize("action", EXAMPLES, ids=lambda a: type(a).__name__)
def test_action_has_value_equality_and_hash(action: Action) -> None:
    # Replays and the no-repeat trade rule compare actions by value.
    twin = dataclasses.replace(action)
    assert twin == action
    assert hash(twin) == hash(action)


def test_offers_compare_by_value() -> None:
    same = Offer(give=ResourceCounts(brick=1), want=ResourceCounts(ore=1))
    other = Offer(give=ResourceCounts(brick=1), want=ResourceCounts(wool=1))
    assert same == OFFER and hash(same) == hash(OFFER)
    assert other != OFFER


def test_resource_counts_default_to_zero_in_resource_order() -> None:
    counts = ResourceCounts(ore=2, wool=1)
    assert counts.as_tuple() == (0, 0, 2, 0, 1)
    assert [r.name for r in Resource] == ["BRICK", "LUMBER", "ORE", "GRAIN", "WOOL"]


def test_move_robber_victim_is_optional() -> None:
    # No adjacent opponent to steal from -> victim is None.
    assert MoveRobber(hex=0, victim=None).victim is None
