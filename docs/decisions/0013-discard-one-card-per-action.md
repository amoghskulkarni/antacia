# 0013: Discards after a 7, one card per action

Status: Accepted (2026-10-25)

## Context
When a 7 is rolled, each player with more than the hand limit must discard half their cards (rounded down; exact rule in `docs/rules-spec.md` section 4). At the table this happens all at once. The engine is single-actor (one actor at a time), and the RL action list must be a fixed, enumerable set (ADR 0005).

## Decision
`DiscardOne(resource)` discards a single card. A player who owes discards acts repeatedly until they have discarded enough, then the next owing player acts. The engine tracks how many cards each player still owes. The order in which players discard is a rules-spec decision (section 4), not part of this ADR.

## Options considered
- **One card per action (chosen):** 5 action ids; legality is just "you hold this resource and still owe a discard".
- **Whole discard at once, `Discard(cards: ResourceCounts)`:** one action per player, closer to table play, but the RL list would need every possible combination of cards (hundreds of ids for large hands), most of them illegal in any given state.
- **Engine accepts both:** flexible, but two encodings of the same thing make replays and legality harder to keep consistent.

## Consequences
- Good: tiny, fixed action set; easy masks; every intermediate state is valid.
- Bad: longer episodes after a 7 (up to about 10 extra steps for a big hand), which slightly dilutes RL credit assignment. Opponents see the discard one card at a time in the log, which reveals no more than the whole discard would.
- The server/UI can let a human select all cards at once and send them as a sequence of `DiscardOne`.

## Revisit when
- Phase 5 profiling or training shows discard sequences hurt learning or throughput.
- Factored action heads arrive (a "discard vector" head becomes practical).
- Simultaneous discards matter for real-time play (a server concern, which would still feed the engine ordered `DiscardOne`s).
