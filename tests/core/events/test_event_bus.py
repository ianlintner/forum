"""
Tests for the event bus system.

These tests verify that the EventBus correctly routes events to handlers
and manages subscriptions.
"""

import unittest
from unittest.mock import MagicMock

from src.roman_senate.core.events.base import BaseEvent, EventHandler
from src.roman_senate.core.events.event_bus import EventBus


class TestEventBus(unittest.TestCase):
    """Tests for the EventBus class."""
    
    def setUp(self):
        """Set up test environment before each test."""
        self.event_bus = EventBus()
        
        # Create mock handlers
        self.handler1 = MagicMock(spec=EventHandler)
        self.handler2 = MagicMock(spec=EventHandler)
        self.wildcard_handler = MagicMock(spec=EventHandler)
    
    def test_subscribe_and_publish(self):
        """Test subscribing to an event type and publishing events."""
        # Subscribe handlers
        self.event_bus.subscribe("TEST_EVENT", self.handler1)
        
        # Create and publish an event
        event = BaseEvent(event_type="TEST_EVENT", source="test_source")
        self.event_bus.publish(event)
        
        # Check that the handler was called
        self.handler1.handle_event.assert_called_once_with(event)
        
        # Handler for a different event type shouldn't be called
        self.event_bus.subscribe("OTHER_EVENT", self.handler2)
        self.handler2.handle_event.assert_not_called()
    
    def test_subscribe_to_all(self):
        """Test subscribing to all event types."""
        # Subscribe to all events
        self.event_bus.subscribe_to_all(self.wildcard_handler)
        
        # Create and publish events of different types
        event1 = BaseEvent(event_type="TYPE1", source="test")
        event2 = BaseEvent(event_type="TYPE2", source="test")
        
        self.event_bus.publish(event1)
        self.event_bus.publish(event2)
        
        # Check that the handler was called for both events
        self.assertEqual(self.wildcard_handler.handle_event.call_count, 2)
        self.wildcard_handler.handle_event.assert_any_call(event1)
        self.wildcard_handler.handle_event.assert_any_call(event2)
    
    def test_unsubscribe(self):
        """Test unsubscribing from event types."""
        # Subscribe and then unsubscribe
        self.event_bus.subscribe("TEST_EVENT", self.handler1)
        self.event_bus.unsubscribe("TEST_EVENT", self.handler1)
        
        # Publish an event
        event = BaseEvent(event_type="TEST_EVENT", source="test")
        self.event_bus.publish(event)
        
        # Handler shouldn't be called
        self.handler1.handle_event.assert_not_called()
    
    def test_unsubscribe_from_all(self):
        """Test unsubscribing from all event types."""
        # Subscribe to all and specific event types
        self.event_bus.subscribe_to_all(self.wildcard_handler)
        self.event_bus.subscribe("TEST_EVENT", self.wildcard_handler)
        
        # Unsubscribe from all
        self.event_bus.unsubscribe_from_all(self.wildcard_handler)
        
        # Publish events
        event1 = BaseEvent(event_type="TEST_EVENT", source="test")
        event2 = BaseEvent(event_type="OTHER_EVENT", source="test")
        self.event_bus.publish(event1)
        self.event_bus.publish(event2)
        
        # Handler shouldn't be called
        self.wildcard_handler.handle_event.assert_not_called()
    
    def test_multiple_handlers(self):
        """Test multiple handlers for the same event type."""
        # Subscribe multiple handlers to the same event type
        self.event_bus.subscribe("TEST_EVENT", self.handler1)
        self.event_bus.subscribe("TEST_EVENT", self.handler2)
        
        # Publish an event
        event = BaseEvent(event_type="TEST_EVENT", source="test")
        self.event_bus.publish(event)
        
        # Both handlers should be called
        self.handler1.handle_event.assert_called_once_with(event)
        self.handler2.handle_event.assert_called_once_with(event)
    
    def test_handler_priority(self):
        """Test that handlers are called in priority order."""
        # Create a list to track call order
        call_order = []
        
        # Create handlers that record their call order
        class OrderTrackingHandler(EventHandler):
            def __init__(self, name, order_list):
                self.name = name
                self.order_list = order_list
                
            def handle_event(self, event):
                self.order_list.append(self.name)
        
        handler_high = OrderTrackingHandler("high", call_order)
        handler_medium = OrderTrackingHandler("medium", call_order)
        handler_low = OrderTrackingHandler("low", call_order)
        
        # Subscribe with different priorities
        self.event_bus.subscribe("TEST_EVENT", handler_low, priority=0)
        self.event_bus.subscribe("TEST_EVENT", handler_medium, priority=10)
        self.event_bus.subscribe("TEST_EVENT", handler_high, priority=20)
        
        # Publish an event
        event = BaseEvent(event_type="TEST_EVENT", source="test")
        self.event_bus.publish(event)
        
        # Check that they were called in priority order
        self.assertEqual(call_order, ["high", "medium", "low"])
    
    def test_event_filters(self):
        """Test that event filters can block events."""
        # Subscribe a handler
        self.event_bus.subscribe("TEST_EVENT", self.handler1)
        
        # Add a filter that blocks events with a specific source
        self.event_bus.add_filter(lambda e: e.source != "blocked_source")
        
        # Publish events
        allowed_event = BaseEvent(event_type="TEST_EVENT", source="allowed_source")
        blocked_event = BaseEvent(event_type="TEST_EVENT", source="blocked_source")
        
        self.event_bus.publish(allowed_event)
        self.event_bus.publish(blocked_event)
        
        # Only the allowed event should reach the handler
        self.handler1.handle_event.assert_called_once_with(allowed_event)
    
    def test_get_handlers(self):
        """Test retrieving handlers for an event type."""
        # Subscribe handlers
        self.event_bus.subscribe("TEST_EVENT", self.handler1)
        self.event_bus.subscribe_to_all(self.wildcard_handler)
        
        # Get handlers
        handlers = self.event_bus.get_handlers("TEST_EVENT")
        
        # Should include both specific and wildcard handlers
        self.assertEqual(len(handlers), 2)
        self.assertIn(self.handler1, handlers)
        self.assertIn(self.wildcard_handler, handlers)
    
    def test_exception_handling(self):
        """Test that exceptions in handlers don't break event distribution."""
        # Create a handler that raises an exception
        failing_handler = MagicMock(spec=EventHandler)
        failing_handler.handle_event.side_effect = Exception("Test exception")
        
        # Create another handler that should still be called
        self.event_bus.subscribe("TEST_EVENT", failing_handler)
        self.event_bus.subscribe("TEST_EVENT", self.handler1)
        
        # Publish an event
        event = BaseEvent(event_type="TEST_EVENT", source="test")
        
        # Should not raise an exception
        self.event_bus.publish(event)
        
        # Second handler should still be called
        self.handler1.handle_event.assert_called_once_with(event)


if __name__ == "__main__":
    unittest.main()