# 0009: Board layout generation and harbors

Status: Accepted (2026-10-25). Token spiral and harbor rules verified against the rulebook.

## Context
Each game needs a layout: a terrain per hex, a number token per non-desert hex, a harbor type per harbor slot, and the robber's start. The rulebook gives a fixed beginner layout and a variable setup. Training wants many varied boards; humans may want the familiar beginner board; replays need every layout to be reproducible from the seed.

## Decision
- **Config option `layout: "beginner" | "random"`, default `random`.** `beginner` is the rulebook's fixed starting board, stored as data.
- **Random terrains:** shuffle the 19 terrain tiles over the 19 hexes with the seeded RNG (ADR 0010).
- **Number tokens, official method (verified):** place the tokens in the rulebook's lettered order A-R (5, 2, 6, 3, 8, 10, 9, 12, 11, 4, 8, 10, 9, 4, 5, 6, 3, 11) along a counterclockwise spiral from a randomly chosen outer corner hex towards the centre, skipping the desert. Property tests check that red numbers (6, 8) never end up on adjacent hexes.
- **Harbors (verified): 9 fixed coastal slots, each slot one coastal edge (its two vertices get the harbor); random mode shuffles the 9 harbor tiles (4 generic 3:1, one 2:1 per resource) over the slots.** The slot edges are data in `engine/topology.py` (`HARBOR_FRAMES[0]`, verified with `render_topology()`). Slot numbering, the second harbor frame and board symmetries: ADR 0015.
- **The robber starts on the desert.**
- **Generation is a pure function `generate_board(layout, rng) -> (Board, rng)`.** Its RNG draws come first in every game, in a fixed order (terrains, start corner, harbors), so the seed alone fixes the board. `beginner` draws nothing.
- The whole layout is public and part of every observation.

## Options considered
- **Official spiral tokens (chosen):** rule-faithful and avoids adjacent red numbers by design. Less variety: only 6 token arrangements (one per start corner) per terrain layout.
- **Fully random tokens with a "no adjacent 6/8" constraint** (resample or swap until valid): the most variety and common in online apps, but not the rulebook's procedure, and resampling makes RNG consumption variable.
- **Fully random tokens, no constraint:** maximum variety, but produces boards the rulebook avoids.
- **Fixed harbors vs shuffled:** fixed is simpler; shuffling harbor types adds variety and is what the variable setup prescribes.

## Consequences
- Good: rule-faithful by default; one seed fully determines a board; the beginner board gives a stable target for tests and the ASCII printer.
- Bad: the spiral method needs the official letter order and spiral path as data, and both must be checked carefully. If we later want "fair board" generators (balancing pips per resource), that's a new option, not a replacement.

## Revisit when
Training shows overfitting to the limited token arrangements, or players ask for balanced or custom boards.
