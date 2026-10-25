# Decision index

One ADR per decision that is costly to reverse or likely to be questioned. Open only the one you need. Never delete an ADR; supersede it with a new one and update its status.

| #    | Title                                          | Status   | One-line summary                                                                 |
| ---- | ---------------------------------------------- | -------- | -------------------------------------------------------------------------------- |
| 0001 | Python engine first, Rust port later           | Accepted | Python is the reference engine; port to a PyO3 crate validated by golden replays |
| 0002 | Immutable copy-on-step game state              | Accepted | `step()` returns a new state; revisit if steps/sec is too low                    |
| 0003 | Turn-synchronous trading                       | Accepted | Active player only; real-time negotiation is a server concern                    |
| 0004 | Pydantic at the boundaries only                | Proposed | Frozen dataclasses in the engine; Pydantic for APIs, config, logs                |
| 0005 | Flat action list with a bounded trade subset   | Accepted | Fixed enumerated ids plus masks; engine accepts any valid offer                  |
| 0006 | Structured observation with a flatten function | Proposed | MLP now, GNN-ready later                                                         |

## ADR Template

```markdown
# NNNN: Title

Status: Proposed | Accepted | Superseded by NNNN (date)

## Context

## Decision

## Options considered

## Consequences

## Revisit when
```
