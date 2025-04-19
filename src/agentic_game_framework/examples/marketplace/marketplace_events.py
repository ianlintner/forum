"""
Marketplace Events for Agentic Game Framework.

This module defines the domain-specific events for the marketplace domain,
such as trade events, price change events, etc.
"""

from typing import Dict, Optional

from ...events.base import BaseEvent


class TradeEvent(BaseEvent):
    """
    Event representing a trade between agents.
    
    A trade event occurs when one agent gives items to another agent
    in exchange for other items or currency.
    
    Attributes:
        items_given: Dictionary of items given by the source agent
        items_received: Dictionary of items received by the source agent
    """
    
    def __init__(
        self,
        source: str,
        target: str,
        items_given: Dict[str, int],
        items_received: Dict[str, int]
    ):
        """
        Initialize a new trade event.
        
        Args:
            source: ID of the agent initiating the trade
            target: ID of the agent receiving the trade offer
            items_given: Dictionary of item IDs to quantities given by source
            items_received: Dictionary of item IDs to quantities requested by source
        """
        super().__init__(
            event_type="trade",
            source=source,
            target=target,
            data={
                "items_given": items_given,
                "items_received": items_received,
                "relationship_impact": 0.05,  # Trading is generally positive
                "participants": [source, target]
            }
        )


class PriceChangeEvent(BaseEvent):
    """
    Event representing a change in item price.
    
    A price change event occurs when a merchant changes the price
    of an item they are selling.
    
    Attributes:
        item_id: ID of the item whose price is changing
        old_price: Previous price of the item
        new_price: New price of the item
    """
    
    def __init__(
        self,
        source: str,
        item_id: str,
        old_price: float,
        new_price: float,
        target: Optional[str] = None
    ):
        """
        Initialize a new price change event.
        
        Args:
            source: ID of the agent changing the price
            item_id: ID of the item whose price is changing
            old_price: Previous price of the item
            new_price: New price of the item
            target: Optional target agent (e.g., for targeted discounts)
        """
        super().__init__(
            event_type="price_change",
            source=source,
            target=target,
            data={
                "item_id": item_id,
                "old_price": old_price,
                "new_price": new_price,
                "percent_change": (new_price - old_price) / old_price if old_price > 0 else 0,
                "is_increase": new_price > old_price
            }
        )


class ItemListingEvent(BaseEvent):
    """
    Event representing an item being listed for sale.
    
    An item listing event occurs when a merchant makes an item
    available for purchase in the marketplace.
    
    Attributes:
        item_id: ID of the item being listed
        quantity: Quantity of the item available
        price: Price per unit of the item
    """
    
    def __init__(
        self,
        source: str,
        item_id: str,
        quantity: int,
        price: float,
        target: Optional[str] = None
    ):
        """
        Initialize a new item listing event.
        
        Args:
            source: ID of the agent listing the item
            item_id: ID of the item being listed
            quantity: Quantity of the item available
            price: Price per unit of the item
            target: Optional target agent (e.g., for exclusive offers)
        """
        super().__init__(
            event_type="item_listing",
            source=source,
            target=target,
            data={
                "item_id": item_id,
                "quantity": quantity,
                "price": price,
                "total_value": quantity * price
            }
        )


class NegotiationEvent(BaseEvent):
    """
    Event representing a negotiation between agents.
    
    A negotiation event occurs when agents discuss terms of a
    potential trade or business deal.
    
    Attributes:
        proposal: Details of the negotiation proposal
        is_counter: Whether this is a counter-proposal
    """
    
    def __init__(
        self,
        source: str,
        target: str,
        proposal: Dict[str, any],
        is_counter: bool = False,
        previous_proposal_id: Optional[str] = None
    ):
        """
        Initialize a new negotiation event.
        
        Args:
            source: ID of the agent making the proposal
            target: ID of the agent receiving the proposal
            proposal: Details of the negotiation proposal
            is_counter: Whether this is a counter-proposal
            previous_proposal_id: ID of the previous proposal (if counter)
        """
        super().__init__(
            event_type="negotiation",
            source=source,
            target=target,
            data={
                "proposal": proposal,
                "is_counter": is_counter,
                "previous_proposal_id": previous_proposal_id,
                "relationship_impact": 0.02,  # Negotiating has a small positive impact
                "participants": [source, target]
            }
        )


class BusinessDealEvent(BaseEvent):
    """
    Event representing a business deal between agents.
    
    A business deal event occurs when agents establish a longer-term
    business relationship with specific terms.
    
    Attributes:
        deal_id: Unique identifier for the deal
        terms: Terms of the business deal
    """
    
    def __init__(
        self,
        source: str,
        target: str,
        deal_id: str,
        terms: Dict[str, any]
    ):
        """
        Initialize a new business deal event.
        
        Args:
            source: ID of the agent proposing the deal
            target: ID of the agent accepting the deal
            deal_id: Unique identifier for the deal
            terms: Terms of the business deal
        """
        super().__init__(
            event_type="business_deal",
            source=source,
            target=target,
            data={
                "deal_id": deal_id,
                "terms": terms,
                "relationship_impact": 0.15,  # Business deals have a significant positive impact
                "participants": [source, target]
            }
        )


class DealBreachEvent(BaseEvent):
    """
    Event representing a breach of a business deal.
    
    A deal breach event occurs when an agent fails to fulfill
    their obligations in a business deal.
    
    Attributes:
        deal_id: ID of the breached deal
        breach_type: Type of breach
        severity: Severity of the breach (0.0-1.0)
    """
    
    def __init__(
        self,
        source: str,
        target: str,
        deal_id: str,
        breach_type: str,
        severity: float = 0.5
    ):
        """
        Initialize a new deal breach event.
        
        Args:
            source: ID of the agent breaching the deal
            target: ID of the affected agent
            deal_id: ID of the breached deal
            breach_type: Type of breach
            severity: Severity of the breach (0.0-1.0)
        """
        super().__init__(
            event_type="deal_breach",
            source=source,
            target=target,
            data={
                "deal_id": deal_id,
                "breach_type": breach_type,
                "severity": max(0.0, min(1.0, severity)),
                "relationship_impact": -0.2 * severity,  # Breaches damage relationships
                "participants": [source, target]
            }
        )


class MarketTrendEvent(BaseEvent):
    """
    Event representing a market-wide trend.
    
    A market trend event affects multiple items and agents
    in the marketplace, such as inflation or scarcity.
    
    Attributes:
        trend_type: Type of market trend
        affected_items: Items affected by the trend
        impact: Impact of the trend on prices (multiplier)
    """
    
    def __init__(
        self,
        trend_type: str,
        affected_items: Dict[str, float],
        impact: float,
        source: Optional[str] = None,
        target: Optional[str] = None
    ):
        """
        Initialize a new market trend event.
        
        Args:
            trend_type: Type of market trend
            affected_items: Dictionary of item IDs to impact multipliers
            impact: Overall impact of the trend on prices (multiplier)
            source: Optional source agent (e.g., for agent-caused trends)
            target: Optional target agent (e.g., for targeted trends)
        """
        super().__init__(
            event_type="market_trend",
            source=source,
            target=target,
            data={
                "trend_type": trend_type,
                "affected_items": affected_items,
                "impact": impact,
                "is_positive": impact > 1.0
            }
        )