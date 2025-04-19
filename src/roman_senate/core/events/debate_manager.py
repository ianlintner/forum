"""
Roman Senate Simulation
Debate Manager Module

This module provides the DebateManager class, which coordinates debates using
the event-driven architecture.
"""

import asyncio
import logging
import random
from typing import Any, Dict, List, Optional, Tuple

from ..debate import display_speech, add_to_debate_history
from .base import Event
from .event_bus import EventBus
from .debate_events import (
    DebateEvent, 
    DebateEventType,
    SpeechEvent, 
    ReactionEvent, 
    InterjectionEvent,
    InterjectionType
)

logger = logging.getLogger(__name__)

class DebateManager:
    """
    Manages the debate process using the event-driven architecture.
    
    This class is responsible for:
    1. Coordinating the debate flow
    2. Publishing debate events
    3. Handling interruptions and reactions
    4. Integrating with the existing debate system
    """
    
    def __init__(self, event_bus: EventBus, game_state: Any):
        """
        Initialize the debate manager.
        
        Args:
            event_bus: The event bus to use for publishing events
            game_state: The current game state
        """
        self.event_bus = event_bus
        self.game_state = game_state
        self.current_debate_topic = None
        self.current_speaker = None
        self.registered_speakers = []
        self.debate_in_progress = False
        
        # Subscribe to relevant event types
        self.event_bus.subscribe(InterjectionEvent.TYPE, self.handle_interjection)
        self.event_bus.subscribe(ReactionEvent.TYPE, self.handle_reaction)
        
    async def start_debate(self, topic: str, senators: List[Dict[str, Any]]) -> None:
        """
        Start a new debate on the given topic.
        
        Args:
            topic: The topic to debate
            senators: List of senators participating in the debate
        """
        if self.debate_in_progress:
            logger.warning("Attempt to start debate while another is in progress")
            return
            
        self.debate_in_progress = True
        self.current_debate_topic = topic
        self.registered_speakers = senators.copy()
        
        # Publish debate start event
        debate_start_event = DebateEvent(
            debate_event_type=DebateEventType.DEBATE_START,
            topic=topic,
            metadata={
                "participant_count": len(senators),
                "participants": [s.get("name", "Unknown") for s in senators]
            }
        )
        await self.event_bus.publish(debate_start_event)
        
        logger.info(f"Debate started on topic: {topic} with {len(senators)} participants")
        
    async def end_debate(self) -> None:
        """End the current debate."""
        if not self.debate_in_progress:
            logger.warning("Attempt to end debate when none is in progress")
            return
            
        # Publish debate end event
        debate_end_event = DebateEvent(
            debate_event_type=DebateEventType.DEBATE_END,
            topic=self.current_debate_topic,
            metadata={
                "duration": "unknown",  # Could track actual duration if needed
                "participant_count": len(self.registered_speakers)
            }
        )
        await self.event_bus.publish(debate_end_event)
        
        # Reset debate state
        self.debate_in_progress = False
        self.current_debate_topic = None
        self.current_speaker = None
        self.registered_speakers = []
        
        logger.info("Debate ended")
        
    async def register_speaker(self, senator: Dict[str, Any]) -> None:
        """
        Register a senator to speak in the debate.
        
        Args:
            senator: The senator to register
        """
        if senator not in self.registered_speakers:
            self.registered_speakers.append(senator)
            logger.debug(f"Registered speaker: {senator.get('name', 'Unknown')}")
            
    async def next_speaker(self) -> Optional[Dict[str, Any]]:
        """
        Get the next speaker in the debate.
        
        Returns:
            The next senator to speak, or None if no more speakers
        """
        if not self.registered_speakers:
            return None
            
        # Get the next speaker
        next_speaker = self.registered_speakers.pop(0)
        self.current_speaker = next_speaker
        
        # Publish speaker change event
        speaker_change_event = DebateEvent(
            debate_event_type=DebateEventType.SPEAKER_CHANGE,
            topic=self.current_debate_topic,
            source=next_speaker,
            metadata={
                "speaker_name": next_speaker.get("name", "Unknown"),
                "speaker_faction": next_speaker.get("faction", "Unknown")
            }
        )
        await self.event_bus.publish(speaker_change_event)
        
        return next_speaker
        
    async def publish_speech(
        self, 
        speaker: Dict[str, Any], 
        topic: str, 
        latin_content: str, 
        english_content: str, 
        stance: str,
        key_points: Optional[List[str]] = None
    ) -> SpeechEvent:
        """
        Publish a speech event.
        
        Args:
            speaker: The senator giving the speech
            topic: The topic of the speech
            latin_content: The Latin version of the speech
            english_content: The English version of the speech
            stance: The speaker's stance on the topic
            key_points: Key points made in the speech
            
        Returns:
            The published speech event
        """
        # Create speech event
        speech_event = SpeechEvent(
            speaker=speaker,
            topic=topic,
            latin_content=latin_content,
            english_content=english_content,
            stance=stance,
            key_points=key_points
        )
        
        # Publish the event
        await self.event_bus.publish(speech_event)
        
        # Add to debate history (for backward compatibility)
        speech_data = {
            "senator_id": speaker.get("id"),
            "senator_name": speaker.get("name"),
            "faction": speaker.get("faction"),
            "stance": stance,
            "speech": f"---LATIN---\n{latin_content}\n---ENGLISH---\n{english_content}",
            "key_points": key_points or []
        }
        add_to_debate_history(speech_data)
        
        return speech_event
        
    async def handle_interjection(self, event: InterjectionEvent) -> None:
        """
        Handle an interjection event.
        
        Args:
            event: The interjection event
        """
        if not self.debate_in_progress or not self.current_speaker:
            logger.warning("Interjection received but no debate in progress")
            return
            
        # Check if the interjection should be allowed based on rank
        interjector_rank = event.interjector.get("rank", 0)
        speaker_rank = self.current_speaker.get("rank", 0)
        
        # Higher rank can always interrupt
        allow_interruption = interjector_rank > speaker_rank
        
        # Equal rank can interrupt for procedural matters
        if interjector_rank == speaker_rank and event.interjection_type == InterjectionType.PROCEDURAL:
            allow_interruption = True
            
        # Log the interjection
        logger.info(
            f"Interjection from {event.interjector.get('name')}: "
            f"{event.interjection_type.value} - Allowed: {allow_interruption}"
        )
        
        # If allowed, display the interjection
        if allow_interruption:
            # Display the interjection (this would integrate with the UI)
            # For now, we'll just log it
            logger.info(f"INTERJECTION: {event.english_content}")
            
            # In a real implementation, this would pause the current speech
            # and display the interjection to the user
            
    async def handle_reaction(self, event: ReactionEvent) -> None:
        """
        Handle a reaction event.
        
        Args:
            event: The reaction event
        """
        if not self.debate_in_progress:
            logger.warning("Reaction received but no debate in progress")
            return
            
        # Log the reaction
        logger.info(
            f"Reaction from {event.reactor.get('name')}: "
            f"{event.reaction_type} - {event.content}"
        )
        
        # In a real implementation, this would update the UI to show
        # the reaction, but wouldn't interrupt the current speech
        
    async def conduct_debate(
        self, 
        topic: str, 
        senators: List[Dict[str, Any]], 
        environment: Any = None
    ) -> List[Dict[str, Any]]:
        """
        Conduct a full debate on the given topic.
        
        This method integrates with the existing debate system while using
        the new event-driven architecture.
        
        Args:
            topic: The topic to debate
            senators: List of senators participating in the debate
            environment: The environment object (for backward compatibility)
            
        Returns:
            List of speech data dictionaries
        """
        # Start the debate
        await self.start_debate(topic, senators)
        
        # Track all speeches for return value
        all_speeches = []
        
        # Let each senator speak
        for senator in senators:
            # Set as current speaker
            self.current_speaker = senator
            await self.next_speaker()
            
            # Generate the speech (this would normally call the senator agent)
            # For now, we'll create a placeholder
            latin_content = f"Latin speech by {senator.get('name')} on {topic}"
            english_content = f"English speech by {senator.get('name')} on {topic}"
            stance = random.choice(["support", "oppose", "neutral"])
            
            # Create speech data for backward compatibility
            speech_data = {
                "senator_id": senator.get("id"),
                "senator_name": senator.get("name"),
                "faction": senator.get("faction"),
                "stance": stance,
                "speech": f"---LATIN---\n{latin_content}\n---ENGLISH---\n{english_content}",
                "key_points": []
            }
            
            # Publish the speech event
            speech_event = await self.publish_speech(
                speaker=senator,
                topic=topic,
                latin_content=latin_content,
                english_content=english_content,
                stance=stance
            )
            
            # Display the speech (for backward compatibility)
            display_speech(senator, speech_data, topic)
            
            # Add to return value
            all_speeches.append(speech_data)
            
            # Pause to allow reactions and interjections
            await asyncio.sleep(1)
            
        # End the debate
        await self.end_debate()
        
        return all_speeches