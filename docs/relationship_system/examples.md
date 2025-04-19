# Senator Relationship System: Examples

**Author:** Documentation Team  
**Version:** 2.0.0
**Date:** April 19, 2025

## Table of Contents

- [Introduction](#introduction)
- [Basic Usage Examples](#basic-usage-examples)
  - [Creating Relationship-Aware Senators](#creating-relationship-aware-senators)
  - [Setting Initial Relationships](#setting-initial-relationships)
  - [Getting Relationship Values](#getting-relationship-values)
  - [Updating Relationships](#updating-relationships)
  - [Applying Time Decay](#applying-time-decay)
- [Event-Based Examples](#event-based-examples)
  - [Speech Events](#speech-events)
  - [Reaction Events](#reaction-events)
  - [Vote Events](#vote-events)
  - [Interjection Events](#interjection-events)
- [Decision-Making Examples](#decision-making-examples)
  - [Stance Decisions](#stance-decisions)
  - [Relationship-Influenced Voting](#relationship-influenced-voting)
- [Persistence Examples](#persistence-examples)
  - [Saving Relationship State](#saving-relationship-state)
  - [Loading Relationship State](#loading-relationship-state)
- [Visualization Examples](#visualization-examples)
- [Advanced Examples](#advanced-examples)
  - [Custom Relationship Types](#custom-relationship-types)
  - [Custom Event Handlers](#custom-event-handlers)
  - [Integration Testing](#integration-testing)

## Introduction

This document provides practical examples of using the Senator Relationship System in various scenarios. Each example includes code snippets and explanations to help you understand how to use the system effectively.

## Basic Usage Examples

### Creating Relationship-Aware Senators

```python
from roman_senate.core.events import EventBus
from roman_senate.agents.relationship_aware_senator_agent import RelationshipAwareSenatorAgent
from roman_senate.agents.memory_persistence_manager import MemoryPersistenceManager
from roman_senate.utils.llm.mock import MockLLMProvider

# Create shared components
event_bus = EventBus()
memory_manager = MemoryPersistenceManager(base_path="saves/example")
llm_provider = MockLLMProvider()

# Create relationship-aware senators
cicero = RelationshipAwareSenatorAgent(
    senator={
        "name": "Marcus Cicero",
        "id": "senator_cicero",
        "faction": "Optimates",
        "rank": 4
    },
    llm_provider=llm_provider,
    event_bus=event_bus,
    memory_manager=memory_manager
)

caesar = RelationshipAwareSenatorAgent(
    senator={
        "name": "Julius Caesar",
        "id": "senator_caesar",
        "faction": "Populares",
        "rank": 5
    },
    llm_provider=llm_provider,
    event_bus=event_bus,
    memory_manager=memory_manager
)
```

### Setting Initial Relationships

```python
# Set up Cicero's relationships with Caesar
cicero.relationship_manager.update_relationship(
    "senator_caesar", "political", -0.4, "Political rivalry but respect for abilities"
)
cicero.relationship_manager.update_relationship(
    "senator_caesar", "personal", 0.2, "Personal respect despite political differences"
)

# Set up Caesar's relationships with Cicero
caesar.relationship_manager.update_relationship(
    "senator_cicero", "political", -0.4, "Political opposition but recognizes influence"
)
caesar.relationship_manager.update_relationship(
    "senator_cicero", "personal", 0.1, "Grudging personal respect for intellect"
)
```

### Getting Relationship Values

```python
# Get a specific relationship type
political_rel = cicero.relationship_manager.get_relationship("senator_caesar", "political")
print(f"Cicero's political relationship with Caesar: {political_rel:.2f}")

# Get all relationship types
all_rels = cicero.relationship_manager.get_relationship("senator_caesar")
print("All relationships:")
for rel_type, value in all_rels.items():
    print(f"  {rel_type}: {value:.2f}")

# Get overall relationship
overall_rel = cicero.relationship_manager.get_overall_relationship("senator_caesar")
print(f"Overall relationship: {overall_rel:.2f}")
```

### Updating Relationships

```python
# Update a relationship with a positive change
cicero.relationship_manager.update_relationship(
    "senator_caesar",
    "political",
    0.1,  # Positive change
    "Supported my proposal on military funding"
)

# Update a relationship with a negative change
cicero.relationship_manager.update_relationship(
    "senator_caesar",
    "personal",
    -0.2,  # Negative change
    "Made disparaging remarks about my oratory"
)
```

### Applying Time Decay

```python
# Apply time decay for 30 days
cicero.relationship_manager.apply_time_decay(30)

# Apply time decay through senator agent
cicero.apply_time_effects(30)  # This also applies memory decay

# Check relationship after decay
political_rel_after = cicero.relationship_manager.get_relationship("senator_caesar", "political")
print(f"Political relationship after 30 days: {political_rel_after:.2f}")
```

## Event-Based Examples

### Speech Events

```python
from roman_senate.core.events import SpeechEvent

# Create and publish a speech event
speech_event = SpeechEvent(
    speaker=caesar.senator,
    topic="Land Reform Act",
    latin_content="Latin speech by Caesar...",
    english_content="I, Caesar, speak on Land Reform Act with a support stance.",
    stance="support",
    key_points=["Point from Caesar on Land Reform"]
)

# Publish the event
await event_bus.publish(speech_event)

# The relationship manager will automatically handle the event
# and update relationships based on stance alignment
```

### Reaction Events

```python
from roman_senate.core.events import ReactionEvent

# Create and publish a reaction event
reaction_event = ReactionEvent(
    reactor=cicero.senator,
    target_event_id=speech_event.event_id,
    reaction_type="disagreement",
    content="Reaction from Cicero: disagreement"
)

# Publish the event
await event_bus.publish(reaction_event)
```

### Vote Events

```python
from roman_senate.core.events import VoteEvent

# Create and publish a vote event
vote_event = VoteEvent(
    proposal="Land Reform Act",
    votes={
        "senator_cicero": "oppose",
        "senator_caesar": "support",
        "senator_cato": "oppose"
    },
    metadata={"proposal": "Land Reform Act"}
)

# Publish the event
await event_bus.publish(vote_event)
```

### Interjection Events

```python
from roman_senate.core.events import InterjectionEvent, InterjectionType

# Create and publish an interjection event
interjection_event = InterjectionEvent(
    interjector=cicero.senator,
    target_speaker=caesar.senator,
    interjection_type=InterjectionType.CHALLENGE,
    latin_content="Latin interjection by Cicero...",
    english_content="I challenge your assertion about land distribution!"
)

# Publish the event
await event_bus.publish(interjection_event)
```

## Decision-Making Examples

### Stance Decisions

```python
# Get base stance without relationship influence
base_stance, base_reasoning = await cicero.get_base_stance("Land Reform Act", {})

# Get stance with relationship influence
final_stance, reasoning = await cicero.decide_stance("Land Reform Act", {})

print(f"Base stance: {base_stance}")
print(f"Final stance: {final_stance}")
print(f"Reasoning: {reasoning}")

# If the stance changed due to relationships, the reasoning will explain why
if base_stance != final_stance:
    print("Stance changed due to relationship influence!")
```

When testing relationship-influenced decisions, you can use the `testing=True` parameter to ensure deterministic behavior:

```python
# For testing purposes, disable random abstention
async def run_vote_test(environment, topic):
    """Run a vote with deterministic behavior for testing."""
    # Get stances from all senators
    votes = {}
    for senator in environment.senators:
        stance, reasoning = await senator.decide_stance(topic, {})
        votes[senator.senator["id"]] = stance  # No random abstention
    
    # Create and publish vote event
    vote_event = VoteEvent(
        proposal=topic,
        votes=votes,
        metadata={"proposal": topic}
    )
    
    await environment.event_bus.publish(vote_event)
    return votes
```

### Relationship-Influenced Voting

```python
class RelationshipAwareVotingSystem:
    """Voting system that considers relationships."""
    
    def __init__(self, event_bus):
        self.event_bus = event_bus
    
    async def conduct_vote(self, proposal, senators):
        """Conduct a vote with relationship influences."""
        votes = {}
        changed_votes = []
        
        # Collect votes from each senator
        for senator in senators:
            # Get base stance without relationships
            base_stance, _ = await senator.get_base_stance(proposal, {})
            
            # Get final stance with relationships
            final_stance, reasoning = await senator.decide_stance(proposal, {})
            
            # Record vote
            votes[senator.senator["id"]] = final_stance
            
            # Track changed votes
            if base_stance != final_stance:
                changed_votes.append({
                    "senator": senator.name,
                    "from": base_stance,
                    "to": final_stance,
                    "reasoning": reasoning
                })
        
        # Create and publish vote event
        vote_event = VoteEvent(
            proposal=proposal,
            votes=votes,
            metadata={"proposal": proposal}
        )
        
        await self.event_bus.publish(vote_event)
        
        # Return results
        return {
            "votes": votes,
            "changed_votes": changed_votes,
            "outcome": self._determine_outcome(votes)
        }
```

## Persistence Examples

### Saving Relationship State

```python
# Save memory state for a senator
memory_manager.save_memory(cicero.senator["id"], cicero.memory)

# Save memory state for all senators
def save_all_senators(senators, memory_manager):
    """Save memory state for all senators."""
    for senator in senators:
        memory_manager.save_memory(senator.senator["id"], senator.memory)
    
    print(f"Saved memory state for {len(senators)} senators")
```

### Loading Relationship State

```python
# Load memory state for a senator
memory_manager.load_memory(cicero.senator["id"], cicero.memory)

# Reload relationships from memory
cicero.relationship_manager._load_relationships_from_memory()

# Load memory state for all senators
def load_all_senators(senators, memory_manager):
    """Load memory state for all senators."""
    for senator in senators:
        memory_manager.load_memory(senator.senator["id"], senator.memory)
        senator.relationship_manager._load_relationships_from_memory()
    
    print(f"Loaded memory state for {len(senators)} senators")
```

## Visualization Examples

The relationship system provides several visualization methods:

1. **Relationship Network Graph**: Visualizes relationships as a network graph
2. **Relationship Matrix**: Creates a heatmap of relationships between senators
3. **Relationship Timeline**: Shows how a relationship has changed over time

Example code for these visualizations can be found in the [Developer Guide](developer_guide.md#visualizing-relationships).

## Advanced Examples

### Custom Relationship Types

```python
# Extend RelationshipManager with a custom relationship type
class EnhancedRelationshipManager(RelationshipManager):
    """Enhanced relationship manager with additional relationship types."""
    
    # Define extended relationship types
    RELATIONSHIP_TYPES = [
        "political",  # Political alliance/opposition
        "personal",   # Personal friendship/animosity
        "mentor",     # Mentor/mentee relationship
        "rival",      # Direct rivalry/competition
        "family",     # Family connection
        "economic",   # Economic relationship (new)
        "military"    # Military alliance/rivalry (new)
    ]
    
    # Default decay rates per relationship type (monthly)
    DECAY_RATES = {
        "political": 0.08,
        "personal": 0.04,
        "mentor": 0.02,
        "rival": 0.05,
        "family": 0.01,
        "economic": 0.06,  # New decay rate
        "military": 0.03   # New decay rate
    }
```

### Custom Event Handlers

```python
# Add a custom event handler for economic events
class EconomicEvent(Event):
    """Event for economic interactions between senators."""
    
    TYPE = "economic_event"
    
    def __init__(
        self,
        actor_id: str,
        target_id: str,
        transaction_type: str,  # "loan", "investment", "gift", etc.
        amount: float,
        success: bool
    ):
        super().__init__()
        self.actor_id = actor_id
        self.target_id = target_id
        self.transaction_type = transaction_type
        self.amount = amount
        self.success = success
        self.metadata = {
            "actor_id": actor_id,
            "target_id": target_id,
            "transaction_type": transaction_type,
            "amount": amount,
            "success": success
        }

# Add handler to RelationshipManager
def _handle_economic_event(self, event: EconomicEvent):
    """Process economic events for relationship impacts."""
    # Skip own events
    if event.actor_id == self.senator_id:
        return
        
    # Skip events where this senator is not the target
    if event.target_id != self.senator_id:
        return
        
    # Update economic relationship based on transaction type and success
    if event.transaction_type == "loan":
        if event.success:
            # Successful loan improves economic relationship
            self.update_relationship(
                event.actor_id,
                "economic",
                0.1,
                f"Provided a loan of {event.amount} denarii",
                event.event_id
            )
        else:
            # Failed loan harms economic relationship
            self.update_relationship(
                event.actor_id,
                "economic",
                -0.2,
                f"Failed to provide promised loan of {event.amount} denarii",
                event.event_id
            )
            
### Integration Testing

When testing the integration between the relationship system and other components, it's important to ensure deterministic behavior. Here's an example of how to test the integration between the relationship system and the voting system:

```python
import pytest
from roman_senate.core.events import EventBus
from roman_senate.agents.relationship_aware_senator_agent import RelationshipAwareSenatorAgent
from roman_senate.agents.memory_persistence_manager import MemoryPersistenceManager
from roman_senate.utils.llm.mock import MockLLMProvider
from roman_senate.core.senate_session import SenateEnvironment

@pytest.fixture
async def test_environment():
    """Create a test environment with relationship-aware senators."""
    # Create shared components
    event_bus = EventBus()
    memory_manager = MemoryPersistenceManager(base_path="saves/test")
    llm_provider = MockLLMProvider()
    
    # Create senators
    cicero = RelationshipAwareSenatorAgent(
        senator={"name": "Cicero", "id": "senator_cicero", "faction": "Optimates"},
        llm_provider=llm_provider,
        event_bus=event_bus,
        memory_manager=memory_manager
    )
    
    cato = RelationshipAwareSenatorAgent(
        senator={"name": "Cato", "id": "senator_cato", "faction": "Optimates"},
        llm_provider=llm_provider,
        event_bus=event_bus,
        memory_manager=memory_manager
    )
    
    caesar = RelationshipAwareSenatorAgent(
        senator={"name": "Caesar", "id": "senator_caesar", "faction": "Populares"},
        llm_provider=llm_provider,
        event_bus=event_bus,
        memory_manager=memory_manager
    )
    
    # Create environment
    environment = SenateEnvironment(
        senators=[cicero, cato, caesar],
        event_bus=event_bus,
        llm_provider=llm_provider
    )
    
    # Set up initial relationships
    cicero.relationship_manager.update_relationship(
        "senator_cato", "political", 0.8, "Strong political alliance"
    )
    
    return environment

@pytest.mark.asyncio
async def test_debate_and_vote_integration(test_environment):
    """Test integration between debate, relationships, and voting."""
    env = test_environment
    
    # Patch the run_vote method to disable random abstention
    original_run_vote = env.run_vote
    
    async def patched_run_vote(topic_text, context):
        # Call the original method but with testing=True to disable random abstention
        return await original_run_vote(topic_text, context, testing=True)
    
    # Apply the patch
    env.run_vote = patched_run_vote
    
    # Run a debate and vote
    topic = "Military Funding"
    await env.run_debate(topic, {})
    vote_results = await env.run_vote(topic, {})
    
    # Check that relationships influenced the vote
    assert vote_results["for"] == 2, "Should have 2 votes for (Cicero and Cato)"
    assert vote_results["against"] == 1, "Should have 1 vote against (Caesar)"
```

This example demonstrates how to:

1. Create a test environment with relationship-aware senators
2. Patch the `run_vote` method to disable random abstention for deterministic testing
3. Test that relationships properly influence voting behavior
4. Make assertions about the expected voting results

By using the `testing=True` parameter, you ensure that the random abstention feature doesn't interfere with your tests, making them reliable and deterministic.
