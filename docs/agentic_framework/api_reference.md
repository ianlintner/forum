# Agentic Game Framework API Reference

**Author:** Documentation Team  
**Version:** 1.0.0  
**Date:** April 19, 2025

## Table of Contents

- [Introduction](#introduction)
- [Event System](#event-system)
  - [BaseEvent](#baseevent)
  - [EventBus](#eventbus)
  - [EventHandler](#eventhandler)
- [Agent System](#agent-system)
  - [BaseAgent](#baseagent)
  - [AgentFactory](#agentfactory)
  - [AgentManager](#agentmanager)
- [Memory System](#memory-system)
  - [MemoryItem](#memoryitem)
  - [EventMemoryItem](#eventmemoryitem)
  - [MemoryInterface](#memoryinterface)
- [Relationship System](#relationship-system)
  - [BaseRelationship](#baserelationship)
  - [RelationshipManager](#relationshipmanager)
- [Domain Adaptation Layer](#domain-adaptation-layer)
  - [Domain](#domain)
  - [DomainRegistry](#domainregistry)
  - [ExtensionPoint](#extensionpoint)

## Introduction

This API reference provides detailed documentation of the classes, methods, and functions available in the Agentic Game Framework. It is intended for developers who want to use or extend the framework.

## Event System

The Event System is the backbone of the framework, enabling communication between components.

### BaseEvent

```python
class BaseEvent(ABC):
    """
    Abstract base class for all events in the system.
    
    Events are the primary communication mechanism between components in the framework.
    Each event has a type, timestamp, optional source and target, and additional data.
    """
    
    def __init__(
        self,
        event_type: str,
        source: Optional[str] = None,
        target: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None,
        event_id: Optional[str] = None
    )
    
    def get_id(self) -> str
    def to_dict(self) -> Dict[str, Any]
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseEvent'
```

### EventBus

```python
class EventBus:
    """
    Central event dispatcher for the framework.
    
    The EventBus allows components to:
    1. Subscribe to specific event types
    2. Publish events to all interested subscribers
    3. Filter and prioritize event handling
    """
    
    def __init__(self)
    def subscribe(self, event_type: str, handler: EventHandler, priority: int = 0) -> None
    def subscribe_to_all(self, handler: EventHandler, priority: int = 0) -> None
    def unsubscribe(self, event_type: str, handler: EventHandler) -> None
    def unsubscribe_from_all(self, handler: EventHandler) -> None
    def add_filter(self, filter_func: Callable[[BaseEvent], bool]) -> None
    def remove_filter(self, filter_func: Callable[[BaseEvent], bool]) -> None
    def get_handlers(self, event_type: str) -> List[EventHandler]
    def publish(self, event: BaseEvent) -> bool
```

### EventHandler

```python
class EventHandler(ABC):
    """
    Abstract base class for event handlers.
    
    Event handlers process events of specific types and implement the business logic
    for responding to those events.
    """
    
    @abstractmethod
    def handle_event(self, event: BaseEvent) -> None
```

## Agent System

The Agent System manages the creation, lifecycle, and processing of agents.

### BaseAgent

```python
class BaseAgent(ABC):
    """
    Abstract base class for all agents in the system.
    
    Agents are autonomous entities that can process events, make decisions,
    generate actions, and maintain internal state.
    """
    
    def __init__(
        self,
        name: str,
        attributes: Optional[Dict[str, Any]] = None,
        agent_id: Optional[str] = None,
        initial_state: Optional[Dict[str, Any]] = None
    )
    
    @abstractmethod
    def process_event(self, event: BaseEvent) -> None
    
    @abstractmethod
    def generate_action(self) -> Optional[BaseEvent]
    
    def update_state(self, updates: Dict[str, Any]) -> None
    def get_state(self) -> Dict[str, Any]
    def get_attribute(self, key: str, default: Any = None) -> Any
    def set_attribute(self, key: str, value: Any) -> None
    def subscribe_to_event(self, event_type: str) -> None
    def unsubscribe_from_event(self, event_type: str) -> None
    def get_subscriptions(self) -> Set[str]
    def to_dict(self) -> Dict[str, Any]
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseAgent'
```

### AgentFactory

```python
class AgentFactory:
    """
    Factory for creating agents of different types.
    
    The AgentFactory maintains a registry of agent types and provides methods
    for creating agents based on type names and configuration.
    """
    
    def __init__(self)
    def register_agent_type(self, type_name: str, agent_class: Type[BaseAgent]) -> None
    def create_agent(self, agent_type: str, **kwargs) -> BaseAgent
    def create_agents_batch(self, specs: List[Dict[str, Any]]) -> List[BaseAgent]
```

### AgentManager

```python
class AgentManager:
    """
    Manager for collections of agents.
    
    The AgentManager maintains a registry of agents and provides methods for
    updating them, retrieving them, and managing their lifecycle.
    """
    
    def __init__(self, event_bus: Optional[EventBus] = None)
    def register_agent(self, agent: BaseAgent) -> None
    def unregister_agent(self, agent_id: str) -> None
    def get_agent(self, agent_id: str) -> Optional[BaseAgent]
    def get_all_agents(self) -> List[BaseAgent]
    def update_agent(self, agent_id: str) -> Optional[BaseEvent]
    def update_all(self) -> List[Optional[BaseEvent]]
```

## Memory System

The Memory System handles the storage and retrieval of agent memories and experiences.

### MemoryItem

```python
class MemoryItem:
    """
    Base class for memory entries.
    
    Memory items represent discrete pieces of information that agents can
    remember, such as events, facts, or experiences.
    """
    
    def __init__(
        self,
        memory_id: str,
        timestamp: float,
        content: Any,
        importance: float = 0.5,
        associations: Optional[Dict[str, Any]] = None
    )
    
    def update_importance(self, new_importance: float) -> None
    def add_association(self, key: str, value: Any) -> None
    def to_dict(self) -> Dict[str, Any]
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryItem'
```

### EventMemoryItem

```python
class EventMemoryItem(MemoryItem):
    """
    Memory item specifically for storing events.
    
    This specialized memory item is designed to store event information,
    making it easier to retrieve and process event-related memories.
    """
    
    def __init__(
        self,
        memory_id: str,
        timestamp: float,
        event: BaseEvent,
        importance: float = 0.5,
        associations: Optional[Dict[str, Any]] = None
    )
```

### MemoryInterface

```python
class MemoryInterface(ABC):
    """
    Abstract interface for memory implementations.
    
    This interface defines the core operations that any memory system must
    support, including adding memories, retrieving memories based on queries,
    and forgetting memories.
    """
    
    @abstractmethod
    def add_memory(self, memory_item: MemoryItem) -> str
    
    @abstractmethod
    def retrieve_memories(
        self, 
        query: Dict[str, Any], 
        limit: Optional[int] = None,
        importance_threshold: Optional[float] = None
    ) -> List[MemoryItem]
    
    @abstractmethod
    def get_memory(self, memory_id: str) -> Optional[MemoryItem]
    
    @abstractmethod
    def update_memory(self, memory_id: str, updates: Dict[str, Any]) -> bool
    
    @abstractmethod
    def forget(self, memory_id: str) -> bool
    
    @abstractmethod
    def clear(self) -> None
```

## Relationship System

The Relationship System manages the connections and interactions between agents.

### BaseRelationship

```python
class BaseRelationship(ABC):
    """
    Abstract base class for all agent relationships in the system.
    
    Relationships represent connections between agents, including their type,
    strength, and attributes.
    """
    
    def __init__(
        self,
        agent_a_id: str,
        agent_b_id: str,
        relationship_type: str,
        strength: float = 0.0,
        attributes: Optional[Dict[str, Any]] = None,
        relationship_id: Optional[str] = None
    )
    
    @abstractmethod
    def update(self, event: BaseEvent) -> bool
    
    def get_sentiment(self) -> float
    def get_attribute(self, key: str, default: Any = None) -> Any
    def set_attribute(self, key: str, value: Any) -> None
    def update_strength(self, delta: float, reason: Optional[str] = None) -> None
    def get_history(self) -> List[Dict[str, Any]]
    def involves_agent(self, agent_id: str) -> bool
    def get_other_agent_id(self, agent_id: str) -> Optional[str]
    def to_dict(self) -> Dict[str, Any]
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseRelationship'
```

### RelationshipManager

```python
class RelationshipManager:
    """
    Manager for collections of relationships.
    
    The RelationshipManager maintains a registry of relationships and provides
    methods for creating, retrieving, and updating relationships.
    """
    
    def __init__(self, event_bus: Optional[EventBus] = None)
    
    def create_relationship(
        self,
        relationship_type: str,
        agent_a_id: str,
        agent_b_id: str,
        strength: float = 0.0,
        attributes: Optional[Dict[str, Any]] = None
    ) -> BaseRelationship
    
    def get_relationship(self, agent_a_id: str, agent_b_id: str) -> Optional[BaseRelationship]
    def get_agent_relationships(self, agent_id: str) -> List[BaseRelationship]
    def update_relationships(self, event: BaseEvent) -> None
    def get_relationship_by_id(self, relationship_id: str) -> Optional[BaseRelationship]
    def remove_relationship(self, relationship_id: str) -> bool
    def clear_relationships(self) -> None
```

## Domain Adaptation Layer

The Domain Adaptation Layer bridges the gap between the core systems and domain-specific implementations.

### Domain

```python
class Domain:
    """
    Representation of a specific domain in the framework.
    
    A domain encapsulates domain-specific components, configuration, and extension points.
    """
    
    def __init__(
        self,
        domain_id: str,
        name: str,
        description: str = "",
        config: Optional[Dict[str, Any]] = None
    )
    
    def register_extension_point(self, extension_point: ExtensionPoint) -> None
    def get_extension_point(self, extension_point_id: str) -> Optional[ExtensionPoint]
    def get_config(self, key: str, default: Any = None) -> Any
```

### DomainRegistry

```python
class DomainRegistry:
    """
    Registry for domains and domain-specific components.
    
    The DomainRegistry maintains a registry of domains and provides methods for
    registering and retrieving domains and domain-specific components.
    """
    
    def __init__(self)
    def register_domain(self, domain: Domain) -> None
    def unregister_domain(self, domain_id: str) -> None
    def get_domain(self, domain_id: str) -> Optional[Domain]
    def get_all_domains(self) -> List[Domain]
    def register_event_type(self, domain_id: str, event_type: str, event_class: Type[BaseEvent]) -> None
    def register_agent_type(self, domain_id: str, agent_type: str, agent_class: Type[BaseAgent]) -> None
    def register_relationship_type(self, domain_id: str, relationship_type: str, relationship_class: Type[BaseRelationship]) -> None
    def get_event_type(self, event_type: str) -> Optional[Type[BaseEvent]]
    def get_agent_type(self, agent_type: str) -> Optional[Type[BaseAgent]]
    def get_relationship_type(self, relationship_type: str) -> Optional[Type[BaseRelationship]]
```

### ExtensionPoint

```python
class ExtensionPoint(ABC):
    """
    Abstract base class for domain extension points.
    
    Extension points define interfaces that domain-specific implementations can
    implement to extend the core functionality of the framework.
    """
    
    def __init__(self, extension_point_id: str, name: str, description: str = "")
    
    @abstractmethod
    def initialize(self) -> None
    
    @abstractmethod
    def shutdown(self) -> None
```

For more detailed information on the API, please refer to the source code and inline documentation.
