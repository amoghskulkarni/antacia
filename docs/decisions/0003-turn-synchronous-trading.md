# 0003: Turn-synchronous trading

Status: Accepted (2026-10-20)

## Context
Trading is the project's differentiator: it should feel like a natural over-the-board conversation between humans and bots. Official rules let only the active player trade with others. RL training and replays need a deterministic, strictly ordered event sequence.

## Decision
Domestic trades are initiated only by the active player, during their own turn. The engine runs a single-actor state machine: propose, then each responder in seat order accepts, rejects or counters, then the active player confirms one response, re-proposes (bounded rounds) or cancels. Real-time simultaneous negotiation is deferred and treated as a **server** feature (timers, ordering of concurrent responses); the engine stays unchanged. Details: `docs/trade-protocol.md`.

## Options considered
- **Turn-synchronous, sequential public responses (chosen):** deterministic, replayable, matches official rules.
- **Sealed simultaneous responses:** closer to real play in some ways, but needs a hidden-response mechanic in the engine. Left as an open question.
- **Real-time negotiation inside the engine:** introduces timing and races into the rules core and breaks determinism.
- **Any player may propose trades to any other player:** violates the official rules.

## Consequences
- Good: deterministic logs and golden replays, a clean RL formulation, and a path to real-time play without engine changes.
- Bad: less spontaneous than real table talk until the server and chat layers exist. Limits (max proposals, no repeats) are needed to stop negotiation loops.

## Revisit when
Real-time online play starts (Phase 3 onward), or play testing shows sequential public responses feel unnatural or are exploitable.
