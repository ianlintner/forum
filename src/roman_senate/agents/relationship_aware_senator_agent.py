"""
Roman Senate AI Game
Relationship-Aware Senator Agent Module

This module provides a senator agent with enhanced relationship capabilities,
building on the EnhancedSenatorAgent with the RelationshipManager.
"""

import asyncio
import logging
import random
from typing import Dict, List, Any, Optional, Tuple, Union, Set

from ..utils.llm.base import LLMProvider
from .enhanced_senator_agent import EnhancedSenatorAgent
from .relationship_manager import RelationshipManager
from .memory_persistence_manager import MemoryPersistenceManager
from .enhanced_event_memory import EnhancedEventMemory
from ..core.events import (
    Event,
    EventBus,
    SpeechEvent
)

logger = logging.getLogger(__name__)


class RelationshipAwareSenatorAgent(EnhancedSenatorAgent):
    """
    Senator agent with enhanced relationship capabilities.
    
    This class extends the EnhancedSenatorAgent with:
    - Relationship management system
    - Relationship-influenced decision making
    - Relationship-based stance changes
    - Relationship decay over time
    """
    
    def __init__(
        self,
        senator: Dict[str, Any],
        llm_provider: LLMProvider,
        event_bus: EventBus,
        memory_manager: Optional[MemoryPersistenceManager] = None
    ):
        """Initialize a relationship-aware senator agent."""
        # Initialize with base senator properties
        self.senator = senator
        self.llm_provider = llm_provider
        self.current_stance = None
        
        # Generate a unique ID for this senator if not present
        if "id" not in self.senator:
            self.senator["id"] = f"senator_{self.senator['name'].lower().replace(' ', '_')}"
        
        # Create enhanced memory
        self.memory = EnhancedEventMemory(senator_id=self.senator["id"])
        
        self.event_bus = event_bus
        self.active_debate_topic = None
        self.current_speaker = None
        self.debate_in_progress = False
        
        # Memory persistence manager
        self.memory_manager = memory_manager or MemoryPersistenceManager()
        
        # Initialize the relationship manager
        self.relationship_manager = RelationshipManager(
            senator_id=self.senator["id"],
            event_bus=self.event_bus,
            memory=self.memory
        )
        
        # Subscribe to relevant event types
        self.subscribe_to_events()
        
        logger.info(f"Relationship-aware senator agent initialized for {self.name}")
    
    async def decide_stance(self, topic: str, context: Dict) -> Tuple[str, str]:
        """
        Enhanced stance decision that considers relationships.
        
        Args:
            topic: The topic being debated
            context: Additional context about the topic
            
        Returns:
            A tuple of (stance, reasoning) where stance is "support", "oppose", or "neutral"
            and reasoning explains the decision
        """
        # Get base stance from principle alignment
        base_stance, base_reasoning = await super().decide_stance(topic, context)
        
        # Find key senators with opinions on this topic
        key_senators = await self._find_key_senators_for_topic(topic)
        
        # If no key senators found, return the base stance
        if not key_senators:
            return base_stance, base_reasoning
        
        # Calculate relationship influence
        relationship_influence = 0.0
        relationship_factors = []
        
        for senator_id, stance in key_senators.items():
            # Get overall relationship
            rel_score = self.relationship_manager.get_overall_relationship(senator_id)
            
            # Only strong relationships influence decisions
            if abs(rel_score) > 0.3:
                # Positive relationship pulls toward their stance
                # Negative relationship pushes away from their stance
                if stance == "support":
                    influence = rel_score * 0.2  # 20% weight to relationships
                elif stance == "oppose":
                    influence = -rel_score * 0.2
                else:
                    influence = 0.0
                    
                relationship_influence += influence
                
                # Record factor for explanation
                if abs(influence) > 0.05:
                    senator_name = self._get_senator_name(senator_id)
                    relationship_factors.append(
                        f"{senator_name}'s {stance} position ({rel_score:.1f} relationship)"
                    )
        
        # Apply relationship influence
        final_stance = base_stance
        if base_stance == "neutral" and abs(relationship_influence) > 0.2:
            # Relationships can sway neutral positions
            final_stance = "support" if relationship_influence > 0 else "oppose"
            
        # If relationships changed the stance, update reasoning
        if final_stance != base_stance:
            factors_text = ", ".join(relationship_factors)
            reasoning = f"{base_reasoning} However, I'm influenced by {factors_text}."
            
            # Record the relationship influence
            self.memory.add_observation(
                f"Stance on '{topic}' changed from {base_stance} to {final_stance} "
                f"due to relationship influences."
            )
            
            # Save the new stance
            self.current_stance = final_stance
            
            return final_stance, reasoning
            
        return base_stance, base_reasoning
    
    async def _consider_stance_change(self, event: SpeechEvent) -> None:
        """
        Enhanced stance change consideration that uses the relationship manager.
        
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
        
        # Get speaker ID
        speaker_id = event.speaker.get("id", "")
        if not speaker_id:
            return
            
        # Adjust based on relationship with speaker (using relationship manager)
        political_rel = self.relationship_manager.get_relationship(speaker_id, "political")
        personal_rel = self.relationship_manager.get_relationship(speaker_id, "personal")
        
        # Political relationships have more influence on stance changes
        relationship_factor = max(0, political_rel * 0.15 + personal_rel * 0.05)
        
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
                f"Persuaded by {event.speaker.get('name')}'s speech (relationship: {political_rel:.2f} political, {personal_rel:.2f} personal)",
                event.event_id
            )
            
            logger.info(
                f"Senator {self.name} changed stance on {self.active_debate_topic} "
                f"from {old_stance} to {new_stance} due to {event.speaker.get('name')}'s speech "
                f"(relationship: {political_rel:.2f} political, {personal_rel:.2f} personal)"
            )
    
    async def _find_key_senators_for_topic(self, topic: str) -> Dict[str, str]:
        """
        Find key senators with known stances on a topic.
        
        Args:
            topic: The topic to find stances for
            
        Returns:
            Dictionary mapping senator IDs to stances
        """
        # In a real implementation, this would query the memory system
        # for senators who have spoken on this topic
        # For now, we'll return a simple mock implementation
        
        # Query memory for events related to this topic
        criteria = {
            "tags": [topic],
            "min_strength": 0.3  # Only consider strong memories
        }
        
        # Add await here since query might be async
        topic_memories = await self.memory.memory_index.query(criteria)
        
        # Extract senator stances from memories
        senator_stances = {}
        
        for memory in topic_memories:
            # Look for speech events
            if hasattr(memory, 'event_type') and memory.event_type == "speech":
                if hasattr(memory, 'source') and hasattr(memory, 'stance'):
                    # Extract senator ID and stance
                    senator_id = memory.source.get("id") if isinstance(memory.source, dict) else None
                    if senator_id and senator_id != self.senator["id"]:  # Skip self
                        senator_stances[senator_id] = memory.stance
        
        return senator_stances
    
    def _get_senator_name(self, senator_id: str) -> str:
        """
        Get a senator's name from their ID.
        
        Args:
            senator_id: The ID of the senator
            
        Returns:
            The senator's name, or a formatted version of the ID if not found
        """
        # In a real implementation, this would look up the senator in a registry
        # For now, return a formatted version of the ID
        return senator_id.replace("senator_", "").replace("_", " ").title()
    
    async def apply_time_effects(self, days_elapsed: int) -> None:
        """
        Apply time-based effects, including relationship decay.
        
        Args:
            days_elapsed: Number of days that have passed
        """
        # Apply relationship decay
        self.relationship_manager.apply_time_decay(days_elapsed)
        
        # Other time-based effects could be added here
        
        logger.info(f"Applied {days_elapsed} days of time effects for {self.name}")
        
    def _load_memory(self):
        """
        Load memory from persistence if available.
        This method is called during initialization.
        """
        try:
            # Try to load memory from persistence
            loaded_memory = self.memory_manager.load_memory(self.senator["id"])
            if loaded_memory and isinstance(loaded_memory, EnhancedEventMemory):
                # Merge the loaded memory with our current memory
                self.memory.merge_with(loaded_memory)
                logger.info(f"Loaded memory for {self.name} from persistence")
            else:
                logger.info(f"No persistent memory found for {self.name}")
        except Exception as e:
            logger.warning(f"Failed to load memory for {self.name}: {e}")
            
    def subscribe_to_events(self):
        """
        Subscribe to relevant event types.
        """
        # Subscribe to speech events to track stances
        self.event_bus.subscribe("speech", self._handle_speech_event)
        
        # Subscribe to debate events to track active topics
        self.event_bus.subscribe("debate", self._handle_debate_event)
        
        # Subscribe to relationship events
        self.event_bus.subscribe("relationship_change", self._handle_relationship_event)
        
        logger.info(f"Senator {self.name} subscribed to events")
    
    async def _handle_speech_event(self, event):
        """
        Handle speech events.
        
        Args:
            event: The speech event
        """
        # Record the speech in memory
        self.memory.record_event(event)
        
        # Consider stance change based on the speech
        await self._consider_stance_change(event)
        
        logger.debug(f"Senator {self.name} processed speech event: {event.event_id}")
    
    async def _handle_debate_event(self, event):
        """
        Handle debate events.
        
        Args:
            event: The debate event
        """
        # Update active debate topic
        if event.event_subtype == "debate_start":
            self.active_debate_topic = event.metadata.get("topic")
            self.debate_in_progress = True
            logger.debug(f"Senator {self.name} tracking debate on {self.active_debate_topic}")
        elif event.event_subtype == "debate_end":
            self.debate_in_progress = False
            logger.debug(f"Senator {self.name} noted end of debate on {self.active_debate_topic}")
        # Record the debate event
        self.memory.record_event(event)
        
        
    def _handle_relationship_event(self, event):
        """
        Handle relationship change events.
        
        Args:
            event: The relationship change event
        """
        # Only process events that involve this senator
        if event.senator_id == self.senator["id"] or event.target_senator_id == self.senator["id"]:
            self.memory.record_event(event)
            logger.debug(f"Senator {self.name} recorded relationship event: {event.event_id}")