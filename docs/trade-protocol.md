# Trade protocol (v1: turn-synchronous)

Spec for player-to-player ("domestic") trading in the engine. Referenced from `CLAUDE.md`. Items marked VERIFY are my recollection of the official rules and must be checked against the rulebook; record the outcome in `rules-spec.md` section 8.

## 1. Principles
- Only the **active player** may start a trade, and only during their own turn. Other players may only respond to it (official rule, per project decision).
- The engine is a strict state machine with **one actor at a time**. Same seed + same action list always gives the same game.
- **Open-ended offers** are legal in the engine. The RL agent uses a bounded subset (section 7).
- Chat/table talk is **not** part of the rules engine. It maps to and from the protocol messages here (section 9).
- Domestic trades are separate from **bank/harbor trades** (4:1, 3:1, 2:1), which are single-actor actions (`BankTrade`) and don't use this protocol.

## 2. Vocabulary
- `Offer(proposer, give, want)`: `proposer` gives the resources in `give` and receives those in `want`. `give` and `want` are resource-count vectors over the 5 resources.
- Valid offer (VERIFY against rulebook):
  - `give` and `want` are both non-empty (no gifts, no empty asks),
  - the two sides share **no resource type** (no swapping like for like),
  - `proposer` holds everything in `give`.
- **Active player** = the player whose turn it is. **Responders** = the other players, in seat order starting with the player to the active player's left.

## 3. When trading is allowed
- Only in the main phase of the active player's turn, **after the dice roll and any 7 resolution (robber/discard) is finished**, and never during setup (VERIFY).
- It may be interleaved with building and playing a development card in any order, but only while no trade is open.
- While a trade is open, **no other action is legal** for anyone. Hands therefore cannot change between a response and the active player's decision (key invariant, see section 8).

## 4. State machine

```
MAIN ──ProposeTrade──► RESPONDING ──(all responders done)──► DECIDING
 ▲                          │                                   │
 │                          └── each responder acts in seat     │
 │                              order: Accept | Reject |        │
 │                              Counter                         │
 │                                                              │
 ├────────── ConfirmTrade(j) (executes swap) ◄──────────────────┤
 ├────────── CancelTrade ◄──────────────────────────────────────┤
 └──────────────── ProposeTrade (new round) ───► RESPONDING ◄───┘
```

### MAIN (no trade open)
Legal for the active player, in addition to the usual build/dev-card/bank/end-turn actions:
- `ProposeTrade(offer)` if the offer is valid and the per-turn limits in section 6 allow it.

### RESPONDING
The engine asks each responder in seat order, one at a time. Each responder's legal actions:
- `Reject`: always legal.
- `Accept`: legal only if the responder holds everything in `offer.want`.
- `Counter(offer')`: legal if `offer'` is a valid offer with `proposer` = the responder, it is **not identical** to the current offer (mirrored), and the responder holds `offer'.give`.

A responder who cannot accept or counter (for example an empty hand) has only `Reject`. Environments may auto-step such forced moves (section 7).

Responses are **sequential and public**: later responders see earlier responses. This matches table play and keeps the engine single-actor. A counter is visible to everyone, but only the active player can accept it.

### DECIDING
After the last responder, the active player picks exactly one of:
- `ConfirmTrade(j)`: execute a trade with responder `j`, using either `j`'s `Accept` (at the original offer's terms) or `j`'s `Counter` (at the counter's terms). Legal only for responders who accepted or countered.
- `ProposeTrade(offer)`: start a new round (a different offer; see limits).
- `CancelTrade`: close negotiation, return to MAIN.

If nobody accepted or countered, only `ProposeTrade` and `CancelTrade` are offered.

### Execution
`ConfirmTrade(j)` swaps the resources atomically and returns to MAIN. Because no other action was possible in between, the swap cannot fail on resource checks.

## 5. Official-rules alignment (VERIFY each)
- Trade is only between the active player and others; **responders never trade among themselves**.
- Counter-offers: the rulebook allows negotiation, so responders may propose alternatives to the active player. Decision: modeled as `Counter`.
- Trading before the roll: not allowed (assumed).
- Giving cards away for nothing: not allowed (assumed).
- Whether an Accept is binding before the active player confirms: in this engine it is not; only `ConfirmTrade` is binding.

## 6. Limits (config, defaults are proposals)
Real negotiation can loop forever, so the engine bounds it:
- `max_proposals_per_turn`: default 5. A `ProposeTrade` is illegal once reached; `CancelTrade` remains legal.
- **No repeats**: an offer identical to one already proposed this turn is illegal. This blocks trivial loops and keeps the logs meaningful.
- Counters: at most one per responder per round (inherent in the single response per responder).

## 7. Action encoding for RL (fixed flat list for now)
The engine accepts any valid offer. The RL action list enumerates a **bounded subset** with a config cap `rl_max_cards_per_side`:

| Cap | Distinct offers | Notes |
|---|---|---|
| 2 cards per side | 230 | Good default for the first agents |
| 3 cards per side | 1,170 | Verified by brute-force enumeration |

Flat action ids for trading:
- `ProposeTrade(offer)`: one id per enumerated offer
- `Counter(offer)`: one id per enumerated offer (same table, from the responder's side)
- `Accept`, `Reject`: 1 id each
- `ConfirmTrade(j)`: one id per other seat (3 for a 4-player game; seat-relative, so id 0 = player to the left)
- `CancelTrade`: 1 id

Legal-action masks come from `legal_actions(state)`, which already encodes holdings and limits. In Phase 5 this can be revisited as a factored head ("what to give", then "what to ask").

Gym env details:
- `current_player` during RESPONDING is the **responder**, not the active player, so the env must expose whose observation to build.
- Forced single-action states (only `Reject` legal) can be auto-stepped by the env; the engine itself does not skip them.
- Observation must include: the open offer, each responder's response so far, the number of proposals used this turn, and the offers already tried this turn.

## 8. Invariants (hypothesis property tests)
1. **Conservation:** total cards of each resource across all hands are unchanged by a domestic trade.
2. **Frozen hands:** hands do not change between `ProposeTrade` and `ConfirmTrade`/`CancelTrade`.
3. **Confirm always executes:** every `ConfirmTrade(j)` listed as legal succeeds.
4. **Termination:** with the limits in section 6, every turn's trade phase terminates.
5. **Only the active player proposes:** `ProposeTrade` is never legal for anyone else.
6. **Determinism:** replaying (seed, actions) reproduces identical state hashes.
7. **Validity:** no executed trade has an empty side, overlapping resource types, or a negative hand.

## 9. Logging and replay
Every trade event is logged, **including offers that nobody accepts**:
- `TradeProposed(turn, round, offer)`
- `TradeResponded(responder, Accept | Reject | Counter(offer'))`
- `TradeConfirmed(with, terms)` or `TradeCancelled`

This is part of the normal (seed + actions) game log, so it goes into the golden replays. The data is also the training set for a future trading policy.

## 10. Real-time negotiation (v2, later)
The engine stays as specified. Real-time simultaneous negotiation is a **server** concern:
- The server collects responses from humans and bots concurrently, applies a response timer, and **orders** them (first valid accept wins ties, timeouts become `Reject`).
- It then feeds the engine the same ordered events as above, so replays and RL semantics are unchanged.
- Race conditions (two simultaneous accepts) are resolved in the server by ordering, never inside the engine.

## 11. Chat and LLM layer (later)
- Natural language ("anyone got wheat? I'll give brick") is parsed into `ProposeTrade`, `Accept`, `Reject` or `Counter`.
- Every parsed intent is **validated against `legal_actions`** before it reaches the engine.
- The bots' trade decisions come from the RL/search agent. The LLM only phrases the bot's decision and parses humans' words. It never decides a trade.
- The LLM must not reveal the bot's hand beyond what a human would reveal.

## 12. Edge cases to specify and test
| # | Situation | Decision |
|---|-----------|----------|
| 1 | Responder cannot afford `want` | `Accept` not legal |
| 2 | Active player no longer holds `give` after a counter swap? | Not possible: hands are frozen while a trade is open |
| 3 | Two responders accept | Active player picks one; the other is unaffected |
| 4 | Counter identical to the original offer | Illegal; use `Accept` instead |
| 5 | Active player re-proposes an earlier offer this turn | Illegal (no repeats) |
| 6 | Bank has no card for a bank trade | Not related to this protocol; covered in `rules-spec.md` |
| 7 | Trade attempt during setup, before the roll, or during robber resolution | Illegal |
| 8 | Player reaches 10 VP | Not triggered by trading; win check as in `rules-spec.md` |
| 9 | 3-player game | Seat-relative `ConfirmTrade` ids use 2 slots |

## 13. Open questions
- **Targeted offers:** should the active player be able to address an offer to a subset ("anyone with wheat?" vs "Player 2 only")? v1 broadcasts to all; an optional `audience` field could be reserved now for the chat layer.
- Default values for `max_proposals_per_turn` and `rl_max_cards_per_side`.
- Whether responses should be hidden until all responders have acted (simultaneous sealed responses) instead of sequential and public.