# Agentic Game Framework User Guide

**Author:** Documentation Team  
**Version:** 1.1.0  
**Date:** April 19, 2025

## Table of Contents

- [Introduction](#introduction)
- [Installation](#installation)
- [Architecture Overview](#architecture-overview)
  - [Event-Driven Architecture](#event-driven-architecture)
  - [Legacy Architecture](#legacy-architecture)
  - [Dual-Mode Operation](#dual-mode-operation)
- [Getting Started](#getting-started)
  - [Creating a Simple Simulation](#creating-a-simple-simulation)
  - [Running the Simulation](#running-the-simulation)
- [Core Concepts](#core-concepts)
  - [Events](#events)
  - [Agents](#agents)
  - [Memory](#memory)
  - [Relationships](#relationships)
- [Using Existing Domains](#using-existing-domains)
  - [Senate Domain](#senate-domain)
  - [Marketplace Domain](#marketplace-domain)
- [Creating Your Own Domain](#creating-your-own-domain)
- [CLI Reference](#cli-reference)
  - [Mode Selection](#mode-selection)
  - [Configuration Options](#configuration-options)
  - [Common Commands](#common-commands)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [References](#references)

## Introduction

The Agentic Game Framework is a flexible, extensible framework for building agent-based game systems and simulations. It provides a foundation for creating complex, interactive agent systems across different domains, allowing you to focus on domain-specific logic rather than infrastructure.

This user guide will help you get started with the framework, understand its core concepts, and learn how to use it to create your own agent-based simulations.

## Installation

To install the Agentic Game Framework, you can use pip:

```bash
pip install agentic-game-framework
```

Alternatively, you can clone the repository and install it from source:

```bash
git clone https://github.com/your-organization/agentic-game-framework.git
cd agentic-game-framework
pip install -e .
```

## Architecture Overview

The Agentic Game Framework supports multiple architectural approaches to accommodate both new development and migration from existing systems.

### Event-Driven Architecture

The core of the framework is built on an event-driven architecture, which provides several benefits:

1. **Decoupling**: Components are decoupled, making the system more modular and extensible
2. **Scalability**: The event system can handle large numbers of events and agents efficiently
3. **Flexibility**: New components can be added by subscribing to existing event types
4. **Testability**: Events can be easily mocked and intercepted for testing

The event-driven architecture uses the following key components:

- **Event Bus**: Central hub for event distribution
- **Events**: Messages that represent actions or occurrences
- **Event Handlers**: Components that process specific types of events
- **Event Filters**: Mechanisms to selectively process events

### Legacy Architecture

The framework also supports integration with legacy systems that use different architectural patterns:

1. **Direct Method Calls**: Traditional object-oriented approach with direct method invocation
2. **Centralized State**: Global state management rather than distributed agent state
3. **Procedural Logic**: Sequential processing rather than event-driven logic

### Dual-Mode Operation

One of the key features of the framework is its ability to operate in multiple modes:

1. **Legacy Mode**: Uses the original architecture for backward compatibility
2. **New Mode**: Uses the new event-driven architecture for new development
3. **Hybrid Mode**: Runs both architectures in parallel for migration and comparison

You can select the mode using command-line flags (see the [CLI Reference](#cli-reference) section).

## Getting Started

### Creating a Simple Simulation

Let's create a simple simulation with a few agents that interact with each other. First, import the necessary components:

```python
from agentic_game_framework.events.event_bus import EventBus
from agentic_game_framework.agents.agent_manager import AgentManager
from agentic_game_framework.relationships.relationship_manager import RelationshipManager
from agentic_game_framework.events.base import BaseEvent
from agentic_game_framework.agents.base_agent import BaseAgent
```

Next, create a custom event type:

```python
class GreetingEvent(BaseEvent):
    """Event representing a greeting between agents."""
    
    def __init__(self, source, target, message, **kwargs):
        """Initialize a greeting event."""
        super().__init__(
            event_type="greeting",
            source=source,
            target=target,
            data={"message": message},
            **kwargs
        )
```

Then, create a custom agent type:

```python
class SimpleAgent(BaseAgent):
    """A simple agent that can greet other agents."""
    
    def __init__(self, name, friendliness=0.5, **kwargs):
        """Initialize a simple agent."""
        super().__init__(
            name=name,
            attributes={"friendliness": friendliness},
            **kwargs
        )
        
        # Subscribe to greeting events
        self.subscribe_to_event("greeting")
    
    def process_event(self, event):
        """Process an incoming event."""
        if event.event_type == "greeting" and event.target == self.id:
            print(f"{self.name} received greeting from {event.source}: {event.data['message']}")
            
            # Respond to the greeting if the agent is friendly enough
            if self.get_attribute("friendliness") > 0.3:
                return GreetingEvent(
                    source=self.id,
                    target=event.source,
                    message=f"Hello, {event.source}! Nice to meet you."
                )
    
    def generate_action(self):
        """Generate an action based on the agent's current state."""
        # In this simple example, agents don't generate actions on their own
        return None
```

### Running the Simulation

Now, let's set up and run the simulation:

```python
# Create core components
event_bus = EventBus()
agent_manager = AgentManager(event_bus)
relationship_manager = RelationshipManager(event_bus)

# Create agents
agent1 = SimpleAgent(name="Agent1", friendliness=0.8)
agent2 = SimpleAgent(name="Agent2", friendliness=0.6)
agent3 = SimpleAgent(name="Agent3", friendliness=0.2)

# Register agents
agent_manager.register_agent(agent1)
agent_manager.register_agent(agent2)
agent_manager.register_agent(agent3)

# Create relationships
relationship_manager.create_relationship(
    relationship_type="acquaintance",
    agent_a_id=agent1.id,
    agent_b_id=agent2.id,
    strength=0.5
)

relationship_manager.create_relationship(
    relationship_type="acquaintance",
    agent_a_id=agent1.id,
    agent_b_id=agent3.id,
    strength=0.3
)

# Start the simulation with an initial event
initial_event = GreetingEvent(
    source=agent1.id,
    target=agent2.id,
    message="Hello, I'm Agent1!"
)

event_bus.publish(initial_event)

# Run a few simulation steps
for _ in range(5):
    # Process agent actions
    actions = agent_manager.update_all()
    
    # Publish actions as events
    for action in actions:
        if action:
            event_bus.publish(action)
```

This simple simulation demonstrates the basic components of the framework:
- Events for communication between agents
- Agents that process events and generate actions
- Relationships between agents
- An event bus for distributing events
- An agent manager for updating agents

## Core Concepts

### Events

Events are the primary communication mechanism in the framework. They represent actions, occurrences, or information that agents can respond to. Each event has:

- A type that identifies the kind of event
- A source that indicates where the event came from
- An optional target that indicates the intended recipient
- Data that contains event-specific information
- A timestamp that indicates when the event occurred

Events flow through the event bus, which distributes them to interested subscribers.

**Example of custom event creation:**

```python
from agentic_game_framework.events.base import BaseEvent

class TradeEvent(BaseEvent):
    def __init__(self, seller_id, buyer_id, item, price, **kwargs):
        super().__init__(
            event_type="marketplace.trade",
            source=seller_id,
            target=buyer_id,
            data={
                "item": item,
                "price": price,
                "transaction_type": "sale"
            },
            **kwargs
        )
```

### Agents

Agents are autonomous entities that can process events, make decisions, and generate actions. Each agent has:

- A unique identifier
- A name
- Attributes that define its characteristics
- State that represents its current condition
- Event subscriptions that determine which events it receives

Agents process events through their `process_event` method and generate actions through their `generate_action` method.

**Example of custom agent creation:**

```python
from agentic_game_framework.agents.base_agent import BaseAgent

class MerchantAgent(BaseAgent):
    def __init__(self, name, inventory=None, gold=100, **kwargs):
        super().__init__(
            name=name,
            attributes={
                "profession": "merchant",
                "trading_skill": 0.7
            },
            **kwargs
        )
        
        self.state = {
            "inventory": inventory or {},
            "gold": gold
        }
        
        # Subscribe to relevant events
        self.subscribe_to_event("marketplace.trade")
        self.subscribe_to_event("marketplace.price_inquiry")
    
    def process_event(self, event):
        if event.event_type == "marketplace.price_inquiry" and event.target == self.id:
            item = event.data.get("item")
            # Calculate price based on trading skill and item properties
            price = self._calculate_price(item)
            
            return PriceQuoteEvent(
                source=self.id,
                target=event.source,
                item=item,
                price=price
            )
        
        # Handle other event types...
        
    def generate_action(self):
        # Example: If low on certain goods, generate a purchase order
        if self._needs_restocking():
            return self._generate_purchase_order()
        
        return None
```

### Memory

The memory system allows agents to store and retrieve information about past events and experiences. Memories have:

- A unique identifier
- A timestamp
- Content (the actual information)
- An importance score
- Associations that help with retrieval

Agents can use their memories to make decisions based on past experiences.

**Example of creating and using memories:**

```python
from agentic_game_framework.memory.memory_interface import MemoryItem

class TradeMemory(MemoryItem):
    def __init__(self, trade_event, **kwargs):
        super().__init__(**kwargs)
        self.trader_id = trade_event.source if trade_event.source != self.owner_id else trade_event.target
        self.item = trade_event.data.get("item")
        self.price = trade_event.data.get("price")
        self.timestamp = trade_event.timestamp
        self.was_buyer = trade_event.target == self.owner_id

# In the agent's process_event method:
def process_event(self, event):
    if event.event_type == "marketplace.trade":
        # Create a memory of this trade
        memory = TradeMemory(
            trade_event=event,
            owner_id=self.id,
            importance=0.6
        )
        self.memory_manager.add_memory(memory)
        
    # Later, retrieve memories to make decisions
    def decide_price(self, item, trader_id):
        # Get memories of previous trades with this trader
        trade_memories = self.memory_manager.get_memories({
            "type": "trade",
            "trader_id": trader_id,
            "item": item
        })
        
        if trade_memories:
            # Use previous trade prices to inform decision
            avg_price = sum(m.price for m in trade_memories) / len(trade_memories)
            return avg_price * (0.9 if self.is_buying else 1.1)
        
        # Default price if no memories
        return self._calculate_base_price(item)
```

### Relationships

The relationship system models connections between agents. Relationships have:

- Two agent identifiers (the agents in the relationship)
- A type that indicates the kind of relationship
- A strength value that indicates how strong the relationship is
- Attributes that contain relationship-specific information

Relationships can change over time based on interactions between agents.

**Example of managing relationships:**

```python
from agentic_game_framework.relationships.base_relationship import BaseRelationship

class BusinessRelationship(BaseRelationship):
    def __init__(self, agent_a_id, agent_b_id, **kwargs):
        super().__init__(
            agent_a_id=agent_a_id,
            agent_b_id=agent_b_id,
            relationship_type="business",
            **kwargs
        )
        
        # Initialize business-specific attributes
        self.attributes.update({
            "trust": 0.5,
            "satisfaction": 0.5,
            "transaction_count": 0
        })
    
    def update_after_trade(self, fair_price, actual_price):
        """Update the relationship after a trade."""
        price_fairness = 1.0 - abs(fair_price - actual_price) / fair_price
        
        # Update trust based on price fairness
        self.attributes["trust"] += (price_fairness - 0.5) * 0.1
        self.attributes["trust"] = max(0.0, min(1.0, self.attributes["trust"]))
        
        # Update transaction count
        self.attributes["transaction_count"] += 1
        
        # Update overall relationship strength
        self.update_strength(price_fairness * 0.05)
```

## Using Existing Domains

The framework comes with several pre-built domains that you can use in your simulations.

### Senate Domain

The Senate domain models a political environment inspired by the Roman Senate. It includes:

- Senator agents with political affiliations and goals
- Debate and voting events
- Political relationships
- Memory of speeches and votes

To use the Senate domain:

```python
from agentic_game_framework.domains.senate import (
    SenateSimulation,
    SenatorAgent,
    DebateEvent,
    VoteEvent
)

# Create a Senate simulation
simulation = SenateSimulation()

# Add senators
simulation.add_senator("Cicero", faction="Optimates")
simulation.add_senator("Caesar", faction="Populares")

# Run the simulation
simulation.run_session(topic="Land Reform")
```

Or customize the simulation:

```python
from agentic_game_framework.events.event_bus import EventBus
from agentic_game_framework.agents.agent_manager import AgentManager
from agentic_game_framework.domains.senate import SenatorAgent, SenateEventRegistry

# Create core components
event_bus = EventBus()
agent_manager = AgentManager(event_bus)

# Register Senate-specific event types
event_registry = SenateEventRegistry()
event_registry.register_all_event_types(event_bus)

# Create custom senators
cicero = SenatorAgent(
    name="Cicero",
    faction="Optimates",
    attributes={
        "oratory": 0.9,
        "reputation": 0.8,
        "philosophy": "stoic"
    }
)

caesar = SenatorAgent(
    name="Caesar",
    faction="Populares",
    attributes={
        "oratory": 0.8,
        "military": 0.9,
        "ambition": 0.95
    }
)

# Register agents
agent_manager.register_agent(cicero)
agent_manager.register_agent(caesar)

# Start a debate
debate_event = DebateEvent(
    topic="Military Command in Gaul",
    sponsor=caesar.id
)
event_bus.publish(debate_event)
```

### Marketplace Domain

The Marketplace domain models an economic environment with traders, merchants, and goods. It includes:

- Merchant agents that buy and sell goods
- Trade events for buying and selling
- Business relationships between traders
- Memory of past transactions and prices

To use the Marketplace domain:

```python
from agentic_game_framework.domains.marketplace import (
    MarketplaceSimulation,
    MerchantAgent,
    TradeEvent
)

# Create a marketplace simulation
simulation = MarketplaceSimulation()

# Add merchants
simulation.add_merchant("Marcus", initial_gold=500, specialization="weapons")
simulation.add_merchant("Julia", initial_gold=600, specialization="textiles")

# Run the simulation
simulation.run_trading_day(days=5)
```

## Creating Your Own Domain

You can create your own domain by implementing the extension points provided by the framework:

1. **Define Custom Event Types**:
   ```python
   from agentic_game_framework.events.base import BaseEvent
   
   class HarvestEvent(BaseEvent):
       def __init__(self, farmer_id, crop, amount, **kwargs):
           super().__init__(
               event_type="farm.harvest",
               source=farmer_id,
               data={
                   "crop": crop,
                   "amount": amount
               },
               **kwargs
           )
   ```

2. **Create Custom Agent Types**:
   ```python
   from agentic_game_framework.agents.base_agent import BaseAgent
   
   class FarmerAgent(BaseAgent):
       def __init__(self, name, farm_size=10, **kwargs):
           super().__init__(
               name=name,
               attributes={
                   "profession": "farmer",
                   "farming_skill": 0.6
               },
               **kwargs
           )
           
           self.farm_size = farm_size
           self.crops = {}
           
           # Subscribe to relevant events
           self.subscribe_to_event("weather.rain")
           self.subscribe_to_event("weather.drought")
           self.subscribe_to_event("market.price_change")
       
       def process_event(self, event):
           # Implement event handling logic...
           pass
       
       def generate_action(self):
           # Implement action generation logic...
           pass
   ```

3. **Define Custom Relationship Types**:
   ```python
   from agentic_game_framework.relationships.base_relationship import BaseRelationship
   
   class NeighborRelationship(BaseRelationship):
       def __init__(self, farmer_a_id, farmer_b_id, **kwargs):
           super().__init__(
               agent_a_id=farmer_a_id,
               agent_b_id=farmer_b_id,
               relationship_type="neighbor",
               **kwargs
           )
           
           # Add neighbor-specific attributes
           self.attributes.update({
               "boundary_disputes": 0,
               "shared_equipment": False,
               "water_sharing": 0.5
           })
   ```

4. **Create Domain Extension Points**:
   ```python
   from agentic_game_framework.domains.extension_points import (
       EventTypeRegistry,
       AgentBehaviorExtension
   )
   
   class FarmingEventRegistry(EventTypeRegistry):
       def register_event_types(self):
           return {
               "farm.harvest": HarvestEvent,
               "farm.plant": PlantEvent,
               "weather.rain": RainEvent,
               "weather.drought": DroughtEvent
           }
   
   class FarmerBehaviorExtension(AgentBehaviorExtension):
       def extend_agent(self, agent):
           # Add farming-specific behavior...
           pass
       
       def process_domain_event(self, agent, event):
           # Handle domain-specific events...
           pass
       
       def generate_domain_actions(self, agent):
           # Generate domain-specific actions...
           pass
   ```

5. **Register Your Domain**:
   ```python
   from agentic_game_framework.domains.domain_registry import DomainRegistry
   
   # Create your domain
   farming_domain = FarmingDomain()
   
   # Register it with the domain registry
   domain_registry = DomainRegistry()
   domain_registry.register_domain(farming_domain)
   
   # Activate the domain
   domain_registry.activate_domain("farming")
   ```

## CLI Reference

The framework provides a command-line interface (CLI) for running simulations and managing domains.

### Mode Selection

You can select the architecture mode using the `--mode` flag:

```bash
# Run in legacy mode (original architecture)
python run_simulation.py --mode legacy

# Run in new mode (event-driven architecture)
python run_simulation.py --mode new

# Run in hybrid mode (both architectures in parallel)
python run_simulation.py --mode hybrid
```

### Configuration Options

Common configuration options:

```bash
# Set the number of agents
python run_simulation.py --agents 100

# Set the simulation duration
python run_simulation.py --duration 60

# Load a specific configuration file
python run_simulation.py --config configs/senate_large.json

# Enable verbose logging
python run_simulation.py --verbose
```

### Common Commands

Common commands for different domains:

```bash
# Run a Senate simulation
python run_senate.py --topic "Land Reform" --senators 50

# Run a Marketplace simulation
python run_marketplace.py --merchants 20 --days 30

# Run a custom domain simulation
python run_simulation.py --domain farming --farmers 50 --weather random
```

## Configuration

The framework can be configured using a configuration file or command-line arguments. Configuration options include:

- **Core System Settings**:
  - `event_history_size`: Number of events to keep in history (default: 1000)
  - `agent_update_batch_size`: Number of agents to update in one batch (default: 50)
  - `memory_limit_per_agent`: Maximum number of memories per agent (default: 500)

- **Performance Settings**:
  - `enable_parallel_processing`: Enable parallel processing of agents (default: false)
  - `memory_pruning_threshold`: Importance threshold for memory pruning (default: 0.2)
  - `relationship_caching`: Enable relationship caching (default: true)

- **Domain-Specific Settings**:
  - Each domain can define its own configuration options that are available when that domain is active.

Example configuration file (`config.json`):

```json
{
  "core": {
    "event_history_size": 2000,
    "agent_update_batch_size": 100,
    "memory_limit_per_agent": 1000
  },
  "performance": {
    "enable_parallel_processing": true,
    "memory_pruning_threshold": 0.1,
    "relationship_caching": true
  },
  "domains": {
    "senate": {
      "max_senators": 100,
      "debate_duration": 5,
      "voting_threshold": 0.6
    },
    "marketplace": {
      "initial_gold_range": [100, 500],
      "price_volatility": 0.2,
      "goods_types": ["food", "weapons", "textiles", "spices"]
    }
  }
}
```

## Troubleshooting

Common issues and their solutions:

#### Events Not Being Processed

- **Issue**: Events are published but not being processed by agents.
- **Solution**: Check that agents are subscribed to the correct event types.
  ```python
  # Make sure agents are subscribing to events
  agent.subscribe_to_event("event_type")
  
  # Check that the event type is correctly set
  event = CustomEvent(event_type="event_type", ...)
  ```

#### Agents Not Generating Actions

- **Issue**: Agents are not generating actions during updates.
- **Solution**: Check the agent's `generate_action` method and state.
  ```python
  # Implement or debug the generate_action method
  def generate_action(self):
      print(f"Agent {self.id} state: {self.state}")
      # Return an event or None
  ```

#### Memory Retrieval Issues

- **Issue**: Memories are not being retrieved correctly.
- **Solution**: Check memory queries and importance settings.
  ```python
  # Check that memories are being created with sufficient importance
  memory = MemoryItem(importance=0.7, ...)
  
  # Verify query parameters
  memories = memory_manager.get_memories({"type": "correct_type", ...})
  ```

#### Relationship Updates Not Working

- **Issue**: Relationships are not updating based on interactions.
- **Solution**: Check relationship update logic and event handling.
  ```python
  # Make sure relationships are being updated in event handlers
  def process_event(self, event):
      if event.event_type == "interaction":
          relationship = relationship_manager.get_relationship(self.id, event.source)
          if relationship:
              relationship.update_strength(0.1)  # Example update
  ```

### Debugging

For more serious issues, you can enable debug mode:

```bash
python run_simulation.py --debug

# Or for more verbose output
python run_simulation.py --debug --verbose
```

This will provide detailed logging of events, agent updates, and system operations, helping you identify issues.

## References

1. Event-Driven Architecture in Game AI Systems
2. Agent-Based Modeling and Simulation
3. Memory Systems for Intelligent Agents
4. Relationship Modeling in Multi-Agent Systems
5. Domain-Driven Design in Game Development