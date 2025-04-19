"""
Roman Senate AI Game
Enhanced Event Memory Module

This module provides an enhanced version of the EventMemory class
with support for memory decay, importance weighting, and efficient retrieval.

Part of the Phase 3 Migration: Memory System - Adapting or extending agentic_game_framework.memory
"""

import os
import json
import datetime
import logging
import uuid
from typing import Dict, List, Any, Optional, Set, Tuple, Union, Type
from pathlib import Path

from agentic_game_framework.memory.memory_interface import MemoryInterface, MemoryItem as FrameworkMemoryItem
from agentic_game_framework.memory.vectorized_memory import VectorizedMemory

from .agent_memory import AgentMemory
from .event_memory import EventMemory, EventMemoryItem as BaseEventMemoryItem
from .memory_base import MemoryBase
from .memory_items import (
    EventMemoryItem,
    ReactionMemoryItem,
    StanceChangeMemoryItem,
    RelationshipImpactItem,
    create_memory_from_dict
)
from .memory_index import MemoryIndex

# Define RomanEvent type for type annotations
try:
    from ..core.events.base import BaseEvent as RomanEvent
except ImportError:
    # Fallback if import fails
    from ..core.events import Event as RomanEvent

logger = logging.getLogger(__name__)


class EnhancedEventMemory(EventMemory, MemoryInterface):
    """
    Enhanced memory for event-driven senator agents with persistence and decay.
    
    This class extends the EventMemory with:
    - Memory importance weighting
    - Time-based memory decay
    - Efficient memory indexing and retrieval
    - Persistence to disk
    - Memory consolidation
    
    Additionally, it implements the MemoryInterface from the agentic game framework
    to ensure compatibility with the framework's memory system.
    """
    
    def __init__(self, senator_id: Optional[str] = None, use_vectorization: bool = False):
        """
        Initialize an enhanced event memory.
        
        Args:
            senator_id: Optional ID of the senator this memory belongs to
            use_vectorization: Whether to use vectorized memory for semantic search
        """
        super().__init__()
        
        # Senator identifier for persistence
        self.senator_id = senator_id
        
        # Replace list/dict storage with enhanced memory items
        self.enhanced_event_history: List[EventMemoryItem] = []
        self.enhanced_reaction_history: List[ReactionMemoryItem] = []
        self.enhanced_stance_changes: Dict[str, List[StanceChangeMemoryItem]] = {}
        self.enhanced_event_relationships: Dict[str, List[RelationshipImpactItem]] = {}
        
        # Memory index for efficient retrieval
        self.memory_index = self._create_memory_index()
        
        # Track last memory update time
        self.last_update_time = datetime.datetime.now()
        
        # Optional vectorized memory for semantic search
        self.use_vectorization = use_vectorization
        self.vector_memory = VectorizedMemory() if use_vectorization else None
    
    def _create_memory_index(self) -> MemoryIndex:
        """Create a new memory index."""
        return MemoryIndex(use_framework_index=True)
    
    def record_event(self, event: RomanEvent) -> None:
        """
        Record an observed event in memory with importance weighting.
        
        Args:
            event: The event to record
        """
        # Store in the original EventMemory format if needed
        if hasattr(super(), 'add_event'):
            super().add_event(event)
        
        # Extract source name properly from different source types
        source_repr = "Unknown"
        if event.source:
            if isinstance(event.source, dict) and "name" in event.source:
                source_repr = event.source["name"]
            else:
                source_repr = getattr(event.source, "name", str(event.source))
        
        # Determine importance based on event type and content
        importance = self._calculate_event_importance(event)
        
        # Determine emotional impact
        emotional_impact = self._calculate_emotional_impact(event)
        
        # Generate tags for the event
        tags = self._generate_event_tags(event)
        
        # Create enhanced event memory item
        event_memory = EventMemoryItem(
            event_id=event.event_id,
            event_type=event.event_type,
            source=source_repr,
            metadata=event.metadata.copy(),
            timestamp=datetime.datetime.fromisoformat(event.timestamp) if isinstance(event.timestamp, str) else event.timestamp,
            importance=importance,
            decay_rate=0.1,  # Default decay rate
            tags=tags,
            emotional_impact=emotional_impact
        )
        
        # Add to enhanced event history
        self.enhanced_event_history.append(event_memory)
        
        # Add to memory index
        self.memory_index.add_memory(event_memory)
        
        # Add to vector memory if enabled
        if self.use_vectorization and self.vector_memory:
            self.vector_memory.add_memory(event_memory.to_framework_memory_item())
        
        logger.debug(f"Recorded event {event.event_id} in enhanced memory with importance {importance:.2f}")
    
    def record_reaction(self, event_id: str, reaction_type: str, content: str) -> None:
        """
        Record a reaction to an event with importance weighting.
        
        Args:
            event_id: ID of the event being reacted to
            reaction_type: Type of reaction
            content: Content of the reaction
        """
        # No equivalent in parent EventMemory class
        
        # Determine importance based on reaction type
        importance = self._calculate_reaction_importance(reaction_type)
        
        # Determine emotional impact
        emotional_impact = self._calculate_reaction_emotional_impact(reaction_type)
        
        # Generate tags for the reaction
        tags = ["reaction", reaction_type]
        
        # Create enhanced reaction memory item
        reaction_memory = ReactionMemoryItem(
            event_id=event_id,
            reaction_type=reaction_type,
            content=content,
            timestamp=datetime.datetime.now(),
            importance=importance,
            decay_rate=0.15,  # Reactions decay a bit faster than events
            tags=tags,
            emotional_impact=emotional_impact
        )
        
        # Add to enhanced reaction history
        self.enhanced_reaction_history.append(reaction_memory)
        
        # Add to memory index
        self.memory_index.add_memory(reaction_memory)
        
        # Add to vector memory if enabled
        if self.use_vectorization and self.vector_memory:
            self.vector_memory.add_memory(reaction_memory.to_framework_memory_item())
        
        logger.debug(f"Recorded reaction to event {event_id} in enhanced memory with importance {importance:.2f}")
    
    def record_stance_change(self, topic: str, old_stance: str, new_stance: str, reason: str, event_id: Optional[str] = None) -> None:
        """
        Record a change in stance on a topic with importance weighting.
        
        Args:
            topic: The topic the stance is about
            old_stance: Previous stance
            new_stance: New stance
            reason: Reason for the change
            event_id: Optional ID of the event that triggered the change
        """
        # No equivalent in parent EventMemory class
        
        # Determine importance based on stance change magnitude
        importance = self._calculate_stance_change_importance(old_stance, new_stance)
        
        # Determine emotional impact
        emotional_impact = self._calculate_stance_emotional_impact(old_stance, new_stance)
        
        # Generate tags for the stance change
        tags = ["stance_change", topic]
        
        # Create enhanced stance change memory item
        stance_memory = StanceChangeMemoryItem(
            topic=topic,
            old_stance=old_stance,
            new_stance=new_stance,
            reason=reason,
            event_id=event_id,
            timestamp=datetime.datetime.now(),
            importance=importance,
            decay_rate=0.05,  # Stance changes decay slowly
            tags=tags,
            emotional_impact=emotional_impact
        )
        
        # Add to enhanced stance changes
        if topic not in self.enhanced_stance_changes:
            self.enhanced_stance_changes[topic] = []
        self.enhanced_stance_changes[topic].append(stance_memory)
        
        # Add to memory index
        self.memory_index.add_memory(stance_memory)
        
        # Add to vector memory if enabled
        if self.use_vectorization and self.vector_memory:
            self.vector_memory.add_memory(stance_memory.to_framework_memory_item())
        
        logger.debug(f"Recorded stance change on {topic} in enhanced memory with importance {importance:.2f}")
    
    def record_event_relationship_impact(self, senator_name: str, event_id: str, impact: float, reason: str) -> None:
        """
        Record how an event impacted a relationship with another senator.
        
        Args:
            senator_name: Name of the senator
            event_id: ID of the event that affected the relationship
            impact: Impact on relationship score
            reason: Reason for the impact
        """
        # No equivalent in parent EventMemory class
        
        # Determine importance based on impact magnitude
        importance = 0.5 + abs(impact) * 0.5  # Higher impact = higher importance
        
        # Generate tags for the relationship impact
        tags = ["relationship", senator_name]
        
        # Create enhanced relationship impact memory item
        relationship_memory = RelationshipImpactItem(
            senator_name=senator_name,
            event_id=event_id,
            impact=impact,
            reason=reason,
            timestamp=datetime.datetime.now(),
            importance=importance,
            decay_rate=0.08,  # Relationship impacts decay moderately
            tags=tags,
            emotional_impact=impact  # Direct mapping of impact to emotion
        )
        
        # Add to enhanced event relationships
        if senator_name not in self.enhanced_event_relationships:
            self.enhanced_event_relationships[senator_name] = []
        self.enhanced_event_relationships[senator_name].append(relationship_memory)
        
        # Add to memory index
        self.memory_index.add_memory(relationship_memory)
        
        # Add to vector memory if enabled
        if self.use_vectorization and self.vector_memory:
            self.vector_memory.add_memory(relationship_memory.to_framework_memory_item())
        
        logger.debug(f"Recorded relationship impact with {senator_name} in enhanced memory with importance {importance:.2f}")
    
    def update_memory_strengths(self) -> None:
        """
        Update memory strengths based on time decay.
        
        This should be called periodically to ensure memory strengths are current.
        """
        current_time = datetime.datetime.now()
        self.last_update_time = current_time
        
        # Update memory index to reflect any category changes
        self.memory_index.update_indices()
    
    def prune_weak_memories(self, threshold: float = 0.1) -> int:
        """
        Remove memories with strength below the threshold.
        
        Args:
            threshold: Minimum strength to keep
            
        Returns:
            Number of memories removed
        """
        current_time = datetime.datetime.now()
        removed_count = 0
        
        # Prune event memories
        old_count = len(self.enhanced_event_history)
        self.enhanced_event_history = [
            memory for memory in self.enhanced_event_history
            if memory.get_current_strength(current_time) >= threshold or memory.is_core_memory()
        ]
        removed_count += old_count - len(self.enhanced_event_history)
        
        # Prune reaction memories
        old_count = len(self.enhanced_reaction_history)
        self.enhanced_reaction_history = [
            memory for memory in self.enhanced_reaction_history
            if memory.get_current_strength(current_time) >= threshold or memory.is_core_memory()
        ]
        removed_count += old_count - len(self.enhanced_reaction_history)
        
        # Prune stance change memories
        for topic in list(self.enhanced_stance_changes.keys()):
            old_count = len(self.enhanced_stance_changes[topic])
            self.enhanced_stance_changes[topic] = [
                memory for memory in self.enhanced_stance_changes[topic]
                if memory.get_current_strength(current_time) >= threshold or memory.is_core_memory()
            ]
            removed_count += old_count - len(self.enhanced_stance_changes[topic])
            if not self.enhanced_stance_changes[topic]:
                del self.enhanced_stance_changes[topic]
        
        # Prune relationship impact memories
        for senator in list(self.enhanced_event_relationships.keys()):
            old_count = len(self.enhanced_event_relationships[senator])
            self.enhanced_event_relationships[senator] = [
                memory for memory in self.enhanced_event_relationships[senator]
                if memory.get_current_strength(current_time) >= threshold or memory.is_core_memory()
            ]
            removed_count += old_count - len(self.enhanced_event_relationships[senator])
            if not self.enhanced_event_relationships[senator]:
                del self.enhanced_event_relationships[senator]
        
        # Recreate the memory index
        old_index = self.memory_index
        self.memory_index = self._create_memory_index()
        
        # Re-index all remaining memories
        for memory in self.enhanced_event_history:
            self.memory_index.add_memory(memory)
        for memory in self.enhanced_reaction_history:
            self.memory_index.add_memory(memory)
        for topic_memories in self.enhanced_stance_changes.values():
            for memory in topic_memories:
                self.memory_index.add_memory(memory)
        for senator_memories in self.enhanced_event_relationships.values():
            for memory in senator_memories:
                self.memory_index.add_memory(memory)
        
        logger.info(f"Pruned {removed_count} weak memories with threshold {threshold}")
        return removed_count
    
    def get_relevant_memories(self, context: Dict[str, Any], limit: int = 10) -> List[MemoryBase]:
        """
        Get memories that are relevant to the given context.
        
        Args:
            context: Dictionary of context information
            limit: Maximum number of memories to return
            
        Returns:
            List of relevant memory items
        """
        # Use the memory index to search for relevant memories
        memories = self.memory_index.query({
            "context": context,
            "limit": limit
        })
        
        return memories
    
    def get_memory_narrative(self, context: Dict[str, Any], limit: int = 5) -> str:
        """
        Generate a narrative of relevant memories.
        
        Args:
            context: Dictionary of context information
            limit: Maximum number of memories to include
            
        Returns:
            Narrative text
        """
        # Get relevant memories
        memories = self.get_relevant_memories(context, limit)
        
        if not memories:
            return "I don't recall anything relevant to this context."
        
        # Sort by timestamp (oldest first for narrative flow)
        memories.sort(key=lambda m: m.timestamp)
        
        # Generate narrative
        narrative_parts = []
        
        for memory in memories:
            if isinstance(memory, EventMemoryItem):
                narrative_parts.append(f"I recall an event of type {memory.event_type} from {memory.source}.")
                
                # Add important metadata
                for key, value in memory.metadata.items():
                    if key in ["description", "summary", "content"]:
                        narrative_parts.append(f"The {key} was: {value}")
                
            elif isinstance(memory, ReactionMemoryItem):
                narrative_parts.append(f"I reacted with {memory.reaction_type} to an event.")
                narrative_parts.append(f"My reaction was: {memory.content}")
                
            elif isinstance(memory, StanceChangeMemoryItem):
                narrative_parts.append(f"I changed my stance on {memory.topic} from {memory.old_stance} to {memory.new_stance}.")
                narrative_parts.append(f"This was because: {memory.reason}")
                
            elif isinstance(memory, RelationshipImpactItem):
                direction = "positively" if memory.impact > 0 else "negatively"
                narrative_parts.append(f"My relationship with {memory.senator_name} was {direction} impacted.")
                narrative_parts.append(f"This happened because: {memory.reason}")
        
        return "\n".join(narrative_parts)
    
    def save_to_disk(self, path: Optional[str] = None) -> str:
        """
        Save memory to disk.
        
        Args:
            path: Optional directory path to save in
            
        Returns:
            Path to the saved file
        """
        # Default path
        if path is None:
            path = "saves/memories"
        
        # Ensure the directory exists
        os.makedirs(path, exist_ok=True)
        
        # Set default senator ID if not set
        if not self.senator_id:
            self.senator_id = f"senator_{uuid.uuid4().hex[:8]}"
        
        # Create the file path
        filename = f"{self.senator_id}_memory.json"
        file_path = os.path.join(path, filename)
        
        # Prepare memory data
        memory_data = {
            "senator_id": self.senator_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "event_history": [memory.to_dict() for memory in self.enhanced_event_history],
            "reaction_history": [memory.to_dict() for memory in self.enhanced_reaction_history],
            "stance_changes": {
                topic: [memory.to_dict() for memory in memories]
                for topic, memories in self.enhanced_stance_changes.items()
            },
            "relationship_impacts": {
                senator: [memory.to_dict() for memory in memories]
                for senator, memories in self.enhanced_event_relationships.items()
            }
        }
        
        # Save to file
        with open(file_path, 'w') as f:
            json.dump(memory_data, f, indent=2)
        
        logger.info(f"Saved memory to {file_path}")
        return file_path
    
    def load_from_disk(self, path: Optional[str] = None) -> bool:
        """
        Load memory from disk.
        
        Args:
            path: Optional directory path to load from
            
        Returns:
            True if loaded successfully, False otherwise
        """
        # Default path
        if path is None:
            path = "saves/memories"
        
        # Check if the directory exists
        if not os.path.exists(path):
            logger.warning(f"Memory directory not found: {path}")
            return False
        
        # Create the file path
        if not self.senator_id:
            logger.warning("Cannot load memory without senator_id")
            return False
        
        filename = f"{self.senator_id}_memory.json"
        file_path = os.path.join(path, filename)
        
        # Check if the file exists
        if not os.path.exists(file_path):
            logger.warning(f"Memory file not found: {file_path}")
            return False
        
        try:
            # Load from file
            with open(file_path, 'r') as f:
                memory_data = json.load(f)
            
            # Clear current memories
            self.enhanced_event_history.clear()
            self.enhanced_reaction_history.clear()
            self.enhanced_stance_changes.clear()
            self.enhanced_event_relationships.clear()
            
            # Load event history
            for event_data in memory_data.get("event_history", []):
                event_memory = create_memory_from_dict(event_data)
                self.enhanced_event_history.append(event_memory)
            
            # Load reaction history
            for reaction_data in memory_data.get("reaction_history", []):
                reaction_memory = create_memory_from_dict(reaction_data)
                self.enhanced_reaction_history.append(reaction_memory)
            
            # Load stance changes
            for topic, stance_data_list in memory_data.get("stance_changes", {}).items():
                self.enhanced_stance_changes[topic] = [
                    create_memory_from_dict(stance_data)
                    for stance_data in stance_data_list
                ]
            
            # Load relationship impacts
            for senator, relation_data_list in memory_data.get("relationship_impacts", {}).items():
                self.enhanced_event_relationships[senator] = [
                    create_memory_from_dict(relation_data)
                    for relation_data in relation_data_list
                ]
            
            # Recreate the memory index
            self.memory_index = self._create_memory_index()
            
            # Re-index all memories
            for memory in self.enhanced_event_history:
                self.memory_index.add_memory(memory)
            for memory in self.enhanced_reaction_history:
                self.memory_index.add_memory(memory)
            for topic_memories in self.enhanced_stance_changes.values():
                for memory in topic_memories:
                    self.memory_index.add_memory(memory)
            for senator_memories in self.enhanced_event_relationships.values():
                for memory in senator_memories:
                    self.memory_index.add_memory(memory)
            
            # If using vectorization, add to vector memory
            if self.use_vectorization and self.vector_memory:
                for memory in self.enhanced_event_history:
                    self.vector_memory.add_memory(memory.to_framework_memory_item())
                for memory in self.enhanced_reaction_history:
                    self.vector_memory.add_memory(memory.to_framework_memory_item())
                for topic_memories in self.enhanced_stance_changes.values():
                    for memory in topic_memories:
                        self.vector_memory.add_memory(memory.to_framework_memory_item())
                for senator_memories in self.enhanced_event_relationships.values():
                    for memory in senator_memories:
                        self.vector_memory.add_memory(memory.to_framework_memory_item())
            
            logger.info(f"Loaded memory from {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading memory from {file_path}: {e}")
            return False
    
    def merge_with(self, other_memory: 'EnhancedEventMemory') -> None:
        """
        Merge another memory into this one.
        
        Args:
            other_memory: The memory to merge in
        """
        # Merge event histories, avoiding duplicates by event_id
        existing_event_ids = {event.event_id for event in self.enhanced_event_history}
        for event in other_memory.enhanced_event_history:
            if event.event_id not in existing_event_ids:
                self.enhanced_event_history.append(event)
                self.memory_index.add_memory(event)
                existing_event_ids.add(event.event_id)
        
        # Merge reaction histories, avoiding exact duplicates
        existing_reactions = {(reaction.event_id, reaction.reaction_type, reaction.content)
                             for reaction in self.enhanced_reaction_history}
        for reaction in other_memory.enhanced_reaction_history:
            key = (reaction.event_id, reaction.reaction_type, reaction.content)
            if key not in existing_reactions:
                self.enhanced_reaction_history.append(reaction)
                self.memory_index.add_memory(reaction)
                existing_reactions.add(key)
        
        # Merge stance changes
        for topic, other_stances in other_memory.enhanced_stance_changes.items():
            if topic not in self.enhanced_stance_changes:
                self.enhanced_stance_changes[topic] = []
            
            # Get existing stance changes for this topic
            existing_stance_changes = {(stance.old_stance, stance.new_stance, stance.reason)
                                     for stance in self.enhanced_stance_changes[topic]}
            
            # Add new stance changes
            for stance in other_stances:
                key = (stance.old_stance, stance.new_stance, stance.reason)
                if key not in existing_stance_changes:
                    self.enhanced_stance_changes[topic].append(stance)
                    self.memory_index.add_memory(stance)
                    existing_stance_changes.add(key)
        
        # Merge relationship impacts
        for senator, other_impacts in other_memory.enhanced_event_relationships.items():
            if senator not in self.enhanced_event_relationships:
                self.enhanced_event_relationships[senator] = []
            
            # Get existing relationship impacts for this senator
            existing_impacts = {(impact.event_id, impact.impact, impact.reason)
                             for impact in self.enhanced_event_relationships[senator]}
            
            # Add new relationship impacts
            for impact in other_impacts:
                key = (impact.event_id, impact.impact, impact.reason)
                if key not in existing_impacts:
                    self.enhanced_event_relationships[senator].append(impact)
                    self.memory_index.add_memory(impact)
                    existing_impacts.add(key)
    
    def _calculate_event_importance(self, event: RomanEvent) -> float:
        """
        Calculate the importance of an event.
        
        Args:
            event: The event to calculate importance for
            
        Returns:
            Importance score (0.0-1.0)
        """
        # Define base importance by event type
        base_importance = {
            "speech": 0.4,
            "vote": 0.6,
            "proposal": 0.5,
            "scandal": 0.7,
            "military_news": 0.6,
            "religious_event": 0.5,
            "relationship_change": 0.6,
            "stance_change": 0.5,
            "alliance_formed": 0.7,
            "rivalry_declared": 0.7,
            "election_result": 0.8
        }
        
        # Default importance if event type is not in the dictionary
        importance = base_importance.get(event.event_type, 0.5)
        
        # Adjust importance based on metadata
        if "importance" in event.metadata:
            # If the event has its own importance score, blend it with our calculated score
            event_importance = float(event.metadata["importance"])
            importance = (importance + event_importance) / 2
        
        # Check if this is a core memory that should never decay
        if event.metadata.get("core_memory", False):
            importance = max(importance, 0.9)  # Ensure core memories have high importance
        
        # Check if this is directed specifically at the agent
        if "target" in event.metadata and event.metadata["target"] == self.senator_id:
            importance += 0.2  # Increase importance for events targeting this agent
        
        # Clamp the importance to the valid range
        return max(0.0, min(1.0, importance))
    
    def _calculate_emotional_impact(self, event: RomanEvent) -> float:
        """
        Calculate the emotional impact of an event.
        
        Args:
            event: The event to calculate emotional impact for
            
        Returns:
            Emotional impact score (-1.0 to 1.0)
        """
        # If the event has an explicit emotional_impact in metadata, use that
        if "emotional_impact" in event.metadata:
            try:
                return float(event.metadata["emotional_impact"])
            except (ValueError, TypeError):
                pass
        
        # Default neutral emotional impact
        emotional_impact = 0.0
        
        # Infer emotional impact from event type and metadata
        if event.event_type in ["scandal", "attack", "rivalry_declared"]:
            emotional_impact = -0.5  # Negative emotions
        elif event.event_type in ["alliance_formed", "praise", "election_win"]:
            emotional_impact = 0.5  # Positive emotions
        
        # Adjust based on event outcome if available
        if "outcome" in event.metadata:
            outcome = event.metadata["outcome"]
            if outcome in ["success", "victory", "praise"]:
                emotional_impact += 0.3
            elif outcome in ["failure", "defeat", "criticism"]:
                emotional_impact -= 0.3
        
        # Adjust based on personal involvement
        if "target" in event.metadata and event.metadata["target"] == self.senator_id:
            # Amplify emotional impact for personally targeted events
            emotional_impact *= 1.5
        
        # Clamp to the valid range
        return max(-1.0, min(1.0, emotional_impact))
    
    def _generate_event_tags(self, event: RomanEvent) -> List[str]:
        """
        Generate tags for an event.
        
        Args:
            event: The event to generate tags for
            
        Returns:
            List of tags
        """
        tags = [event.event_type]
        
        # Add source as a tag if it's a string
        if event.source and isinstance(event.source, str):
            tags.append(event.source)
        elif event.source and isinstance(event.source, dict) and "name" in event.source:
            tags.append(event.source["name"])
        
        # Add target as a tag if it exists
        if "target" in event.metadata and event.metadata["target"]:
            tags.append(event.metadata["target"])
        
        # Add location as a tag if it exists
        if "location" in event.metadata and event.metadata["location"]:
            tags.append(event.metadata["location"])
        
        # Add topic as a tag if it exists
        if "topic" in event.metadata and event.metadata["topic"]:
            tags.append(event.metadata["topic"])
            
        # Add tags from metadata if they exist
        if "tags" in event.metadata and isinstance(event.metadata["tags"], list):
            tags.extend(event.metadata["tags"])
        
        return tags
    
    def _calculate_reaction_importance(self, reaction_type: str) -> float:
        """
        Calculate the importance of a reaction.
        
        Args:
            reaction_type: The type of reaction
            
        Returns:
            Importance score (0.0-1.0)
        """
        # Define base importance by reaction type
        base_importance = {
            "support": 0.5,
            "oppose": 0.6,
            "neutral": 0.3,
            "outrage": 0.8,
            "praise": 0.6,
            "criticism": 0.7,
            "speech": 0.5,
            "vote": 0.7
        }
        
        # Default importance if reaction type is not in the dictionary
        return base_importance.get(reaction_type, 0.5)
    
    def _calculate_reaction_emotional_impact(self, reaction_type: str) -> float:
        """
        Calculate the emotional impact of a reaction.
        
        Args:
            reaction_type: The type of reaction
            
        Returns:
            Emotional impact score (-1.0 to 1.0)
        """
        # Map reaction types to emotional impacts
        emotional_impacts = {
            "support": 0.3,
            "oppose": -0.3,
            "neutral": 0.0,
            "outrage": -0.8,
            "praise": 0.7,
            "criticism": -0.5,
            "speech": 0.2,
            "vote": 0.1
        }
        
        # Default to neutral if reaction type is not in the dictionary
        return emotional_impacts.get(reaction_type, 0.0)
    
    def _calculate_stance_change_importance(self, old_stance: str, new_stance: str) -> float:
        """
        Calculate the importance of a stance change.
        
        Args:
            old_stance: The previous stance
            new_stance: The new stance
            
        Returns:
            Importance score (0.0-1.0)
        """
        # Define stance value mapping
        stance_values = {
            "strongly_oppose": -2,
            "oppose": -1,
            "neutral": 0,
            "support": 1,
            "strongly_support": 2
        }
        
        # Get numerical values for old and new stances
        old_value = stance_values.get(old_stance, 0)
        new_value = stance_values.get(new_stance, 0)
        
        # Calculate change magnitude
        change_magnitude = abs(new_value - old_value)
        
        # Map change magnitude to importance
        if change_magnitude >= 4:  # Extreme change
            return 0.9
        elif change_magnitude >= 3:  # Large change
            return 0.8
        elif change_magnitude >= 2:  # Moderate change
            return 0.7
        elif change_magnitude >= 1:  # Small change
            return 0.6
        else:  # Minimal change
            return 0.5
    
    def _calculate_stance_emotional_impact(self, old_stance: str, new_stance: str) -> float:
        """
        Calculate the emotional impact of a stance change.
        
        Args:
            old_stance: The previous stance
            new_stance: The new stance
            
        Returns:
            Emotional impact score (-1.0 to 1.0)
        """
        # Define stance value mapping
        stance_values = {
            "strongly_oppose": -2,
            "oppose": -1,
            "neutral": 0,
            "support": 1,
            "strongly_support": 2
        }
        
        # Get numerical values for old and new stances
        old_value = stance_values.get(old_stance, 0)
        new_value = stance_values.get(new_stance, 0)
        
        # Calculate direction and magnitude of change
        change = new_value - old_value
        
        # Map change to emotional impact
        # Positive change is positive emotion, negative change is negative emotion
        # Scale to fit in the -1.0 to 1.0 range
        return max(-1.0, min(1.0, change / 4.0))
    
    # MemoryInterface implementation for framework compatibility
    
    def add_memory(self, memory_item: Union[MemoryBase, BaseEventMemoryItem]) -> str:
        """
        Add a memory item to the memory store.
        
        Args:
            memory_item: The memory item to add
            
        Returns:
            The ID of the added memory item
        """
        # If it's a framework memory item, convert it
        if hasattr(memory_item, 'content') and not isinstance(memory_item, MemoryBase):
            if hasattr(memory_item, 'event_type'):
                from .memory_items import EventMemoryItem
                memory_item = EventMemoryItem.from_framework_event_memory_item(memory_item)
            else:
                memory_item = MemoryBase.from_framework_memory_item(memory_item)
        
        # Add to our memory based on type
        if hasattr(memory_item, 'event_type'):
            self.enhanced_event_history.append(memory_item)
        elif hasattr(memory_item, 'reaction_type'):
            self.enhanced_reaction_history.append(memory_item)
        elif hasattr(memory_item, 'topic') and hasattr(memory_item, 'old_stance'):
            topic = memory_item.topic
            if topic not in self.enhanced_stance_changes:
                self.enhanced_stance_changes[topic] = []
            self.enhanced_stance_changes[topic].append(memory_item)
        elif hasattr(memory_item, 'senator_name') and hasattr(memory_item, 'impact'):
            senator = memory_item.senator_name
            if senator not in self.enhanced_event_relationships:
                self.enhanced_event_relationships[senator] = []
            self.enhanced_event_relationships[senator].append(memory_item)
        
        # Add to memory index
        self.memory_index.add_memory(memory_item)
        
        # Add to vector memory if enabled
        if self.use_vectorization and self.vector_memory:
            if hasattr(memory_item, 'to_framework_memory_item'):
                framework_item = memory_item.to_framework_memory_item()
            else:
                framework_item = memory_item
            self.vector_memory.add_memory(framework_item)
        
        return memory_item.id
    
    def retrieve_memories(
        self, 
        query: Dict[str, Any], 
        limit: Optional[int] = None,
        importance_threshold: Optional[float] = None
    ) -> List[MemoryBase]:
        """
        Retrieve memories that match the given query.
        
        Args:
            query: Dictionary of search criteria
            limit: Maximum number of memories to return
            importance_threshold: Minimum importance score for returned memories
            
        Returns:
            List of matching memory items
        """
        # Add limit to query if provided
        if limit is not None:
            query["limit"] = limit
        
        # Add importance threshold to query if provided
        if importance_threshold is not None:
            query["min_strength"] = importance_threshold
        
        # Use our memory index for the query
        return self.memory_index.query(query)
    
    def get_memory(self, memory_id: str) -> Optional[MemoryBase]:
        """
        Get a specific memory by ID.
        
        Args:
            memory_id: ID of the memory to retrieve
            
        Returns:
            Optional[MemoryBase]: The memory item, or None if not found
        """
        return self.memory_index.get_memory(memory_id)
    
    def update_memory(self, memory_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update a memory item.
        
        Args:
            memory_id: ID of the memory to update
            updates: Dictionary of fields to update
            
        Returns:
            bool: True if the memory was updated, False if not found
        """
        memory = self.memory_index.get_memory(memory_id)
        if not memory:
            return False
        
        # Update memory attributes
        for key, value in updates.items():
            if key == "importance":
                memory.update_importance(value)
            elif hasattr(memory, key):
                setattr(memory, key, value)
        
        # Update in memory index
        self.memory_index.update_memory(memory)
        
        # Update in vector memory if enabled
        if self.use_vectorization and self.vector_memory:
            if hasattr(memory, 'to_framework_memory_item'):
                framework_item = memory.to_framework_memory_item()
                self.vector_memory.update_memory(memory_id, framework_item.to_dict())
        
        return True
    
    def forget(self, memory_id: str) -> bool:
        """
        Remove a memory from the memory store.
        
        Args:
            memory_id: ID of the memory to forget
            
        Returns:
            bool: True if the memory was forgotten, False if not found
        """
        memory = self.memory_index.get_memory(memory_id)
        if not memory:
            return False
        
        # Remove from the appropriate collection
        if hasattr(memory, 'event_type'):
            if memory in self.enhanced_event_history:
                self.enhanced_event_history.remove(memory)
        elif hasattr(memory, 'reaction_type'):
            if memory in self.enhanced_reaction_history:
                self.enhanced_reaction_history.remove(memory)
        elif hasattr(memory, 'topic') and hasattr(memory, 'old_stance'):
            topic = memory.topic
            if topic in self.enhanced_stance_changes:
                if memory in self.enhanced_stance_changes[topic]:
                    self.enhanced_stance_changes[topic].remove(memory)
                if not self.enhanced_stance_changes[topic]:
                    del self.enhanced_stance_changes[topic]
        elif hasattr(memory, 'senator_name') and hasattr(memory, 'impact'):
            senator = memory.senator_name
            if senator in self.enhanced_event_relationships:
                if memory in self.enhanced_event_relationships[senator]:
                    self.enhanced_event_relationships[senator].remove(memory)
                if not self.enhanced_event_relationships[senator]:
                    del self.enhanced_event_relationships[senator]
        
        # Remove from memory index
        self.memory_index.remove_memory(memory)
        
        # Remove from vector memory if enabled
        if self.use_vectorization and self.vector_memory:
            self.vector_memory.forget(memory_id)
        
        return True
    
    def clear(self) -> None:
        """
        Clear all memories from the memory store.
        """
        self.enhanced_event_history.clear()
        self.enhanced_reaction_history.clear()
        self.enhanced_stance_changes.clear()
        self.enhanced_event_relationships.clear()
        
        # Clear memory index
        self.memory_index = self._create_memory_index()
        
        # Clear vector memory if enabled
        if self.use_vectorization and self.vector_memory:
            self.vector_memory.clear()