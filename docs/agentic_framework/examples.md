# Agentic Game Framework Examples and Tutorials

**Author:** Documentation Team  
**Version:** 1.0.0  
**Date:** April 19, 2025

## Table of Contents

- [Introduction](#introduction)
- [Basic Examples](#basic-examples)
  - [Simple Agent Interaction](#simple-agent-interaction)
  - [Custom Events](#custom-events)
  - [Agent Memory](#agent-memory)
  - [Agent Relationships](#agent-relationships)
- [Domain-Specific Examples](#domain-specific-examples)
  - [Marketplace Domain](#marketplace-domain)
  - [Senate Domain](#senate-domain)
- [Advanced Examples](#advanced-examples)
  - [Cross-Domain Integration](#cross-domain-integration)
  - [Custom Domain Implementation](#custom-domain-implementation)
- [Tutorials](#tutorials)
  - [Creating a Simple Simulation](#creating-a-simple-simulation)
  - [Extending the Framework](#extending-the-framework)

## Introduction

This document provides examples and tutorials for using the Agentic Game Framework. It includes basic examples of framework components, domain-specific examples, and step-by-step tutorials for common tasks.

## Basic Examples

### Simple Agent Interaction

This example demonstrates a simple interaction between two agents using events:

```python
from agentic_game_framework.events.event_bus import EventBus
from agentic_game_framework.events.base import BaseEvent
from agentic_game_framework.agents.base_agent import BaseAgent

# Create a custom event
class GreetingEvent(BaseEvent):
    def __init__(self, source, target, message, **kwargs):
        super().__init__(
            event_type="greeting",
            source=source,
            target=target,
            data={"message": message},
            **kwargs
        )

# Create a custom agent
class SimpleAgent(BaseAgent):
    def __init__(self, name, friendliness=0.5, **kwargs):
        super().__init__(
            name=name,
            attributes={"friendliness": friendliness},
            **kwargs
        )
        self.subscribe_to_event("greeting")
    
    def process_event(self, event):
        if event.event_type == "greeting" and event.target == self.id:
            print(f"{self.name} received greeting: {event.data['message']}")
            
            # Respond if friendly enough
            if self.get_attribute("friendliness") > 0.3:
                return GreetingEvent(
                    source=self.id,
                    target=event.source,
                    message=f"Hello, nice to meet you!"
                )
    
    def generate_action(self):
        # No autonomous actions in this simple example
        return None

# Create event bus and agents
event_bus = EventBus()
agent1 = SimpleAgent(name="Agent1", friendliness=0.8)
agent2 = SimpleAgent(name="Agent2", friendliness=0.2)

# Subscribe agents to event bus
event_bus.subscribe("greeting", agent1)
event_bus.subscribe("greeting", agent2)

# Create and publish an initial event
initial_event = GreetingEvent(
    source=agent1.id,
    target=agent2.id,
    message="Hi there!"
)
event_bus.publish(initial_event)

# Process any responses
response = agent2.process_event(initial_event)
if response:
    event_bus.publish(response)
```

### Custom Events

This example shows how to create custom event types for specific domains:

```python
from agentic_game_framework.events.base import BaseEvent
from datetime import datetime

# Trade event for a marketplace domain
class TradeEvent(BaseEvent):
    def __init__(
        self,
        source: str,
        target: str,
        items_given: dict,
        items_received: dict,
        timestamp: datetime = None,
        event_id: str = None
    ):
        # Calculate trade value
        trade_value = sum(items_received.values()) - sum(items_given.values())
        
        # Create event data
        data = {
            "items_given": items_given,
            "items_received": items_received,
            "trade_value": trade_value
        }
        
        super().__init__(
            event_type="trade",
            source=source,
            target=target,
            data=data,
            timestamp=timestamp,
            event_id=event_id
        )

# Vote event for a senate domain
class VoteEvent(BaseEvent):
    def __init__(
        self,
        source: str,
        topic: str,
        vote: str,  # "aye", "nay", or "abstain"
        timestamp: datetime = None,
        event_id: str = None
    ):
        data = {
            "topic": topic,
            "vote": vote
        }
        
        super().__init__(
            event_type="vote",
            source=source,
            target=None,  # Votes don't have a specific target
            data=data,
            timestamp=timestamp,
            event_id=event_id
        )

# Create and use the events
trade = TradeEvent(
    source="merchant1",
    target="customer1",
    items_given={"gold": 10},
    items_received={"sword": 1}
)

vote = VoteEvent(
    source="senator1",
    topic="peace_treaty",
    vote="aye"
)

print(f"Trade event: {trade.to_dict()}")
print(f"Vote event: {vote.to_dict()}")
```

### Agent Memory

This example demonstrates how to use the memory system to store and retrieve agent memories:

```python
from agentic_game_framework.memory.memory_interface import MemoryItem, MemoryInterface
import time
import uuid

# Create a simple memory implementation
class SimpleMemory(MemoryInterface):
    def __init__(self):
        self._memories = {}
        self._indices = {}
    
    def add_memory(self, memory_item):
        self._memories[memory_item.id] = memory_item
        self._update_indices(memory_item)
        return memory_item.id
    
    def retrieve_memories(self, query, limit=None, importance_threshold=None):
        results = []
        
        for memory in self._memories.values():
            if self._matches_query(memory, query) and (importance_threshold is None or memory.importance >= importance_threshold):
                results.append(memory)
        
        # Sort by importance and recency
        results.sort(key=lambda m: (m.importance, m.timestamp), reverse=True)
        
        # Apply limit
        if limit is not None:
            results = results[:limit]
            
        return results
    
    def get_memory(self, memory_id):
        return self._memories.get(memory_id)
    
    def update_memory(self, memory_id, updates):
        if memory_id not in self._memories:
            return False
            
        memory = self._memories[memory_id]
        
        if "importance" in updates:
            memory.update_importance(updates["importance"])
            
        if "associations" in updates:
            for key, value in updates["associations"].items():
                memory.add_association(key, value)
                
        return True
    
    def forget(self, memory_id):
        if memory_id not in self._memories:
            return False
            
        memory = self._memories[memory_id]
        self._remove_from_indices(memory)
        del self._memories[memory_id]
        return True
    
    def clear(self):
        self._memories.clear()
        self._indices.clear()
    
    def _matches_query(self, memory, query):
        for key, value in query.items():
            if key == "content" and hasattr(memory, "content"):
                if value not in str(memory.content):
                    return False
            elif key in memory.associations:
                if memory.associations[key] != value:
                    return False
            else:
                return False
        return True
    
    def _update_indices(self, memory):
        for key, value in memory.associations.items():
            if key not in self._indices:
                self._indices[key] = {}
            if value not in self._indices[key]:
                self._indices[key][value] = set()
            self._indices[key][value].add(memory.id)
    
    def _remove_from_indices(self, memory):
        for key, value in memory.associations.items():
            if key in self._indices and value in self._indices[key]:
                self._indices[key][value].discard(memory.id)
                if not self._indices[key][value]:
                    del self._indices[key][value]
                if not self._indices[key]:
                    del self._indices[key]

# Create a memory system
memory = SimpleMemory()

# Add memories
memory.add_memory(MemoryItem(
    memory_id=str(uuid.uuid4()),
    timestamp=time.time(),
    content="Met a merchant in the market",
    importance=0.7,
    associations={"location": "market", "person": "merchant", "type": "meeting"}
))

memory.add_memory(MemoryItem(
    memory_id=str(uuid.uuid4()),
    timestamp=time.time(),
    content="Bought a sword for 10 gold",
    importance=0.8,
    associations={"location": "market", "item": "sword", "type": "purchase"}
))

memory.add_memory(MemoryItem(
    memory_id=str(uuid.uuid4()),
    timestamp=time.time(),
    content="Saw a guard patrolling the city",
    importance=0.3,
    associations={"location": "city", "person": "guard", "type": "observation"}
))

# Retrieve memories
market_memories = memory.retrieve_memories({"location": "market"})
print(f"Market memories: {len(market_memories)}")
for mem in market_memories:
    print(f"- {mem.content} (importance: {mem.importance})")

important_memories = memory.retrieve_memories({}, importance_threshold=0.5)
print(f"\nImportant memories: {len(important_memories)}")
for mem in important_memories:
    print(f"- {mem.content} (importance: {mem.importance})")
```

### Agent Relationships

This example demonstrates how to use the relationship system to model connections between agents:

```python
from agentic_game_framework.relationships.base_relationship import BaseRelationship
from agentic_game_framework.relationships.relationship_manager import RelationshipManager
from agentic_game_framework.events.event_bus import EventBus
from agentic_game_framework.events.base import BaseEvent

# Create a custom relationship type
class FriendshipRelationship(BaseRelationship):
    def __init__(
        self,
        agent_a_id: str,
        agent_b_id: str,
        strength: float = 0.0,
        attributes: dict = None,
        relationship_id: str = None
    ):
        super().__init__(
            agent_a_id=agent_a_id,
            agent_b_id=agent_b_id,
            relationship_type="friendship",
            strength=strength,
            attributes=attributes or {},
            relationship_id=relationship_id
        )
        
        # Initialize friendship-specific attributes
        self.attributes.setdefault("interaction_count", 0)
        self.attributes.setdefault("last_interaction", None)
    
    def update(self, event: BaseEvent) -> bool:
        if not self._event_involves_both_agents(event):
            return False
            
        if event.event_type == "greeting":
            # Update interaction count
            self.attributes["interaction_count"] += 1
            
            # Update last interaction
            self.attributes["last_interaction"] = event.timestamp.timestamp()
            
            # Update relationship strength
            # Positive message strengthens the relationship
            message = event.data.get("message", "")
            if "nice" in message or "friend" in message:
                delta = 0.1
            else:
                delta = 0.05
                
            self.update_strength(delta, reason=f"Greeting: {event.get_id()}")
            
            return True
            
        return False
    
    def _event_involves_both_agents(self, event: BaseEvent) -> bool:
        return (
            (event.source == self.agent_a_id and event.target == self.agent_b_id) or
            (event.source == self.agent_b_id and event.target == self.agent_a_id)
        )

# Create event bus and relationship manager
event_bus = EventBus()
relationship_manager = RelationshipManager(event_bus)

# Register relationship types
relationship_manager._relationship_factory.register_relationship_type("friendship", FriendshipRelationship)

# Create relationships
friendship = relationship_manager.create_relationship(
    relationship_type="friendship",
    agent_a_id="agent1",
    agent_b_id="agent2",
    strength=0.2
)

# Create and publish events
greeting_event = BaseEvent(
    event_type="greeting",
    source="agent1",
    target="agent2",
    data={"message": "Hello, nice to see you my friend!"}
)

event_bus.publish(greeting_event)

# Check relationship after event
print(f"Relationship strength: {friendship.strength}")
print(f"Interaction count: {friendship.attributes['interaction_count']}")
```

## Domain-Specific Examples

### Marketplace Domain

The Marketplace domain example demonstrates a simulation of merchants and customers trading items:

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

For more details on the Marketplace domain, see the [Marketplace Example README](../src/agentic_game_framework/examples/marketplace/README.md).

### Senate Domain

The Senate domain example demonstrates a simulation of senators debating and voting on topics:

```python
from agentic_game_framework.domains.senate import SenateSimulation

# Create a Senate simulation
simulation = SenateSimulation()

# Add senators
simulation.add_senator("Cicero", faction="Optimates")
simulation.add_senator("Caesar", faction="Populares")
simulation.add_senator("Cato", faction="Optimates")
simulation.add_senator("Clodius", faction="Populares")

# Add topics
simulation.add_topic("Peace Treaty", description="A treaty to end the war with Carthage")
simulation.add_topic("Land Reform", description="A proposal to redistribute land to veterans")

# Run the simulation
simulation.run(steps=10)
```

## Advanced Examples

### Cross-Domain Integration

This example demonstrates how to integrate multiple domains in a single simulation:

```python
from agentic_game_framework.events.event_bus import EventBus
from agentic_game_framework.agents.agent_manager import AgentManager
from agentic_game_framework.relationships.relationship_manager import RelationshipManager
from agentic_game_framework.domains.domain_registry import DomainRegistry, Domain

# Create core components
event_bus = EventBus()
agent_manager = AgentManager(event_bus)
relationship_manager = RelationshipManager(event_bus)
domain_registry = DomainRegistry()

# Create domains
senate_domain = Domain(
    domain_id="senate",
    name="Senate Domain",
    description="A domain for simulating a senate with senators and debates",
    config={"faction_types": ["Optimates", "Populares"]}
)

market_domain = Domain(
    domain_id="market",
    name="Market Domain",
    description="A domain for simulating a marketplace with merchants and customers",
    config={"item_types": ["gold", "silver", "food", "tools"]}
)

# Register domains
domain_registry.register_domain(senate_domain)
domain_registry.register_domain(market_domain)

# Create domain-specific components
# (This would typically be done through extension points)

# Create cross-domain events
class EconomicPolicyEvent(BaseEvent):
    def __init__(
        self,
        source: str,
        policy_type: str,
        affected_items: list,
        tax_rate: float,
        **kwargs
    ):
        data = {
            "policy_type": policy_type,
            "affected_items": affected_items,
            "tax_rate": tax_rate
        }
        
        super().__init__(
            event_type="economic_policy",
            source=source,
            target=None,
            data=data,
            **kwargs
        )

# Run the simulation
# ...
```

### Custom Domain Implementation

This example demonstrates how to create a custom domain implementation:

```python
from agentic_game_framework.domains.domain_registry import Domain
from agentic_game_framework.domains.extension_points import (
    EventTypeRegistry,
    AgentBehaviorExtension,
    RelationshipTypeExtension,
    MemoryTypeExtension
)

# Create custom event types
class CityEvent(BaseEvent):
    # Implementation
    pass

class CitizenAgent(BaseAgent):
    # Implementation
    pass

class CitizenRelationship(BaseRelationship):
    # Implementation
    pass

# Create extension points
class CityEventRegistry(EventTypeRegistry):
    def register_event_types(self, registry):
        registry.register_event_type("city", "construction", ConstructionEvent)
        registry.register_event_type("city", "crime", CrimeEvent)
        registry.register_event_type("city", "celebration", CelebrationEvent)
    
    def create_event(self, event_type, **kwargs):
        if event_type == "construction":
            return ConstructionEvent(**kwargs)
        elif event_type == "crime":
            return CrimeEvent(**kwargs)
        elif event_type == "celebration":
            return CelebrationEvent(**kwargs)
        return None

# Create domain
city_domain = Domain(
    domain_id="city",
    name="City Domain",
    description="A domain for simulating a city with citizens and buildings",
    config={
        "building_types": ["house", "shop", "temple", "barracks"],
        "citizen_types": ["noble", "merchant", "worker", "soldier"]
    }
)

# Register extension points
city_domain.register_extension_point(CityEventRegistry())
city_domain.register_extension_point(CitizenBehaviorExtension())
city_domain.register_extension_point(CitizenRelationshipExtension())
city_domain.register_extension_point(CitizenMemoryExtension())

# Register domain
domain_registry.register_domain(city_domain)
```

## Tutorials

### Creating a Simple Simulation

This tutorial walks through the process of creating a simple simulation using the framework:

1. **Set up the environment**:
   ```python
   from agentic_game_framework.events.event_bus import EventBus
   from agentic_game_framework.agents.agent_manager import AgentManager
   from agentic_game_framework.relationships.relationship_manager import RelationshipManager
   
   # Create core components
   event_bus = EventBus()
   agent_manager = AgentManager(event_bus)
   relationship_manager = RelationshipManager(event_bus)
   ```

2. **Define custom events**:
   ```python
   from agentic_game_framework.events.base import BaseEvent
   
   class GreetingEvent(BaseEvent):
       def __init__(self, source, target, message, **kwargs):
           super().__init__(
               event_type="greeting",
               source=source,
               target=target,
               data={"message": message},
               **kwargs
           )
   ```

3. **Define custom agents**:
   ```python
   from agentic_game_framework.agents.base_agent import BaseAgent
   
   class SimpleAgent(BaseAgent):
       def __init__(self, name, friendliness=0.5, **kwargs):
           super().__init__(
               name=name,
               attributes={"friendliness": friendliness},
               **kwargs
           )
           self.subscribe_to_event("greeting")
       
       def process_event(self, event):
           if event.event_type == "greeting" and event.target == self.id:
               print(f"{self.name} received greeting: {event.data['message']}")
               
               # Respond if friendly enough
               if self.get_attribute("friendliness") > 0.3:
                   return GreetingEvent(
                       source=self.id,
                       target=event.source,
                       message=f"Hello, nice to meet you!"
                   )
       
       def generate_action(self):
           # No autonomous actions in this simple example
           return None
   ```

4. **Create and register agents**:
   ```python
   # Create agents
   agent1 = SimpleAgent(name="Agent1", friendliness=0.8)
   agent2 = SimpleAgent(name="Agent2", friendliness=0.2)
   
   # Register agents
   agent_manager.register_agent(agent1)
   agent_manager.register_agent(agent2)
   ```

5. **Create relationships**:
   ```python
   # Create a relationship
   relationship_manager.create_relationship(
       relationship_type="acquaintance",
       agent_a_id=agent1.id,
       agent_b_id=agent2.id,
       strength=0.1
   )
   ```

6. **Run the simulation**:
   ```python
   # Create an initial event
   initial_event = GreetingEvent(
       source=agent1.id,
       target=agent2.id,
       message="Hi there!"
   )
   
   # Publish the event
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

### Extending the Framework

This tutorial walks through the process of extending the framework with custom components:

1. **Create custom events**:
   ```python
   from agentic_game_framework.events.base import BaseEvent
   
   class CustomEvent(BaseEvent):
       def __init__(self, source, target, custom_data, **kwargs):
           super().__init__(
               event_type="custom",
               source=source,
               target=target,
               data={"custom_data": custom_data},
               **kwargs
           )
   ```

2. **Create custom agents**:
   ```python
   from agentic_game_framework.agents.base_agent import BaseAgent
   
   class CustomAgent(BaseAgent):
       def __init__(self, name, **kwargs):
           super().__init__(
               name=name,
               **kwargs
           )
           self.subscribe_to_event("custom")
       
       def process_event(self, event):
           # Implementation
           pass
       
       def generate_action(self):
           # Implementation
           pass
   ```

3. **Create custom relationships**:
   ```python
   from agentic_game_framework.relationships.base_relationship import BaseRelationship
   
   class CustomRelationship(BaseRelationship):
       def __init__(self, agent_a_id, agent_b_id, **kwargs):
           super().__init__(
               agent_a_id=agent_a_id,
               agent_b_id=agent_b_id,
               relationship_type="custom",
               **kwargs
           )
       
       def update(self, event):
           # Implementation
           pass
   ```

4. **Create custom memories**:
   ```python
   from agentic_game_framework.memory.memory_interface import MemoryItem
   
   class CustomMemory(MemoryItem):
       def __init__(self, memory_id, timestamp, custom_content, **kwargs):
           super().__init__(
               memory_id=memory_id,
               timestamp=timestamp,
               content=custom_content,
               **kwargs
           )
   ```

5. **Register custom components**:
   ```python
   # Register custom agent type
   agent_factory = AgentFactory()
   agent_factory.register_agent_type("custom", CustomAgent)
   
   # Register custom relationship type
   relationship_manager._relationship_factory.register_relationship_type("custom", CustomRelationship)
   ```

6. **Use custom components**:
   ```python
   # Create custom agent
   agent = agent_factory.create_agent(
       agent_type="custom",
       name="Custom Agent"
   )
   
   # Create custom relationship
   relationship = relationship_manager.create_relationship(
       relationship_type="custom",
       agent_a_id="agent1",
       agent_b_id="agent2"
   )
   
   # Create custom event
   event = CustomEvent(
       source="agent1",
       target="agent2",
       custom_data="Hello, world!"
   )
   ```

For more detailed examples and tutorials, see the [Developer Guide](developer_guide.md).