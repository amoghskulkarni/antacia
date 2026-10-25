# Status

Update at the end of every session. Keep it under ~40 lines.

**Last updated:** 2026-10-25
**Phase:** 1 (core engine), Week 0 (Week 1 board work pulled forward and done)

## Done
- Planning, docs, ADRs 0001-0006. Tooling: `pyproject.toml` (uv, Python >=3.14, ruff, mypy strict on `engine/`, pytest, hypothesis), CI workflow (passes locally; not yet run on GitHub).
- Engine scaffold: API stubs in `engine/game.py`, `types.py` enums, placeholder `GameState`; nested `CLAUDE.md` in `tests/`, `engine/rules/`.
- Actions: 19 frozen dataclasses in `engine/actions.py`; `ResourceCounts`, `Offer`, board id aliases. Encodings recorded as ADRs 0011-0014 (setup reuses build actions, combined `MoveRobber`, `DiscardOne`, broadcast-only offers).
- ADRs 0007-0010 Accepted and implemented:
  - `engine/rng.py`: SplitMix64 (matches reference outputs), `randbelow`, `shuffle`, `roll_dice`.
  - `engine/topology.py`: axial coordinates, row-major ids (19/54/72), adjacency tables, coast ring, 9 harbor slots; pinned by `tests/conformance/topology.json`.
  - `engine/board.py`: beginner + random layouts, A-R spiral tokens, shuffled harbors, `render_board` ASCII printer.
- `trade-protocol.md` aligned with the code (action names, `Offer` without proposer, counters from the responder's side).

## Now (Week 0)
1. Push and confirm CI is green on GitHub.
2. VERIFY against the rulebook: beginner terrains/tokens and harbor types (`engine/board.py`), harbor slot positions (`engine/topology.py`), spiral direction (counterclockwise). Run `render_board` to compare.
3. Fill `docs/rules-spec.md` sections 1-3; resolve the `VERIFY` items.
4. Check the `VERIFY` items in `docs/trade-protocol.md` against the rulebook.
5. Decide license (MIT / Apache-2.0 / GPL) and confirm the project name.
6. Review ADRs 0004 and 0006 (status Proposed).

## Next (Week 2)
- `GameState` fields + setup phase (snake order, distance rule, starting resources); random agent completes setup legally.

## Blocked / open questions
- Sequential vs sealed trade responses (`trade-protocol.md` section 13).
- Defaults for `max_proposals_per_turn` and the RL trade-size cap.
- Discard order between players after a 7 (`rules-spec.md` section 4, ADR 0013).

## Pointers (Do not preload)
- Roadmap and decisions: `docs/project-context.md`
- Decision index: `docs/decisions/README.md`
