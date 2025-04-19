"""
Tests for the base event system classes.

These tests verify that the Roman Senate event system properly extends and adapts
the agentic_game_framework event system.
"""

import unittest
from datetime import datetime
import uuid

from src.roman_senate.core.events.base import (
    BaseEvent, 
    RomanEvent, 
    EventHandler, 
    RomanEventHandler
)


class TestBaseEvent(unittest.TestCase):
    """Test the Roman Senate BaseEvent class."""
    
    def test_base_event_initialization(self):
        """Test that BaseEvent initializes with correct attributes."""
        event_type = "TEST_EVENT"
        source = "test_source"
        target = "test_target"
        data = {"key": "value"}
        timestamp = datetime.now()
        event_id = str(uuid.uuid4())
        
        event = BaseEvent(
            event_type=event_type,
            source=source,
            target=target,
            data=data,
            timestamp=timestamp,
            event_id=event_id
        )
        
        self.assertEqual(event.event_type, event_type)
        self.assertEqual(event.source, source)
        self.assertEqual(event.target, target)
        self.assertEqual(event.data, data)
        self.assertEqual(event.timestamp, timestamp)
        self.assertEqual(event.get_id(), event_id)
    
    def test_base_event_to_dict(self):
        """Test BaseEvent to_dict serialization."""
        event_type = "TEST_EVENT"
        source = "test_source"
        target = "test_target"
        data = {"key": "value"}
        timestamp = datetime.now()
        event_id = str(uuid.uuid4())
        
        event = BaseEvent(
            event_type=event_type,
            source=source,
            target=target,
            data=data,
            timestamp=timestamp,
            event_id=event_id
        )
        
        event_dict = event.to_dict()
        
        self.assertEqual(event_dict["id"], event_id)
        self.assertEqual(event_dict["event_type"], event_type)
        self.assertEqual(event_dict["timestamp"], timestamp.isoformat())
        self.assertEqual(event_dict["source"], source)
        self.assertEqual(event_dict["target"], target)
        self.assertEqual(event_dict["data"], data)
    
    def test_base_event_from_dict(self):
        """Test BaseEvent from_dict deserialization."""
        event_type = "TEST_EVENT"
        source = "test_source"
        target = "test_target"
        data = {"key": "value"}
        timestamp = datetime.now()
        event_id = str(uuid.uuid4())
        
        event_dict = {
            "id": event_id,
            "event_type": event_type,
            "timestamp": timestamp.isoformat(),
            "source": source,
            "target": target,
            "data": data
        }
        
        event = BaseEvent.from_dict(event_dict)
        
        self.assertEqual(event.event_type, event_type)
        self.assertEqual(event.source, source)
        self.assertEqual(event.target, target)
        self.assertEqual(event.data, data)
        self.assertEqual(event.get_id(), event_id)
        # Check timestamp with some flexibility for ISO parsing
        self.assertAlmostEqual(
            event.timestamp.timestamp(),
            timestamp.timestamp(),
            delta=1
        )


class TestRomanEvent(unittest.TestCase):
    """Test the RomanEvent class."""
    
    def test_roman_event_initialization(self):
        """Test that RomanEvent initializes with correct attributes."""
        event_type = "ROMAN_TEST_EVENT"
        source = "roman_source"
        target = "roman_target"
        data = {"roman_key": "roman_value"}
        timestamp = datetime.now()
        event_id = str(uuid.uuid4())
        
        event = RomanEvent(
            event_type=event_type,
            source=source,
            target=target,
            data=data,
            timestamp=timestamp,
            event_id=event_id
        )
        
        self.assertEqual(event.event_type, event_type)
        self.assertEqual(event.source, source)
        self.assertEqual(event.target, target)
        self.assertEqual(event.data, data)
        self.assertEqual(event.timestamp, timestamp)
        self.assertEqual(event.get_id(), event_id)
    
    def test_roman_event_is_framework_compatible(self):
        """Test that RomanEvent instances can be treated as framework BaseEvents."""
        from agentic_game_framework.events.base import BaseEvent as FrameworkBaseEvent
        
        event = RomanEvent(
            event_type="ROMAN_COMPAT_TEST",
            source="test_source"
        )
        
        # Check that RomanEvent is an instance of framework BaseEvent
        self.assertIsInstance(event, FrameworkBaseEvent)


class TestEventHandler(unittest.TestCase):
    """Test the event handler classes."""
    
    def test_roman_event_handler(self):
        """Test basic functionality of RomanEventHandler."""
        # Create a concrete implementation
        class TestHandler(RomanEventHandler):
            def __init__(self):
                self.handled_events = []
            
            def handle_event(self, event):
                self.handled_events.append(event)
        
        handler = TestHandler()
        event = RomanEvent(event_type="TEST_EVENT")
        
        # Handle the event and check it was recorded
        handler.handle_event(event)
        self.assertEqual(len(handler.handled_events), 1)
        self.assertEqual(handler.handled_events[0], event)


if __name__ == "__main__":
    unittest.main()