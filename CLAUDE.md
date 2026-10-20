# Antacia (working name; anagram of "Catan AI"): Catan-compatible engine, RL gym, and web app

## Goal
A deterministic, fast, official-rules base-game engine (3-4 players) that powers:
1. a Gymnasium/PettingZoo env for RL training and bot-vs-bot evaluation,
2. a FastAPI game server (authoritative) with WebSockets,
3. a React client for humans.
Trading between humans and bots is a first-class feature. The project will be open-sourced.

## Context
Full decision log, roadmap and current phase plan: @docs/project-context.md
Rules source of truth: @docs/rules-spec.md

## Architecture
- `engine/`: pure rules. No I/O, no globals, no wall-clock time, seedable RNG only. Single source of truth.
- `gym_env/`: thin wrapper over the engine. No rules logic here.
- `bots/`: baseline and learned agents. They only see an Observation and return an Action.
- `eval/`: tournament and Elo/TrueSkill harness.
- `server/`: FastAPI + WebSockets. Holds one engine instance per game. No rules logic here.
- `web/`: React client. Renders server state and sends intents. No rules logic here.
- `tests/conformance/`: language-agnostic golden replays (seed + actions -> expected state hashes). A future Rust engine must pass these.

## Hard rules
- The engine is deterministic given (seed, action list). Never use unseeded randomness or time in `engine/`.
- State is immutable and copy-on-step: `step(state, action) -> new_state`. Never mutate a state in place.
- Inside the engine hot path use frozen dataclasses / tuples, not Pydantic. Pydantic is for config, API schemas, and log serialization at the boundaries.
- Follow `docs/rules-spec.md` strictly (official Catan rules). If a rule is ambiguous, ask me; do not guess.
- Trades: only the active player initiates, only during their own turn (turn-synchronous protocol, see `docs/trade-protocol.md`).
- Every rule or behavior change needs a test. Add hypothesis property tests for invariants (resource conservation, legal-action masks, determinism).
- Type everything; `mypy engine` must pass.

## Commands
- Install: `uv sync`
- Test: `uv run pytest -q`
- Lint/format: `uv run ruff check . && uv run ruff format .`
- Types: `uv run mypy engine`

## How we work together (important)
The goal of this project is for me to learn, not just to ship. So:
- Before implementing any non-trivial module, propose a short plan (data structures, function signatures, edge cases) and wait for my go-ahead.
- Work in small steps: one function or one rule at a time, small diffs, one concern per commit.
- Prefer tests first: write or propose failing tests, then the implementation.
- Briefly explain non-obvious design choices and algorithms (e.g. longest-road search) in plain language.
- I will write some core pieces myself. When I do, review them critically rather than rewriting them.
- Ask before adding a dependency or changing project structure.