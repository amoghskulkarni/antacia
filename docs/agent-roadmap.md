# Agent roadmap (Phases 5 and 6, plus the conversation layer)

How Antacia's bots will be built, from baselines to a strong, human-feeling player. Companion to `project-context.md` (decisions) and `trade-protocol.md` (trade rules). Cost figures are rough and must be re-checked before relying on them.

## 0. Why Catan is hard for RL
- **4 players, non-zero-sum:** two-player self-play theory doesn't transfer cleanly.
- **Stochastic:** dice and development-card draws.
- **Hidden information:** opponents' hands and unplayed development cards.
- **Large, structured action space:** placements, robber moves, trades.
- **Long games with sparse reward.**
- **Trading and negotiation:** the social part, and where current bots are weakest. This is Antacia's differentiator.

## 1. Design principle
The **decision layer (RL policy + search) makes every game move**. An LLM, if used, only talks: it phrases the bot's decisions and parses humans' words. Every parsed intent is validated against `legal_actions` before it reaches the engine.

```
Conversation layer (LLM)        banter, parsing table talk, explanations
Persona / intent layer          personality, mood, grudges, "tells"
Decision layer (RL + search)    the actual moves, including trade decisions
Game engine (authoritative)     rules, legality, determinism
```

## 2. Phase 5: Agent v1 (about 2-4 weeks of effort)

### 5a. Baselines and benchmark ladder
- Opponent ladder: Random -> Greedy (immediate VP or production) -> Weighted heuristic (pip count, resource diversity, ports, road potential) -> plain MCTS.
- Evaluate with **seat rotation** and 1,000+ games per matchup. Seat advantage and 4-player noise make small samples misleading.
- The ladder is the regression test for every later agent.

### 5b. ISMCTS baseline
- Hidden information: sample ("determinize") plausible hidden states consistent with observations, run MCTS on each, aggregate visit counts. ISMCTS does this inside a single tree over information sets.
- Dice and card draws are **chance nodes**: sample outcomes, or use expectation at shallow depth.
- Use heuristic rollouts and a depth cap with a value-function cutoff. Fully random Catan rollouts are long and noisy.
- Expected to beat simple heuristics, but slow per move, which matters for hosting cost.

### 5c. PPO with action masking
- Network: shared trunk over the observation, policy head over the flat action list (illegal actions masked), value head.
- Tools: CleanRL (readable single-file) or Stable-Baselines3-contrib `MaskablePPO`.
- The flat action list includes the bounded trade subset from `trade-protocol.md` section 7 (230 offers at a 2-card cap, 1,170 at 3). Revisit **factored/autoregressive heads** here (pick action type, then location; or "what to give" then "what to ask") if the flat softmax becomes a problem.
- Reward: win/loss plus small VP-difference shaping, **annealed toward zero**. Heavy shaping produces bots that grab early VP and lose long-term.
- Train first against the heuristic ladder (stable curriculum), not pure self-play.

### 5d. Self-play league
- Pure 4-player self-play can collapse into degenerate strategies. Use a **league**: current policy plus a pool of past checkpoints and fixed baselines, sampled per game.
- Track **TrueSkill** (native multiplayer) or Elo against the fixed ladder to catch regressions.
- Later add **exploiter agents**: bots trained only to beat the current best, to expose weaknesses.

### 5e. Human data
- Log every human game (seed + action sequence, including all trade offers).
- Uses: evaluation (does the bot agree with strong human moves?), **behavior cloning** warm-starts, and **style modeling** for human-like play.

**Exit criteria:** consistently beats the heuristic and ISMCTS baselines at a statistically meaningful rate, and decides in about 1 second or less per move on CPU.

## 3. Phase 6: Agent v2 (open-ended)

### 6a. AlphaZero-style search with a learned network
- Replace random rollouts with a **policy prior** (guides expansion) and a **value head** (replaces rollouts).
- Catan adaptations:
  - **Chance nodes:** sampling or expectation (Stochastic MuZero is the reference).
  - **Hidden info:** determinize over opponents' hidden cards using a belief model (6d).
  - **Multiplayer values:** value head outputs one win probability per player; backups use the component of the player to move (max^n style).
- Train by generating search-guided self-play and fitting the net to visit-count policies and outcomes.

### 6b. Graph neural network encoder
Where the encoding choice matters:
- **Flat/MLP:** one big vector; each position has its own weights, so "good spot at vertex 17" and "good spot at vertex 18" are learned separately, and adjacency is not built in.
- **GNN:** the board is a graph (vertices, edges, hexes). Message passing with shared weights learns "what a good neighborhood looks like" once and applies it everywhere. Gives sample efficiency and handles the board's 12 symmetries (rotations and reflections) almost for free; an MLP needs augmentation.
- **Variable topology** (expansions, other boards) breaks a flat vector but not a GNN. Out of scope for now.

**Decision:** the base-game board has a fixed topology, so start with a flat MLP. The engine exposes a **structured observation** (separate vertex, edge and hex arrays plus adjacency) with a thin `flatten()`, so adopting a GNN later is a model change only. Learning a GNN is a deliberate Phase 6 learning goal. Use symmetry augmentation (x12) regardless.

### 6c. Imperfect-information methods (optional, advanced)
ReBeL and Student of Games combine search with belief states and fit hidden-information games, but are heavy and mostly proven in two-player settings. For 4-player Catan, determinization plus a learned belief model is the pragmatic route first.

### 6d. Belief modeling
A small model predicts opponents' hidden hands from public history (builds, trades, what they could have built but didn't). It strengthens search and also makes the bot reason like a human ("she's holding wheat").

### 6e. Trading and negotiation
The hardest part, and the project's main goal. Plan:
1. **Engine level:** trades are discrete protocol actions (`trade-protocol.md`), trained by RL. Log every offer, even rejected ones, as training data.
2. **Agent level:** a trade policy that values offers (accept, reject, counter) using the value head and belief model, and proposes offers that benefit it without helping the leader.
3. **Language level:** the LLM phrases the agent's decision and parses humans' words into protocol messages.

## 4. Conversation layer (LLM)

### Is it necessary?
Not for a strong bot, but it is the biggest lever for the "real over-the-board game" feel, especially for trading.

### What the LLM does
1. **Speaks:** given a structured event, the bot's persona and mood, it produces a short in-character line.
2. **Understands chat:** "I'll give you 2 brick for 1 wheat" becomes `ProposeTrade(give={brick:2}, want={wheat:1})`; "stop blocking me" becomes a social signal.
3. **Negotiates:** converts an offer into a query to the agent (accept, reject, counter), then phrases the reply naturally.
4. **Explains (optional):** narrates the agent's structured rationale ("why did you put the robber there?").

### Structured rationale, not free-form chain-of-thought
The agent outputs its move plus **machine-readable reasons**: top-k candidate moves with values, search visit counts, and engine-computed features (pips gained, port access, blocks Player 3's road). The LLM turns this structure into a sentence. It does not re-derive the decision.

An optional extra: the LLM may pick among the agent's top-k strong moves based on persona and social context. The agent guarantees every option is strong; the LLM adds variety.

### Guardrails
- Validate every LLM-derived intent against `legal_actions`.
- Strict JSON schemas and a fixed intent vocabulary.
- Never leak hidden information; only pass what a human at the table would know plus the bot's own private state.
- Cap message length and frequency to avoid spam.

### Human-feel details beyond chat
- **Think-time delays** scaled to decision difficulty, randomized.
- **Configurable imperfection** (temperature or skill level) plus human-like quirks.
- **Style cloning** from logged human games.
- **Personas:** aggressive trader, cautious builder, grudge-holder. Persona changes move selection (within a strong range) and chat style.
- **Emotion/state memory:** small structured state ("robbed 3 times by Player 2") fed to the LLM prompt.

### Cost implications (rough; verify current prices)
Per bot per game: about 20-60 utterances, each about 500-1,500 input tokens and 20-60 output tokens, so roughly 30k-90k input and 1-4k output tokens per game.

| Option | Approx. cost per game per bot | Notes |
|---|---|---|
| Small hosted model (cheap tier) | cents or less | Easiest, lowest ops |
| Self-hosted small open model (3B-8B, quantized) | near-zero marginal, but you pay for a GPU server | Ops burden; makes sense at volume |
| In-browser small model (WebGPU) | zero server cost | Quality and device support limits |

Ways to cut cost: **templates first** (canned lines for 70-80% of trivial moments), prompt caching for the persona and rules prefix, small models for banter and intent parsing, per-game and per-user token caps, and escalate to a larger model only when parsing fails.

The larger hosting cost is usually the **bot's search and inference compute**, not chat. Offer a lighter policy-only mode for casual games.

### Build order
1. Bot with **template chat plus think-time delays** (cheap, big UX win).
2. LLM **intent parser** for human chat and trade offers.
3. **Persona-driven banter and explanations.**
4. Belief models, style cloning, emotional memory.

## 5. Compute plan
- **Training:** local RTX 3080. No cloud training budget.
- **Inference:** cloud, CPU first. Policy networks of this size likely don't need a GPU; measure before deciding. Export to ONNX or TorchScript.
- Keep training and serving on the same engine via the Gym wrapper and the server, so bots see identical rules in both.

## 6. Open questions
- LLM choice: hosted API versus self-hosted open model (decide when Phase 5 completes).
- How strong should bots be by default? Add difficulty levels (search budget, temperature)?
- Whether to publish a bot-vs-bot API/protocol early to attract outside bot developers.
- GNN adoption timing: only if flat-MLP agents plateau, or as a deliberate learning project.