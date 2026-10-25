# 0001: Python engine first, Rust port later

Status: Accepted (2026-10-20)

## Context
Training needs millions of engine steps, so engine speed will eventually matter. Right now, development speed and correctness matter more, and I am confident in Python (some Rust experience) and want to learn Rust properly through this project. The engine is the hot path; the server mostly shuffles a few messages per second per game.

## Decision
Write the engine in Python first. It is the **reference implementation**. Later, port it to a Rust crate that is (1) exposed to Python through PyO3/maturin for training and (2) used directly by a Rust server. The Python engine stays as the oracle. The port is validated by language-neutral golden replays (`tests/conformance/`) plus differential testing (same random games through both engines, compare states).

## Options considered
- **A. Rust engine via PyO3, shared with a Rust server (chosen, staged).** One rules implementation for training and serving, fast in-process calls, no network in the hot path.
- **B. Rust server only, engine stays in Python.** Training gets no faster. The server would need an embedded interpreter, IPC to a Python process, or a second rules implementation that must be kept in sync.
- **C. TypeScript engine shared with the React client.** Awkward for RL tooling and a Python training loop.
- **D. Python forever.** Simplest, but caps self-play throughput.

## Consequences
- Good: fast iteration now; the conformance suite defines correct behavior independent of language; Rust learning has a concrete target and a test oracle.
- Bad: two implementations for a period; the engine must avoid Python-only idioms; the golden replay format must be language-neutral from day one.

## Revisit when
The steps/sec benchmark (Week 7) or Phase 5 profiling shows the engine is the training bottleneck, or the project gains contributors who prefer a different split.
