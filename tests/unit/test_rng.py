import dataclasses

import pytest

from engine.rng import Rng, next_u64, randbelow, roll_dice, seed_rng, shuffle

# Reference SplitMix64 outputs (Vigna's splitmix64.c) for seed 1234567.
# The Rust port must produce the same sequence.
REFERENCE_SEED = 1234567
REFERENCE_OUTPUTS = [
    6457827717110365317,
    3203168211198807973,
    9817491932198370423,
    4593380528125082431,
    16408922859458223821,
]


def test_next_u64_matches_reference_splitmix64() -> None:
    rng = seed_rng(REFERENCE_SEED)
    outputs = []
    for _ in REFERENCE_OUTPUTS:
        value, rng = next_u64(rng)
        outputs.append(value)
    assert outputs == REFERENCE_OUTPUTS


def test_next_u64_does_not_change_its_input() -> None:
    rng = seed_rng(1)
    first, _ = next_u64(rng)
    again, _ = next_u64(rng)
    assert first == again


def test_rng_is_frozen() -> None:
    rng = seed_rng(1)
    with pytest.raises(dataclasses.FrozenInstanceError):
        rng.state = 2  # type: ignore[misc]


def test_seed_is_reduced_to_64_bits() -> None:
    assert seed_rng(2**64 + 5) == seed_rng(5)
    assert seed_rng(-1) == Rng(state=2**64 - 1)


def test_randbelow_rejects_non_positive_bound() -> None:
    with pytest.raises(ValueError):
        randbelow(seed_rng(1), 0)


def test_randbelow_one_is_always_zero_but_still_advances() -> None:
    rng = seed_rng(1)
    value, after = randbelow(rng, 1)
    assert value == 0
    assert after != rng


def test_shuffle_of_empty_and_single_draws_nothing() -> None:
    rng = seed_rng(1)
    assert shuffle(rng, ()) == ((), rng)
    assert shuffle(rng, ("a",)) == (("a",), rng)


def test_roll_dice_is_two_separate_d6_draws() -> None:
    rng = seed_rng(42)
    (d1, d2), after = roll_dice(rng)
    first, mid = randbelow(rng, 6)
    second, end = randbelow(mid, 6)
    assert (d1, d2) == (first + 1, second + 1)
    assert after == end


def test_dice_frequencies_are_roughly_uniform() -> None:
    rng = seed_rng(7)
    counts = [0] * 6
    for _ in range(6000):
        (d1, _d2), rng = roll_dice(rng)
        counts[d1 - 1] += 1
    # Expected 1000 each; a 5-sigma band is about +-200.
    assert all(800 < c < 1200 for c in counts), counts
