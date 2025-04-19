# Marketplace Domain Example

This example demonstrates how to extend the Agentic Game Framework to create a domain-specific implementation for a marketplace simulation. It showcases the framework's flexibility and how different components can be customized for specific use cases.

## Overview

The marketplace domain simulates a virtual economy where merchant agents sell items to customer agents. The simulation includes:

- Domain-specific events (trades, price changes, negotiations, etc.)
- Domain-specific agent types (merchants and customers)
- Domain-specific relationships (business relationships, competitor relationships, supplier relationships)
- Domain-specific memory items (transaction memories, price memories, business deal memories)

## Components

### Domain Definition

The `marketplace_domain.py` file defines the marketplace domain and registers it with the framework. It implements several extension points:

- `MarketplaceEventRegistry`: Registers domain-specific event types
- `MarketplaceMemoryExtension`: Registers domain-specific memory types
- `MarketplaceRelationshipExtension`: Registers domain-specific relationship types
- `MarketplaceAgentBehaviorExtension`: Extends agents with marketplace-specific behaviors
- `MarketplaceConfigExtension`: Provides configuration for the marketplace domain

### Events

The `marketplace_events.py` file defines domain-specific events:

- `TradeEvent`: Represents a trade between agents
- `PriceChangeEvent`: Represents a change in item price
- `ItemListingEvent`: Represents an item being listed for sale
- `NegotiationEvent`: Represents a negotiation between agents
- `BusinessDealEvent`: Represents a business deal between agents
- `DealBreachEvent`: Represents a breach of a business deal
- `MarketTrendEvent`: Represents a market-wide trend affecting prices

### Agents

The example includes two agent types:

- `MerchantAgent` (`merchant_agent.py`): Specializes in buying, selling, and trading items
- `CustomerAgent` (`customer_agent.py`): Specializes in purchasing items based on needs and preferences

Both agent types extend the base `BaseAgent` class and implement domain-specific behaviors.

### Relationships

The `business_relationship.py` file defines domain-specific relationship types:

- `BusinessRelationship`: Represents a general commercial connection
- `CompetitorRelationship`: Represents competition between merchants
- `SupplierRelationship`: Represents a supplier-customer connection

Each relationship type extends the base `BaseRelationship` class and implements domain-specific update logic.

### Memory Items

The `transaction_memory.py` file defines domain-specific memory types:

- `TransactionMemory`: Stores information about trades
- `PriceMemory`: Stores information about item prices
- `BusinessDealMemory`: Stores information about business deals

Each memory type extends the base `MemoryItem` or `EventMemoryItem` class and implements domain-specific functionality.

### Simulation Runner

The `marketplace_simulation.py` file provides a simulation runner that demonstrates how all these components work together. It:

1. Creates merchant and customer agents
2. Establishes initial relationships between agents
3. Runs a simulation where agents interact through events
4. Logs events and prints a summary of the simulation results

## How to Run

To run the marketplace simulation:

```python
from agentic_game_framework.examples.marketplace.marketplace_simulation import run_marketplace_simulation

# Run with default parameters
run_marketplace_simulation()

# Or customize the simulation
run_marketplace_simulation(
    num_merchants=5,
    num_customers=10,
    max_steps=30
)
```

## Framework Extension Demonstration

This example demonstrates several key aspects of extending the framework:

### 1. Domain-Specific Components

The example shows how to create domain-specific components by extending the base classes provided by the framework:

- Events extend `BaseEvent`
- Agents extend `BaseAgent`
- Relationships extend `BaseRelationship`
- Memory items extend `MemoryItem` or `EventMemoryItem`

### 2. Event-Driven Architecture

The example demonstrates the event-driven architecture of the framework:

- Agents generate events based on their state and goals
- Events are distributed through the event bus
- Agents process events and update their state
- Relationships are updated based on events
- Memories are created from events

This event-driven approach allows for decoupled, modular components that can interact without direct dependencies.

### 3. Memory System

The example shows how the memory system enables agent decision-making:

- Agents store events as memories
- Memories have importance scores and associations
- Agents can retrieve memories based on queries
- Different memory types store different kinds of information
- Memories influence agent behavior and decision-making

### 4. Relationship System

The example demonstrates how the relationship system models connections between agents:

- Different relationship types represent different kinds of connections
- Relationships are updated based on events
- Relationship strength affects agent interactions
- Relationships store history and attributes

### 5. Extension Points

The example shows how to use the framework's extension points to register domain-specific components:

- `EventTypeRegistry` for registering event types
- `AgentBehaviorExtension` for extending agent behaviors
- `MemoryTypeExtension` for registering memory types
- `RelationshipTypeExtension` for registering relationship types
- `DomainConfigExtension` for providing domain configuration

## Customization

The marketplace example can be customized in several ways:

- Add new event types for different kinds of interactions
- Create new agent types with different behaviors
- Define new relationship types for different kinds of connections
- Implement new memory types for different kinds of information
- Modify the simulation parameters to create different scenarios

This flexibility demonstrates how the Agentic Game Framework can be adapted to a wide range of domains and use cases.