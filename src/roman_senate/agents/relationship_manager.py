"""
Roman Senate AI Game
Relationship Manager Module

This module provides the RelationshipManager class for managing senator relationships,
including storage, retrieval, updates, and decay over time.
"""

import datetime
import logging
from typing import Dict, List, Optional, Union, Any

from .memory_items import RelationshipMemoryItem
from .enhanced_event_memory import EnhancedEventMemory
from ..core.events import (
    Event,
    EventBus,
    SpeechEvent,
    ReactionEvent,
    InterjectionEvent,
    RelationshipChangeEvent
)

logger = logging.getLogger(__name__)


class RelationshipManager:
    """
    Central system for managing senator relationships.
    
    Handles:
    1. Storing/retrieving relationship data via memory system
    2. Registering/handling relationship events
    3. Applying relationship decay over time
    4. Providing relationship query capabilities
    """
    
    # Define relationship types
    RELATIONSHIP_TYPES = [
        "political",  # Political alliance/opposition
        "personal",   # Personal friendship/animosity
        "mentor",     # Mentor/mentee relationship
        "rival",      # Direct rivalry/competition
        "family"      # Family connection
    ]
    
    # Default decay rates per relationship type (monthly)
    DECAY_RATES = {
        "political": 0.08,  # Political relationships change moderately fast
        "personal": 0.04,   # Personal relationships change slowly
        "mentor": 0.02,     # Mentor relationships very stable
        "rival": 0.05,      # Rival relationships moderately stable
        "family": 0.01      # Family connections extremely stable
    }
    
    def __init__(
        self,
        senator_id: str,
        event_bus: EventBus,
        memory: EnhancedEventMemory
    ):
        """
        Initialize a relationship manager.
        
        Args:
            senator_id: ID of the senator this manager belongs to
            event_bus: Event bus for subscribing to and publishing events
            memory: Enhanced memory system for storing relationship data
        """
        self.senator_id = senator_id
        self.event_bus = event_bus
        self.memory = memory
        
        # Cache of current relationship values for quick access
        self.relationship_cache = {}
        for rel_type in self.RELATIONSHIP_TYPES:
            self.relationship_cache[rel_type] = {}
            
        # Initialize from memory
        self._load_relationships_from_memory()
        
        # Register for events
        self._register_event_handlers()
        
        logger.info(f"Relationship manager initialized for senator {senator_id}")
    
    def get_relationship(
        self,
        target_senator_id: str,
        relationship_type: Optional[str] = None
    ) -> Union[float, Dict[str, float]]:
        """
        Get relationship value(s) with another senator.
        
        Args:
            target_senator_id: ID of the target senator
            relationship_type: Type of relationship to get, or None for all types
            
        Returns:
            Float value if type specified, dict of {type: value} if not
        """
        if relationship_type:
            if relationship_type not in self.RELATIONSHIP_TYPES:
                logger.warning(f"Unknown relationship type: {relationship_type}")
                return 0.0
            return self.relationship_cache[relationship_type].get(target_senator_id, 0.0)
        
        return {
            rel_type: self.relationship_cache[rel_type].get(target_senator_id, 0.0)
            for rel_type in self.RELATIONSHIP_TYPES
        }
    
    def update_relationship(
        self,
        target_senator_id: str,
        relationship_type: str,
        change_value: float,
        reason: str,
        source_event_id: Optional[str] = None,
        publish_event: bool = True
    ) -> float:
        """
        Update relationship with another senator.
        
        Args:
            target_senator_id: ID of the target senator
            relationship_type: Type of relationship to update
            change_value: Value to add to relationship
            reason: Reason for the change
            source_event_id: Optional ID of event causing change
            publish_event: Whether to publish a RelationshipChangeEvent
            
        Returns:
            New relationship value
        """
        if relationship_type not in self.RELATIONSHIP_TYPES:
            logger.warning(f"Unknown relationship type: {relationship_type}")
            return 0.0
            
        # Get current value
        old_value = self.relationship_cache[relationship_type].get(target_senator_id, 0.0)
        
        # Calculate new value (bounded between -1.0 and 1.0)
        new_value = max(-1.0, min(1.0, old_value + change_value))
        
        # Update cache
        self.relationship_cache[relationship_type][target_senator_id] = new_value
        
        # Create relationship memory item
        rel_memory = RelationshipMemoryItem(
            senator_id=self.senator_id,
            target_senator_id=target_senator_id,
            relationship_type=relationship_type,
            relationship_value=new_value,
            timestamp=datetime.datetime.now(),
            importance=0.6 + abs(change_value) * 0.4,  # Higher change = higher importance
            decay_rate=self.DECAY_RATES[relationship_type],
            emotional_impact=change_value,
            context=reason
        )
        
        # Store in memory
        self.memory.memory_index.add_memory(rel_memory)
        
        # Publish event if requested and there was a significant change
        if publish_event and abs(new_value - old_value) > 0.001:
            event = RelationshipChangeEvent(
                senator_id=self.senator_id,
                target_senator_id=target_senator_id,
                relationship_type=relationship_type,
                old_value=old_value,
                new_value=new_value,
                change_value=change_value,
                reason=reason,
                source_event_id=source_event_id
            )
            self.event_bus.publish(event)
            
        logger.debug(
            f"Updated {relationship_type} relationship with {target_senator_id} "
            f"from {old_value:.2f} to {new_value:.2f} ({change_value:+.2f}): {reason}"
        )
            
        return new_value
    
    def apply_time_decay(self, days_elapsed: int):
        """
        Apply time-based decay to relationships.
        
        Args:
            days_elapsed: Number of days that have passed
        """
        logger.info(f"Applying {days_elapsed} days of relationship decay for {self.senator_id}")
        
        # For each relationship type and target
        for rel_type in self.RELATIONSHIP_TYPES:
            decay_rate = self.DECAY_RATES[rel_type]
            
            for target_id, value in list(self.relationship_cache[rel_type].items()):
                if abs(value) < 0.01:
                    continue  # Skip near-zero relationships
                    
                # Convert monthly rate to daily and calculate decay amount
                daily_decay = decay_rate / 30  # Monthly rate to daily
                total_decay = daily_decay * days_elapsed
                
                # Calculate decay direction (relationships trend toward neutral)
                decay_direction = 1.0 if value > 0 else -1.0
                decay_amount = total_decay * decay_direction
                
                # Calculate new value
                new_value = value - decay_amount
                
                # Check if the decay crossed zero (avoid oscillation)
                if (value > 0 and new_value < 0) or (value < 0 and new_value > 0):
                    new_value = 0.0
                    
                # Only update if significant change
                if abs(new_value - value) > 0.01:
                    # Update the relationship cache directly
                    self.relationship_cache[rel_type][target_id] = new_value
                    
                    # Only create memory items for significant decay
                    if abs(new_value - value) > 0.05:
                        # Create a relationship memory item with low importance
                        rel_memory = RelationshipMemoryItem(
                            senator_id=self.senator_id,
                            target_senator_id=target_id,
                            relationship_type=rel_type,
                            relationship_value=new_value,
                            timestamp=datetime.datetime.now(),
                            importance=0.3,  # Lower importance for decay events
                            decay_rate=self.DECAY_RATES[rel_type],
                            emotional_impact=0.0,  # Neutral emotional impact for natural decay
                            context=f"Natural relationship decay over {days_elapsed} days"
                        )
                        
                        # Add to memory
                        self.memory.memory_index.add_memory(rel_memory)
                        
                        logger.debug(
                            f"Decayed {rel_type} relationship with {target_id} "
                            f"from {value:.2f} to {new_value:.2f} over {days_elapsed} days"
                        )
    
    def get_relationship_history(
        self,
        target_senator_id: str,
        relationship_type: Optional[str] = None,
        limit: int = 10
    ) -> List[RelationshipMemoryItem]:
        """
        Get history of relationship changes.
        
        Args:
            target_senator_id: ID of the target senator
            relationship_type: Optional type to filter by
            limit: Maximum number of items to return
            
        Returns:
            List of relationship memory items, newest first
        """
        # Prepare query criteria
        criteria = {
            "tags": ["relationship", target_senator_id]
        }
        
        if relationship_type:
            criteria["tags"].append(relationship_type)
            
        # Query memory index
        memories = self.memory.memory_index.query(criteria)
        
        # Filter to only RelationshipMemoryItem instances
        rel_memories = [m for m in memories if isinstance(m, RelationshipMemoryItem)]
        
        # Sort by timestamp (newest first) and limit
        sorted_memories = sorted(
            rel_memories, 
            key=lambda m: m.timestamp,
            reverse=True
        )
        
        return sorted_memories[:limit]
        
    def get_overall_relationship(self, target_senator_id: str) -> float:
        """
        Calculate an overall relationship score across all types.
        
        Args:
            target_senator_id: ID of the target senator
            
        Returns:
            Weighted average relationship value
        """
        scores = self.get_relationship(target_senator_id)
        
        # Weighted average based on importance of each type
        weights = {
            "political": 0.3,
            "personal": 0.3,
            "mentor": 0.15,
            "rival": 0.2,
            "family": 0.05
        }
        
        weighted_sum = sum(scores[t] * weights[t] for t in self.RELATIONSHIP_TYPES)
        return weighted_sum
    
    def _register_event_handlers(self):
        """Register handlers for events that affect relationships."""
        self.event_bus.subscribe(SpeechEvent.TYPE, self._handle_speech_event)
        self.event_bus.subscribe(ReactionEvent.TYPE, self._handle_reaction_event)
        self.event_bus.subscribe(InterjectionEvent.TYPE, self._handle_interjection_event)
        
    async def _handle_speech_event(self, event: SpeechEvent):
        """Process speech events for relationship impacts."""
        # Skip own speeches
        if event.speaker.get("id") == self.senator_id:
            return
            
        speaker_id = event.speaker.get("id")
        stance = event.stance
        topic = event.metadata.get("topic", "unknown")
        
        # Political impact based on stance alignment
        if hasattr(self, 'current_stance') and self.current_stance:
            if self.current_stance == stance:
                # Agreement strengthens political relationship
                self.update_relationship(
                    speaker_id,
                    "political",
                    0.05,
                    f"Agreed with stance on {topic}",
                    event.event_id
                )
            elif self.current_stance != "neutral" and stance != "neutral":
                # Disagreement weakens political relationship
                self.update_relationship(
                    speaker_id,
                    "political",
                    -0.05,
                    f"Disagreed with stance on {topic}",
                    event.event_id
                )
                
    async def _handle_reaction_event(self, event: ReactionEvent):
        """Process reaction events for relationship impacts."""
        # Skip own reactions
        if event.reactor.get("id") == self.senator_id:
            return
            
        reactor_id = event.reactor.get("id")
        reaction_type = event.reaction_type
        target_event_id = event.target_event_id
        
        # Check if this is a reaction to our speech
        if hasattr(event, 'target_event') and hasattr(event.target_event, 'speaker') and \
           event.target_event.speaker.get("id") == self.senator_id:
            # Someone reacted to our speech
            if reaction_type in ["agreement", "interest"]:
                # Positive reaction strengthens personal relationship
                self.update_relationship(
                    reactor_id,
                    "personal",
                    0.05,
                    f"Reacted positively to my speech ({reaction_type})",
                    target_event_id
                )
            elif reaction_type in ["disagreement", "skepticism"]:
                # Negative reaction affects personal relationship
                self.update_relationship(
                    reactor_id,
                    "personal",
                    -0.03,
                    f"Reacted negatively to my speech ({reaction_type})",
                    target_event_id
                )
                
    async def _handle_interjection_event(self, event: InterjectionEvent):
        """Process interjection events for relationship impacts."""
        # Skip own interjections
        if event.interjector.get("id") == self.senator_id:
            return
            
        interjector_id = event.interjector.get("id")
        interjection_type = event.interjection_type
        
        # If we're the target of the interjection
        if event.target_speaker.get("id") == self.senator_id:
            if interjection_type.value == "support":
                # Support interjection strengthens both relationships
                self.update_relationship(
                    interjector_id,
                    "political",
                    0.08,
                    "Supported me during a speech",
                    event.event_id
                )
                self.update_relationship(
                    interjector_id,
                    "personal",
                    0.05,
                    "Supported me during a speech",
                    event.event_id
                )
            elif interjection_type.value == "challenge":
                # Challenge interjection affects political relationship
                self.update_relationship(
                    interjector_id,
                    "political",
                    -0.08,
                    "Challenged me during a speech",
                    event.event_id
                )
            elif interjection_type.value == "emotional":
                # Emotional interjection affects personal relationship
                self.update_relationship(
                    interjector_id,
                    "personal",
                    -0.1,
                    "Made an emotional outburst during my speech",
                    event.event_id
                )
    
    def _load_relationships_from_memory(self):
        """Initialize relationship cache from memory."""
        # Query memory for relationship items
        memories = self.memory.memory_index.query({"tags": ["relationship"]})
        
        # Group by target and type, keeping only the most recent
        latest_relationships = {}
        
        for memory in memories:
            if not isinstance(memory, RelationshipMemoryItem):
                continue
                
            key = (memory.target_senator_id, memory.relationship_type)
            
            if key not in latest_relationships or memory.timestamp > latest_relationships[key].timestamp:
                latest_relationships[key] = memory
                
        # Populate the cache
        for key, memory in latest_relationships.items():
            target_id, rel_type = key
            if rel_type in self.RELATIONSHIP_TYPES:
                self.relationship_cache[rel_type][target_id] = memory.relationship_value
                
        logger.info(
            f"Loaded {len(latest_relationships)} relationships for senator {self.senator_id}"
        )