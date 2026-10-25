# 0012: Robber move and steal as one action

Status: Accepted (2026-10-25)

## Context
After a 7 (and its discards) or a Knight, the active player moves the robber to another hex and then steals one random card from an opponent with a settlement or city on that hex, if any. This can be encoded as one decision or two.

## Decision
One action, `MoveRobber(hex, victim)`. `victim` is a `PlayerId`, or `None` only when no opponent with cards touches the new hex. `legal_actions` lists every valid `(hex, victim)` pair. The stolen card is chosen by the seeded RNG during `step`.

## Options considered
- **Combined (chosen):** one decision, no in-between "choose victim" phase in the state machine; about 19 × 4 RL ids (hexes × {opponents, none}).
- **Two steps, `MoveRobber(hex)` then `Steal(victim)`:** fewer ids (19 + 3), and maybe closer to how people say it at the table, but it needs an extra phase, and in most positions the steal step has only one legal option anyway.

## Consequences
- Good: a simpler phase machine; the agent picks the hex and victim together, which is the actual strategic choice.
- Bad: a slightly larger flat action space; most `(hex, victim)` pairs are illegal in any given state (masked).
- The UI can still present it as two clicks; the client combines them into one intent.

## Revisit when
- Phase 5 moves to factored or autoregressive action heads (hex, then victim).
- The flat action space size becomes a training problem.
- Expansions add robber-like pieces with separate effects (e.g. a pirate).
