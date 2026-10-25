# Antacia 

Catan-compatible base-game platform (3-4 players, official rules): a deterministic rules engine, a Gymnasium/PettingZoo env for RL, a FastAPI server, and a React client. Trading between humans and bots is a first-class feature. Hobby project, to be open-sourced.

## Layout
- `engine/`: rules engine, the single source of truth (has its own `CLAUDE.md`)
- `gym_env/`: RL wrapper over the engine; no rules logic
- `bots/`, `eval/`: agents; tournaments and ratings
- `server/`: FastAPI + WebSockets, authoritative; no rules logic
- `web/`: React client; renders state and sends intents; no rules logic
- `tests/`: `unit/`, `property/`, `conformance/` (golden replays)

## Where to look (read on demand, do not preload)
- Current state and next tasks: `docs/STATUS.md` (read this first each session)
- Decisions and roadmap: `docs/project-context.md`
- Why a decision was made: `docs/decisions/README.md` (index; open only the ADR you need)
- Rules, source of truth: `docs/rules-spec.md`
- Trading protocol: `docs/trade-protocol.md`
- Bots, search, LLM chat layer: `docs/agent-roadmap.md`

## Commands
- Install: `uv sync`
- Test: `uv run pytest -q`
- Lint/format: `uv run ruff check . && uv run ruff format .`

## How we work together (important)
The goal of this project is for me to learn, not just to ship. So:
- Before implementing any non-trivial module, propose a short plan (data structures, function signatures, edge cases) and wait for my go-ahead.
- Work in small steps: one function or one rule at a time, small diffs, one concern per commit.
- Prefer tests first: write or propose failing tests, then the implementation.
- Briefly explain non-obvious design choices and algorithms in plain language.
- I will write some core pieces myself. When I do, review them critically rather than rewriting them.
- Ask before adding a dependency or changing project structure.
- Every behavior change needs a test.
- At the end of a session: update `docs/STATUS.md`, and add an ADR in `docs/decisions/` for any decision that is costly to reverse.
