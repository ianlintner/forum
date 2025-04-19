"""
Event Bus for Roman Senate.

This module provides the central event dispatching mechanism for the Roman Senate
simulation, adapting the agentic_game_framework event bus architecture.

Part of the Migration Plan: Phase 1 - Core Event System.
"""

from collections import defaultdict
from typing import Callable, Dict, List, Optional, Set, Type

from agentic_game_framework.events.event_bus import EventBus as FrameworkEventBus

from .base import BaseEvent, EventHandler


class EventBus:
    """
    Central event dispatcher for the Roman Senate simulation.
    
    The EventBus allows components to:
    1. Subscribe to specific event types
    2. Publish events to all interested subscribers
    3. Filter and prioritize event handling
    
    This implementation adapts the agentic_game_framework's EventBus
    to the Roman Senate application context.
    """
    
    def __init__(self):
        """Initialize a new event bus with empty handler registries."""
        # Map of event_type -> set of handlers
        self._handlers: Dict[str, Set[EventHandler]] = defaultdict(set)
        # Map of event_type -> set of wildcard handlers (receive all events)
        self._wildcard_handlers: Set[EventHandler] = set()
        # Optional event filters that can block events
        self._filters: List[Callable[[BaseEvent], bool]] = []
        # Handler priorities (higher numbers = higher priority)
        self._priorities: Dict[EventHandler, int] = {}
    
    def subscribe(self, event_type: str, handler: EventHandler, priority: int = 0) -> None:
        """
        Register a handler to receive events of a specific type.
        
        Args:
            event_type: The event type to subscribe to
            handler: The handler that will process these events
            priority: Handler priority (higher numbers = higher priority)
        """
        self._handlers[event_type].add(handler)
        self._priorities[handler] = priority
    
    def subscribe_to_all(self, handler: EventHandler, priority: int = 0) -> None:
        """
        Register a handler to receive all events regardless of type.
        
        Args:
            handler: The handler that will process all events
            priority: Handler priority (higher numbers = higher priority)
        """
        self._wildcard_handlers.add(handler)
        self._priorities[handler] = priority
    
    def unsubscribe(self, event_type: str, handler: EventHandler) -> None:
        """
        Remove a handler's subscription to a specific event type.
        
        Args:
            event_type: The event type to unsubscribe from
            handler: The handler to remove
        """
        if event_type in self._handlers and handler in self._handlers[event_type]:
            self._handlers[event_type].remove(handler)
            
            # Clean up empty handler sets
            if not self._handlers[event_type]:
                del self._handlers[event_type]
                
        # Clean up priorities if no longer needed
        if not any(handler in handlers for handlers in self._handlers.values()) and handler not in self._wildcard_handlers:
            if handler in self._priorities:
                del self._priorities[handler]
    
    def unsubscribe_from_all(self, handler: EventHandler) -> None:
        """
        Remove a handler from all event subscriptions.
        
        Args:
            handler: The handler to remove
        """
        # Remove from wildcard handlers
        if handler in self._wildcard_handlers:
            self._wildcard_handlers.remove(handler)
            
        # Remove from specific event type handlers
        for event_type in list(self._handlers.keys()):
            if handler in self._handlers[event_type]:
                self._handlers[event_type].remove(handler)
                
                # Clean up empty handler sets
                if not self._handlers[event_type]:
                    del self._handlers[event_type]
                    
        # Clean up priorities
        if handler in self._priorities:
            del self._priorities[handler]
    
    def add_filter(self, filter_func: Callable[[BaseEvent], bool]) -> None:
        """
        Add a filter function that can block events from being processed.
        
        Args:
            filter_func: Function that returns True if event should be processed, False to block
        """
        self._filters.append(filter_func)
    
    def remove_filter(self, filter_func: Callable[[BaseEvent], bool]) -> None:
        """
        Remove a previously added filter function.
        
        Args:
            filter_func: The filter function to remove
        """
        if filter_func in self._filters:
            self._filters.remove(filter_func)
    
    def get_handlers(self, event_type: str) -> List[EventHandler]:
        """
        Get all handlers for a specific event type, sorted by priority.
        
        Args:
            event_type: The event type to get handlers for
            
        Returns:
            List[EventHandler]: Sorted list of handlers (highest priority first)
        """
        # Combine specific handlers and wildcard handlers
        all_handlers = list(self._handlers.get(event_type, set())) + list(self._wildcard_handlers)
        
        # Sort by priority (highest first)
        return sorted(all_handlers, key=lambda h: self._priorities.get(h, 0), reverse=True)
    
    def publish(self, event: BaseEvent) -> bool:
        """
        Publish an event to all subscribed handlers.
        
        The event will be passed through all filters first. If any filter returns False,
        the event will not be processed.
        
        Args:
            event: The event to publish
            
        Returns:
            bool: True if the event was processed, False if it was filtered out
        """
        # Check if event passes all filters
        for filter_func in self._filters:
            if not filter_func(event):
                return False
                
        # Get handlers for this event type
        handlers = self.get_handlers(event.event_type)
        
        # Dispatch event to all handlers
        for handler in handlers:
            try:
                handler.handle_event(event)
            except Exception as e:
                # In a real system, we would log this error
                print(f"Error in handler {handler} processing event {event}: {e}")
                
        return True
    
    @classmethod
    def create_from_framework_bus(cls, framework_bus: Optional[FrameworkEventBus] = None) -> 'EventBus':
        """
        Create an EventBus that proxies to a framework EventBus, if provided.
        
        This is useful for integrating with existing framework components.
        
        Args:
            framework_bus: Optional framework EventBus to delegate to
            
        Returns:
            EventBus: A new event bus
        """
        bus = cls()
        
        if framework_bus:
            # Create an adapter that forwards events to the framework bus
            bus.publish_original = bus.publish
            
            def proxy_publish(event):
                # Publish locally
                bus.publish_original(event)
                # Also publish to framework bus
                framework_bus.publish(event)
                return True
                
            bus.publish = proxy_publish
            
        return bus