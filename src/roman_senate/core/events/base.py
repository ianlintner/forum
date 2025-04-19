"""
Base Event System for Roman Senate.

This module defines the core event classes and interfaces that adapt the
event-driven architecture from the agentic_game_framework for use in the
Roman Senate project.

Part of the Migration Plan: Phase 1 - Core Event System.
"""

import uuid
from datetime import datetime
from typing import Any, Dict, Optional, Union

# Import from the agentic_game_framework
from agentic_game_framework.events.base import BaseEvent as FrameworkBaseEvent
from agentic_game_framework.events.base import EventHandler as FrameworkEventHandler


class RomanEvent(FrameworkBaseEvent):
    """
    Base class for all Roman Senate specific events.
    
    This class extends the agentic_game_framework BaseEvent class to provide
    specific functionality needed for the Roman Senate simulation.
    
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
        Initialize a new Roman Senate event.
        
        Args:
            event_type: The type identifier for the event
            source: Identifier of the component that generated the event
            target: Identifier of the intended recipient (if any)
            data: Additional event-specific data
            timestamp: When the event was created (defaults to now)
            event_id: Unique identifier for the event (generated if not provided)
        """
        super().__init__(
            event_type=event_type,
            source=source,
            target=target,
            data=data or {},
            timestamp=timestamp,
            event_id=event_id
        )


class RomanEventHandler(FrameworkEventHandler):
    """
    Base class for Roman Senate specific event handlers.
    
    Event handlers process events of specific types and implement the business logic
    for responding to those events within the Roman Senate simulation.
    """
    
    def handle_event(self, event: RomanEvent) -> None:
        """
        Process a Roman Senate event.
        
        Args:
            event: The event to process
        """
        # Delegate to child class implementation
        pass


# For backward compatibility and simpler imports in rest of codebase
BaseEvent = RomanEvent
EventHandler = RomanEventHandler