"""
Roman Senate Events for Agentic Game Framework.

This module implements Roman Senate specific events using the Agentic Game Framework.
"""

import logging
from datetime import datetime
from typing import Any, Dict, Optional, List

from src.agentic_game_framework.events.base import BaseEvent

logger = logging.getLogger(__name__)

class SenateEvent(BaseEvent):
    """Base class for all Senate-specific events in the framework."""
    
    EVENT_TYPE = "senate.base"
    
    def __init__(
        self,
        event_type: str = None,
        source: Optional[str] = None,
        target: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None,
        event_id: Optional[str] = None
    ):
        """Initialize a Senate event."""
        super().__init__(
            event_type=event_type or self.EVENT_TYPE,
            source=source,
            target=target,
            data=data or {},
            timestamp=timestamp,
            event_id=event_id
        )


class SpeechEvent(SenateEvent):
    """Speech event in the Roman Senate."""
    
    EVENT_TYPE = "senate.speech"
    
    def __init__(
        self,
        speaker_id: str,
        content: str,
        topic: str,
        stance: str,
        source: Optional[str] = None,
        target: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """Initialize a speech event."""
        # Create data structure for the event
        speech_data = data or {}
        speech_data.update({
            "speaker_id": speaker_id,
            "content": content,
            "topic": topic,
            "stance": stance
        })
        
        # Initialize the base event
        super().__init__(
            event_type=self.EVENT_TYPE,
            source=source or speaker_id,
            target=target,
            data=speech_data,
            **kwargs
        )
    
    @property
    def speaker_id(self) -> str:
        """Get the speaker ID."""
        return self.data.get("speaker_id")
    
    @property
    def content(self) -> str:
        """Get the speech content."""
        return self.data.get("content")
    
    @property
    def topic(self) -> str:
        """Get the speech topic."""
        return self.data.get("topic")
    
    @property
    def stance(self) -> str:
        """Get the speaker's stance."""
        return self.data.get("stance")


class DebateEvent(SenateEvent):
    """Debate event in the Roman Senate."""
    
    EVENT_TYPE = "senate.debate"
    
    # Debate event types
    DEBATE_START = "debate_start"
    DEBATE_END = "debate_end"
    SPEAKER_CHANGE = "speaker_change"
    
    def __init__(
        self,
        debate_event_type: str,
        topic: str,
        source: Optional[str] = None,
        target: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """Initialize a debate event."""
        # Create data structure for the event
        debate_data = data or {}
        debate_data.update({
            "debate_event_type": debate_event_type,
            "topic": topic
        })
        
        # Initialize the base event
        super().__init__(
            event_type=self.EVENT_TYPE,
            source=source,
            target=target,
            data=debate_data,
            **kwargs
        )
    
    @property
    def debate_event_type(self) -> str:
        """Get the debate event type."""
        return self.data.get("debate_event_type")
    
    @property
    def topic(self) -> str:
        """Get the debate topic."""
        return self.data.get("topic")


class ReactionEvent(SenateEvent):
    """Reaction event in the Roman Senate."""
    
    EVENT_TYPE = "senate.reaction"
    
    def __init__(
        self,
        reactor_id: str,
        target_event_id: str,
        reaction_type: str,
        content: str,
        source: Optional[str] = None,
        target: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """Initialize a reaction event."""
        # Create data structure for the event
        reaction_data = data or {}
        reaction_data.update({
            "reactor_id": reactor_id,
            "target_event_id": target_event_id,
            "reaction_type": reaction_type,
            "content": content
        })
        
        # Initialize the base event
        super().__init__(
            event_type=self.EVENT_TYPE,
            source=source or reactor_id,
            target=target,
            data=reaction_data,
            **kwargs
        )
    
    @property
    def reactor_id(self) -> str:
        """Get the reactor ID."""
        return self.data.get("reactor_id")
    
    @property
    def target_event_id(self) -> str:
        """Get the target event ID."""
        return self.data.get("target_event_id")
    
    @property
    def reaction_type(self) -> str:
        """Get the reaction type."""
        return self.data.get("reaction_type")
    
    @property
    def content(self) -> str:
        """Get the reaction content."""
        return self.data.get("content")


class InterjectionEvent(SenateEvent):
    """Interjection event in the Roman Senate."""
    
    EVENT_TYPE = "senate.interjection"
    
    # Interjection types
    SUPPORT = "support"
    OPPOSITION = "opposition"
    QUESTION = "question"
    CLARIFICATION = "clarification"
    PROCEDURAL = "procedural"
    
    def __init__(
        self,
        interjecter_id: str,
        target_speaker_id: str,
        interjection_type: str,
        content: str,
        source: Optional[str] = None,
        target: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """Initialize an interjection event."""
        # Create data structure for the event
        interjection_data = data or {}
        interjection_data.update({
            "interjecter_id": interjecter_id,
            "target_speaker_id": target_speaker_id,
            "interjection_type": interjection_type,
            "content": content
        })
        
        # Initialize the base event
        super().__init__(
            event_type=self.EVENT_TYPE,
            source=source or interjecter_id,
            target=target or target_speaker_id,
            data=interjection_data,
            **kwargs
        )
    
    @property
    def interjecter_id(self) -> str:
        """Get the interjecter ID."""
        return self.data.get("interjecter_id")
    
    @property
    def target_speaker_id(self) -> str:
        """Get the target speaker ID."""
        return self.data.get("target_speaker_id")
    
    @property
    def interjection_type(self) -> str:
        """Get the interjection type."""
        return self.data.get("interjection_type")
    
    @property
    def content(self) -> str:
        """Get the interjection content."""
        return self.data.get("content")


class RelationshipEvent(SenateEvent):
    """Relationship event in the Roman Senate."""
    
    EVENT_TYPE = "senate.relationship"
    
    # Relationship event types
    RELATIONSHIP_CHANGE = "relationship_change"
    ALLIANCE_FORMED = "alliance_formed"
    RIVALRY_FORMED = "rivalry_formed"
    
    def __init__(
        self,
        source_id: str,
        target_id: str,
        relationship_event_type: str,
        relationship_type: str,
        change_value: float,
        reason: str,
        source: Optional[str] = None,
        target: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """Initialize a relationship event."""
        # Create data structure for the event
        relationship_data = data or {}
        relationship_data.update({
            "source_id": source_id,
            "target_id": target_id,
            "relationship_event_type": relationship_event_type,
            "relationship_type": relationship_type,
            "change_value": change_value,
            "reason": reason
        })
        
        # Initialize the base event
        super().__init__(
            event_type=self.EVENT_TYPE,
            source=source or source_id,
            target=target or target_id,
            data=relationship_data,
            **kwargs
        )
    
    @property
    def source_id(self) -> str:
        """Get the source ID."""
        return self.data.get("source_id")
    
    @property
    def target_id(self) -> str:
        """Get the target ID."""
        return self.data.get("target_id")
    
    @property
    def relationship_event_type(self) -> str:
        """Get the relationship event type."""
        return self.data.get("relationship_event_type")
    
    @property
    def relationship_type(self) -> str:
        """Get the relationship type."""
        return self.data.get("relationship_type")
    
    @property
    def change_value(self) -> float:
        """Get the change value."""
        return self.data.get("change_value")
    
    @property
    def reason(self) -> str:
        """Get the reason for the change."""
        return self.data.get("reason")


# Event utility functions
def create_debate_start_event(topic: str, source_id: Optional[str] = None) -> DebateEvent:
    """
    Create a debate start event.
    
    Args:
        topic: The debate topic
        source_id: Optional source identifier
        
    Returns:
        A debate start event
    """
    return DebateEvent(
        debate_event_type=DebateEvent.DEBATE_START,
        topic=topic,
        source=source_id
    )

def create_debate_end_event(topic: str, source_id: Optional[str] = None) -> DebateEvent:
    """
    Create a debate end event.
    
    Args:
        topic: The debate topic
        source_id: Optional source identifier
        
    Returns:
        A debate end event
    """
    return DebateEvent(
        debate_event_type=DebateEvent.DEBATE_END,
        topic=topic,
        source=source_id
    )

def create_speaker_change_event(
    topic: str, 
    speaker_id: str, 
    source_id: Optional[str] = None
) -> DebateEvent:
    """
    Create a speaker change event.
    
    Args:
        topic: The debate topic
        speaker_id: The new speaker's ID
        source_id: Optional source identifier
        
    Returns:
        A speaker change event
    """
    # Create data with speaker information
    data = {
        "speaker_id": speaker_id
    }
    
    return DebateEvent(
        debate_event_type=DebateEvent.SPEAKER_CHANGE,
        topic=topic,
        source=source_id,
        target=speaker_id,
        data=data
    )