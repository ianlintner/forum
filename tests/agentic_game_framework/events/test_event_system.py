"""
Unit tests for the event system components.

This module contains tests for the BaseEvent and EventBus classes.
"""

import unittest
from datetime import datetime
from typing import List

from src.agentic_game_framework.events.base import BaseEvent, EventHandler
from src.agentic_game_framework.events.event_bus import EventBus


class TestEvent(BaseEvent):
    """Simple event implementation for testing."""
    
    def __init__(self, event_type="test_event", source=None, target=None, data=None):
        super().__init__(event_type, source, target, data)


class TestEventHandler(EventHandler):
    """Simple event handler implementation for testing."""
    
    def __init__(self):
        self.handled_events: List[BaseEvent] = []
    
    def handle_event(self, event: BaseEvent) -> None:
        self.handled_events.append(event)
        
    def clear(self) -> None:
        self.handled_events.clear()


class TestBaseEvent(unittest.TestCase):
    """Tests for the BaseEvent class."""
    
    def test_initialization(self):
        """Test that a BaseEvent can be properly initialized."""
        event = TestEvent(
            event_type="test_type",
            source="test_source",
            target="test_target",
            data={"key": "value"}
        )
        
        self.assertEqual(event.event_type, "test_type")
        self.assertEqual(event.source, "test_source")
        self.assertEqual(event.target, "test_target")
        self.assertEqual(event.data, {"key": "value"})
        self.assertIsInstance(event.timestamp, datetime)
        self.assertIsNotNone(event.get_id())
    
    def test_to_dict(self):
        """Test that a BaseEvent can be converted to a dictionary."""
        event = TestEvent(
            event_type="test_type",
            source="test_source",
            target="test_target",
            data={"key": "value"}
        )
        
        event_dict = event.to_dict()
        
        self.assertEqual(event_dict["event_type"], "test_type")
        self.assertEqual(event_dict["source"], "test_source")
        self.assertEqual(event_dict["target"], "test_target")
        self.assertEqual(event_dict["data"], {"key": "value"})
        self.assertIn("timestamp", event_dict)
        self.assertIn("id", event_dict)
    
    def test_from_dict(self):
        """Test that a BaseEvent can be created from a dictionary."""
        event_dict = {
            "event_type": "test_type",
            "source": "test_source",
            "target": "test_target",
            "data": {"key": "value"},
            "timestamp": datetime.now().isoformat(),
            "id": "test_id"
        }
        
        event = TestEvent.from_dict(event_dict)
        
        self.assertEqual(event.event_type, "test_type")
        self.assertEqual(event.source, "test_source")
        self.assertEqual(event.target, "test_target")
        self.assertEqual(event.data, {"key": "value"})
        self.assertEqual(event.get_id(), "test_id")
    
    def test_missing_event_type(self):
        """Test that creating an event from a dict without event_type raises an error."""
        event_dict = {
            "source": "test_source",
            "target": "test_target",
            "data": {"key": "value"}
        }
        
        with self.assertRaises(ValueError):
            TestEvent.from_dict(event_dict)


class TestEventBus(unittest.TestCase):
    """Tests for the EventBus class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.event_bus = EventBus()
        self.handler1 = TestEventHandler()
        self.handler2 = TestEventHandler()
        self.handler3 = TestEventHandler()
    
    def test_subscribe_and_publish(self):
        """Test that handlers receive events they subscribe to."""
        # Subscribe handlers to different event types
        self.event_bus.subscribe("type1", self.handler1)
        self.event_bus.subscribe("type2", self.handler2)
        
        # Create and publish events
        event1 = TestEvent(event_type="type1", data={"value": 1})
        event2 = TestEvent(event_type="type2", data={"value": 2})
        event3 = TestEvent(event_type="type3", data={"value": 3})
        
        self.event_bus.publish(event1)
        self.event_bus.publish(event2)
        self.event_bus.publish(event3)
        
        # Check that handlers received the correct events
        self.assertEqual(len(self.handler1.handled_events), 1)
        self.assertEqual(self.handler1.handled_events[0].event_type, "type1")
        self.assertEqual(self.handler1.handled_events[0].data, {"value": 1})
        
        self.assertEqual(len(self.handler2.handled_events), 1)
        self.assertEqual(self.handler2.handled_events[0].event_type, "type2")
        self.assertEqual(self.handler2.handled_events[0].data, {"value": 2})
    
    def test_subscribe_to_all(self):
        """Test that wildcard handlers receive all events."""
        # Subscribe a handler to all events
        self.event_bus.subscribe_to_all(self.handler3)
        
        # Create and publish events of different types
        event1 = TestEvent(event_type="type1")
        event2 = TestEvent(event_type="type2")
        
        self.event_bus.publish(event1)
        self.event_bus.publish(event2)
        
        # Check that the handler received all events
        self.assertEqual(len(self.handler3.handled_events), 2)
        self.assertEqual(self.handler3.handled_events[0].event_type, "type1")
        self.assertEqual(self.handler3.handled_events[1].event_type, "type2")
    
    def test_unsubscribe(self):
        """Test that handlers stop receiving events after unsubscribing."""
        # Subscribe and then unsubscribe a handler
        self.event_bus.subscribe("type1", self.handler1)
        self.event_bus.publish(TestEvent(event_type="type1"))
        self.assertEqual(len(self.handler1.handled_events), 1)
        
        self.event_bus.unsubscribe("type1", self.handler1)
        self.event_bus.publish(TestEvent(event_type="type1"))
        self.assertEqual(len(self.handler1.handled_events), 1)  # Still 1, not 2
    
    def test_unsubscribe_from_all(self):
        """Test that handlers stop receiving all events after unsubscribing from all."""
        # Subscribe to all and then unsubscribe from all
        self.event_bus.subscribe_to_all(self.handler3)
        self.event_bus.publish(TestEvent(event_type="type1"))
        self.assertEqual(len(self.handler3.handled_events), 1)
        
        self.event_bus.unsubscribe_from_all(self.handler3)
        self.event_bus.publish(TestEvent(event_type="type1"))
        self.assertEqual(len(self.handler3.handled_events), 1)  # Still 1, not 2
    
    def test_get_handlers(self):
        """Test that get_handlers returns the correct handlers for an event type."""
        self.event_bus.subscribe("type1", self.handler1)
        self.event_bus.subscribe("type1", self.handler2)
        self.event_bus.subscribe_to_all(self.handler3)
        
        handlers = self.event_bus.get_handlers("type1")
        
        self.assertEqual(len(handlers), 3)
        self.assertIn(self.handler1, handlers)
        self.assertIn(self.handler2, handlers)
        self.assertIn(self.handler3, handlers)
    
    def test_handler_priority(self):
        """Test that handlers are called in priority order."""
        # Track the order of handler calls
        call_order = []
        
        class OrderTrackingHandler(EventHandler):
            def __init__(self, name):
                self.name = name
            
            def handle_event(self, event):
                call_order.append(self.name)
        
        handler_high = OrderTrackingHandler("high")
        handler_medium = OrderTrackingHandler("medium")
        handler_low = OrderTrackingHandler("low")
        
        # Subscribe with different priorities
        self.event_bus.subscribe("test", handler_low, priority=0)
        self.event_bus.subscribe("test", handler_medium, priority=1)
        self.event_bus.subscribe("test", handler_high, priority=2)
        
        # Publish an event
        self.event_bus.publish(TestEvent(event_type="test"))
        
        # Check that handlers were called in priority order
        self.assertEqual(call_order, ["high", "medium", "low"])
    
    def test_event_filter(self):
        """Test that event filters can block events."""
        self.event_bus.subscribe("test", self.handler1)
        
        # Add a filter that blocks events with a specific source
        def filter_func(event):
            return event.source != "blocked_source"
            
        self.event_bus.add_filter(filter_func)
        
        # Publish events with different sources
        self.event_bus.publish(TestEvent(event_type="test", source="allowed_source"))
        self.event_bus.publish(TestEvent(event_type="test", source="blocked_source"))
        
        # Check that only the allowed event was processed
        self.assertEqual(len(self.handler1.handled_events), 1)
        self.assertEqual(self.handler1.handled_events[0].source, "allowed_source")
        
        # Remove the filter and check that events are no longer blocked
        self.event_bus.remove_filter(filter_func)
        self.event_bus.publish(TestEvent(event_type="test", source="blocked_source"))
        self.assertEqual(len(self.handler1.handled_events), 2)


if __name__ == "__main__":
    unittest.main()