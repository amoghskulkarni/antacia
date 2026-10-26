# Board symmetries

How the engine treats rotated and mirrored boards as the same game, what that changed in the code, and how to turn one recorded game into 12 training games.

Decision: ADR 0015. Prerequisite: `docs/board-topology.md` (coordinates, ids, adjacency tables). All example numbers on this page were printed from the code.

## 1. The idea

Walk around a Catan table and look at the board from another seat: nothing about the game has changed, only which hex you'd call "top left". The engine sees the board through fixed coordinates and ids, so from its point of view a turned board *looks* different (different ids everywhere) even though it *is* the same game.

A mirror image is a little different: you can't see it by walking around the table. But no rule depends on handedness either, so it is also the same game.

Two consequences:

- The engine should accept every turned or mirrored board as a legal board.
- A bot that learns from one game can also learn from its 11 turned and mirrored copies, for free.

## 2. The 12 symmetries

A regular hexagon (and the 19-hex board) has exactly 12 symmetries: 6 rotations and 6 mirror images. In the code each one has an index `s`:

| `s` | symmetry |
|---|---|
| 0 | identity (do nothing) |
| 1..5 | rotate by 60°, 120°, 180°, 240°, 300° **counterclockwise** (on screen) |
| 6 | mirror left-right (across the vertical line through the centre hex) |
| 7..11 | mirror left-right, then rotate by 60°, 120°, 180°, 240°, 300° |

Where hex 0 (the top-left hex, `(0, -2)`) goes under each one:

| `s` | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hex 0 goes to | 0 | 7 | 16 | 18 | 11 | 2 | 2 | 0 | 7 | 16 | 18 | 11 |

Note `s = 7` keeps hex 0 in place: mirroring and then rotating by 60° is itself a mirror, across the line through hex 0 and the centre.

### Rotation and mirror in axial coordinates

Both are one line each (`topology.rotate_hex`, `topology.mirror_hex`):

```
rotate 60° counterclockwise:   (q, r)  ->  (q + r, -q)
mirror left-right:             (q, r)  ->  (-q - r, r)
```

Check the rotation on the east corner hex `(2, 0)`: it goes to `(2, -2)`, the north-east corner, which is "up" on screen, i.e. counterclockwise. Check the mirror on any hex: its on-screen x position `2q + r` becomes `2(-q - r) + r = -(2q + r)`, so x flips sign and y (`3r`) stays.

In cube coordinates `(q, r, s)` with `s = -q - r`, the rotation is `(q, r, s) -> (-s, -q, -r)`: shift the three coordinates round and negate them. That is the usual way to see why six of them bring you back to the start.

### Vertices and edges

A vertex is named after the hex that owns it (`(q, r, N or S)`, see `board-topology.md` section 5), and that naming does not survive a rotation: the top corner of a hex is not the top corner after turning the board. So vertices and edges are transformed through a name-free description instead:

- a vertex is identified by the **3 hexes** that meet at it (land or sea);
- an edge is identified by the **2 hexes** on either side of it.

Transform those hexes, then look up which vertex or edge they describe. That is how `VERTEX_SYMMETRIES` and `EDGE_SYMMETRIES` are built.

### The tables

All transforms are precomputed permutation tables in `engine/topology.py`, indexed `[s][id]`:

| table | meaning |
|---|---|
| `HEX_SYMMETRIES[s][h]` | where hex `h` goes under symmetry `s` |
| `VERTEX_SYMMETRIES[s][v]` | where vertex `v` goes |
| `EDGE_SYMMETRIES[s][e]` | where edge `e` goes |
| `INVERSE_SYMMETRY[s]` | the symmetry that undoes `s` |

`INVERSE_SYMMETRY` is `(0, 5, 4, 3, 2, 1, 6, 7, 8, 9, 10, 11)`: rotating by 60° is undone by rotating by 300°, and every mirror undoes itself.

Example, vertex 24 (the NE corner of the centre hex): under `s = 1` it goes to vertex 18 (the centre hex's top corner), and under the mirror `s = 6` to vertex 23 (the NW corner).

## 3. What a transformed board looks like

The beginner board, and the same board under `s = 1` (rotate 60°) and `s = 6` (mirror), from `render_board`:

```
beginner                          s = 1 (rotate 60°)               s = 6 (mirror)
      [MO10][PA 2][FO 9]                [FO 9][HI10][MO 8]               [FO 9][PA 2][MO10]
   [FI12][HI 6][PA 4][HI10]          [PA 2][PA 4][FO 3][PA 5]         [HI10][PA 4][HI 6][FI12]
[FI 9][FO11][DE  ][FO 3][MO 8]    [MO10][HI 6][DE  ][FI 4][PA11]   [MO 8][FO 3][DE  ][FO11][FI 9]
   [FO 8][MO 3][FI 4][PA 5]          [FI12][FO11][MO 3][FI 6]         [PA 5][FI 4][MO 3][FO 8]
      [HI 5][FI 6][PA11]                [FI 9][FO 8][HI 5]               [PA11][FI 6][HI 5]
```

In the rotated board, the top-left mountain 10 (hex 0) has moved to the west corner (hex 7). In the mirrored board every row is reversed. The desert stays in the centre: the centre hex is the one hex no symmetry moves.

## 4. Harbor frames

The 9 rulebook harbor edges are **not** symmetric under every rotation. Turning the board by 60° moves them onto 9 other coastal edges. Doing that for all 12 symmetries gives exactly **two** sets, called *frames*:

| frame | harbor edges, slot 0..8 |
|---|---|
| 0 (rulebook) | 0, 3, 17, 38, 61, 69, 66, 49, 18 |
| 1 (frame 0 turned 60°) | 33, 10, 2, 5, 22, 53, 71, 68, 54 |

The two frames share no edges (they do share 6 vertices). Which frame each symmetry produces from frame 0:

- rotations by 0°, 120°, 240° and three of the mirrors: frame 0 (harbors stay on the same edges, possibly reshuffled between slots);
- rotations by 60°, 180°, 300° and the other three mirrors: frame 1.

A board records its frame in `Board.frame`, and `Board.harbors[i]` is the harbor type on slot `i` of that frame (edge `HARBOR_FRAMES[board.frame][i]`).

### Slot ids

Frame 0 slots run clockwise around the coast starting at edge 0. Frame 1 slot `i` is frame 0 slot `i` turned by 60°, so it is clockwise too. Because of this, symmetries act on `(frame, slot)` by simple formulas:

```
rotate by 60°·k:     (f, i)  ->  ((f + k) mod 2,  i - 3·floor((f + k) / 2)  mod 9)
mirror left-right:   (f, i)  ->  (1 - f,  3 - i  mod 9)
```

For example, rotating by 120° (`k = 2`) keeps frame 0 and sends slot `i` to slot `i - 3`: slot ids go *down* because slots are clockwise and the rotation is counterclockwise. The code doesn't use these formulas (it uses `HARBOR_SLOT_OF_EDGE`, a lookup from edge to `(frame, slot)`), but a test checks them, so they are safe to rely on in reasoning.

### Never use slot ids in rules

Rules and observations must look harbors up **per vertex**, with `engine.board.vertex_harbors(board)`. It returns, for each of the 54 vertices, the harbor type there or `None`. That works the same for both frames and all symmetries; slot ids only matter for dealing harbor tiles in `generate_board`.

## 5. The token spiral and mirrors

Number tokens are dealt along a counterclockwise spiral (ADR 0009). Rotating a board keeps the spiral counterclockwise. Mirroring reverses it: a mirrored board's tokens follow a *clockwise* spiral. The game is unaffected (tokens are just numbers on hexes), and clockwise spirals also never put two red numbers (6, 8) next to each other, so mirrored boards are just as fair. The generator always deals counterclockwise (ADR 0015); mirrored boards only appear through `transform_board`.

## 6. What changed in the code

| before | after | why |
|---|---|---|
| `topology.HARBOR_SLOTS` (9 edges) | `topology.HARBOR_FRAMES` (2 frames of 9 edges) and `HARBOR_SLOT_OF_EDGE` | a turned board puts harbors on the other frame |
| `Board(terrains, tokens, harbors)` | `Board(terrains, tokens, harbors, frame)` | a board must say which frame its slots refer to |
| harbors looked up by slot | `engine.board.vertex_harbors(board)`, per vertex | works for both frames and every symmetry |
| (none) | `rotate_hex`, `mirror_hex`, `apply_symmetry` | the geometry of the 12 symmetries |
| (none) | `HEX_SYMMETRIES`, `VERTEX_SYMMETRIES`, `EDGE_SYMMETRIES`, `INVERSE_SYMMETRY` | precomputed relabellings |
| (none) | `engine/symmetry.py`: `transform_board`, `transform_action` | apply a symmetry to game data |
| `topology.json`: `harbor_slots` | `harbor_frames` plus the four symmetry tables | pins everything for the Rust port |
| `render_board` | also prints `harbor frame N` | |

Unchanged: all ids, the adjacency tables, and `generate_board`. Every seed still deals exactly the same board (frame 0), so nothing in the RNG order moved.

## 7. Augmenting one game x12

A recorded game is a board plus a list of actions (and the RNG state after the board was dealt). To get the 12 equivalent games:

```python
from engine import topology as t
from engine.symmetry import transform_action, transform_board

for s in range(t.NUM_SYMMETRIES):
    board_s = transform_board(board, s)
    actions_s = [transform_action(a, s) for a in actions]
    # replay actions_s on board_s with the same RNG state: it is game s
```

What moves under a symmetry: hexes (terrains, tokens, the robber), vertices (settlements, cities, harbors), edges (roads). What doesn't: players, seat order, hands, resources, dice, development cards, trade offers. So `MoveRobber(hex=0, victim=2)` becomes `MoveRobber(hex=7, victim=2)` under `s = 1`: the hex moves, the victim doesn't.

Why the same RNG state reproduces the transformed game: after the board is dealt, chance only decides dice, card draws and which card is stolen. None of those depend on where things are on the board, so the same draws give the same outcomes in all 12 copies.

Planned next (when the types exist): `transform_state` (Week 2), and observation, action-id and legality-mask transforms (Week 6).

## 8. New concepts

- **Permutation table.** A symmetry is stored as a list where position `x` holds the id that `x` moves to. Applying it is one lookup; no geometry at runtime.
- **Composition and inverse.** Doing symmetry `a` and then `b` is again one of the 12 (`table[b][table[a][x]]`), and every symmetry has an inverse that undoes it. Mathematically the 12 form a *group* (the dihedral group of the hexagon, often written D6). You don't need group theory to use the tables; "you can chain them and undo them" is all it means here.
- **Invariance.** Some quantities don't change under a symmetry: who is winning, the value of a position, the number of legal moves. A value network should give the same output for all 12 copies of a position.
- **Equivariance.** Some quantities change *in step with* the board: the best move under symmetry `s` is the best move transformed by `s`. For the engine this means `step(g·state, g·action) = g·step(state, action)`. A policy network should be equivariant: its probability for action `a` in a position equals its probability for `g·a` in `g·position`.
- **Augmentation.** Train on all 12 copies of each position, so the network learns invariance and equivariance from data. This is what ADR 0006's "x12 augmentation" means.
- **Canonicalisation.** The alternative to augmentation: before a bot sees a position, transform it into one standard orientation, and transform the chosen action back with the inverse. Less variety in training, but no extra data. Both use the same tables.
- **Test-time augmentation.** At play time, ask the network about all 12 copies of the current position, transform each answer back with `INVERSE_SYMMETRY`, and average. Usually a small strength gain for 12x the inference cost.
- **Harbor frame.** One of the two legal sets of 9 harbor edges (section 4).
- **Legal board.** A board the generator can deal, seen under any of the 12 symmetries.

## 9. Rules for engine code

- **Never break a tie or order an outcome by hex, vertex or edge id.** If a rule picks "the first vertex" or iterates ids to decide something, the turned board would play out differently and equivariance breaks. Order by player or by explicit rule instead.
- **Never use slot ids outside board generation.** Use `vertex_harbors`.
- **Transform actions together with the board.** Transforming only the board (or only the observation) silently teaches a bot the wrong moves.
- **Adding a new action kind** means saying how it transforms: `transform_action` lists every action kind explicitly, so mypy fails until you do.

## 10. How it is tested

`tests/unit/test_symmetry.py`:

- each table holds 12 distinct permutations, and `s = 0` is the identity;
- **every symmetry preserves every adjacency table** (the property that makes them the same game);
- `s = 1` is a counterclockwise 60° rotation, `s = 6` negates every x position, `s = 6..11` are mirror-then-rotate, and inverses undo;
- the two frames, the slot formulas from section 4, and `HARBOR_SLOT_OF_EDGE`;
- `transform_board` moves terrains, tokens and per-vertex harbors with the symmetry and round-trips through the inverse; `transform_action` moves only board locations.

`tests/property/test_symmetry_properties.py` checks, over random seeds and symmetries, that transformed boards keep every component, never put red numbers side by side, keep harbors on the transformed vertices, and that transforming twice equals transforming once by the composition. `tests/conformance/topology.json` pins all symmetry tables and both frames.

Still to come: the equivariance property test for `step` and `legal_actions`, once `GameState` exists (Week 2).
