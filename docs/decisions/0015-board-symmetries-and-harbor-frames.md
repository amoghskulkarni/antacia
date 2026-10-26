# 0015: Board symmetries, two harbor frames, and x12 equivalent games

Status: Accepted (2026-10-26)

## Context
The hexagonal board has 12 symmetries: 6 rotations (multiples of 60°) and 6 mirror images. Every rule in the engine is defined through the adjacency tables (ADR 0008), and each symmetry preserves all of them. So a board turned or mirrored is the **same game**: same legal moves, same outcomes, only relabelled ids. Turning the board is just seeing the table from another seat. A mirror image cannot be seen that way, but no rule depends on handedness either (turn order follows seats, not board positions).

Our coordinates, however, have a built-in "up". Computing all 12 symmetries of the verified board (ADR 0009) showed:

| symmetry | harbors stay on the rulebook edges? | token spiral still counterclockwise? |
|---|---|---|
| rotate 0°, 120°, 240° | yes | yes |
| rotate 60°, 180°, 300° | no, they move to a second edge set | yes |
| 3 mirror images | yes | no (it becomes clockwise) |
| other 3 mirror images | no | no |

So under a rigid reading of the rules, only 3 of the 12 images of a generated board are boards the rules can deal. Yet all 12 are the same game, and ADR 0006 wants x12 symmetry augmentation for RL.

## Decision
1. **All 12 images of a legal board are legal boards.** A board is legal if it is a generated board seen under one of the 12 symmetries.
2. **Two harbor frames.** `topology.HARBOR_FRAMES` holds two disjoint sets of 9 harbor edges: frame 0, the rulebook frame (edges 0, 3, 17, 38, 61, 69, 66, 49, 18), and frame 1, frame 0 turned 60° counterclockwise (33, 10, 2, 5, 22, 53, 71, 68, 54). The 12 symmetries map frames onto frames and nothing else. `Board` records which frame it uses (`Board.frame`).
3. **Slot ids.** Frame 0 slots run clockwise around the coast starting at edge 0. Frame 1 slot `i` is the 60° rotation of frame 0 slot `i`. These ids are fixed from here on; data about specific harbors (the beginner board) is keyed by edge id, not slot id.
4. **Symmetry tables in the topology.** `HEX_SYMMETRIES`, `VERTEX_SYMMETRIES`, `EDGE_SYMMETRIES` (12 permutations each) and `INVERSE_SYMMETRY`, built at import like the other tables and pinned in `tests/conformance/topology.json`. Symmetry `s` is: `s = 0..5` rotate by 60°·s counterclockwise; `s = 6..11` mirror left-right, then rotate by 60°·(s − 6).
5. **Transforms in `engine/symmetry.py`.** `transform_board(board, s)` and `transform_action(action, s)`; GameState, observation and action-mask transforms are added when those types exist.
6. **Harbor lookup per vertex.** Rules and observations use `engine.board.vertex_harbors(board)` (vertex → harbor type or none), never slot ids, so they work for both frames.
7. **The generator only deals the original orientation.** `generate_board` always deals frame 0 with a counterclockwise spiral, so every seed gives the same board as before. This is a deliberate, final choice: the other 11 orientations exist only through `transform_board` (augmentation, canonicalisation, custom boards).
8. **Rules must be equivariant.** For any symmetry `g`: `step(g·state, g·action) = g·step(state, action)`, and `legal_actions(g·state)` = `g·legal_actions(state)` as sets. In practice: no rule may break a tie or order an outcome by hex, vertex or edge id. This becomes a hard rule in `engine/CLAUDE.md` and a property test once `GameState` exists.

## Options considered
- **All 12 legal, generator unchanged (chosen):** matches what the game is; enables exact x12 augmentation; no change to seeded boards, so nothing in the RNG order moves.
- **All 12 legal, and the generator also deals other orientations (rejected):** training and real games would see the same distribution of orientations, but every seed would produce a different board, the RNG order would change, and games would stop matching the physical game's setup procedure.
- **Rigid rules: only frame 0 and counterclockwise spirals are legal:** smallest change, but only x3 augmentation is valid, and the engine would reject boards that are the same game.
- **Canonicalise instead of augmenting:** rotate every game into one standard orientation before a bot sees it. Less data variety than augmentation, but still needs the same symmetry tables; it remains possible on top of this decision.
- **Slot ids in edge-id order instead of clockwise:** consistent with ADR 0008's id style, but symmetries then act on slots as arbitrary permutations. With clockwise slots they are formulas: rotation by 60°·k sends (frame f, slot i) to `((f + k) mod 2, i − 3·⌊(f + k)/2⌋ mod 9)`, and the left-right mirror sends `(f, i)` to `(1 − f, 3 − i mod 9)`.

## Consequences
- Good: one recorded game becomes 12 exactly equivalent games (boards and actions transformed; dice, cards and steals are not geometric, so the same RNG stream after board generation reproduces each one). ADR 0006's x12 augmentation is now correct, not approximate. Every transform is a table lookup, pinned by the conformance fixture for the Rust port.
- Bad: `Board` has an extra field; 18 edges can now hold a harbor, so code must not assume the frame-0 edges. Augmented games cannot be replayed from a seed alone (the seed always deals frame 0); the replay format (Week 6) must be able to start from an explicit board and RNG state.
- Training: actions and masks must be transformed with the board; transforming only the board teaches the model wrong moves. Real games (frame 0, counterclockwise) cover 3 of the 12 orientations; the other 9 appear only in augmented data. Because the game is identical, this costs model capacity, not correctness.
- The equivariance rule (decision 8) constrains future rule code, and its property test is the safety net.

## Revisit when
- An expansion or a 5-6 player board brings a different board shape or harbor frame.
- Training shows augmented-only orientations hurt more than they help (then canonicalise instead).
