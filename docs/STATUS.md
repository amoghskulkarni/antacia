# Status

Update at the end of every session. Keep it under ~40 lines.

**Last updated:** 2026-10-23
**Phase:** 1 (core engine), Week 0

## Done
- Planning complete: scope, architecture, tech choices (see `project-context.md`).
- Docs drafted: `CLAUDE.md` (root and `engine/`), `rules-spec.md` skeleton, `trade-protocol.md`, `agent-roadmap.md`, ADRs 0001-0006.
- Repo created under the name `antacia`.

## Now (Week 0)
1. `pyproject.toml` with uv, ruff, mypy (strict on `engine/`), pytest, hypothesis.
2. CI workflow (lint, types, tests) green on an empty test.
3. Fill `docs/rules-spec.md` sections 1-3 from the official rulebook; resolve the `VERIFY` items.
4. Check the `VERIFY` items in `docs/trade-protocol.md` against the rulebook.
5. Decide license (MIT / Apache-2.0 / GPL) and confirm the project name.
6. Review ADRs 0004 and 0006 (status Proposed) and mark them Accepted or revise.

## Next (Week 1)
- Board geometry: choose the hex coordinate system (first real design decision, write an ADR), vertices/edges, adjacency, harbors, seeded board generation, ASCII printer.

## Blocked / open questions
- Targeted vs broadcast trade offers; sequential vs sealed responses (`trade-protocol.md` section 13).
- Defaults for `max_proposals_per_turn` and the RL trade-size cap.

## Pointers (Do not preload)
- Roadmap and decisions: `docs/project-context.md`
- Decision index: `docs/decisions/README.md`
