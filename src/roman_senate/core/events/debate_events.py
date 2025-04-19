"""
Debate Events for Roman Senate.

This module defines debate-specific event types that build on the base event system.
These events represent actions and state changes that occur during Senate debates.

Part of the Migration Plan: Phase 1 - Core Event System.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from .base import BaseEvent, RomanEvent


class DebateStartedEvent(RomanEvent):
    """
    Event emitted when a debate session begins.
    
    Attributes:
        topic (str): The main topic of the debate
        initiator (str): Senator or official who initiated the debate
        participants (List[str]): Initial list of participating senators
    """
    
    def __init__(
        self,
        topic: str,
        initiator: str,
        participants: Optional[List[str]] = None,
        source: Optional[str] = None,
        target: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None,
        event_id: Optional[str] = None
    ):
        """
        Initialize a new DebateStartedEvent.
        
        Args:
            topic: Main topic of the debate
            initiator: Senator or official who initiated the debate
            participants: Initial list of participating senators (optional)
            source: Component that generated this event
            target: Intended recipient (if any)
            data: Additional event data
            timestamp: Event creation time (defaults to now)
            event_id: Unique event identifier (generated if not provided)
        """
        # Prepare event data
        event_data = data or {}
        event_data.update({
            "topic": topic,
            "initiator": initiator,
            "participants": participants or []
        })
        
        super().__init__(
            event_type="DEBATE_STARTED",
            source=source,
            target=target,
            data=event_data,
            timestamp=timestamp,
            event_id=event_id
        )
    
    @property
    def topic(self) -> str:
        """Get the debate topic."""
        return self.data["topic"]
    
    @property
    def initiator(self) -> str:
        """Get the debate initiator."""
        return self.data["initiator"]
    
    @property
    def participants(self) -> List[str]:
        """Get the list of debate participants."""
        return self.data["participants"]


class DebateEndedEvent(RomanEvent):
    """
    Event emitted when a debate session concludes.
    
    Attributes:
        topic (str): The topic of the debate that ended
        outcome (str): Result or outcome of the debate, if any
        duration_minutes (int): How long the debate lasted
    """
    
    def __init__(
        self,
        topic: str,
        outcome: Optional[str] = None,
        duration_minutes: Optional[int] = None,
        source: Optional[str] = None,
        target: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None,
        event_id: Optional[str] = None
    ):
        """
        Initialize a new DebateEndedEvent.
        
        Args:
            topic: Topic of the debate that ended
            outcome: Result or outcome of the debate (optional)
            duration_minutes: How long the debate lasted (optional)
            source: Component that generated this event
            target: Intended recipient (if any)
            data: Additional event data
            timestamp: Event creation time (defaults to now)
            event_id: Unique event identifier (generated if not provided)
        """
        # Prepare event data
        event_data = data or {}
        event_data.update({
            "topic": topic,
            "outcome": outcome,
            "duration_minutes": duration_minutes
        })
        
        super().__init__(
            event_type="DEBATE_ENDED",
            source=source,
            target=target,
            data=event_data,
            timestamp=timestamp,
            event_id=event_id
        )
    
    @property
    def topic(self) -> str:
        """Get the debate topic."""
        return self.data["topic"]
    
    @property
    def outcome(self) -> Optional[str]:
        """Get the debate outcome, if available."""
        return self.data.get("outcome")
    
    @property
    def duration_minutes(self) -> Optional[int]:
        """Get the debate duration in minutes, if available."""
        return self.data.get("duration_minutes")


class SpeechStartedEvent(RomanEvent):
    """
    Event emitted when a senator begins a speech.
    
    Attributes:
        speaker (str): The senator delivering the speech
        topic (str): Topic of the speech
        position (Optional[str]): The speaker's position on the topic
    """
    
    def __init__(
        self,
        speaker: str,
        topic: str,
        position: Optional[str] = None,
        source: Optional[str] = None,
        target: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None,
        event_id: Optional[str] = None
    ):
        """
        Initialize a new SpeechStartedEvent.
        
        Args:
            speaker: The senator delivering the speech
            topic: Topic of the speech
            position: The speaker's position on the topic (optional)
            source: Component that generated this event
            target: Intended recipient (if any)
            data: Additional event data
            timestamp: Event creation time (defaults to now)
            event_id: Unique event identifier (generated if not provided)
        """
        # Prepare event data
        event_data = data or {}
        event_data.update({
            "speaker": speaker,
            "topic": topic,
            "position": position
        })
        
        super().__init__(
            event_type="SPEECH_STARTED",
            source=source,
            target=target,
            data=event_data,
            timestamp=timestamp,
            event_id=event_id
        )
    
    @property
    def speaker(self) -> str:
        """Get the speech speaker."""
        return self.data["speaker"]
    
    @property
    def topic(self) -> str:
        """Get the speech topic."""
        return self.data["topic"]
    
    @property
    def position(self) -> Optional[str]:
        """Get the speaker's position, if available."""
        return self.data.get("position")


class SpeechEndedEvent(RomanEvent):
    """
    Event emitted when a senator concludes a speech.
    
    Attributes:
        speaker (str): The senator who delivered the speech
        topic (str): Topic of the speech
        duration_minutes (Optional[int]): How long the speech lasted
        impact (Optional[float]): Measure of impact on the audience (0-1)
    """
    
    def __init__(
        self,
        speaker: str,
        topic: str,
        duration_minutes: Optional[int] = None,
        impact: Optional[float] = None,
        source: Optional[str] = None,
        target: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None,
        event_id: Optional[str] = None
    ):
        """
        Initialize a new SpeechEndedEvent.
        
        Args:
            speaker: The senator who delivered the speech
            topic: Topic of the speech
            duration_minutes: How long the speech lasted (optional)
            impact: Measure of impact on the audience, 0-1 (optional)
            source: Component that generated this event
            target: Intended recipient (if any)
            data: Additional event data
            timestamp: Event creation time (defaults to now)
            event_id: Unique event identifier (generated if not provided)
        """
        # Prepare event data
        event_data = data or {}
        event_data.update({
            "speaker": speaker,
            "topic": topic,
            "duration_minutes": duration_minutes,
            "impact": impact
        })
        
        super().__init__(
            event_type="SPEECH_ENDED",
            source=source,
            target=target,
            data=event_data,
            timestamp=timestamp,
            event_id=event_id
        )
    
    @property
    def speaker(self) -> str:
        """Get the speech speaker."""
        return self.data["speaker"]
    
    @property
    def topic(self) -> str:
        """Get the speech topic."""
        return self.data["topic"]
    
    @property
    def duration_minutes(self) -> Optional[int]:
        """Get the speech duration in minutes, if available."""
        return self.data.get("duration_minutes")
    
    @property
    def impact(self) -> Optional[float]:
        """Get the speech impact score, if available."""
        return self.data.get("impact")


class InterjectionEvent(RomanEvent):
    """
    Event emitted when a senator interjects during another's speech.
    
    Attributes:
        speaker (str): The senator delivering the interjection
        target_speaker (str): The senator being interrupted
        content_type (str): Type of interjection (e.g., 'question', 'objection', 'support')
    """
    
    def __init__(
        self,
        speaker: str,
        target_speaker: str,
        content_type: str,
        source: Optional[str] = None,
        target: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None,
        event_id: Optional[str] = None
    ):
        """
        Initialize a new InterjectionEvent.
        
        Args:
            speaker: The senator delivering the interjection
            target_speaker: The senator being interrupted
            content_type: Type of interjection (e.g., 'question', 'objection', 'support')
            source: Component that generated this event
            target: Intended recipient (if any)
            data: Additional event data
            timestamp: Event creation time (defaults to now)
            event_id: Unique event identifier (generated if not provided)
        """
        # Prepare event data
        event_data = data or {}
        event_data.update({
            "speaker": speaker,
            "target_speaker": target_speaker,
            "content_type": content_type
        })
        
        super().__init__(
            event_type="INTERJECTION",
            source=source,
            target=target,
            data=event_data,
            timestamp=timestamp,
            event_id=event_id
        )
    
    @property
    def speaker(self) -> str:
        """Get the interjection speaker."""
        return self.data["speaker"]
    
    @property
    def target_speaker(self) -> str:
        """Get the senator being interrupted."""
        return self.data["target_speaker"]
    
    @property
    def content_type(self) -> str:
        """Get the type of interjection."""
        return self.data["content_type"]


class VoteRequestedEvent(RomanEvent):
    """
    Event emitted when a vote is called for during a debate.
    
    Attributes:
        topic (str): Issue being voted on
        requester (str): Senator requesting the vote
        vote_type (str): Type of vote (e.g., 'voice', 'division', 'ballot')
    """
    
    def __init__(
        self,
        topic: str,
        requester: str,
        vote_type: str,
        source: Optional[str] = None,
        target: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None,
        event_id: Optional[str] = None
    ):
        """
        Initialize a new VoteRequestedEvent.
        
        Args:
            topic: Issue being voted on
            requester: Senator requesting the vote
            vote_type: Type of vote (e.g., 'voice', 'division', 'ballot')
            source: Component that generated this event
            target: Intended recipient (if any)
            data: Additional event data
            timestamp: Event creation time (defaults to now)
            event_id: Unique event identifier (generated if not provided)
        """
        # Prepare event data
        event_data = data or {}
        event_data.update({
            "topic": topic,
            "requester": requester,
            "vote_type": vote_type
        })
        
        super().__init__(
            event_type="VOTE_REQUESTED",
            source=source,
            target=target,
            data=event_data,
            timestamp=timestamp,
            event_id=event_id
        )
    
    @property
    def topic(self) -> str:
        """Get the voting topic."""
        return self.data["topic"]
    
    @property
    def requester(self) -> str:
        """Get the senator requesting the vote."""
        return self.data["requester"]
    
    @property
    def vote_type(self) -> str:
        """Get the type of vote."""
        return self.data["vote_type"]


class DebateTopicChangedEvent(RomanEvent):
    """
    Event emitted when the topic of a debate changes.
    
    Attributes:
        old_topic (str): Previous debate topic
        new_topic (str): New debate topic
        initiator (str): Senator who changed the topic
    """
    
    def __init__(
        self,
        old_topic: str,
        new_topic: str,
        initiator: str,
        source: Optional[str] = None,
        target: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None,
        event_id: Optional[str] = None
    ):
        """
        Initialize a new DebateTopicChangedEvent.
        
        Args:
            old_topic: Previous debate topic
            new_topic: New debate topic
            initiator: Senator who changed the topic
            source: Component that generated this event
            target: Intended recipient (if any)
            data: Additional event data
            timestamp: Event creation time (defaults to now)
            event_id: Unique event identifier (generated if not provided)
        """
        # Prepare event data
        event_data = data or {}
        event_data.update({
            "old_topic": old_topic,
            "new_topic": new_topic,
            "initiator": initiator
        })
        
        super().__init__(
            event_type="TOPIC_CHANGED",
            source=source,
            target=target,
            data=event_data,
            timestamp=timestamp,
            event_id=event_id
        )
    
    @property
    def old_topic(self) -> str:
        """Get the previous debate topic."""
        return self.data["old_topic"]
    
    @property
    def new_topic(self) -> str:
        """Get the new debate topic."""
        return self.data["new_topic"]
    
    @property
    def initiator(self) -> str:
        """Get the senator who changed the topic."""
        return self.data["initiator"]