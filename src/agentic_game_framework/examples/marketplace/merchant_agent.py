"""
Merchant Agent for Marketplace Domain.

This module defines the merchant agent type for the marketplace domain,
which specializes in buying, selling, and trading items.
"""

import random
import time
from typing import Any, Dict, List, Optional

from ...agents.base_agent import BaseAgent
from ...events.base import BaseEvent
from ...memory.persistence import MemoryStore
from .marketplace_events import (
    TradeEvent,
    PriceChangeEvent,
    ItemListingEvent,
    NegotiationEvent,
    BusinessDealEvent,
)


class MerchantAgent(BaseAgent):
    """
    Agent representing a merchant in the marketplace.
    
    Merchants specialize in buying, selling, and trading items.
    They maintain inventory, set prices, and seek profitable trades.
    
    Attributes:
        inventory: Dictionary of items and quantities in stock
        price_beliefs: Dictionary of item price beliefs
        specialties: List of item types the merchant specializes in
        trade_history: List of past trades
        business_deals: List of active business deals
    """
    
    def __init__(
        self,
        name: str,
        attributes: Optional[Dict[str, Any]] = None,
        agent_id: Optional[str] = None,
        specialties: Optional[List[str]] = None
    ):
        """
        Initialize a new merchant agent.
        
        Args:
            name: Human-readable name for the agent
            attributes: Agent-specific attributes
            agent_id: Unique identifier (generated if not provided)
            specialties: Item types the merchant specializes in
        """
        # Set default attributes if not provided
        if attributes is None:
            attributes = {}
        
        # Set default specialties if not provided
        if specialties is None:
            specialties = random.sample(
                ["gold", "silver", "food", "tools", "clothing", "luxury_goods", "raw_materials", "crafted_goods"],
                k=random.randint(2, 4)
            )
        
        # Initialize with merchant-specific state
        initial_state = {
            "marketplace": {
                "inventory": self._generate_initial_inventory(specialties),
                "price_beliefs": self._generate_initial_price_beliefs(),
                "specialties": specialties,
                "trade_history": [],
                "business_deals": [],
                "reputation": random.uniform(0.3, 0.8),  # 0.0 = poor, 1.0 = excellent
                "profit_margin": random.uniform(0.1, 0.3),  # Desired profit margin
                "risk_tolerance": random.uniform(0.2, 0.8),  # 0.0 = risk-averse, 1.0 = risk-seeking
                "last_action_time": 0,
            }
        }
        
        # Add merchant-specific attributes
        attributes.update({
            "agent_type": "merchant",
            "trading_skill": random.uniform(0.3, 0.9),
            "negotiation_skill": random.uniform(0.3, 0.9),
            "market_knowledge": random.uniform(0.3, 0.9),
        })
        
        super().__init__(name, attributes, agent_id, initial_state)
        
        # Subscribe to relevant event types
        self.subscribe_to_event("trade")
        self.subscribe_to_event("price_change")
        self.subscribe_to_event("item_listing")
        self.subscribe_to_event("negotiation")
        self.subscribe_to_event("business_deal")
        self.subscribe_to_event("deal_breach")
        self.subscribe_to_event("market_trend")
        
        # Create a memory store for this agent
        self.memory = MemoryStore(self.id)
    
    def _generate_initial_inventory(self, specialties: List[str]) -> Dict[str, int]:
        """
        Generate initial inventory based on specialties.
        
        Args:
            specialties: Item types the merchant specializes in
            
        Returns:
            Dict[str, int]: Initial inventory
        """
        inventory = {}
        
        # Add specialty items with higher quantities
        for item_type in specialties:
            inventory[item_type] = random.randint(5, 15)
        
        # Add some non-specialty items with lower quantities
        non_specialties = [
            item for item in ["gold", "silver", "food", "tools", "clothing", "luxury_goods", "raw_materials", "crafted_goods"]
            if item not in specialties
        ]
        
        for item_type in random.sample(non_specialties, k=min(2, len(non_specialties))):
            inventory[item_type] = random.randint(1, 5)
        
        return inventory
    
    def _generate_initial_price_beliefs(self) -> Dict[str, float]:
        """
        Generate initial price beliefs for common items.
        
        Returns:
            Dict[str, float]: Initial price beliefs
        """
        return {
            "gold": random.uniform(15, 25),
            "silver": random.uniform(8, 15),
            "food": random.uniform(3, 8),
            "tools": random.uniform(5, 12),
            "clothing": random.uniform(7, 18),
            "luxury_goods": random.uniform(20, 40),
            "raw_materials": random.uniform(2, 6),
            "crafted_goods": random.uniform(10, 20),
        }
    
    def process_event(self, event: BaseEvent) -> None:
        """
        Process an incoming event.
        
        Args:
            event: The event to process
        """
        # Store event in memory (could be enhanced with domain-specific memory items)
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
        elif event.event_type == "deal_breach":
            self._process_deal_breach_event(event)
        elif event.event_type == "market_trend":
            self._process_market_trend_event(event)
    
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
            "price_change": 0.4,
            "item_listing": 0.3,
            "negotiation": 0.5,
            "business_deal": 0.8,
            "deal_breach": 0.9,
            "market_trend": 0.7,
        }.get(event.event_type, 0.5)
        
        # Adjust importance based on whether the agent is involved
        if event.source == self.id or event.target == self.id:
            base_importance += 0.2
        
        # Adjust importance based on item relevance
        if event.event_type in ["trade", "price_change", "item_listing"]:
            item_id = None
            if event.event_type == "trade":
                # Check if any specialty items are involved in the trade
                items_given = event.data.get("items_given", {})
                items_received = event.data.get("items_received", {})
                all_items = list(items_given.keys()) + list(items_received.keys())
                for item in all_items:
                    if item in self.state["marketplace"]["specialties"]:
                        base_importance += 0.1
                        break
            elif event.event_type in ["price_change", "item_listing"]:
                item_id = event.data.get("item_id")
                if item_id in self.state["marketplace"]["specialties"]:
                    base_importance += 0.1
        
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
            # Still learn from observed trades
            self._update_price_beliefs_from_trade(event)
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
        
        elif event.target == self.id:
            # Agent is receiving items
            for item_id, quantity in items_given.items():
                if item_id not in self.state["marketplace"]["inventory"]:
                    self.state["marketplace"]["inventory"][item_id] = 0
                self.state["marketplace"]["inventory"][item_id] += quantity
            
            # Agent is giving items
            for item_id, quantity in items_received.items():
                if item_id in self.state["marketplace"]["inventory"]:
                    self.state["marketplace"]["inventory"][item_id] -= quantity
                    if self.state["marketplace"]["inventory"][item_id] <= 0:
                        del self.state["marketplace"]["inventory"][item_id]
        
        # Record trade in history
        self.state["marketplace"]["trade_history"].append({
            "timestamp": event.timestamp.timestamp(),
            "partner_id": event.source if event.target == self.id else event.target,
            "items_given": items_received if event.source == self.id else items_given,
            "items_received": items_given if event.source == self.id else items_received,
        })
        
        # Update price beliefs based on this trade
        self._update_price_beliefs_from_trade(event)
    
    def _update_price_beliefs_from_trade(self, event: BaseEvent) -> None:
        """
        Update price beliefs based on observed trade.
        
        Args:
            event: The trade event to learn from
        """
        items_given = event.data.get("items_given", {})
        items_received = event.data.get("items_received", {})
        
        # Calculate implied values
        total_given_value = sum(
            quantity * self.state["marketplace"]["price_beliefs"].get(item_id, 10)
            for item_id, quantity in items_given.items()
        )
        
        total_received_value = sum(
            quantity * self.state["marketplace"]["price_beliefs"].get(item_id, 10)
            for item_id, quantity in items_received.items()
        )
        
        # Skip if either side has zero items
        if not items_given or not items_received:
            return
        
        # Calculate value ratio
        if total_given_value > 0 and total_received_value > 0:
            ratio = total_received_value / total_given_value
            
            # Update price beliefs based on this ratio
            for item_id, quantity in items_given.items():
                current_belief = self.state["marketplace"]["price_beliefs"].get(item_id, 10)
                # Adjust belief slightly based on observed value
                implied_value = (total_received_value / sum(items_given.values())) * ratio
                # Blend current belief with new observation (80% old, 20% new)
                new_belief = (0.8 * current_belief) + (0.2 * implied_value)
                self.state["marketplace"]["price_beliefs"][item_id] = new_belief
            
            for item_id, quantity in items_received.items():
                current_belief = self.state["marketplace"]["price_beliefs"].get(item_id, 10)
                # Adjust belief slightly based on observed value
                implied_value = (total_given_value / sum(items_received.values())) / ratio
                # Blend current belief with new observation (80% old, 20% new)
                new_belief = (0.8 * current_belief) + (0.2 * implied_value)
                self.state["marketplace"]["price_beliefs"][item_id] = new_belief
    
    def _process_price_change_event(self, event: BaseEvent) -> None:
        """
        Process a price change event.
        
        Args:
            event: The price change event to process
        """
        item_id = event.data.get("item_id")
        new_price = event.data.get("new_price")
        
        if item_id and new_price is not None:
            # Update price belief (with some skepticism if not our own change)
            current_belief = self.state["marketplace"]["price_beliefs"].get(item_id, 10)
            
            if event.source == self.id:
                # Our own price change, fully update
                self.state["marketplace"]["price_beliefs"][item_id] = new_price
            else:
                # Someone else's price change, partially update based on market knowledge
                market_knowledge = self.get_attribute("market_knowledge", 0.5)
                # More market knowledge means more trust in observed prices
                trust_factor = 0.3 + (0.4 * market_knowledge)
                new_belief = (1 - trust_factor) * current_belief + trust_factor * new_price
                self.state["marketplace"]["price_beliefs"][item_id] = new_belief
    
    def _process_item_listing_event(self, event: BaseEvent) -> None:
        """
        Process an item listing event.
        
        Args:
            event: The item listing event to process
        """
        item_id = event.data.get("item_id")
        price = event.data.get("price")
        
        if item_id and price is not None:
            # Update price belief (with some skepticism)
            current_belief = self.state["marketplace"]["price_beliefs"].get(item_id, 10)
            
            # Adjust trust based on market knowledge
            market_knowledge = self.get_attribute("market_knowledge", 0.5)
            trust_factor = 0.2 + (0.3 * market_knowledge)
            
            # Blend current belief with listed price
            new_belief = (1 - trust_factor) * current_belief + trust_factor * price
            self.state["marketplace"]["price_beliefs"][item_id] = new_belief
    
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
        self.state["marketplace"]["business_deals"].append({
            "deal_id": deal_id,
            "partner_id": partner_id,
            "terms": terms,
            "start_time": event.timestamp.timestamp(),
            "active": True,
        })
    
    def _process_deal_breach_event(self, event: BaseEvent) -> None:
        """
        Process a deal breach event.
        
        Args:
            event: The deal breach event to process
        """
        # Only process if this agent is involved
        if event.source != self.id and event.target != self.id:
            return
        
        deal_id = event.data.get("deal_id")
        severity = event.data.get("severity", 0.5)
        
        # Update the business deal status
        for deal in self.state["marketplace"]["business_deals"]:
            if deal["deal_id"] == deal_id:
                # Mark deal as inactive if breach is severe
                if severity > 0.7:
                    deal["active"] = False
                
                # Record the breach
                if "breaches" not in deal:
                    deal["breaches"] = []
                
                deal["breaches"].append({
                    "timestamp": event.timestamp.timestamp(),
                    "severity": severity,
                    "by_partner": event.source != self.id,
                })
                
                break
    
    def _process_market_trend_event(self, event: BaseEvent) -> None:
        """
        Process a market trend event.
        
        Args:
            event: The market trend event to process
        """
        trend_type = event.data.get("trend_type")
        affected_items = event.data.get("affected_items", {})
        impact = event.data.get("impact", 1.0)
        
        # Update price beliefs based on market trend
        for item_id, item_impact in affected_items.items():
            if item_id in self.state["marketplace"]["price_beliefs"]:
                current_price = self.state["marketplace"]["price_beliefs"][item_id]
                # Apply the trend impact, weighted by market knowledge
                market_knowledge = self.get_attribute("market_knowledge", 0.5)
                adjustment_factor = 0.5 + (0.5 * market_knowledge)  # More knowledge = more adjustment
                new_price = current_price * (1 + ((item_impact - 1) * adjustment_factor))
                self.state["marketplace"]["price_beliefs"][item_id] = max(1, new_price)
    
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
        action_types = ["trade", "price_change", "item_listing", "negotiation", "business_deal"]
        
        # Adjust weights based on agent attributes and state
        trading_skill = self.get_attribute("trading_skill", 0.5)
        negotiation_skill = self.get_attribute("negotiation_skill", 0.5)
        market_knowledge = self.get_attribute("market_knowledge", 0.5)
        
        weights = [
            0.4 * trading_skill,  # trade
            0.2 * market_knowledge,  # price_change
            0.2 * market_knowledge,  # item_listing
            0.1 * negotiation_skill,  # negotiation
            0.1 * negotiation_skill,  # business_deal
        ]
        
        action_type = random.choices(action_types, weights=weights, k=1)[0]
        
        # Need a target agent ID for the action
        # This would normally come from the agent manager, but for this example
        # we'll just use a placeholder that will be filled in by the simulation
        target_id = "TARGET_PLACEHOLDER"
        
        if action_type == "trade" and self.state["marketplace"]["inventory"]:
            return self._generate_trade_offer(target_id)
        elif action_type == "price_change" and self.state["marketplace"]["inventory"]:
            return self._generate_price_change()
        elif action_type == "item_listing" and self.state["marketplace"]["inventory"]:
            return self._generate_item_listing()
        elif action_type == "negotiation":
            return self._generate_negotiation(target_id)
        elif action_type == "business_deal":
            return self._generate_business_deal(target_id)
        
        return None
    
    def _generate_trade_offer(self, target_id: str) -> Optional[TradeEvent]:
        """
        Generate a trade offer based on inventory and price beliefs.
        
        Args:
            target_id: ID of the target agent
            
        Returns:
            Optional[TradeEvent]: A trade event, or None if no valid trade
        """
        # Choose an item to offer
        available_items = list(self.state["marketplace"]["inventory"].keys())
        if not available_items:
            return None
            
        offer_item_id = random.choice(available_items)
        offer_quantity = min(
            random.randint(1, 3),
            self.state["marketplace"]["inventory"][offer_item_id]
        )
        
        # Calculate the value of the offered items
        offer_value = offer_quantity * self.state["marketplace"]["price_beliefs"].get(offer_item_id, 10)
        
        # Choose what to request in return
        # Prefer items we don't have or specialty items
        potential_request_items = [
            item for item in self.state["marketplace"]["price_beliefs"].keys()
            if item not in self.state["marketplace"]["inventory"] or 
               item in self.state["marketplace"]["specialties"]
        ]
        
        if not potential_request_items:
            potential_request_items = list(self.state["marketplace"]["price_beliefs"].keys())
        
        request_item_id = random.choice(potential_request_items)
        
        # Calculate a fair quantity based on price beliefs
        request_price = self.state["marketplace"]["price_beliefs"].get(request_item_id, 10)
        
        # Apply profit margin to the trade
        profit_margin = self.state["marketplace"]["profit_margin"]
        desired_value = offer_value * (1 + profit_margin)
        
        request_quantity = max(1, round(desired_value / request_price))
        
        return TradeEvent(
            source=self.id,
            target=target_id,
            items_given={offer_item_id: offer_quantity},
            items_received={request_item_id: request_quantity}
        )
    
    def _generate_price_change(self) -> Optional[PriceChangeEvent]:
        """
        Generate a price change for an item in inventory.
        
        Returns:
            Optional[PriceChangeEvent]: A price change event, or None if no valid change
        """
        # Choose an item to change price for
        available_items = list(self.state["marketplace"]["inventory"].keys())
        if not available_items:
            return None
            
        item_id = random.choice(available_items)
        current_price = self.state["marketplace"]["price_beliefs"].get(item_id, 10)
        
        # Adjust price based on market conditions and strategy
        # For simplicity, we'll just randomly adjust up or down
        risk_tolerance = self.state["marketplace"]["risk_tolerance"]
        
        # Higher risk tolerance means more volatile price changes
        price_change_factor = random.uniform(-0.1, 0.15) * (0.5 + risk_tolerance)
        new_price = max(1, current_price * (1 + price_change_factor))
        
        return PriceChangeEvent(
            source=self.id,
            item_id=item_id,
            old_price=current_price,
            new_price=new_price
        )
    
    def _generate_item_listing(self) -> Optional[ItemListingEvent]:
        """
        Generate an item listing for an item in inventory.
        
        Returns:
            Optional[ItemListingEvent]: An item listing event, or None if no valid listing
        """
        # Choose an item to list
        available_items = list(self.state["marketplace"]["inventory"].keys())
        if not available_items:
            return None
            
        item_id = random.choice(available_items)
        quantity = min(
            random.randint(1, 5),
            self.state["marketplace"]["inventory"][item_id]
        )
        
        # Set price based on price belief and profit margin
        base_price = self.state["marketplace"]["price_beliefs"].get(item_id, 10)
        profit_margin = self.state["marketplace"]["profit_margin"]
        
        # Apply profit margin to the price
        price = base_price * (1 + profit_margin)
        
        return ItemListingEvent(
            source=self.id,
            item_id=item_id,
            quantity=quantity,
            price=price
        )
    
    def _generate_negotiation(self, target_id: str) -> Optional[NegotiationEvent]:
        """
        Generate a negotiation proposal.
        
        Args:
            target_id: ID of the target agent
            
        Returns:
            Optional[NegotiationEvent]: A negotiation event, or None if no valid proposal
        """
        # Choose an item to negotiate for
        available_items = list(self.state["marketplace"]["inventory"].keys())
        if not available_items:
            return None
            
        item_id = random.choice(available_items)
        quantity = min(
            random.randint(1, 3),
            self.state["marketplace"]["inventory"][item_id]
        )
        
        # Set price based on price belief and negotiation skill
        base_price = self.state["marketplace"]["price_beliefs"].get(item_id, 10)
        negotiation_skill = self.get_attribute("negotiation_skill", 0.5)
        
        # Better negotiators start with more favorable terms
        price_adjustment = 0.1 + (0.2 * negotiation_skill)
        proposed_price = base_price * (1 + price_adjustment)
        
        return NegotiationEvent(
            source=self.id,
            target=target_id,
            proposal={
                "item_id": item_id,
                "quantity": quantity,
                "price": proposed_price,
                "flexible": random.random() < negotiation_skill  # More skilled negotiators are more flexible
            }
        )
    
    def _generate_business_deal(self, target_id: str) -> Optional[BusinessDealEvent]:
        """
        Generate a business deal proposal.
        
        Args:
            target_id: ID of the target agent
            
        Returns:
            Optional[BusinessDealEvent]: A business deal event, or None if no valid deal
        """
        # Choose items for the deal
        specialty_items = [
            item for item in self.state["marketplace"]["inventory"].keys()
            if item in self.state["marketplace"]["specialties"]
        ]
        
        if not specialty_items:
            specialty_items = list(self.state["marketplace"]["inventory"].keys())
        
        if not specialty_items:
            return None
            
        deal_items = {}
        for item_id in random.sample(specialty_items, k=min(2, len(specialty_items))):
            quantity = min(
                random.randint(1, 3),
                self.state["marketplace"]["inventory"][item_id]
            )
            
            base_price = self.state["marketplace"]["price_beliefs"].get(item_id, 10)
            profit_margin = self.state["marketplace"]["profit_margin"]
            
            # Apply a slight discount for bulk deals
            price = base_price * (1 + profit_margin) * 0.95
            
            deal_items[item_id] = {
                "quantity": quantity,
                "price": price
            }
        
        if not deal_items:
            return None
            
        # Generate deal terms
        deal_id = f"deal_{random.randint(1000, 9999)}"
        duration = random.randint(5, 20)  # Number of time steps
        
        # More reputable merchants might offer exclusivity
        reputation = self.state["marketplace"]["reputation"]
        exclusivity = random.random() < (reputation * 0.5)
        
        return BusinessDealEvent(
            source=self.id,
            target=target_id,
            deal_id=deal_id,
            terms={
                "duration": duration,
                "items": deal_items,
                "exclusivity": exclusivity,
                "renewal_option": random.random() < 0.3
            }
        )