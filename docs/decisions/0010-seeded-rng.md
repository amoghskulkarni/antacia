# 0010: Seeded RNG for chance events

Status: Proposed (2026-10-25). Review and mark Accepted or revise.

## Context
Chance enters through board generation, dice rolls, dev-card draws and robber steals. The engine must be deterministic given `(seed, actions)` (ADR 0002), carry its RNG inside the immutable `GameState` (copied on every step), and be reproducible bit-for-bit in Rust (ADR 0001). Search bots (ISMCTS, Phase 5) branch from states and must not be able to "see" future chance outcomes.

## Decision (recommended)
- **Generator: SplitMix64**, with the state as one 64-bit integer stored in `GameState`. Each draw adds a constant and runs a fixed mixing function. In Python every operation is masked with `& 0xFFFF_FFFF_FFFF_FFFF`; in Rust it uses `wrapping_add`/`wrapping_mul`.
- **Pure interface:** `next_u64(rng) -> (value, rng)`, plus helpers built only on it:
  - `randbelow(rng, n)`: unbiased integer in `[0, n)` by rejection sampling, with the exact algorithm written down in `rng.py` so Rust matches it.
  - `shuffle(rng, items)`: Fisher-Yates in a documented direction (from the last index down).
  - Dice are two separate `randbelow(rng, 6) + 1` draws, not one draw over 2..12.
- **Dev cards are drawn on demand:** each draw picks uniformly from the remaining deck counts, instead of shuffling a deck order at game start. The distribution is the same, but the state never contains a hidden predetermined order, which keeps determinisation for search simple.
- **The RNG state is never part of any observation.** Search bots must re-seed or determinise before simulating; this goes into the bot interface docs.
- **Seed input:** a Python `int` reduced to 64 bits; the replay log stores it.

## Options considered
- **SplitMix64 (recommended):** 64-bit state, a few lines of code, statistically good enough for games (passes BigCrush), trivially ported, cheap to copy.
- **PCG32:** better-studied quality, also a 64-bit state, slightly more code. A fine alternative if SplitMix64 ever proves weak.
- **xoshiro256\*\*:** excellent quality, but a 256-bit state (four ints to copy each step) for no practical gain here.
- **Python `random.Random` (Mersenne Twister):** in the stdlib, but about 2.5 KB of state to copy on every step, and `randrange`/`shuffle` internals would have to be re-implemented exactly in Rust.
- **NumPy `Generator`:** a new dependency, mutable objects, and also hard to match in Rust.
- **Separate streams per purpose** (dice, steals, cards): keeps dice sequences stable when unrelated rules change, but adds complexity; golden replays pin behaviour anyway.

## Consequences
- Good: tiny state, pure functions, exact Rust parity, easy property tests (same seed gives the same sequence; `randbelow` is within range and roughly uniform).
- Bad: one shared stream means any rule change that adds or removes a draw shifts all later outcomes, so golden replays must be regenerated on rule changes (expected anyway). Not cryptographically secure; for online play the server can choose seeds secretly.

## Revisit when
Statistical tests show bias, a per-purpose stream becomes useful (e.g. for variance-reduced evaluation with shared dice), or online play needs stronger guarantees against seed prediction.
