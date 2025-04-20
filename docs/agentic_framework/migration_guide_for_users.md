# Agentic Game Framework: Migration Guide for Users

**Author:** Documentation Team  
**Version:** 1.0.0  
**Date:** April 19, 2025

## Table of Contents

- [Introduction](#introduction)
- [Migration Overview](#migration-overview)
- [Step-by-Step Migration](#step-by-step-migration)
  - [Step 1: Analyze Your Existing Code](#step-1-analyze-your-existing-code)
  - [Step 2: Set Up Dual-Mode Operation](#step-2-set-up-dual-mode-operation)
  - [Step 3: Migrate Event Processing](#step-3-migrate-event-processing)
  - [Step 4: Migrate Agents](#step-4-migrate-agents)
  - [Step 5: Migrate Memory and Relationships](#step-5-migrate-memory-and-relationships)
  - [Step 6: Test and Verify](#step-6-test-and-verify)
- [Common Migration Patterns](#common-migration-patterns)
  - [Converting Direct Calls to Events](#converting-direct-calls-to-events)
  - [Converting State to Agent Attributes](#converting-state-to-agent-attributes)
  - [Converting Relationships](#converting-relationships)
  - [Converting Memory Storage](#converting-memory-storage)
- [Architectural Comparison](#architectural-comparison)
- [Using Command-Line Flags](#using-command-line-flags)
- [Troubleshooting](#troubleshooting)
- [Examples](#examples)

## Introduction

This guide provides practical, step-by-step instructions for migrating your existing code to the new event-driven architecture of the Agentic Game Framework. The framework now supports both the legacy architecture and the new event-driven architecture, allowing for a gradual migration.

The migration process is designed to be incremental, allowing you to migrate components one at a time while maintaining functionality. This guide focuses on practical code examples and common patterns to help you through the process.

## Migration Overview

The migration involves several key changes:

1. **Event-Driven Communication**: Moving from direct method calls to event-based communication
2. **Agent Abstraction**: Converting specific entities to generic agents with specialized behavior
3. **Memory System**: Implementing a structured approach to agent memory
4. **Relationship System**: Formalizing relationships between agents
5. **Dual-Mode Operation**: Supporting both legacy and new architectures during migration

The framework provides tools to facilitate this migration, including architecture bridges, event converters, and command-line flags for selecting operation modes.

## Step-by-Step Migration

### Step 1: Analyze Your Existing Code

Begin by analyzing your existing code to identify key components and their interactions:

1. **Identify Entities**: List all entities (senators, players, etc.) in your system
2. **Map Communications**: Document how these entities communicate with each other
3. **Identify State**: List the state maintained by each entity
4. **Identify Relationships**: Document relationships between entities

**Example Analysis:**

```
Entities:
- Senator (name, faction, skills, reputation)
- Senate (senators, active debates, votes)
- Debate (topic, sponsor, arguments, votes)

Communications:
- Senate notifies Senators of new debates
- Senators submit speeches to Debates
- Senators vote on Debates
- Senate announces Debate results

State:
- Senator: reputation, relationships, past votes
- Senate: current session, active debates
- Debate: arguments, votes, status

Relationships:
- Senator-Senator: alliances, rivalries, trust
```

### Step 2: Set Up Dual-Mode Operation

Set up your system to run in dual-mode, which allows you to migrate components incrementally:

1. **Add Command-Line Flag**: Add a `--mode` flag to your main script
2. **Create Mode Handler**: Implement logic to run in legacy, new, or hybrid mode
3. **Set Up Architecture Bridge**: Create bridges between legacy and new components

**Example Code:**

```python
import argparse
from agentic_game_framework.integration.bridges import ArchitectureBridge
from agentic_game_framework.events.event_bus import EventBus

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["legacy", "new", "hybrid"], default="legacy",
                        help="Architecture mode to run in")
    args = parser.parse_args()
    
    if args.mode == "legacy":
        run_legacy_mode()
    elif args.mode == "new":
        run_new_mode()
    else:  # hybrid
        run_hybrid_mode()

def run_hybrid_mode():
    # Set up legacy components
    legacy_senate = LegacySenate()
    
    # Set up new components
    event_bus = EventBus()
    agent_manager = AgentManager(event_bus)
    
    # Create bridge between architectures
    bridge = SenateBridge(event_bus, legacy_senate)
    
    # Run simulation
    # ...
```

### Step 3: Migrate Event Processing

Convert your direct communication to event-based communication:

1. **Define Event Types**: Create event classes for each type of communication
2. **Create Event Bus**: Set up an event bus for distributing events
3. **Replace Direct Calls**: Convert direct method calls to event publishing
4. **Implement Event Handlers**: Add event handling logic to your components

**Example Original Code:**

```python
class LegacySenate:
    def start_debate(self, topic, sponsor):
        debate = Debate(topic, sponsor)
        self.active_debates.append(debate)
        
        # Direct notification to all senators
        for senator in self.senators:
            senator.notify_debate(debate)
```

**Example Migrated Code:**

```python
from agentic_game_framework.events.base import BaseEvent

class DebateStartEvent(BaseEvent):
    def __init__(self, topic, sponsor, **kwargs):
        super().__init__(
            event_type="senate.debate.start",
            source=sponsor,
            data={"topic": topic},
            **kwargs
        )

class Senate:
    def __init__(self, event_bus):
        self.event_bus = event_bus
        self.active_debates = []
    
    def start_debate(self, topic, sponsor):
        debate = Debate(topic, sponsor)
        self.active_debates.append(debate)
        
        # Publish event instead of direct notification
        event = DebateStartEvent(topic, sponsor)
        self.event_bus.publish(event)
```

### Step 4: Migrate Agents

Convert your entities to agents:

1. **Create Agent Classes**: Define agent classes for each entity type
2. **Implement Event Processing**: Add event processing logic to agents
3. **Implement Action Generation**: Add action generation logic to agents
4. **Register Agents**: Register agents with the agent manager

**Example Original Code:**

```python
class LegacySenator:
    def __init__(self, name, faction):
        self.name = name
        self.faction = faction
        self.reputation = 50
        self.relationships = {}
    
    def notify_debate(self, debate):
        # Process debate notification
        if self.is_interested(debate.topic):
            speech = self.generate_speech(debate.topic)
            debate.add_speech(self, speech)
```

**Example Migrated Code:**

```python
from agentic_game_framework.agents.base_agent import BaseAgent

class SenatorAgent(BaseAgent):
    def __init__(self, name, faction, **kwargs):
        super().__init__(
            agent_id=f"senator_{name.lower()}",
            attributes={
                "name": name,
                "faction": faction,
                "reputation": 50
            },
            **kwargs
        )
        
        # Subscribe to relevant event types
        self.subscribe_to_event("senate.debate.start")
    
    def process_event(self, event):
        """Process incoming events."""
        if event.event_type == "senate.debate.start":
            topic = event.data.get("topic")
            
            if self.is_interested(topic):
                return SpeechEvent(
                    source=self.id,
                    topic=topic,
                    content=self.generate_speech_content(topic)
                )
        
        return None
    
    def is_interested(self, topic):
        # Determine if senator is interested in topic
        # ...
        return True
    
    def generate_speech_content(self, topic):
        # Generate speech content based on topic and senator attributes
        # ...
        return f"{self.attributes['name']} speaks about {topic}..."
```

### Step 5: Migrate Memory and Relationships

Implement memory and relationship systems:

1. **Create Memory Types**: Define memory classes for different information types
2. **Implement Memory Storage**: Add memory creation and retrieval
3. **Define Relationship Types**: Create relationship classes for different relationship types
4. **Implement Relationship Logic**: Add relationship creation and updating

**Example Memory Implementation:**

```python
from agentic_game_framework.memory.memory_interface import MemoryItem

class SpeechMemory(MemoryItem):
    def __init__(self, speech_event, **kwargs):
        super().__init__(**kwargs)
        self.speaker_id = speech_event.source
        self.topic = speech_event.data.get("topic")
        self.content = speech_event.data.get("content")
        self.timestamp = speech_event.timestamp

# In SenatorAgent class:
def process_event(self, event):
    # Create memory of speech events
    if event.event_type == "senate.speech":
        memory = SpeechMemory(
            speech_event=event,
            importance=0.7 if event.source == self.id else 0.5
        )
        self.memory_manager.add_memory(memory)
    
    # Use memories in decision making
    if event.event_type == "senate.vote.request":
        topic = event.data.get("topic")
        # Retrieve relevant memories
        speech_memories = self.memory_manager.get_memories({
            "type": "speech",
            "topic": topic
        })
        # Use memories to inform vote decision
        # ...
```

**Example Relationship Implementation:**

```python
from agentic_game_framework.relationships.base_relationship import BaseRelationship

class PoliticalRelationship(BaseRelationship):
    def __init__(self, agent_a_id, agent_b_id, **kwargs):
        super().__init__(
            agent_a_id=agent_a_id,
            agent_b_id=agent_b_id,
            relationship_type="political",
            **kwargs
        )
        
        # Initialize political-specific attributes
        self.attributes.update({
            "trust": 0.5,
            "respect": 0.5,
            "agreement": 0.5
        })

# In a relationship manager:
def update_from_speech(self, speech_event):
    speaker_id = speech_event.source
    topic = speech_event.data.get("topic")
    
    # Update relationships based on speech content
    for relationship in self.get_relationships_for_agent(speaker_id):
        other_id = relationship.get_other_agent_id(speaker_id)
        other_agent = self.agent_manager.get_agent(other_id)
        
        # Calculate agreement factor
        agreement = self.calculate_agreement(
            other_agent.get_attribute("faction"),
            topic,
            speech_event.data.get("position")
        )
        
        # Update relationship attributes
        relationship.update_attribute("agreement", agreement * 0.1, relative=True)
        relationship.update_strength(agreement * 0.05)
```

### Step 6: Test and Verify

Test the migrated components:

1. **Unit Testing**: Test individual components in isolation
2. **Integration Testing**: Test interactions between components
3. **Comparison Testing**: Compare results from legacy and new architectures
4. **Performance Testing**: Measure performance in both architectures

**Example Test Code:**

```python
def test_senator_event_processing():
    # Set up event bus
    event_bus = EventBus()
    
    # Create senator agent
    senator = SenatorAgent(name="Cicero", faction="Optimates")
    
    # Create debate event
    debate_event = DebateStartEvent(
        topic="Land Reform",
        sponsor="caesar"
    )
    
    # Process event
    response = senator.process_event(debate_event)
    
    # Verify response
    assert response is not None
    assert response.event_type == "senate.speech"
    assert response.source == senator.id
    assert "Land Reform" in response.data.get("topic")
```

## Common Migration Patterns

### Converting Direct Calls to Events

Pattern for converting direct method calls to events:

1. **Identify Method Call**: Find direct method calls between components
2. **Create Event Class**: Create an event class for this type of communication
3. **Replace Call with Event**: Replace the method call with event publishing
4. **Implement Handler**: Add event handling logic to the receiving component

**Example:**

```python
# Before:
def deliver_speech(self, topic, content):
    for senator in self.senators:
        senator.hear_speech(self.id, topic, content)

# After:
def deliver_speech(self, topic, content):
    speech_event = SpeechEvent(
        source=self.id,
        topic=topic,
        content=content
    )
    self.event_bus.publish(speech_event)
```

### Converting State to Agent Attributes

Pattern for converting entity state to agent attributes:

1. **Identify State**: List all state variables for the entity
2. **Categorize State**: Separate into attributes (static/slow-changing) and state (dynamic)
3. **Initialize Agent**: Set up agent with attributes and initial state
4. **Update State**: Add state update logic in event handlers

**Example:**

```python
# Before:
class Senator:
    def __init__(self, name, faction):
        self.name = name
        self.faction = faction
        self.reputation = 50
        self.influence = 30
        self.current_position = None

# After:
class SenatorAgent(BaseAgent):
    def __init__(self, name, faction, **kwargs):
        # Attributes (slower-changing properties)
        attributes = {
            "name": name,
            "faction": faction,
        }
        
        # State (dynamic properties)
        initial_state = {
            "reputation": 50,
            "influence": 30,
            "current_position": None
        }
        
        super().__init__(
            agent_id=f"senator_{name.lower()}",
            attributes=attributes,
            initial_state=initial_state,
            **kwargs
        )
```

### Converting Relationships

Pattern for converting relationships:

1. **Identify Relationship**: Find relationship data between entities
2. **Create Relationship Class**: Define a relationship class for this type
3. **Initialize Relationships**: Set up initial relationships
4. **Update Logic**: Add relationship update logic

**Example:**

```python
# Before:
class Senator:
    def __init__(self, name, faction):
        self.name = name
        self.faction = faction
        self.relationships = {}  # senator_id -> value
    
    def update_relationship(self, other_id, change):
        self.relationships[other_id] = self.relationships.get(other_id, 0) + change

# After:
from agentic_game_framework.relationships.base_relationship import BaseRelationship

class SenatePoliticalRelationship(BaseRelationship):
    def __init__(self, senator_a_id, senator_b_id, **kwargs):
        super().__init__(
            agent_a_id=senator_a_id,
            agent_b_id=senator_b_id,
            relationship_type="political",
            **kwargs
        )

# In a relationship manager:
def initialize_relationships(self, senators):
    for i, senator_a in enumerate(senators):
        for senator_b in senators[i+1:]:
            # Check faction alignment
            same_faction = senator_a.get_attribute("faction") == senator_b.get_attribute("faction")
            initial_strength = 0.3 if same_faction else -0.1
            
            # Create relationship
            self.create_relationship(
                relationship_type="political",
                agent_a_id=senator_a.id,
                agent_b_id=senator_b.id,
                initial_strength=initial_strength
            )
```

### Converting Memory Storage

Pattern for converting memory storage:

1. **Identify Memory Data**: Find stored memory/history in entities
2. **Create Memory Classes**: Define memory classes for different types
3. **Add Memory Creation**: Add logic to create memories from events
4. **Add Memory Retrieval**: Add logic to retrieve and use memories

**Example:**

```python
# Before:
class Senator:
    def __init__(self, name, faction):
        self.name = name
        self.faction = faction
        self.speech_history = []  # List of past speeches
    
    def remember_speech(self, speaker, topic, content):
        self.speech_history.append({
            "speaker": speaker,
            "topic": topic,
            "content": content,
            "time": time.time()
        })

# After:
from agentic_game_framework.memory.memory_interface import MemoryItem

class SpeechMemory(MemoryItem):
    def __init__(self, speaker_id, topic, content, **kwargs):
        super().__init__(**kwargs)
        self.speaker_id = speaker_id
        self.topic = topic
        self.content = content

# In SenatorAgent class:
def process_event(self, event):
    if event.event_type == "senate.speech":
        # Create memory
        self.memory_manager.add_memory(SpeechMemory(
            speaker_id=event.source,
            topic=event.data.get("topic"),
            content=event.data.get("content"),
            importance=0.6,
            timestamp=time.time()
        ))
```

## Architectural Comparison

This table compares the legacy and new architectures:

| Feature | Legacy Architecture | New Event-Driven Architecture |
|---------|--------------------|-----------------------------|
| Communication | Direct method calls | Event publication and subscription |
| State Management | Centralized or global state | Distributed agent state |
| Agent Logic | Domain-specific logic | Domain-agnostic core with extensions |
| Memory | Ad-hoc or application-specific | Structured memory system |
| Relationships | Implicit or application-specific | Explicit relationship system |
| Scalability | Limited by direct coupling | Enhanced by decoupling |
| Testability | Harder to test due to coupling | Easier to test with event interception |
| Extensibility | Requires modifying existing code | Can extend through new subscribers |

## Using Command-Line Flags

The framework provides command-line flags for controlling the migration process:

```bash
# Run in legacy mode (original architecture)
python run_simulation.py --mode legacy

# Run in new mode (event-driven architecture)
python run_simulation.py --mode new

# Run in hybrid mode (both architectures)
python run_simulation.py --mode hybrid

# Run with specific comparison options
python run_simulation.py --mode hybrid --compare-output --save-results

# Run with specific components in new mode
python run_simulation.py --mode hybrid --new-components agents,events --legacy-components memory
```

## Troubleshooting

Common migration issues and solutions:

### Event Handling Issues

**Problem:** Events are published but not processed by subscribers.

**Solutions:**
- Check that agents are subscribed to the correct event types
- Verify that event types match exactly (including case)
- Ensure the event bus is properly shared between components
- Add debug logging to track event flow

### State Synchronization Issues

**Problem:** Legacy and new components get out of sync in hybrid mode.

**Solutions:**
- Implement proper bidirectional bridges
- Use event converters to ensure complete data translation
- Synchronize state at key points in the simulation
- Log state differences to identify desynchronization

### Performance Issues

**Problem:** The new architecture performs differently than the legacy one.

**Solutions:**
- Implement event batching for high-volume events
- Use event filters to reduce unnecessary processing
- Optimize memory retrieval queries
- Consider agent pooling for inactive agents

## Examples

Complete examples of migrated components:

### Migrated Senator Agent

```python
from agentic_game_framework.agents.base_agent import BaseAgent
from agentic_game_framework.events.base import BaseEvent

class SpeechEvent(BaseEvent):
    def __init__(self, source, topic, content, **kwargs):
        super().__init__(
            event_type="senate.speech",
            source=source,
            data={
                "topic": topic,
                "content": content
            },
            **kwargs
        )

class SenatorAgent(BaseAgent):
    def __init__(self, name, faction, attributes=None, **kwargs):
        # Set up senator-specific attributes
        senator_attributes = attributes or {}
        senator_attributes.update({
            "name": name,
            "faction": faction
        })
        
        # Set up initial state
        initial_state = {
            "reputation": 50,
            "influence": 30,
            "current_position": None,
            "speaking": False
        }
        
        super().__init__(
            agent_id=f"senator_{name.lower()}",
            attributes=senator_attributes,
            initial_state=initial_state,
            **kwargs
        )
        
        # Subscribe to relevant event types
        self.subscribe_to_event("senate.debate.start")
        self.subscribe_to_event("senate.speech")
        self.subscribe_to_event("senate.vote.request")
    
    def process_event(self, event):
        """Process incoming events."""
        if event.event_type == "senate.debate.start":
            return self._process_debate_start(event)
        elif event.event_type == "senate.speech":
            return self._process_speech(event)
        elif event.event_type == "senate.vote.request":
            return self._process_vote_request(event)
        
        return None
    
    def _process_debate_start(self, event):
        """Process a debate start event."""
        topic = event.data.get("topic")
        
        # Check if interested in the topic
        if self._is_interested_in_topic(topic):
            # Update state to indicate interest
            self.update_state("current_position", self._determine_position(topic))
            
            # If influential or quick to speak, generate a speech
            if self.get_attribute("influence", 0) > 50 or self.get_attribute("quick_to_speak", False):
                return SpeechEvent(
                    source=self.id,
                    topic=topic,
                    content=self._generate_speech_content(topic)
                )
        
        return None
    
    def _process_speech(self, event):
        """Process a speech event."""
        # Create memory of the speech
        self.memory_manager.add_memory(SpeechMemory(
            speaker_id=event.source,
            topic=event.data.get("topic"),
            content=event.data.get("content"),
            importance=0.6
        ))
        
        # Determine if should respond
        if self._should_respond_to_speech(event):
            # Generate response speech
            return SpeechEvent(
                source=self.id,
                topic=event.data.get("topic"),
                content=self._generate_response_content(event)
            )
        
        return None
    
    def _process_vote_request(self, event):
        """Process a vote request event."""
        topic = event.data.get("topic")
        
        # Retrieve memories about this topic
        topic_memories = self.memory_manager.get_memories({
            "topic": topic
        })
        
        # Determine vote based on position and memories
        vote = self._determine_vote(topic, topic_memories)
        
        return VoteEvent(
            source=self.id,
            topic=topic,
            vote=vote
        )
    
    def generate_action(self):
        """Generate an action based on current state."""
        # If not currently engaged, may initiate action
        if not self.get_state("speaking"):
            # Check for active debates
            active_debates = self.get_state("active_debates", [])
            
            if active_debates:
                # Choose a debate to speak on
                debate = self._choose_debate(active_debates)
                
                if debate:
                    return SpeechEvent(
                        source=self.id,
                        topic=debate.get("topic"),
                        content=self._generate_speech_content(debate.get("topic"))
                    )
        
        return None
    
    def _is_interested_in_topic(self, topic):
        """Determine if senator is interested in a topic."""
        faction = self.get_attribute("faction")
        interests = self.get_attribute("interests", [])
        
        # Check faction-based interests
        if faction == "Optimates" and topic in ["Traditional Values", "Senate Authority"]:
            return True
        elif faction == "Populares" and topic in ["Land Reform", "Debt Relief"]:
            return True
        
        # Check personal interests
        return topic in interests
    
    def _determine_position(self, topic):
        """Determine position on a topic."""
        faction = self.get_attribute("faction")
        
        # Simplified position determination based on faction
        if faction == "Optimates":
            if topic in ["Land Reform", "Debt Relief"]:
                return "against"
            else:
                return "for"
        else:  # Populares
            if topic in ["Land Reform", "Debt Relief"]:
                return "for"
            else:
                return "against"
    
    def _generate_speech_content(self, topic):
        """Generate speech content for a topic."""
        position = self.get_state("current_position")
        name = self.get_attribute("name")
        
        # Very simplified speech generation
        return f"{name} speaks {position} the matter of {topic}."
    
    def _should_respond_to_speech(self, event):
        """Determine if should respond to a speech."""
        # Check if this is our own speech
        if event.source == self.id:
            return False
        
        # Get relationship with speaker
        speaker_id = event.source
        relationship = self.relationship_manager.get_relationship(self.id, speaker_id)
        
        # Determine response likelihood based on relationship and topic
        response_likelihood = 0.3  # Base likelihood
        
        if relationship:
            # More likely to respond to allies or rivals
            strength = abs(relationship.get_strength())
            response_likelihood += strength * 0.4
        
        # Topic alignment affects response likelihood
        topic = event.data.get("topic")
        if self._is_interested_in_topic(topic):
            response_likelihood += 0.3
        
        # Random chance based on likelihood
        return random.random() < response_likelihood
    
    def _generate_response_content(self, speech_event):
        """Generate content in response to another speech."""
        speaker_id = speech_event.source
        topic = speech_event.data.get("topic")
        original_content = speech_event.data.get("content")
        
        # Get relationship with speaker
        relationship = self.relationship_manager.get_relationship(self.id, speaker_id)
        
        # Determine response type based on relationship and positions
        my_position = self.get_state("current_position")
        
        if relationship and relationship.get_strength() > 0.6:
            # Friendly response
            return f"I support the views of my colleague on {topic}."
        elif relationship and relationship.get_strength() < -0.6:
            # Hostile response
            return f"I must firmly disagree with the previous speaker on {topic}."
        else:
            # Neutral response
            return f"Regarding {topic}, I have my own perspective to share."
    
    def _determine_vote(self, topic, memories):
        """Determine vote on a topic based on position and memories."""
        position = self.get_state("current_position")
        
        # Default vote based on position
        if position == "for":
            vote = "aye"
        else:
            vote = "nay"
        
        # Check if memories influence vote
        influential_speeches = []
        for memory in memories:
            if hasattr(memory, "speaker_id") and memory.importance > 0.7:
                influential_speeches.append(memory)
        
        if influential_speeches:
            # Get relationships with influential speakers
            for speech in influential_speeches:
                relationship = self.relationship_manager.get_relationship(
                    self.id, speech.speaker_id
                )
                
                if relationship and relationship.get_strength() > 0.8:
                    # Very strong relationship may sway vote
                    return "aye" if speech.position == "for" else "nay"
        
        return vote
```

### Migrated Senate Session Bridge

```python
from agentic_game_framework.integration.bridges import ArchitectureBridge

class SenateSessionBridge(ArchitectureBridge):
    """Bridge between legacy Senate session and new event-driven architecture."""
    
    def __init__(self, event_bus, legacy_senate):
        """Initialize the bridge."""
        self.event_bus = event_bus
        self.legacy_senate = legacy_senate
        
        # Subscribe to relevant events
        self.event_bus.subscribe("senate.session.start", self._handle_session_start)
        self.event_bus.subscribe("senate.session.end", self._handle_session_end)
        self.event_bus.subscribe("senate.debate.start", self._handle_debate_start)
        self.event_bus.subscribe("senate.speech", self._handle_speech)
        self.event_bus.subscribe("senate.vote", self._handle_vote)
        
        # Set up legacy callbacks
        self.legacy_senate.on_debate_start = self._on_legacy_debate_start
        self.legacy_senate.on_speech_delivered = self._on_legacy_speech
        self.legacy_senate.on_vote_cast = self._on_legacy_vote
    
    def _handle_session_start(self, event):
        """Handle session start event."""
        self.legacy_senate.start_session(
            date=event.data.get("date"),
            presiding_official=event.data.get("presiding_official")
        )
    
    def _handle_session_end(self, event):
        """Handle session end event."""
        self.legacy_senate.end_session(
            outcomes=event.data.get("outcomes")
        )
    
    def _handle_debate_start(self, event):
        """Handle debate start event."""
        self.legacy_senate.start_debate(
            topic=event.data.get("topic"),
            sponsor=event.source
        )
    
    def _handle_speech(self, event):
        """Handle speech event."""
        speaker_id = event.source
        legacy_senator = self.get_legacy_senator(speaker_id)
        
        if legacy_senator:
            self.legacy_senate.register_speech(
                senator=legacy_senator,
                topic=event.data.get("topic"),
                content=event.data.get("content")
            )
    
    def _handle_vote(self, event):
        """Handle vote event."""
        voter_id = event.source
        legacy_senator = self.get_legacy_senator(voter_id)
        
        if legacy_senator:
            self.legacy_senate.register_vote(
                senator=legacy_senator,
                topic=event.data.get("topic"),
                vote=event.data.get("vote")
            )
    
    def _on_legacy_debate_start(self, topic, sponsor):
        """Handle legacy debate start."""
        sponsor_id = self.get_new_agent_id(sponsor)
        
        self.event_bus.publish(DebateStartEvent(
            topic=topic,
            source=sponsor_id
        ))
    
    def _on_legacy_speech(self, senator, topic, content):
        """Handle legacy speech."""
        speaker_id = self.get_new_agent_id(senator)
        
        self.event_bus.publish(SpeechEvent(
            source=speaker_id,
            topic=topic,
            content=content
        ))
    
    def _on_legacy_vote(self, senator, topic, vote):
        """Handle legacy vote."""
        voter_id = self.get_new_agent_id(senator)
        
        self.event_bus.publish(VoteEvent(
            source=voter_id,
            topic=topic,
            vote=vote
        ))
    
    def get_legacy_senator(self, agent_id):
        """Get legacy senator corresponding to a new agent ID."""
        # Extract name from agent ID (e.g., "senator_cicero" -> "Cicero")
        if agent_id.startswith("senator_"):
            name = agent_id[8:].capitalize()
            
            # Find senator with this name
            for senator in self.legacy_senate.senators:
                if senator.name.lower() == name.lower():
                    return senator
        
        return None
    
    def get_new_agent_id(self, legacy_senator):
        """Get new agent ID corresponding to a legacy senator."""
        return f"senator_{legacy_senator.name.lower()}"
```

This comprehensive guide should help you migrate your existing code to the new architecture in a step-by-step manner. If you encounter specific issues not covered in this guide, please consult the more detailed technical documentation or contact the framework support team.