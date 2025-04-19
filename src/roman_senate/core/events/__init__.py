"""
Roman Senate AI Game - Events Package.

This package provides the core event system for the Roman Senate simulation.
It includes base event classes, debate-specific events, and event management.

Part of the Migration Plan: Phase 1 - Core Event System.
"""

# Base event classes
from .base import BaseEvent, EventHandler, RomanEvent, RomanEventHandler

# Event bus for event distribution
from .event_bus import EventBus

# Debate-specific events
from .debate_events import (
    DebateStartedEvent,
    DebateEndedEvent,
    SpeechStartedEvent,
    SpeechEndedEvent,
    InterjectionEvent,
    VoteRequestedEvent,
    DebateTopicChangedEvent
)

# Debate management
from .debate_manager import DebateManager, DebateSession

# Export all classes for easier imports
__all__ = [
    # Base
    'BaseEvent',
    'EventHandler',
    'RomanEvent',
    'RomanEventHandler',
    
    # Event Bus
    'EventBus',
    
    # Debate Events
    'DebateStartedEvent',
    'DebateEndedEvent',
    'SpeechStartedEvent',
    'SpeechEndedEvent',
    'InterjectionEvent',
    'VoteRequestedEvent',
    'DebateTopicChangedEvent',
    
    # Management
    'DebateManager',
    'DebateSession'
]