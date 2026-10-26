# General architecture 

```
TRAINING / EVALUATION (local, RTX 3080)
 ┌──────────────┐   obs/mask   ┌─────────────┐  step()  ┌──────────┐
 │ RL trainer   │◄────────────►│  Gym env    │◄────────►│ Engine   │
 │ (PPO, league)│   actions    │ (wrapper)   │          │ (rules)  │
 └──────┬───────┘              └─────────────┘          └──────────┘
        │ checkpoints
        ▼
 ┌──────────────┐   ONNX/TorchScript export
 │ Model store  │──────────────────────────┐
 └──────────────┘                          │
                                           ▼
LIVE PLAY (cloud, CPU/small GPU)           │
 ┌────────────┐ WebSocket ┌──────────────┐ │   ┌──────────────┐
 │ React web  │◄─────────►│ Game server  │ │   │ Bot runtime  │
 │ client     │  intents/ │ (FastAPI →   │◄┴──►│ (inference + │
 └────────────┘  state    │  Rust later) │     │  search)     │
                          │  ┌────────┐  │     └──────┬───────┘
                          │  │ Engine │  │            │ events
                          │  └────────┘  │     ┌──────▼───────┐
                          └──────┬───────┘     │ Chat/LLM     │
                                 │             │ layer (later)│
                          ┌──────▼───────┐     └──────────────┘
                          │ Postgres     │  accounts, games, replay logs
                          └──────────────┘
```

## Software components 

| Component      | Role                                                                                                              | Used when                                         |
| -------------- | ----------------------------------------------------------------------------------------------------------------- | ------------------------------------------------- |
| Engine         | Pure rules: `legal_actions`, `step`, `scoring`. Deterministic.                                                    | Everywhere: training, server, tests               |
| Gym env        | Adapts the engine to RL: observation encoding, action masks, rewards, vectorization.                              | Training and evaluation only; never in production |
| RL trainer     | PPO/self-play loop with a league, on your GPU.                                                                    | Offline, local                                    |
| Model store    | Checkpoints, exported inference models, Elo records.                                                              | Between training and serving                      |
| Bot runtime    | Loads a model, turns the engine state into an observation, returns an action (plus optional search).              | Local eval (Phase 2+) and live play on the server |
| Game server    | Authoritative: owns an engine instance per game, validates every action, handles seats/humans/bots, logs replays. | Live play                                         |
| Web client     | Rendering and input only; no rules logic.                                                                         | Live play                                         |
| Chat/LLM layer | Banter, parsing trade talk into protocol messages.                                                                | Later phase, attached to the server               |
| Postgres       | Accounts, games, replays.                                                                                         | Hosting phase                                     |

## Repo structure (Phase 1)

```
antacia/
├── CLAUDE.md
├── docs/
│   ├── rules-spec.md          # your authoritative rules + edge cases
│   ├── trade-protocol.md
│   ├── architecture.md
│   └── decisions/             # short ADRs (why Python first, Rust later, etc.)
├── engine/                    # python package
│   ├── topology.py            # static geometry: coordinates, dense ids, adjacency, harbor slots
│   ├── board.py               # per-game layout: terrains, tokens, harbors; ASCII printer
│   ├── symmetry.py            # the 12 board symmetries applied to boards and actions
│   ├── state.py               # GameState
│   ├── actions.py             # action enum + encoding
│   ├── rules/                 # setup, production, build, robber, devcards, trade, scoring
│   ├── rng.py                 # seeded RNG, chance events
│   └── game.py                # step(), legal_actions(), is_terminal()
├── gym_env/
├── bots/                      # random, greedy, heuristic
├── eval/                      # tournament + Elo/TrueSkill harness
├── tests/
│   ├── unit/
│   ├── property/
│   └── conformance/           # JSON golden replays (shared with future Rust port)
├── server/                    # stubs until Phase 3/4
├── web/                       # stubs until Phase 3/4
├── .claude/
|   ├── unit/commands/  
|   └── agents/
└── pyproject.toml             # uv + ruff + mypy + pytest + hypothesis
```

## Practical points 

Practical points:

- The **Gym env and server both wrap the same engine**, so a bot can’t “know” anything different in training than in production.
- Inference is the only cloud-GPU-ish piece, and for a policy network of this size a **CPU** is probably enough. TBD later after measuring.
- Because the server is authoritative, anyone who plugs in a custom bot over the API gets the same rules enforcement. This is what would make “people train their own bots and pit them against each other” work.