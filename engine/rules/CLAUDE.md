# engine/rules/: one module per rule area

All of `engine/CLAUDE.md` applies here. Additionally:

- Each module covers one section of `docs/rules-spec.md` and says which in its docstring. If a rule isn't in the spec yet, add it to the spec (and ask me if it's ambiguous) before coding it.
- Rule functions are pure helpers called only from `engine/game.py`; nothing outside the engine imports them.
- Keep legality checks and state transitions side by side, so `legal_actions` and `step` can't drift apart.
- No module imports another rule module's internals; shared logic goes in `engine/` (e.g. `board.py`, `types.py`).
- Chance (dice, draws, steals) takes the RNG state as input and returns the new one; never call `random`.
