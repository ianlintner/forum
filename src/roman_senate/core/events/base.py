"""
Roman Senate Simulation
Base Event Module

This module defines the base Event class and related interfaces for the event system.
"""

import uuid
from datetime import datetime
from typing import Any, Dict, Optional, Protocol, runtime_checkable
import logging

logger = logging.getLogger(__name__)

class Event:
    """
    Base class for all events in the system.
    
    All events have a unique identifier, type, timestamp, source, and optional metadata.
    """
    
    def __init__(self, event_type: str, source: Any = None, metadata: Optional[Dict[str, Any]] = None):
        """
        Initialize a new event.
        
        Args:
            event_type: The type of event
            source: The entity that generated the event (e.g., a senator)
            metadata: Additional event-specific data
        """
        self.event_id = str(uuid.uuid4())
        self.event_type = event_type
        self.timestamp = datetime.now().isoformat()
        self.source = source
        self.metadata = metadata or {}
        self.priority = 0  # Default priority (higher values = higher priority)
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the event to a dictionary for serialization.
        
        Returns:
            Dictionary representation of the event
        """
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "timestamp": self.timestamp,
            "source": getattr(self.source, "name", str(self.source)) if self.source else None,
            "metadata": self.metadata,
            "priority": self.priority
        }
    
    def __str__(self) -> str:
        """String representation of the event."""
        source_name = getattr(self.source, "name", str(self.source)) if self.source else "Unknown"
        return f"Event({self.event_type}, source={source_name}, id={self.event_id})"


@runtime_checkable
class EventHandler(Protocol):
    """
    Protocol defining the interface for event handlers.
    
    Event handlers must implement an async handle_event method that takes an Event.
    """
    
    async def handle_event(self, event: Event) -> None:
        """
        Process an event.
        
        Args:
            event: The event to process
        """
        ...