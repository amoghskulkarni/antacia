from hypothesis import given
from hypothesis import strategies as st

from engine.rng import next_u64, randbelow, seed_rng, shuffle

seeds = st.integers(min_value=0, max_value=2**64 - 1)


@given(seeds)
def test_same_seed_same_sequence(seed: int) -> None:
    a, b = seed_rng(seed), seed_rng(seed)
    for _ in range(5):
        x, a = next_u64(a)
        y, b = next_u64(b)
        assert x == y


@given(seeds)
def test_next_u64_is_a_64_bit_value(seed: int) -> None:
    value, rng = next_u64(seed_rng(seed))
    assert 0 <= value < 2**64
    assert 0 <= rng.state < 2**64


@given(seeds, st.integers(min_value=1, max_value=2**64))
def test_randbelow_is_in_range(seed: int, n: int) -> None:
    value, _ = randbelow(seed_rng(seed), n)
    assert 0 <= value < n


@given(seeds, st.lists(st.integers(), max_size=30))
def test_shuffle_is_a_permutation(seed: int, items: list[int]) -> None:
    shuffled, _ = shuffle(seed_rng(seed), tuple(items))
    assert sorted(shuffled) == sorted(items)
