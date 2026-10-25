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
- Action dataclasses in `engine/actions.py` (19 kinds), plus `ResourceCounts`, `Offer` and board id aliases in `types.py`. Decisions: setup reuses `BuildSettlement`/`BuildRoad`; robber move + steal is one `MoveRobber(hex, victim)`; 7-discards are one card per `DiscardOne`; actions never name the actor; no targeted offers yet.
- ADRs 0007-0010 drafted (Proposed): hex coordinates, board ids/topology, layout generation, RNG.

## Now (Week 0)
1. Push and confirm CI is green on GitHub.
2. Review ADRs 0007-0010 one by one; mark Accepted or revise. Resolve their `VERIFY` items (0009) against the rulebook.
3. Fill `docs/rules-spec.md` sections 1-3 from the official rulebook; resolve the `VERIFY` items.
4. Check the `VERIFY` items in `docs/trade-protocol.md` against the rulebook. Section 2 says `Offer(proposer, ...)`; the code leaves the proposer implicit.
5. Decide license (MIT / Apache-2.0 / GPL) and confirm the project name.
6. Review ADRs 0004 and 0006 (status Proposed) and mark them Accepted or revise.

## Next (Week 1)
- Implement ADRs 0007-0010: coordinates, ids and topology tables, seeded RNG, board generation, ASCII printer.

## Blocked / open questions
- Targeted vs broadcast trade offers; sequential vs sealed responses (`trade-protocol.md` section 13).
- Defaults for `max_proposals_per_turn` and the RL trade-size cap.

## Pointers (Do not preload)
- Roadmap and decisions: `docs/project-context.md`
- Decision index: `docs/decisions/README.md`
