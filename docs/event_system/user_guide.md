# Roman Senate Event System: User Guide

**Author:** Documentation Team  
**Version:** 1.0.0  
**Date:** April 18, 2025

## Table of Contents

- [Introduction](#introduction)
- [Running the Simulation](#running-the-simulation)
  - [Basic Commands](#basic-commands)
  - [Command-Line Options](#command-line-options)
  - [Logging Options](#logging-options)
- [Understanding Debate Behavior](#understanding-debate-behavior)
  - [Speech Events](#speech-events)
  - [Reactions](#reactions)
  - [Interjections](#interjections)
  - [Position Changes](#position-changes)
- [Debugging and Monitoring](#debugging-and-monitoring)
  - [Log Files](#log-files)
  - [Event History](#event-history)
- [Extending the System](#extending-the-system)
  - [Creating New Event Types](#creating-new-event-types)
  - [Adding Custom Reactions](#adding-custom-reactions)
  - [Modifying Behavior Parameters](#modifying-behavior-parameters)
- [Troubleshooting](#troubleshooting)
  - [Common Issues](#common-issues)
  - [Performance Considerations](#performance-considerations)

## Introduction

The Roman Senate Event System enhances the simulation with dynamic interactions between senators during debates. This guide will help you run the simulation, understand the new event-driven behaviors, and customize the system to your needs.

## Running the Simulation

### Basic Commands

The Roman Senate simulation can be run using the command-line interface (CLI). Here are the basic commands:

```bash
# Run a standard simulation
python -m src.roman_senate.cli simulate

# Run a simulation with player participation
python -m src.roman_senate.cli play

# Run the event system demo (simplified example)
python -m src.roman_senate.examples.event_system_demo
```

### Command-Line Options

The CLI supports various options to customize the simulation:

```bash
# Run with a specific number of senators
python -m src.roman_senate.cli simulate --senators 15

# Run with a specific number of debate rounds
python -m src.roman_senate.cli simulate --debate-rounds 5

# Run with a specific number of topics
python -m src.roman_senate.cli simulate --topics 3

# Run in a specific year of Roman history
python -m src.roman_senate.cli simulate --year -50
```

### Logging Options

The event system includes comprehensive logging capabilities:

```bash
# Run with verbose logging (DEBUG level)
python -m src.roman_senate.cli simulate --verbose

# Run with a specific log level
python -m src.roman_senate.cli simulate --log-level INFO

# Run with a custom log file
python -m src.roman_senate.cli simulate --log-file my_simulation.log

# Combine options
python -m src.roman_senate.cli simulate --verbose --log-file detailed_debug.log
```

Log levels from least to most verbose:
- CRITICAL: Only critical errors
- ERROR: Errors that prevent normal operation
- WARNING: Unexpected situations that don't prevent operation
- INFO: General information about operation (default)
- DEBUG: Detailed information for debugging

## Understanding Debate Behavior

The event system creates dynamic debates where senators react to speeches, interject, and may change their positions based on persuasive arguments.

### Speech Events

When a senator gives a speech:

1. The speech is published as a `SpeechEvent` to the event bus
2. Other senators receive the event and process it
3. The speech is displayed to the user with the senator's name, faction, and stance
4. The speech is recorded in the debate history

Example output:
```
-----------------------------------------
Senator Cato (Optimates) is speaking
-----------------------------------------
[Latin]
Ceterum censeo Carthaginem esse delendam.

[English]
Furthermore, I think Carthage must be destroyed.

[Stance: support]
```

### Reactions

Senators may react to speeches based on:
- Their relationship with the speaker
- Faction alignment
- Interest in the topic
- Random chance (for variety)

Reactions are non-disruptive responses like:
- Nodding in agreement
- Frowning in disagreement
- Leaning forward with interest
- Looking bored or disinterested

Example output:
```
Senator Cicero nods in agreement with Cato
Senator Brutus looks unconvinced by Cato's arguments
```

### Interjections

Higher-ranking senators may interject during speeches. Interjections are more disruptive than reactions and may interrupt the flow of a speech.

Interjection types include:
- **Support**: Expressions of agreement ("Hear, hear!")
- **Challenge**: Questioning or challenging a point ("That claim is unfounded!")
- **Procedural**: Points of order or procedure ("Point of order!")
- **Emotional**: Emotional outbursts ("Outrageous!")
- **Informational**: Providing additional information ("If I may add a relevant fact...")

Example output:
```
INTERJECTION from Caesar: "I must challenge Cato's assertion!"
```

The debate manager determines whether to allow an interjection based on:
- The rank of the interrupting senator
- The rank of the speaking senator
- The type of interjection (procedural interruptions may be given higher priority)

### Position Changes

Senators may change their position on a topic based on persuasive speeches. This is influenced by:
- Relationship with the speaker
- Faction alignment
- Speaker's rank
- Random chance (for variety)

Position changes are more likely when:
- The speaker is from the same faction
- The senator has a positive relationship with the speaker
- The speaker has a high rank

Example output:
```
Senator Brutus changed stance on "Expansion in Gaul" from oppose to neutral due to Caesar's speech
```

## Debugging and Monitoring

### Log Files

Log files are stored in the `logs` directory with timestamped filenames:
```
logs/run.2025-04-18_20-15-30.log
```

Each log entry has the format:
```
YYYY-MM-DD HH:MM:SS | LEVEL | module:line_number | message
```

Example log entries:
```
2025-04-18 20:15:30 | INFO | root:100 | Roman Senate AI Game starting
2025-04-18 20:15:31 | DEBUG | event_bus:83 | Publishing event: Event(speech, source=Cato, id=123e4567-e89b-12d3-a456-426614174000)
2025-04-18 20:15:31 | INFO | event_driven_senator_agent:574 | Senator Brutus changed stance on Expansion in Gaul from oppose to neutral due to Caesar's speech
```

### Event History

The `EventBus` maintains a history of recent events that can be accessed programmatically:

```python
# Get the most recent events
recent_events = event_bus.get_recent_events(count=10)

# Print event summary
for event in recent_events:
    print(f"{event.event_type} from {event.source}: {event.timestamp}")
```

## Extending the System

### Creating New Event Types

You can create new event types by extending the base `Event` class:

```python
from roman_senate.core.events.base import Event

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
```

### Adding Custom Reactions

You can customize how senators react to events by modifying the reaction generation methods in `EventDrivenSenatorAgent`:

```python
# In a subclass of EventDrivenSenatorAgent
async def _generate_reaction_content(self, event, reaction_type):
    """Generate custom reaction content."""
    if reaction_type == "agreement":
        return f"Strongly agrees with {event.speaker.get('name')}'s position on {event.metadata.get('topic')}"
    # Add more custom reactions...
```

### Modifying Behavior Parameters

You can adjust the probabilities and thresholds that govern senator behavior:

```python
# Increase the base probability of reactions
agent._should_react_to_speech = lambda event: random.random() < 0.5  # 50% chance

# Increase the probability of interjections for high-ranking senators
if senator.get("rank") > 3:
    agent._should_interject = lambda event: random.random() < 0.4  # 40% chance
else:
    agent._should_interject = lambda event: random.random() < 0.1  # 10% chance
```

## Troubleshooting

### Common Issues

**Issue**: No reactions or interjections during debates
- **Solution**: Check that senator agents are properly subscribed to events
- **Solution**: Increase the probability thresholds for reactions and interjections
- **Solution**: Ensure the event bus is correctly publishing events

**Issue**: Too many interruptions making debates chaotic
- **Solution**: Decrease the probability thresholds for interjections
- **Solution**: Adjust the rank-based interruption rules in the debate manager

**Issue**: Senators not changing positions despite persuasive speeches
- **Solution**: Increase the base probability for stance changes
- **Solution**: Check that the stance change logic is correctly implemented
- **Solution**: Ensure relationships between senators are being properly tracked

### Performance Considerations

The event system adds some computational overhead due to:
- Event distribution to multiple subscribers
- Processing of events by each senator agent
- Generation of reactions and interjections

For large simulations (20+ senators), consider:
- Limiting the number of events stored in history
- Reducing the probability of reactions and interjections
- Using more efficient event filtering to reduce unnecessary processing