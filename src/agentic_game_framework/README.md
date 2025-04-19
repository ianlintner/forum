# Agentic Game Framework

A domain-agnostic framework for building agent-based game systems and simulations.

## Overview

The Agentic Game Framework provides a flexible foundation for creating agent-based games and simulations across different domains. It abstracts common patterns and components found in agent systems, allowing developers to focus on domain-specific logic rather than infrastructure.

Key features:
- Event-driven architecture for loose coupling between components
- Flexible agent system with customizable behaviors
- Memory system for agent knowledge persistence
- Relationship system for modeling connections between agents
- Domain adaptation layer for extending the framework to specific contexts

## Core Components

### Event System

The event system serves as the backbone of the architecture, facilitating communication between components.

- `BaseEvent`: Abstract base class for all events
- `EventBus`: Central event dispatcher for publishing and subscribing to events

### Agent System

The agent system manages the creation, configuration, and lifecycle of agents.

- `BaseAgent`: Abstract base class for all agents
- `AgentFactory`: Creates agents based on templates or configurations
- `AgentManager`: Manages collections of agents

### Memory System

The memory system handles the storage and retrieval of agent memories and experiences.

- `MemoryInterface`: Abstract interface for memory implementations
- `MemoryItem`: Base class for memory entries
- `MemoryIndex`: Efficient memory retrieval system
- `MemoryPersistenceManager`: Handles saving and loading memories

### Relationship System

The relationship system manages the connections and interactions between agents.

- `BaseRelationship`: Abstract base class for agent relationships
- `RelationshipManager`: Manages collections of relationships

### Domain Adaptation Layer

The domain adaptation layer allows the core architecture to be extended for specific game domains.

- `DomainRegistry`: Registry of domain-specific components
- `DomainExtensionPoint`: Defined interfaces for domain-specific extensions

## Usage

To use the framework, you typically:

1. Define domain-specific event types
2. Create custom agent types that extend BaseAgent
3. Configure the event bus and subscribe agents to relevant events
4. Implement domain-specific behaviors and relationships
5. Run the simulation by publishing events and updating agents

## Example

```python
from agentic_game_framework.events.event_bus import EventBus
from agentic_game_framework.agents.agent_manager import AgentManager
from agentic_game_framework.relationships.relationship_manager import RelationshipManager

# Create core components
event_bus = EventBus()
agent_manager = AgentManager(event_bus)
relationship_manager = RelationshipManager(event_bus)

# Register with event bus
event_bus.subscribe_to_all(relationship_manager)

# Create agents (domain-specific implementation)
agent1 = MyCustomAgent("Agent1")
agent2 = MyCustomAgent("Agent2")

# Add agents to manager
agent_manager.add_agent(agent1)
agent_manager.add_agent(agent2)

# Create relationships
relationship_manager.create_relationship(
    agent1.id, 
    agent2.id, 
    "alliance", 
    strength=0.5
)

# Run simulation
while simulation_active:
    # Generate agent actions
    actions = agent_manager.update_all()
    
    # Process actions as events
    for action in actions:
        event_bus.publish(action)
```

## Extending the Framework

The framework is designed to be extended for specific domains:

1. Create domain-specific event types that extend BaseEvent
2. Implement custom agent behaviors by extending BaseAgent
3. Define domain-specific relationships by extending BaseRelationship
4. Register domain components with the DomainRegistry
5. Implement extension points for domain-specific functionality

## License

This project is licensed under the MIT License - see the LICENSE file for details.