# Decision index

One ADR per decision that is costly to reverse or likely to be questioned. Open only the one you need. Never delete an ADR; supersede it with a new one and update its status.

| #    | Title                                          | Status   | One-line summary                                                                 |
| ---- | ---------------------------------------------- | -------- | -------------------------------------------------------------------------------- |
| 0001 | Python engine first, Rust port later           | Accepted | Python is the reference engine; port to a PyO3 crate validated by golden replays |
| 0002 | Immutable copy-on-step game state              | Accepted | `step()` returns a new state; revisit if steps/sec is too low                    |
| 0003 | Turn-synchronous trading                       | Accepted | Active player only; real-time negotiation is a server concern                    |
| 0004 | Pydantic at the boundaries only                | Proposed | Frozen dataclasses in the engine; Pydantic for APIs, config, logs                |
| 0005 | Flat action list with a bounded trade subset   | Accepted | Fixed enumerated ids plus masks; engine accepts any valid offer                  |
| 0006 | Structured observation with a flatten function | Proposed | MLP now, GNN-ready later                                                         |
| 0007 | Hex coordinate system                          | Accepted | Pointy-top axial hexes; vertices `(q,r,N/S)`, edges `(q,r,NE/NW/W)`              |
| 0008 | Dense board ids and topology tables            | Accepted | Row-major int ids; topology precomputed as immutable tuples; layout separate     |
| 0009 | Board layout generation and harbors            | Accepted | Beginner or random; official spiral tokens; shuffled harbor types               |
| 0010 | Seeded RNG for chance events                   | Accepted | SplitMix64 state in `GameState`; dev cards drawn on demand; never observed      |
| 0011 | Setup placements reuse the build actions       | Accepted | `BuildSettlement`/`BuildRoad` in setup; the phase decides cost and legality      |
| 0012 | Robber move and steal as one action            | Accepted | `MoveRobber(hex, victim)`; victim `None` only if nobody can be robbed            |
| 0013 | Discards after a 7, one card per action        | Accepted | `DiscardOne(resource)` repeated until the player has discarded enough            |
| 0014 | Trade offers are broadcast (no targeted offers)| Accepted | `Offer(give, want)` goes to all opponents; audience comes with the chat layer    |
| 0015 | Board symmetries and harbor frames             | Accepted | All 12 rotations/mirrors are legal boards; 2 harbor frames; exact x12 augmentation |
| 0016 | Seat 0 always starts                           | Accepted | Engine starts with seat 0; server/eval/env shuffle seats every game              |

## ADR Template

```markdown
# NNNN: Title

Status: Proposed | Accepted | Superseded by NNNN (date)

## Context

## Decision

## Options considered

## Consequences

## Revisit when
```
