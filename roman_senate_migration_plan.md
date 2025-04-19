# Roman Senate Migration Plan

## 1. Introduction

This document outlines a concrete migration plan for transitioning the Roman Senate simulation system to the new agentic game framework. Rather than maintaining multiple transitional states, this will be implemented as a fork that will become the mainline once completed.

## 2. Phased Migration Approach with Milestones

### Phase 1: Event System Migration
**Duration: 1-2 weeks**

#### Objectives:
- Map existing Senate event types to new framework's BaseEvent implementations
- Implement Senate-specific events extending the framework's BaseEvent
- Create mappings between Senate event data structures and framework event data structures

#### Key Components:
- Create Senate-specific event types (SpeechEvent, DebateEvent, etc.) as extensions of BaseEvent
- Implement serialization/deserialization for Senate-specific event content
- Set up the domain registration system for Senate event types

#### Example Mapping:
```python
# Example: Senate SpeechEvent Implementation
from agentic_game_framework.events.base import BaseEvent

class SpeechEvent(BaseEvent):
    """Speech event in the Roman Senate domain."""
    
    EVENT_TYPE = "senate.speech"
    
    def __init__(
        self,
        speaker_id: str,
        content: str,
        topic: str,
        stance: str,
        source: str = None,
        target: str = None,
        **kwargs
    ):
        """Initialize a speech event."""
        # Create data structure for the event
        data = {
            "speaker_id": speaker_id,
            "content": content,
            "topic": topic,
            "stance": stance
        }
        
        # Initialize the base event
        super().__init__(
            event_type=self.EVENT_TYPE,
            source=source or speaker_id,
            target=target,
            data=data,
            **kwargs
        )
```

### Phase 2: Agent System Migration
**Duration: 1-2 weeks**

#### Objectives:
- Implement Senate-specific agent types extending BaseAgent
- Map existing senator behaviors to framework agent patterns
- Create agent factories for Senate-specific agent types

#### Key Components:
- Create SenatorAgent implementation extending BaseAgent
- Implement event handling and agent behaviors
- Set up agent state management compatible with the framework

#### Example Mapping:
```python
# Example: SenatorAgent Implementation
from agentic_game_framework.agents.base_agent import BaseAgent
from agentic_game_framework.events.base import BaseEvent

class SenatorAgent(BaseAgent):
    """Roman Senator agent implementation."""
    
    def __init__(
        self,
        name: str,
        faction: str,
        rank: int,
        agent_id: str = None,
        attributes: dict = None,
        initial_state: dict = None
    ):
        """Initialize a senator agent."""
        # Set up senator-specific attributes
        senator_attributes = attributes or {}
        senator_attributes.update({
            "faction": faction,
            "rank": rank
        })
        
        # Initialize base agent
        super().__init__(
            name=name,
            agent_id=agent_id,
            attributes=senator_attributes,
            initial_state=initial_state or {}
        )
        
        # Subscribe to relevant event types
        self.subscribe_to_event("senate.speech")
        self.subscribe_to_event("senate.debate")
    
    def process_event(self, event: BaseEvent) -> None:
        """Process an incoming event."""
        # Handle different event types
        if event.event_type == "senate.speech":
            self._handle_speech_event(event)
        elif event.event_type == "senate.debate":
            self._handle_debate_event(event)
    
    def generate_action(self) -> BaseEvent:
        """Generate an action based on the current state."""
        # Decision making logic
        if self._should_speak():
            return self._generate_speech()
        return None
    
    def _handle_speech_event(self, event: BaseEvent) -> None:
        """Handle a speech event."""
        # Skip own speeches
        if event.source == self.id:
            return
        
        # Record in memory
        self._record_speech(event)
        
        # Determine if agent should react
        if self._should_react_to_speech(event):
            # Generate reaction
            reaction = self._generate_reaction(event)
            return reaction
    
    def _handle_debate_event(self, event: BaseEvent) -> None:
        """Handle a debate event."""
        # Implementation
        pass
```

### Phase 3: Memory System Migration
**Duration: 1-2 weeks**

#### Objectives:
- Implement memory system compatible with the framework
- Migrate existing memory structures to new framework patterns
- Design efficient memory storage and retrieval for Senate agents

#### Key Components:
- Create Senate-specific memory types extending framework memory interfaces
- Implement memory indexing and retrieval functions
- Set up memory persistence compatible with the framework

#### Example Mapping:
```python
# Example: Senator Memory Implementation
from agentic_game_framework.memory.memory_interface import MemoryInterface, MemoryItem
import time
import uuid

class SenatorMemory(MemoryInterface):
    """Memory system for senator agents."""
    
    def __init__(self, senator_id: str):
        """Initialize the senator memory."""
        self.senator_id = senator_id
        self._memories = {}
        self._event_index = {}
        self._speaker_index = {}
        self._topic_index = {}
    
    def add_memory(self, memory_item: MemoryItem) -> str:
        """Add a memory item to the memory store."""
        # Store the memory
        self._memories[memory_item.id] = memory_item
        
        # Update indices for efficient retrieval
        self._update_indices(memory_item)
        
        return memory_item.id
    
    def retrieve_memories(self, query: dict, limit=None, importance_threshold=None):
        """Retrieve memories matching the query."""
        # Implement efficient query logic using indices
        results = []
        
        # Example: Query by event type
        if "event_type" in query:
            event_type = query["event_type"]
            memory_ids = self._event_index.get(event_type, [])
            
            for memory_id in memory_ids:
                memory = self._memories.get(memory_id)
                if memory and (importance_threshold is None or memory.importance >= importance_threshold):
                    results.append(memory)
        
        # Sort by recency or importance
        results.sort(key=lambda m: m.timestamp, reverse=True)
        
        # Apply limit
        if limit is not None:
            results = results[:limit]
            
        return results
    
    def _update_indices(self, memory_item: MemoryItem) -> None:
        """Update memory indices for efficient retrieval."""
        # Index by event type
        event_type = memory_item.associations.get("event_type")
        if event_type:
            if event_type not in self._event_index:
                self._event_index[event_type] = []
            self._event_index[event_type].append(memory_item.id)
        
        # Index by speaker
        speaker_id = memory_item.associations.get("speaker_id")
        if speaker_id:
            if speaker_id not in self._speaker_index:
                self._speaker_index[speaker_id] = []
            self._speaker_index[speaker_id].append(memory_item.id)
        
        # Index by topic
        topic = memory_item.associations.get("topic")
        if topic:
            if topic not in self._topic_index:
                self._topic_index[topic] = []
            self._topic_index[topic].append(memory_item.id)
```

### Phase 4: Relationship System Migration
**Duration: 1-2 weeks**

#### Objectives:
- Implement Senate-specific relationship system compatible with the framework
- Migrate relationship types and dynamics to new framework patterns
- Set up relationship management and update functions

#### Key Components:
- Create Senate-specific relationship types extending BaseRelationship
- Implement relationship dynamics (formation, decay, update)
- Set up relationship indexing and querying

#### Example Mapping:
```python
# Example: Political Relationship Implementation
from agentic_game_framework.relationships.base_relationship import BaseRelationship
from agentic_game_framework.events.base import BaseEvent

class PoliticalRelationship(BaseRelationship):
    """Political relationship between senators."""
    
    def __init__(
        self,
        agent_a_id: str,
        agent_b_id: str,
        strength: float = 0.0,
        attributes: dict = None,
        relationship_id: str = None
    ):
        """Initialize a political relationship."""
        super().__init__(
            agent_a_id=agent_a_id,
            agent_b_id=agent_b_id,
            relationship_type="political",
            strength=strength,
            attributes=attributes,
            relationship_id=relationship_id
        )
        
        # Senate-specific relationship attributes
        self.attributes.setdefault("alliance_type", "none")
        self.attributes.setdefault("voting_similarity", 0.5)
        self.attributes.setdefault("last_interaction", None)
    
    def update(self, event: BaseEvent) -> bool:
        """Update the relationship based on an event."""
        updated = False
        
        # Update based on voting events
        if event.event_type == "senate.vote":
            # Get vote details
            agent_a_vote = self._get_agent_vote(event, self.agent_a_id)
            agent_b_vote = self._get_agent_vote(event, self.agent_b_id)
            
            if agent_a_vote is not None and agent_b_vote is not None:
                # Update voting similarity
                if agent_a_vote == agent_b_vote:
                    # Votes align - strengthen relationship
                    self._update_voting_similarity(True)
                    delta = 0.05
                else:
                    # Votes differ - weaken relationship
                    self._update_voting_similarity(False)
                    delta = -0.03
                
                # Update relationship strength
                self.update_strength(delta, f"Vote on {event.data.get('topic', 'unknown topic')}")
                updated = True
        
        # Update based on speech events
        elif event.event_type == "senate.speech":
            if self._event_involves_both_agents(event):
                # Update based on speech stance and content
                # Implementation details...
                updated = True
        
        # Record last interaction
        if updated:
            self.attributes["last_interaction"] = event.timestamp
            
        return updated
    
    def _update_voting_similarity(self, aligned: bool) -> None:
        """Update the voting similarity attribute."""
        current = self.attributes["voting_similarity"]
        if aligned:
            # Increase similarity (with diminishing returns)
            self.attributes["voting_similarity"] = current + (1 - current) * 0.1
        else:
            # Decrease similarity (with diminishing effects)
            self.attributes["voting_similarity"] = current * 0.9
```

### Phase 5: Senate Domain Implementation
**Duration: 1-2 weeks**

#### Objectives:
- Register Senate domain with the framework
- Implement Senate-specific domain logic and behaviors
- Set up domain extension points and customization

#### Key Components:
- Create SenateDomain class to register with domain registry
- Implement domain-specific logic and behaviors
- Set up extension points for customization

#### Example Implementation:
```python
# Example: Senate Domain Registration
from agentic_game_framework.domains.domain_registry import DomainRegistry

class SenateDomain:
    """Roman Senate domain implementation."""
    
    DOMAIN_ID = "roman_senate"
    
    def __init__(self, registry: DomainRegistry):
        """Initialize the Senate domain."""
        self.registry = registry
    
    def register(self):
        """Register the domain with the framework."""
        # Register domain
        self.registry.register_domain(
            domain_id=self.DOMAIN_ID,
            domain_config={
                "name": "Roman Senate Simulation",
                "description": "Simulation of ancient Roman Senate debates and politics",
                "version": "2.0.0"
            }
        )
        
        # Register event types
        self._register_event_types()
        
        # Register agent types
        self._register_agent_types()
        
        # Register relationship types
        self._register_relationship_types()
    
    def _register_event_types(self):
        """Register Senate-specific event types."""
        from senate.events import SpeechEvent, DebateEvent, VoteEvent
        
        self.registry.register_event_type(
            domain_id=self.DOMAIN_ID,
            event_type="senate.speech",
            event_config={
                "class": SpeechEvent,
                "description": "A speech by a senator"
            }
        )
        
        self.registry.register_event_type(
            domain_id=self.DOMAIN_ID,
            event_type="senate.debate",
            event_config={
                "class": DebateEvent,
                "description": "A debate in the Senate"
            }
        )
        
        self.registry.register_event_type(
            domain_id=self.DOMAIN_ID,
            event_type="senate.vote",
            event_config={
                "class": VoteEvent,
                "description": "A vote on a topic"
            }
        )
    
    def _register_agent_types(self):
        """Register Senate-specific agent types."""
        from senate.agents import SenatorAgent, ConsulAgent, PraetorAgent
        
        self.registry.register_agent_type(
            domain_id=self.DOMAIN_ID,
            agent_type="senator",
            agent_config={
                "class": SenatorAgent,
                "description": "A Roman senator"
            }
        )
        
        self.registry.register_agent_type(
            domain_id=self.DOMAIN_ID,
            agent_type="consul",
            agent_config={
                "class": ConsulAgent,
                "description": "A Roman consul with executive power"
            }
        )
    
    def _register_relationship_types(self):
        """Register Senate-specific relationship types."""
        from senate.relationships import PoliticalRelationship, PersonalRelationship
        
        self.registry.register_relationship_type(
            domain_id=self.DOMAIN_ID,
            relationship_type="political",
            relationship_config={
                "class": PoliticalRelationship,
                "description": "Political alliance or opposition",
                "decay_rate": 0.08
            }
        )
        
        self.registry.register_relationship_type(
            domain_id=self.DOMAIN_ID,
            relationship_type="personal",
            relationship_config={
                "class": PersonalRelationship,
                "description": "Personal friendship or animosity",
                "decay_rate": 0.04
            }
        )
```

### Phase 6: Integration Testing
**Duration: 1 week**

#### Objectives:
- Implement test suite for migrated components
- Validate domain-specific behavior against expected outcomes
- Perform integration testing across component boundaries

#### Key Components:
- Create unit tests for individual components
- Implement integration tests for component interactions
- Validate Senate-specific behavior against expected outcomes

#### Example Test:
```python
# Example: Test for SenatorAgent Speech Generation
import unittest
from senate.agents import SenatorAgent
from agentic_game_framework.events.event_bus import EventBus

class TestSenatorSpeech(unittest.TestCase):
    """Test senator speech generation."""
    
    def setUp(self):
        """Set up the test."""
        self.event_bus = EventBus()
        
        # Create test senators
        self.senator_a = SenatorAgent(
            name="Cato",
            faction="Optimates",
            rank=3,
            attributes={"eloquence": 0.8, "conservatism": 0.7}
        )
        
        self.senator_b = SenatorAgent(
            name="Caesar",
            faction="Populares",
            rank=4,
            attributes={"eloquence": 0.9, "conservatism": 0.2}
        )
        
        # Subscribe to event bus
        self.events_received = []
        self.event_bus.subscribe("senate.speech", self._record_event)
    
    def _record_event(self, event):
        """Record an event for testing."""
        self.events_received.append(event)
    
    def test_speech_generation(self):
        """Test that senators can generate speeches."""
        # Set up debate topic
        topic = "Land Reform"
        
        # Generate speech from senator
        speech_event = self.senator_a.generate_speech(topic)
        
        # Publish the event
        self.event_bus.publish(speech_event)
        
        # Verify event was received
        self.assertEqual(len(self.events_received), 1)
        
        # Verify speech content
        received_event = self.events_received[0]
        self.assertEqual(received_event.event_type, "senate.speech")
        self.assertEqual(received_event.source, self.senator_a.id)
        self.assertEqual(received_event.data["topic"], topic)
        self.assertIsNotNone(received_event.data["content"])
        
        # Verify speech stance aligns with senator's attributes
        # Conservative senator should have conservative stance on land reform
        self.assertIn(received_event.data["stance"], ["conservative", "moderate_conservative"])
```

### Phase 7: Documentation and Deployment
**Duration: 1 week**

#### Objectives:
- Document the migrated system architecture and components
- Create user guide for interacting with the new system
- Implement deployment scripts and configurations

#### Key Components:
- Create architecture documentation
- Implement user guide and tutorials
- Set up deployment configurations

## 3. Component Mapping Between Old and New Systems

### Event System Mapping

| Roman Senate Component | Agentic Framework Component | Migration Approach |
|------------------------|---------------------------|-------------------|
| `Event` | `BaseEvent` | Create Senate-specific events extending BaseEvent |
| `EventBus` | `EventBus` | Use framework EventBus directly |
| `SpeechEvent` | `SpeechEvent extends BaseEvent` | Implement as domain-specific event |
| `DebateEvent` | `DebateEvent extends BaseEvent` | Implement as domain-specific event |
| `ReactionEvent` | `ReactionEvent extends BaseEvent` | Implement as domain-specific event |

### Agent System Mapping

| Roman Senate Component | Agentic Framework Component | Migration Approach |
|------------------------|---------------------------|-------------------|
| `SenatorAgent` | `SenatorAgent extends BaseAgent` | Implement as domain-specific agent |
| `EventDrivenSenatorAgent` | `SenatorAgent with event processing` | Consolidate into single SenatorAgent class |
| `RelationshipAwareSenatorAgent` | `SenatorAgent with relationship awareness` | Consolidate into single SenatorAgent class |

### Memory System Mapping

| Roman Senate Component | Agentic Framework Component | Migration Approach |
|------------------------|---------------------------|-------------------|
| `AgentMemory` | `MemoryInterface` | Implement SenatorMemory extending MemoryInterface |
| `EventMemory` | `SenatorMemory` | Consolidate into a single memory implementation |
| `EnhancedEventMemory` | `SenatorMemory` | Consolidate into a single memory implementation |

### Relationship System Mapping

| Roman Senate Component | Agentic Framework Component | Migration Approach |
|------------------------|---------------------------|-------------------|
| `RelationshipManager` | `RelationshipManager` | Use framework RelationshipManager directly |
| Relationship types | Senate-specific relationship classes | Create classes extending BaseRelationship |

## 4. Timeline and Resource Estimates

| Phase | Timeline | Resources | Deliverables |
|-------|----------|-----------|-------------|
| 1: Event System Migration | Week 1-2 | 1 Developer | Senate event types, event conversion utilities |
| 2: Agent System Migration | Week 2-3 | 1 Developer | Senate agent types, agent factories |
| 3: Memory System Migration | Week 3-4 | 1 Developer | Senate memory system, memory persistence |
| 4: Relationship System Migration | Week 4-5 | 1 Developer | Senate relationship types, relationship management |
| 5: Senate Domain Implementation | Week 5-6 | 1 Developer | Senate domain registration, domain-specific logic |
| 6: Integration Testing | Week 6-7 | 1 Developer, 1 QA | Test suite, validation of behavior |
| 7: Documentation and Deployment | Week 7-8 | 1 Developer | Documentation, deployment scripts |

## 5. Validation and Testing Strategy

### Unit Testing

1. **Event System Tests**
   - Verify event creation, serialization, and deserialization
   - Test event distribution through EventBus
   - Validate event handling in subscribers

2. **Agent System Tests**
   - Test agent creation and initialization
   - Verify agent event processing
   - Validate agent decision making and action generation

3. **Memory System Tests**
   - Test memory storage and retrieval
   - Verify memory indexing and search
   - Validate memory persistence and loading

4. **Relationship System Tests**
   - Test relationship creation and initialization
   - Verify relationship updates based on events
   - Validate relationship decay and dynamics

### Integration Testing

1. **Cross-Component Integration**
   - Test agent-memory integration
   - Verify agent-relationship integration
   - Validate event-relationship-memory flow

2. **Scenario-Based Testing**
   - Implement test scenarios based on existing system
   - Verify complex multi-component interactions
   - Validate overall system behavior

3. **Performance Testing**
   - Test system performance with large numbers of agents
   - Verify memory usage and optimization
   - Validate event processing throughput

## 6. Risk Assessment and Mitigation

| Risk | Impact | Likelihood | Mitigation Strategy |
|------|--------|------------|---------------------|
| Complex domain-specific behavior | High | Medium | Thorough analysis of existing system, comprehensive testing |
| Performance issues | Medium | Low | Performance profiling, optimization in critical paths |
| Framework limitations | Medium | Low | Extend framework as needed, document extensions |
| Timeline slippage | Medium | Medium | Clear prioritization, focus on core functionality first |
| Knowledge transfer | Medium | Low | Thorough documentation, pair programming |

## 7. Code Examples for Key Migration Patterns

### Event System Migration

```python
# Old Event Implementation
class SpeechEvent(Event):
    TYPE = "speech"
    
    def __init__(self, speaker, content, stance, topic):
        super().__init__(self.TYPE, speaker)
        self.content = content
        self.stance = stance
        self.topic = topic
        self.metadata = {
            "content": content,
            "stance": stance,
            "topic": topic
        }

# New Event Implementation
class SpeechEvent(BaseEvent):
    EVENT_TYPE = "senate.speech"
    
    def __init__(self, speaker_id, content, stance, topic, **kwargs):
        data = {
            "content": content,
            "stance": stance,
            "topic": topic
        }
        
        super().__init__(
            event_type=self.EVENT_TYPE,
            source=speaker_id,
            data=data,
            **kwargs
        )
    
    @property
    def content(self):
        return self.data.get("content", "")
    
    @property
    def stance(self):
        return self.data.get("stance", "")
    
    @property
    def topic(self):
        return self.data.get("topic", "")
```

### Agent System Migration

```python
# Old Senator Agent Implementation
class SenatorAgent:
    def __init__(self, senator, llm_provider):
        self.senator = senator
        self.llm_provider = llm_provider
        self.memory = AgentMemory()
        self.current_stance = None
    
    def decide_stance(self, topic, context):
        # Implementation...
        pass
    
    def generate_speech(self, topic, context):
        # Implementation...
        pass

# New Senator Agent Implementation
class SenatorAgent(BaseAgent):
    def __init__(self, name, faction, rank, **kwargs):
        attributes = kwargs.pop("attributes", {})
        attributes.update({
            "faction": faction,
            "rank": rank
        })
        
        super().__init__(name=name, attributes=attributes, **kwargs)
        
        # Senator-specific initialization
        self.current_stance = None
        
        # Subscribe to relevant events
        self.subscribe_to_event("senate.speech")
        self.subscribe_to_event("senate.debate")
    
    def process_event(self, event):
        # Event handling implementation
        if event.event_type == "senate.speech":
            self._handle_speech(event)
        elif event.event_type == "senate.debate":
            self._handle_debate(event)
    
    def generate_action(self):
        # Action generation implementation
        if self._should_speak():
            return self._generate_speech()
        return None
    
    def decide_stance(self, topic):
        # Stance decision implementation
        # ...
        pass
```

### Memory System Migration

```python
# Old Memory Implementation
class EventMemory(AgentMemory):
    def __init__(self):
        super().__init__()
        self.event_history = []
        self.reaction_history = []
    
    def record_event(self, event):
        # Implementation...
        pass
    
    def get_events_by_type(self, event_type):
        # Implementation...
        pass

# New Memory Implementation
class SenatorMemory(MemoryInterface):
    def __init__(self, senator_id):
        self.senator_id = senator_id
        self._memories = {}
        self._indices = {}
    
    def add_memory(self, memory_item):
        # Store memory
        self._memories[memory_item.id] = memory_item
        
        # Update indices
        self._update_indices(memory_item)
        
        return memory_item.id
    
    def retrieve_memories(self, query, limit=None, importance_threshold=None):
        # Query implementation using indices
        # ...
        pass
    
    def record_event(self, event):
        # Create memory item from event
        memory_id = str(uuid.uuid4())
        timestamp = time.time()
        
        memory_item = MemoryItem(
            memory_id=memory_id,
            timestamp=timestamp,
            content=event.to_dict(),
            importance=0.5,  # Default importance
            associations={
                "event_type": event.event_type,
                "source": event.source
            }
        )
        
        # Add to memory
        return self.add_memory(memory_item)
```

### Relationship System Migration

```python
# Old Relationship Implementation
class RelationshipManager:
    def __init__(self, senator_id, event_bus, memory):
        self.senator_id = senator_id
        self.event_bus = event_bus
        self.memory = memory
        self.relationship_cache = {}
    
    def update_relationship(self, target_senator_id, relationship_type, change_value, reason):
        # Implementation...
        pass
    
    def get_relationship(self, target_senator_id, relationship_type=None):
        # Implementation...
        pass

# New Relationship Implementation
from agentic_game_framework.relationships.base_relationship import BaseRelationship
from agentic_game_framework.relationships.relationship_manager import RelationshipManager

# Define relationship types
class PoliticalRelationship(BaseRelationship):
    def __init__(self, agent_a_id, agent_b_id, strength=0.0, **kwargs):
        super().__init__(
            agent_a_id=agent_a_id,
            agent_b_id=agent_b_id,
            relationship_type="political",
            strength=strength,
            **kwargs
        )
    
    def update(self, event):
        # Implementation for updating based on events
        # ...
        pass

# Using the framework relationship manager
relationship_manager = RelationshipManager()

# Creating relationships
relationship = PoliticalRelationship(
    agent_a_id="senator_1",
    agent_b_id="senator_2",
    strength=0.3,
    attributes={"alliance_type": "faction"}
)

# Add to manager
relationship_manager.add_relationship(relationship)

# Retrieving relationships
rel = relationship_manager.get_relationship_between("senator_1", "senator_2")
```

## 8. Conclusion

This migration plan provides a comprehensive approach to transitioning the Roman Senate system to the new agentic game framework. By following this component-based migration approach, we can efficiently implement the Senate domain using the new framework's abstractions and capabilities.

The plan prioritizes direct implementation over transitional compatibility, which simplifies the migration process and reduces complexity. Each phase focuses on a specific component group, allowing for focused development and testing.

The ultimate goal is a clean implementation of the Roman Senate system using the new framework, maintaining all the functionality and behavior of the original system while leveraging the new framework's improved architecture, performance, and scalability.