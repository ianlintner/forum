"""
Base Event System for Agentic Game Framework.

This module defines the core event classes and interfaces that form the backbone
of the event-driven architecture used throughout the framework.
"""

import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Optional, Union


class BaseEvent(ABC):
    """
    Abstract base class for all events in the system.
    
    Events are the primary communication mechanism between components in the framework.
    Each event has a type, timestamp, optional source and target, and additional data.
    
    Attributes:
        event_type (str): The type identifier for the event
        timestamp (datetime): When the event was created
        source (Optional[str]): Identifier of the component that generated the event
        target (Optional[str]): Identifier of the intended recipient (if any)
        data (Dict[str, Any]): Additional event-specific data
    """
    
    def __init__(
        self,
        event_type: str,
        source: Optional[str] = None,
        target: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None,
        event_id: Optional[str] = None
    ):
        """
        Initialize a new event.
        
        Args:
            event_type: The type identifier for the event
            source: Identifier of the component that generated the event
            target: Identifier of the intended recipient (if any)
            data: Additional event-specific data
            timestamp: When the event was created (defaults to now)
            event_id: Unique identifier for the event (generated if not provided)
        """
        self.event_type = event_type
        self.source = source
        self.target = target
        self.data = data or {}
        self.timestamp = timestamp or datetime.now()
        self._id = event_id or str(uuid.uuid4())
    
    def get_id(self) -> str:
        """
        Get the unique identifier for this event.
        
        Returns:
            str: The event's unique identifier
        """
        return self._id
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the event to a dictionary representation.
        
        This is useful for serialization, persistence, and transmission.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the event
        """
        return {
            "id": self._id,
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "target": self.target,
            "data": self.data
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseEvent':
        """
        Create an event from a dictionary representation.
        
        Args:
            data: Dictionary containing event data
            
        Returns:
            BaseEvent: A new event instance
            
        Raises:
            ValueError: If the dictionary is missing required fields
        """
        if "event_type" not in data:
            raise ValueError("Event dictionary must contain 'event_type'")
        
        timestamp = data.get("timestamp")
        if timestamp and isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)
            
        return cls(
            event_type=data["event_type"],
            source=data.get("source"),
            target=data.get("target"),
            data=data.get("data", {}),
            timestamp=timestamp,
            event_id=data.get("id")
        )
    
    def __str__(self) -> str:
        """
        Get a string representation of the event.
        
        Returns:
            str: String representation
        """
        return f"{self.event_type} (id: {self._id}, source: {self.source}, target: {self.target})"


class EventHandler(ABC):
    """
    Abstract base class for event handlers.
    
    Event handlers process events of specific types and implement the business logic
    for responding to those events.
    """
    
    @abstractmethod
    def handle_event(self, event: BaseEvent) -> None:
        """
        Process an event.
        
        Args:
            event: The event to process
        """
        pass