# Event-Driven Architecture for Roman Senate Simulation

This package implements an event-driven architecture for the Roman Senate simulation, enabling senators to observe, listen to, and react to events in their environment - particularly during debates.

## Overview

The event system is built on a publisher-subscriber (pub/sub) pattern, where:
- Events are published to an `EventBus`
- Subscribers (like senator agents) register to receive specific event types
- When events occur, all subscribers are notified and can react accordingly

This architecture enhances the realism of the simulation by allowing senators to dynamically react to speeches, change their positions based on persuasive arguments, and interrupt each other based on rank and relationships.

## Core Components

### Event Classes

- `Event`: Base class for all events with common properties (ID, type, timestamp, etc.)
- `DebateEvent`: Events related to the overall debate process (start, end, speaker changes)
- `SpeechEvent`: Represents a speech delivered by a senator
- `ReactionEvent`: Represents a senator's reaction to a speech
- `InterjectionEvent`: Represents an interruption during a speech

### EventBus

The `EventBus` is the central component that:
- Manages subscriptions to event types
- Distributes events to subscribers
- Prioritizes events based on senator rank (for interruptions)

### DebateManager

The `DebateManager` coordinates debates using the event system:
- Starts and ends debates
- Manages speaker transitions
- Publishes speech events
- Handles interruptions and reactions

## Usage Example

Here's a simple example of how to use the event system:

```python
# Create event bus
event_bus = EventBus()

# Create debate manager
debate_manager = DebateManager(event_bus, game_state)

# Create senator agents that subscribe to events
senator_agents = [
    EventDrivenSenatorAgent(senator, llm_provider, event_bus)
    for senator in senators
]

# Start a debate
await debate_manager.start_debate("Expansion in Gaul", senators)

# Publish a speech event
speech_event = await debate_manager.publish_speech(
    speaker=senator,
    topic="Expansion in Gaul",
    latin_content="Latin speech...",
    english_content="English speech...",
    stance="support"
)

# End the debate
await debate_manager.end_debate()
```

## Integration with Senator Agents

The `EventDrivenSenatorAgent` class extends the base `SenatorAgent` with event-driven capabilities:
- Subscribes to relevant event types
- Processes events and determines appropriate reactions
- Generates and publishes reactions and interjections
- Updates memory based on observed events
- Can change stance based on persuasive speeches

## Event Flow

1. A senator gives a speech, which is published as a `SpeechEvent`
2. Other senators receive the event and decide whether to react
3. Reactions are published as `ReactionEvent` objects
4. Some senators may decide to interject, publishing `InterjectionEvent` objects
5. The `DebateManager` handles interruptions based on senator rank
6. All events are recorded in senator memory for future reference

## Demo

See `src/roman_senate/examples/event_system_demo.py` for a complete demonstration of the event system in action.