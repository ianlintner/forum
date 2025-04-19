"""
Marketplace Simulation for Agentic Game Framework.

This module provides a simulation runner for the marketplace domain,
demonstrating how merchants and customers interact through events.
"""

import random
import time
from typing import Dict, List, Optional

from ...agents.agent_factory import AgentFactory
from ...agents.agent_manager import AgentManager
from ...events.event_bus import EventBus
from ...relationships.relationship_manager import RelationshipManager
from .customer_agent import CustomerAgent
from .merchant_agent import MerchantAgent
from .marketplace_events import (
    TradeEvent,
    PriceChangeEvent,
    ItemListingEvent,
    NegotiationEvent,
    BusinessDealEvent,
    MarketTrendEvent,
)


class MarketplaceSimulation:
    """
    Simulation runner for the marketplace domain.
    
    This class sets up and runs a marketplace simulation with merchants
    and customers interacting through various events.
    
    Attributes:
        agent_manager: Manager for all agents in the simulation
        event_bus: Event bus for event distribution
        relationship_manager: Manager for agent relationships
        config: Simulation configuration
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize a new marketplace simulation.
        
        Args:
            config: Optional configuration for the simulation
        """
        self.config = config or self._get_default_config()
        
        # Initialize core components
        self.event_bus = EventBus()
        self.agent_factory = AgentFactory()
        self.agent_manager = AgentManager(self.event_bus)
        self.relationship_manager = RelationshipManager(self.event_bus)
        
        # Register agent types
        self.agent_factory.register_agent_type("merchant", MerchantAgent)
        self.agent_factory.register_agent_type("customer", CustomerAgent)
        
        # Initialize simulation state
        self.merchants = []
        self.customers = []
        self.market_trends = []
        self.step_count = 0
    
    def _get_default_config(self) -> Dict:
        """
        Get the default simulation configuration.
        
        Returns:
            Dict: Default configuration
        """
        return {
            "num_merchants": 3,
            "num_customers": 5,
            "max_steps": 20,
            "step_delay": 0.5,  # seconds between steps
            "market_trend_probability": 0.1,
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
            "merchant_specialties": {
                "Blacksmith": ["tools", "raw_materials"],
                "Jeweler": ["gold", "silver", "luxury_goods"],
                "Tailor": ["clothing", "luxury_goods"],
                "Farmer": ["food", "raw_materials"],
                "Craftsman": ["crafted_goods", "tools"],
            },
            "customer_needs": {
                "Noble": {"luxury_goods": 0.9, "clothing": 0.7, "crafted_goods": 0.5},
                "Soldier": {"tools": 0.8, "food": 0.6, "clothing": 0.4},
                "Farmer": {"tools": 0.7, "food": 0.3, "raw_materials": 0.5},
                "Merchant": {"gold": 0.6, "silver": 0.6, "luxury_goods": 0.4},
                "Craftsman": {"tools": 0.5, "raw_materials": 0.9, "food": 0.4},
            },
        }
    
    def setup(self) -> None:
        """
        Set up the simulation by creating agents and relationships.
        """
        print("Setting up marketplace simulation...")
        
        # Create merchant agents
        for i in range(self.config["num_merchants"]):
            # Choose a merchant type or use a generic name
            if i < len(self.config["merchant_specialties"]):
                merchant_type = list(self.config["merchant_specialties"].keys())[i]
                specialties = self.config["merchant_specialties"][merchant_type]
                name = f"{merchant_type} {i+1}"
            else:
                merchant_type = "Generic"
                specialties = random.sample(self.config["item_types"], k=random.randint(2, 4))
                name = f"Merchant {i+1}"
            
            # Create and register the merchant
            merchant = self.agent_factory.create_agent(
                agent_type="merchant",
                name=name,
                attributes={"merchant_type": merchant_type},
                specialties=specialties
            )
            
            self.agent_manager.register_agent(merchant)
            self.merchants.append(merchant)
            
            print(f"Created merchant: {merchant.name} specializing in {', '.join(specialties)}")
        
        # Create customer agents
        for i in range(self.config["num_customers"]):
            # Choose a customer type or use a generic name
            if i < len(self.config["customer_needs"]):
                customer_type = list(self.config["customer_needs"].keys())[i]
                needs = self.config["customer_needs"][customer_type]
                name = f"{customer_type} {i+1}"
            else:
                customer_type = "Generic"
                # Generate random needs
                all_items = self.config["item_types"]
                num_needs = random.randint(2, 4)
                selected_items = random.sample(all_items, k=num_needs)
                
                needs = {
                    item: random.uniform(0.3, 1.0)
                    for item in selected_items
                }
                name = f"Customer {i+1}"
            
            # Create and register the customer
            customer = self.agent_factory.create_agent(
                agent_type="customer",
                name=name,
                attributes={"customer_type": customer_type},
                needs=needs
            )
            
            self.agent_manager.register_agent(customer)
            self.customers.append(customer)
            
            print(f"Created customer: {customer.name} needing {', '.join(needs.keys())}")
        
        # Create initial relationships
        print("Establishing initial relationships...")
        self._setup_initial_relationships()
        
        # Subscribe to events for logging
        self.event_bus.subscribe("trade", self._log_trade_event)
        self.event_bus.subscribe("price_change", self._log_price_change_event)
        self.event_bus.subscribe("item_listing", self._log_item_listing_event)
        self.event_bus.subscribe("negotiation", self._log_negotiation_event)
        self.event_bus.subscribe("business_deal", self._log_business_deal_event)
        self.event_bus.subscribe("market_trend", self._log_market_trend_event)
    
    def _setup_initial_relationships(self) -> None:
        """
        Set up initial relationships between agents.
        """
        # Create relationships between merchants (competitors)
        for i, merchant_a in enumerate(self.merchants):
            for merchant_b in self.merchants[i+1:]:
                # Check if they have overlapping specialties
                specialties_a = merchant_a.state["marketplace"]["specialties"]
                specialties_b = merchant_b.state["marketplace"]["specialties"]
                
                if set(specialties_a).intersection(set(specialties_b)):
                    # They are competitors
                    strength = random.uniform(-0.5, -0.1)
                    relationship = self.relationship_manager.create_relationship(
                        "competitor",
                        merchant_a.id,
                        merchant_b.id,
                        strength
                    )
                    print(f"Created competitor relationship between {merchant_a.name} and {merchant_b.name}")
                else:
                    # They are business partners
                    strength = random.uniform(0.1, 0.4)
                    relationship = self.relationship_manager.create_relationship(
                        "business",
                        merchant_a.id,
                        merchant_b.id,
                        strength
                    )
                    print(f"Created business relationship between {merchant_a.name} and {merchant_b.name}")
        
        # Create relationships between merchants and customers
        for merchant in self.merchants:
            for customer in self.customers:
                # Check if merchant specialties match customer needs
                specialties = merchant.state["marketplace"]["specialties"]
                needs = customer.state["marketplace"]["needs"]
                
                matching_items = set(specialties).intersection(set(needs.keys()))
                
                if matching_items:
                    # They have a supplier relationship
                    strength = random.uniform(0.2, 0.6)
                    relationship = self.relationship_manager.create_relationship(
                        "supplier",
                        merchant.id,
                        customer.id,
                        strength
                    )
                    print(f"Created supplier relationship between {merchant.name} and {customer.name}")
                else:
                    # They have a basic business relationship
                    strength = random.uniform(0.0, 0.3)
                    relationship = self.relationship_manager.create_relationship(
                        "business",
                        merchant.id,
                        customer.id,
                        strength
                    )
                    print(f"Created business relationship between {merchant.name} and {customer.name}")
    
    def run(self, max_steps: Optional[int] = None) -> None:
        """
        Run the simulation for a specified number of steps.
        
        Args:
            max_steps: Maximum number of simulation steps (overrides config)
        """
        steps = max_steps or self.config["max_steps"]
        
        print(f"\nStarting marketplace simulation for {steps} steps...")
        
        for step in range(steps):
            self.step_count = step + 1
            print(f"\n--- Step {self.step_count} ---")
            
            # Run a simulation step
            self._run_step()
            
            # Wait between steps
            time.sleep(self.config["step_delay"])
        
        print("\nSimulation complete!")
        self._print_summary()
    
    def _run_step(self) -> None:
        """
        Run a single simulation step.
        """
        # 1. Generate market trends (occasionally)
        if random.random() < self.config["market_trend_probability"]:
            self._generate_market_trend()
        
        # 2. Let agents generate actions
        self._generate_agent_actions()
        
        # 3. Process all pending events
        self.event_bus.process_events()
        
        # 4. Update relationships based on events
        self.relationship_manager.update_relationships()
    
    def _generate_market_trend(self) -> None:
        """
        Generate a market-wide trend event.
        """
        trend_types = ["inflation", "scarcity", "surplus", "demand_increase", "demand_decrease"]
        trend_type = random.choice(trend_types)
        
        # Determine which items are affected
        num_affected_items = random.randint(1, 3)
        affected_items = {}
        
        for _ in range(num_affected_items):
            item_id = random.choice(self.config["item_types"])
            
            # Determine impact based on trend type
            if trend_type in ["inflation", "scarcity", "demand_increase"]:
                # Price increase
                impact = random.uniform(1.05, 1.3)
            else:
                # Price decrease
                impact = random.uniform(0.7, 0.95)
            
            affected_items[item_id] = impact
        
        # Create and publish the event
        event = MarketTrendEvent(
            trend_type=trend_type,
            affected_items=affected_items,
            impact=list(affected_items.values())[0]  # Use first item's impact as overall impact
        )
        
        self.event_bus.publish(event)
        self.market_trends.append(event)
    
    def _generate_agent_actions(self) -> None:
        """
        Let all agents generate actions.
        """
        # Let merchants generate actions
        for merchant in self.merchants:
            action = merchant.generate_action()
            if action:
                # Replace placeholder target with actual target
                if hasattr(action, "target") and action.target == "TARGET_PLACEHOLDER":
                    # Choose a random customer as target
                    action.target = random.choice(self.customers).id
                
                # Publish the action as an event
                self.event_bus.publish(action)
        
        # Let customers generate actions
        for customer in self.customers:
            action = customer.generate_action()
            if action:
                # Replace placeholder target with actual target
                if hasattr(action, "target") and action.target == "TARGET_PLACEHOLDER":
                    # Choose a random merchant as target
                    action.target = random.choice(self.merchants).id
                
                # Publish the action as an event
                self.event_bus.publish(action)
    
    def _log_trade_event(self, event: TradeEvent) -> None:
        """
        Log a trade event.
        
        Args:
            event: The trade event to log
        """
        source_agent = self.agent_manager.get_agent(event.source)
        target_agent = self.agent_manager.get_agent(event.target)
        
        if not source_agent or not target_agent:
            return
        
        items_given_str = ", ".join(
            f"{qty} {item}" for item, qty in event.data.get("items_given", {}).items()
        )
        
        items_received_str = ", ".join(
            f"{qty} {item}" for item, qty in event.data.get("items_received", {}).items()
        )
        
        print(f"TRADE: {source_agent.name} gave {items_given_str} to {target_agent.name} "
              f"and received {items_received_str}")
    
    def _log_price_change_event(self, event: PriceChangeEvent) -> None:
        """
        Log a price change event.
        
        Args:
            event: The price change event to log
        """
        source_agent = self.agent_manager.get_agent(event.source)
        
        if not source_agent:
            return
        
        item_id = event.data.get("item_id")
        old_price = event.data.get("old_price")
        new_price = event.data.get("new_price")
        
        change_type = "increased" if new_price > old_price else "decreased"
        
        print(f"PRICE CHANGE: {source_agent.name} {change_type} price of {item_id} "
              f"from {old_price:.2f} to {new_price:.2f}")
    
    def _log_item_listing_event(self, event: ItemListingEvent) -> None:
        """
        Log an item listing event.
        
        Args:
            event: The item listing event to log
        """
        source_agent = self.agent_manager.get_agent(event.source)
        
        if not source_agent:
            return
        
        item_id = event.data.get("item_id")
        quantity = event.data.get("quantity")
        price = event.data.get("price")
        
        print(f"LISTING: {source_agent.name} listed {quantity} {item_id} for sale at {price:.2f} each")
    
    def _log_negotiation_event(self, event: NegotiationEvent) -> None:
        """
        Log a negotiation event.
        
        Args:
            event: The negotiation event to log
        """
        source_agent = self.agent_manager.get_agent(event.source)
        target_agent = self.agent_manager.get_agent(event.target)
        
        if not source_agent or not target_agent:
            return
        
        proposal = event.data.get("proposal", {})
        is_counter = event.data.get("is_counter", False)
        
        proposal_type = "counter-proposal" if is_counter else "proposal"
        
        print(f"NEGOTIATION: {source_agent.name} made a {proposal_type} to {target_agent.name}: "
              f"{proposal}")
    
    def _log_business_deal_event(self, event: BusinessDealEvent) -> None:
        """
        Log a business deal event.
        
        Args:
            event: The business deal event to log
        """
        source_agent = self.agent_manager.get_agent(event.source)
        target_agent = self.agent_manager.get_agent(event.target)
        
        if not source_agent or not target_agent:
            return
        
        deal_id = event.data.get("deal_id")
        terms = event.data.get("terms", {})
        
        print(f"BUSINESS DEAL: {source_agent.name} established deal {deal_id} with {target_agent.name}: "
              f"{terms}")
    
    def _log_market_trend_event(self, event: MarketTrendEvent) -> None:
        """
        Log a market trend event.
        
        Args:
            event: The market trend event to log
        """
        trend_type = event.data.get("trend_type")
        affected_items = event.data.get("affected_items", {})
        impact = event.data.get("impact")
        
        direction = "up" if impact > 1.0 else "down"
        
        affected_items_str = ", ".join(
            f"{item} ({impact:.2f}x)" for item, impact in affected_items.items()
        )
        
        print(f"MARKET TREND: {trend_type} causing prices to trend {direction}. "
              f"Affected items: {affected_items_str}")
    
    def _print_summary(self) -> None:
        """
        Print a summary of the simulation results.
        """
        print("\n=== Simulation Summary ===")
        print(f"Steps completed: {self.step_count}")
        print(f"Agents: {len(self.merchants)} merchants, {len(self.customers)} customers")
        print(f"Market trends: {len(self.market_trends)}")
        
        # Print merchant summaries
        print("\n--- Merchant Summary ---")
        for merchant in self.merchants:
            inventory_str = ", ".join(
                f"{item}: {qty}" for item, qty in merchant.state["marketplace"]["inventory"].items()
            )
            
            trade_count = len(merchant.state["marketplace"]["trade_history"])
            deal_count = len(merchant.state["marketplace"]["business_deals"])
            
            print(f"{merchant.name}:")
            print(f"  Inventory: {inventory_str}")
            print(f"  Trades: {trade_count}")
            print(f"  Business Deals: {deal_count}")
        
        # Print customer summaries
        print("\n--- Customer Summary ---")
        for customer in self.customers:
            inventory_str = ", ".join(
                f"{item}: {qty}" for item, qty in customer.state["marketplace"]["inventory"].items()
            )
            
            purchase_count = len(customer.state["marketplace"]["purchase_history"])
            satisfaction = customer.state["marketplace"]["satisfaction"]
            
            print(f"{customer.name}:")
            print(f"  Inventory: {inventory_str}")
            print(f"  Purchases: {purchase_count}")
            print(f"  Satisfaction: {satisfaction:.2f}")
        
        # Print relationship summary
        print("\n--- Relationship Summary ---")
        relationships = self.relationship_manager.get_all_relationships()
        
        relationship_types = {}
        for rel in relationships:
            rel_type = rel.relationship_type
            if rel_type not in relationship_types:
                relationship_types[rel_type] = []
            relationship_types[rel_type].append(rel)
        
        for rel_type, rels in relationship_types.items():
            avg_strength = sum(rel.strength for rel in rels) / len(rels)
            print(f"{rel_type.capitalize()} relationships: {len(rels)}, avg strength: {avg_strength:.2f}")


def run_marketplace_simulation(num_merchants: int = 3, num_customers: int = 5, max_steps: int = 20) -> None:
    """
    Run a marketplace simulation with the specified parameters.
    
    Args:
        num_merchants: Number of merchant agents
        num_customers: Number of customer agents
        max_steps: Maximum number of simulation steps
    """
    config = {
        "num_merchants": num_merchants,
        "num_customers": num_customers,
        "max_steps": max_steps,
        "step_delay": 0.5,
        "market_trend_probability": 0.1,
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
        "merchant_specialties": {
            "Blacksmith": ["tools", "raw_materials"],
            "Jeweler": ["gold", "silver", "luxury_goods"],
            "Tailor": ["clothing", "luxury_goods"],
            "Farmer": ["food", "raw_materials"],
            "Craftsman": ["crafted_goods", "tools"],
        },
        "customer_needs": {
            "Noble": {"luxury_goods": 0.9, "clothing": 0.7, "crafted_goods": 0.5},
            "Soldier": {"tools": 0.8, "food": 0.6, "clothing": 0.4},
            "Farmer": {"tools": 0.7, "food": 0.3, "raw_materials": 0.5},
            "Merchant": {"gold": 0.6, "silver": 0.6, "luxury_goods": 0.4},
            "Craftsman": {"tools": 0.5, "raw_materials": 0.9, "food": 0.4},
        },
    }
    
    simulation = MarketplaceSimulation(config)
    simulation.setup()
    simulation.run()


if __name__ == "__main__":
    run_marketplace_simulation()