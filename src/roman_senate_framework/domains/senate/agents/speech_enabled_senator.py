"""
Modified SenatorAgent implementation that enables actual LLM-powered speech generation.
"""

import logging
import random
import time
import asyncio
from typing import Any, Dict, List, Optional, Set, Tuple

from src.roman_senate_framework.domains.senate.agents.senator_agent import SenatorAgent
from src.roman_senate_framework.domains.senate.events.senate_events import SpeechEvent
from src.agentic_game_framework.events.event_bus import EventBus
from src.agentic_game_framework.memory.memory_interface import MemoryInterface
from src.roman_senate.utils.llm.base import LLMProvider

logger = logging.getLogger(__name__)

class SpeechEnabledSenator(SenatorAgent):
    """
    Enhanced SenatorAgent that uses LLM to generate actual speech content.
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
        """Initialize with all the same parameters as the parent class."""
        super().__init__(
            name=name,
            faction=faction,
            rank=rank,
            llm_provider=llm_provider,
            event_bus=event_bus,
            memory=memory,
            agent_id=agent_id,
            attributes=attributes,
            initial_state=initial_state
        )
        
        # Log that we're using the enhanced speech-enabled senator
        logger.info(f"Created speech-enabled senator: {name} ({faction}, Rank {rank})")
    
    def _generate_speech(self) -> Optional[SpeechEvent]:
        """
        Generate a speech for the current debate topic using the LLM provider.
        
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
        
        try:
            # Generate speech content using the LLM
            prompt = f"""Generate a 3-5 sentence speech for Roman Senator {self.name} of the {self.faction} faction who {stance}s the topic: "{topic}".
            
            The speech should reflect the senator's faction ({self.faction}), rank ({self.rank}), and stance ({stance}).
            
            The speech should include appropriate Latin phrases, rhetorical devices, and references to Roman history and politics.
            
            SPEECH:"""
            
            # Try to use the LLM first
            try:
                # Use sync version for compatibility, but this should be async in production
                content = self.llm_provider.generate_completion(prompt)
                logger.info(f"Generated LLM speech for {self.name} on topic: {topic}")
            except Exception as e:
                # Fallback to template if LLM fails
                logger.error(f"Error generating speech with LLM: {e}")
                content = f"As a {self.faction} senator with rank {self.rank}, I {stance} this proposal about {topic}."
        except Exception as e:
            # Final fallback
            logger.error(f"Error in speech generation process: {e}")
            content = f"As a {self.faction} senator with rank {self.rank}, I {stance} this proposal about {topic}."
        
        # Create additional data for the speech event
        speech_data = {
            "senator_name": self.name,
            "faction": self.faction,
            "rank": self.rank
        }
        
        # Add portrait URL if available in senator state
        if "portrait_url" in self.state:
            speech_data["portrait_url"] = self.state["portrait_url"]
        
        # Create speech event
        speech_event = SpeechEvent(
            speaker_id=self.id,
            content=content,
            topic=topic,
            stance=stance,
            source=self.id,
            data=speech_data
        )
        
        # Update state
        self.state["last_speech_time"] = time.time()
        self.state["speeches_given"] = self.state.get("speeches_given", 0) + 1
        
        return speech_event