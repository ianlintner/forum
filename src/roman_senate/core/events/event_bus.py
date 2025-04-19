"""
Roman Senate Simulation
Event Bus Module

This module provides the EventBus class, which implements the publisher-subscriber pattern
for distributing events throughout the simulation.
"""

import logging
import asyncio
from typing import Any, Callable, Dict, List, Optional, Set, Type, Union
from collections import defaultdict

from .base import Event, EventHandler

logger = logging.getLogger(__name__)

class EventBus:
    """
    Central event distribution system implementing the publisher-subscriber pattern.
    
    The EventBus allows components to:
    1. Subscribe to specific event types
    2. Publish events to all subscribers
    3. Prioritize event handling based on subscriber attributes (e.g., senator rank)
    """
    
    def __init__(self):
        """Initialize the event bus with empty subscriber collections."""
        # Map of event_type -> list of handler functions/objects
        self.subscribers = defaultdict(list)
        # Set of all events that have been published (for debugging/history)
        self.published_events: List[Event] = []
        # Maximum events to keep in history
        self.max_history = 100
        
    def subscribe(self, event_type: str, handler: Union[EventHandler, Callable[[Event], Any]]) -> None:
        """
        Subscribe to events of a specific type.
        
        Args:
            event_type: The type of events to subscribe to
            handler: The handler function or object to call when events occur
        """
        if handler not in self.subscribers[event_type]:
            self.subscribers[event_type].append(handler)
            logger.debug(f"Subscribed handler to {event_type} events")
        
    def unsubscribe(self, event_type: str, handler: Union[EventHandler, Callable[[Event], Any]]) -> None:
        """
        Unsubscribe from events of a specific type.
        
        Args:
            event_type: The type of events to unsubscribe from
            handler: The handler to remove
        """
        if event_type in self.subscribers:
            self.subscribers[event_type] = [h for h in self.subscribers[event_type] if h != handler]
            logger.debug(f"Unsubscribed handler from {event_type} events")
    
    def get_subscribers(self, event_type: str) -> List[Union[EventHandler, Callable[[Event], Any]]]:
        """
        Get all subscribers for a specific event type.
        
        Args:
            event_type: The event type to get subscribers for
            
        Returns:
            List of handler functions or objects
        """
        return self.subscribers.get(event_type, [])
    
    async def publish(self, event: Event) -> None:
        """
        Publish an event to all subscribers.
        
        This method distributes the event to all handlers that have subscribed to
        the event's type. Handlers are called in order of priority if applicable.
        
        Args:
            event: The event to publish
        """
        logger.debug(f"Publishing event: {event}")
        
        # Add to history (limited size)
        self.published_events.append(event)
        if len(self.published_events) > self.max_history:
            self.published_events = self.published_events[-self.max_history:]
        
        # If no subscribers for this event type, just return
        if event.event_type not in self.subscribers:
            logger.debug(f"No subscribers for event type: {event.event_type}")
            return
            
        # Get handlers for this event type
        handlers = self.subscribers[event.event_type]
        
        # Sort handlers by priority if the event has a priority
        # This is used for interruptions where senator rank matters
        if hasattr(event, 'priority') and event.priority > 0:
            # Sort handlers based on senator rank if handlers are senator agents
            handlers = sorted(
                handlers, 
                key=lambda h: self._get_handler_priority(h),
                reverse=True  # Higher priority first
            )
        
        # Notify all subscribers
        for handler in handlers:
            try:
                if hasattr(handler, 'handle_event'):
                    # If it's an object with handle_event method
                    await handler.handle_event(event)
                else:
                    # If it's a callable function
                    result = handler(event)
                    # If the result is a coroutine, await it
                    if asyncio.iscoroutine(result):
                        await result
            except Exception as e:
                logger.error(f"Error in event handler: {e}", exc_info=True)
    
    def _get_handler_priority(self, handler: Any) -> int:
        """
        Determine the priority of a handler based on its attributes.
        
        For senator agents, this will use their rank. For other handlers,
        it will use a default priority.
        
        Args:
            handler: The event handler
            
        Returns:
            Priority value (higher = more important)
        """
        # If handler is a senator agent, use their rank
        if hasattr(handler, 'senator') and hasattr(handler.senator, 'get'):
            return handler.senator.get('rank', 0)
        
        # If handler has an explicit priority attribute, use that
        if hasattr(handler, 'priority'):
            return handler.priority
        
        # Default priority
        return 0
    
    def clear_history(self) -> None:
        """Clear the event history."""
        self.published_events = []
        
    def get_recent_events(self, count: int = 10) -> List[Event]:
        """
        Get the most recent events.
        
        Args:
            count: Maximum number of events to return
            
        Returns:
            List of recent events
        """
        return self.published_events[-count:]