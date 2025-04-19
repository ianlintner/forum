# Roman Senate Event System: Quick Start Guide

**Author:** Documentation Team  
**Version:** 1.0.0  
**Date:** April 18, 2025

## Introduction

This Quick Start Guide will help you get up and running with the Roman Senate Event System quickly. It provides the essential information you need to understand, use, and extend the event-driven architecture.

## Table of Contents

- [Understanding the Basics](#understanding-the-basics)
- [Setting Up the Event System](#setting-up-the-event-system)
- [Creating Your First Event](#creating-your-first-event)
- [Subscribing to Events](#subscribing-to-events)
- [Running a Simple Debate](#running-a-simple-debate)
- [Common Tasks](#common-tasks)
- [Next Steps](#next-steps)

## Understanding the Basics

The Roman Senate Event System is built on a publisher-subscriber (pub/sub) pattern:

1. **Events** are objects that represent something that happened (e.g., a speech, a reaction)
2. The **EventBus** is the central component that distributes events to subscribers
3. **Subscribers** register to receive specific types of events
4. **Handlers** process events when they are received

This architecture allows for dynamic interactions between senators during debates, with reactions, interruptions, and position changes.

## Setting Up the Event System

Here's how to set up the basic event system:

```python
from roman_senate.core.events import EventBus, DebateManager

# Create the event bus
event_bus = EventBus()

# Create a game state (can be a simple dictionary for testing)
game_state = {"year": -50, "month": 3, "day": 15}

# Create the debate manager
debate_manager = DebateManager(event_bus, game_state)
```

## Creating Your First Event

Events are created by instantiating the appropriate event class:

```python
from roman_senate.core.events import SpeechEvent

# Create a speech event
speech_event = SpeechEvent(
    speaker={"id": "senator1", "name": "Cato", "faction": "Optimates", "rank": 4},
    topic="Expansion in Gaul",
    latin_content="Ceterum censeo Carthaginem esse delendam",
    english_content="Furthermore, I think Carthage must be destroyed",
    stance="support",
    key_points=["Carthage is a threat", "War is necessary"]
)

# Publish the event
await event_bus.publish(speech_event)
```

## Subscribing to Events

Components can subscribe to events they're interested in:

```python
# Define an event handler function
async def handle_speech_event(event):
    print(f"Received speech by {event.speaker.get('name')}")
    print(f"Content: {event.english_content}")

# Subscribe to speech events
event_bus.subscribe("speech", handle_speech_event)
```

## Running a Simple Debate

Here's how to run a simple debate with the event system:

```python
import asyncio
from roman_senate.core.events import EventBus, DebateManager
from roman_senate.agents.event_driven_senator_agent import EventDrivenSenatorAgent
from roman_senate.utils.llm.mock_provider import MockLLMProvider

async def run_simple_debate():
    # Create event bus and debate manager
    event_bus = EventBus()
    game_state = {"year": -50, "month": 3, "day": 15}
    debate_manager = DebateManager(event_bus, game_state)
    
    # Create mock LLM provider
    llm_provider = MockLLMProvider()
    
    # Define senators
    senators = [
        {"id": "senator1", "name": "Cato", "faction": "Optimates", "rank": 4},
        {"id": "senator2", "name": "Caesar", "faction": "Populares", "rank": 3},
        {"id": "senator3", "name": "Cicero", "faction": "Optimates", "rank": 2}
    ]
    
    # Create senator agents
    senator_agents = [
        EventDrivenSenatorAgent(senator, llm_provider, event_bus)
        for senator in senators
    ]
    
    # Define a topic
    topic = "Whether Rome should go to war with Carthage"
    
    # Run the debate
    await debate_manager.conduct_debate(topic, senators)

# Run the debate
asyncio.run(run_simple_debate())
```

## Common Tasks

### Creating a Custom Event Type

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
            "senator_name": senator.get("name", "Unknown")
        })
```

### Creating a Custom Event Handler

```python
class VoteCounter:
    """Counts votes on topics."""
    
    def __init__(self, event_bus):
        self.event_bus = event_bus
        self.vote_counts = {}
        
        # Subscribe to vote events
        self.event_bus.subscribe("vote", self.handle_event)
        
    async def handle_event(self, event):
        """Handle a vote event."""
        topic = event.topic
        vote_value = event.vote_value
        
        if topic not in self.vote_counts:
            self.vote_counts[topic] = {"support": 0, "oppose": 0, "neutral": 0}
            
        self.vote_counts[topic][vote_value] += 1
```

### Logging Events

```python
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("event_system")

# Create an event logger
async def log_events(event):
    """Log events to the console."""
    logger.info(f"Event: {event.event_type} - {event.event_id}")
    
# Subscribe to all event types
event_types = ["debate", "speech", "reaction", "interjection"]
for event_type in event_types:
    event_bus.subscribe(event_type, log_events)
```

## Next Steps

Now that you understand the basics, here are some next steps:

1. **Explore the Examples**: Check out the [Examples](examples.md) document for more detailed code examples.
2. **Understand the Architecture**: Read the [Architecture](architecture.md) document to understand the system design.
3. **Learn Advanced Features**: The [Developer Guide](developer_guide.md) covers advanced topics like event prioritization and custom event types.
4. **Run the Demo**: Try running the event system demo:
   ```bash
   python -m src.roman_senate.examples.event_system_demo
   ```

For more detailed information, refer to the full documentation:
- [README](README.md): System overview
- [User Guide](user_guide.md): How to run the simulation
- [Developer Guide](developer_guide.md): How to extend the system
- [Architecture](architecture.md): Detailed system design
- [Examples](examples.md): Code examples and patterns