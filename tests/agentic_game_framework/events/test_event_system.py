"""
Unit tests for the event system components.

This module contains tests for the BaseEvent and EventBus classes.
"""

import pytest
from datetime import datetime
from typing import List

from src.agentic_game_framework.events.base import BaseEvent, EventHandler
from src.agentic_game_framework.events.event_bus import EventBus


class MockEvent(BaseEvent):
    """Simple event implementation for testing."""
    
    def __init__(self, event_type="test_event", source=None, target=None, data=None, timestamp=None, event_id=None):
        super().__init__(event_type, source, target, data, timestamp, event_id)


class MockEventHandler(EventHandler):
    """Simple event handler implementation for testing."""
    
    def __init__(self):
        self.handled_events: List[BaseEvent] = []
    
    def handle_event(self, event: BaseEvent) -> None:
        self.handled_events.append(event)
        
    def clear(self) -> None:
        self.handled_events.clear()


# --- BaseEvent Tests ---

def test_event_initialization():
    """Test that a BaseEvent can be properly initialized."""
    event = MockEvent(
        event_type="test_type",
        source="test_source",
        target="test_target",
        data={"key": "value"}
    )
    
    assert event.event_type == "test_type"
    assert event.source == "test_source"
    assert event.target == "test_target"
    assert event.data == {"key": "value"}
    assert isinstance(event.timestamp, datetime)
    assert event.get_id() is not None


def test_event_to_dict():
    """Test that a BaseEvent can be converted to a dictionary."""
    event = MockEvent(
        event_type="test_type",
        source="test_source",
        target="test_target",
        data={"key": "value"}
    )
    
    event_dict = event.to_dict()
    
    assert event_dict["event_type"] == "test_type"
    assert event_dict["source"] == "test_source"
    assert event_dict["target"] == "test_target"
    assert event_dict["data"] == {"key": "value"}
    assert "timestamp" in event_dict
    assert "id" in event_dict


def test_event_from_dict():
    """Test that a BaseEvent can be created from a dictionary."""
    event_dict = {
        "event_type": "test_type",
        "source": "test_source",
        "target": "test_target",
        "data": {"key": "value"},
        "timestamp": datetime.now().isoformat(),
        "id": "test_id"
    }
    
    event = MockEvent.from_dict(event_dict)
    
    assert event.event_type == "test_type"
    assert event.source == "test_source"
    assert event.target == "test_target"
    assert event.data == {"key": "value"}
    assert event.get_id() == "test_id"


def test_event_missing_event_type():
    """Test that creating an event from a dict without event_type raises an error."""
    event_dict = {
        "source": "test_source",
        "target": "test_target",
        "data": {"key": "value"}
    }
    
    with pytest.raises(ValueError):
        MockEvent.from_dict(event_dict)


# --- EventBus Tests ---

@pytest.fixture
def event_bus_setup():
    """Fixture providing an EventBus and handlers for testing."""
    event_bus = EventBus()
    handler1 = MockEventHandler()
    handler2 = MockEventHandler()
    handler3 = MockEventHandler()
    
    return {
        "event_bus": event_bus,
        "handler1": handler1,
        "handler2": handler2,
        "handler3": handler3
    }


def test_subscribe_and_publish(event_bus_setup):
    """Test that handlers receive events they subscribe to."""
    event_bus = event_bus_setup["event_bus"]
    handler1 = event_bus_setup["handler1"]
    handler2 = event_bus_setup["handler2"]
    
    # Subscribe handlers to different event types
    event_bus.subscribe("type1", handler1)
    event_bus.subscribe("type2", handler2)
    
    # Create and publish events
    event1 = MockEvent(event_type="type1", data={"value": 1})
    event2 = MockEvent(event_type="type2", data={"value": 2})
    event3 = MockEvent(event_type="type3", data={"value": 3})
    
    event_bus.publish(event1)
    event_bus.publish(event2)
    event_bus.publish(event3)
    
    # Check that handlers received the correct events
    assert len(handler1.handled_events) == 1
    assert handler1.handled_events[0].event_type == "type1"
    assert handler1.handled_events[0].data == {"value": 1}
    
    assert len(handler2.handled_events) == 1
    assert handler2.handled_events[0].event_type == "type2"
    assert handler2.handled_events[0].data == {"value": 2}


def test_subscribe_to_all(event_bus_setup):
    """Test that wildcard handlers receive all events."""
    event_bus = event_bus_setup["event_bus"]
    handler3 = event_bus_setup["handler3"]
    
    # Subscribe a handler to all events
    event_bus.subscribe_to_all(handler3)
    
    # Create and publish events of different types
    event1 = MockEvent(event_type="type1")
    event2 = MockEvent(event_type="type2")
    
    event_bus.publish(event1)
    event_bus.publish(event2)
    
    # Check that the handler received all events
    assert len(handler3.handled_events) == 2
    assert handler3.handled_events[0].event_type == "type1"
    assert handler3.handled_events[1].event_type == "type2"


def test_unsubscribe(event_bus_setup):
    """Test that handlers stop receiving events after unsubscribing."""
    event_bus = event_bus_setup["event_bus"]
    handler1 = event_bus_setup["handler1"]
    
    # Subscribe and then unsubscribe a handler
    event_bus.subscribe("type1", handler1)
    event_bus.publish(MockEvent(event_type="type1"))
    assert len(handler1.handled_events) == 1
    
    event_bus.unsubscribe("type1", handler1)
    event_bus.publish(MockEvent(event_type="type1"))
    assert len(handler1.handled_events) == 1  # Still 1, not 2


def test_unsubscribe_from_all(event_bus_setup):
    """Test that handlers stop receiving all events after unsubscribing from all."""
    event_bus = event_bus_setup["event_bus"]
    handler3 = event_bus_setup["handler3"]
    
    # Subscribe to all and then unsubscribe from all
    event_bus.subscribe_to_all(handler3)
    event_bus.publish(MockEvent(event_type="type1"))
    assert len(handler3.handled_events) == 1
    
    event_bus.unsubscribe_from_all(handler3)
    event_bus.publish(MockEvent(event_type="type1"))
    assert len(handler3.handled_events) == 1  # Still 1, not 2


def test_get_handlers(event_bus_setup):
    """Test that get_handlers returns the correct handlers for an event type."""
    event_bus = event_bus_setup["event_bus"]
    handler1 = event_bus_setup["handler1"]
    handler2 = event_bus_setup["handler2"]
    handler3 = event_bus_setup["handler3"]
    
    event_bus.subscribe("type1", handler1)
    event_bus.subscribe("type1", handler2)
    event_bus.subscribe_to_all(handler3)
    
    handlers = event_bus.get_handlers("type1")
    
    assert len(handlers) == 3
    assert handler1 in handlers
    assert handler2 in handlers
    assert handler3 in handlers


def test_handler_priority(event_bus_setup):
    """Test that handlers are called in priority order."""
    event_bus = event_bus_setup["event_bus"]
    
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
    event_bus.subscribe("test", handler_low, priority=0)
    event_bus.subscribe("test", handler_medium, priority=1)
    event_bus.subscribe("test", handler_high, priority=2)
    
    # Publish an event
    event_bus.publish(MockEvent(event_type="test"))
    
    # Check that handlers were called in priority order
    assert call_order == ["high", "medium", "low"]


def test_event_filter(event_bus_setup):
    """Test that event filters can block events."""
    event_bus = event_bus_setup["event_bus"]
    handler1 = event_bus_setup["handler1"]
    
    event_bus.subscribe("test", handler1)
    
    # Add a filter that blocks events with a specific source
    def filter_func(event):
        return event.source != "blocked_source"
        
    event_bus.add_filter(filter_func)
    
    # Publish events with different sources
    event_bus.publish(MockEvent(event_type="test", source="allowed_source"))
    event_bus.publish(MockEvent(event_type="test", source="blocked_source"))
    
    # Check that only the allowed event was processed
    assert len(handler1.handled_events) == 1
    assert handler1.handled_events[0].source == "allowed_source"
    
    # Remove the filter and check that events are no longer blocked
    event_bus.remove_filter(filter_func)
    event_bus.publish(MockEvent(event_type="test", source="blocked_source"))
    assert len(handler1.handled_events) == 2