"""
Business Relationships for Marketplace Domain.

This module defines the domain-specific relationship types for the marketplace domain,
such as business relationships, competitor relationships, and supplier relationships.
"""

from typing import Any, Dict, Optional

from ...events.base import BaseEvent
from ...relationships.base_relationship import BaseRelationship


class BusinessRelationship(BaseRelationship):
    """
    Relationship representing a business connection between agents.
    
    A business relationship represents a general commercial connection
    between two agents who regularly engage in trade with each other.
    
    Attributes:
        transaction_count: Number of transactions between the agents
        average_transaction_value: Average value of transactions
        last_transaction_time: Timestamp of the last transaction
    """
    
    def __init__(
        self,
        agent_a_id: str,
        agent_b_id: str,
        strength: float = 0.3,
        attributes: Optional[Dict[str, Any]] = None,
        relationship_id: Optional[str] = None
    ):
        """
        Initialize a new business relationship.
        
        Args:
            agent_a_id: ID of the first agent
            agent_b_id: ID of the second agent
            strength: Initial strength (-1.0 to 1.0)
            attributes: Additional relationship attributes
            relationship_id: Unique identifier (generated if not provided)
        """
        # Set default attributes if not provided
        if attributes is None:
            attributes = {}
        
        # Initialize business-specific attributes
        attributes.update({
            "transaction_count": 0,
            "average_transaction_value": 0.0,
            "last_transaction_time": None,
            "trust_level": strength * 0.5 + 0.5,  # Convert from [-1,1] to [0,1]
            "relationship_age": 0,
        })
        
        super().__init__(
            agent_a_id=agent_a_id,
            agent_b_id=agent_b_id,
            relationship_type="business",
            strength=strength,
            attributes=attributes,
            relationship_id=relationship_id
        )
    
    def update(self, event: BaseEvent) -> bool:
        """
        Update the relationship based on an event.
        
        Args:
            event: The event that might affect the relationship
            
        Returns:
            bool: True if the relationship was updated, False otherwise
        """
        # Check if event involves both agents
        if not self._event_involves_both_agents(event):
            return False
        
        updated = False
        
        if event.event_type == "trade":
            updated = self._handle_trade_event(event)
        elif event.event_type == "negotiation":
            updated = self._handle_negotiation_event(event)
        elif event.event_type == "business_deal":
            updated = self._handle_business_deal_event(event)
        elif event.event_type == "deal_breach":
            updated = self._handle_deal_breach_event(event)
        
        # Increment relationship age
        self.attributes["relationship_age"] += 1
        
        # Apply relationship decay over time
        if self.attributes["relationship_age"] % 10 == 0:
            # Slight decay every 10 updates
            self.update_strength(-0.01, "natural relationship decay")
        
        return updated
    
    def _handle_trade_event(self, event: BaseEvent) -> bool:
        """
        Handle a trade event between the agents.
        
        Args:
            event: The trade event
            
        Returns:
            bool: True if the relationship was updated
        """
        # Extract trade details
        items_given = event.data.get("items_given", {})
        items_received = event.data.get("items_received", {})
        
        # Calculate transaction value (simplified)
        transaction_value = sum(items_given.values()) + sum(items_received.values())
        
        # Update transaction count and average value
        self.attributes["transaction_count"] += 1
        
        # Update average transaction value
        count = self.attributes["transaction_count"]
        current_avg = self.attributes["average_transaction_value"]
        new_avg = ((count - 1) * current_avg + transaction_value) / count
        self.attributes["average_transaction_value"] = new_avg
        
        # Update last transaction time
        self.attributes["last_transaction_time"] = event.timestamp.timestamp()
        
        # Update relationship strength
        # Trades generally improve business relationships
        impact = event.data.get("relationship_impact", 0.05)
        self.update_strength(impact, "successful trade")
        
        # Update trust level
        trust_change = impact * 0.5  # Trust changes more slowly than relationship strength
        self.attributes["trust_level"] = min(1.0, max(0.0, self.attributes["trust_level"] + trust_change))
        
        return True
    
    def _handle_negotiation_event(self, event: BaseEvent) -> bool:
        """
        Handle a negotiation event between the agents.
        
        Args:
            event: The negotiation event
            
        Returns:
            bool: True if the relationship was updated
        """
        # Negotiations have a small positive impact
        impact = event.data.get("relationship_impact", 0.02)
        self.update_strength(impact, "negotiation")
        
        return True
    
    def _handle_business_deal_event(self, event: BaseEvent) -> bool:
        """
        Handle a business deal event between the agents.
        
        Args:
            event: The business deal event
            
        Returns:
            bool: True if the relationship was updated
        """
        # Business deals have a significant positive impact
        impact = event.data.get("relationship_impact", 0.15)
        self.update_strength(impact, "business deal established")
        
        # Update trust level
        trust_change = impact * 0.7  # Business deals significantly impact trust
        self.attributes["trust_level"] = min(1.0, max(0.0, self.attributes["trust_level"] + trust_change))
        
        # Store the deal ID
        if "active_deals" not in self.attributes:
            self.attributes["active_deals"] = []
        
        deal_id = event.data.get("deal_id")
        if deal_id:
            self.attributes["active_deals"].append(deal_id)
        
        return True
    
    def _handle_deal_breach_event(self, event: BaseEvent) -> bool:
        """
        Handle a deal breach event between the agents.
        
        Args:
            event: The deal breach event
            
        Returns:
            bool: True if the relationship was updated
        """
        # Deal breaches have a negative impact
        severity = event.data.get("severity", 0.5)
        impact = event.data.get("relationship_impact", -0.2 * severity)
        self.update_strength(impact, "deal breach")
        
        # Update trust level
        trust_change = impact * 1.5  # Breaches severely impact trust
        self.attributes["trust_level"] = min(1.0, max(0.0, self.attributes["trust_level"] + trust_change))
        
        # Remove the deal from active deals
        if "active_deals" in self.attributes:
            deal_id = event.data.get("deal_id")
            if deal_id and deal_id in self.attributes["active_deals"]:
                self.attributes["active_deals"].remove(deal_id)
        
        return True
    
    def _event_involves_both_agents(self, event: BaseEvent) -> bool:
        """
        Check if an event involves both agents in this relationship.
        
        Args:
            event: The event to check
            
        Returns:
            bool: True if both agents are involved
        """
        # Check direct involvement (source and target)
        if event.source == self.agent_a_id and event.target == self.agent_b_id:
            return True
        if event.source == self.agent_b_id and event.target == self.agent_a_id:
            return True
        
        # Check participants list if available
        participants = event.data.get("participants", [])
        if self.agent_a_id in participants and self.agent_b_id in participants:
            return True
        
        return False


class CompetitorRelationship(BaseRelationship):
    """
    Relationship representing competition between agents.
    
    A competitor relationship represents a competitive dynamic
    between two agents who sell similar items or target similar customers.
    
    Attributes:
        competing_items: List of items both agents sell
        market_share_difference: Difference in market share between agents
        price_war_intensity: Intensity of price competition
    """
    
    def __init__(
        self,
        agent_a_id: str,
        agent_b_id: str,
        strength: float = -0.3,
        attributes: Optional[Dict[str, Any]] = None,
        relationship_id: Optional[str] = None
    ):
        """
        Initialize a new competitor relationship.
        
        Args:
            agent_a_id: ID of the first agent
            agent_b_id: ID of the second agent
            strength: Initial strength (-1.0 to 1.0), typically negative
            attributes: Additional relationship attributes
            relationship_id: Unique identifier (generated if not provided)
        """
        # Set default attributes if not provided
        if attributes is None:
            attributes = {}
        
        # Initialize competitor-specific attributes
        attributes.update({
            "competing_items": [],
            "market_share_difference": 0.0,
            "price_war_intensity": 0.0,
            "last_price_change_time": None,
            "relationship_age": 0,
        })
        
        super().__init__(
            agent_a_id=agent_a_id,
            agent_b_id=agent_b_id,
            relationship_type="competitor",
            strength=strength,
            attributes=attributes,
            relationship_id=relationship_id
        )
    
    def update(self, event: BaseEvent) -> bool:
        """
        Update the relationship based on an event.
        
        Args:
            event: The event that might affect the relationship
            
        Returns:
            bool: True if the relationship was updated, False otherwise
        """
        # Check if event involves both agents or is relevant to competition
        if not self._is_relevant_event(event):
            return False
        
        updated = False
        
        if event.event_type == "price_change":
            updated = self._handle_price_change_event(event)
        elif event.event_type == "item_listing":
            updated = self._handle_item_listing_event(event)
        elif event.event_type == "trade":
            updated = self._handle_trade_event(event)
        elif event.event_type == "market_trend":
            updated = self._handle_market_trend_event(event)
        
        # Increment relationship age
        self.attributes["relationship_age"] += 1
        
        # Apply relationship normalization over time
        if self.attributes["relationship_age"] % 15 == 0:
            # Competition tends to stabilize over time
            if self.strength < -0.7:
                self.update_strength(0.02, "competition normalization")
            elif self.strength > -0.1:
                self.update_strength(-0.02, "competition normalization")
        
        return updated
    
    def _is_relevant_event(self, event: BaseEvent) -> bool:
        """
        Check if an event is relevant to this competitor relationship.
        
        Args:
            event: The event to check
            
        Returns:
            bool: True if the event is relevant
        """
        # Direct involvement
        if event.source in [self.agent_a_id, self.agent_b_id] and event.target in [self.agent_a_id, self.agent_b_id]:
            return True
        
        # Check for competition-relevant events
        if event.event_type in ["price_change", "item_listing"]:
            # Check if the event is from one of our agents
            if event.source in [self.agent_a_id, self.agent_b_id]:
                # Check if the item is a competing item
                item_id = event.data.get("item_id")
                if item_id and item_id in self.attributes["competing_items"]:
                    return True
        
        # Market trends affect all competitors
        if event.event_type == "market_trend":
            return True
        
        return False
    
    def _handle_price_change_event(self, event: BaseEvent) -> bool:
        """
        Handle a price change event.
        
        Args:
            event: The price change event
            
        Returns:
            bool: True if the relationship was updated
        """
        item_id = event.data.get("item_id")
        new_price = event.data.get("new_price")
        old_price = event.data.get("old_price")
        
        # Add to competing items if not already there
        if item_id and item_id not in self.attributes["competing_items"]:
            self.attributes["competing_items"].append(item_id)
        
        # Update last price change time
        self.attributes["last_price_change_time"] = event.timestamp.timestamp()
        
        # If price decreased significantly, increase price war intensity
        if new_price < old_price:
            price_decrease_percent = (old_price - new_price) / old_price
            
            if price_decrease_percent > 0.05:
                # Significant price decrease
                intensity_increase = price_decrease_percent * 2
                self.attributes["price_war_intensity"] = min(
                    1.0, 
                    self.attributes["price_war_intensity"] + intensity_increase
                )
                
                # Price wars intensify competition
                self.update_strength(-0.05 * intensity_increase, "price war escalation")
                
                return True
        
        # Price increases reduce price war intensity
        if new_price > old_price:
            self.attributes["price_war_intensity"] = max(
                0.0,
                self.attributes["price_war_intensity"] - 0.1
            )
            
            # Reduced price war intensity slightly improves relationship
            self.update_strength(0.01, "price war de-escalation")
        
        return True
    
    def _handle_item_listing_event(self, event: BaseEvent) -> bool:
        """
        Handle an item listing event.
        
        Args:
            event: The item listing event
            
        Returns:
            bool: True if the relationship was updated
        """
        item_id = event.data.get("item_id")
        
        # Add to competing items if not already there
        if item_id and item_id not in self.attributes["competing_items"]:
            self.attributes["competing_items"].append(item_id)
            
            # New competing item slightly increases competition
            self.update_strength(-0.02, "new competing item")
            
            return True
        
        return False
    
    def _handle_trade_event(self, event: BaseEvent) -> bool:
        """
        Handle a trade event.
        
        Args:
            event: The trade event
            
        Returns:
            bool: True if the relationship was updated
        """
        # If one competitor is trading with a customer that the other competitor
        # has also traded with, increase competition
        
        # This would require knowledge of past trades, which we don't have in this
        # simplified implementation. In a real system, we would track this.
        
        return False
    
    def _handle_market_trend_event(self, event: BaseEvent) -> bool:
        """
        Handle a market trend event.
        
        Args:
            event: The market trend event
            
        Returns:
            bool: True if the relationship was updated
        """
        trend_type = event.data.get("trend_type")
        impact = event.data.get("impact", 1.0)
        
        # Market contraction (impact < 1.0) increases competition
        if impact < 1.0:
            competition_increase = (1.0 - impact) * 0.2
            self.update_strength(-competition_increase, f"market contraction: {trend_type}")
            return True
        
        # Market expansion (impact > 1.0) decreases competition
        if impact > 1.0:
            competition_decrease = (impact - 1.0) * 0.1
            self.update_strength(competition_decrease, f"market expansion: {trend_type}")
            return True
        
        return False


class SupplierRelationship(BaseRelationship):
    """
    Relationship representing a supplier-customer connection.
    
    A supplier relationship represents a connection where one agent
    regularly supplies items to another agent.
    
    Attributes:
        supplier_id: ID of the supplier agent
        customer_id: ID of the customer agent
        supplied_items: Dictionary of items supplied and their quantities
        reliability: Supplier's reliability score
        delivery_quality: Quality of deliveries
    """
    
    def __init__(
        self,
        agent_a_id: str,
        agent_b_id: str,
        strength: float = 0.4,
        attributes: Optional[Dict[str, Any]] = None,
        relationship_id: Optional[str] = None
    ):
        """
        Initialize a new supplier relationship.
        
        Args:
            agent_a_id: ID of the supplier agent
            agent_b_id: ID of the customer agent
            strength: Initial strength (-1.0 to 1.0)
            attributes: Additional relationship attributes
            relationship_id: Unique identifier (generated if not provided)
        """
        # Set default attributes if not provided
        if attributes is None:
            attributes = {}
        
        # Initialize supplier-specific attributes
        attributes.update({
            "supplier_id": agent_a_id,
            "customer_id": agent_b_id,
            "supplied_items": {},
            "reliability": 0.7,
            "delivery_quality": 0.7,
            "last_delivery_time": None,
            "relationship_age": 0,
        })
        
        super().__init__(
            agent_a_id=agent_a_id,
            agent_b_id=agent_b_id,
            relationship_type="supplier",
            strength=strength,
            attributes=attributes,
            relationship_id=relationship_id
        )
    
    def update(self, event: BaseEvent) -> bool:
        """
        Update the relationship based on an event.
        
        Args:
            event: The event that might affect the relationship
            
        Returns:
            bool: True if the relationship was updated, False otherwise
        """
        # Check if event involves both agents
        if not self._event_involves_both_agents(event):
            return False
        
        updated = False
        
        if event.event_type == "trade":
            updated = self._handle_trade_event(event)
        elif event.event_type == "business_deal":
            updated = self._handle_business_deal_event(event)
        elif event.event_type == "deal_breach":
            updated = self._handle_deal_breach_event(event)
        
        # Increment relationship age
        self.attributes["relationship_age"] += 1
        
        # Apply relationship decay over time
        if self.attributes["relationship_age"] % 10 == 0:
            # Slight decay every 10 updates
            self.update_strength(-0.02, "natural relationship decay")
            
            # Reliability and quality also decay slightly if no recent deliveries
            if self.attributes["last_delivery_time"] is None or \
               (event.timestamp.timestamp() - self.attributes["last_delivery_time"]) > 100:
                self.attributes["reliability"] = max(0.0, self.attributes["reliability"] - 0.05)
                self.attributes["delivery_quality"] = max(0.0, self.attributes["delivery_quality"] - 0.03)
        
        return updated
    
    def _handle_trade_event(self, event: BaseEvent) -> bool:
        """
        Handle a trade event between supplier and customer.
        
        Args:
            event: The trade event
            
        Returns:
            bool: True if the relationship was updated
        """
        # Determine direction of trade
        if event.source == self.attributes["supplier_id"] and event.target == self.attributes["customer_id"]:
            # Supplier to customer trade (delivery)
            items_given = event.data.get("items_given", {})
            
            # Update supplied items
            for item_id, quantity in items_given.items():
                if item_id not in self.attributes["supplied_items"]:
                    self.attributes["supplied_items"][item_id] = 0
                self.attributes["supplied_items"][item_id] += quantity
            
            # Update last delivery time
            self.attributes["last_delivery_time"] = event.timestamp.timestamp()
            
            # Update relationship strength
            impact = event.data.get("relationship_impact", 0.05)
            self.update_strength(impact, "successful delivery")
            
            # Successful delivery improves reliability
            self.attributes["reliability"] = min(1.0, self.attributes["reliability"] + 0.02)
            
            return True
        
        elif event.source == self.attributes["customer_id"] and event.target == self.attributes["supplier_id"]:
            # Customer to supplier trade (payment or return)
            # This could be a payment or a return of defective items
            
            # For simplicity, we'll just apply a small positive impact
            impact = event.data.get("relationship_impact", 0.02)
            self.update_strength(impact, "customer payment")
            
            return True
        
        return False
    
    def _handle_business_deal_event(self, event: BaseEvent) -> bool:
        """
        Handle a business deal event between supplier and customer.
        
        Args:
            event: The business deal event
            
        Returns:
            bool: True if the relationship was updated
        """
        # Business deals have a significant positive impact
        impact = event.data.get("relationship_impact", 0.15)
        self.update_strength(impact, "supply agreement established")
        
        # Store the deal ID
        if "active_deals" not in self.attributes:
            self.attributes["active_deals"] = []
        
        deal_id = event.data.get("deal_id")
        if deal_id:
            self.attributes["active_deals"].append(deal_id)
            
            # Extract items from the deal
            terms = event.data.get("terms", {})
            items = terms.get("items", {})
            
            # Add these items to supplied items
            for item_id in items:
                if item_id not in self.attributes["supplied_items"]:
                    self.attributes["supplied_items"][item_id] = 0
        
        return True
    
    def _handle_deal_breach_event(self, event: BaseEvent) -> bool:
        """
        Handle a deal breach event between supplier and customer.
        
        Args:
            event: The deal breach event
            
        Returns:
            bool: True if the relationship was updated
        """
        # Deal breaches have a negative impact
        severity = event.data.get("severity", 0.5)
        impact = event.data.get("relationship_impact", -0.2 * severity)
        
        # If supplier breached, impact reliability
        if event.source == self.attributes["supplier_id"]:
            self.attributes["reliability"] = max(0.0, self.attributes["reliability"] - (0.1 * severity))
            self.update_strength(impact * 1.5, "supplier breach of contract")
        else:
            # Customer breach
            self.update_strength(impact, "customer breach of contract")
        
        # Remove the deal from active deals
        if "active_deals" in self.attributes:
            deal_id = event.data.get("deal_id")
            if deal_id and deal_id in self.attributes["active_deals"]:
                self.attributes["active_deals"].remove(deal_id)
        
        return True
    
    def _event_involves_both_agents(self, event: BaseEvent) -> bool:
        """
        Check if an event involves both the supplier and customer.
        
        Args:
            event: The event to check
            
        Returns:
            bool: True if both agents are involved
        """
        supplier_id = self.attributes["supplier_id"]
        customer_id = self.attributes["customer_id"]
        
        # Check direct involvement (source and target)
        if (event.source == supplier_id and event.target == customer_id) or \
           (event.source == customer_id and event.target == supplier_id):
            return True
        
        # Check participants list if available
        participants = event.data.get("participants", [])
        if supplier_id in participants and customer_id in participants:
            return True
        
        return False