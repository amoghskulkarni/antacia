# 0011: Setup placements reuse the build actions

Status: Accepted (2026-10-25)

## Context
In the setup phase each player places two settlements and two roads for free, in snake order, under slightly different legality rules: no road connection is needed for the settlement, and the road must touch the settlement just placed. The same pieces are built normally later, for a cost. Free roads also come from the Road Building card. The action set (ADR 0005) should stay small and the same from every seat.

## Decision
Setup uses the normal `BuildSettlement(vertex)` and `BuildRoad(edge)` actions. The **phase in `GameState` decides** whether a placement is free and which legality rules apply. `legal_actions` encodes the setup rules; there are no setup-only action kinds. The Road Building card's free roads work the same way.

## Options considered
- **Reuse the build actions (chosen):** fewer action kinds and RL ids; one place (the legality code) holds every rule difference; a policy sees "a settlement on vertex v" as the same thing in both phases.
- **Separate `PlaceInitialSettlement` / `PlaceInitialRoad`:** makes the phase explicit in the action and the log, but duplicates ids (54 + 72 more) and splits closely related code.

## Consequences
- Good: smaller action space; the replay log reads naturally; the free-placement logic is shared with Road Building.
- Bad: an action alone doesn't say whether it was free; you need the state's phase to interpret it. Legality code must branch on the phase carefully, and tests must cover setup vs normal play for both actions.

## Revisit when
- The RL work in Phase 5 wants a separate setup policy or head (common in strong Catan agents, since opening placement is a different problem). That can be done in the env by phase without changing the engine, so only revisit the engine if it can't.
- Setup legality code becomes hard to follow because of the phase branching.
