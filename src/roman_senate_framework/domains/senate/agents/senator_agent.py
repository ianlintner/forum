"""
Roman Senate Agent Implementation for Agentic Game Framework.

This module implements the SenatorAgent class that extends the framework's BaseAgent.
"""

import logging
import asyncio
import random
from typing import Any, Dict, List, Optional, Set, Tuple

from src.agentic_game_framework.agents.base_agent import BaseAgent
from src.agentic_game_framework.events.base import BaseEvent
from src.agentic_game_framework.events.event_bus import EventBus
from src.agentic_game_framework.memory.memory_interface import MemoryInterface

from src.roman_senate.utils.llm.base import LLMProvider
from src.roman_senate_framework.domains.senate.events.senate_events import (
    SpeechEvent, DebateEvent, ReactionEvent, InterjectionEvent, RelationshipEvent,
    create_debate_start_event, create_debate_end_event, create_speaker_change_event
)

logger = logging.getLogger(__name__)


class SenatorAgent(BaseAgent):
    """
    Roman Senator agent implementation using the Agentic Game Framework.
    
    This agent represents a senator in the Roman Senate simulation and can
    participate in debates, give speeches, react to other senators, etc.
    """
    
    def __init__(
        self,
        name: str,
        faction: str,
        rank: int,
        llm_provider: LLMProvider,
        event_bus: EventBus,
        memory: Optional[MemoryInterface] = None,
        agent_id: Optional[str] = None,
        attributes: Optional[Dict[str, Any]] = None,
        initial_state: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a senator agent.
        
        Args:
            name: The senator's name
            faction: The senator's political faction
            rank: The senator's rank (higher = more influential)
            llm_provider: The LLM provider for generating content
            event_bus: The event bus for publishing and subscribing to events
            memory: Optional memory system for the agent
            agent_id: Optional unique identifier
            attributes: Optional additional attributes
            initial_state: Optional initial state
        """
        # Set up senator-specific attributes
        senator_attributes = attributes or {}
        senator_attributes.update({
            "faction": faction,
            "rank": rank,
            "oratory_skill": random.uniform(0.3, 0.9),  # Random oratory skill
            "influence": rank * 0.2,  # Influence based on rank
            "ambition": random.uniform(0.2, 0.8),  # Random ambition level
            "traditionalism": random.uniform(0.2, 0.8)  # Random traditionalism level
        })
        
        # Initialize base agent
        super().__init__(
            name=name,
            attributes=senator_attributes,
            agent_id=agent_id,
            initial_state=initial_state or {}
        )
        
        # Store additional components
        self.llm_provider = llm_provider
        self.event_bus = event_bus
        self.memory = memory
        
        # Senator state
        self.state.update({
            "current_stance": None,
            "active_debate_topic": None,
            "current_speaker": None,
            "debate_in_progress": False,
            "last_speech_time": 0,
            "speeches_given": 0,
            "reactions_given": 0,
            "interjections_given": 0
        })
        
        # Topic stances (will be populated as debates occur)
        self.topic_stances = {}
        
        # Set up event subscriptions
        self._subscriptions = {
            "senate.speech",
            "senate.debate",
            "senate.reaction",
            "senate.interjection",
            "senate.relationship"
        }
    
    def get_subscriptions(self) -> set:
        """
        Get the event types this agent is subscribed to.
        
        Returns:
            set: Set of event type strings
        """
        return self._subscriptions
    
    def process_event(self, event: BaseEvent) -> None:
        """
        Process an incoming event.
        
        Args:
            event: The event to process
        """
        # Handle different event types
        if event.event_type == "senate.speech":
            self._handle_speech_event(event)
        elif event.event_type == "senate.debate":
            self._handle_debate_event(event)
        elif event.event_type == "senate.reaction":
            self._handle_reaction_event(event)
        elif event.event_type == "senate.interjection":
            self._handle_interjection_event(event)
        elif event.event_type == "senate.relationship":
            self._handle_relationship_event(event)
    
    def generate_action(self) -> Optional[BaseEvent]:
        """
        Generate an action based on the current state.
        
        Returns:
            An event representing the action, or None if no action
        """
        # If in a debate and not currently speaking, consider generating a speech
        if self.state["debate_in_progress"] and self.state["active_debate_topic"] and self.state["current_speaker"] != self.id:
            if self._should_speak():
                return self._generate_speech()
        
        # If someone else is speaking, consider generating a reaction or interjection
        if self.state["current_speaker"] and self.state["current_speaker"] != self.id:
            # Chance to react
            if random.random() < self._get_reaction_chance():
                return self._generate_reaction()
            
            # Chance to interject
            if random.random() < self._get_interjection_chance():
                return self._generate_interjection()
        
        return None
    
    @property
    def faction(self) -> str:
        """Get the senator's faction."""
        return self.attributes.get("faction", "")
    
    @property
    def rank(self) -> int:
        """Get the senator's rank."""
        return self.attributes.get("rank", 0)
    
    @property
    def oratory_skill(self) -> float:
        """Get the senator's oratory skill."""
        return self.attributes.get("oratory_skill", 0.5)
    
    @property
    def influence(self) -> float:
        """Get the senator's influence."""
        return self.attributes.get("influence", 0.0)
    
    def _handle_speech_event(self, event: BaseEvent) -> None:
        """
        Handle a speech event.
        
        Args:
            event: The speech event to process
        """
        # Skip own speeches
        if event.source == self.id:
            return
            
        # Record the event in memory if available
        if self.memory:
            self.memory.add_memory({
                "type": "speech",
                "speaker": event.source,
                "topic": event.data.get("topic"),
                "stance": event.data.get("stance"),
                "content": event.data.get("content")
            })
        
        # Store current speaker
        self.state["current_speaker"] = event.source
        
        # If the speech is about a topic we have a stance on, record the speaker's stance
        topic = event.data.get("topic")
        if topic and topic in self.topic_stances:
            speaker_stance = event.data.get("stance")
            if speaker_stance:
                # Record the stance for relationship updates
                self.state[f"speaker_{event.source}_stance_{topic}"] = speaker_stance
                
                # Compare stances for potential relationship changes
                own_stance = self.topic_stances[topic]
                if own_stance == speaker_stance:
                    # Agreement could improve relationship
                    reaction = self._generate_reaction()
                    if reaction:
                        self.event_bus.publish(reaction)
                else:
                    # Disagreement could worsen relationship
                    # Could generate a negative reaction here
                    pass
    
    def _handle_debate_event(self, event: BaseEvent) -> None:
        """
        Handle a debate event.
        
        Args:
            event: The debate event to process
        """
        # Record the event in memory if available
        if self.memory:
            self.memory.add_memory({
                "type": "debate",
                "debate_event_type": event.data.get("debate_event_type"),
                "topic": event.data.get("topic")
            })
        
        debate_event_type = event.data.get("debate_event_type")
        
        if debate_event_type == DebateEvent.DEBATE_START:
            self.state["debate_in_progress"] = True
            self.state["active_debate_topic"] = event.data.get("topic")
            logger.debug(f"Senator {self.name} noticed debate start on {self.state['active_debate_topic']}")
            
            # If we don't have a stance on this topic yet, decide one
            if self.state["active_debate_topic"]:
                self.decide_stance(self.state["active_debate_topic"])
            
        elif debate_event_type == DebateEvent.DEBATE_END:
            self.state["debate_in_progress"] = False
            self.state["active_debate_topic"] = None
            self.state["current_speaker"] = None
            logger.debug(f"Senator {self.name} noticed debate end")
            
        elif debate_event_type == DebateEvent.SPEAKER_CHANGE:
            self.state["current_speaker"] = event.data.get("speaker_id")
            logger.debug(f"Senator {self.name} noticed speaker change to {event.data.get('speaker_id')}")
    
    def _handle_reaction_event(self, event: BaseEvent) -> None:
        """
        Handle a reaction event.
        
        Args:
            event: The reaction event to process
        """
        # Skip own reactions
        if event.source == self.id:
            return
            
        # Record the event in memory if available
        if self.memory:
            self.memory.add_memory({
                "type": "reaction",
                "reactor": event.source,
                "target_event_id": event.data.get("target_event_id"),
                "reaction_type": event.data.get("reaction_type"),
                "content": event.data.get("content")
            })
    
    def _handle_interjection_event(self, event: BaseEvent) -> None:
        """
        Handle an interjection event.
        
        Args:
            event: The interjection event to process
        """
        # Skip own interjections
        if event.source == self.id:
            return
            
        # Record the event in memory if available
        if self.memory:
            self.memory.add_memory({
                "type": "interjection",
                "interjecter": event.source,
                "target_speaker": event.target,
                "interjection_type": event.data.get("interjection_type"),
                "content": event.data.get("content")
            })
    
    def _handle_relationship_event(self, event: BaseEvent) -> None:
        """
        Handle a relationship event.
        
        Args:
            event: The relationship event to process
        """
        # Record the event in memory if available
        if self.memory:
            self.memory.add_memory({
                "type": "relationship",
                "source_id": event.data.get("source_id"),
                "target_id": event.data.get("target_id"),
                "relationship_type": event.data.get("relationship_type"),
                "change_value": event.data.get("change_value"),
                "reason": event.data.get("reason")
            })
    
    def decide_stance(self, topic: str) -> str:
        """
        Decide the senator's stance on a topic.
        
        Args:
            topic: The topic to decide a stance on
            
        Returns:
            str: The decided stance ("support", "oppose", or "neutral")
        """
        # Check if we already have a stance on this topic
        if topic in self.topic_stances:
            return self.topic_stances[topic]
        
        # Factors that influence stance:
        # 1. Faction alignment
        # 2. Personal attributes (traditionalism, ambition)
        # 3. Topic keywords
        
        # Default to neutral
        stance = "neutral"
        
        # Faction influence
        if self.faction == "Optimates":
            # Optimates tend to be conservative/traditional
            stance_bias = 0.3  # Bias toward opposition (to change)
        elif self.faction == "Populares":
            # Populares tend to be progressive/reformist
            stance_bias = -0.3  # Bias toward support (of change)
        else:
            # Neutral faction
            stance_bias = 0.0
        
        # Personal attributes influence
        traditionalism = self.attributes.get("traditionalism", 0.5)
        ambition = self.attributes.get("ambition", 0.5)
        
        # More traditional senators are more likely to oppose change
        stance_bias += (traditionalism - 0.5) * 0.4
        
        # More ambitious senators are more likely to take strong positions
        # (either support or oppose, less likely to be neutral)
        ambition_factor = ambition * 0.4
        
        # Topic keywords influence
        topic_lower = topic.lower()
        
        # Topics that Optimates typically support
        optimates_keywords = ["tradition", "senate power", "patrician", "nobility", "authority"]
        # Topics that Populares typically support
        populares_keywords = ["reform", "people", "plebeian", "land distribution", "grain", "citizenship"]
        
        for keyword in optimates_keywords:
            if keyword in topic_lower:
                stance_bias += 0.2
                break
                
        for keyword in populares_keywords:
            if keyword in topic_lower:
                stance_bias -= 0.2
                break
        
        # Determine stance based on final bias
        if stance_bias > 0.2 + (random.random() * ambition_factor):
            stance = "oppose"
        elif stance_bias < -0.2 - (random.random() * ambition_factor):
            stance = "support"
        else:
            stance = "neutral"
        
        # Store the stance for future reference
        self.topic_stances[topic] = stance
        
        logger.debug(f"Senator {self.name} ({self.faction}) decided to {stance} topic: {topic}")
        return stance
    
    def _should_speak(self) -> bool:
        """
        Determine if the senator should speak in the current debate.
        
        Returns:
            bool: True if the senator should speak, False otherwise
        """
        # Factors that influence speaking:
        # 1. Rank (higher rank = more likely to speak)
        # 2. Oratory skill (higher skill = more likely to speak)
        # 3. Time since last speech (longer time = more likely to speak)
        # 4. Number of speeches already given (more speeches = less likely to speak)
        
        # Base chance based on rank and oratory skill
        speak_chance = 0.1 + (self.rank * 0.05) + (self.oratory_skill * 0.2)
        
        # Adjust based on time since last speech
        import time
        current_time = time.time()
        time_since_last_speech = current_time - self.state.get("last_speech_time", 0)
        if time_since_last_speech < 30:  # Less than 30 seconds
            speak_chance *= 0.2  # Much less likely to speak again immediately
        elif time_since_last_speech < 60:  # Less than 1 minute
            speak_chance *= 0.5  # Less likely to speak again soon
        
        # Adjust based on number of speeches given
        speeches_given = self.state.get("speeches_given", 0)
        if speeches_given > 3:
            speak_chance *= 0.7  # Less likely after several speeches
        
        # Random chance
        return random.random() < speak_chance
    
    def _get_reaction_chance(self) -> float:
        """
        Get the chance of reacting to the current speaker.
        
        Returns:
            float: Chance of reacting (0.0 to 1.0)
        """
        # Base chance based on personality
        base_chance = 0.05 + (self.attributes.get("expressiveness", 0.5) * 0.1)
        
        # Adjust based on number of reactions already given
        reactions_given = self.state.get("reactions_given", 0)
        if reactions_given > 5:
            base_chance *= 0.5  # Less likely after several reactions
        
        return base_chance
    
    def _get_interjection_chance(self) -> float:
        """
        Get the chance of interjecting during the current speech.
        
        Returns:
            float: Chance of interjecting (0.0 to 1.0)
        """
        # Base chance based on rank and personality
        base_chance = 0.03 + (self.rank * 0.01) + (self.attributes.get("assertiveness", 0.5) * 0.1)
        
        # Adjust based on number of interjections already given
        interjections_given = self.state.get("interjections_given", 0)
        if interjections_given > 3:
            base_chance *= 0.3  # Much less likely after several interjections
        
        return base_chance
    
    def _generate_speech(self) -> Optional[SpeechEvent]:
        """
        Generate a speech for the current debate topic.
        
        Returns:
            Optional[SpeechEvent]: The generated speech event, or None if unable to generate
        """
        topic = self.state.get("active_debate_topic")
        if not topic:
            return None
        
        # Get or decide stance on the topic
        stance = self.topic_stances.get(topic)
        if not stance:
            stance = self.decide_stance(topic)
        
        # Generate speech content
        # In a real implementation, this would use the LLM to generate more sophisticated content
        content = f"As a {self.faction} senator with rank {self.rank}, I {stance} this proposal about {topic}."
        
        # For more sophisticated content, we would use the LLM:
        # prompt = f"Generate a speech for Roman Senator {self.name} of the {self.faction} faction who {stance}s the topic: {topic}."
        # content = await self.llm_provider.generate_text(prompt)
        
        # Create speech event
        speech_event = SpeechEvent(
            speaker_id=self.id,
            content=content,
            topic=topic,
            stance=stance,
            source=self.id
        )
        
        # Update state
        import time
        self.state["last_speech_time"] = time.time()
        self.state["speeches_given"] = self.state.get("speeches_given", 0) + 1
        
        return speech_event
    
    def _should_react_to_speech(self, event: BaseEvent) -> bool:
        """
        Determine if the senator should react to a speech.
        
        Args:
            event: The speech event
            
        Returns:
            bool: True if the senator should react, False otherwise
        """
        # Skip if this is our own speech
        if event.source == self.id:
            return False
        
        # Get the topic and stance from the speech
        topic = event.data.get("topic")
        speaker_stance = event.data.get("stance")
        
        if not topic or not speaker_stance:
            return False
        
        # Get our stance on the topic
        our_stance = self.topic_stances.get(topic)
        if not our_stance:
            our_stance = self.decide_stance(topic)
        
        # More likely to react if we have a strong opinion (not neutral)
        if our_stance == "neutral":
            base_chance = 0.1
        else:
            base_chance = 0.3
        
        # More likely to react if we strongly agree or disagree
        if our_stance == speaker_stance:
            # Agreement
            reaction_chance = base_chance + 0.2
        else:
            # Disagreement
            reaction_chance = base_chance + 0.3
        
        # Adjust based on rank and personality
        reaction_chance += (self.rank * 0.02) + (self.attributes.get("expressiveness", 0.5) * 0.1)
        
        # Random chance
        return random.random() < reaction_chance
    
    def _should_interject(self, event: BaseEvent) -> bool:
        """
        Determine if the senator should interject during a speech.
        
        Args:
            event: The speech event
            
        Returns:
            bool: True if the senator should interject, False otherwise
        """
        # Skip if this is our own speech
        if event.source == self.id:
            return False
        
        # Get the topic and stance from the speech
        topic = event.data.get("topic")
        speaker_stance = event.data.get("stance")
        
        if not topic or not speaker_stance:
            return False
        
        # Get our stance on the topic
        our_stance = self.topic_stances.get(topic)
        if not our_stance:
            our_stance = self.decide_stance(topic)
        
        # Base chance depends on rank and assertiveness
        base_chance = 0.05 + (self.rank * 0.02) + (self.attributes.get("assertiveness", 0.5) * 0.1)
        
        # More likely to interject if we strongly disagree
        if our_stance != speaker_stance and our_stance != "neutral":
            base_chance += 0.2
        
        # Random chance
        return random.random() < base_chance
    
    def _generate_reaction(self) -> Optional[ReactionEvent]:
        """
        Generate a reaction to the current speaker.
        
        Returns:
            Optional[ReactionEvent]: The generated reaction event, or None if unable to generate
        """
        current_speaker = self.state.get("current_speaker")
        if not current_speaker:
            return None
        
        # Determine reaction type based on relationship and stance
        topic = self.state.get("active_debate_topic")
        if topic and topic in self.topic_stances:
            our_stance = self.topic_stances[topic]
            speaker_stance_key = f"speaker_{current_speaker}_stance_{topic}"
            speaker_stance = self.state.get(speaker_stance_key)
            
            if speaker_stance:
                if our_stance == speaker_stance:
                    # Agreement
                    reaction_types = ["approval", "agreement", "interest"]
                else:
                    # Disagreement
                    reaction_types = ["disapproval", "disagreement", "skepticism"]
            else:
                # No known stance, generic reactions
                reaction_types = ["interest", "contemplation", "surprise"]
        else:
            # No topic or stance, generic reactions
            reaction_types = ["interest", "contemplation", "surprise"]
        
        # Choose a reaction type
        reaction_type = random.choice(reaction_types)
        
        # Generate reaction content
        content = f"Reacts with {reaction_type}"
        
        # Create reaction event
        reaction_event = ReactionEvent(
            reactor_id=self.id,
            target_event_id="current_speech",  # This would be the actual event ID in practice
            reaction_type=reaction_type,
            content=content,
            source=self.id,
            target=current_speaker
        )
        
        # Update state
        self.state["reactions_given"] = self.state.get("reactions_given", 0) + 1
        
        return reaction_event
    
    def _generate_interjection(self) -> Optional[InterjectionEvent]:
        """
        Generate an interjection during the current speech.
        
        Returns:
            Optional[InterjectionEvent]: The generated interjection event, or None if unable to generate
        """
        current_speaker = self.state.get("current_speaker")
        if not current_speaker:
            return None
        
        # Determine interjection type based on relationship and stance
        topic = self.state.get("active_debate_topic")
        if topic and topic in self.topic_stances:
            our_stance = self.topic_stances[topic]
            speaker_stance_key = f"speaker_{current_speaker}_stance_{topic}"
            speaker_stance = self.state.get(speaker_stance_key)
            
            if speaker_stance:
                if our_stance == speaker_stance:
                    # Agreement
                    interjection_types = ["support", "clarification"]
                else:
                    # Disagreement
                    interjection_types = ["opposition", "question"]
            else:
                # No known stance, generic interjections
                interjection_types = ["question", "clarification", "procedural"]
        else:
            # No topic or stance, generic interjections
            interjection_types = ["question", "clarification", "procedural"]
        
        # Choose an interjection type
        interjection_type = random.choice(interjection_types)
        
        # Generate interjection content
        content = f"Interjects with {interjection_type}"
        
        # Create interjection event
        interjection_event = InterjectionEvent(
            interjecter_id=self.id,
            target_speaker_id=current_speaker,
            interjection_type=interjection_type,
            content=content,
            source=self.id,
            target=current_speaker
        )
        
        # Update state
        self.state["interjections_given"] = self.state.get("interjections_given", 0) + 1
        
        return interjection_event
    
    def _update_relationship(
        self,
        target_id: str,
        relationship_type: str,
        change_value: float,
        reason: str
    ) -> None:
        """
        Update a relationship with another senator.
        
        Args:
            target_id: ID of the target senator
            relationship_type: Type of relationship to update
            change_value: Value to change the relationship by
            reason: Reason for the change
        """
        # Create relationship event
        relationship_event = RelationshipEvent(
            source_id=self.id,
            target_id=target_id,
            relationship_event_type="relationship_change",
            relationship_type=relationship_type,
            change_value=change_value,
            reason=reason,
            source=self.id,
            target=target_id
        )
        
        # Publish the event
        self.event_bus.publish(relationship_event)