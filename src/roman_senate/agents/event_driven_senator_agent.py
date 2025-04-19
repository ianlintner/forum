"""
Roman Senate AI Game
Event-Driven Senator Agent Module

This module implements a senator agent that consumes and produces events
using the event-driven architecture. It adapts the agentic_game_framework's
BaseAgent architecture to work with the Roman Senate event system.

Part of the Migration Plan: Phase 2 - Agent System Migration.
"""

import asyncio
import random
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any, Set

from agentic_game_framework.agents.base_agent import BaseAgent as FrameworkBaseAgent

from ..core.events.base import BaseEvent as RomanEvent
from ..core.events.event_bus import EventBus
from ..utils.llm.base import LLMProvider
from .event_memory import EventMemory


class EventDrivenSenatorAgent(FrameworkBaseAgent):
    """
    Event-driven implementation of a Roman Senator agent.
    
    This class adapts the agentic_game_framework's BaseAgent for the Roman Senate
    simulation. It responds to events, maintains memory of past events,
    and can generate new events.
    
    Senator agents can generate speeches, vote on topics, and interact with
    other senators through the event system rather than direct method calls.
    """
    
    def __init__(
        self,
        senator: Dict[str, Any],
        llm_provider: LLMProvider,
        event_bus: EventBus,
        agent_id: Optional[str] = None,
        initial_state: Optional[Dict[str, Any]] = None,
        event_subscriptions: Optional[List[str]] = None
    ):
        """
        Initialize a senator agent.
        
        Args:
            senator: Dictionary containing senator details (name, faction, etc.)
            llm_provider: Provider for language model interactions
            event_bus: Event bus for publishing and subscribing to events
            agent_id: Unique identifier (generated if not provided)
            initial_state: Initial state for the agent
            event_subscriptions: List of event types to subscribe to
        """
        # Initialize base agent - we'll use senator's name as the agent name
        # Important: This sets self.name as an attribute (not a property)
        super().__init__(
            name=senator["name"],
            attributes=senator,
            agent_id=agent_id or str(uuid.uuid4()),
            initial_state=initial_state or {}
        )
        
        # Store additional attributes
        self.senator = senator
        self.llm_provider = llm_provider
        self.event_bus = event_bus
        self.memory = EventMemory(owner_id=self.id)
        
        # Set up initial state values if not provided
        if "current_stance" not in self.state:
            self.state["current_stance"] = None
        if "relationship_scores" not in self.state:
            self.state["relationship_scores"] = {}
        
        # Subscribe to events
        self._subscribe_to_events(event_subscriptions or [])
        
        # Track currently processing events to prevent feedback loops
        self._processing_events: Set[str] = set()
    
    # We use the parent's self.name directly instead of defining a property
    
    @property
    def faction(self) -> str:
        """Get the senator's faction."""
        return self.senator["faction"]
    
    def _subscribe_to_events(self, event_types: List[str]) -> None:
        """
        Subscribe to specific event types.
        
        Args:
            event_types: List of event types to subscribe to
        """
        # Default event subscriptions for all senator agents
        default_subscriptions = [
            "debate.topic_introduced",
            "debate.speech_delivered",
            "debate.vote_requested",
            "senate.session_started",
            "senate.session_ended",
            "relationship.reputation_changed"
        ]
        
        # Subscribe to default events
        for event_type in default_subscriptions:
            self.subscribe_to_event(event_type)
            self.event_bus.subscribe(event_type, self, priority=1)
        
        # Subscribe to additional events
        for event_type in event_types:
            if event_type not in default_subscriptions:
                self.subscribe_to_event(event_type)
                self.event_bus.subscribe(event_type, self, priority=1)
    
    def process_event(self, event: RomanEvent) -> None:
        """
        Process an incoming event.
        
        This method is called when an event the agent is subscribed to occurs.
        The agent updates its internal state, makes decisions, and potentially
        generates new events or actions.
        
        Args:
            event: The event to process
        """
        # Avoid processing the same event twice or processing events we generated
        event_id = event.get_id()
        if event_id in self._processing_events or event.source == self.id:
            return
        
        # Mark this event as being processed
        self._processing_events.add(event_id)
        
        # Store the event in memory
        self.memory.add_event(event)
        
        # Handle different event types
        if event.event_type == "debate.topic_introduced":
            self._handle_topic_introduced(event)
        elif event.event_type == "debate.speech_delivered":
            self._handle_speech_delivered(event)
        elif event.event_type == "debate.vote_requested":
            self._handle_vote_requested(event)
        elif event.event_type == "relationship.reputation_changed":
            self._handle_reputation_changed(event)
        
        # Mark event as processed
        self._processing_events.remove(event_id)
    
    def _handle_topic_introduced(self, event: RomanEvent) -> None:
        """
        Handle a topic introduction event.
        
        Determines the stance on the topic and prepares to participate in debate.
        
        Args:
            event: The topic introduction event
        """
        # Extract topic from event
        topic = event.data.get("topic", "")
        if not topic:
            return
        
        # Update state with the current topic
        self.update_state({"current_topic": topic})
        
        # Determine stance on topic (using synchronous method)
        stance, reasoning = self._decide_stance(topic, event.data)
        
        # Update state with stance and reasoning
        self.update_state({
            "current_stance": stance,
            "stance_reasoning": reasoning
        })
    
    def _handle_speech_delivered(self, event: RomanEvent) -> None:
        """
        Handle a speech delivered event.
        
        May generate interjections or update relationships based on the speech.
        
        Args:
            event: The speech delivered event
        """
        speaker_id = event.source
        if speaker_id == self.id:
            return  # Don't respond to own speeches
        
        speech_data = event.data
        speaker_name = speech_data.get("speaker_name", "Unknown Senator")
        speech_content = speech_data.get("content", "")
        stance = speech_data.get("stance", "neutral")
        
        # Update relationship based on alignment of stances
        if self.state.get("current_stance") and stance:
            self._update_relationship_based_on_stance(speaker_id, stance)
        
        # Decide whether to generate an interjection
        should_interject = self._should_interject(speaker_name, speech_data)
        
        if should_interject:
            # Direct synchronous call
            interjection = self._generate_interjection(speaker_name, speech_data)
            
            if interjection:
                # Publish interjection event
                interjection_event = RomanEvent(
                    event_type="debate.interjection",
                    source=self.id,
                    target=speaker_id,
                    data={
                        "speaker_name": speaker_name,
                        "interjecting_senator": self.name,
                        "latin_content": interjection.get("latin_content", ""),
                        "english_content": interjection.get("english_content", ""),
                        "type": interjection.get("type", "supportive"),
                        "intensity": interjection.get("intensity", 0.5)
                    }
                )
                self.event_bus.publish(interjection_event)
    
    def _handle_vote_requested(self, event: RomanEvent) -> None:
        """
        Handle a vote request event.
        
        Casts a vote on the current topic based on the agent's stance.
        
        Args:
            event: The vote request event
        """
        topic = event.data.get("topic", "")
        if not topic:
            return
            
        # Check if we have already determined a stance
        stance = self.state.get("current_stance")
        if not stance:
            # Determine stance if we haven't already using synchronous method
            stance, reasoning = self._decide_stance(topic, event.data)
            
            # Update state with stance and reasoning
            self.update_state({
                "current_stance": stance,
                "stance_reasoning": reasoning
            })
        
        # Map stance to vote
        vote = "for" if stance == "support" else "against" if stance == "oppose" else "abstain"
        
        # Publish vote event
        vote_event = RomanEvent(
            event_type="debate.vote_cast",
            source=self.id,
            data={
                "topic": topic,
                "senator_name": self.name,
                "vote": vote,
                "faction": self.faction,
                "reasoning": self.state.get("stance_reasoning", "")
            }
        )
        self.event_bus.publish(vote_event)
    
    def _handle_reputation_changed(self, event: RomanEvent) -> None:
        """
        Handle a reputation change event.
        
        Updates relationship scores based on reputation changes.
        
        Args:
            event: The reputation change event
        """
        target_id = event.target
        if not target_id or target_id == self.id:
            return
            
        change_amount = event.data.get("change", 0.0)
        source_id = event.source
        
        if source_id and source_id != self.id:
            # Update our relationship with the source of the reputation change
            # (we'll be more aligned with senators who support those we support)
            if target_id in self.state["relationship_scores"]:
                target_relationship = self.state["relationship_scores"][target_id]
                
                # If we like the target, we'll like those who improve their reputation
                # and dislike those who harm it
                relationship_update = change_amount * 0.2 * (1 if target_relationship > 0 else -1)
                
                self._update_relationship_score(source_id, relationship_update)
    
    def _update_relationship_based_on_stance(self, senator_id: str, stance: str) -> None:
        """
        Update relationship with another senator based on stance alignment.
        
        Args:
            senator_id: ID of the senator to update relationship with
            stance: Stance of the other senator
        """
        our_stance = self.state.get("current_stance", "neutral")
        
        # No change for neutral stances
        if our_stance == "neutral" or stance == "neutral":
            return
            
        # Determine if stances align
        stances_align = our_stance == stance
        
        # Update relationship score
        change = 0.1 if stances_align else -0.1
        self._update_relationship_score(senator_id, change)
    
    def _update_relationship_score(self, senator_id: str, change: float) -> None:
        """
        Update relationship score with another senator.
        
        Args:
            senator_id: ID of the senator to update relationship with
            change: Amount to change the relationship by (-1.0 to 1.0)
        """
        current_score = self.state["relationship_scores"].get(senator_id, 0.0)
        new_score = max(-1.0, min(1.0, current_score + change))
        
        relationship_scores = self.state["relationship_scores"].copy()
        relationship_scores[senator_id] = new_score
        self.update_state({"relationship_scores": relationship_scores})
        
        # Publish relationship update event
        relationship_event = RomanEvent(
            event_type="relationship.updated",
            source=self.id,
            target=senator_id,
            data={
                "source_name": self.name,
                "target_name": senator_id,  # In real system, we'd have name lookup
                "old_score": current_score,
                "new_score": new_score,
                "change": change
            }
        )
        self.event_bus.publish(relationship_event)
    
    def _decide_stance(self, topic: str, context: Dict) -> Tuple[str, str]:
        """
        Decide the stance on a given topic based on the senator's characteristics.
        
        Args:
            topic: The topic being debated
            context: Additional context about the topic
            
        Returns:
            A tuple of (stance, reasoning) where stance is "support", "oppose", or "neutral"
            and reasoning explains the decision
        """
        # Generate the prompt for stance determination
        prompt = f"""
        You are {self.name}, a {self.faction} senator in the Roman Senate.
        Topic for debate: {topic}
        
        Based on your faction ({self.faction}) and your personality traits,
        what stance would you take on this topic: for, against, or neutral?
        Consider your past voting history and relationships with other senators.
        
        First provide your reasoning in 1-2 sentences, then on a new line
        return ONLY the word "for", "against", or "neutral".
        """
        
        # Get response from LLM
        response = self.llm_provider.generate_text(prompt)
        
        # Parse response to extract reasoning and stance
        reasoning = ""
        stance_text = ""
        lines = response.strip().split('\n')
        
        if len(lines) > 1:
            # Multiple lines - take all but last as reasoning, last as stance
            reasoning = ' '.join(lines[:-1]).strip()
            stance_text = lines[-1].lower()
        else:
            # Single line - use same text for both
            reasoning = response.strip()
            stance_text = response.strip().lower()
        
        # Determine stance based on text keywords
        final_stance = "neutral"  # Default stance
        
        if "for" in stance_text or "support" in stance_text:
            final_stance = "support"
        elif "against" in stance_text or "oppose" in stance_text:
            final_stance = "oppose"
        
        return final_stance, reasoning
    
    def generate_speech(self, topic: str, context: Dict) -> Dict[str, Any]:
        """
        Generate a speech for the current debate topic.
        
        Args:
            topic: The topic being debated
            context: Additional context about the debate
            
        Returns:
            Dictionary containing speech details including content and metadata
        """
        # Ensure we have a stance on the topic
        if not self.state.get("current_stance"):
            stance, reasoning = self._decide_stance(topic, context)
            self.update_state({
                "current_stance": stance,
                "stance_reasoning": reasoning
            })
        else:
            stance = self.state["current_stance"]
            reasoning = self.state.get("stance_reasoning", "")
        
        # Generate the English speech first
        english_prompt = f"""
        You are {self.name}, a {self.faction} senator in the Roman Senate.
        Topic for debate: {topic}
        Your stance: {stance}
        
        Generate a brief speech (3-4 sentences) expressing your views on this topic in English.
        Your speech should reflect your faction's values and your personal style.
        
        After the speech, on a new line, briefly explain your rhetorical approach
        and why you chose it (1-2 sentences).
        """
        
        english_response = self.llm_provider.generate_text(english_prompt)
        
        # Parse the response to separate English speech from reasoning
        english_parts = english_response.strip().split('\n\n', 1)
        if len(english_parts) > 1:
            english_text = english_parts[0].strip()
            speech_reasoning = english_parts[1].strip()
        else:
            # If no clear separation, use the whole response as speech
            english_text = english_response.strip()
            speech_reasoning = "Strategic approach based on faction interests and personal style."
        
        # Generate the Latin version of the speech
        latin_prompt = f"""
        You are a Classical Latin expert specialized in translating English to authentic Classical Latin.
        
        Translate the following English Roman Senate speech into authentic Classical Latin of the Republican era.
        
        Guidelines for your translation:
        1. Use Classical Latin vocabulary, syntax, and rhetorical devices from the Republican era
        2. Maintain the formal oratorical style appropriate for the Roman Senate
        3. Ensure it sounds like genuine Classical Latin that Cicero might have used
        Return ONLY the Latin translation, with no additional commentary or explanations.

        English speech:
        {english_text}
        """
        
        # Request Latin translation from LLM
        latin_text = self.llm_provider.generate_text(latin_prompt)
        latin_text = latin_text.strip()
        
        # For backward compatibility, create a combined speech text
        speech = f"---LATIN---\n{latin_text}\n---ENGLISH---\n{english_text}"
        
        # Create speech result
        speech_result = {
            "speech": speech,
            "reasoning": speech_reasoning,
            "latin_text": latin_text,
            "english_text": english_text,
            "stance": stance,
            "stance_reasoning": reasoning,
            "speaker_name": self.name,
            "faction": self.faction
        }
        
        return speech_result
    
    def _should_interject(self, speaker_name: str, speech_content: Dict[str, Any]) -> bool:
        """
        Determine whether this senator should interject during another's speech.
        
        Args:
            speaker_name: The name of the senator who is speaking
            speech_content: The content of the speech
            
        Returns:
            True if the senator should interject, False otherwise
        """
        # Don't interject during your own speech
        if speaker_name == self.name:
            return False
            
        # Base probability of interjection
        base_probability = 0.15  # 15% chance by default
        
        # Adjust based on relationship with speaker (stronger feelings = more likely to interject)
        speaker_id = speech_content.get("speaker_id", "")
        relationship = 0.0
        
        if speaker_id and speaker_id in self.state["relationship_scores"]:
            relationship = self.state["relationship_scores"][speaker_id]
            relationship_factor = abs(relationship) * 0.2  # Max +/- 0.2
            base_probability += relationship_factor
        
        # Faction alignment affects interjection probability
        speaker_faction = speech_content.get("faction", "")
        if speaker_faction == self.faction:
            # More likely to interject positively for same faction
            if relationship >= 0:
                base_probability += 0.1
        else:
            # More likely to interject negatively for different faction
            if relationship <= 0:
                base_probability += 0.1
        
        # Random check based on final probability
        return random.random() < base_probability
    
    def _generate_interjection(self, speaker_name: str, speech_content: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Generate an interjection in response to another senator's speech.
        
        Args:
            speaker_name: The name of the senator who is speaking
            speech_content: The content of the speech being responded to
            
        Returns:
            Dictionary with interjection details if generated, None otherwise
        """
        # Extract speech content
        speech_text = speech_content.get("english_text", "")
        if not speech_text:
            return None
        
        # Determine interjection type based on relationships and stances
        speaker_id = speech_content.get("speaker_id", "")
        relationship = 0.0
        
        if speaker_id and speaker_id in self.state["relationship_scores"]:
            relationship = self.state["relationship_scores"][speaker_id]
        
        # Basic determination of interjection type
        if relationship > 0.3:
            interjection_type = "supportive"
        elif relationship < -0.3:
            interjection_type = "hostile"
        else:
            interjection_type = random.choice(["supportive", "hostile", "questioning", "procedural"])
        
        # Calculate intensity based on relationship strength
        intensity = min(1.0, 0.5 + abs(relationship) * 0.5)
        
        # Generate the interjection content
        prompt = f"""
        You are {self.name}, a {self.faction} senator in the Roman Senate.
        
        Senator {speaker_name} is speaking and has said:
        "{speech_text}"
        
        Generate a brief interjection (1-2 sentences) that is {interjection_type} in tone.
        The interjection should reflect your faction's values and your personal style.
        Make it authentic to ancient Roman political discourse.
        
        Return only the interjection text with no additional explanation.
        """
        
        english_content = self.llm_provider.generate_text(prompt)
        english_content = english_content.strip()
        
        # Generate Latin version
        latin_prompt = f"""
        Translate this Roman Senate interjection into authentic Classical Latin:
        
        "{english_content}"
        
        Return only the Latin translation.
        """
        
        latin_content = self.llm_provider.generate_text(latin_prompt)
        latin_content = latin_content.strip()
        
        return {
            "latin_content": latin_content,
            "english_content": english_content,
            "type": interjection_type,
            "intensity": intensity,
            "timing": random.choice(["beginning", "middle", "end"])
        }
    
    def generate_action(self) -> Optional[RomanEvent]:
        """
        Generate an action based on the agent's current state.
        
        This method is called periodically to allow the agent to take initiative
        and generate actions without direct external stimuli.
        
        Returns:
            Optional[RomanEvent]: An event representing the action, or None if no action
        """
        # Check if there's a current topic that we haven't spoken on yet
        current_topic = self.state.get("current_topic")
        if not current_topic:
            return None
            
        # Check if we've already spoken on this topic
        spoke_on_current_topic = False
        recent_speeches = self.memory.get_events_by_type("debate.speech_delivered")
        
        for speech_event in recent_speeches:
            if (speech_event.source == self.id and 
                speech_event.data.get("topic") == current_topic):
                spoke_on_current_topic = True
                break
        
        if spoke_on_current_topic:
            return None
            
        # Generate a speech on the current topic
        context = {}  # Minimal context for now
        
        try:
            # Direct synchronous call
            speech_result = self.generate_speech(current_topic, context)
            
            # Create speech event
            speech_event = RomanEvent(
                event_type="debate.speech_delivered",
                source=self.id,
                data={
                    "topic": current_topic,
                    "speaker_name": self.name,
                    "speaker_id": self.id,
                    "faction": self.faction,
                    "stance": speech_result["stance"],
                    "content": speech_result["speech"],
                    "latin_text": speech_result["latin_text"],
                    "english_text": speech_result["english_text"],
                    "reasoning": speech_result["reasoning"]
                }
            )
            
            return speech_event
        except Exception as e:
            # In a real system, we'd log this error
            print(f"Error generating speech for {self.name}: {e}")
            return None
    
    def handle_event(self, event: RomanEvent) -> None:
        """
        Handle an event received through the event bus.
        
        This method is called by the event bus when this agent receives an event.
        
        Args:
            event: The event to handle
        """
        self.process_event(event)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the agent to a dictionary representation.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the agent
        """
        data = super().to_dict()
        
        # Add additional senator-specific data
        data.update({
            "senator": self.senator,
            "memory": self.memory.to_dict(),
            "event_subscriptions": list(self._event_subscriptions)
        })
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], llm_provider: LLMProvider, event_bus: EventBus) -> 'EventDrivenSenatorAgent':
        """
        Create an agent from a dictionary representation.
        
        Args:
            data: Dictionary containing agent data
            llm_provider: Provider for language model interactions
            event_bus: Event bus for publishing and subscribing to events
            
        Returns:
            EventDrivenSenatorAgent: A new agent instance
        """
        if "senator" not in data or "name" not in data["senator"]:
            raise ValueError("Agent dictionary must contain senator data with name")
            
        agent = cls(
            senator=data["senator"],
            llm_provider=llm_provider,
            event_bus=event_bus,
            agent_id=data.get("id"),
            initial_state=data.get("state", {}),
            event_subscriptions=data.get("event_subscriptions", [])
        )
        
        # Restore memory if present
        if "memory" in data:
            agent.memory = EventMemory.from_dict(data["memory"])
            
        return agent