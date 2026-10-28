# Rules specification (base game, 3-4 players)

Source of truth for the engine. Fill in from your own copy of the official rulebook; this file records *decisions and edge cases*, not the rulebook's prose. Items marked VERIFY are my recollection of the standard rules and must be checked against the rulebook.

## 1. Components (VERIFIED)
- 19 hexes: 4 forest (lumber), 4 pasture (wool), 4 fields (grain), 3 hills (brick), 3 mountains (ore), 1 desert
- 18 number tokens: 2 and 12 once each; 3, 4, 5, 6, 8, 9, 10, 11 twice each
- 9 harbors: 4 generic 3:1, 5 resource-specific 2:1
- Per player: 5 settlements, 4 cities, 15 roads
- Resource cards: 19 per resource (bank supply)
- Development deck: 25 cards (14 knights, 5 victory points, 2 road building, 2 year of plenty, 2 monopoly)
- Setup variability: board layout, token placement, harbor placement, player order

## 2. Setup phase
- [x] Placement of settlements and roads - A settlement is placed on a vertex on the board, and a road is placed on the edge of the board
- [x] Placement order (snake order) - Each player places **a pair of 1 settlement and 1 road** (normal placement rules are to be honored) in the first-to-last (forward) order. Then all players place the second pair of 1 settlement and 1 road, this tie in the last-to-first (reverse) order 
- [x] Starting resources - Placement of the **second settlement** grants starting resources to each player. 1 resource per adjacent hex to the second settlement is given
- [x] Road placement rule ("Connection rule") - Road must be placed connected to the settlement (or "owned" vertex). In setup, the road must touch the settlement placed just before it (in round 2, not the first settlement or its road; ADR 0011)
- [x] Settlement placement rule ("Distance rule") - No two settlements (of any player, including of one's own) can be placed on the same edge. Consequently the same rule applies for the cities, as cities are upgraded settlements placed on the same spot (i.e. when placed, a city just replaces the settlement in question)
- [x] Beginner vs random layout (decision: both; `random` is the default, see ADR 0009)
- Encoding: setup placements use `BuildSettlement`/`BuildRoad`; the phase makes them free (ADR 0011)

## 3. Turn structure
- [ ] Order of phases: (optional dev card) -> roll -> production -> (trade/build/dev card in any order) -> end turn
- [ ] Exactly what may happen before the roll
- [ ] Resource shortage rule when the bank can't pay everyone (VERIFY)

## 4. Rolling a 7 and the robber
- [ ] Discard rule (threshold, how many, who chooses)
- [ ] Robber movement and stealing (who can be stolen from, random card)
- [ ] Knight card interaction
- Encoding: discards are one `DiscardOne(resource)` per card (ADR 0013); move + steal is one `MoveRobber(hex, victim)` (ADR 0012)

## 5. Building
- [ ] Costs (road, settlement, city, development card)
- [ ] Road connectivity, settlement distance rule, city upgrade
- [ ] Piece limits

## 6. Development cards
- [ ] One-per-turn rule and exceptions
- [ ] Cannot play a card on the turn it was bought (exception for victory points?)
- [ ] Each card's exact effect and edge cases

## 7. Special awards
- [ ] Longest Road: threshold, tie-breaking, how opponent settlements break a road, loops/branching
- [ ] Largest Army: threshold, tie-breaking
- [ ] When can the award change hands?

## 8. Trading (official rules)
- [ ] Domestic trade: who may trade with whom (only the active player with others?), who may trade with the bank
- [ ] Maritime trade ratios (4:1, 3:1, 2:1) and when harbors apply
- [ ] Are counter-offers allowed under the rulebook? (project decision: see trade-protocol.md)
- Encoding: offers are broadcast to all opponents; no targeted offers yet (ADR 0014)
- [ ] Can a player trade or build after rolling in any order?

## 9. Winning
- [ ] Victory point threshold and *when* it must be reached (on own turn?)
- [ ] Hidden victory point cards

## 10. Edge cases log (add as you find them)
| # | Situation | Decision | Test |
|---|-----------|----------|------|
| 1 | Desert on the token spiral | Skipped; the next hex takes the next letter (ADR 0009) | `tests/unit/test_board.py::test_spiral_skips_the_desert_without_losing_a_token` |
| 2 | Last seat in setup | Places both of its pairs back to back (snake order) | `tests/unit/test_setup.py::test_setup_follows_the_snake_order` |
| 3 | Distance rule against your own settlement | Applies: no settlement next to any settlement, own included | `tests/unit/test_setup.py::test_the_distance_rule_also_applies_to_your_own_settlements` |