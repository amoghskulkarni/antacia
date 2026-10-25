# Project context and decision log

Distilled from the planning conversation (Oct 2026). Lives at `docs/project-context.md` and is imported from `CLAUDE.md`. Update it when a decision changes; record the reasoning for big decisions as an ADR in `docs/decisions/`.

## About me (the developer)
- Confident in Python (complex projects), have used FastAPI. Some Rust (built an Actix microservice).
- Broad but shallow ML/RL knowledge. No GNN experience yet; want to learn.
- Hobby project, 10-12 hours/week, over months. Goals: learn software development, project management, open source, RL/ML/AI, hosting, maintenance and scaling.
- I want to stay actively in the coding loop and review important code line by line.

## Vision
- A Catan-compatible base-game engine (3-4 players, official rulebook, strictly) with:
  - a Python RL gym for training bots (self-play and vs humans),
  - a web app where humans play with humans and bots in real time, with accounts.
- Trading is the differentiator. Strong bots today trade badly; I want human-bot and multi-bot trading to feel like a natural over-the-board conversation.
- Open-source both the gym and the web app so others can train their own bots and pit them against each other.
- Working name: Antacia (an anagram of "Catan AI"). Branding may differ from Catan, but it must be clear it's the same game.

## Tech decisions
| Area | Decision |
|---|---|
| Engine v1 | Python, pure functions, deterministic given (seed, actions) |
| State model | Immutable, copy-on-step: `step(state, action) -> new_state` |
| Hot-path types | Frozen dataclasses / tuples. Pydantic only at boundaries (API schemas, config, replay logs) |
| Tooling | uv, ruff, mypy (strict on `engine/`), Pydantic, pytest, hypothesis |
| Server v1 | FastAPI + WebSockets, server-authoritative |
| Frontend | React; no rules logic in the client |
| Rust plan | Option (a): later port the engine to a Rust crate, expose to Python with PyO3/maturin for training, and build the Rust server on the same crate. Python engine stays as the reference oracle. Port validated by golden replays + differential testing |
| Action space | Fixed flat enumerated action list with legality masks for now; revisit factored/autoregressive heads in Phase 5 |
| Trades | Engine accepts open-ended offers. RL action list enumerates a bounded subset (e.g. <=3 cards per side) |
| Observation | Structured arrays (vertices, edges, hexes + adjacency) with a flatten function, so an MLP works now and a GNN can be swapped in later |
| Training compute | Local RTX 3080. Cloud only for inference in production |
| Game logs | Every game stored as seed + action sequence (incl. all trade offers, even rejected ones) |

## Trading protocol (v1: turn-synchronous)
- Only the active player may initiate a trade, and only during their own turn (after rolling), per official rules.
- Flow: active player `Propose(give, want)` -> each other player responds in seat order with `Accept` / `Reject` / `Counter(give, want)` -> active player picks one response, makes a new offer (bounded number of rounds), or cancels -> engine executes the swap atomically.
- The engine sees a strictly ordered event sequence, so games are deterministic and replayable.
- v2 (later): real-time simultaneous negotiation is a *server* feature (timers, first-valid-accept ordering, race handling). The engine stays the same.
- Later: an LLM chat layer turns natural-language table talk into these protocol messages and back. The LLM never decides moves; the RL/search agent does, and every LLM-extracted intent is validated against `legal_actions`.

## Architecture
- `engine/`: rules (used everywhere).
- `gym_env/`: RL wrapper (training/eval only, never in production).
- `bots/`: agents; take an Observation, return an Action.
- `eval/`: tournaments, Elo/TrueSkill with seat rotation.
- `server/`: owns one engine per game, validates every action, seats humans/bots, logs replays.
- `web/`: renders state, sends intents.
- `tests/conformance/`: language-neutral golden replays.
- Later: model store (checkpoints, ONNX exports), bot runtime service, chat/LLM layer, Postgres.

## Roadmap
- Phase 0: scoping and rules spec
- Phase 1: core engine (current)
- Phase 2: Gym/PettingZoo env, baseline bots, eval harness
- Phase 3: FastAPI server
- Phase 4: React client
- Phase 5: agent v1 (ISMCTS baseline, MaskablePPO, self-play league, human data)
- Phase 6: agent v2 (AlphaZero-style search with chance/hidden-info handling, GNN encoder, belief model, trading/negotiation)
- Phase 7: deployment (Docker, hosting, Postgres, bot inference service)
- Later: Rust engine + server, real-time trading, LLM chat layer, personas and human-like behavior

## Phase 1 plan (10-12 hrs/week)
| Week | Focus | Done when |
|---|---|---|
| 0 | Repo skeleton, uv, ruff/mypy/pytest CI, CLAUDE.md, action dataclasses, board + RNG ADRs (0007-0010), fill rules-spec.md, pick name + license | CI green; spec sections 1-3 filled; ADRs 0007-0010 Accepted |
| 1 | Implement ADRs 0007-0010: board geometry, adjacency, harbors, seeded RNG and board generation (done early, in Week 0) | ASCII board printer; geometry and RNG property tests |
| 2 | GameState + setup phase | Random agent completes setup legally |
| 3 | Dice, production, building, robber, 7-discard | Full no-trade, no-dev-card random game finishes |
| 4 | Dev cards, Longest Road, Largest Army, win detection | Edge-case tests pass; invariants hold |
| 5 | Bank/harbor trades + player-trade protocol | Offer/accept/counter flows tested |
| 6 | Action list, masks, Gym env, golden replay format | 100k random games, zero invariant violations |
| 7 | Baseline bots, tournament harness, profiling | Elo ladder runs; steps/sec recorded |

## Open questions
- Final project name and license (MIT / Apache-2.0 / GPL).
- Exact bounds for the RL trade subset and max negotiation rounds per turn.
- Board and RNG decisions: drafted as ADRs 0007-0010 (Proposed), to be reviewed in Week 0.