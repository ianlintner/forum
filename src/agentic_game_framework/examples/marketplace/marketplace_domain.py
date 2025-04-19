"""
Marketplace Domain Definition for Agentic Game Framework.

This module defines the marketplace domain and its extension points.
"""

from typing import Any, Dict, List, Optional, Set, Type

from ...agents.base_agent import BaseAgent
from ...domains.extension_points import (
    AgentBehaviorExtension,
    DomainConfigExtension,
    DomainExtensionPoint,
    EventTypeRegistry,
    MemoryTypeExtension,
    RelationshipTypeExtension,
)
from ...domains.domain_registry import register_component
from ...events.base import BaseEvent
from ...memory.memory_interface import MemoryItem
from ...relationships.base_relationship import BaseRelationship

# Domain identifier
MARKETPLACE_DOMAIN = "marketplace"


class MarketplaceEventRegistry(EventTypeRegistry):
    """
    Registry for marketplace-specific event types.
    
    This class registers all event types used in the marketplace domain,
    such as trade events, price change events, etc.
    """
    
    def register_event_types(self) -> Dict[str, Type[BaseEvent]]:
        """
        Register marketplace-specific event types.
        
        Returns:
            Dict[str, Type[BaseEvent]]: Map of event type IDs to event classes
        """
        from .marketplace_events import (
            TradeEvent,
            PriceChangeEvent,
            ItemListingEvent,
            NegotiationEvent,
            BusinessDealEvent,
        )
        
        return {
            "trade": TradeEvent,
            "price_change": PriceChangeEvent,
            "item_listing": ItemListingEvent,
            "negotiation": NegotiationEvent,
            "business_deal": BusinessDealEvent,
        }
    
    def get_event_type_metadata(self, event_type: str) -> Dict[str, Any]:
        """
        Get metadata for a specific event type.
        
        Args:
            event_type: Event type identifier
            
        Returns:
            Dict[str, Any]: Metadata for the event type
        """
        metadata = {
            "trade": {
                "description": "Exchange of items between agents",
                "affects_relationship": True,
                "relationship_impact_range": (-0.1, 0.2),
                "creates_memory": True,
                "memory_importance": 0.7,
            },
            "price_change": {
                "description": "Change in item price",
                "affects_relationship": False,
                "creates_memory": True,
                "memory_importance": 0.5,
            },
            "item_listing": {
                "description": "Item listed for sale",
                "affects_relationship": False,
                "creates_memory": True,
                "memory_importance": 0.4,
            },
            "negotiation": {
                "description": "Negotiation between agents",
                "affects_relationship": True,
                "relationship_impact_range": (-0.2, 0.1),
                "creates_memory": True,
                "memory_importance": 0.6,
            },
            "business_deal": {
                "description": "Long-term business arrangement",
                "affects_relationship": True,
                "relationship_impact_range": (0.1, 0.3),
                "creates_memory": True,
                "memory_importance": 0.8,
            },
        }
        
        return metadata.get(event_type, {})


class MarketplaceMemoryExtension(MemoryTypeExtension):
    """
    Extension for marketplace-specific memory types.
    
    This class defines custom memory types for the marketplace domain,
    such as transaction memories, price memories, etc.
    """
    
    def register_memory_types(self) -> Dict[str, Type[MemoryItem]]:
        """
        Register marketplace-specific memory types.
        
        Returns:
            Dict[str, Type[MemoryItem]]: Map of memory type IDs to memory classes
        """
        from .transaction_memory import (
            TransactionMemory,
            PriceMemory,
            BusinessDealMemory,
        )
        
        return {
            "transaction": TransactionMemory,
            "price": PriceMemory,
            "business_deal": BusinessDealMemory,
        }
    
    def create_memory_from_event(self, event: BaseEvent) -> Optional[MemoryItem]:
        """
        Create a domain-specific memory from an event.
        
        Args:
            event: The event to create a memory from
            
        Returns:
            Optional[MemoryItem]: The created memory, or None if not applicable
        """
        from .transaction_memory import (
            TransactionMemory,
            PriceMemory,
            BusinessDealMemory,
        )
        import time
        import uuid
        
        if event.event_type == "trade":
            return TransactionMemory(
                memory_id=f"transaction_{str(uuid.uuid4())}",
                timestamp=time.time(),
                event=event,
                importance=0.7,
            )
        elif event.event_type == "price_change":
            return PriceMemory(
                memory_id=f"price_{str(uuid.uuid4())}",
                timestamp=time.time(),
                event=event,
                importance=0.5,
            )
        elif event.event_type == "business_deal":
            return BusinessDealMemory(
                memory_id=f"deal_{str(uuid.uuid4())}",
                timestamp=time.time(),
                event=event,
                importance=0.8,
            )
        
        return None
    
    def enhance_memory_retrieval(
        self,
        query: Dict[str, Any],
        memories: List[MemoryItem]
    ) -> List[MemoryItem]:
        """
        Enhance memory retrieval with domain-specific logic.
        
        Args:
            query: The retrieval query
            memories: The initially retrieved memories
            
        Returns:
            List[MemoryItem]: The enhanced list of memories
        """
        # Sort by relevance to marketplace activities
        if "relevance" in query:
            if query["relevance"] == "price":
                # Prioritize price memories
                memories.sort(key=lambda m: 1.0 if hasattr(m, "price_data") else 0.5, reverse=True)
            elif query["relevance"] == "transaction":
                # Prioritize transaction memories
                memories.sort(key=lambda m: 1.0 if hasattr(m, "transaction_data") else 0.5, reverse=True)
            elif query["relevance"] == "business_deal":
                # Prioritize business deal memories
                memories.sort(key=lambda m: 1.0 if hasattr(m, "deal_data") else 0.5, reverse=True)
        
        return memories


class MarketplaceRelationshipExtension(RelationshipTypeExtension):
    """
    Extension for marketplace-specific relationship types.
    
    This class defines custom relationship types for the marketplace domain,
    such as business relationships, rivalries, etc.
    """
    
    def register_relationship_types(self) -> Dict[str, Type[BaseRelationship]]:
        """
        Register marketplace-specific relationship types.
        
        Returns:
            Dict[str, Type[BaseRelationship]]: Map of relationship type IDs to relationship classes
        """
        from .business_relationship import (
            BusinessRelationship,
            CompetitorRelationship,
            SupplierRelationship,
        )
        
        return {
            "business": BusinessRelationship,
            "competitor": CompetitorRelationship,
            "supplier": SupplierRelationship,
        }
    
    def create_default_relationships(
        self,
        agent_ids: List[str]
    ) -> List[BaseRelationship]:
        """
        Create default relationships between agents.
        
        Args:
            agent_ids: List of agent IDs
            
        Returns:
            List[BaseRelationship]: List of created relationships
        """
        from .business_relationship import (
            BusinessRelationship,
            CompetitorRelationship,
            SupplierRelationship,
        )
        import random
        
        relationships = []
        
        # Create a mix of relationship types between agents
        for i, agent_a_id in enumerate(agent_ids):
            for agent_b_id in agent_ids[i+1:]:
                # Randomly choose relationship type
                rel_type = random.choice(["business", "competitor", "supplier"])
                
                if rel_type == "business":
                    relationships.append(
                        BusinessRelationship(
                            agent_a_id=agent_a_id,
                            agent_b_id=agent_b_id,
                            strength=random.uniform(0.1, 0.5)
                        )
                    )
                elif rel_type == "competitor":
                    relationships.append(
                        CompetitorRelationship(
                            agent_a_id=agent_a_id,
                            agent_b_id=agent_b_id,
                            strength=random.uniform(-0.5, -0.1)
                        )
                    )
                elif rel_type == "supplier":
                    # Randomly decide which agent is the supplier
                    if random.random() > 0.5:
                        agent_a_id, agent_b_id = agent_b_id, agent_a_id
                        
                    relationships.append(
                        SupplierRelationship(
                            agent_a_id=agent_a_id,  # Supplier
                            agent_b_id=agent_b_id,  # Customer
                            strength=random.uniform(0.2, 0.6)
                        )
                    )
        
        return relationships
    
    def get_relationship_dynamics(
        self,
        relationship_type: str
    ) -> Dict[str, Any]:
        """
        Get dynamics information for a relationship type.
        
        Args:
            relationship_type: Relationship type identifier
            
        Returns:
            Dict[str, Any]: Dynamics information
        """
        dynamics = {
            "business": {
                "description": "Business relationship between agents",
                "default_strength": 0.3,
                "decay_rate": 0.01,  # How quickly it decays without interaction
                "event_impacts": {
                    "trade": 0.1,
                    "negotiation": 0.05,
                    "business_deal": 0.2,
                },
            },
            "competitor": {
                "description": "Competitive relationship between agents",
                "default_strength": -0.3,
                "decay_rate": 0.005,
                "event_impacts": {
                    "price_change": -0.05,
                    "item_listing": -0.02,
                },
            },
            "supplier": {
                "description": "Supplier-customer relationship",
                "default_strength": 0.4,
                "decay_rate": 0.02,
                "event_impacts": {
                    "trade": 0.15,
                    "price_change": -0.1,
                    "business_deal": 0.25,
                },
            },
        }
        
        return dynamics.get(relationship_type, {})


class MarketplaceAgentBehaviorExtension(AgentBehaviorExtension):
    """
    Extension for marketplace-specific agent behaviors.
    
    This class defines custom behaviors for agents in the marketplace domain,
    such as trading, negotiating, etc.
    """
    
    def extend_agent(self, agent: BaseAgent) -> None:
        """
        Extend an agent with marketplace-specific behaviors.
        
        Args:
            agent: The agent to extend
        """
        # Subscribe to marketplace events
        agent.subscribe_to_event("trade")
        agent.subscribe_to_event("price_change")
        agent.subscribe_to_event("item_listing")
        agent.subscribe_to_event("negotiation")
        agent.subscribe_to_event("business_deal")
        
        # Initialize marketplace-specific state
        if "marketplace" not in agent.state:
            agent.state["marketplace"] = {
                "inventory": {},
                "price_beliefs": {},
                "trade_history": [],
                "business_deals": [],
            }
    
    def process_domain_event(self, agent: BaseAgent, event: BaseEvent) -> None:
        """
        Process a marketplace-specific event for an agent.
        
        Args:
            agent: The agent processing the event
            event: The event to process
        """
        if event.event_type == "trade" and (event.source == agent.id or event.target == agent.id):
            self._process_trade_event(agent, event)
        elif event.event_type == "price_change":
            self._process_price_change_event(agent, event)
        elif event.event_type == "item_listing":
            self._process_item_listing_event(agent, event)
        elif event.event_type == "negotiation" and (event.source == agent.id or event.target == agent.id):
            self._process_negotiation_event(agent, event)
        elif event.event_type == "business_deal" and (event.source == agent.id or event.target == agent.id):
            self._process_business_deal_event(agent, event)
    
    def _process_trade_event(self, agent: BaseAgent, event: BaseEvent) -> None:
        """Process a trade event."""
        # Extract trade details
        items_given = event.data.get("items_given", {})
        items_received = event.data.get("items_received", {})
        
        # Update inventory based on whether agent is source or target
        if event.source == agent.id:
            # Agent is giving items
            for item_id, quantity in items_given.items():
                if item_id in agent.state["marketplace"]["inventory"]:
                    agent.state["marketplace"]["inventory"][item_id] -= quantity
                    if agent.state["marketplace"]["inventory"][item_id] <= 0:
                        del agent.state["marketplace"]["inventory"][item_id]
            
            # Agent is receiving items
            for item_id, quantity in items_received.items():
                if item_id not in agent.state["marketplace"]["inventory"]:
                    agent.state["marketplace"]["inventory"][item_id] = 0
                agent.state["marketplace"]["inventory"][item_id] += quantity
        
        elif event.target == agent.id:
            # Agent is receiving items
            for item_id, quantity in items_given.items():
                if item_id not in agent.state["marketplace"]["inventory"]:
                    agent.state["marketplace"]["inventory"][item_id] = 0
                agent.state["marketplace"]["inventory"][item_id] += quantity
            
            # Agent is giving items
            for item_id, quantity in items_received.items():
                if item_id in agent.state["marketplace"]["inventory"]:
                    agent.state["marketplace"]["inventory"][item_id] -= quantity
                    if agent.state["marketplace"]["inventory"][item_id] <= 0:
                        del agent.state["marketplace"]["inventory"][item_id]
        
        # Record trade in history
        agent.state["marketplace"]["trade_history"].append({
            "timestamp": event.timestamp.timestamp(),
            "partner_id": event.source if event.target == agent.id else event.target,
            "items_given": items_received if event.source == agent.id else items_given,
            "items_received": items_given if event.source == agent.id else items_received,
        })
    
    def _process_price_change_event(self, agent: BaseAgent, event: BaseEvent) -> None:
        """Process a price change event."""
        item_id = event.data.get("item_id")
        new_price = event.data.get("new_price")
        
        if item_id and new_price is not None:
            # Update price belief
            agent.state["marketplace"]["price_beliefs"][item_id] = new_price
    
    def _process_item_listing_event(self, agent: BaseAgent, event: BaseEvent) -> None:
        """Process an item listing event."""
        item_id = event.data.get("item_id")
        price = event.data.get("price")
        
        if item_id and price is not None:
            # Update price belief
            agent.state["marketplace"]["price_beliefs"][item_id] = price
    
    def _process_negotiation_event(self, agent: BaseAgent, event: BaseEvent) -> None:
        """Process a negotiation event."""
        # Negotiations might affect future trades but don't directly change inventory
        pass
    
    def _process_business_deal_event(self, agent: BaseAgent, event: BaseEvent) -> None:
        """Process a business deal event."""
        deal_id = event.data.get("deal_id")
        partner_id = event.source if event.target == agent.id else event.target
        terms = event.data.get("terms", {})
        
        # Record the business deal
        agent.state["marketplace"]["business_deals"].append({
            "deal_id": deal_id,
            "partner_id": partner_id,
            "terms": terms,
            "start_time": event.timestamp.timestamp(),
            "active": True,
        })
    
    def generate_domain_actions(self, agent: BaseAgent) -> List[BaseEvent]:
        """
        Generate marketplace-specific actions for an agent.
        
        Args:
            agent: The agent generating actions
            
        Returns:
            List[BaseEvent]: List of generated events
        """
        from .marketplace_events import (
            TradeEvent,
            PriceChangeEvent,
            ItemListingEvent,
            NegotiationEvent,
            BusinessDealEvent,
        )
        import random
        
        actions = []
        
        # Only generate actions occasionally
        if random.random() < 0.3:
            # Choose an action type based on agent state
            action_types = ["trade", "price_change", "item_listing", "negotiation", "business_deal"]
            weights = [0.4, 0.2, 0.2, 0.1, 0.1]  # Trade is most common
            
            action_type = random.choices(action_types, weights=weights, k=1)[0]
            
            if action_type == "trade" and agent.state["marketplace"]["inventory"]:
                # Find a target agent (placeholder, would be replaced in simulation)
                target_id = "TARGET_PLACEHOLDER"
                
                # Choose an item to trade
                available_items = list(agent.state["marketplace"]["inventory"].keys())
                if available_items:
                    item_id = random.choice(available_items)
                    quantity = min(
                        random.randint(1, 3),
                        agent.state["marketplace"]["inventory"][item_id]
                    )
                    
                    # Choose what to request in return
                    request_item_id = random.choice(["gold", "silver", "food", "tools"])
                    request_quantity = random.randint(1, 3)
                    
                    actions.append(
                        TradeEvent(
                            source=agent.id,
                            target=target_id,
                            items_given={item_id: quantity},
                            items_received={request_item_id: request_quantity}
                        )
                    )
            
            elif action_type == "price_change" and agent.state["marketplace"]["inventory"]:
                # Choose an item to change price for
                available_items = list(agent.state["marketplace"]["inventory"].keys())
                if available_items:
                    item_id = random.choice(available_items)
                    current_price = agent.state["marketplace"]["price_beliefs"].get(item_id, 10)
                    
                    # Adjust price up or down
                    price_change = random.uniform(-0.2, 0.3) * current_price
                    new_price = max(1, current_price + price_change)
                    
                    actions.append(
                        PriceChangeEvent(
                            source=agent.id,
                            item_id=item_id,
                            old_price=current_price,
                            new_price=new_price
                        )
                    )
            
            elif action_type == "item_listing" and agent.state["marketplace"]["inventory"]:
                # Choose an item to list
                available_items = list(agent.state["marketplace"]["inventory"].keys())
                if available_items:
                    item_id = random.choice(available_items)
                    quantity = min(
                        random.randint(1, 5),
                        agent.state["marketplace"]["inventory"][item_id]
                    )
                    
                    price = agent.state["marketplace"]["price_beliefs"].get(item_id, 10)
                    
                    actions.append(
                        ItemListingEvent(
                            source=agent.id,
                            item_id=item_id,
                            quantity=quantity,
                            price=price
                        )
                    )
            
            elif action_type == "negotiation":
                # Find a target agent (placeholder, would be replaced in simulation)
                target_id = "TARGET_PLACEHOLDER"
                
                actions.append(
                    NegotiationEvent(
                        source=agent.id,
                        target=target_id,
                        proposal={
                            "item_id": random.choice(["gold", "silver", "food", "tools"]),
                            "quantity": random.randint(1, 5),
                            "price": random.randint(5, 20)
                        }
                    )
                )
            
            elif action_type == "business_deal":
                # Find a target agent (placeholder, would be replaced in simulation)
                target_id = "TARGET_PLACEHOLDER"
                
                actions.append(
                    BusinessDealEvent(
                        source=agent.id,
                        target=target_id,
                        deal_id=f"deal_{random.randint(1000, 9999)}",
                        terms={
                            "duration": random.randint(5, 20),
                            "items": {
                                random.choice(["gold", "silver", "food", "tools"]): {
                                    "quantity": random.randint(1, 5),
                                    "price": random.randint(5, 20)
                                }
                            },
                            "exclusivity": random.random() > 0.7
                        }
                    )
                )
        
        return actions


class MarketplaceConfigExtension(DomainConfigExtension):
    """
    Extension for marketplace-specific configuration.
    
    This class defines configuration parameters for the marketplace domain,
    such as item types, price ranges, etc.
    """
    
    def get_default_config(self) -> Dict[str, Any]:
        """
        Get the default configuration for the marketplace domain.
        
        Returns:
            Dict[str, Any]: Default configuration
        """
        return {
            "item_types": [
                "gold",
                "silver",
                "food",
                "tools",
                "clothing",
                "luxury_goods",
                "raw_materials",
                "crafted_goods",
            ],
            "price_ranges": {
                "gold": (15, 25),
                "silver": (8, 15),
                "food": (3, 8),
                "tools": (5, 12),
                "clothing": (7, 18),
                "luxury_goods": (20, 40),
                "raw_materials": (2, 6),
                "crafted_goods": (10, 20),
            },
            "starting_inventory": {
                "merchant": {
                    "gold": (2, 5),
                    "silver": (5, 10),
                    "luxury_goods": (1, 3),
                    "crafted_goods": (3, 8),
                },
                "customer": {
                    "gold": (5, 15),
                    "food": (3, 8),
                    "raw_materials": (2, 6),
                },
            },
            "trade_frequency": 0.3,  # Probability of trade action
            "price_change_frequency": 0.1,  # Probability of price change
            "negotiation_success_rate": 0.6,  # Probability of successful negotiation
            "business_deal_duration": (5, 20),  # Range of business deal durations
        }
    
    def validate_config(self, config: Dict[str, Any]) -> List[str]:
        """
        Validate a configuration for the marketplace domain.
        
        Args:
            config: Configuration to validate
            
        Returns:
            List[str]: List of validation errors, empty if valid
        """
        errors = []
        
        # Check required sections
        required_sections = ["item_types", "price_ranges", "starting_inventory"]
        for section in required_sections:
            if section not in config:
                errors.append(f"Missing required section: {section}")
        
        # Validate item types
        if "item_types" in config and not isinstance(config["item_types"], list):
            errors.append("item_types must be a list")
        
        # Validate price ranges
        if "price_ranges" in config:
            if not isinstance(config["price_ranges"], dict):
                errors.append("price_ranges must be a dictionary")
            else:
                for item, price_range in config["price_ranges"].items():
                    if not isinstance(price_range, tuple) or len(price_range) != 2:
                        errors.append(f"Price range for {item} must be a tuple of (min, max)")
                    elif price_range[0] >= price_range[1]:
                        errors.append(f"Price range for {item} must have min < max")
        
        # Validate starting inventory
        if "starting_inventory" in config:
            if not isinstance(config["starting_inventory"], dict):
                errors.append("starting_inventory must be a dictionary")
            else:
                for agent_type, inventory in config["starting_inventory"].items():
                    if not isinstance(inventory, dict):
                        errors.append(f"Inventory for {agent_type} must be a dictionary")
                    else:
                        for item, quantity_range in inventory.items():
                            if not isinstance(quantity_range, tuple) or len(quantity_range) != 2:
                                errors.append(f"Quantity range for {item} must be a tuple of (min, max)")
                            elif quantity_range[0] > quantity_range[1]:
                                errors.append(f"Quantity range for {item} must have min <= max")
        
        return errors
    
    def apply_config(self, config: Dict[str, Any]) -> None:
        """
        Apply a configuration to the marketplace domain.
        
        Args:
            config: Configuration to apply
        """
        # This would typically update global state or registries
        # For this example, we'll just print the configuration
        print(f"Applying marketplace configuration with {len(config['item_types'])} item types")


def register_marketplace_domain():
    """
    Register all marketplace domain components with the global registry.
    """
    # Register event types
    register_component(
        "event_registry",
        MARKETPLACE_DOMAIN,
        MarketplaceEventRegistry
    )
    
    # Register memory types
    register_component(
        "memory_extension",
        MARKETPLACE_DOMAIN,
        MarketplaceMemoryExtension
    )
    
    # Register relationship types
    register_component(
        "relationship_extension",
        MARKETPLACE_DOMAIN,
        MarketplaceRelationshipExtension
    )
    
    # Register agent behaviors
    register_component(
        "agent_behavior",
        MARKETPLACE_DOMAIN,
        MarketplaceAgentBehaviorExtension
    )
    
    # Register configuration
    register_component(
        "domain_config",
        MARKETPLACE_DOMAIN,
        MarketplaceConfigExtension
    )
    
    print(f"Registered marketplace domain with ID: {MARKETPLACE_DOMAIN}")


# Register the domain when this module is imported
register_marketplace_domain()