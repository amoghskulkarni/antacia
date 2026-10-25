# Property tests

`hypothesis` tests for engine invariants that must hold in every reachable state:

- resource conservation (bank + all hands = fixed totals)
- `legal_actions` matches `step` legality (every listed action is accepted, unlisted ones rejected)
- determinism: same seed + actions -> same state
- no negative hands, piece limits respected

Added as each rule lands (from Week 1 onward). See `tests/CLAUDE.md` for conventions.
