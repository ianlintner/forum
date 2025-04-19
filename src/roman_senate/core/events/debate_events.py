"""
Roman Senate Simulation
Debate Events Module

This module defines event types specific to senate debates, including speech events,
reaction events, and interjection events.
"""

import enum
from typing import Any, Dict, List, Optional

from .base import Event

class DebateEventType(enum.Enum):
    """Types of debate-level events."""
    DEBATE_START = "debate_start"
    DEBATE_END = "debate_end"
    SPEAKER_CHANGE = "speaker_change"
    TOPIC_CHANGE = "topic_change"


class InterjectionType(enum.Enum):
    """Types of interjections during speeches."""
    SUPPORT = "support"           # Expressions of agreement
    CHALLENGE = "challenge"       # Questioning or challenging a point
    PROCEDURAL = "procedural"     # Points of order or procedure
    EMOTIONAL = "emotional"       # Emotional outbursts
    INFORMATIONAL = "informational"  # Providing additional information


class DebateEvent(Event):
    """
    Base class for events related to the overall debate process.
    
    These events represent debate-level occurrences like starting/ending a debate,
    changing topics, or changing speakers.
    """
    
    TYPE = "debate"
    
    def __init__(
        self, 
        debate_event_type: DebateEventType,
        topic: Optional[str] = None,
        source: Any = None, 
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a debate event.
        
        Args:
            debate_event_type: The specific type of debate event
            topic: The debate topic (if applicable)
            source: The entity that generated the event
            metadata: Additional event-specific data
        """
        super().__init__(
            event_type=self.TYPE,
            source=source,
            metadata=metadata or {}
        )
        self.debate_event_type = debate_event_type
        
        # Add debate-specific metadata
        if topic:
            self.metadata["topic"] = topic
        self.metadata["debate_event_type"] = debate_event_type.value
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, including debate-specific fields."""
        data = super().to_dict()
        data["debate_event_type"] = self.debate_event_type.value
        return data


class SpeechEvent(Event):
    """
    Event representing a speech delivered in the senate.
    
    This event contains the full content of a speech, including both Latin and English
    versions, key points, and the speaker's stance on the topic.
    """
    
    TYPE = "speech"
    
    def __init__(
        self,
        speaker: Dict[str, Any],
        topic: str,
        latin_content: str,
        english_content: str,
        stance: str,
        key_points: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a speech event.
        
        Args:
            speaker: The senator who delivered the speech
            topic: The topic of the speech
            latin_content: The Latin version of the speech
            english_content: The English version of the speech
            stance: The speaker's stance on the topic (support, oppose, neutral)
            key_points: List of key points made in the speech
            metadata: Additional event-specific data
        """
        super().__init__(
            event_type=self.TYPE,
            source=speaker,
            metadata=metadata or {}
        )
        self.speech_id = self.event_id  # Use the event ID as the speech ID
        self.speaker = speaker
        self.latin_content = latin_content
        self.english_content = english_content
        self.stance = stance
        self.key_points = key_points or []
        
        # Add speech-specific metadata
        self.metadata.update({
            "topic": topic,
            "stance": stance,
            "speaker_name": speaker.get("name", "Unknown"),
            "speaker_faction": speaker.get("faction", "Unknown"),
        })
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, including speech-specific fields."""
        data = super().to_dict()
        data.update({
            "speech_id": self.speech_id,
            "latin_content": self.latin_content,
            "english_content": self.english_content,
            "stance": self.stance,
            "key_points": self.key_points,
            "speaker": {
                "id": self.speaker.get("id"),
                "name": self.speaker.get("name"),
                "faction": self.speaker.get("faction")
            }
        })
        return data


class ReactionEvent(Event):
    """
    Event representing a senator's reaction to another event (typically a speech).
    
    Reactions are non-disruptive responses to speeches or other events, such as
    nodding in agreement, frowning, or making quiet comments to neighbors.
    """
    
    TYPE = "reaction"
    
    def __init__(
        self,
        reactor: Dict[str, Any],
        target_event: Event,
        reaction_type: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a reaction event.
        
        Args:
            reactor: The senator who is reacting
            target_event: The event being reacted to
            reaction_type: The type of reaction (e.g., "agreement", "disagreement")
            content: The content of the reaction
            metadata: Additional event-specific data
        """
        super().__init__(
            event_type=self.TYPE,
            source=reactor,
            metadata=metadata or {}
        )
        self.reactor = reactor
        self.target_event_id = target_event.event_id
        self.target_event_type = target_event.event_type
        self.reaction_type = reaction_type
        self.content = content
        
        # Add reaction-specific metadata
        self.metadata.update({
            "reactor_name": reactor.get("name", "Unknown"),
            "reactor_faction": reactor.get("faction", "Unknown"),
            "target_event_id": self.target_event_id,
            "target_event_type": self.target_event_type,
            "reaction_type": reaction_type
        })
        
        # If the target is a speech, add speaker info
        if hasattr(target_event, 'speaker'):
            self.metadata["target_speaker"] = target_event.speaker.get("name", "Unknown")
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, including reaction-specific fields."""
        data = super().to_dict()
        data.update({
            "reactor": {
                "id": self.reactor.get("id"),
                "name": self.reactor.get("name"),
                "faction": self.reactor.get("faction")
            },
            "target_event_id": self.target_event_id,
            "target_event_type": self.target_event_type,
            "reaction_type": self.reaction_type,
            "content": self.content
        })
        return data


class InterjectionEvent(Event):
    """
    Event representing an interjection during a speech.
    
    Interjections are more disruptive than reactions and may interrupt the flow
    of a speech. They include procedural objections, challenges to points made,
    or emotional outbursts.
    """
    
    TYPE = "interjection"
    
    def __init__(
        self,
        interjector: Dict[str, Any],
        target_speaker: Dict[str, Any],
        interjection_type: InterjectionType,
        latin_content: str,
        english_content: str,
        target_speech_id: Optional[str] = None,
        causes_disruption: bool = False,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize an interjection event.
        
        Args:
            interjector: The senator making the interjection
            target_speaker: The senator being interrupted
            interjection_type: The type of interjection
            latin_content: The Latin version of the interjection
            english_content: The English version of the interjection
            target_speech_id: ID of the speech being interrupted (if applicable)
            causes_disruption: Whether this interjection disrupts the debate flow
            metadata: Additional event-specific data
        """
        super().__init__(
            event_type=self.TYPE,
            source=interjector,
            metadata=metadata or {}
        )
        self.interjector = interjector
        self.target_speaker = target_speaker
        self.interjection_type = interjection_type
        self.latin_content = latin_content
        self.english_content = english_content
        self.target_speech_id = target_speech_id
        self.causes_disruption = causes_disruption
        
        # Set priority based on interjector's rank and interjection type
        # Procedural interjections get higher priority
        self.priority = interjector.get("rank", 0)
        if interjection_type == InterjectionType.PROCEDURAL:
            self.priority += 10
        
        # Add interjection-specific metadata
        self.metadata.update({
            "interjector_name": interjector.get("name", "Unknown"),
            "interjector_faction": interjector.get("faction", "Unknown"),
            "target_speaker_name": target_speaker.get("name", "Unknown"),
            "interjection_type": interjection_type.value,
            "causes_disruption": causes_disruption
        })
        if target_speech_id:
            self.metadata["target_speech_id"] = target_speech_id
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, including interjection-specific fields."""
        data = super().to_dict()
        data.update({
            "interjector": {
                "id": self.interjector.get("id"),
                "name": self.interjector.get("name"),
                "faction": self.interjector.get("faction")
            },
            "target_speaker": {
                "id": self.target_speaker.get("id"),
                "name": self.target_speaker.get("name"),
                "faction": self.target_speaker.get("faction")
            },
            "interjection_type": self.interjection_type.value,
            "latin_content": self.latin_content,
            "english_content": self.english_content,
            "causes_disruption": self.causes_disruption
        })
        if self.target_speech_id:
            data["target_speech_id"] = self.target_speech_id
        return data