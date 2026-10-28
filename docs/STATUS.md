# Status

Update at the end of every session. Keep it under ~40 lines.

**Last updated:** 2026-10-28
**Phase:** 1 (core engine), Week 2 (setup phase done; equivariance test left)

## Done
- Planning, docs, ADRs 0001-0016. Tooling: uv, ruff, mypy strict, pytest, hypothesis; CI green on GitHub. License: MIT.
- Actions: 19 frozen dataclasses (`engine/actions.py`); encodings in ADRs 0011-0014.
- Board (ADRs 0007-0010, 0015): SplitMix64 RNG, topology tables, beginner + random layouts with the rulebook spiral (counterclockwise from any corner, verified), ASCII printer, 12 symmetries, `transform_board`/`transform_action`.
- rules-spec sections 1-2 filled and verified; edge cases 1-5 logged in section 10.
- Week 2 setup (rules-spec 2): `ResourceCounts` arithmetic, `terrain_resource`, `GameState`/`PlayerState`/`Phase`, `new_game` (3-4 players, seat 0 starts per ADR 0016), setup `legal_actions`/`step` in `engine/rules/setup.py` (snake order, distance rule, connection rule, starting resources, ends in `PRE_ROLL`), `IllegalActionError`. Property tests: random agent completes setup for any seed, 3 and 4 players.

## Now
1. `transform_state` + equivariance property test for setup (ADR 0015); then finish Week 2.
2. Fill rules-spec section 3 (turn structure); section 4-5 before Week 3 coding starts.
3. Confirm the project name.

## Planned (do in due time; remind at session start)
- Review ADRs 0004 and 0006 (status Proposed); 0006 is needed by Week 6.
- Check the `VERIFY` items in `docs/trade-protocol.md` against the rulebook (needed by Week 5).
- `docs/workflow.md` is empty: fill it or delete it.

## Next (Week 3: dice, production, building, robber, 7-discard)
- Adds `robber` (starts on the desert; add to the spec first) and city tracking to `GameState`.
- Move `_distance_rule_ok` from `rules/setup.py` to `engine/` when normal building needs it.

## Blocked / open questions
- Sequential vs sealed trade responses (`trade-protocol.md` section 13).
- Defaults for `max_proposals_per_turn` and the RL trade-size cap.
- Discard order between players after a 7 (`rules-spec.md` section 4, ADR 0013).

## Pointers (Do not preload)
- Roadmap and decisions: `docs/project-context.md`
- Decision index: `docs/decisions/README.md`
