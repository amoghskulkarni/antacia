# 0014: Trade offers are broadcast to all opponents (no targeted offers yet)

Status: Accepted (2026-10-25)

## Context
At the table, players often address offers to someone ("Player 2, brick for ore?") or to whoever has a resource. `docs/trade-protocol.md` left open whether `Offer` should carry an `audience`. The chat/LLM layer, which is the main reason to want targeted offers, comes much later.

## Decision
v1 offers have no audience: every `ProposeTrade` goes to all opponents, who respond in seat order (trade-protocol section 4). `Offer` is just `(give, want)`. Targeted offers will be added later, together with the chat layer.

## Options considered
- **Broadcast only (chosen):** simplest protocol and RL encoding; one id per offer.
- **Optional `audience` field now:** ready for the chat layer, but multiplies the RL trade ids by the number of possible audiences (or forces a separate head), for a feature nothing uses yet.
- **Audience as a server/UI hint only** (the engine ignores it): misleading, because non-addressed players could still accept.

## Consequences
- Good: small trade action space; fewer protocol states; simpler tests.
- Bad: adding an audience later changes `Offer`, the RL encoding and the log format, so trade logs and trained trading policies from before that change need a version bump or migration.
- A human can still direct an offer socially (chat), and others simply `RejectTrade`.

## Revisit when
- The chat/LLM layer work starts.
- Human playtests show broadcast offers feel unnatural or slow the game down.
- Real-time negotiation (trade-protocol v2) is designed.
