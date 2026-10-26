# engine/: rules engine

Pure game rules. This is the single source of truth for the server, the Gym env, the bots and (later) the Rust port.

## Hard rules
- **Deterministic:** the same `(seed, action list)` always produces the same game. No unseeded randomness, no wall-clock time, no globals, no I/O.
- **Immutable, copy-on-step:** `step(state, action) -> new_state`. Never mutate a state in place. (ADR 0002)
- **Hot-path types:** frozen dataclasses (slots) and tuples. No Pydantic inside the engine; Pydantic belongs at the boundaries (API schemas, config, replay logs). (ADR 0004)
- **Official rules, strictly:** follow `docs/rules-spec.md`. If a rule is ambiguous, ask me; do not guess.
- **Trades:** only the active player initiates, only during their own turn. Follow `docs/trade-protocol.md`. (ADR 0003)
- **Python-only idioms stay out** of the engine core (no dynamic attribute tricks, no reliance on dict ordering for game logic), because a Rust port must reproduce it exactly. (ADR 0001)
- **Equivariant under board symmetries (ADR 0015):** never break a tie or order an outcome by hex, vertex or edge id, and never use harbor slot ids outside board generation (use `vertex_harbors`). Turning or mirroring the board must give the same game. See `docs/board-symmetry.md`.
- **Chance is explicit:** dice and card draws come from the seeded RNG passed through the state, never from a global.

## Interfaces the engine must provide
- `legal_actions(state) -> mask / list`: single source of legality for everyone.
- `step(state, action) -> new_state`.
- `is_terminal(state)`, `winner(state)`.
- A structured observation (vertex, edge and hex arrays plus adjacency) with a separate `flatten()`. (ADR 0006)
- A fixed, enumerated action list; the engine itself accepts any valid trade offer, while the RL list uses a bounded subset. (ADR 0005)

## Testing
- Every rule change needs a unit test.
- Add `hypothesis` property tests for invariants: resource conservation, legal-action masks match `step` legality, determinism, no negative hands, piece limits.
- Golden replays in `tests/conformance/` (seed + actions -> expected state hashes) are language-neutral; the Rust port must pass them.
- Log every game as seed + action sequence, including all trade offers, even rejected ones.

## Commands
- Types: `uv run mypy engine` (strict; must pass)
- Tests for this package: `uv run pytest tests -q`
