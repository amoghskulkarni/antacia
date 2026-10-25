# 0006: Structured observation with a flatten function

Status: Proposed (2026-10-21). Review and mark Accepted or revise.

## Context
The base-game board has a fixed topology, so a flat vector with an MLP is a reasonable first agent. A graph neural network (GNN) can share weights across the board and exploit its 12 rotations and reflections, and I want to learn GNNs later. I want the engine and Gym env stable while the model changes.

## Decision
The engine and Gym wrapper expose a **structured observation**: separate arrays for vertices, edges and hexes, adjacency lists, and the public and private player information (own hand visible, opponents' hands hidden). A thin `flatten()` turns it into a vector for the first MLP agents. A GNN encoder consumes the structured form later. Use symmetry augmentation (x12) regardless of encoder.

## Options considered
- **Structured observation plus `flatten()` (chosen):** MLP now, GNN later with no engine change.
- **Flat vector only:** simplest, but swapping to a GNN later would require re-deriving the structure and changing the env.
- **GNN from the start:** best long-term fit, but adds learning overhead before there is a baseline to compare against.
- **Grid or image-like encoding for a CNN:** hex boards map awkwardly onto grids.

## Consequences
- Good: the model can change without touching the engine; the structured form is also useful for rationale generation and debugging.
- Bad: a little more upfront design in the observation code, and the flat and graph paths both need tests.

## Revisit when
MLP agents plateau in Phase 5, or when Phase 6 starts the GNN work, or if observation encoding becomes a measurable bottleneck.
