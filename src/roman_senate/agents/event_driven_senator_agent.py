"""
Roman Senate AI Game
Event-Driven Senator Agent Module

This module extends the SenatorAgent class with event-driven capabilities,
allowing senators to observe, listen to, and react to events in their environment.
"""

import asyncio
import logging
import random
from typing import Dict, List, Optional, Tuple, Any, Union

from ..utils.llm.base import LLMProvider
from ..core.interjection import Interjection, InterjectionTiming, generate_fallback_interjection
from .agent_memory import AgentMemory
from .event_memory import EventMemory
from .senator_agent import SenatorAgent
from ..core.events import (
    Event, 
    EventBus, 
    SpeechEvent, 
    DebateEvent,
    DebateEventType,
    ReactionEvent,
    InterjectionEvent,
    InterjectionType
)

logger = logging.getLogger(__name__)

class EventDrivenSenatorAgent(SenatorAgent):
    """
    Event-driven implementation of a Roman Senator agent.
    
    This class extends the base SenatorAgent with event-driven capabilities,
    allowing senators to subscribe to events, process them, and react accordingly.
    """
    
    def __init__(self, senator: Dict[str, Any], llm_provider: LLMProvider, event_bus: EventBus):
        """
        Initialize an event-driven senator agent.
        
        Args:
            senator: The senator dictionary with properties like name, faction, etc.
            llm_provider: The LLM provider to use for generating responses
            event_bus: The event bus to use for subscribing to and publishing events
        """
        # Initialize with base senator properties but replace memory with EventMemory
        self.senator = senator
        self.llm_provider = llm_provider
        self.current_stance = None
        
        # Use enhanced event memory instead of basic agent memory
        self.memory = EventMemory()
        
        self.event_bus = event_bus
        self.active_debate_topic = None
        self.current_speaker = None
        self.debate_in_progress = False
        
        # Subscribe to relevant event types
        self.subscribe_to_events()
        
    def subscribe_to_events(self) -> None:
        """Subscribe to relevant event types."""
        self.event_bus.subscribe(SpeechEvent.TYPE, self.handle_speech_event)
        self.event_bus.subscribe(DebateEvent.TYPE, self.handle_debate_event)
        logger.debug(f"Senator {self.name} subscribed to events")
        
    async def handle_speech_event(self, event: SpeechEvent) -> None:
        """
        Handle a speech event.
        
        Args:
            event: The speech event to process
        """
        # Skip own speeches
        if event.speaker.get("id") == self.senator.get("id"):
            return
            
        # Record the event in memory
        self.memory.record_event(event)
        
        # Record interaction with the speaker
        self.memory.add_interaction(
            event.speaker.get("name"),
            "heard_speech",
            {
                "topic": event.metadata.get("topic"),
                "stance": event.stance,
                "speech_id": event.speech_id
            }
        )
        
        # Store current speaker for potential reactions
        self.current_speaker = event.speaker
        
        # Determine if senator should react to the speech
        if await self._should_react_to_speech(event):
            # Generate and publish reaction
            await self._generate_and_publish_reaction(event)
            
        # Determine if senator should interject
        if await self._should_interject(event):
            # Generate and publish interjection
            await self._generate_and_publish_interjection(event)
            
        # Check if stance should change based on speech
        await self._consider_stance_change(event)
            
    async def handle_debate_event(self, event: DebateEvent) -> None:
        """
        Handle a debate event.
        
        Args:
            event: The debate event to process
        """
        # Record the event in memory
        self.memory.record_event(event)
        
        if event.debate_event_type == DebateEventType.DEBATE_START:
            self.debate_in_progress = True
            self.active_debate_topic = event.metadata.get("topic")
            logger.debug(f"Senator {self.name} noticed debate start on {self.active_debate_topic}")
            
            # If we don't have a stance on this topic yet, decide one
            if not self.current_stance and self.active_debate_topic:
                await self.decide_stance(self.active_debate_topic, {})
            
        elif event.debate_event_type == DebateEventType.DEBATE_END:
            self.debate_in_progress = False
            self.active_debate_topic = None
            self.current_speaker = None
            logger.debug(f"Senator {self.name} noticed debate end")
            
        elif event.debate_event_type == DebateEventType.SPEAKER_CHANGE:
            self.current_speaker = event.source
            logger.debug(f"Senator {self.name} noticed speaker change to {event.metadata.get('speaker_name')}")
            
    async def _should_react_to_speech(self, event: SpeechEvent) -> bool:
        """
        Determine if the senator should react to a speech.
        
        Args:
            event: The speech event
            
        Returns:
            True if the senator should react, False otherwise
        """
        # Base probability of reaction
        base_probability = 0.3  # 30% chance by default
        
        # Adjust based on relationship with speaker
        relationship = self.memory.relationship_scores.get(event.speaker.get("name", ""), 0)
        relationship_factor = abs(relationship) * 0.2  # Max +/- 0.2
        
        # Faction alignment affects reaction probability
        speaker_faction = event.speaker.get("faction", "")
        if speaker_faction == self.faction:
            # More likely to react positively to same faction
            if relationship >= 0:
                base_probability += 0.1
        else:
            # More likely to react negatively to different faction
            if relationship < 0:
                base_probability += 0.1
                
        # Topic interest affects reaction probability
        # This would be more sophisticated in a real implementation
        topic_interest = random.random() * 0.3  # Random interest level
        
        # Calculate final probability
        final_probability = min(0.8, base_probability + relationship_factor + topic_interest)
        
        # Decide whether to react
        return random.random() < final_probability
        
    async def _should_interject(self, event: SpeechEvent) -> bool:
        """
        Determine if the senator should interject during a speech.
        
        Args:
            event: The speech event
            
        Returns:
            True if the senator should interject, False otherwise
        """
        # Base probability of interjection (lower than reaction)
        base_probability = 0.1  # 10% chance by default
        
        # Adjust based on relationship with speaker (stronger feelings = more likely to interject)
        relationship = self.memory.relationship_scores.get(event.speaker.get("name", ""), 0)
        relationship_factor = abs(relationship) * 0.15  # Max +/- 0.15
        
        # Rank affects interjection probability
        # Higher rank senators are more likely to interject
        rank = self.senator.get("rank", 0)
        rank_factor = min(0.2, rank * 0.05)  # Max +0.2 for rank 4+
        
        # Stance disagreement increases interjection probability
        stance_factor = 0
        if self.current_stance and self.current_stance != event.stance:
            stance_factor = 0.15
            
        # Calculate final probability
        final_probability = min(0.5, base_probability + relationship_factor + rank_factor + stance_factor)
        
        # Decide whether to interject
        return random.random() < final_probability
        
    async def _generate_and_publish_reaction(self, event: SpeechEvent) -> None:
        """
        Generate and publish a reaction to a speech.
        
        Args:
            event: The speech event to react to
        """
        # Determine reaction type based on relationship and stance
        relationship = self.memory.relationship_scores.get(event.speaker.get("name", ""), 0)
        stance_agreement = (self.current_stance == event.stance)
        
        reaction_types = ["neutral", "agreement", "disagreement", "interest", "boredom", "skepticism"]
        
        if relationship > 0.3 and stance_agreement:
            reaction_type = random.choice(["agreement", "interest"])
        elif relationship < -0.3 and not stance_agreement:
            reaction_type = random.choice(["disagreement", "skepticism"])
        else:
            reaction_type = random.choice(reaction_types)
            
        # Generate reaction content
        reaction_content = await self._generate_reaction_content(event, reaction_type)
        
        # Create and publish reaction event
        reaction_event = ReactionEvent(
            reactor=self.senator,
            target_event=event,
            reaction_type=reaction_type,
            content=reaction_content
        )
        
        await self.event_bus.publish(reaction_event)
        logger.debug(f"Senator {self.name} reacted to speech with {reaction_type}")
        
        # Record in memory
        self.memory.record_reaction(event.event_id, reaction_type, reaction_content)
        
        # Update relationship based on reaction
        relationship_impact = 0
        if reaction_type == "agreement":
            relationship_impact = 0.05
        elif reaction_type == "disagreement":
            relationship_impact = -0.05
            
        if relationship_impact != 0:
            self.memory.record_event_relationship_impact(
                event.speaker.get("name", "Unknown"),
                event.event_id,
                relationship_impact,
                f"Reaction to speech: {reaction_type}"
            )
        
    async def _generate_reaction_content(self, event: SpeechEvent, reaction_type: str) -> str:
        """
        Generate content for a reaction.
        
        Args:
            event: The speech event to react to
            reaction_type: The type of reaction
            
        Returns:
            The reaction content
        """
        # This would normally use the LLM to generate a contextual reaction
        # For now, we'll use templates
        
        speaker_name = event.speaker.get("name", "the speaker")
        topic = event.metadata.get("topic", "the topic")
        
        templates = {
            "agreement": [
                f"Nods in agreement with {speaker_name}",
                f"Gestures supportively toward {speaker_name}",
                f"Quietly says 'Bene dictum' (well said)"
            ],
            "disagreement": [
                f"Frowns at {speaker_name}'s points",
                f"Shakes head in disagreement",
                f"Mutters quietly in disagreement"
            ],
            "interest": [
                f"Leans forward with interest",
                f"Listens attentively to {speaker_name}",
                f"Takes mental notes on {speaker_name}'s arguments"
            ],
            "boredom": [
                "Stifles a yawn",
                "Looks disinterested",
                "Glances around the chamber"
            ],
            "skepticism": [
                "Raises an eyebrow skeptically",
                f"Looks unconvinced by {speaker_name}'s arguments",
                "Exchanges skeptical glances with nearby senators"
            ],
            "neutral": [
                "Maintains a neutral expression",
                "Listens without visible reaction",
                "Considers the arguments carefully"
            ]
        }
        
        return random.choice(templates.get(reaction_type, templates["neutral"]))
        
    async def _generate_and_publish_interjection(self, event: SpeechEvent) -> None:
        """
        Generate and publish an interjection during a speech.
        
        Args:
            event: The speech event to interject during
        """
        # Determine interjection type
        interjection_type = await self._determine_interjection_type(event)
        
        # Generate interjection content
        latin_content, english_content = await self._generate_interjection_content(
            event.speaker.get("name", "Unknown"),
            interjection_type
        )
        
        # Create and publish interjection event
        interjection_event = InterjectionEvent(
            interjector=self.senator,
            target_speaker=event.speaker,
            interjection_type=interjection_type,
            latin_content=latin_content,
            english_content=english_content,
            target_speech_id=event.speech_id,
            causes_disruption=(interjection_type.value in ["procedural", "emotional"])
        )
        
        await self.event_bus.publish(interjection_event)
        logger.debug(f"Senator {self.name} interjected during {event.speaker.get('name')}'s speech")
        
        # Record in memory
        self.memory.record_event(interjection_event)
        
        # Update relationship based on interjection type
        relationship_impact = 0
        if interjection_type.value == "support":
            relationship_impact = 0.1
        elif interjection_type.value == "challenge":
            relationship_impact = -0.1
        elif interjection_type.value == "emotional":
            relationship_impact = -0.2
            
        if relationship_impact != 0:
            self.memory.record_event_relationship_impact(
                event.speaker.get("name", "Unknown"),
                event.event_id,
                relationship_impact,
                f"Interjection during speech: {interjection_type.value}"
            )
        
    async def _determine_interjection_type(self, event: SpeechEvent) -> InterjectionType:
        """
        Determine the type of interjection to make.
        
        Args:
            event: The speech event
            
        Returns:
            The interjection type
        """
        # Relationship affects interjection type
        relationship = self.memory.relationship_scores.get(event.speaker.get("name", ""), 0)
        
        # Stance agreement affects interjection type
        stance_agreement = (self.current_stance == event.stance)
        
        # Senator rank affects likelihood of procedural interjections
        rank = self.senator.get("rank", 0)
        
        # Define interjection types
        support_type = InterjectionType.SUPPORT
        challenge_type = InterjectionType.CHALLENGE
        procedural_type = InterjectionType.PROCEDURAL
        emotional_type = InterjectionType.EMOTIONAL
        informational_type = InterjectionType.INFORMATIONAL
        
        # Determine weights for different interjection types
        if relationship > 0.3:
            # Positive relationship - more likely to support or provide information
            weights = {
                support_type: 0.5,
                informational_type: 0.3,
                challenge_type: 0.1,
                procedural_type: 0.1 if rank > 2 else 0.0,
                emotional_type: 0.0
            }
        elif relationship < -0.3:
            # Negative relationship - more likely to challenge or make emotional interjections
            weights = {
                challenge_type: 0.5,
                emotional_type: 0.2,
                procedural_type: 0.2 if rank > 2 else 0.1,
                informational_type: 0.1,
                support_type: 0.0
            }
        else:
            # Neutral relationship - balanced weights
            weights = {
                informational_type: 0.3,
                challenge_type: 0.2 if not stance_agreement else 0.1,
                support_type: 0.2 if stance_agreement else 0.1,
                procedural_type: 0.2 if rank > 2 else 0.1,
                emotional_type: 0.1
            }
            
        # Choose interjection type based on weights
        types = list(weights.keys())
        weights_list = [weights[t] for t in types]
        
        # Normalize weights
        total = sum(weights_list)
        if total > 0:
            weights_list = [w / total for w in weights_list]
            
        return random.choices(types, weights=weights_list, k=1)[0]
        
    async def _generate_interjection_content(
        self, 
        speaker_name: str,
        interjection_type: InterjectionType
    ) -> Tuple[str, str]:
        """
        Generate content for an interjection.
        
        Args:
            speaker_name: The name of the senator being interrupted
            interjection_type: The type of interjection
            
        Returns:
            Tuple of (latin_content, english_content)
        """
        # This would normally use the LLM to generate contextual interjections
        # For now, we'll use templates
        
        # Get the string value of the interjection type
        type_value = interjection_type.value
        
        english_templates = {
            "support": [
                f"I strongly support {speaker_name}'s position!",
                "Hear, hear!",
                "Well said, colleague!"
            ],
            "challenge": [
                f"I must challenge {speaker_name}'s assertion!",
                "That claim is unfounded!",
                "Where is your evidence for this?"
            ],
            "procedural": [
                "Point of order!",
                "The speaker is out of time!",
                "This matter is not properly before the Senate!"
            ],
            "emotional": [
                "Outrageous!",
                "Absurd!",
                "How dare you suggest such a thing!"
            ],
            "informational": [
                "If I may add a relevant fact...",
                "The senator has overlooked an important detail.",
                "Let me clarify an important point."
            ]
        }
        
        latin_templates = {
            "support": [
                "Assentior!",
                "Bene dictum!",
                "Recte dicis!"
            ],
            "challenge": [
                "Nego!",
                "Falsum est!",
                "Ubi probatio?"
            ],
            "procedural": [
                "Ad ordinem!",
                "Tempus exhaustum est!",
                "Non recte procedit!"
            ],
            "emotional": [
                "Infandum!",
                "Absurdum!",
                "Quomodo audes!"
            ],
            "informational": [
                "Si licet addere...",
                "Senator praetermisit...",
                "Rem gravem explicabo."
            ]
        }
        
        english_content = random.choice(english_templates.get(type_value, ["I interject!"]))
        latin_content = random.choice(latin_templates.get(type_value, ["Interrumpo!"]))
        
        return latin_content, english_content
        
    async def _consider_stance_change(self, event: SpeechEvent) -> None:
        """
        Consider changing stance based on a speech.
        
        Args:
            event: The speech event that might influence stance
        """
        # Only consider stance change if we have a current stance and topic
        if not self.current_stance or not self.active_debate_topic:
            return
            
        # Skip if the speech is on a different topic
        speech_topic = event.metadata.get("topic")
        if speech_topic != self.active_debate_topic:
            return
            
        # Base probability of stance change (very low)
        base_probability = 0.05  # 5% chance by default
        
        # Adjust based on relationship with speaker
        relationship = self.memory.relationship_scores.get(event.speaker.get("name", ""), 0)
        relationship_factor = max(0, relationship * 0.1)  # Only positive relationships increase chance
        
        # Faction alignment affects stance change probability
        speaker_faction = event.speaker.get("faction", "")
        faction_factor = 0.05 if speaker_faction == self.faction else 0
        
        # Speaker rank affects persuasiveness
        rank_factor = min(0.1, event.speaker.get("rank", 0) * 0.025)  # Max +0.1 for rank 4+
        
        # Calculate final probability
        final_probability = min(0.3, base_probability + relationship_factor + faction_factor + rank_factor)
        
        # Decide whether to change stance
        if random.random() < final_probability:
            # Determine new stance (usually move toward speaker's stance)
            speaker_stance = event.stance
            old_stance = self.current_stance
            
            # If we're neutral, adopt speaker's stance
            if old_stance == "neutral":
                new_stance = speaker_stance
            # If we disagree with speaker, move to neutral
            elif old_stance != speaker_stance:
                new_stance = "neutral"
            # If we already agree, no change
            else:
                return
                
            # Record stance change
            self.current_stance = new_stance
            self.memory.record_stance_change(
                self.active_debate_topic,
                old_stance,
                new_stance,
                f"Persuaded by {event.speaker.get('name')}'s speech",
                event.event_id
            )
            
            logger.info(
                f"Senator {self.name} changed stance on {self.active_debate_topic} "
                f"from {old_stance} to {new_stance} due to {event.speaker.get('name')}'s speech"
            )