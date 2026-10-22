### Pydantic: When, why, how 

Pydantic validation is slow for objects created millions of times. I put this in `CLAUDE.md` as a rule: use frozen dataclasses or tuples for the hot path of the engine (GameState, Action), and Pydantic at the boundaries (API schemas, config, replay logs). This also makes the later Rust port closer to a 1:1 translation.