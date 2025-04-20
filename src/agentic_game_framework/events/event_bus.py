"""
Event Bus for Agentic Game Framework.

This module provides the central event dispatching mechanism that allows components
to publish events and subscribe to event types they're interested in.
"""

import logging
import time
import threading
from collections import defaultdict, deque
from typing import Callable, Dict, List, Optional, Set, Type, Tuple, Any, Iterable

from .base import BaseEvent, EventHandler

# Set up module logger
logger = logging.getLogger(__name__)

class EventBus:
    """
    Central event dispatcher for the framework.
    
    The EventBus allows components to:
    1. Subscribe to specific event types
    2. Publish events to all interested subscribers
    3. Filter and prioritize event handling
    
    It maintains a registry of event handlers for each event type and
    dispatches events to the appropriate handlers when they are published.
    """
    
    def _start_processing_thread(self) -> None:
        """Start a background thread for processing events asynchronously."""
        if self._processing_thread is not None and self._processing_thread.is_alive():
            return
            
        def process_events() -> None:
            """Process events from the queue in a loop."""
            logger.info("Event processing thread started")
            while not self._stop_processing.is_set():
                # Process a batch of events
                processed = 0
                start_time = time.time()
                
                with self._lock:
                    # Check if there are events in the queue
                    if len(self._event_queue) == 0:
                        self._stop_processing.wait(0.01)  # Brief pause if queue is empty
                        continue
                    
                    # Track high water mark
                    queue_size = len(self._event_queue)
                    if queue_size > self._metrics["queue_high_water_mark"]:
                        self._metrics["queue_high_water_mark"] = queue_size
                    
                    # Get a batch of events to process
                    batch = []
                    for _ in range(min(self._batch_size, len(self._event_queue))):
                        if self._event_queue:
                            batch.append(self._event_queue.popleft())
                
                # Process each event in the batch
                for event in batch:
                    self._process_event(event)
                    processed += 1
                    
                # Record metrics
                if processed > 0 and self._monitor_performance:
                    batch_time = time.time() - start_time
                    avg_time = batch_time / processed
                    with self._lock:
                        self._metrics["avg_processing_time"] = (
                            (self._metrics["avg_processing_time"] * self._metrics["events_processed"] + batch_time) /
                            (self._metrics["events_processed"] + processed)
                        )
                        self._metrics["events_processed"] += processed
                        
                    if batch_time > 0.1:  # Log slow batch processing
                        logger.debug(f"Processed {processed} events in {batch_time:.3f}s ({avg_time:.3f}s per event)")
                
        self._stop_processing.clear()
        self._processing_thread = threading.Thread(target=process_events, daemon=True)
        self._processing_thread.start()

    def __init__(self, enable_async: bool = False, batch_size: int = 10,
                monitor_performance: bool = True):
        """
        Initialize a new event bus with empty handler registries.
        
        Args:
            enable_async: Whether to enable asynchronous event processing
            batch_size: Number of events to process in a batch (for async mode)
            monitor_performance: Whether to track detailed performance metrics
        """
        # Map of event_type -> set of handlers
        self._handlers: Dict[str, Set[EventHandler]] = defaultdict(set)
        
        # Wildcard handlers (receive all events)
        self._wildcard_handlers: Set[EventHandler] = set()
        
        # Optional event filters that can block events
        self._filters: List[Callable[[BaseEvent], bool]] = []
        
        # Handler priorities (higher numbers = higher priority)
        self._priorities: Dict[EventHandler, int] = {}
        
        # Cache for sorted handlers (invalidated when subscriptions change)
        self._handlers_cache: Dict[str, List[EventHandler]] = {}
        
        # Event frequency tracking (for optimization)
        self._event_frequency: Dict[str, int] = defaultdict(int)
        self._frequent_events: Set[str] = set()  # Event types that occur frequently
        
        # Settings
        self._enable_async = enable_async
        self._batch_size = batch_size
        self._monitor_performance = monitor_performance
        
        # Event queue for asynchronous processing
        self._event_queue = deque()
        self._processing_thread = None
        self._stop_processing = threading.Event()
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Performance metrics
        self._metrics = {
            "events_published": 0,
            "events_filtered": 0,
            "events_queued": 0,
            "events_processed": 0,
            "handler_errors": 0,
            "handler_calls": 0,
            "avg_processing_time": 0.0,
            "max_processing_time": 0.0,
            "queue_high_water_mark": 0
        }
        
        # Handler performance tracking
        self._handler_metrics: Dict[EventHandler, Dict[str, Any]] = {}
        
        # Start async processing thread if enabled
        if enable_async:
            self._start_processing_thread()
            
        logger.info(f"Initialized EventBus with async={'enabled' if enable_async else 'disabled'}, " +
                   f"batch_size={batch_size}")
    
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
        
        # Invalidate cache for this event type
        if event_type in self._handlers_cache:
            del self._handlers_cache[event_type]
    
    def subscribe_to_all(self, handler: EventHandler, priority: int = 0) -> None:
        """
        Register a handler to receive all events regardless of type.
        
        Args:
            handler: The handler that will process all events
            priority: Handler priority (higher numbers = higher priority)
        """
        self._wildcard_handlers.add(handler)
        self._priorities[handler] = priority
        
        # Invalidate all caches since wildcard handlers affect all event types
        self._handlers_cache.clear()
        logger.debug(f"Handler {handler} subscribed to all events with priority {priority}")
    
    def unsubscribe(self, event_type: str, handler: EventHandler) -> None:
        """
        Remove a handler's subscription to a specific event type.
        
        Args:
            event_type: The event type to unsubscribe from
            handler: The handler to remove
        """
        was_removed = False
        if event_type in self._handlers and handler in self._handlers[event_type]:
            self._handlers[event_type].remove(handler)
            was_removed = True
            
            # Clean up empty handler sets
            if not self._handlers[event_type]:
                del self._handlers[event_type]
                
        # Clean up priorities if no longer needed
        if not any(handler in handlers for handlers in self._handlers.values()) and handler not in self._wildcard_handlers:
            if handler in self._priorities:
                del self._priorities[handler]
                
        # Invalidate cache for this event type
        if was_removed and event_type in self._handlers_cache:
            del self._handlers_cache[event_type]
            logger.debug(f"Handler {handler} unsubscribed from {event_type}")
    
    def unsubscribe_from_all(self, handler: EventHandler) -> None:
        """
        Remove a handler from all event subscriptions.
        
        Args:
            handler: The handler to remove
        """
        was_wildcard = False
        # Remove from wildcard handlers
        if handler in self._wildcard_handlers:
            self._wildcard_handlers.remove(handler)
            was_wildcard = True
            
        # Remove from specific event type handlers
        affected_types = []
        for event_type in list(self._handlers.keys()):
            if handler in self._handlers[event_type]:
                self._handlers[event_type].remove(handler)
                affected_types.append(event_type)
                
                # Clean up empty handler sets
                if not self._handlers[event_type]:
                    del self._handlers[event_type]
                    
        # Clean up priorities
        if handler in self._priorities:
            del self._priorities[handler]
        
        # Invalidate caches
        if was_wildcard:
            # Wildcard handlers affect all events, so clear entire cache
            self._handlers_cache.clear()
            logger.debug(f"Wildcard handler {handler} unsubscribed from all events")
        else:
            # Only clear cache for affected event types
            for event_type in affected_types:
                if event_type in self._handlers_cache:
                    del self._handlers_cache[event_type]
            if affected_types:
                logger.debug(f"Handler {handler} unsubscribed from {len(affected_types)} event types")
    
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
        Uses caching for improved performance.
        
        Args:
            event_type: The event type to get handlers for
            
        Returns:
            List[EventHandler]: Sorted list of handlers (highest priority first)
        """
        # Check cache first
        if event_type in self._handlers_cache:
            return self._handlers_cache[event_type]
            
        # Combine specific handlers and wildcard handlers
        all_handlers = list(self._handlers.get(event_type, set())) + list(self._wildcard_handlers)
        
        # Sort by priority (highest first)
        sorted_handlers = sorted(all_handlers, key=lambda h: self._priorities.get(h, 0), reverse=True)
        
        # Cache the result
        self._handlers_cache[event_type] = sorted_handlers
        
        return sorted_handlers
    
    def _start_processing_thread(self) -> None:
        """Start a background thread for processing events asynchronously."""
        if self._processing_thread is not None and self._processing_thread.is_alive():
            return
            
        def process_events() -> None:
            """Process events from the queue in a loop."""
            logger.info("Event processing thread started")
            while not self._stop_processing.is_set():
                # Process a batch of events
                processed = 0
                start_time = time.time()
                
                with self._lock:
                    # Check if there are events in the queue
                    if len(self._event_queue) == 0:
                        self._stop_processing.wait(0.01)  # Brief pause if queue is empty
                        continue
                    
                    # Track high water mark
                    queue_size = len(self._event_queue)
                    if queue_size > self._metrics["queue_high_water_mark"]:
                        self._metrics["queue_high_water_mark"] = queue_size
                    
                    # Get a batch of events to process
                    batch = []
                    for _ in range(min(self._batch_size, len(self._event_queue))):
                        if self._event_queue:
                            batch.append(self._event_queue.popleft())
                
                # Process each event in the batch
                for event in batch:
                    self._process_event(event)
                    processed += 1
                    
                # Record metrics
                if processed > 0 and self._monitor_performance:
                    batch_time = time.time() - start_time
                    avg_time = batch_time / processed
                    with self._lock:
                        self._metrics["avg_processing_time"] = (
                            (self._metrics["avg_processing_time"] * self._metrics["events_processed"] + batch_time) /
                            (self._metrics["events_processed"] + processed)
                        )
                        self._metrics["events_processed"] += processed
                        
                    if batch_time > 0.1:  # Log slow batch processing
                        logger.debug(f"Processed {processed} events in {batch_time:.3f}s ({avg_time:.3f}s per event)")
                
        self._stop_processing.clear()
        self._processing_thread = threading.Thread(target=process_events, daemon=True)
        self._processing_thread.start()

    def stop(self) -> None:
        """Stop the event processing thread and clean up resources."""
        if self._processing_thread and self._processing_thread.is_alive():
            logger.info("Stopping event processing thread...")
            self._stop_processing.set()
            self._processing_thread.join(timeout=1.0)
            if self._processing_thread.is_alive():
                logger.warning("Event processing thread did not stop gracefully")
                
        # Process any remaining events in the queue
        remaining = len(self._event_queue)
        if remaining > 0:
            logger.info(f"Processing {remaining} remaining events before shutdown")
            while self._event_queue:
                event = self._event_queue.popleft()
                self._process_event(event)
                
        # Log final metrics
        if self._monitor_performance:
            logger.info(f"EventBus shutdown. Final metrics: {self._metrics}")

    def _process_event(self, event: BaseEvent) -> bool:
        """
        Process a single event by dispatching it to handlers.
        
        Args:
            event: The event to process
            
        Returns:
            bool: True if the event was processed, False if it was filtered out
        """
        start_time = time.time()
        
        # Check if event passes all filters
        for filter_func in self._filters:
            if not filter_func(event):
                with self._lock:
                    self._metrics["events_filtered"] += 1
                logger.debug(f"Event filtered: {event.event_type}")
                return False
                
        # Track event frequency
        if self._monitor_performance:
            with self._lock:
                event_type = event.event_type
                self._event_frequency[event_type] += 1
                if self._event_frequency[event_type] > 100:  # Arbitrary threshold
                    self._frequent_events.add(event_type)
                
        # Get handlers for this event type (using cached version)
        handlers = self.get_handlers(event.event_type)
        
        if not handlers:
            logger.debug(f"No handlers for event type: {event.event_type}")
            return True  # Event was published but no handlers were interested
        
        # Dispatch event to all handlers
        for handler in handlers:
            try:
                handler_start = time.time() if self._monitor_performance else 0
                handler.handle_event(event)
                
                # Track handler performance
                if self._monitor_performance:
                    handler_time = time.time() - handler_start
                    with self._lock:
                        self._metrics["handler_calls"] += 1
                        if handler not in self._handler_metrics:
                            self._handler_metrics[handler] = {
                                "calls": 0,
                                "errors": 0,
                                "total_time": 0,
                                "avg_time": 0
                            }
                        
                        metrics = self._handler_metrics[handler]
                        metrics["calls"] += 1
                        metrics["total_time"] += handler_time
                        metrics["avg_time"] = metrics["total_time"] / metrics["calls"]
                        
                        if handler_time > 0.05:  # Flag slow handlers
                            logger.debug(f"Slow handler {handler} for {event.event_type}: {handler_time:.4f}s")
            
            except Exception as e:
                with self._lock:
                    self._metrics["handler_errors"] += 1
                    if self._monitor_performance and handler in self._handler_metrics:
                        self._handler_metrics[handler]["errors"] += 1
                logger.error(f"Error in handler {handler} processing event {event}: {e}", exc_info=True)
        
        # Log timing for high frequency events
        processing_time = time.time() - start_time
        if processing_time > 0.1:  # Log slow event processing
            logger.warning(f"Slow event processing: {event.event_type} took {processing_time:.3f}s with {len(handlers)} handlers")
            
        # Update max processing time metric
        if self._monitor_performance and processing_time > self._metrics["max_processing_time"]:
            with self._lock:
                self._metrics["max_processing_time"] = processing_time
        
        return True

    def publish(self, event: BaseEvent) -> bool:
        """
        Publish an event to all subscribed handlers.
        
        In synchronous mode, the event is processed immediately.
        In asynchronous mode, the event is added to the queue for processing.
        
        Args:
            event: The event to publish
            
        Returns:
            bool: True if the event was queued/processed, False if it was filtered out
        """
        with self._lock:
            self._metrics["events_published"] += 1
        
        # In async mode, add to queue and return immediately
        if self._enable_async:
            # Quick filter check before queuing
            for filter_func in self._filters:
                if not filter_func(event):
                    with self._lock:
                        self._metrics["events_filtered"] += 1
                    return False
            
            # Add to queue for async processing
            with self._lock:
                self._event_queue.append(event)
                self._metrics["events_queued"] += 1
                
                # Start processing thread if it's not running
                if not self._processing_thread or not self._processing_thread.is_alive():
                    self._start_processing_thread()
                    
            return True
        
        # In synchronous mode, process immediately
        return self._process_event(event)