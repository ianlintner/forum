"""
Roman Senate Simulation
Events Package

This package provides the event-driven architecture for the Roman Senate simulation,
enabling senators to observe, listen to, and react to events in their environment.
"""

from .base import Event, EventHandler
from .event_bus import EventBus
from .debate_events import (
    DebateEvent, 
    DebateEventType,
    SpeechEvent, 
    ReactionEvent, 
    InterjectionEvent,
    InterjectionType
)
from .debate_manager import DebateManager

__all__ = [
    'Event',
    'EventHandler',
    'EventBus',
    'DebateEvent',
    'DebateEventType',
    'SpeechEvent',
    'ReactionEvent',
    'InterjectionEvent',
    'InterjectionType',
    'DebateManager',
]