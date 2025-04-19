"""
Test module for EventMemory.

This module contains tests for the EventMemory class, which extends
AgentMemory with event-driven capabilities.
"""

import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock

from roman_senate.agents.event_memory import EventMemory
from roman_senate.core.events.base import Event
from roman_senate.core.events.debate_events import (
    SpeechEvent,
    ReactionEvent,
    InterjectionEvent,
    InterjectionType
)


class TestEventMemory:
    """Test suite for the EventMemory class."""
    
    @pytest.fixture
    def event_memory(self):
        """Create an EventMemory instance for testing."""
        return EventMemory()
    
    @pytest.fixture
    def sample_event(self):
        """Create a sample event for testing."""
        return Event(
            event_type="test_event",
            source={"name": "Test source"},
            metadata={"key": "value"}
        )
    
    @pytest.fixture
    def sample_speech_event(self):
        """Create a sample speech event for testing."""
        speaker = {
            "id": "speaker_id",
            "name": "Test speaker",
            "faction": "Test faction"
        }
        return SpeechEvent(
            speaker=speaker,
            topic="Test topic",
            latin_content="Latin content",
            english_content="English content",
            stance="support",
            key_points=["Point 1", "Point 2"]
        )
    
    def test_initialization(self, event_memory):
        """Test initialization of EventMemory."""
        # Basic AgentMemory properties
        assert hasattr(event_memory, "observations")
        assert hasattr(event_memory, "relationship_scores")
        assert hasattr(event_memory, "voting_history")
        assert hasattr(event_memory, "interactions")
        
        # EventMemory-specific properties
        assert event_memory.event_history == []
        assert event_memory.reaction_history == []
        assert event_memory.stance_changes == {}
        assert event_memory.event_relationships == {}
    
    def test_record_event(self, event_memory, sample_event):
        """Test recording an event in memory."""
        # Record the event
        event_memory.record_event(sample_event)
        
        # Check event was added to history
        assert len(event_memory.event_history) == 1
        recorded_event = event_memory.event_history[0]
        
        # Check recorded event data
        assert recorded_event["event_id"] == sample_event.event_id
        assert recorded_event["event_type"] == "test_event"
        assert recorded_event["timestamp"] == sample_event.timestamp
        assert recorded_event["source"] == "Test source"
        assert recorded_event["metadata"] == {"key": "value"}
        assert "recorded_at" in recorded_event
        
        # Check observation was also added (backward compatibility)
        assert len(event_memory.observations) == 1
        assert "Observed test_event event from Test source" in event_memory.observations[0]
    
    def test_record_reaction(self, event_memory, sample_event):
        """Test recording a reaction to an event."""
        # Record a reaction
        event_memory.record_reaction(
            event_id=sample_event.event_id,
            reaction_type="agreement",
            content="Nods in agreement"
        )
        
        # Check reaction was added to history
        assert len(event_memory.reaction_history) == 1
        reaction = event_memory.reaction_history[0]
        
        # Check reaction data
        assert reaction["event_id"] == sample_event.event_id
        assert reaction["reaction_type"] == "agreement"
        assert reaction["content"] == "Nods in agreement"
        assert "timestamp" in reaction
    
    def test_record_stance_change(self, event_memory, sample_event):
        """Test recording a stance change."""
        # Record a stance change
        event_memory.record_stance_change(
            topic="Test topic",
            old_stance="neutral",
            new_stance="support",
            reason="Persuasive argument",
            event_id=sample_event.event_id
        )
        
        # Check stance change was recorded
        assert "Test topic" in event_memory.stance_changes
        assert len(event_memory.stance_changes["Test topic"]) == 1
        stance_change = event_memory.stance_changes["Test topic"][0]
        
        # Check stance change data
        assert stance_change["old_stance"] == "neutral"
        assert stance_change["new_stance"] == "support"
        assert stance_change["reason"] == "Persuasive argument"
        assert stance_change["event_id"] == sample_event.event_id
        assert "timestamp" in stance_change
        
        # Check vote was also recorded (backward compatibility)
        assert "Test topic" in event_memory.voting_history
        assert event_memory.voting_history["Test topic"] == "support"
    
    def test_record_stance_change_without_event(self, event_memory):
        """Test recording a stance change without an associated event."""
        # Record a stance change without event ID
        event_memory.record_stance_change(
            topic="Test topic",
            old_stance="neutral",
            new_stance="support",
            reason="Personal consideration"
        )
        
        # Check stance change was recorded
        assert "Test topic" in event_memory.stance_changes
        stance_change = event_memory.stance_changes["Test topic"][0]
        
        # Check stance change data
        assert stance_change["old_stance"] == "neutral"
        assert stance_change["new_stance"] == "support"
        assert stance_change["reason"] == "Personal consideration"
        assert "event_id" not in stance_change
    
    def test_record_event_relationship_impact(self, event_memory, sample_event):
        """Test recording how an event impacted a relationship."""
        # Record relationship impact
        event_memory.record_event_relationship_impact(
            senator_name="Test senator",
            event_id=sample_event.event_id,
            impact=0.1,
            reason="Positive interaction"
        )
        
        # Check impact was recorded
        assert "Test senator" in event_memory.event_relationships
        assert len(event_memory.event_relationships["Test senator"]) == 1
        impact = event_memory.event_relationships["Test senator"][0]
        
        # Check impact data
        assert impact["event_id"] == sample_event.event_id
        assert impact["impact"] == 0.1
        assert impact["reason"] == "Positive interaction"
        assert "timestamp" in impact
        
        # Check relationship score was also updated (backward compatibility)
        assert "Test senator" in event_memory.relationship_scores
        assert event_memory.relationship_scores["Test senator"] == 0.1
    
    def test_record_multiple_impacts(self, event_memory, sample_event):
        """Test recording multiple relationship impacts for the same senator."""
        # Record multiple impacts
        event_memory.record_event_relationship_impact(
            senator_name="Test senator",
            event_id=sample_event.event_id,
            impact=0.1,
            reason="First interaction"
        )
        
        event_memory.record_event_relationship_impact(
            senator_name="Test senator",
            event_id="another_event_id",
            impact=-0.05,
            reason="Second interaction"
        )
        
        # Check both impacts were recorded
        assert len(event_memory.event_relationships["Test senator"]) == 2
        
        # Check relationship score is cumulative
        assert event_memory.relationship_scores["Test senator"] == 0.05  # 0.1 + (-0.05)
    
    def test_get_events_by_type(self, event_memory):
        """Test getting events by type."""
        # Add events of different types
        event1 = Event(event_type="type_a")
        event2 = Event(event_type="type_b")
        event3 = Event(event_type="type_a")
        
        event_memory.record_event(event1)
        event_memory.record_event(event2)
        event_memory.record_event(event3)
        
        # Get events by type
        type_a_events = event_memory.get_events_by_type("type_a")
        type_b_events = event_memory.get_events_by_type("type_b")
        type_c_events = event_memory.get_events_by_type("type_c")
        
        # Check results
        assert len(type_a_events) == 2
        assert type_a_events[0]["event_type"] == "type_a"
        assert type_a_events[1]["event_type"] == "type_a"
        
        assert len(type_b_events) == 1
        assert type_b_events[0]["event_type"] == "type_b"
        
        assert len(type_c_events) == 0
    
    def test_get_events_by_source(self, event_memory):
        """Test getting events by source."""
        # Add events from different sources
        event1 = Event(event_type="test", source={"name": "Source A"})
        event2 = Event(event_type="test", source={"name": "Source B"})
        event3 = Event(event_type="test", source={"name": "Source A"})
        
        event_memory.record_event(event1)
        event_memory.record_event(event2)
        event_memory.record_event(event3)
        
        # Get events by source
        source_a_events = event_memory.get_events_by_source("Source A")
        source_b_events = event_memory.get_events_by_source("Source B")
        source_c_events = event_memory.get_events_by_source("Source C")
        
        # Check results
        assert len(source_a_events) == 2
        assert source_a_events[0]["source"] == "Source A"
        assert source_a_events[1]["source"] == "Source A"
        
        assert len(source_b_events) == 1
        assert source_b_events[0]["source"] == "Source B"
        
        assert len(source_c_events) == 0
    
    def test_get_reactions_to_event(self, event_memory, sample_event):
        """Test getting reactions to a specific event."""
        # Record multiple reactions to different events
        event_memory.record_reaction(
            event_id=sample_event.event_id,
            reaction_type="agreement",
            content="First reaction"
        )
        
        event_memory.record_reaction(
            event_id="another_event_id",
            reaction_type="disagreement",
            content="Second reaction"
        )
        
        event_memory.record_reaction(
            event_id=sample_event.event_id,
            reaction_type="interest",
            content="Third reaction"
        )
        
        # Get reactions to specific event
        reactions = event_memory.get_reactions_to_event(sample_event.event_id)
        other_reactions = event_memory.get_reactions_to_event("another_event_id")
        nonexistent_reactions = event_memory.get_reactions_to_event("nonexistent_id")
        
        # Check results
        assert len(reactions) == 2
        assert reactions[0]["content"] == "First reaction"
        assert reactions[1]["content"] == "Third reaction"
        
        assert len(other_reactions) == 1
        assert other_reactions[0]["content"] == "Second reaction"
        
        assert len(nonexistent_reactions) == 0
    
    def test_get_stance_changes_for_topic(self, event_memory):
        """Test getting stance changes for a specific topic."""
        # Record stance changes for different topics
        event_memory.record_stance_change(
            topic="Topic A",
            old_stance="neutral",
            new_stance="support",
            reason="First change"
        )
        
        event_memory.record_stance_change(
            topic="Topic B",
            old_stance="oppose",
            new_stance="neutral",
            reason="Second change"
        )
        
        event_memory.record_stance_change(
            topic="Topic A",
            old_stance="support",
            new_stance="oppose",
            reason="Third change"
        )
        
        # Get stance changes for specific topic
        topic_a_changes = event_memory.get_stance_changes_for_topic("Topic A")
        topic_b_changes = event_memory.get_stance_changes_for_topic("Topic B")
        topic_c_changes = event_memory.get_stance_changes_for_topic("Topic C")
        
        # Check results
        assert len(topic_a_changes) == 2
        assert topic_a_changes[0]["reason"] == "First change"
        assert topic_a_changes[1]["reason"] == "Third change"
        
        assert len(topic_b_changes) == 1
        assert topic_b_changes[0]["reason"] == "Second change"
        
        assert len(topic_c_changes) == 0
    
    def test_get_relationship_impacts_by_senator(self, event_memory):
        """Test getting relationship impacts for a specific senator."""
        # Record impacts for different senators
        event_memory.record_event_relationship_impact(
            senator_name="Senator A",
            event_id="event1",
            impact=0.1,
            reason="First impact"
        )
        
        event_memory.record_event_relationship_impact(
            senator_name="Senator B",
            event_id="event2",
            impact=-0.1,
            reason="Second impact"
        )
        
        event_memory.record_event_relationship_impact(
            senator_name="Senator A",
            event_id="event3",
            impact=0.2,
            reason="Third impact"
        )
        
        # Get impacts for specific senator
        senator_a_impacts = event_memory.get_relationship_impacts_by_senator("Senator A")
        senator_b_impacts = event_memory.get_relationship_impacts_by_senator("Senator B")
        senator_c_impacts = event_memory.get_relationship_impacts_by_senator("Senator C")
        
        # Check results
        assert len(senator_a_impacts) == 2
        assert senator_a_impacts[0]["reason"] == "First impact"
        assert senator_a_impacts[1]["reason"] == "Third impact"
        
        assert len(senator_b_impacts) == 1
        assert senator_b_impacts[0]["reason"] == "Second impact"
        
        assert len(senator_c_impacts) == 0
    
    def test_get_recent_events(self, event_memory):
        """Test getting the most recent events."""
        # Create events with different timestamps
        events = []
        for i in range(10):
            event = Event(event_type=f"event_{i}")
            # Manually set timestamps to ensure known order
            event.timestamp = f"2023-01-01T00:00:{i:02d}"
            events.append(event)
            event_memory.record_event(event)
        
        # Get recent events with default count
        recent_events = event_memory.get_recent_events()
        
        # Check results - should be 5 most recent events in reverse order
        assert len(recent_events) == 5
        assert recent_events[0]["timestamp"] == "2023-01-01T00:00:09"
        assert recent_events[1]["timestamp"] == "2023-01-01T00:00:08"
        assert recent_events[4]["timestamp"] == "2023-01-01T00:00:05"
        
        # Get with custom count
        recent_events = event_memory.get_recent_events(count=3)
        assert len(recent_events) == 3
        assert recent_events[0]["timestamp"] == "2023-01-01T00:00:09"
        assert recent_events[2]["timestamp"] == "2023-01-01T00:00:07"
    
    def test_integration_with_agent_memory(self, event_memory, sample_speech_event):
        """Test integration with the base AgentMemory functionality."""
        # Record event and relationship impact
        event_memory.record_event(sample_speech_event)
        event_memory.record_event_relationship_impact(
            senator_name="Test speaker",
            event_id=sample_speech_event.event_id,
            impact=0.2,
            reason="Good speech"
        )
        
        # Check that relationship was updated
        assert event_memory.relationship_scores["Test speaker"] == 0.2
        
        # Add an interaction via base method
        event_memory.add_interaction(
            senator_name="Test speaker",
            interaction_type="conversation",
            details={"topic": "Private discussion"}
        )
        
        # Check that interaction was recorded
        assert len(event_memory.interactions["Test speaker"]) >= 1  # at least the one from add_interaction
        
        # Add observation via base method
        event_memory.add_observation("Test observation")
        
        # Check that observation was added
        assert "Test observation" in [o.strip() for o in event_memory.observations]
        
        # Record vote via base method
        event_memory.record_vote("Another topic", "oppose")
        
        # Check that vote was recorded
        assert event_memory.voting_history["Another topic"] == "oppose"