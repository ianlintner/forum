"""
Tests for the Roman Senate EventMemory component.

This test suite verifies that the EventMemory class properly stores,
retrieves, and manages events in memory.
"""

import pytest
import datetime
from typing import Dict, Any

from roman_senate.core.events.base import BaseEvent as RomanEvent
from roman_senate.agents.event_memory import EventMemory, EventMemoryItem


class TestEventMemoryItem:
    """Tests for the EventMemoryItem class."""
    
    def test_init(self):
        """Test initialization of an EventMemoryItem."""
        # Create a test event
        event = RomanEvent(
            event_type="test.event",
            source="test_source",
            target="test_target",
            data={"key": "value"}
        )
        
        # Create a memory item
        memory_item = EventMemoryItem(event=event, importance=0.75)
        
        # Assert properties were set correctly
        assert memory_item.event_type == "test.event"
        assert memory_item.source == "test_source"
        assert memory_item.target == "test_target"
        assert memory_item.importance == 0.75
        assert memory_item.content["event_type"] == "test.event"
        assert memory_item.content["data"] == {"key": "value"}
        assert isinstance(memory_item.memory_id, str)
        
    def test_to_dict_from_dict(self):
        """Test conversion to and from dictionary representation."""
        # Create a test event
        event = RomanEvent(
            event_type="test.event",
            source="test_source",
            target="test_target",
            data={"key": "value"}
        )
        
        # Create a memory item
        original_item = EventMemoryItem(
            event=event, 
            importance=0.75,
            decay_rate=0.2,
            tags=["test", "important"],
            emotional_impact=0.5
        )
        
        # Convert to dictionary
        data = original_item.to_dict()
        
        # Assert dictionary contains expected values
        assert data["event_type"] == "test.event"
        assert data["source"] == "test_source"
        assert data["target"] == "test_target"
        assert data["importance"] == 0.75
        assert data["decay_rate"] == 0.2
        assert "test" in data["tags"]
        assert "important" in data["tags"]
        assert data["emotional_impact"] == 0.5
        
        # Reconstruct from dictionary
        reconstructed_item = EventMemoryItem.from_dict(data)
        
        # Assert reconstructed item matches original
        assert reconstructed_item.event_type == original_item.event_type
        assert reconstructed_item.source == original_item.source
        assert reconstructed_item.target == original_item.target
        assert reconstructed_item.importance == original_item.importance
        assert reconstructed_item.decay_rate == original_item.decay_rate
        assert set(reconstructed_item.tags) == set(original_item.tags)
        assert reconstructed_item.emotional_impact == original_item.emotional_impact
    
    def test_get_event(self):
        """Test retrieval of the original event from a memory item."""
        # Create a test event
        original_event = RomanEvent(
            event_type="test.event",
            source="test_source",
            target="test_target",
            data={"key": "value"}
        )
        
        # Create a memory item
        memory_item = EventMemoryItem(event=original_event)
        
        # Get event from memory item
        retrieved_event = memory_item.get_event()
        
        # Assert event properties match the original
        assert retrieved_event.event_type == original_event.event_type
        assert retrieved_event.source == original_event.source
        assert retrieved_event.target == original_event.target
        assert retrieved_event.data == {"key": "value"}


class TestEventMemory:
    """Tests for the EventMemory class."""
    
    @pytest.fixture
    def event_memory(self):
        """Create an EventMemory instance for tests."""
        return EventMemory(owner_id="test_owner")
    
    @pytest.fixture
    def test_event(self):
        """Create a test event for use in tests."""
        return RomanEvent(
            event_type="test.event",
            source="test_source",
            target="test_target",
            data={"key": "value"}
        )
    
    def test_init(self, event_memory):
        """Test initialization of an EventMemory."""
        assert event_memory.owner_id == "test_owner"
        assert len(event_memory._memory_items) == 0
        assert event_memory.index is not None
    
    def test_add_event(self, event_memory, test_event):
        """Test adding an event to memory."""
        # Add event to memory
        memory_id = event_memory.add_event(test_event)
        
        # Assert event was added
        assert len(event_memory._memory_items) == 1
        assert memory_id in event_memory._memory_items
        
        # Get memory item
        memory_item = event_memory._memory_items[memory_id]
        
        # Assert memory item properties match the event
        assert memory_item.event_type == test_event.event_type
        assert memory_item.source == test_event.source
        assert memory_item.target == test_event.target
    
    def test_get_memory(self, event_memory, test_event):
        """Test retrieving a memory item by ID."""
        # Add event to memory
        memory_id = event_memory.add_event(test_event)
        
        # Get memory item
        memory_item = event_memory.get_memory(memory_id)
        
        # Assert memory item exists and matches the event
        assert memory_item is not None
        assert memory_item.event_type == test_event.event_type
        
        # Test getting non-existent memory
        assert event_memory.get_memory("non_existent_id") is None
    
    def test_get_events_by_type(self, event_memory):
        """Test retrieving events by type."""
        # Add events of different types
        event1 = RomanEvent(event_type="type1", data={})
        event2 = RomanEvent(event_type="type2", data={})
        event3 = RomanEvent(event_type="type1", data={})
        
        event_memory.add_event(event1)
        event_memory.add_event(event2)
        event_memory.add_event(event3)
        
        # Get events by type
        type1_events = event_memory.get_events_by_type("type1")
        type2_events = event_memory.get_events_by_type("type2")
        
        # Assert correct events were retrieved
        assert len(type1_events) == 2
        assert all(e.event_type == "type1" for e in type1_events)
        
        assert len(type2_events) == 1
        assert type2_events[0].event_type == "type2"
    
    def test_get_recent_events(self, event_memory):
        """Test retrieving recent events."""
        # Create events with different timestamps
        event1 = RomanEvent(event_type="test.event", data={})
        event1.timestamp = datetime.datetime(2023, 1, 1)
        
        event2 = RomanEvent(event_type="test.event", data={})
        event2.timestamp = datetime.datetime(2023, 1, 2)
        
        event3 = RomanEvent(event_type="test.event", data={})
        event3.timestamp = datetime.datetime(2023, 1, 3)
        
        # Add events in random order
        event_memory.add_event(event2)
        event_memory.add_event(event1)
        event_memory.add_event(event3)
        
        # Get recent events
        recent_events = event_memory.get_recent_events(limit=2)
        
        # Assert newest events were retrieved
        assert len(recent_events) == 2
        assert recent_events[0].timestamp == datetime.datetime(2023, 1, 3)
        assert recent_events[1].timestamp == datetime.datetime(2023, 1, 2)
    
    def test_forget(self, event_memory, test_event):
        """Test removing a memory item."""
        # Add event to memory
        memory_id = event_memory.add_event(test_event)
        assert len(event_memory._memory_items) == 1
        
        # Remove memory item
        result = event_memory.forget(memory_id)
        
        # Assert memory item was removed
        assert result is True
        assert len(event_memory._memory_items) == 0
        
        # Test removing non-existent memory
        assert event_memory.forget("non_existent_id") is False
    
    def test_clear(self, event_memory):
        """Test clearing all memory items."""
        # Add multiple events
        event_memory.add_event(RomanEvent(event_type="test1", data={}))
        event_memory.add_event(RomanEvent(event_type="test2", data={}))
        event_memory.add_event(RomanEvent(event_type="test3", data={}))
        
        assert len(event_memory._memory_items) == 3
        
        # Clear memory
        event_memory.clear()
        
        # Assert memory is empty
        assert len(event_memory._memory_items) == 0
    
    def test_to_dict_from_dict(self, event_memory, test_event):
        """Test conversion to and from dictionary representation."""
        # Add event to memory
        event_memory.add_event(test_event)
        
        # Convert to dictionary
        data = event_memory.to_dict()
        
        # Assert dictionary contains expected values
        assert data["owner_id"] == "test_owner"
        assert "memory_items" in data
        assert len(data["memory_items"]) == 1
        
        # Reconstruct from dictionary
        reconstructed_memory = EventMemory.from_dict(data)
        
        # Assert reconstructed memory matches original
        assert reconstructed_memory.owner_id == event_memory.owner_id
        assert len(reconstructed_memory._memory_items) == len(event_memory._memory_items)
        
        # Get events from both memory instances
        original_events = event_memory.get_recent_events()
        reconstructed_events = reconstructed_memory.get_recent_events()
        
        # Assert events match
        assert len(original_events) == len(reconstructed_events)
        assert original_events[0].event_type == reconstructed_events[0].event_type
        assert original_events[0].source == reconstructed_events[0].source
        assert original_events[0].target == reconstructed_events[0].target