### Turn-synchronous: The engine is a strict state machine and trade happens in ordered steps, always initiated by the active player.

1. Active player proposes `Offer(give, want)`.
2. Each other player responds in seat order: `Accept`, `Reject`, or `Counter(give, want)`.
3. The active player then picks one outcome: accept a response (either the original offer or the counter), or cancel.
4. The engine executes the swap atomically.

Even if bots “think in parallel”, the engine only sees a well-defined sequence of events. Same seed plus same actions always gives the same game, which is what RL training and replays need. This matches the official rule that only the active player trades with others.

### Real-time simultaneous negotiation (later phases): People talk and respond at the same time, and several bots and humans may react within the same second. 

This introduces timeouts, race conditions (two players “accept” together), and an ordering problem. It’s a **server concern**: the server collects events, orders them (first valid accept wins, a response timer closes the window), and feeds the engine the same ordered events as before. If the engine is event-driven and deterministic in the earlier stages, real-time is an upgrade to the server and UI later, not an engine rewrite.