"""
Simple Simulation Example for Agentic Game Framework.

This example demonstrates a basic simulation with agents interacting through
events and forming relationships.
"""

import random
import time
from typing import Dict, List, Optional

from ..agents.agent_factory import AgentFactory
from ..agents.agent_manager import AgentManager
from ..agents.base_agent import BaseAgent
from ..events.base import BaseEvent
from ..events.event_bus import EventBus
from ..memory.memory_interface import MemoryItem
from ..memory.persistence import MemoryStore
from ..relationships.base_relationship import SimpleRelationship
from ..relationships.relationship_manager import RelationshipManager


# Define custom event types
class GreetingEvent(BaseEvent):
    """Event representing a greeting from one agent to another."""
    
    def __init__(self, source: str, target: str, greeting_type: str = "neutral"):
        super().__init__(
            event_type="greeting",
            source=source,
            target=target,
            data={
                "greeting_type": greeting_type,
                "relationship_impact": {
                    "friendly": 0.1,
                    "neutral": 0.0,
                    "hostile": -0.1
                }[greeting_type]
            }
        )


class TradeEvent(BaseEvent):
    """Event representing a trade between agents."""
    
    def __init__(
        self,
        source: str,
        target: str,
        offer: Dict[str, int],
        request: Dict[str, int]
    ):
        super().__init__(
            event_type="trade",
            source=source,
            target=target,
            data={
                "offer": offer,
                "request": request,
                "relationship_impact": 0.05,  # Trading is generally positive
                "participants": [source, target]
            }
        )


class DisputeEvent(BaseEvent):
    """Event representing a dispute between agents."""
    
    def __init__(self, source: str, target: str, severity: float = 0.5):
        super().__init__(
            event_type="dispute",
            source=source,
            target=target,
            data={
                "severity": severity,
                "relationship_impact": -0.1 * severity,  # Disputes damage relationships
                "participants": [source, target]
            }
        )


# Define a simple agent implementation
class SimpleAgent(BaseAgent):
    """
    A simple agent implementation that can greet, trade, and dispute with other agents.
    """
    
    def __init__(
        self,
        name: str,
        attributes: Optional[Dict[str, any]] = None,
        agent_id: Optional[str] = None
    ):
        # Initialize with some resources
        initial_state = {
            "resources": {
                "food": random.randint(5, 15),
                "gold": random.randint(3, 10),
                "wood": random.randint(8, 20)
            },
            "mood": random.uniform(0.3, 0.8),  # 0.0 = angry, 1.0 = happy
            "last_action_time": 0
        }
        
        super().__init__(name, attributes, agent_id, initial_state)
        
        # Subscribe to relevant event types
        self.subscribe_to_event("greeting")
        self.subscribe_to_event("trade")
        self.subscribe_to_event("dispute")
        
        # Create a memory store for this agent
        self.memory = MemoryStore(self.id)
    
    def process_event(self, event: BaseEvent) -> None:
        """Process an incoming event."""
        # Store the event in memory
        memory_item = MemoryItem(
            memory_id=f"memory_{event.get_id()}",
            timestamp=time.time(),
            content=event.to_dict(),
            importance=0.5
        )
        self.memory.add_memory(memory_item)
        
        # Process different event types
        if event.event_type == "greeting":
            self._process_greeting(event)
        elif event.event_type == "trade":
            self._process_trade(event)
        elif event.event_type == "dispute":
            self._process_dispute(event)
    
    def _process_greeting(self, event: BaseEvent) -> None:
        """Process a greeting event."""
        if event.target == self.id:
            greeting_type = event.data.get("greeting_type", "neutral")
            
            # Update mood based on greeting type
            mood_change = {
                "friendly": 0.05,
                "neutral": 0.0,
                "hostile": -0.05
            }[greeting_type]
            
            self.state["mood"] = min(1.0, max(0.0, self.state["mood"] + mood_change))
    
    def _process_trade(self, event: BaseEvent) -> None:
        """Process a trade event."""
        if event.target == self.id:
            # Extract trade details
            offer = event.data.get("offer", {})
            request = event.data.get("request", {})
            
            # Check if we can fulfill the request
            can_fulfill = True
            for resource, amount in request.items():
                if self.state["resources"].get(resource, 0) < amount:
                    can_fulfill = False
                    break
            
            # If we can fulfill, complete the trade
            if can_fulfill:
                # Give requested resources
                for resource, amount in request.items():
                    self.state["resources"][resource] -= amount
                
                # Receive offered resources
                for resource, amount in offer.items():
                    if resource not in self.state["resources"]:
                        self.state["resources"][resource] = 0
                    self.state["resources"][resource] += amount
                
                # Improve mood slightly
                self.state["mood"] = min(1.0, self.state["mood"] + 0.03)
    
    def _process_dispute(self, event: BaseEvent) -> None:
        """Process a dispute event."""
        if event.target == self.id or event.source == self.id:
            # Extract dispute details
            severity = event.data.get("severity", 0.5)
            
            # Decrease mood based on severity
            self.state["mood"] = max(0.0, self.state["mood"] - (0.05 * severity))
    
    def generate_action(self) -> Optional[BaseEvent]:
        """Generate an action based on the agent's current state."""
        # Only act every few seconds to avoid spamming
        current_time = time.time()
        if current_time - self.state["last_action_time"] < 2.0:
            return None
            
        self.state["last_action_time"] = current_time
        
        # Randomly choose an action type based on mood
        action_type = random.choices(
            ["greeting", "trade", "dispute"],
            weights=[0.5, 0.3, 0.2 * (1.0 - self.state["mood"])],  # Less likely to dispute when happy
            k=1
        )[0]
        
        # Need a target agent ID for the action
        # This would normally come from the agent manager, but for this example
        # we'll just use a placeholder that will be filled in by the simulation
        target_id = "TARGET_PLACEHOLDER"
        
        if action_type == "greeting":
            # Choose greeting type based on mood
            greeting_type = random.choices(
                ["friendly", "neutral", "hostile"],
                weights=[self.state["mood"], 0.5, 1.0 - self.state["mood"]],
                k=1
            )[0]
            
            return GreetingEvent(self.id, target_id, greeting_type)
            
        elif action_type == "trade":
            # Offer a random resource we have
            available_resources = [
                r for r, amount in self.state["resources"].items() if amount > 1
            ]
            
            if not available_resources:
                return None
                
            offer_resource = random.choice(available_resources)
            offer_amount = random.randint(1, self.state["resources"][offer_resource] // 2)
            
            # Request a random resource
            all_resources = ["food", "gold", "wood", "stone", "iron"]
            request_resource = random.choice(all_resources)
            request_amount = random.randint(1, 3)
            
            return TradeEvent(
                self.id,
                target_id,
                {offer_resource: offer_amount},
                {request_resource: request_amount}
            )
            
        elif action_type == "dispute":
            # Generate a dispute with severity based on inverse of mood
            severity = random.uniform(0.3, 0.8) * (1.0 - self.state["mood"])
            
            return DisputeEvent(self.id, target_id, severity)
            
        return None


def run_simulation(num_agents: int = 5, max_steps: int = 20) -> None:
    """
    Run a simple simulation with the specified number of agents.
    
    Args:
        num_agents: Number of agents to create
        max_steps: Maximum number of simulation steps
    """
    print("Initializing simulation...")
    
    # Create core components
    event_bus = EventBus()
    agent_factory = AgentFactory()
    agent_manager = AgentManager(event_bus)
    relationship_manager = RelationshipManager(event_bus)
    
    # Register agent types
    agent_factory.register_agent_type("simple", SimpleAgent)
    
    # Create agents
    agents = []
    for i in range(num_agents):
        agent = agent_factory.create_agent(
            "simple",
            {"name": f"Agent-{i+1}"}
        )
        agent_manager.add_agent(agent)
        agents.append(agent)
        print(f"Created {agent.name} (ID: {agent.id})")
    
    # Create initial relationships
    for i, agent_a in enumerate(agents):
        for agent_b in agents[i+1:]:
            # Random initial relationship strength
            strength = random.uniform(-0.3, 0.3)
            relationship = relationship_manager.create_relationship(
                agent_a.id,
                agent_b.id,
                "acquaintance",
                strength
            )
            print(f"Created relationship between {agent_a.name} and {agent_b.name} (strength: {strength:.2f})")
    
    print("\nStarting simulation...")
    
    # Run simulation steps
    for step in range(max_steps):
        print(f"\n--- Step {step+1} ---")
        
        # Generate agent actions
        actions = agent_manager.update_all()
        
        # Replace placeholder targets with real agent IDs
        for action in actions:
            if action and action.target == "TARGET_PLACEHOLDER":
                # Choose a random target that isn't the source
                possible_targets = [a.id for a in agents if a.id != action.source]
                if possible_targets:
                    action.target = random.choice(possible_targets)
        
        # Process actions as events
        for action in actions:
            if action and action.target != "TARGET_PLACEHOLDER":
                print(f"{action.source} -> {action.target}: {action.event_type}")
                event_bus.publish(action)
        
        # Display agent states
        for agent in agents:
            mood_str = "😊" if agent.state["mood"] > 0.7 else "😐" if agent.state["mood"] > 0.4 else "😠"
            resources = agent.state["resources"]
            print(f"{agent.name} {mood_str} - Food: {resources.get('food', 0)}, Gold: {resources.get('gold', 0)}, Wood: {resources.get('wood', 0)}")
        
        # Display relationships
        if step % 5 == 0 or step == max_steps - 1:
            print("\nRelationships:")
            for relationship in relationship_manager.get_all_relationships():
                agent_a = agent_manager.get_agent(relationship.agent_a_id).name
                agent_b = agent_manager.get_agent(relationship.agent_b_id).name
                strength = relationship.strength
                sentiment = "Positive" if strength > 0.3 else "Negative" if strength < -0.3 else "Neutral"
                print(f"{agent_a} <-> {agent_b}: {sentiment} ({strength:.2f})")
        
        # Pause between steps
        time.sleep(0.5)
    
    print("\nSimulation complete!")


if __name__ == "__main__":
    run_simulation()