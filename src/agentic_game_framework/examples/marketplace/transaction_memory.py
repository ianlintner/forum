"""
Transaction Memory for Marketplace Domain.

This module defines the domain-specific memory types for the marketplace domain,
such as transaction memories, price memories, and business deal memories.
"""

import time
from typing import Any, Dict, Optional

from ...events.base import BaseEvent
from ...memory.memory_interface import EventMemoryItem, MemoryItem


class TransactionMemory(EventMemoryItem):
    """
    Memory item for storing transaction information.
    
    Transaction memories represent trades between agents, including
    the items exchanged, their quantities, and the perceived value.
    
    Attributes:
        transaction_data: Detailed information about the transaction
        partner_id: ID of the trading partner
        items_given: Items given in the transaction
        items_received: Items received in the transaction
        perceived_value: Subjective value of the transaction
    """
    
    def __init__(
        self,
        memory_id: str,
        timestamp: float,
        event: BaseEvent,
        importance: float = 0.7,
        associations: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a new transaction memory.
        
        Args:
            memory_id: Unique identifier for the memory
            timestamp: When the memory was created/occurred
            event: The trade event to store
            importance: How important this memory is (0.0-1.0)
            associations: Related concepts or metadata
        """
        super().__init__(
            memory_id=memory_id,
            timestamp=timestamp,
            event=event,
            importance=importance,
            associations=associations or {}
        )
        
        # Extract transaction-specific data
        self.transaction_data = self._extract_transaction_data(event)
        
        # Add transaction-specific associations
        self.add_association("transaction_type", "trade")
        self.add_association("partner_id", self.transaction_data["partner_id"])
        
        for item_id in self.transaction_data["items_given"]:
            self.add_association(f"gave_{item_id}", True)
            
        for item_id in self.transaction_data["items_received"]:
            self.add_association(f"received_{item_id}", True)
    
    def _extract_transaction_data(self, event: BaseEvent) -> Dict[str, Any]:
        """
        Extract transaction data from a trade event.
        
        Args:
            event: The trade event
            
        Returns:
            Dict[str, Any]: Extracted transaction data
        """
        # Determine the agent's perspective
        agent_id = self.associations.get("agent_id")
        
        if agent_id == event.source:
            # Agent is the source of the trade
            partner_id = event.target
            items_given = event.data.get("items_given", {})
            items_received = event.data.get("items_received", {})
        elif agent_id == event.target:
            # Agent is the target of the trade
            partner_id = event.source
            items_given = event.data.get("items_received", {})
            items_received = event.data.get("items_given", {})
        else:
            # Agent is observing the trade
            partner_id = None
            items_given = {}
            items_received = {}
        
        # Calculate perceived value (simplified)
        perceived_value = sum(items_received.values()) - sum(items_given.values())
        
        return {
            "partner_id": partner_id,
            "items_given": items_given,
            "items_received": items_received,
            "perceived_value": perceived_value,
            "transaction_time": event.timestamp.timestamp(),
        }
    
    def get_summary(self) -> str:
        """
        Get a human-readable summary of the transaction.
        
        Returns:
            str: Summary of the transaction
        """
        partner = self.transaction_data["partner_id"] or "unknown"
        
        items_given_str = ", ".join(
            f"{qty} {item}" for item, qty in self.transaction_data["items_given"].items()
        ) or "nothing"
        
        items_received_str = ", ".join(
            f"{qty} {item}" for item, qty in self.transaction_data["items_received"].items()
        ) or "nothing"
        
        value_assessment = ""
        if self.transaction_data["perceived_value"] > 0:
            value_assessment = "This was a good deal."
        elif self.transaction_data["perceived_value"] < 0:
            value_assessment = "This was a poor deal."
        else:
            value_assessment = "This was a fair exchange."
        
        return f"Traded with {partner}, gave {items_given_str}, received {items_received_str}. {value_assessment}"
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the memory item to a dictionary representation.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the memory item
        """
        data = super().to_dict()
        data["transaction_data"] = self.transaction_data
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TransactionMemory':
        """
        Create a transaction memory from a dictionary representation.
        
        Args:
            data: Dictionary containing memory item data
            
        Returns:
            TransactionMemory: A new transaction memory instance
        """
        memory = super().from_dict(data)
        memory.transaction_data = data.get("transaction_data", {})
        return memory


class PriceMemory(EventMemoryItem):
    """
    Memory item for storing price information.
    
    Price memories represent knowledge about item prices,
    including price changes and market trends.
    
    Attributes:
        price_data: Detailed information about the price
        item_id: ID of the item
        price: Current price of the item
        price_history: History of price changes
    """
    
    def __init__(
        self,
        memory_id: str,
        timestamp: float,
        event: BaseEvent,
        importance: float = 0.5,
        associations: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a new price memory.
        
        Args:
            memory_id: Unique identifier for the memory
            timestamp: When the memory was created/occurred
            event: The price-related event to store
            importance: How important this memory is (0.0-1.0)
            associations: Related concepts or metadata
        """
        super().__init__(
            memory_id=memory_id,
            timestamp=timestamp,
            event=event,
            importance=importance,
            associations=associations or {}
        )
        
        # Extract price-specific data
        self.price_data = self._extract_price_data(event)
        
        # Add price-specific associations
        self.add_association("memory_type", "price")
        self.add_association("item_id", self.price_data["item_id"])
        self.add_association("price", self.price_data["price"])
        
        if "source_id" in self.price_data:
            self.add_association("source_id", self.price_data["source_id"])
    
    def _extract_price_data(self, event: BaseEvent) -> Dict[str, Any]:
        """
        Extract price data from a price-related event.
        
        Args:
            event: The price-related event
            
        Returns:
            Dict[str, Any]: Extracted price data
        """
        if event.event_type == "price_change":
            return {
                "item_id": event.data.get("item_id"),
                "price": event.data.get("new_price"),
                "old_price": event.data.get("old_price"),
                "percent_change": event.data.get("percent_change"),
                "is_increase": event.data.get("is_increase"),
                "source_id": event.source,
                "observation_time": event.timestamp.timestamp(),
            }
        elif event.event_type == "item_listing":
            return {
                "item_id": event.data.get("item_id"),
                "price": event.data.get("price"),
                "quantity": event.data.get("quantity"),
                "source_id": event.source,
                "observation_time": event.timestamp.timestamp(),
            }
        elif event.event_type == "market_trend":
            affected_items = event.data.get("affected_items", {})
            trend_type = event.data.get("trend_type")
            impact = event.data.get("impact", 1.0)
            
            return {
                "trend_type": trend_type,
                "impact": impact,
                "affected_items": affected_items,
                "observation_time": event.timestamp.timestamp(),
            }
        
        # Default for unknown event types
        return {
            "item_id": "unknown",
            "price": 0,
            "observation_time": event.timestamp.timestamp(),
        }
    
    def get_summary(self) -> str:
        """
        Get a human-readable summary of the price information.
        
        Returns:
            str: Summary of the price information
        """
        if "trend_type" in self.price_data:
            # This is a market trend
            trend = self.price_data["trend_type"]
            impact = self.price_data["impact"]
            direction = "up" if impact > 1.0 else "down"
            
            return f"Market trend: {trend}, prices trending {direction} by factor of {impact:.2f}"
        
        item_id = self.price_data.get("item_id", "unknown")
        price = self.price_data.get("price", 0)
        
        if "old_price" in self.price_data:
            old_price = self.price_data["old_price"]
            change_type = "increased" if self.price_data.get("is_increase", False) else "decreased"
            
            return f"Price of {item_id} {change_type} from {old_price} to {price}"
        
        return f"Price of {item_id} is {price}"
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the memory item to a dictionary representation.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the memory item
        """
        data = super().to_dict()
        data["price_data"] = self.price_data
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PriceMemory':
        """
        Create a price memory from a dictionary representation.
        
        Args:
            data: Dictionary containing memory item data
            
        Returns:
            PriceMemory: A new price memory instance
        """
        memory = super().from_dict(data)
        memory.price_data = data.get("price_data", {})
        return memory


class BusinessDealMemory(EventMemoryItem):
    """
    Memory item for storing business deal information.
    
    Business deal memories represent long-term commercial arrangements
    between agents, including terms, duration, and performance.
    
    Attributes:
        deal_data: Detailed information about the business deal
        deal_id: Unique identifier for the deal
        partner_id: ID of the partner in the deal
        terms: Terms of the deal
        start_time: When the deal started
        end_time: When the deal is scheduled to end
        is_active: Whether the deal is currently active
    """
    
    def __init__(
        self,
        memory_id: str,
        timestamp: float,
        event: BaseEvent,
        importance: float = 0.8,
        associations: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a new business deal memory.
        
        Args:
            memory_id: Unique identifier for the memory
            timestamp: When the memory was created/occurred
            event: The business deal event to store
            importance: How important this memory is (0.0-1.0)
            associations: Related concepts or metadata
        """
        super().__init__(
            memory_id=memory_id,
            timestamp=timestamp,
            event=event,
            importance=importance,
            associations=associations or {}
        )
        
        # Extract deal-specific data
        self.deal_data = self._extract_deal_data(event)
        
        # Add deal-specific associations
        self.add_association("memory_type", "business_deal")
        self.add_association("deal_id", self.deal_data["deal_id"])
        self.add_association("partner_id", self.deal_data["partner_id"])
        
        for item_id in self.deal_data.get("items", {}):
            self.add_association(f"deal_item_{item_id}", True)
    
    def _extract_deal_data(self, event: BaseEvent) -> Dict[str, Any]:
        """
        Extract business deal data from a deal event.
        
        Args:
            event: The business deal event
            
        Returns:
            Dict[str, Any]: Extracted deal data
        """
        # Determine the agent's perspective
        agent_id = self.associations.get("agent_id")
        
        if agent_id == event.source:
            # Agent is the source of the deal
            partner_id = event.target
            is_initiator = True
        elif agent_id == event.target:
            # Agent is the target of the deal
            partner_id = event.source
            is_initiator = False
        else:
            # Agent is observing the deal
            partner_id = None
            is_initiator = False
        
        deal_id = event.data.get("deal_id")
        terms = event.data.get("terms", {})
        
        # Calculate deal duration
        duration = terms.get("duration", 0)
        start_time = event.timestamp.timestamp()
        end_time = start_time + (duration * 86400)  # Convert days to seconds
        
        # Extract items involved in the deal
        items = terms.get("items", {})
        
        return {
            "deal_id": deal_id,
            "partner_id": partner_id,
            "is_initiator": is_initiator,
            "terms": terms,
            "items": items,
            "start_time": start_time,
            "end_time": end_time,
            "is_active": True,
            "performance_history": [],
        }
    
    def update_performance(self, event: BaseEvent) -> None:
        """
        Update the deal's performance history based on an event.
        
        Args:
            event: The event related to the deal's performance
        """
        if event.event_type == "trade":
            # Check if this trade is related to the deal
            if self._is_deal_related_trade(event):
                self.deal_data["performance_history"].append({
                    "event_type": "trade",
                    "timestamp": event.timestamp.timestamp(),
                    "fulfilled_items": self._extract_fulfilled_items(event),
                })
        elif event.event_type == "deal_breach":
            # Check if this breach is for this deal
            if event.data.get("deal_id") == self.deal_data["deal_id"]:
                self.deal_data["performance_history"].append({
                    "event_type": "breach",
                    "timestamp": event.timestamp.timestamp(),
                    "severity": event.data.get("severity", 0.5),
                    "breach_type": event.data.get("breach_type"),
                })
                
                # Update active status if breach is severe
                if event.data.get("severity", 0.5) > 0.7:
                    self.deal_data["is_active"] = False
    
    def _is_deal_related_trade(self, event: BaseEvent) -> bool:
        """
        Check if a trade event is related to this deal.
        
        Args:
            event: The trade event to check
            
        Returns:
            bool: True if the trade is related to this deal
        """
        # Check if the trade is between the deal partners
        agent_id = self.associations.get("agent_id")
        partner_id = self.deal_data["partner_id"]
        
        if not ((event.source == agent_id and event.target == partner_id) or
                (event.source == partner_id and event.target == agent_id)):
            return False
        
        # Check if any of the traded items are part of the deal
        deal_items = set(self.deal_data.get("items", {}).keys())
        
        traded_items = set()
        traded_items.update(event.data.get("items_given", {}).keys())
        traded_items.update(event.data.get("items_received", {}).keys())
        
        return bool(deal_items.intersection(traded_items))
    
    def _extract_fulfilled_items(self, event: BaseEvent) -> Dict[str, int]:
        """
        Extract items from a trade event that fulfill deal requirements.
        
        Args:
            event: The trade event
            
        Returns:
            Dict[str, int]: Fulfilled items and quantities
        """
        agent_id = self.associations.get("agent_id")
        deal_items = set(self.deal_data.get("items", {}).keys())
        
        fulfilled_items = {}
        
        if agent_id == event.source:
            # Agent is giving items
            for item_id, quantity in event.data.get("items_given", {}).items():
                if item_id in deal_items:
                    fulfilled_items[item_id] = quantity
        elif agent_id == event.target:
            # Agent is receiving items
            for item_id, quantity in event.data.get("items_received", {}).items():
                if item_id in deal_items:
                    fulfilled_items[item_id] = quantity
        
        return fulfilled_items
    
    def get_summary(self) -> str:
        """
        Get a human-readable summary of the business deal.
        
        Returns:
            str: Summary of the business deal
        """
        partner = self.deal_data["partner_id"] or "unknown"
        status = "active" if self.deal_data["is_active"] else "inactive"
        
        items_str = ", ".join(
            f"{item}" for item in self.deal_data.get("items", {}).keys()
        ) or "no specific items"
        
        duration = round((self.deal_data["end_time"] - self.deal_data["start_time"]) / 86400)
        
        performance = ""
        if self.deal_data["performance_history"]:
            trades = sum(1 for p in self.deal_data["performance_history"] if p["event_type"] == "trade")
            breaches = sum(1 for p in self.deal_data["performance_history"] if p["event_type"] == "breach")
            
            performance = f" There have been {trades} deliveries and {breaches} breaches."
        
        return f"Business deal with {partner} for {items_str}, lasting {duration} days, currently {status}.{performance}"
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the memory item to a dictionary representation.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the memory item
        """
        data = super().to_dict()
        data["deal_data"] = self.deal_data
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BusinessDealMemory':
        """
        Create a business deal memory from a dictionary representation.
        
        Args:
            data: Dictionary containing memory item data
            
        Returns:
            BusinessDealMemory: A new business deal memory instance
        """
        memory = super().from_dict(data)
        memory.deal_data = data.get("deal_data", {})
        return memory