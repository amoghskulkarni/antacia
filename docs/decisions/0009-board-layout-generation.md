# 0009: Board layout generation and harbors

Status: Proposed (2026-10-25). Review and mark Accepted or revise. Items marked VERIFY need checking against the rulebook and recording in `docs/rules-spec.md` sections 1-2.

## Context
Each game needs a layout: a terrain per hex, a number token per non-desert hex, a harbor type per harbor slot, and the robber's start. The rulebook gives a fixed beginner layout and a variable setup. Training wants many varied boards; humans may want the familiar beginner board; replays need every layout to be reproducible from the seed.

## Decision (recommended)
- **Config option `layout: "beginner" | "random"`, default `random`.** `beginner` is the rulebook's fixed starting board, stored as data.
- **Random terrains:** shuffle the 19 terrain tiles over the 19 hexes with the seeded RNG (ADR 0010).
- **Number tokens, official method (VERIFY):** place the tokens in the rulebook's fixed lettered order (A-R) along a spiral, starting from a randomly chosen corner and skipping the desert. This method keeps the red numbers (6, 8) off adjacent hexes without any resampling.
- **Harbors: 9 fixed coastal slots, each slot a pair of adjacent coastal vertices (VERIFY slot positions); random mode shuffles the 9 harbor types over the slots.**
- **The robber starts on the desert.**
- **Generation is a pure function `generate_board(config, rng) -> (Board, rng)`.** Its RNG draws come first in every game, so the seed alone fixes the board.
- The whole layout is public and part of every observation.

## Options considered
- **Official spiral tokens (recommended):** rule-faithful and avoids adjacent red numbers by design. Less variety: only 6 start corners × 2 directions (VERIFY) of token arrangement per terrain layout.
- **Fully random tokens with a "no adjacent 6/8" constraint** (resample or swap until valid): the most variety and common in online apps, but not the rulebook's procedure, and resampling makes RNG consumption variable.
- **Fully random tokens, no constraint:** maximum variety, but produces boards the rulebook avoids.
- **Fixed harbors vs shuffled:** fixed is simpler; shuffling harbor types adds variety and is allowed by the variable setup (VERIFY).

## Consequences
- Good: rule-faithful by default; one seed fully determines a board; the beginner board gives a stable target for tests and the ASCII printer.
- Bad: the spiral method needs the official letter order and spiral path as data, and both must be checked carefully. If we later want "fair board" generators (balancing pips per resource), that's a new option, not a replacement.

## Revisit when
Training shows overfitting to the limited token arrangements, or players ask for balanced or custom boards.
