# Roman Senate Event System: Examples

**Author:** Documentation Team  
**Version:** 1.0.0  
**Date:** April 18, 2025

## Table of Contents

- [Introduction](#introduction)
- [Basic Usage Examples](#basic-usage-examples)
  - [Setting Up the Event System](#setting-up-the-event-system)
  - [Creating and Publishing Events](#creating-and-publishing-events)
  - [Subscribing to Events](#subscribing-to-events)
- [Debate Examples](#debate-examples)
  - [Starting and Ending Debates](#starting-and-ending-debates)
  - [Managing Speakers](#managing-speakers)
  - [Publishing Speeches](#publishing-speeches)
- [Senator Agent Examples](#senator-agent-examples)
  - [Creating Event-Driven Senators](#creating-event-driven-senators)
  - [Handling Speech Events](#handling-speech-events)
  - [Generating Reactions](#generating-reactions)
  - [Generating Interjections](#generating-interjections)
  - [Changing Stances](#changing-stances)
- [Event Memory Examples](#event-memory-examples)
  - [Recording Events](#recording-events)
  - [Retrieving Events](#retrieving-events)
  - [Tracking Relationships](#tracking-relationships)
- [Advanced Examples](#advanced-examples)
  - [Custom Event Types](#custom-event-types)
  - [Custom Event Handlers](#custom-event-handlers)
  - [Event Filtering](#event-filtering)
  - [Priority-Based Handling](#priority-based-handling)
- [Integration Examples](#integration-examples)
  - [Integrating with Existing Code](#integrating-with-existing-code)
  - [Integrating with Logging](#integrating-with-logging)
- [Testing Examples](#testing-examples)
  - [Unit Testing Events](#unit-testing-events)
  - [Testing Event Flow](#testing-event-flow)

## Introduction

This document provides practical examples of how to use the Roman Senate Event System. Each example includes code snippets and explanations to help you understand how to implement and extend the event-driven architecture.

## Basic Usage Examples

### Setting Up the Event System

The first step is to set up the event system with an `EventBus` and a `DebateManager`:

```python
import asyncio
from roman_senate.core.events import EventBus, DebateManager

# Create the event bus
event_bus = EventBus()

# Create a game state (can be a simple dictionary for testing)
game_state = {"year": -50, "month": 3, "day": 15}

# Create the debate manager
debate_manager = DebateManager(event_bus, game_state)

# Now you're ready to use the event system
```

### Creating and Publishing Events

You can create and publish events to the event bus:

```python
from roman_senate.core.events import Event, SpeechEvent

# Create a simple event
simple_event = Event(
    event_type="custom_event",
    source="example_script",
    metadata={"key": "value"}
)

# Publish the event
await event_bus.publish(simple_event)

# Create a speech event
speech_event = SpeechEvent(
    speaker={"id": "senator1", "name": "Cato", "faction": "Optimates", "rank": 4},
    topic="Expansion in Gaul",
    latin_content="Ceterum censeo Carthaginem esse delendam",
    english_content="Furthermore, I think Carthage must be destroyed",
    stance="support",
    key_points=["Carthage is a threat", "War is necessary"]
)

# Publish the speech event
await event_bus.publish(speech_event)
```

### Subscribing to Events

Components can subscribe to events they're interested in:

```python
# Define an event handler function
async def handle_custom_event(event):
    print(f"Received event: {event.event_type}")
    print(f"Metadata: {event.metadata}")

# Subscribe to a specific event type
event_bus.subscribe("custom_event", handle_custom_event)

# Define a class-based handler
class SpeechHandler:
    async def handle_event(self, event):
        if event.event_type == "speech":
            print(f"Speech by {event.speaker.get('name')}: {event.english_content}")

# Create an instance and subscribe
speech_handler = SpeechHandler()
event_bus.subscribe("speech", speech_handler.handle_event)
```

## Debate Examples

### Starting and Ending Debates

The `DebateManager` handles the debate lifecycle:

```python
# Define senators
senators = [
    {"id": "senator1", "name": "Cato", "faction": "Optimates", "rank": 4},
    {"id": "senator2", "name": "Caesar", "faction": "Populares", "rank": 3},
    {"id": "senator3", "name": "Cicero", "faction": "Optimates", "rank": 2}
]

# Start a debate
topic = "Whether Rome should go to war with Carthage"
await debate_manager.start_debate(topic, senators)

# ... debate activities ...

# End the debate
await debate_manager.end_debate()
```

### Managing Speakers

The `DebateManager` manages the speaker queue:

```python
# Register a senator to speak
await debate_manager.register_speaker(senators[0])

# Get the next speaker
next_speaker = await debate_manager.next_speaker()
print(f"Next speaker: {next_speaker.get('name')}")
```

### Publishing Speeches

The `DebateManager` can publish speeches:

```python
# Publish a speech
speech_event = await debate_manager.publish_speech(
    speaker=senators[0],
    topic="Expansion in Gaul",
    latin_content="Ceterum censeo Carthaginem esse delendam",
    english_content="Furthermore, I think Carthage must be destroyed",
    stance="support",
    key_points=["Carthage is a threat", "War is necessary"]
)

# The speech event is now available to all subscribers
```

## Senator Agent Examples

### Creating Event-Driven Senators

Create senator agents that can react to events:

```python
from roman_senate.agents.event_driven_senator_agent import EventDrivenSenatorAgent
from roman_senate.utils.llm.mock_provider import MockLLMProvider

# Create a mock LLM provider for testing
llm_provider = MockLLMProvider()

# Create senator agents
senator_agents = [
    EventDrivenSenatorAgent(senator, llm_provider, event_bus)
    for senator in senators
]

# Now the senators will automatically subscribe to relevant events
```

### Handling Speech Events

Senator agents handle speech events:

```python
# This is automatically called when a speech event is published
async def handle_speech_event(self, event: SpeechEvent) -> None:
    """Handle a speech event."""
    # Skip own speeches
    if event.speaker.get("id") == self.senator.get("id"):
        return
        
    # Record the event in memory
    self.memory.record_event(event)
    
    # Record interaction with the speaker
    self.memory.add_interaction(
        event.speaker.get("name"),
        "heard_speech",
        {
            "topic": event.metadata.get("topic"),
            "stance": event.stance,
            "speech_id": event.speech_id
        }
    )
    
    # Store current speaker for potential reactions
    self.current_speaker = event.speaker
    
    # Determine if senator should react to the speech
    if await self._should_react_to_speech(event):
        # Generate and publish reaction
        await self._generate_and_publish_reaction(event)
        
    # Determine if senator should interject
    if await self._should_interject(event):
        # Generate and publish interjection
        await self._generate_and_publish_interjection(event)
        
    # Check if stance should change based on speech
    await self._consider_stance_change(event)
```

### Generating Reactions

Senators can generate reactions to speeches:

```python
# Determine if the senator should react to a speech
async def _should_react_to_speech(self, event: SpeechEvent) -> bool:
    """Determine if the senator should react to a speech."""
    # Base probability of reaction
    base_probability = 0.3  # 30% chance by default
    
    # Adjust based on relationship with speaker
    relationship = self.memory.relationship_scores.get(event.speaker.get("name", ""), 0)
    relationship_factor = abs(relationship) * 0.2  # Max +/- 0.2
    
    # Faction alignment affects reaction probability
    speaker_faction = event.speaker.get("faction", "")
    if speaker_faction == self.faction:
        # More likely to react positively to same faction
        if relationship >= 0:
            base_probability += 0.1
    else:
        # More likely to react negatively to different faction
        if relationship < 0:
            base_probability += 0.1
            
    # Calculate final probability
    final_probability = min(0.8, base_probability + relationship_factor)
    
    # Decide whether to react
    return random.random() < final_probability

# Generate and publish a reaction
async def _generate_and_publish_reaction(self, event: SpeechEvent) -> None:
    """Generate and publish a reaction to a speech."""
    # Determine reaction type based on relationship and stance
    relationship = self.memory.relationship_scores.get(event.speaker.get("name", ""), 0)
    stance_agreement = (self.current_stance == event.stance)
    
    if relationship > 0.3 and stance_agreement:
        reaction_type = random.choice(["agreement", "interest"])
    elif relationship < -0.3 and not stance_agreement:
        reaction_type = random.choice(["disagreement", "skepticism"])
    else:
        reaction_type = random.choice(["neutral", "agreement", "disagreement", "interest", "boredom", "skepticism"])
        
    # Generate reaction content
    reaction_content = await self._generate_reaction_content(event, reaction_type)
    
    # Create and publish reaction event
    reaction_event = ReactionEvent(
        reactor=self.senator,
        target_event=event,
        reaction_type=reaction_type,
        content=reaction_content
    )
    
    await self.event_bus.publish(reaction_event)
```

### Generating Interjections

Higher-ranking senators may interject during speeches:

```python
# Determine if the senator should interject
async def _should_interject(self, event: SpeechEvent) -> bool:
    """Determine if the senator should interject during a speech."""
    # Base probability of interjection (lower than reaction)
    base_probability = 0.1  # 10% chance by default
    
    # Adjust based on relationship with speaker
    relationship = self.memory.relationship_scores.get(event.speaker.get("name", ""), 0)
    relationship_factor = abs(relationship) * 0.15  # Max +/- 0.15
    
    # Rank affects interjection probability
    rank = self.senator.get("rank", 0)
    rank_factor = min(0.2, rank * 0.05)  # Max +0.2 for rank 4+
    
    # Stance disagreement increases interjection probability
    stance_factor = 0
    if self.current_stance and self.current_stance != event.stance:
        stance_factor = 0.15
        
    # Calculate final probability
    final_probability = min(0.5, base_probability + relationship_factor + rank_factor + stance_factor)
    
    # Decide whether to interject
    return random.random() < final_probability

# Generate and publish an interjection
async def _generate_and_publish_interjection(self, event: SpeechEvent) -> None:
    """Generate and publish an interjection during a speech."""
    # Determine interjection type
    interjection_type = await self._determine_interjection_type(event)
    
    # Generate interjection content
    latin_content, english_content = await self._generate_interjection_content(
        event.speaker.get("name", "Unknown"),
        interjection_type
    )
    
    # Create and publish interjection event
    interjection_event = InterjectionEvent(
        interjector=self.senator,
        target_speaker=event.speaker,
        interjection_type=interjection_type,
        latin_content=latin_content,
        english_content=english_content,
        target_speech_id=event.speech_id,
        causes_disruption=(interjection_type.value in ["procedural", "emotional"])
    )
    
    await self.event_bus.publish(interjection_event)
```

### Changing Stances

Senators may change their stance based on persuasive speeches:

```python
async def _consider_stance_change(self, event: SpeechEvent) -> None:
    """Consider changing stance based on a speech."""
    # Only consider stance change if we have a current stance and topic
    if not self.current_stance or not self.active_debate_topic:
        return
        
    # Skip if the speech is on a different topic
    speech_topic = event.metadata.get("topic")
    if speech_topic != self.active_debate_topic:
        return
        
    # Base probability of stance change (very low)
    base_probability = 0.05  # 5% chance by default
    
    # Adjust based on relationship with speaker
    relationship = self.memory.relationship_scores.get(event.speaker.get("name", ""), 0)
    relationship_factor = max(0, relationship * 0.1)  # Only positive relationships increase chance
    
    # Faction alignment affects stance change probability
    speaker_faction = event.speaker.get("faction", "")
    faction_factor = 0.05 if speaker_faction == self.faction else 0
    
    # Speaker rank affects persuasiveness
    rank_factor = min(0.1, event.speaker.get("rank", 0) * 0.025)  # Max +0.1 for rank 4+
    
    # Calculate final probability
    final_probability = min(0.3, base_probability + relationship_factor + faction_factor + rank_factor)
    
    # Decide whether to change stance
    if random.random() < final_probability:
        # Determine new stance (usually move toward speaker's stance)
        speaker_stance = event.stance
        old_stance = self.current_stance
        
        # If we're neutral, adopt speaker's stance
        if old_stance == "neutral":
            new_stance = speaker_stance
        # If we disagree with speaker, move to neutral
        elif old_stance != speaker_stance:
            new_stance = "neutral"
        # If we already agree, no change
        else:
            return
            
        # Record stance change
        self.current_stance = new_stance
        self.memory.record_stance_change(
            self.active_debate_topic,
            old_stance,
            new_stance,
            f"Persuaded by {event.speaker.get('name')}'s speech",
            event.event_id
        )
```

## Event Memory Examples

### Recording Events

The `EventMemory` class records events and related information:

```python
from roman_senate.agents.event_memory import EventMemory

# Create an event memory
memory = EventMemory()

# Record an event
memory.record_event(speech_event)

# Record a reaction to an event
memory.record_reaction(
    event_id=speech_event.event_id,
    reaction_type="agreement",
    content="Nods in agreement"
)

# Record a stance change
memory.record_stance_change(
    topic="Expansion in Gaul",
    old_stance="neutral",
    new_stance="support",
    reason="Persuaded by Cato's speech",
    event_id=speech_event.event_id
)

# Record how an event affected a relationship
memory.record_event_relationship_impact(
    senator_name="Cato",
    event_id=speech_event.event_id,
    impact=0.1,  # Positive impact
    reason="Agreed with speech"
)
```

### Retrieving Events

The `EventMemory` class provides methods to retrieve events:

```python
# Get events by type
speech_events = memory.get_events_by_type("speech")

# Get events by source
cato_events = memory.get_events_by_source("Cato")

# Get reactions to a specific event
reactions = memory.get_reactions_to_event(speech_event.event_id)

# Get stance changes for a topic
stance_changes = memory.get_stance_changes_for_topic("Expansion in Gaul")

# Get relationship impacts with a specific senator
relationship_impacts = memory.get_relationship_impacts_by_senator("Cato")

# Get recent events
recent_events = memory.get_recent_events(count=5)
```

### Tracking Relationships

The `EventMemory` class tracks relationships between senators:

```python
# Get the current relationship score with a senator
relationship_score = memory.relationship_scores.get("Cato", 0)

# Update a relationship based on an interaction
memory.update_relationship("Cato", 0.1)  # Improve relationship

# Add an interaction to the history
memory.add_interaction(
    "Cato",
    "agreed_with_speech",
    {"topic": "Expansion in Gaul", "stance": "support"}
)

# Get all interactions with a senator
interactions = memory.get_interactions_with("Cato")
```

## Advanced Examples

### Custom Event Types

You can create custom event types by extending the `Event` class:

```python
from roman_senate.core.events import Event

class VoteEvent(Event):
    """Event representing a vote cast by a senator."""
    
    TYPE = "vote"
    
    def __init__(self, senator, topic, vote_value, metadata=None):
        super().__init__(
            event_type=self.TYPE,
            source=senator,
            metadata=metadata or {}
        )
        self.senator = senator
        self.topic = topic
        self.vote_value = vote_value
        
        # Add vote-specific metadata
        self.metadata.update({
            "topic": topic,
            "vote_value": vote_value,
            "senator_name": senator.get("name", "Unknown"),
            "senator_faction": senator.get("faction", "Unknown")
        })
        
    def to_dict(self):
        """Convert to dictionary, including vote-specific fields."""
        data = super().to_dict()
        data.update({
            "senator": {
                "id": self.senator.get("id"),
                "name": self.senator.get("name"),
                "faction": self.senator.get("faction")
            },
            "topic": self.topic,
            "vote_value": self.vote_value
        })
        return data

# Create and publish a vote event
vote_event = VoteEvent(
    senator={"id": "senator1", "name": "Cato", "faction": "Optimates", "rank": 4},
    topic="Expansion in Gaul",
    vote_value="support"
)

await event_bus.publish(vote_event)
```

### Custom Event Handlers

You can create custom event handlers to process specific event types:

```python
class VoteRecorder:
    """Records votes cast by senators."""
    
    def __init__(self, event_bus):
        self.event_bus = event_bus
        self.votes = {}
        
        # Subscribe to vote events
        self.event_bus.subscribe(VoteEvent.TYPE, self.handle_event)
        
    async def handle_event(self, event):
        """Handle a vote event."""
        if event.event_type != VoteEvent.TYPE:
            return
            
        # Record the vote
        topic = event.topic
        senator_name = event.senator.get("name", "Unknown")
        vote_value = event.vote_value
        
        if topic not in self.votes:
            self.votes[topic] = {}
            
        self.votes[topic][senator_name] = vote_value
        
        # Log the vote
        print(f"Vote recorded: {senator_name} voted {vote_value} on {topic}")
        
    def get_votes_for_topic(self, topic):
        """Get all votes for a specific topic."""
        return self.votes.get(topic, {})
        
    def get_vote_count(self, topic, vote_value):
        """Count votes of a specific value for a topic."""
        votes = self.get_votes_for_topic(topic)
        return sum(1 for v in votes.values() if v == vote_value)

# Create a vote recorder
vote_recorder = VoteRecorder(event_bus)

# Later, get vote information
gaul_votes = vote_recorder.get_votes_for_topic("Expansion in Gaul")
support_count = vote_recorder.get_vote_count("Expansion in Gaul", "support")
```

### Event Filtering

You can create handlers that filter events based on properties:

```python
class FilteredEventHandler:
    """Handles events that match specific criteria."""
    
    def __init__(self, event_bus, event_type, filter_func):
        self.event_bus = event_bus
        self.event_type = event_type
        self.filter_func = filter_func
        self.matched_events = []
        
        # Subscribe to events
        self.event_bus.subscribe(event_type, self.handle_event)
        
    async def handle_event(self, event):
        """Handle an event if it matches the filter."""
        if self.filter_func(event):
            self.matched_events.append(event)
            print(f"Matched event: {event.event_id}")
            
    def get_matched_events(self):
        """Get all events that matched the filter."""
        return self.matched_events

# Create a filtered handler for speeches by Optimates
optimates_filter = lambda event: event.speaker.get("faction") == "Optimates"
optimates_handler = FilteredEventHandler(event_bus, "speech", optimates_filter)

# Create a filtered handler for supportive speeches
support_filter = lambda event: event.stance == "support"
support_handler = FilteredEventHandler(event_bus, "speech", support_filter)
```

### Priority-Based Handling

You can create handlers with different priorities:

```python
class PriorityHandler:
    """Event handler with a specific priority."""
    
    def __init__(self, priority, name):
        self.priority = priority
        self.name = name
        
    async def handle_event(self, event):
        """Handle an event with this priority."""
        print(f"Handler {self.name} (priority {self.priority}) processing event {event.event_id}")

# Create handlers with different priorities
high_priority = PriorityHandler(10, "High")
medium_priority = PriorityHandler(5, "Medium")
low_priority = PriorityHandler(1, "Low")

# Subscribe handlers to the same event type
event_bus.subscribe("priority_test", high_priority.handle_event)
event_bus.subscribe("priority_test", medium_priority.handle_event)
event_bus.subscribe("priority_test", low_priority.handle_event)

# Create an event with a priority
priority_event = Event(
    event_type="priority_test",
    source="example",
    metadata={}
)
priority_event.priority = 5  # Set event priority

# Publish the event - handlers will be called in priority order
await event_bus.publish(priority_event)
```

## Integration Examples

### Integrating with Existing Code

You can integrate the event system with existing code:

```python
# Existing function to display a speech
def display_speech(senator, speech_data, topic):
    """Display a speech to the user."""
    print(f"\n{'-'*40}")
    print(f"{senator.get('name')} ({senator.get('faction')}) is speaking")
    print(f"{'-'*40}")
    print(f"Topic: {topic}")
    print(f"\n{speech_data['speech']}")
    print(f"\nStance: {speech_data['stance']}")

# Modify to work with the event system
async def display_speech_event(event):
    """Display a speech event to the user."""
    print(f"\n{'-'*40}")
    print(f"{event.speaker.get('name')} ({event.speaker.get('faction')}) is speaking")
    print(f"{'-'*40}")
    print(f"Topic: {event.metadata.get('topic')}")
    print(f"\n[Latin]\n{event.latin_content}")
    print(f"\n[English]\n{event.english_content}")
    print(f"\nStance: {event.stance}")

# Subscribe to speech events
event_bus.subscribe("speech", display_speech_event)
```

### Integrating with Logging

You can integrate the event system with the logging system:

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

# Create a logger
logger = logging.getLogger("event_system")

# Create an event logger handler
class EventLogger:
    """Logs all events to the logging system."""
    
    def __init__(self, event_bus):
        self.event_bus = event_bus
        
        # Subscribe to all event types
        event_types = ["debate", "speech", "reaction", "interjection"]
        for event_type in event_types:
            self.event_bus.subscribe(event_type, self.handle_event)
            
    async def handle_event(self, event):
        """Log the event."""
        logger.info(f"Event: {event.event_type} - {event.event_id}")
        logger.debug(f"Event details: {event.to_dict()}")

# Create an event logger
event_logger = EventLogger(event_bus)
```

## Testing Examples

### Unit Testing Events

You can write unit tests for events:

```python
import pytest
from roman_senate.core.events import Event, SpeechEvent

def test_event_creation():
    """Test that events can be created with the correct properties."""
    event = Event(
        event_type="test",
        source="test_source",
        metadata={"key": "value"}
    )
    
    assert event.event_type == "test"
    assert event.source == "test_source"
    assert event.metadata["key"] == "value"
    assert event.event_id is not None
    assert event.timestamp is not None
    
def test_speech_event_creation():
    """Test that speech events can be created with the correct properties."""
    speaker = {"id": "senator1", "name": "Cato", "faction": "Optimates", "rank": 4}
    speech_event = SpeechEvent(
        speaker=speaker,
        topic="Test Topic",
        latin_content="Latin content",
        english_content="English content",
        stance="support",
        key_points=["Point 1", "Point 2"]
    )
    
    assert speech_event.event_type == "speech"
    assert speech_event.speaker == speaker
    assert speech_event.latin_content == "Latin content"
    assert speech_event.english_content == "English content"
    assert speech_event.stance == "support"
    assert len(speech_event.key_points) == 2
    assert speech_event.metadata["topic"] == "Test Topic"
```

### Testing Event Flow

You can test the flow of events through the system:

```python
import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock

@pytest.mark.asyncio
async def test_event_subscription_and_publication():
    """Test that events are properly distributed to subscribers."""
    # Create event bus
    event_bus = EventBus()
    
    # Create mock handlers
    handler1 = AsyncMock()
    handler2 = AsyncMock()
    
    # Subscribe handlers
    event_bus.subscribe("test_event", handler1)
    event_bus.subscribe("test_event", handler2)
    event_bus.subscribe("other_event", handler1)
    
    # Create and publish an event
    event = Event(event_type="test_event", source="test")
    await event_bus.publish(event)
    
    # Check that both handlers were called
    handler1.assert_called_once_with(event)
    handler2.assert_called_once_with(event)
    
    # Create and publish another event
    other_event = Event(event_type="other_event", source="test")
    await event_bus.publish(other_event)
    
    # Check that only handler1 was called again
    assert handler1.call_count == 2
    assert handler2.call_count == 1