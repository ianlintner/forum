"""
Debate Event Manager for Roman Senate.

This module provides the orchestration logic for debate events in the Roman Senate simulation.
It manages the flow of debate events, tracks active debates, and coordinates interactions
between debate participants.

Part of the Migration Plan: Phase 1 - Core Event System.
"""

from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple, Any

from agentic_game_framework.events.event_bus import EventBus
from .base import BaseEvent, EventHandler, RomanEvent
from .debate_events import (
    DebateStartedEvent,
    DebateEndedEvent,
    SpeechStartedEvent,
    SpeechEndedEvent,
    InterjectionEvent,
    VoteRequestedEvent,
    DebateTopicChangedEvent
)


class DebateSession:
    """
    Represents an active debate session.
    
    Tracks the state of a single debate, including its topic, participants,
    current speaker, and relevant statistics.
    
    Attributes:
        topic (str): The current topic of debate
        initiator (str): The senator who initiated the debate
        participants (Set[str]): Set of participating senators
        start_time (datetime): When the debate began
        current_speaker (Optional[str]): Currently speaking senator, if any
        speech_start_time (Optional[datetime]): When current speech began, if applicable
    """
    
    def __init__(self, topic: str, initiator: str, participants: Optional[List[str]] = None):
        """
        Initialize a new debate session.
        
        Args:
            topic: The debate topic
            initiator: Senator who initiated the debate
            participants: Initial list of participating senators (optional)
        """
        self.topic = topic
        self.initiator = initiator
        # Always add initiator to participants, regardless of whether it's in the provided list
        self.participants = set(participants or []) | {initiator}
        self.start_time = datetime.now()
        self.current_speaker: Optional[str] = None
        self.speech_start_time: Optional[datetime] = None
        self.speeches_delivered: Dict[str, int] = {}  # Senator -> count of speeches
        self.interjections: List[Tuple[str, str, str]] = []  # (speaker, target, type)
        self.is_active = True
    
    def add_participant(self, senator: str) -> None:
        """
        Add a senator to the debate.
        
        Args:
            senator: The senator to add
        """
        self.participants.add(senator)
    
    def remove_participant(self, senator: str) -> None:
        """
        Remove a senator from the debate.
        
        Args:
            senator: The senator to remove
        """
        if senator in self.participants:
            self.participants.remove(senator)
    
    def start_speech(self, senator: str) -> None:
        """
        Record that a senator has started speaking.
        
        Args:
            senator: The speaking senator
        """
        self.current_speaker = senator
        self.speech_start_time = datetime.now()
        
        # Add to participants if not already present
        self.participants.add(senator)
    
    def end_speech(self, senator: str) -> Optional[int]:
        """
        Record that a senator has finished speaking.
        
        Args:
            senator: The senator who was speaking
            
        Returns:
            int: Duration of the speech in minutes, if available
        """
        duration_minutes = None
        
        # Calculate speech duration
        if self.speech_start_time and self.current_speaker == senator:
            duration = datetime.now() - self.speech_start_time
            duration_minutes = int(duration.total_seconds() / 60)
        
        # Update speech count for this senator
        self.speeches_delivered[senator] = self.speeches_delivered.get(senator, 0) + 1
        
        # Clear current speaker
        self.current_speaker = None
        self.speech_start_time = None
        
        return duration_minutes
    
    def record_interjection(self, speaker: str, target: str, content_type: str) -> None:
        """
        Record an interjection during the debate.
        
        Args:
            speaker: Senator making the interjection
            target: Senator being interrupted
            content_type: Type of interjection (e.g., 'question', 'objection')
        """
        self.interjections.append((speaker, target, content_type))
        
        # Add interjector to participants if not already present
        self.participants.add(speaker)
    
    def change_topic(self, new_topic: str) -> None:
        """
        Change the debate topic.
        
        Args:
            new_topic: The new topic for the debate
        """
        self.topic = new_topic
    
    def end_debate(self) -> Dict[str, Any]:
        """
        End the debate and return summary statistics.
        
        Returns:
            Dict[str, Any]: Summary statistics about the debate
        """
        self.is_active = False
        duration = datetime.now() - self.start_time
        duration_minutes = int(duration.total_seconds() / 60)
        
        return {
            "topic": self.topic,
            "initiator": self.initiator,
            "participants": list(self.participants),
            "duration_minutes": duration_minutes,
            "speech_count": sum(self.speeches_delivered.values()),
            "interjection_count": len(self.interjections),
            "most_active_speaker": max(self.speeches_delivered.items(), key=lambda x: x[1])[0] if self.speeches_delivered else None,
        }


class DebateManager(EventHandler):
    """
    Manages debate sessions and coordinates debate-related events.
    
    The DebateManager maintains the state of all active debates, processes
    debate-related events, and orchestrates the flow of the debate process.
    """
    
    def __init__(self, event_bus: EventBus):
        """
        Initialize the debate manager.
        
        Args:
            event_bus: The event bus to publish and subscribe to events
        """
        self.event_bus = event_bus
        self.active_debates: Dict[str, DebateSession] = {}  # topic -> debate
        
        # Subscribe to relevant event types
        self._subscribe_to_events()
    
    def _subscribe_to_events(self) -> None:
        """Subscribe to debate-related event types."""
        self.event_bus.subscribe("DEBATE_STARTED", self)
        self.event_bus.subscribe("DEBATE_ENDED", self)
        self.event_bus.subscribe("SPEECH_STARTED", self)
        self.event_bus.subscribe("SPEECH_ENDED", self)
        self.event_bus.subscribe("INTERJECTION", self)
        self.event_bus.subscribe("VOTE_REQUESTED", self)
        self.event_bus.subscribe("TOPIC_CHANGED", self)
    
    def handle_event(self, event: BaseEvent) -> None:
        """
        Process debate-related events.
        
        Args:
            event: The event to process
        """
        # Route to appropriate handler based on event type
        if event.event_type == "DEBATE_STARTED":
            self._handle_debate_started(event)
        elif event.event_type == "DEBATE_ENDED":
            self._handle_debate_ended(event)
        elif event.event_type == "SPEECH_STARTED":
            self._handle_speech_started(event)
        elif event.event_type == "SPEECH_ENDED":
            self._handle_speech_ended(event)
        elif event.event_type == "INTERJECTION":
            self._handle_interjection(event)
        elif event.event_type == "VOTE_REQUESTED":
            self._handle_vote_requested(event)
        elif event.event_type == "TOPIC_CHANGED":
            self._handle_topic_changed(event)
    
    def _handle_debate_started(self, event: DebateStartedEvent) -> None:
        """Handle the start of a new debate."""
        topic = event.topic
        initiator = event.initiator
        participants = event.participants
        
        # Create new debate session
        debate = DebateSession(topic, initiator, participants)
        self.active_debates[topic] = debate
    
    def _handle_debate_ended(self, event: DebateEndedEvent) -> None:
        """Handle the end of a debate."""
        topic = event.topic
        
        # Remove debate from active list
        if topic in self.active_debates:
            debate = self.active_debates.pop(topic)
            debate.end_debate()
    
    def _handle_speech_started(self, event: SpeechStartedEvent) -> None:
        """Handle the start of a speech."""
        speaker = event.speaker
        topic = event.topic
        
        # Update the debate session if it exists
        if topic in self.active_debates:
            debate = self.active_debates[topic]
            debate.start_speech(speaker)
    
    def _handle_speech_ended(self, event: SpeechEndedEvent) -> None:
        """Handle the end of a speech."""
        speaker = event.speaker
        topic = event.topic
        
        # Update the debate session if it exists
        if topic in self.active_debates:
            debate = self.active_debates[topic]
            debate.end_speech(speaker)
    
    def _handle_interjection(self, event: InterjectionEvent) -> None:
        """Handle an interjection during a speech."""
        speaker = event.speaker
        target_speaker = event.target_speaker
        content_type = event.content_type
        
        # Find the debate where the target speaker is speaking
        for topic, debate in self.active_debates.items():
            if debate.current_speaker == target_speaker:
                debate.record_interjection(speaker, target_speaker, content_type)
                break
    
    def _handle_vote_requested(self, event: VoteRequestedEvent) -> None:
        """Handle a request for a vote during a debate."""
        # This could trigger a voting process, but for now we just acknowledge it
        pass
    
    def _handle_topic_changed(self, event: DebateTopicChangedEvent) -> None:
        """Handle a change in debate topic."""
        old_topic = event.old_topic
        new_topic = event.new_topic
        
        # Update the debate session if it exists
        if old_topic in self.active_debates:
            debate = self.active_debates[old_topic]
            debate.change_topic(new_topic)
            
            # Update the active_debates dictionary
            self.active_debates[new_topic] = debate
            del self.active_debates[old_topic]
    
    # Methods to start new debates and manage existing ones
    
    def start_debate(self, topic: str, initiator: str, participants: Optional[List[str]] = None) -> None:
        """
        Start a new debate session.
        
        Args:
            topic: The debate topic
            initiator: Senator initiating the debate
            participants: Initial list of participating senators (optional)
        """
        # Create and publish a DebateStartedEvent
        event = DebateStartedEvent(
            topic=topic,
            initiator=initiator,
            participants=participants,
            source="DebateManager"
        )
        self.event_bus.publish(event)
        
        # The debate session will be created when the event is handled
    
    def end_debate(self, topic: str, outcome: Optional[str] = None) -> None:
        """
        End an active debate session.
        
        Args:
            topic: The topic of the debate to end
            outcome: Result or outcome of the debate (optional)
        """
        # Get the debate session
        if topic not in self.active_debates:
            return
            
        debate = self.active_debates[topic]
        stats = debate.end_debate()
        
        # Create and publish a DebateEndedEvent
        event = DebateEndedEvent(
            topic=topic,
            outcome=outcome,
            duration_minutes=stats.get("duration_minutes"),
            source="DebateManager",
            data=stats
        )
        self.event_bus.publish(event)
        
        # The debate session will be removed when the event is handled
    
    def is_debate_active(self, topic: str) -> bool:
        """
        Check if a debate is currently active.
        
        Args:
            topic: The debate topic to check
            
        Returns:
            bool: True if the debate is active, False otherwise
        """
        return topic in self.active_debates and self.active_debates[topic].is_active
    
    def get_active_debates(self) -> List[str]:
        """
        Get a list of all active debate topics.
        
        Returns:
            List[str]: List of active debate topics
        """
        return list(self.active_debates.keys())
    
    def get_debate_participants(self, topic: str) -> Optional[List[str]]:
        """
        Get the list of participants in a debate.
        
        Args:
            topic: The debate topic
            
        Returns:
            Optional[List[str]]: List of participants, or None if debate not found
        """
        if topic in self.active_debates:
            return list(self.active_debates[topic].participants)
        return None
    
    def get_current_speaker(self, topic: str) -> Optional[str]:
        """
        Get the current speaker in a debate.
        
        Args:
            topic: The debate topic
            
        Returns:
            Optional[str]: Current speaker's identifier, or None if no active speaker
        """
        if topic in self.active_debates:
            return self.active_debates[topic].current_speaker
        return None