# 0002: Immutable copy-on-step game state

Status: Accepted (2026-10-20)

## Context
Search (MCTS/ISMCTS) branches from the same state many times, golden replays need determinism, and I want the engine easy to reason about and test. Performance matters later but not yet measured.

## Decision
`step(state, action) -> new_state`. States are immutable (frozen dataclasses and tuples). Nothing mutates a state in place.

## Options considered
- **Immutable copy-on-step (chosen):** simple, safe, trivial branching for search, easy property tests.
- **Mutable state with undo:** faster per step and fewer allocations, but easy to corrupt, and undo logic is a source of bugs.
- **Mutable state with explicit `copy()` before branching:** similar cost to copy-on-step but less safe, since forgetting to copy silently corrupts a search tree.

## Consequences
- Good: determinism, trivial tree search branching, simple tests, easier Rust port semantics.
- Bad: allocation and copying cost on every step. Structural sharing (reusing unchanged tuples) helps, but the cost must be measured.

## Revisit when
The steps/sec benchmark (Week 7) falls below the target for training, after profiling confirms copying is the cause, or when the Rust port makes in-place mutation with cheap cloning attractive (see ADR 0001).
