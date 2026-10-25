# Status

Update at the end of every session. Keep it under ~40 lines.

**Last updated:** 2026-10-25
**Phase:** 1 (core engine), Week 0

## Done
- Planning complete: scope, architecture, tech choices (see `project-context.md`).
- Docs drafted: `CLAUDE.md` (root and `engine/`), `rules-spec.md` skeleton, `trade-protocol.md`, `agent-roadmap.md`, ADRs 0001-0006.
- Repo created under the name `antacia`.
- `pyproject.toml` (uv, Python >=3.14, ruff, mypy strict on `engine/`, pytest, hypothesis) and `uv.lock`.
- CI workflow `.github/workflows/ci.yml` (lint, format check, mypy, pytest). Passes locally; not yet run on GitHub.
- Engine scaffold: public API stubs in `engine/game.py`, `types.py` enums, placeholder `GameState` and `Action`, `rules/` modules mapped to spec sections.
- Tests scaffold: smoke tests, `property/` and `conformance/` READMEs. Nested `CLAUDE.md` in `tests/` and `engine/rules/`.

## Now (Week 0)
1. Push and confirm CI is green on GitHub.
2. Fill `docs/rules-spec.md` sections 1-3 from the official rulebook; resolve the `VERIFY` items.
3. Check the `VERIFY` items in `docs/trade-protocol.md` against the rulebook.
4. Decide license (MIT / Apache-2.0 / GPL) and confirm the project name.
5. Review ADRs 0004 and 0006 (status Proposed) and mark them Accepted or revise.

## Next (Week 1)
- ADR: hex coordinate system (first real design decision), then vertices/edges, adjacency, harbors, seeded board generation, ASCII printer.
- ADR: RNG generator (stub and constraints in `engine/rng.py`).

## Blocked / open questions
- Targeted vs broadcast trade offers; sequential vs sealed responses (`trade-protocol.md` section 13).
- Defaults for `max_proposals_per_turn` and the RL trade-size cap.

## Pointers (Do not preload)
- Roadmap and decisions: `docs/project-context.md`
- Decision index: `docs/decisions/README.md`
