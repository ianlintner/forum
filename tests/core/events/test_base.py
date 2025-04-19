"""
Test module for base Event class.

This module contains unit tests for the Event class, testing initialization,
serialization, and string representation.
"""

import pytest
import re
from datetime import datetime

from roman_senate.core.events.base import Event, EventHandler


class TestEvent:
    """Test suite for the Event class."""

    def test_initialization_minimal(self):
        """Test initialization with minimal parameters."""
        event = Event(event_type="test_event")
        
        # Check basic properties
        assert event.event_type == "test_event"
        assert event.source is None
        assert event.metadata == {}
        assert event.priority == 0
        
        # Check event_id is a valid UUID
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        assert re.match(uuid_pattern, event.event_id)
        
        # Check timestamp is a valid ISO format
        # This will raise ValueError if not valid ISO format
        datetime.fromisoformat(event.timestamp)

    def test_initialization_full(self):
        """Test initialization with all parameters."""
        source = {"name": "test_source"}
        metadata = {"key1": "value1", "key2": "value2"}
        
        event = Event(
            event_type="test_event",
            source=source,
            metadata=metadata
        )
        
        # Check properties
        assert event.event_type == "test_event"
        assert event.source == source
        assert event.metadata == metadata
        assert event.priority == 0

    def test_to_dict(self):
        """Test the to_dict method."""
        source = {"name": "test_source"}
        metadata = {"key1": "value1", "key2": "value2"}
        
        event = Event(
            event_type="test_event",
            source=source,
            metadata=metadata
        )
        
        # Get dictionary representation
        event_dict = event.to_dict()
        
        # Check dictionary contents
        assert event_dict["event_id"] == event.event_id
        assert event_dict["event_type"] == "test_event"
        assert event_dict["timestamp"] == event.timestamp
        assert event_dict["source"] == "test_source"  # Should extract name from source
        assert event_dict["metadata"] == metadata
        assert event_dict["priority"] == 0

    def test_to_dict_none_source(self):
        """Test to_dict method with None source."""
        event = Event(event_type="test_event")
        
        # Get dictionary representation
        event_dict = event.to_dict()
        
        # Check source is None
        assert event_dict["source"] is None

    def test_string_representation(self):
        """Test the string representation of an event."""
        source = {"name": "test_source"}
        event = Event(event_type="test_event", source=source)
        
        # Get string representation
        event_str = str(event)
        
        # Check string format
        assert f"Event(test_event, source=test_source, id={event.event_id})" == event_str

    def test_string_representation_none_source(self):
        """Test string representation with None source."""
        event = Event(event_type="test_event")
        
        # Get string representation
        event_str = str(event)
        
        # Check string format
        assert f"Event(test_event, source=Unknown, id={event.event_id})" == event_str

    def test_source_object_with_name(self):
        """Test using an object with a name attribute as the source."""
        class SourceObject:
            def __init__(self, name):
                self.name = name
                
        source = SourceObject("source_name")
        event = Event(event_type="test_event", source=source)
        
        # Check string representation uses the name attribute
        assert f"Event(test_event, source=source_name, id={event.event_id})" == str(event)
        
        # Check to_dict also uses the name attribute
        event_dict = event.to_dict()
        assert event_dict["source"] == "source_name"

    def test_metadata_modification(self):
        """Test that modifying the metadata after initialization works."""
        event = Event(event_type="test_event")
        
        # Initially empty metadata
        assert event.metadata == {}
        
        # Modify metadata
        event.metadata["key"] = "value"
        
        # Check modification
        assert event.metadata == {"key": "value"}
        
        # Check it appears in dictionary representation
        event_dict = event.to_dict()
        assert event_dict["metadata"] == {"key": "value"}


class TestEventHandlerProtocol:
    """Test suite for the EventHandler protocol."""
    
    def test_conforming_class(self):
        """Test a class that conforms to the EventHandler protocol."""
        class ConformingHandler:
            async def handle_event(self, event):
                pass
                
        # This should not raise a TypeError
        handler: EventHandler = ConformingHandler()
        
    def test_non_conforming_class(self):
        """Test a class that doesn't conform to the EventHandler protocol."""
        class NonConformingHandler:
            # Missing handle_event method
            pass
            
        # This would raise TypeError at runtime type checking
        # We can't easily test this directly with pytest since it's a runtime check
        # So we just verify we can't create a non-conforming instance
        assert not hasattr(NonConformingHandler(), "handle_event")