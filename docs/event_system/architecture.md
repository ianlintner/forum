# Roman Senate Event System: Architecture Documentation

**Author:** Documentation Team  
**Version:** 1.0.0  
**Date:** April 18, 2025

## Table of Contents

- [Introduction](#introduction)
- [System Context](#system-context)
- [Component Architecture](#component-architecture)
  - [Core Components](#core-components)
  - [Event Types](#event-types)
  - [Component Relationships](#component-relationships)
- [Event Flow](#event-flow)
  - [Basic Event Flow](#basic-event-flow)
  - [Debate Flow](#debate-flow)
  - [Interruption Handling](#interruption-handling)
- [Data Model](#data-model)
  - [Event Structure](#event-structure)
  - [Memory Model](#memory-model)
- [Design Decisions](#design-decisions)
  - [Publisher-Subscriber Pattern](#publisher-subscriber-pattern)
  - [Asynchronous Event Handling](#asynchronous-event-handling)
  - [Event Prioritization](#event-prioritization)
- [Integration Points](#integration-points)
  - [Integration with Existing Debate System](#integration-with-existing-debate-system)
  - [Integration with Agent Memory](#integration-with-agent-memory)
  - [Integration with Logging System](#integration-with-logging-system)
- [Performance Considerations](#performance-considerations)
  - [Event Distribution Efficiency](#event-distribution-efficiency)
  - [Memory Usage](#memory-usage)
  - [Scaling Considerations](#scaling-considerations)
- [Future Extensions](#future-extensions)
  - [Potential Enhancements](#potential-enhancements)
  - [Extension Points](#extension-points)

## Introduction

The Roman Senate Event System is designed to create a dynamic, interactive simulation where senators can react to speeches, interject, and change their positions based on the flow of debate. This document provides a detailed architectural overview of the system, explaining how the components work together to achieve this goal.

## System Context

The event system operates within the broader Roman Senate simulation:

```mermaid
C4Context
    title System Context Diagram

    Person(user, "User", "Person running the simulation")
    System(eventSystem, "Event System", "Manages events, reactions, and interjections")
    System_Ext(debateSystem, "Debate System", "Manages debate flow and speeches")
    System_Ext(senatorSystem, "Senator System", "Manages senator behavior and decision-making")
    System_Ext(loggingSystem, "Logging System", "Records simulation events and debug information")

    Rel(user, eventSystem, "Configures and observes")
    Rel(eventSystem, debateSystem, "Enhances with events")
    Rel(eventSystem, senatorSystem, "Provides event-driven behavior")
    Rel(eventSystem, loggingSystem, "Logs events and actions")
```

The event system integrates with:
- The debate system to enhance debates with dynamic interactions
- The senator system to provide event-driven behavior for senators
- The logging system to record events and debug information

## Component Architecture

### Core Components

The event system consists of several core components:

```mermaid
classDiagram
    class Event {
        +String eventId
        +String eventType
        +DateTime timestamp
        +Any source
        +Dict metadata
        +int priority
        +to_dict()
        +__str__()
    }
    
    class EventBus {
        +Dict subscribers
        +List published_events
        +int max_history
        +subscribe(event_type, handler)
        +unsubscribe(event_type, handler)
        +get_subscribers(event_type)
        +publish(event)
        +clear_history()
        +get_recent_events(count)
    }
    
    class EventHandler {
        <<interface>>
        +handle_event(event)
    }
    
    class DebateManager {
        +EventBus event_bus
        +Any game_state
        +String current_debate_topic
        +Dict current_speaker
        +List registered_speakers
        +bool debate_in_progress
        +start_debate(topic, senators)
        +end_debate()
        +register_speaker(senator)
        +next_speaker()
        +publish_speech(speaker, topic, latin_content, english_content, stance, key_points)
        +handle_interjection(event)
        +handle_reaction(event)
        +conduct_debate(topic, senators, environment)
    }
    
    class EventDrivenSenatorAgent {
        +Dict senator
        +EventMemory memory
        +EventBus event_bus
        +String current_stance
        +String active_debate_topic
        +Dict current_speaker
        +bool debate_in_progress
        +subscribe_to_events()
        +handle_speech_event(event)
        +handle_debate_event(event)
        +_should_react_to_speech(event)
        +_should_interject(event)
        +_generate_and_publish_reaction(event)
        +_generate_and_publish_interjection(event)
        +_consider_stance_change(event)
    }
    
    class EventMemory {
        +List event_history
        +List reaction_history
        +Dict stance_changes
        +Dict event_relationships
        +record_event(event)
        +record_reaction(event_id, reaction_type, content)
        +record_stance_change(topic, old_stance, new_stance, reason, event_id)
        +record_event_relationship_impact(senator_name, event_id, impact, reason)
        +get_events_by_type(event_type)
        +get_events_by_source(source_name)
        +get_reactions_to_event(event_id)
        +get_stance_changes_for_topic(topic)
        +get_relationship_impacts_by_senator(senator_name)
        +get_recent_events(count)
    }
    
    EventBus o-- "0..*" EventHandler : subscribers
    EventDrivenSenatorAgent ..|> EventHandler
    EventDrivenSenatorAgent --> EventBus
    EventDrivenSenatorAgent --> EventMemory
    DebateManager --> EventBus
```

1. **Event**: Base class for all events in the system
2. **EventBus**: Central component that manages event distribution
3. **EventHandler**: Interface for components that handle events
4. **DebateManager**: Coordinates debates using the event system
5. **EventDrivenSenatorAgent**: Senator agent with event-driven capabilities
6. **EventMemory**: Enhanced memory for storing event-related information

### Event Types

The system defines several event types:

```mermaid
classDiagram
    class Event {
        +String eventId
        +String eventType
        +DateTime timestamp
        +Any source
        +Dict metadata
        +int priority
    }
    
    class DebateEvent {
        +DebateEventType debate_event_type
    }
    
    class SpeechEvent {
        +Dict speaker
        +String latin_content
        +String english_content
        +String stance
        +List key_points
    }
    
    class ReactionEvent {
        +Dict reactor
        +String target_event_id
        +String target_event_type
        +String reaction_type
        +String content
    }
    
    class InterjectionEvent {
        +Dict interjector
        +Dict target_speaker
        +InterjectionType interjection_type
        +String latin_content
        +String english_content
        +String target_speech_id
        +bool causes_disruption
    }
    
    class DebateEventType {
        <<enumeration>>
        DEBATE_START
        DEBATE_END
        SPEAKER_CHANGE
        TOPIC_CHANGE
    }
    
    class InterjectionType {
        <<enumeration>>
        SUPPORT
        CHALLENGE
        PROCEDURAL
        EMOTIONAL
        INFORMATIONAL
    }
    
    Event <|-- DebateEvent
    Event <|-- SpeechEvent
    Event <|-- ReactionEvent
    Event <|-- InterjectionEvent
    DebateEvent --> DebateEventType
    InterjectionEvent --> InterjectionType
```

1. **DebateEvent**: Events related to the overall debate process
2. **SpeechEvent**: Represents a speech delivered by a senator
3. **ReactionEvent**: Represents a senator's reaction to a speech
4. **InterjectionEvent**: Represents an interruption during a speech

### Component Relationships

The following diagram shows how the components interact:

```mermaid
flowchart TD
    EB[EventBus] <--> DM[DebateManager]
    EB <--> SA1[Senator Agent 1]
    EB <--> SA2[Senator Agent 2]
    EB <--> SA3[Senator Agent 3]
    
    DM -- "1. Start Debate" --> EB
    SA1 -- "2. Generate Speech" --> DM
    DM -- "3. Publish Speech" --> EB
    EB -- "4. Notify of Speech" --> SA2
    EB -- "4. Notify of Speech" --> SA3
    SA2 -- "5. React to Speech" --> EB
    SA3 -- "6. Interject" --> EB
    EB -- "7. Notify of Interjection" --> DM
    DM -- "8. Handle Interjection" --> SA1
```

## Event Flow

### Basic Event Flow

The basic flow of events through the system:

```mermaid
sequenceDiagram
    participant Source as Event Source
    participant Bus as EventBus
    participant Handler as Event Handler
    
    Source->>Bus: publish(event)
    Bus->>Bus: Add to history
    Bus->>Bus: Get subscribers for event type
    Bus->>Bus: Sort handlers by priority
    
    loop For each handler
        Bus->>Handler: handle_event(event)
        Handler-->>Bus: (async processing)
    end
```

### Debate Flow

The flow of events during a debate:

```mermaid
sequenceDiagram
    participant DM as DebateManager
    participant EB as EventBus
    participant Speaker as Speaking Senator
    participant Listener as Listening Senator
    
    DM->>EB: publish(DebateEvent.DEBATE_START)
    EB->>Listener: handle_debate_event(event)
    Listener->>Listener: Update debate state
    
    DM->>EB: publish(DebateEvent.SPEAKER_CHANGE)
    EB->>Listener: handle_debate_event(event)
    Listener->>Listener: Update current speaker
    
    Speaker->>DM: Generate speech
    DM->>EB: publish(SpeechEvent)
    EB->>Listener: handle_speech_event(event)
    
    alt Should react
        Listener->>Listener: Generate reaction
        Listener->>EB: publish(ReactionEvent)
        EB->>DM: handle_reaction(event)
        DM->>DM: Log reaction
    end
    
    alt Should interject
        Listener->>Listener: Generate interjection
        Listener->>EB: publish(InterjectionEvent)
        EB->>DM: handle_interjection(event)
        
        alt Allow interruption
            DM->>DM: Display interjection
        end
    end
    
    alt Consider stance change
        Listener->>Listener: Evaluate speech
        Listener->>Listener: Update stance if persuaded
    end
    
    DM->>EB: publish(DebateEvent.DEBATE_END)
    EB->>Listener: handle_debate_event(event)
    Listener->>Listener: Reset debate state
```

### Interruption Handling

The process for handling interruptions:

```mermaid
flowchart TD
    A[Receive InterjectionEvent] --> B{Debate in progress?}
    B -- No --> C[Log warning and return]
    B -- Yes --> D{Current speaker set?}
    D -- No --> C
    D -- Yes --> E[Get ranks]
    E --> F{Interjector rank > Speaker rank?}
    F -- Yes --> G[Allow interruption]
    F -- No --> H{Equal ranks?}
    H -- No --> I[Deny interruption]
    H -- Yes --> J{Is procedural?}
    J -- Yes --> G
    J -- No --> I
    G --> K[Display interjection]
```

## Data Model

### Event Structure

All events share a common structure:

```
Event
├── event_id: UUID
├── event_type: String
├── timestamp: ISO datetime
├── source: Any (usually a senator)
├── metadata: Dictionary
└── priority: Integer
```

Specific event types add their own properties:

```
SpeechEvent
├── (inherits from Event)
├── speaker: Dictionary
├── latin_content: String
├── english_content: String
├── stance: String
└── key_points: List of strings

ReactionEvent
├── (inherits from Event)
├── reactor: Dictionary
├── target_event_id: String
├── target_event_type: String
├── reaction_type: String
└── content: String

InterjectionEvent
├── (inherits from Event)
├── interjector: Dictionary
├── target_speaker: Dictionary
├── interjection_type: InterjectionType
├── latin_content: String
├── english_content: String
├── target_speech_id: String (optional)
└── causes_disruption: Boolean
```

### Memory Model

The `EventMemory` class extends the base `AgentMemory` with event-specific storage:

```
EventMemory
├── (inherits from AgentMemory)
├── event_history: List of events
├── reaction_history: List of reactions
├── stance_changes: Dictionary mapping topics to lists of stance changes
└── event_relationships: Dictionary mapping senator names to lists of relationship impacts
```

## Design Decisions

### Publisher-Subscriber Pattern

The event system uses the publisher-subscriber pattern to decouple components:

**Benefits:**
- Components don't need direct references to each other
- New event types and handlers can be added without modifying existing code
- Events can be broadcast to multiple handlers

**Implementation:**
- The `EventBus` maintains a dictionary mapping event types to lists of handlers
- Handlers subscribe to specific event types
- When an event is published, all handlers for that event type are notified

### Asynchronous Event Handling

The event system uses asynchronous event handling:

**Benefits:**
- Non-blocking event processing
- Better performance for I/O-bound operations
- Support for concurrent event handling

**Implementation:**
- The `publish` method is async and awaits each handler
- Handlers are async methods that can perform I/O operations
- The system uses `asyncio` for asynchronous execution

### Event Prioritization

The event system prioritizes events based on senator rank:

**Benefits:**
- Higher-ranking senators have more influence
- Reflects the hierarchical nature of Roman society
- Creates more realistic debate dynamics

**Implementation:**
- Events have a priority property
- Interjection events set priority based on interjector's rank
- The `EventBus` sorts handlers by priority when applicable

## Integration Points

### Integration with Existing Debate System

The event system integrates with the existing debate system:

```mermaid
flowchart LR
    subgraph "Existing Debate System"
        DS[debate.py]
        DH[display_speech]
        AH[add_to_debate_history]
    end
    
    subgraph "Event System"
        DM[DebateManager]
        EB[EventBus]
        SE[SpeechEvent]
    end
    
    DS --> DM
    DM --> SE
    DM --> DH
    DM --> AH
    SE --> EB
```

**Integration points:**
- The `DebateManager` calls `display_speech` to show speeches
- The `DebateManager` calls `add_to_debate_history` to maintain compatibility
- The `conduct_debate` method replaces or enhances the existing debate flow

### Integration with Agent Memory

The event system integrates with the agent memory system:

```mermaid
flowchart LR
    subgraph "Agent Memory System"
        AM[AgentMemory]
        RS[relationship_scores]
        VH[voting_history]
    end
    
    subgraph "Event System"
        EM[EventMemory]
        EH[event_history]
        RH[reaction_history]
        SC[stance_changes]
        ER[event_relationships]
    end
    
    AM --> EM
    EM --> RS
    EM --> VH
    EM --> EH
    EM --> RH
    EM --> SC
    EM --> ER
```

**Integration points:**
- `EventMemory` extends `AgentMemory` with event-specific storage
- `record_stance_change` updates voting history for backward compatibility
- `record_event_relationship_impact` updates relationship scores for backward compatibility

### Integration with Logging System

The event system integrates with the logging system:

```mermaid
flowchart LR
    subgraph "Logging System"
        LS[logging_utils.py]
        SL[setup_logging]
        GL[get_logger]
    end
    
    subgraph "Event System"
        EB[EventBus]
        DM[DebateManager]
        SA[SenatorAgent]
    end
    
    LS --> SL
    LS --> GL
    SL --> EB
    GL --> EB
    SL --> DM
    GL --> DM
    SL --> SA
    GL --> SA
```

**Integration points:**
- All components use the logging system to record events and debug information
- The `EventBus` logs event publication and subscription
- The `DebateManager` logs debate events and interruptions
- Senator agents log reactions, interjections, and stance changes

## Performance Considerations

### Event Distribution Efficiency

The event system is designed for efficient event distribution:

- Events are distributed only to subscribers of the specific event type
- Handlers are sorted by priority to ensure important handlers run first
- The event history is limited to prevent memory issues

### Memory Usage

The event system manages memory usage:

- The `EventBus` limits the number of events stored in history
- Events use a common base class to reduce code duplication
- The `EventMemory` class efficiently stores event-related information

### Scaling Considerations

For larger simulations:

- The event system can handle many senators, but performance may degrade with very large numbers
- The probability of reactions and interjections can be adjusted to reduce event volume
- The event history size can be reduced to save memory

## Future Extensions

### Potential Enhancements

The event system could be enhanced with:

1. **Event Filtering**: Allow subscribers to filter events based on properties
2. **Event Persistence**: Store events in a database for later analysis
3. **Network Distribution**: Distribute events across network boundaries
4. **Event Visualization**: Create a visual representation of event flow
5. **Custom Event Types**: Support for user-defined event types

### Extension Points

The system provides several extension points:

1. **New Event Types**: Create new event types by extending the `Event` class
2. **Custom Handlers**: Create custom event handlers by implementing the `EventHandler` interface
3. **Enhanced DebateManager**: Extend the `DebateManager` class with custom behavior
4. **Custom Senator Agents**: Create custom senator agents with specialized event handling
5. **Memory Extensions**: Extend the `EventMemory` class with additional storage and retrieval methods