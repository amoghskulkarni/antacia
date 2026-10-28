import engine
from engine.types import DevCard, Phase, Resource, Terrain


def test_public_api_is_exported() -> None:
    for name in (
        "new_game",
        "step",
        "legal_actions",
        "is_terminal",
        "winner",
        "GameState",
        "Action",
    ):
        assert hasattr(engine, name), name


def test_enum_values_are_stable() -> None:
    # These ids are part of the observation/action encoding and golden replays.
    assert [r.value for r in Resource] == [0, 1, 2, 3, 4]
    assert [t.value for t in Terrain] == [0, 1, 2, 3, 4, 5]
    assert [d.value for d in DevCard] == [0, 1, 2, 3, 4]
    assert [p.value for p in Phase] == [0, 1]
