# 0016: Seat 0 always starts; seats are randomised outside the engine

Status: Accepted (2026-10-27)

## Context
The rulebook picks the starting player by a dice roll (highest roll starts). The engine needs a fixed rule for who acts first in setup and in the first turn. Turn order matters for fairness (first-player advantage) and for every replay, observation and rating.

## Decision
In the engine, **seat 0 always starts**, and turn order is seat order 0, 1, ..., N-1. Who sits in which seat is decided **outside the engine**: the server, eval harness and Gym env shuffle the seats for every game. The engine never rolls for the starting player.

## Options considered
- **Seat 0 starts, seats shuffled by the caller (chosen):** the engine has one fewer chance event and one fewer phase; "seat 0 = first player" holds in every replay and observation; seat rotation for fair ratings is the eval harness's job anyway.
- **Roll for first player in the engine:** matches the rulebook ritual, but adds an RNG draw and tie re-rolls before setup, and makes "who started" vary per seed. The outcome is the same as a random seat shuffle.

## Consequences
- Good: simpler engine and observations; the seat id itself tells you turn position.
- Bad: callers must remember to shuffle seats (or rotate them in tournaments), or seat 0 gets the first-player advantage every game. The server and eval harness need a test for this.

## Revisit when
- We support a house rule or variant where the starting player is chosen differently in the middle of a session (e.g. "loser of the last game starts").
