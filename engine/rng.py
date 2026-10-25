"""Seeded randomness for chance events (dice, dev-card draws, steals, layout).

SplitMix64 (ADR 0010). The RNG state is one 64-bit integer that lives inside
GameState and is threaded through pure functions: each call takes an `Rng`
and returns the value together with the next `Rng`. Nothing here is global,
so (seed, actions) fully determines a game (ADR 0002).

Every operation is masked to 64 bits so the Rust port (wrapping u64 arithmetic)
produces identical sequences. Only the functions in this module may draw
randomness; the algorithms below are part of the replay format.
"""

from dataclasses import dataclass

_MASK64 = 0xFFFF_FFFF_FFFF_FFFF
_GAMMA = 0x9E37_79B9_7F4A_7C15
_MIX1 = 0xBF58_476D_1CE4_E5B9
_MIX2 = 0x94D0_49BB_1331_11EB
_TWO64 = 1 << 64


@dataclass(frozen=True, slots=True)
class Rng:
    """SplitMix64 state, 0 <= state < 2**64. Never part of any observation."""

    state: int


def seed_rng(seed: int) -> Rng:
    """Reduce any Python int to a 64-bit seed (two's complement for negatives)."""
    return Rng(state=seed & _MASK64)


def next_u64(rng: Rng) -> tuple[int, Rng]:
    """One SplitMix64 step: advance the state by the golden gamma, then mix it."""
    state = (rng.state + _GAMMA) & _MASK64
    z = state
    z = ((z ^ (z >> 30)) * _MIX1) & _MASK64
    z = ((z ^ (z >> 27)) * _MIX2) & _MASK64
    return z ^ (z >> 31), Rng(state=state)


def randbelow(rng: Rng, n: int) -> tuple[int, Rng]:
    """Unbiased integer in [0, n), for 1 <= n <= 2**64.

    Rejection sampling: draws below `limit` (the largest multiple of n that fits
    in 64 bits) map evenly onto [0, n) with `% n`; draws at or above it are
    discarded and redrawn. Always consumes at least one draw, even for n == 1.
    """
    if not 1 <= n <= _TWO64:
        raise ValueError(f"randbelow bound must be in [1, 2**64], got {n}")
    limit = _TWO64 - (_TWO64 % n)
    while True:
        value, rng = next_u64(rng)
        if value < limit:
            return value % n, rng


def shuffle[T](rng: Rng, items: tuple[T, ...]) -> tuple[tuple[T, ...], Rng]:
    """Fisher-Yates, from the last index down: for i = len-1 .. 1, swap i with randbelow(i+1)."""
    out = list(items)
    for i in range(len(out) - 1, 0, -1):
        j, rng = randbelow(rng, i + 1)
        out[i], out[j] = out[j], out[i]
    return tuple(out), rng


def roll_dice(rng: Rng) -> tuple[tuple[int, int], Rng]:
    """Two separate d6 draws (not one draw over 2..12)."""
    first, rng = randbelow(rng, 6)
    second, rng = randbelow(rng, 6)
    return (first + 1, second + 1), rng
