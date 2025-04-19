# Agentic Game Framework User Guide

**Author:** Documentation Team  
**Version:** 1.0.0  
**Date:** April 19, 2025

## Table of Contents

- [Introduction](#introduction)
- [Installation](#installation)
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

### Agents

Agents are autonomous entities that can process events, make decisions, and generate actions. Each agent has:

- A unique identifier
- A name
- Attributes that define its characteristics
- State that represents its current condition
- Event subscriptions that determine which events it receives

Agents process events through their `process_event` method and generate actions through their `generate_action` method.

### Memory

The memory system allows agents to store and retrieve information about past events and experiences. Memories have:

- A unique identifier
- A timestamp
- Content (the actual information)
- An importance score
- Associations that help with retrieval

Agents can use their memories to make decisions based on past experiences.

### Relationships

The relationship system models connections between agents. Relationships have:

- Two agent identifiers (the agents in the relationship)
- A type that indicates the kind of relationship
- A strength value that indicates how strong the relationship is
- Attributes that contain relationship-specific information

Relationships can change over time based on interactions between agents.

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
simulation.run(steps=10)
```

### Marketplace Domain

The Marketplace domain models an economic environment with merchants and customers. It includes:

- Merchant agents that sell items
- Customer agents that buy items
- Trade and negotiation events
- Business relationships
- Memory of transactions and prices

To use the Marketplace domain:

```python
from agentic_game_framework.examples.marketplace.marketplace_simulation import run_marketplace_simulation

# Run the marketplace simulation with default parameters
run_marketplace_simulation()

# Or customize the simulation
run_marketplace_simulation(
    num_merchants=5,
    num_customers=10,
    max_steps=30
)
```

## Creating Your Own Domain

To create your own domain, you'll need to:

1. Define domain-specific events
2. Create domain-specific agent types
3. Implement domain-specific relationships
4. Create domain-specific memory types
5. Set up a simulation runner

For a detailed guide on creating your own domain, see the [Developer Guide](developer_guide.md).

## Configuration

The framework can be configured through a configuration file or programmatically. Common configuration options include:

- Event processing settings
- Agent update frequency
- Memory retention policies
- Relationship decay rates
- Domain-specific settings

Example configuration:

```python
config = {
    "event_processing": {
        "batch_size": 100,
        "max_events_per_update": 1000
    },
    "agent_update": {
        "frequency": 0.1,  # seconds
        "max_active_agents": 500
    },
    "memory": {
        "importance_threshold": 0.2,
        "max_memories_per_agent": 1000
    },
    "relationships": {
        "decay_rate": 0.01,
        "min_strength": -1.0,
        "max_strength": 1.0
    }
}
```

## Troubleshooting

### Common Issues

#### Events Not Being Processed

If events aren't being processed by agents:

1. Check that agents are subscribed to the event types they should receive
2. Verify that the event bus is correctly publishing events
3. Ensure that agents are registered with the agent manager

#### Agents Not Generating Actions

If agents aren't generating actions:

1. Check the `generate_action` method implementation
2. Verify that the agent's state is being updated correctly
3. Ensure that the agent manager is calling `update` on all agents

#### Memory Retrieval Issues

If agents can't retrieve memories:

1. Check that memories are being added correctly
2. Verify that the query parameters are correct
3. Ensure that memory associations are set up properly

#### Relationship Updates Not Working

If relationships aren't updating:

1. Check that the `update` method is implemented correctly
2. Verify that events involve both agents in the relationship
3. Ensure that the relationship manager is receiving events

### Debugging

The framework provides several debugging tools:

- Event logging to track event flow
- Agent state inspection to examine agent internals
- Memory dumps to view agent memories
- Relationship visualization to see agent connections

For more debugging tips, see the [Developer Guide](developer_guide.md#debugging).

## References

- [Architecture Guide](architecture.md)
- [Developer Guide](developer_guide.md)
- [API Reference](api_reference.md)
- [Examples and Tutorials](examples.md)
- [Migration Guide](migration_guide.md)