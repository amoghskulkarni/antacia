# Flat Action List vs Factored Heads # 0005: Flat action list with a bounded trade subset

Status: Accepted (2026-10-20)

## Context
RL with action masking is simplest with a fixed, enumerated action space. Catan actions are structured (placements, robber moves, trades), and trades are open-ended in principle. I want open-ended trades for humans and the chat layer, but the first agents need something tractable.

## Decision
The RL interface uses a **fixed flat list of action ids** with legality masks from `legal_actions(state)`. The **engine accepts any valid trade offer**; the flat list enumerates only a **bounded subset**, set by `rl_max_cards_per_side`. Counting offers with non-empty sides, no shared resource type, and up to N cards per side gives 230 offers at N=2 and 1,170 at N=3 (verified by brute-force enumeration). Details: `docs/trade-protocol.md` section 7.

## Options considered
- **Flat list with a bounded trade subset (chosen):** simple, works with off-the-shelf masked PPO.
- **Factored or autoregressive heads** (action type, then location; or "what to give", then "what to ask"): handles larger action spaces and bigger offers, but more complex to train.
- **Parametric or continuous action outputs for offers:** flexible, but awkward with masking and discrete rules.
- **Flat list over all possible offers:** the space grows quickly with the card cap and mostly wastes capacity.

## Consequences
- Good: easy to implement and debug; legality masks keep illegal moves out; humans and bots can still make offers outside the RL subset.
- Bad: the bot cannot propose offers outside the subset; a large flat softmax may learn slowly.

## Revisit when
Phase 5 begins, when the flat softmax learns poorly, or when bots need larger offers than the cap allows.
