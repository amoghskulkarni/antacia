# Status

Update at the end of every session. Keep it under ~40 lines.

**Last updated:** 2026-10-27
**Phase:** 1 (core engine), Week 0 wrap-up; Week 2 planned (Week 1 board work pulled forward and done)

## Done
- Planning, docs, ADRs 0001-0006. Tooling: `pyproject.toml` (uv, Python >=3.14, ruff, mypy strict on `engine/`, pytest, hypothesis), CI workflow (passes locally; not yet run on GitHub).
- Engine scaffold: API stubs in `engine/game.py`, `types.py` enums, placeholder `GameState`; nested `CLAUDE.md` in `tests/`, `engine/rules/`.
- Actions: 19 frozen dataclasses in `engine/actions.py`; `ResourceCounts`, `Offer`, board id aliases. Encodings recorded as ADRs 0011-0014 (setup reuses build actions, combined `MoveRobber`, `DiscardOne`, broadcast-only offers).
- ADRs 0007-0010 Accepted and implemented:
  - `engine/rng.py`: SplitMix64 (matches reference outputs), `randbelow`, `shuffle`, `roll_dice`.
  - `engine/topology.py`: axial coordinates, row-major ids (19/54/72), adjacency tables, coast ring, 9 harbor slots; pinned by `tests/conformance/topology.json`.
  - `engine/board.py`: beginner + random layouts, A-R spiral tokens, shuffled harbors, `render_board` ASCII printer.
- ADR 0015: all 12 board symmetries are legal boards. `topology.py` symmetry tables, two harbor frames (`HARBOR_FRAMES` replaces `HARBOR_SLOTS`), `Board.frame`, `vertex_harbors`, `engine/symmetry.py` (`transform_board`, `transform_action`). Docs: `docs/board-symmetry.md`.
- Token spiral verified against the rulebook: counterclockwise from any outer corner (pinned by `test_spiral_from_north_east_corner_matches_rulebook`). CI green on GitHub.
- `trade-protocol.md` aligned with the code (action names, `Offer` without proposer, counters from the responder's side).

## Now (Week 0 wrap-up)
1. Fill `docs/rules-spec.md` sections 1-3 (in progress). Section 2 blocks Week 2.
2. Decide license; a MIT `LICENSE` file already exists. Confirm the project name.

## Planned (do in due time; remind at session start)
- Review ADRs 0004 and 0006 (status Proposed); 0006 is needed by Week 6.
- Check the `VERIFY` items in `docs/trade-protocol.md` against the rulebook (needed by Week 5).
- `docs/workflow.md` is empty: fill it or delete it.

## Next (Week 2: GameState + setup)
Decided: seat 0 starts and callers shuffle seats (ADR 0016); bank and piece counts are derived, not stored.
1. `ResourceCounts` arithmetic.
2. `GameState`/`PlayerState`/`Phase` + `new_game(seed, num_players, layout)`.
3. Setup `legal_actions`/`step`: snake order, distance rule, road touches the new settlement; `IllegalActionError`.
4. Starting resources from the second settlement.
5. End of setup -> `PRE_ROLL`, seat 0.
6. Property tests: random agent completes setup; determinism.
7. `transform_state` + equivariance property test (ADR 0015).

## Blocked / open questions
- Sequential vs sealed trade responses (`trade-protocol.md` section 13).
- Defaults for `max_proposals_per_turn` and the RL trade-size cap.
- Discard order between players after a 7 (`rules-spec.md` section 4, ADR 0013).

## Pointers (Do not preload)
- Roadmap and decisions: `docs/project-context.md`
- Decision index: `docs/decisions/README.md`
