"""
Test module for EventBus class.

This module contains unit tests for the EventBus class, testing the publish/subscribe
mechanisms, event distribution, and event history functionality.
"""

import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock

from roman_senate.core.events.base import Event, EventHandler
from roman_senate.core.events.event_bus import EventBus


class TestEventBus:
    """Test suite for the EventBus class."""

    @pytest.fixture
    def event_bus(self):
        """Create a fresh EventBus for each test."""
        return EventBus()

    @pytest.fixture
    def sample_event(self):
        """Create a sample event for testing."""
        return Event(event_type="test_event", source="test_source")

    def test_initialization(self, event_bus):
        """Test that the EventBus initializes with empty subscribers and history."""
        assert len(event_bus.subscribers) == 0
        assert len(event_bus.published_events) == 0
        assert event_bus.max_history == 100

    def test_subscribe(self, event_bus):
        """Test subscribing a handler to an event type."""
        handler = lambda event: None
        
        # Subscribe the handler
        event_bus.subscribe("test_event", handler)
        
        # Verify subscription
        assert len(event_bus.subscribers["test_event"]) == 1
        assert event_bus.subscribers["test_event"][0] == handler

    def test_subscribe_duplicate(self, event_bus):
        """Test that subscribing the same handler twice only adds it once."""
        handler = lambda event: None
        
        # Subscribe the handler twice
        event_bus.subscribe("test_event", handler)
        event_bus.subscribe("test_event", handler)
        
        # Verify no duplicates
        assert len(event_bus.subscribers["test_event"]) == 1

    def test_unsubscribe(self, event_bus):
        """Test unsubscribing a handler from an event type."""
        handler = lambda event: None
        
        # Subscribe then unsubscribe
        event_bus.subscribe("test_event", handler)
        event_bus.unsubscribe("test_event", handler)
        
        # Verify unsubscription
        assert len(event_bus.subscribers["test_event"]) == 0

    def test_unsubscribe_nonexistent(self, event_bus):
        """Test unsubscribing a handler that wasn't subscribed."""
        handler = lambda event: None
        
        # Unsubscribe without subscribing first
        event_bus.unsubscribe("test_event", handler)
        
        # Should not raise an error
        assert "test_event" not in event_bus.subscribers or len(event_bus.subscribers["test_event"]) == 0

    def test_get_subscribers(self, event_bus):
        """Test getting subscribers for an event type."""
        handler1 = lambda event: None
        handler2 = lambda event: None
        
        # Subscribe handlers
        event_bus.subscribe("test_event", handler1)
        event_bus.subscribe("test_event", handler2)
        
        # Get subscribers
        subscribers = event_bus.get_subscribers("test_event")
        
        # Verify subscribers
        assert len(subscribers) == 2
        assert handler1 in subscribers
        assert handler2 in subscribers

    def test_get_subscribers_empty(self, event_bus):
        """Test getting subscribers for an event type with no subscribers."""
        subscribers = event_bus.get_subscribers("nonexistent_event")
        assert len(subscribers) == 0

    @pytest.mark.asyncio
    async def test_publish(self, event_bus, sample_event):
        """Test publishing an event to subscribers."""
        # Create mock handler
        mock_handler = AsyncMock()
        
        # Subscribe mock handler
        event_bus.subscribe(sample_event.event_type, mock_handler)
        
        # Publish event
        await event_bus.publish(sample_event)
        
        # Verify handler was called
        mock_handler.assert_called_once_with(sample_event)
        
        # Verify event was added to history
        assert len(event_bus.published_events) == 1
        assert event_bus.published_events[0] == sample_event

    @pytest.mark.asyncio
    async def test_publish_no_subscribers(self, event_bus, sample_event):
        """Test publishing an event with no subscribers."""
        # Publish event with no subscribers
        await event_bus.publish(sample_event)
        
        # Verify event was added to history even with no subscribers
        assert len(event_bus.published_events) == 1
        assert event_bus.published_events[0] == sample_event

    @pytest.mark.asyncio
    async def test_publish_multiple_subscribers(self, event_bus, sample_event):
        """Test publishing an event to multiple subscribers."""
        # Create mock handlers
        mock_handler1 = AsyncMock()
        mock_handler2 = AsyncMock()
        
        # Subscribe mock handlers
        event_bus.subscribe(sample_event.event_type, mock_handler1)
        event_bus.subscribe(sample_event.event_type, mock_handler2)
        
        # Publish event
        await event_bus.publish(sample_event)
        
        # Verify handlers were called
        mock_handler1.assert_called_once_with(sample_event)
        mock_handler2.assert_called_once_with(sample_event)

    @pytest.mark.asyncio
    async def test_publish_handler_exception(self, event_bus, sample_event):
        """Test that an exception in one handler doesn't prevent others from being called."""
        # Create handlers - one that raises an exception
        async def failing_handler(event):
            raise Exception("Test exception")
            
        mock_handler = AsyncMock()
        
        # Subscribe handlers
        event_bus.subscribe(sample_event.event_type, failing_handler)
        event_bus.subscribe(sample_event.event_type, mock_handler)
        
        # Publish event - should not raise the exception
        await event_bus.publish(sample_event)
        
        # Verify second handler was still called
        mock_handler.assert_called_once_with(sample_event)

    @pytest.mark.asyncio
    async def test_event_priority_sorting(self, event_bus):
        """Test that handlers are sorted by priority for high-priority events."""
        # Create an event with priority
        priority_event = Event(event_type="priority_event")
        priority_event.priority = 10
        
        # Create mock handlers with different priorities
        class PriorityHandler:
            def __init__(self, priority):
                self.priority = priority
                self.handle_event = AsyncMock()
                
        handler1 = PriorityHandler(1)
        handler2 = PriorityHandler(3)
        handler3 = PriorityHandler(2)
        
        # Subscribe handlers
        event_bus.subscribe(priority_event.event_type, handler1)
        event_bus.subscribe(priority_event.event_type, handler2)
        event_bus.subscribe(priority_event.event_type, handler3)
        
        # Publish event
        await event_bus.publish(priority_event)
        
        # All handlers should have been called
        handler1.handle_event.assert_called_once_with(priority_event)
        handler2.handle_event.assert_called_once_with(priority_event)
        handler3.handle_event.assert_called_once_with(priority_event)
        
        # Create a capture for the call order
        call_order = []
        
        # Reset mocks and set side effect to track call order
        handler1.handle_event.reset_mock()
        handler2.handle_event.reset_mock()
        handler3.handle_event.reset_mock()
        
        handler1.handle_event.side_effect = lambda e: call_order.append(1)
        handler2.handle_event.side_effect = lambda e: call_order.append(3)
        handler3.handle_event.side_effect = lambda e: call_order.append(2)
        
        # Publish event again
        await event_bus.publish(priority_event)
        
        # Verify high priority handlers were called first (reverse order: 3, 2, 1)
        assert call_order == [3, 2, 1]

    def test_history_limit(self, event_bus):
        """Test that event history is limited to max_history."""
        # Set a smaller history limit for testing
        event_bus.max_history = 3
        
        # Create events
        events = [Event(event_type="test_event") for _ in range(5)]
        
        # Publish events
        for event in events:
            asyncio.run(event_bus.publish(event))
        
        # Verify history limit
        assert len(event_bus.published_events) == 3
        assert event_bus.published_events == events[2:5]

    def test_clear_history(self, event_bus, sample_event):
        """Test clearing event history."""
        # Publish an event
        asyncio.run(event_bus.publish(sample_event))
        
        # Verify event was added to history
        assert len(event_bus.published_events) == 1
        
        # Clear history
        event_bus.clear_history()
        
        # Verify history is empty
        assert len(event_bus.published_events) == 0

    def test_get_recent_events(self, event_bus):
        """Test getting recent events."""
        # Create events
        events = [Event(event_type="test_event") for _ in range(10)]
        
        # Publish events
        for event in events:
            asyncio.run(event_bus.publish(event))
        
        # Get recent events with default count (10)
        recent_events = event_bus.get_recent_events()
        assert len(recent_events) == 10
        assert recent_events == events
        
        # Get recent events with smaller count
        recent_events = event_bus.get_recent_events(count=5)
        assert len(recent_events) == 5
        assert recent_events == events[5:]