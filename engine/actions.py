"""Actions a player can take, and (later) their flat integer encoding.

Each action kind is a frozen dataclass; `Action` is the union of all kinds.
This mirrors a Rust enum, so the port can match on it exhaustively.

Actions are plain data: they never name the acting player (the state knows who
acts) and never validate themselves. Legality is decided only by
`legal_actions`; `step` rejects anything else.

The flat id encoding and legality mask for RL arrive in Week 6 (ADR 0005).
"""

from dataclasses import dataclass

from engine.types import EdgeId, HexId, Offer, PlayerId, Resource, VertexId

# --- Turn -------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class RollDice:
    """Roll both dice; triggers production or 7 resolution."""


@dataclass(frozen=True, slots=True)
class EndTurn:
    """End the active player's turn."""


# --- Building (also used for free placements in setup and Road Building) ----


@dataclass(frozen=True, slots=True)
class BuildRoad:
    edge: EdgeId


@dataclass(frozen=True, slots=True)
class BuildSettlement:
    vertex: VertexId


@dataclass(frozen=True, slots=True)
class BuildCity:
    vertex: VertexId


@dataclass(frozen=True, slots=True)
class BuyDevCard:
    pass


# --- Robber -----------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class DiscardOne:
    """Discard one card after a 7; repeated until the player has discarded enough."""

    resource: Resource


@dataclass(frozen=True, slots=True)
class MoveRobber:
    """Move the robber and steal from `victim` (None if nobody can be stolen from)."""

    hex: HexId
    victim: PlayerId | None


# --- Development cards (victory point cards are never played) ---------------


@dataclass(frozen=True, slots=True)
class PlayKnight:
    """Followed by MoveRobber."""


@dataclass(frozen=True, slots=True)
class PlayRoadBuilding:
    """Followed by up to two free BuildRoad actions."""


@dataclass(frozen=True, slots=True)
class PlayYearOfPlenty:
    first: Resource
    second: Resource


@dataclass(frozen=True, slots=True)
class PlayMonopoly:
    resource: Resource


# --- Bank / harbor trade ----------------------------------------------------


@dataclass(frozen=True, slots=True)
class BankTrade:
    """Trade `give` for one `get`; the ratio (4:1, 3:1, 2:1) follows from harbors."""

    give: Resource
    get: Resource


# --- Domestic trade (docs/trade-protocol.md section 4) ----------------------


@dataclass(frozen=True, slots=True)
class ProposeTrade:
    offer: Offer


@dataclass(frozen=True, slots=True)
class AcceptTrade:
    pass


@dataclass(frozen=True, slots=True)
class RejectTrade:
    pass


@dataclass(frozen=True, slots=True)
class CounterTrade:
    """A counter-offer from the responder's point of view (they give `offer.give`)."""

    offer: Offer


@dataclass(frozen=True, slots=True)
class ConfirmTrade:
    """Execute the trade with `responder` (absolute seat) at their accepted or countered terms."""

    responder: PlayerId


@dataclass(frozen=True, slots=True)
class CancelTrade:
    pass


type Action = (
    RollDice
    | EndTurn
    | BuildRoad
    | BuildSettlement
    | BuildCity
    | BuyDevCard
    | DiscardOne
    | MoveRobber
    | PlayKnight
    | PlayRoadBuilding
    | PlayYearOfPlenty
    | PlayMonopoly
    | BankTrade
    | ProposeTrade
    | AcceptTrade
    | RejectTrade
    | CounterTrade
    | ConfirmTrade
    | CancelTrade
)
