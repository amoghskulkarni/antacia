import dataclasses

import engine
from engine.state import GameState
from engine.types import DevCard, Resource, Terrain


def test_public_api_is_exported() -> None:
    for name in ("step", "legal_actions", "is_terminal", "winner", "GameState", "Action"):
        assert hasattr(engine, name), name


def test_enum_values_are_stable() -> None:
    # These ids are part of the observation/action encoding and golden replays.
    assert [r.value for r in Resource] == [0, 1, 2, 3, 4]
    assert [t.value for t in Terrain] == [0, 1, 2, 3, 4, 5]
    assert [d.value for d in DevCard] == [0, 1, 2, 3, 4]


def test_game_state_is_frozen_and_slotted() -> None:
    # ADR 0002. GameState has no fields yet, so assigning to one can't tell frozen from
    # merely slotted (both raise). Check the dataclass params; once fields exist, replace
    # this with an assignment that must raise FrozenInstanceError.
    assert dataclasses.is_dataclass(GameState)
    assert GameState.__dataclass_params__.frozen  # type: ignore[attr-defined]
    assert hasattr(GameState, "__slots__")
