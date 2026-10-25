"""Seeded randomness for chance events (dice, dev-card draws, steals, layout).

The RNG state lives inside GameState and is advanced by `step`, never held in
a global, so that (seed, actions) fully determines a game (ADR 0002).

Planned shape: a pure function `next(rng_state) -> (value, new_rng_state)`.
"""

# TODO: implement once ADR 0010 (generator choice) is Accepted.
