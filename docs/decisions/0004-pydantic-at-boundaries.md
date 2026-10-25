# 0004: Pydantic at the boundaries only

Status: Proposed (2026-10-21). Review and mark Accepted or revise.

## Context
Pydantic is part of the chosen toolchain and is excellent for validating external data. The engine, however, creates and copies state objects millions of times during training, so per-object validation and construction overhead matters. A Rust port is also easier if engine types are plain data.

## Decision
Inside the engine, use frozen dataclasses (with slots) and tuples. Use Pydantic only at the boundaries: API request/response schemas, configuration, and replay/log serialization. Explicit conversion functions sit between the two.

## Options considered
- **Plain frozen dataclasses in the engine, Pydantic at the edges (chosen).**
- **Pydantic everywhere:** one model family and automatic validation, but validation cost lands on the hot path. The actual overhead has not been measured here.
- **Plain dataclasses everywhere with hand-written validation at the edges:** least dependency, but loses Pydantic's schema generation for the API.
- **attrs or msgspec for the engine types:** possible alternatives; not evaluated.

## Consequences
- Good: faster hot path, simple types, closer 1:1 mapping to Rust structs, validation exactly where untrusted data enters.
- Bad: conversion code at the boundary, and two kinds of model types for contributors to learn.

## Revisit when
A benchmark shows Pydantic overhead is negligible for the engine's state, or serialization needs make direct Pydantic models for engine types clearly simpler.
