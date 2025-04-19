# Agentic Game Framework

A domain-agnostic framework for building agent-based game systems and simulations.

## Overview

The Agentic Game Framework provides a flexible foundation for creating agent-based games and simulations across different domains. It abstracts common patterns and components found in agent systems, allowing developers to focus on domain-specific logic rather than infrastructure.

This framework was developed based on lessons learned from the Roman Senate simulation, but generalized to support various types of agent-based simulations and games.

## Features

- **Event-Driven Architecture**: Loosely coupled components communicating through events
- **Flexible Agent System**: Customizable agent behaviors and decision-making
- **Memory System**: Persistent agent knowledge and experience
- **Relationship System**: Dynamic relationships between agents
- **Domain Adaptation Layer**: Extend the framework for specific game domains

## Installation

Clone the repository and navigate to the project directory:

```bash
git clone <repository-url>
cd <repository-directory>
```

The framework is designed to be used as a library within your Python project.

## Usage

### Running the Example Simulation

The framework includes a simple example simulation that demonstrates its core features:

```bash
# Run with default settings (5 agents, 20 steps)
./run_simulation.py

# Run with custom settings
./run_simulation.py --agents 10 --steps 30
```

### Running Tests

To run the test suite:

```bash
# Run all tests
./run_tests.py

# Run only unit tests
./run_tests.py --unit-only

# Run only integration tests
./run_tests.py --integration-only

# Run tests with verbose output
./run_tests.py --verbose
```

## Framework Architecture

### Core Components

#### Event System
- `BaseEvent`: Abstract base class for all events
- `EventBus`: Central event dispatcher

#### Agent System
- `BaseAgent`: Abstract base class for all agents
- `AgentFactory`: Creates agents based on templates or configurations
- `AgentManager`: Manages collections of agents

#### Memory System
- `MemoryInterface`: Abstract interface for memory implementations
- `MemoryItem`: Base class for memory entries
- `MemoryIndex`: Efficient memory retrieval system
- `MemoryPersistenceManager`: Handles saving and loading memories

#### Relationship System
- `BaseRelationship`: Abstract base class for agent relationships
- `RelationshipManager`: Manages collections of relationships

#### Domain Adaptation Layer
- `DomainRegistry`: Registry of domain-specific components
- `DomainExtensionPoint`: Defined interfaces for domain-specific extensions

### Integration Patterns

- **Event-Driven Architecture**: Components communicate primarily through events
- **Dependency Injection**: Components receive their dependencies rather than creating them
- **Observer Pattern**: Components can observe and react to state changes

## Creating a Custom Simulation

To create a custom simulation using the framework:

1. Define domain-specific event types by extending `BaseEvent`
2. Create custom agent types by extending `BaseAgent`
3. Configure the event bus and subscribe agents to relevant events
4. Implement domain-specific behaviors and relationships
5. Run the simulation by publishing events and updating agents

Example:

```python
from agentic_game_framework import EventBus, AgentManager, RelationshipManager

# Create core components
event_bus = EventBus()
agent_manager = AgentManager(event_bus)
relationship_manager = RelationshipManager(event_bus)

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

1. Create domain-specific event types that extend `BaseEvent`
2. Implement custom agent behaviors by extending `BaseAgent`
3. Define domain-specific relationships by extending `BaseRelationship`
4. Register domain components with the `DomainRegistry`
5. Implement extension points for domain-specific functionality

## Documentation

For more detailed documentation, see:

- [Framework Architecture](src/agentic_game_framework/README.md)
- [Event System](src/agentic_game_framework/events/README.md)
- [Agent System](src/agentic_game_framework/agents/README.md)
- [Memory System](src/agentic_game_framework/memory/README.md)
- [Relationship System](src/agentic_game_framework/relationships/README.md)
- [Domain Adaptation](src/agentic_game_framework/domains/README.md)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

This framework was inspired by the Roman Senate simulation project and various agent-based modeling frameworks.