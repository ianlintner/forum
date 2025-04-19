# Roman Senate Integration with Agentic Game Framework

This document explains how to use the integration components between the existing Roman Senate simulation and the new Agentic Game Framework.

## Overview

The integration module provides a bridge between the existing Roman Senate simulation and the new Agentic Game Framework. It allows you to:

1. Use the new framework's event system with Senate-specific events
2. Create Senate agents using the new framework's agent architecture
3. Run simulations that combine components from both systems
4. Gradually migrate from the old system to the new framework

## Integration Components

The integration is organized into several key components:

### 1. Framework Events (`src/roman_senate/integration/framework_events.py`)

This module implements Senate-specific events using the new framework's event system:

- `SenateEvent`: Base class for all Senate events
- `SpeechEvent`: Represents a senator's speech
- `DebateEvent`: Represents debate-related events (start, end, speaker change)
- `ReactionEvent`: Represents reactions to speeches
- `InterjectionEvent`: Represents interjections during speeches
- `RelationshipEvent`: Represents relationship changes between senators

### 2. Framework Agents (`src/roman_senate/integration/framework_agents.py`)

This module implements Senate-specific agents using the new framework's agent system:

- `SenatorAgent`: Represents a senator using the new framework's agent architecture

### 3. Utility Functions (`src/roman_senate/integration/utils.py`)

This module provides utility functions for working with both systems:

- `register_senate_domain()`: Registers the Senate domain with the framework
- `create_event_bus()`: Creates and configures an event bus
- `format_event_for_display()`: Formats events for display
- Helper functions for creating common event types

### 4. Integration Demo (`src/roman_senate/examples/framework_integration_demo/`)

This module provides a demonstration of how to use the integration components:

- `FrameworkIntegrationDemo`: A class that sets up and runs a simulation using the new framework

## Using the Integration

### Running a Simulation with the New Framework

You can run a simulation using the new framework via the CLI:

```bash
python -m src.roman_senate.cli simulate --use-framework
```

Optional parameters:
- `--senators`: Number of senators (default: 10)
- `--debate-rounds`: Number of debate rounds per topic (default: 3)
- `--topics`: Number of topics to debate (default: 3)
- `--year`: Year in Roman history, negative for BCE (default: -100)

### Programmatic Usage

To use the integration components in your own code:

```python
from src.roman_senate.integration.utils import register_senate_domain, create_event_bus
from src.roman_senate.integration.framework_agents import SenatorAgent
from src.roman_senate.integration.framework_events import SpeechEvent, DebateEvent

# Register the Senate domain
register_senate_domain()

# Create an event bus
event_bus = create_event_bus()

# Create senator agents
senator = SenatorAgent(
    name="Cicero",
    faction="Optimates",
    rank=4,
    llm_provider=your_llm_provider,
    event_bus=event_bus
)

# Create and publish events
debate_start = DebateEvent(
    debate_event_type=DebateEvent.DEBATE_START,
    topic="The expansion of Roman citizenship",
    source="consul"
)
event_bus.publish(debate_start)
```

## Migration Path

The integration module is designed to facilitate a gradual migration from the old system to the new framework. Here's a recommended approach:

1. **Start with the Integration Demo**: Run the integration demo to see how the new framework works with Senate-specific components.

2. **Migrate Event Handling First**: Begin by using the new framework's event system while keeping other components unchanged.

3. **Migrate Agents Incrementally**: Replace old agents with new framework agents one at a time, ensuring compatibility.

4. **Migrate Memory and Relationships**: Once events and agents are migrated, move on to memory and relationship systems.

5. **Test Thoroughly**: Test each migration step to ensure compatibility and correct behavior.

## Best Practices for Maintaining Compatibility

1. **Use the Integration Utils**: The utility functions in `src/roman_senate/integration/utils.py` help maintain compatibility between the systems.

2. **Keep Event Types Consistent**: Ensure event types are consistent between the old and new systems.

3. **Maintain Clear Boundaries**: Keep clear boundaries between components using the old system and those using the new framework.

4. **Document Integration Points**: Document where and how the systems interact to make future maintenance easier.

5. **Write Integration Tests**: Create tests that verify the correct interaction between the old and new systems.

## Future Directions

Once the migration is complete, the integration module can be simplified or removed, and the codebase can fully adopt the new framework's architecture. This will provide a more modular, extensible, and maintainable system for future development.