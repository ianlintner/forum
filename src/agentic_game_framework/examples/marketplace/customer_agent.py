"""
Customer Agent for Marketplace Domain.

This module defines the customer agent type for the marketplace domain,
which specializes in purchasing items based on needs and preferences.
"""

import random
import time
from typing import Any, Dict, List, Optional

from ...agents.base_agent import BaseAgent
from ...events.base import BaseEvent
from ...memory.persistence import MemoryStore
from .marketplace_events import (
    TradeEvent,
    NegotiationEvent,
    BusinessDealEvent,
)


class CustomerAgent(BaseAgent):
    """
    Agent representing a customer in the marketplace.
    
    Customers specialize in purchasing items based on their needs and preferences.
    They maintain a budget, shopping list, and preferences for different merchants.
    
    Attributes:
        inventory: Dictionary of items and quantities owned
        budget: Available currency for purchases
        needs: Dictionary of items the customer needs and their priorities
        preferences: Dictionary of item preferences and quality requirements
        merchant_opinions: Dictionary of opinions about different merchants
        purchase_history: List of past purchases
    """
    
    def __init__(
        self,
        name: str,
        attributes: Optional[Dict[str, Any]] = None,
        agent_id: Optional[str] = None,
        needs: Optional[Dict[str, float]] = None
    ):
        """
        Initialize a new customer agent.
        
        Args:
            name: Human-readable name for the agent
            attributes: Agent-specific attributes
            agent_id: Unique identifier (generated if not provided)
            needs: Dictionary of items the customer needs and their priorities
        """
        # Set default attributes if not provided
        if attributes is None:
            attributes = {}
        
        # Set default needs if not provided
        if needs is None:
            # Generate random needs with priorities (0.0-1.0)
            all_items = ["food", "tools", "clothing", "luxury_goods", "crafted_goods"]
            num_needs = random.randint(2, 4)
            selected_items = random.sample(all_items, k=num_needs)
            
            needs = {
                item: random.uniform(0.3, 1.0)
                for item in selected_items
            }
        
        # Initialize with customer-specific state
        initial_state = {
            "marketplace": {
                "inventory": self._generate_initial_inventory(),
                "budget": random.uniform(50, 200),
                "needs": needs,
                "preferences": self._generate_preferences(needs),
                "merchant_opinions": {},
                "purchase_history": [],
                "satisfaction": random.uniform(0.4, 0.8),  # 0.0 = unsatisfied, 1.0 = satisfied
                "price_sensitivity": random.uniform(0.3, 0.9),  # 0.0 = insensitive, 1.0 = very sensitive
                "last_action_time": 0,
            }
        }
        
        # Add customer-specific attributes
        attributes.update({
            "agent_type": "customer",
            "bargaining_skill": random.uniform(0.2, 0.8),
            "loyalty": random.uniform(0.3, 0.9),
            "impulsiveness": random.uniform(0.1, 0.7),
        })
        
        super().__init__(name, attributes, agent_id, initial_state)
        
        # Subscribe to relevant event types
        self.subscribe_to_event("trade")
        self.subscribe_to_event("price_change")
        self.subscribe_to_event("item_listing")
        self.subscribe_to_event("negotiation")
        self.subscribe_to_event("business_deal")
        
        # Create a memory store for this agent
        self.memory = MemoryStore(self.id)
    
    def _generate_initial_inventory(self) -> Dict[str, int]:
        """
        Generate initial inventory for the customer.
        
        Returns:
            Dict[str, int]: Initial inventory
        """
        inventory = {
            "gold": random.randint(5, 15),
            "silver": random.randint(3, 10),
        }
        
        # Add some random items
        other_items = ["food", "tools", "clothing"]
        for item in random.sample(other_items, k=random.randint(1, 2)):
            inventory[item] = random.randint(1, 3)
        
        return inventory
    
    def _generate_preferences(self, needs: Dict[str, float]) -> Dict[str, Dict[str, Any]]:
        """
        Generate preferences for items based on needs.
        
        Args:
            needs: Dictionary of items the customer needs and their priorities
            
        Returns:
            Dict[str, Dict[str, Any]]: Preferences for each item
        """
        preferences = {}
        
        for item, priority in needs.items():
            # Higher priority items have stricter quality requirements
            min_quality = 0.3 + (0.4 * priority)
            
            # Higher priority items have higher price willing to pay
            max_price_factor = 1.0 + (0.5 * priority)
            
            preferences[item] = {
                "min_quality": min_quality,
                "max_price_factor": max_price_factor,
                "preferred_merchants": [],  # Will be populated as the customer interacts with merchants
            }
        
        return preferences
    
    def process_event(self, event: BaseEvent) -> None:
        """
        Process an incoming event.
        
        Args:
            event: The event to process
        """
        # Store event in memory
        from ...memory.memory_interface import MemoryItem
        
        memory_item = MemoryItem(
            memory_id=f"memory_{event.get_id()}",
            timestamp=time.time(),
            content=event.to_dict(),
            importance=self._calculate_event_importance(event)
        )
        self.memory.add_memory(memory_item)
        
        # Process different event types
        if event.event_type == "trade":
            self._process_trade_event(event)
        elif event.event_type == "price_change":
            self._process_price_change_event(event)
        elif event.event_type == "item_listing":
            self._process_item_listing_event(event)
        elif event.event_type == "negotiation":
            self._process_negotiation_event(event)
        elif event.event_type == "business_deal":
            self._process_business_deal_event(event)
    
    def _calculate_event_importance(self, event: BaseEvent) -> float:
        """
        Calculate the importance of an event for this agent.
        
        Args:
            event: The event to evaluate
            
        Returns:
            float: Importance score (0.0-1.0)
        """
        # Base importance by event type
        base_importance = {
            "trade": 0.6,
            "price_change": 0.3,
            "item_listing": 0.5,
            "negotiation": 0.4,
            "business_deal": 0.7,
        }.get(event.event_type, 0.5)
        
        # Adjust importance based on whether the agent is involved
        if event.source == self.id or event.target == self.id:
            base_importance += 0.2
        
        # Adjust importance based on item relevance to needs
        if event.event_type in ["trade", "price_change", "item_listing"]:
            item_id = None
            if event.event_type == "trade":
                # Check if any needed items are involved in the trade
                items_given = event.data.get("items_given", {})
                items_received = event.data.get("items_received", {})
                all_items = list(items_given.keys()) + list(items_received.keys())
                for item in all_items:
                    if item in self.state["marketplace"]["needs"]:
                        priority = self.state["marketplace"]["needs"].get(item, 0)
                        base_importance += 0.1 * priority
                        break
            elif event.event_type in ["price_change", "item_listing"]:
                item_id = event.data.get("item_id")
                if item_id in self.state["marketplace"]["needs"]:
                    priority = self.state["marketplace"]["needs"].get(item_id, 0)
                    base_importance += 0.1 * priority
        
        # Cap importance at 1.0
        return min(1.0, base_importance)
    
    def _process_trade_event(self, event: BaseEvent) -> None:
        """
        Process a trade event.
        
        Args:
            event: The trade event to process
        """
        # Only process if this agent is involved
        if event.source != self.id and event.target != self.id:
            return
        
        # Extract trade details
        items_given = event.data.get("items_given", {})
        items_received = event.data.get("items_received", {})
        
        # Update inventory based on whether agent is source or target
        if event.source == self.id:
            # Agent is giving items
            for item_id, quantity in items_given.items():
                if item_id in self.state["marketplace"]["inventory"]:
                    self.state["marketplace"]["inventory"][item_id] -= quantity
                    if self.state["marketplace"]["inventory"][item_id] <= 0:
                        del self.state["marketplace"]["inventory"][item_id]
            
            # Agent is receiving items
            for item_id, quantity in items_received.items():
                if item_id not in self.state["marketplace"]["inventory"]:
                    self.state["marketplace"]["inventory"][item_id] = 0
                self.state["marketplace"]["inventory"][item_id] += quantity
                
                # Update satisfaction if this was a needed item
                if item_id in self.state["marketplace"]["needs"]:
                    priority = self.state["marketplace"]["needs"].get(item_id, 0)
                    self.state["marketplace"]["satisfaction"] += 0.1 * priority
                    self.state["marketplace"]["satisfaction"] = min(1.0, self.state["marketplace"]["satisfaction"])
        
        elif event.target == self.id:
            # Agent is receiving items
            for item_id, quantity in items_given.items():
                if item_id not in self.state["marketplace"]["inventory"]:
                    self.state["marketplace"]["inventory"][item_id] = 0
                self.state["marketplace"]["inventory"][item_id] += quantity
                
                # Update satisfaction if this was a needed item
                if item_id in self.state["marketplace"]["needs"]:
                    priority = self.state["marketplace"]["needs"].get(item_id, 0)
                    self.state["marketplace"]["satisfaction"] += 0.1 * priority
                    self.state["marketplace"]["satisfaction"] = min(1.0, self.state["marketplace"]["satisfaction"])
            
            # Agent is giving items
            for item_id, quantity in items_received.items():
                if item_id in self.state["marketplace"]["inventory"]:
                    self.state["marketplace"]["inventory"][item_id] -= quantity
                    if self.state["marketplace"]["inventory"][item_id] <= 0:
                        del self.state["marketplace"]["inventory"][item_id]
        
        # Record purchase in history
        partner_id = event.source if event.target == self.id else event.target
        
        self.state["marketplace"]["purchase_history"].append({
            "timestamp": event.timestamp.timestamp(),
            "merchant_id": partner_id,
            "items_given": items_received if event.source == self.id else items_given,
            "items_received": items_given if event.source == self.id else items_received,
        })
        
        # Update opinion of merchant
        self._update_merchant_opinion(partner_id, event)
    
    def _update_merchant_opinion(self, merchant_id: str, event: BaseEvent) -> None:
        """
        Update opinion of a merchant based on an interaction.
        
        Args:
            merchant_id: ID of the merchant
            event: The event representing the interaction
        """
        # Initialize opinion if not exists
        if merchant_id not in self.state["marketplace"]["merchant_opinions"]:
            self.state["marketplace"]["merchant_opinions"][merchant_id] = {
                "trust": 0.5,
                "satisfaction": 0.5,
                "transaction_count": 0,
                "last_transaction": None,
            }
        
        opinion = self.state["marketplace"]["merchant_opinions"][merchant_id]
        
        # Update transaction count and timestamp
        opinion["transaction_count"] += 1
        opinion["last_transaction"] = event.timestamp.timestamp()
        
        if event.event_type == "trade":
            # Evaluate the fairness of the trade
            items_received = event.data.get("items_given", {}) if event.target == self.id else event.data.get("items_received", {})
            items_given = event.data.get("items_received", {}) if event.target == self.id else event.data.get("items_given", {})
            
            # Simple evaluation: did we get items we need?
            satisfaction_change = 0
            for item_id, quantity in items_received.items():
                if item_id in self.state["marketplace"]["needs"]:
                    priority = self.state["marketplace"]["needs"].get(item_id, 0)
                    satisfaction_change += 0.05 * priority * quantity
            
            # Did we pay a fair price?
            price_sensitivity = self.state["marketplace"]["price_sensitivity"]
            
            # Simple heuristic for price fairness
            # In a real implementation, this would compare to market prices
            if random.random() > price_sensitivity:
                # Customer feels the price was fair
                satisfaction_change += 0.05
            else:
                # Customer feels the price was too high
                satisfaction_change -= 0.05
            
            # Update satisfaction with the merchant
            opinion["satisfaction"] = max(0.0, min(1.0, opinion["satisfaction"] + satisfaction_change))
            
            # Update trust based on satisfaction
            loyalty = self.get_attribute("loyalty", 0.5)
            trust_change = satisfaction_change * (0.5 + (0.5 * loyalty))
            opinion["trust"] = max(0.0, min(1.0, opinion["trust"] + trust_change))
            
            # Add merchant to preferred merchants for the items received
            for item_id in items_received:
                if item_id in self.state["marketplace"]["preferences"]:
                    if merchant_id not in self.state["marketplace"]["preferences"][item_id]["preferred_merchants"]:
                        self.state["marketplace"]["preferences"][item_id]["preferred_merchants"].append(merchant_id)
    
    def _process_price_change_event(self, event: BaseEvent) -> None:
        """
        Process a price change event.
        
        Args:
            event: The price change event to process
        """
        item_id = event.data.get("item_id")
        new_price = event.data.get("new_price")
        old_price = event.data.get("old_price")
        
        # Only care about items we need
        if item_id not in self.state["marketplace"]["needs"]:
            return
        
        # Update opinion of merchant if price increased significantly
        if event.source and new_price > old_price:
            price_increase_percent = (new_price - old_price) / old_price
            
            # If price increased more than 10%, reduce trust
            if price_increase_percent > 0.1:
                if event.source in self.state["marketplace"]["merchant_opinions"]:
                    opinion = self.state["marketplace"]["merchant_opinions"][event.source]
                    
                    # More price-sensitive customers react more strongly
                    price_sensitivity = self.state["marketplace"]["price_sensitivity"]
                    trust_change = -0.05 * price_sensitivity * (price_increase_percent / 0.1)
                    
                    opinion["trust"] = max(0.0, opinion["trust"] + trust_change)
    
    def _process_item_listing_event(self, event: BaseEvent) -> None:
        """
        Process an item listing event.
        
        Args:
            event: The item listing event to process
        """
        item_id = event.data.get("item_id")
        price = event.data.get("price")
        
        # Only care about items we need
        if item_id not in self.state["marketplace"]["needs"]:
            return
        
        # Remember this merchant has this item
        merchant_id = event.source
        if merchant_id and item_id in self.state["marketplace"]["preferences"]:
            if merchant_id not in self.state["marketplace"]["preferences"][item_id]["preferred_merchants"]:
                self.state["marketplace"]["preferences"][item_id]["preferred_merchants"].append(merchant_id)
    
    def _process_negotiation_event(self, event: BaseEvent) -> None:
        """
        Process a negotiation event.
        
        Args:
            event: The negotiation event to process
        """
        # Only process if this agent is involved
        if event.source != self.id and event.target != self.id:
            return
        
        # Extract negotiation details
        proposal = event.data.get("proposal", {})
        is_counter = event.data.get("is_counter", False)
        
        # If we're the target, consider the proposal
        if event.target == self.id:
            # This would be handled by generate_action to create a counter-proposal
            # or accept/reject the offer
            pass
    
    def _process_business_deal_event(self, event: BaseEvent) -> None:
        """
        Process a business deal event.
        
        Args:
            event: The business deal event to process
        """
        # Only process if this agent is involved
        if event.source != self.id and event.target != self.id:
            return
        
        deal_id = event.data.get("deal_id")
        partner_id = event.source if event.target == self.id else event.target
        terms = event.data.get("terms", {})
        
        # Record the business deal
        if "business_deals" not in self.state["marketplace"]:
            self.state["marketplace"]["business_deals"] = []
            
        self.state["marketplace"]["business_deals"].append({
            "deal_id": deal_id,
            "partner_id": partner_id,
            "terms": terms,
            "start_time": event.timestamp.timestamp(),
            "active": True,
        })
        
        # Update merchant opinion
        if partner_id in self.state["marketplace"]["merchant_opinions"]:
            opinion = self.state["marketplace"]["merchant_opinions"][partner_id]
            
            # Business deals increase trust
            loyalty = self.get_attribute("loyalty", 0.5)
            trust_change = 0.1 * (0.5 + (0.5 * loyalty))
            
            opinion["trust"] = min(1.0, opinion["trust"] + trust_change)
    
    def generate_action(self) -> Optional[BaseEvent]:
        """
        Generate an action based on the agent's current state.
        
        Returns:
            Optional[BaseEvent]: An event representing the action, or None if no action
        """
        # Only act every few seconds to avoid spamming
        current_time = time.time()
        if current_time - self.state["marketplace"]["last_action_time"] < 2.0:
            return None
            
        self.state["marketplace"]["last_action_time"] = current_time
        
        # Choose an action type based on agent state and attributes
        action_types = ["trade", "negotiation", "business_deal"]
        
        # Adjust weights based on agent attributes and state
        bargaining_skill = self.get_attribute("bargaining_skill", 0.5)
        impulsiveness = self.get_attribute("impulsiveness", 0.3)
        satisfaction = self.state["marketplace"]["satisfaction"]
        
        # More satisfied customers trade less frequently
        trade_weight = 0.6 * (1.0 - (0.5 * satisfaction))
        
        # More impulsive customers trade more frequently
        trade_weight *= (0.7 + (0.3 * impulsiveness))
        
        weights = [
            trade_weight,  # trade
            0.3 * bargaining_skill,  # negotiation
            0.1 * (1.0 - impulsiveness),  # business_deal (less impulsive customers prefer stable deals)
        ]
        
        action_type = random.choices(action_types, weights=weights, k=1)[0]
        
        # Need a target agent ID for the action
        # This would normally come from the agent manager, but for this example
        # we'll just use a placeholder that will be filled in by the simulation
        target_id = "TARGET_PLACEHOLDER"
        
        if action_type == "trade":
            return self._generate_trade_request(target_id)
        elif action_type == "negotiation":
            return self._generate_negotiation(target_id)
        elif action_type == "business_deal":
            return self._generate_business_deal(target_id)
        
        return None
    
    def _generate_trade_request(self, target_id: str) -> Optional[TradeEvent]:
        """
        Generate a trade request based on needs and inventory.
        
        Args:
            target_id: ID of the target merchant
            
        Returns:
            Optional[TradeEvent]: A trade event, or None if no valid trade
        """
        # Choose an item to request based on needs
        needed_items = list(self.state["marketplace"]["needs"].keys())
        if not needed_items:
            return None
            
        # Sort by priority
        needed_items.sort(key=lambda x: self.state["marketplace"]["needs"].get(x, 0), reverse=True)
        
        # Choose one of the top needs
        request_item_id = needed_items[0] if random.random() < 0.7 else random.choice(needed_items)
        request_quantity = random.randint(1, 3)
        
        # Choose what to offer in return
        # Prefer to offer gold or silver if available
        available_items = list(self.state["marketplace"]["inventory"].keys())
        if not available_items:
            return None
            
        # Prioritize currency items
        currency_items = [item for item in available_items if item in ["gold", "silver"]]
        if currency_items:
            offer_item_id = random.choice(currency_items)
        else:
            # Offer a non-needed item if possible
            non_needed_items = [item for item in available_items if item not in needed_items]
            if non_needed_items:
                offer_item_id = random.choice(non_needed_items)
            else:
                # Have to offer a needed item
                offer_item_id = random.choice(available_items)
        
        # Determine quantity to offer
        max_quantity = self.state["marketplace"]["inventory"].get(offer_item_id, 0)
        if max_quantity <= 0:
            return None
            
        offer_quantity = min(random.randint(1, 3), max_quantity)
        
        return TradeEvent(
            source=self.id,
            target=target_id,
            items_given={offer_item_id: offer_quantity},
            items_received={request_item_id: request_quantity}
        )
    
    def _generate_negotiation(self, target_id: str) -> Optional[NegotiationEvent]:
        """
        Generate a negotiation proposal.
        
        Args:
            target_id: ID of the target merchant
            
        Returns:
            Optional[NegotiationEvent]: A negotiation event, or None if no valid proposal
        """
        # Choose an item to negotiate for based on needs
        needed_items = list(self.state["marketplace"]["needs"].keys())
        if not needed_items:
            return None
            
        # Sort by priority
        needed_items.sort(key=lambda x: self.state["marketplace"]["needs"].get(x, 0), reverse=True)
        
        # Choose one of the top needs
        item_id = needed_items[0] if random.random() < 0.7 else random.choice(needed_items)
        quantity = random.randint(1, 3)
        
        # Set price based on bargaining skill
        # In a real implementation, this would be based on market knowledge
        bargaining_skill = self.get_attribute("bargaining_skill", 0.5)
        
        # Better bargainers start with more favorable terms
        price_adjustment = -0.1 - (0.2 * bargaining_skill)
        proposed_price = 10 * (1 + price_adjustment)  # Placeholder price
        
        return NegotiationEvent(
            source=self.id,
            target=target_id,
            proposal={
                "item_id": item_id,
                "quantity": quantity,
                "price": proposed_price,
                "flexible": random.random() < bargaining_skill  # More skilled bargainers are more flexible
            }
        )
    
    def _generate_business_deal(self, target_id: str) -> Optional[BusinessDealEvent]:
        """
        Generate a business deal proposal.
        
        Args:
            target_id: ID of the target merchant
            
        Returns:
            Optional[BusinessDealEvent]: A business deal event, or None if no valid deal
        """
        # Choose items for the deal based on needs
        needed_items = list(self.state["marketplace"]["needs"].keys())
        if not needed_items:
            return None
            
        # Sort by priority
        needed_items.sort(key=lambda x: self.state["marketplace"]["needs"].get(x, 0), reverse=True)
        
        # Choose top needs for the deal
        deal_items = {}
        for item_id in needed_items[:2]:  # Top 2 needs
            quantity = random.randint(1, 3)
            
            # Customers are willing to pay more for regular supply
            priority = self.state["marketplace"]["needs"].get(item_id, 0)
            price_factor = 1.0 + (0.1 * priority)
            
            # Base price is just a placeholder
            price = 10 * price_factor
            
            deal_items[item_id] = {
                "quantity": quantity,
                "price": price
            }
        
        if not deal_items:
            return None
            
        # Generate deal terms
        deal_id = f"deal_{random.randint(1000, 9999)}"
        duration = random.randint(5, 15)  # Number of time steps
        
        # Loyal customers might request exclusivity
        loyalty = self.get_attribute("loyalty", 0.5)
        exclusivity = random.random() < (loyalty * 0.3)
        
        return BusinessDealEvent(
            source=self.id,
            target=target_id,
            deal_id=deal_id,
            terms={
                "duration": duration,
                "items": deal_items,
                "exclusivity": exclusivity,
                "payment_schedule": "per_delivery"  # or "upfront"
            }
        )