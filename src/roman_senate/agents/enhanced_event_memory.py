"""
Roman Senate AI Game
Enhanced Event Memory Module

This module provides an enhanced version of the EventMemory class
with support for memory decay, importance weighting, and efficient retrieval.
"""

import os
import json
import datetime
import logging
from typing import Dict, List, Any, Optional, Set, Tuple
from pathlib import Path

from .agent_memory import AgentMemory
from .event_memory import EventMemory
from .memory_base import MemoryBase
from .memory_items import (
    EventMemoryItem,
    ReactionMemoryItem,
    StanceChangeMemoryItem,
    RelationshipImpactItem
)
from .memory_index import MemoryIndex
from ..core.events import Event

logger = logging.getLogger(__name__)


class EnhancedEventMemory(EventMemory):
    """
    Enhanced memory for event-driven senator agents with persistence and decay.
    
    This class extends the EventMemory with:
    - Memory importance weighting
    - Time-based memory decay
    - Efficient memory indexing and retrieval
    - Persistence to disk
    - Memory consolidation
    """
    
    def __init__(self, senator_id: Optional[str] = None):
        """
        Initialize an enhanced event memory.
        
        Args:
            senator_id: Optional ID of the senator this memory belongs to
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
        self.memory_index = MemoryIndex()
        
        # Track last memory update time
        self.last_update_time = datetime.datetime.now()
    
    def record_event(self, event: Event) -> None:
        """
        Record an observed event in memory with importance weighting.
        
        Args:
            event: The event to record
        """
        # Call the parent method to maintain backward compatibility
        super().record_event(event)
        
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
            timestamp=datetime.datetime.fromisoformat(event.timestamp),
            importance=importance,
            decay_rate=0.1,  # Default decay rate
            tags=tags,
            emotional_impact=emotional_impact
        )
        
        # Add to enhanced event history
        self.enhanced_event_history.append(event_memory)
        
        # Add to memory index
        self.memory_index.add_memory(event_memory)
        
        logger.debug(f"Recorded event {event.event_id} in enhanced memory with importance {importance:.2f}")
    
    def record_reaction(self, event_id: str, reaction_type: str, content: str) -> None:
        """
        Record a reaction to an event with importance weighting.
        
        Args:
            event_id: ID of the event being reacted to
            reaction_type: Type of reaction
            content: Content of the reaction
        """
        # Call the parent method to maintain backward compatibility
        super().record_reaction(event_id, reaction_type, content)
        
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
        # Call the parent method to maintain backward compatibility
        super().record_stance_change(topic, old_stance, new_stance, reason, event_id)
        
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
        # Call the parent method to maintain backward compatibility
        super().record_event_relationship_impact(senator_name, event_id, impact, reason)
        
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
        
        logger.debug("Updated memory strengths based on time decay")
    
    def prune_weak_memories(self, threshold: float = 0.1) -> int:
        """
        Remove memories that have decayed below the threshold.
        
        Args:
            threshold: Minimum strength to keep
            
        Returns:
            Number of memories removed
        """
        # Ensure memory strengths are up to date
        self.update_memory_strengths()
        
        # Use the memory index to prune weak memories
        removed_count = self.memory_index.prune_weak_memories(threshold)
        
        # Update our internal lists to match
        current_time = datetime.datetime.now()
        
        # Prune event history
        self.enhanced_event_history = [
            m for m in self.enhanced_event_history
            if m.get_current_strength(current_time) >= threshold
        ]
        
        # Prune reaction history
        self.enhanced_reaction_history = [
            m for m in self.enhanced_reaction_history
            if m.get_current_strength(current_time) >= threshold
        ]
        
        # Prune stance changes
        for topic in list(self.enhanced_stance_changes.keys()):
            self.enhanced_stance_changes[topic] = [
                m for m in self.enhanced_stance_changes[topic]
                if m.get_current_strength(current_time) >= threshold
            ]
            # Remove empty topics
            if not self.enhanced_stance_changes[topic]:
                del self.enhanced_stance_changes[topic]
        
        # Prune relationship impacts
        for senator in list(self.enhanced_event_relationships.keys()):
            self.enhanced_event_relationships[senator] = [
                m for m in self.enhanced_event_relationships[senator]
                if m.get_current_strength(current_time) >= threshold
            ]
            # Remove empty relationships
            if not self.enhanced_event_relationships[senator]:
                del self.enhanced_event_relationships[senator]
        
        logger.debug(f"Pruned {removed_count} weak memories below threshold {threshold}")
        return removed_count
    
    def get_relevant_memories(self, context: Dict[str, Any], limit: int = 10) -> List[MemoryBase]:
        """
        Get memories relevant to the current context.
        
        Args:
            context: Dictionary of context information
            limit: Maximum number of memories to return
            
        Returns:
            List of relevant memories
        """
        # Ensure memory strengths are up to date
        self.update_memory_strengths()
        
        # Query the memory index
        memories = self.memory_index.query({
            "context": context,
            "min_strength": 0.2  # Only include reasonably strong memories
        })
        
        return memories[:limit]
    
    def get_memory_narrative(self, context: Dict[str, Any], limit: int = 5) -> str:
        """
        Generate a narrative summary of relevant memories.
        
        Args:
            context: Dictionary of context information
            limit: Maximum number of memories to include
            
        Returns:
            Narrative text summarizing relevant memories
        """
        memories = self.get_relevant_memories(context, limit)
        
        if not memories:
            return "I don't recall anything relevant to this situation."
        
        narrative_parts = ["I recall:"]
        
        for memory in memories:
            if isinstance(memory, EventMemoryItem):
                narrative_parts.append(
                    f"- A {memory.event_type} event from {memory.source}"
                )
            elif isinstance(memory, ReactionMemoryItem):
                narrative_parts.append(
                    f"- Reacting with {memory.reaction_type} to an event"
                )
            elif isinstance(memory, StanceChangeMemoryItem):
                narrative_parts.append(
                    f"- Changing my stance on {memory.topic} from {memory.old_stance} to {memory.new_stance} because {memory.reason}"
                )
            elif isinstance(memory, RelationshipImpactItem):
                impact_type = "positively" if memory.impact > 0 else "negatively"
                narrative_parts.append(
                    f"- Being {impact_type} affected by {memory.senator_name} because {memory.reason}"
                )
        
        return "\n".join(narrative_parts)
    
    def save_to_disk(self, path: Optional[str] = None) -> str:
        """
        Save memory to disk.
        
        Args:
            path: Optional directory path to save to
            
        Returns:
            Path to the saved file
        """
        if not self.senator_id:
            raise ValueError("Cannot save memory without a senator_id")
        
        # Default path is in the saves directory
        if not path:
            path = os.path.join("saves", "memories")
        
        # Ensure directory exists
        os.makedirs(path, exist_ok=True)
        
        # Create filename based on senator ID
        filename = f"{self.senator_id}_memory.json"
        full_path = os.path.join(path, filename)
        
        # Serialize all memory items
        memory_data = {
            "senator_id": self.senator_id,
            "saved_at": datetime.datetime.now().isoformat(),
            "events": [m.to_dict() for m in self.enhanced_event_history],
            "reactions": [m.to_dict() for m in self.enhanced_reaction_history],
            "stance_changes": {
                topic: [m.to_dict() for m in memories]
                for topic, memories in self.enhanced_stance_changes.items()
            },
            "relationship_impacts": {
                senator: [m.to_dict() for m in memories]
                for senator, memories in self.enhanced_event_relationships.items()
            }
        }
        
        # Write to file
        with open(full_path, "w", encoding="utf-8") as f:
            json.dump(memory_data, f, indent=2)
        
        logger.info(f"Saved enhanced memory to {full_path}")
        return full_path
    
    def load_from_disk(self, path: Optional[str] = None) -> bool:
        """
        Load memory from disk.
        
        Args:
            path: Optional directory path to load from
            
        Returns:
            True if loaded successfully, False otherwise
        """
        if not self.senator_id:
            raise ValueError("Cannot load memory without a senator_id")
        
        # Default path is in the saves directory
        if not path:
            path = os.path.join("saves", "memories")
        
        # Create filename based on senator ID
        filename = f"{self.senator_id}_memory.json"
        full_path = os.path.join(path, filename)
        
        # Check if file exists
        if not os.path.exists(full_path):
            logger.warning(f"Memory file not found: {full_path}")
            return False
        
        try:
            # Read from file
            with open(full_path, "r", encoding="utf-8") as f:
                memory_data = json.load(f)
            
            # Clear existing memories
            self.enhanced_event_history.clear()
            self.enhanced_reaction_history.clear()
            self.enhanced_stance_changes.clear()
            self.enhanced_event_relationships.clear()
            
            # Deserialize event memories
            for event_data in memory_data.get("events", []):
                event_memory = EventMemoryItem.from_dict(event_data)
                self.enhanced_event_history.append(event_memory)
                self.memory_index.add_memory(event_memory)
            
            # Deserialize reaction memories
            for reaction_data in memory_data.get("reactions", []):
                reaction_memory = ReactionMemoryItem.from_dict(reaction_data)
                self.enhanced_reaction_history.append(reaction_memory)
                self.memory_index.add_memory(reaction_memory)
            
            # Deserialize stance change memories
            for topic, stance_changes in memory_data.get("stance_changes", {}).items():
                self.enhanced_stance_changes[topic] = []
                for stance_data in stance_changes:
                    stance_memory = StanceChangeMemoryItem.from_dict(stance_data)
                    self.enhanced_stance_changes[topic].append(stance_memory)
                    self.memory_index.add_memory(stance_memory)
            
            # Deserialize relationship impact memories
            for senator, impacts in memory_data.get("relationship_impacts", {}).items():
                self.enhanced_event_relationships[senator] = []
                for impact_data in impacts:
                    impact_memory = RelationshipImpactItem.from_dict(impact_data)
                    self.enhanced_event_relationships[senator].append(impact_memory)
                    self.memory_index.add_memory(impact_memory)
            
            # Update memory strengths
            self.update_memory_strengths()
            
            logger.info(f"Loaded enhanced memory from {full_path}")
            return True
        
        except Exception as e:
            logger.error(f"Error loading memory from {full_path}: {e}")
            return False
    
    def merge_with(self, other_memory: 'EnhancedEventMemory') -> None:
        """
        Merge another memory into this one.
        
        Args:
            other_memory: The memory to merge in
        """
        # Merge event history
        for event_memory in other_memory.enhanced_event_history:
            if event_memory not in self.enhanced_event_history:
                self.enhanced_event_history.append(event_memory)
                self.memory_index.add_memory(event_memory)
        
        # Merge reaction history
        for reaction_memory in other_memory.enhanced_reaction_history:
            if reaction_memory not in self.enhanced_reaction_history:
                self.enhanced_reaction_history.append(reaction_memory)
                self.memory_index.add_memory(reaction_memory)
        
        # Merge stance changes
        for topic, stance_changes in other_memory.enhanced_stance_changes.items():
            if topic not in self.enhanced_stance_changes:
                self.enhanced_stance_changes[topic] = []
            for stance_memory in stance_changes:
                if stance_memory not in self.enhanced_stance_changes[topic]:
                    self.enhanced_stance_changes[topic].append(stance_memory)
                    self.memory_index.add_memory(stance_memory)
        
        # Merge relationship impacts
        for senator, impacts in other_memory.enhanced_event_relationships.items():
            if senator not in self.enhanced_event_relationships:
                self.enhanced_event_relationships[senator] = []
            for impact_memory in impacts:
                if impact_memory not in self.enhanced_event_relationships[senator]:
                    self.enhanced_event_relationships[senator].append(impact_memory)
                    self.memory_index.add_memory(impact_memory)
        
        logger.info("Merged memories successfully")
    
    def _calculate_event_importance(self, event: Event) -> float:
        """
        Calculate the importance of an event.
        
        Args:
            event: The event to evaluate
            
        Returns:
            Importance value between 0.0 and 1.0
        """
        # Base importance by event type
        base_importance = {
            "speech": 0.5,
            "debate_start": 0.6,
            "debate_end": 0.4,
            "vote": 0.7,
            "interjection": 0.6,
            "reaction": 0.3
        }.get(event.event_type, 0.5)
        
        # Adjust based on metadata
        if hasattr(event, "metadata"):
            # Important topics increase importance
            if "topic" in event.metadata:
                topic = event.metadata["topic"]
                if any(keyword in topic.lower() for keyword in ["war", "crisis", "emergency", "scandal"]):
                    base_importance += 0.2
            
            # Strong stances increase importance
            if "stance" in event.metadata:
                stance = event.metadata["stance"]
                if stance in ["strongly_support", "strongly_oppose"]:
                    base_importance += 0.1
        
        # Ensure the result is between 0 and 1
        return max(0.0, min(1.0, base_importance))
    
    def _calculate_emotional_impact(self, event: Event) -> float:
        """
        Calculate the emotional impact of an event.
        
        Args:
            event: The event to evaluate
            
        Returns:
            Emotional impact value between -1.0 and 1.0
        """
        # Default neutral impact
        impact = 0.0
        
        # Adjust based on event type
        if event.event_type == "interjection":
            # Interjections often have negative emotional impact
            impact -= 0.3
        elif event.event_type == "vote":
            # Votes can be positive or negative depending on outcome
            if "outcome" in event.metadata:
                if event.metadata["outcome"] == "passed":
                    impact = 0.5
                else:
                    impact = -0.3
        
        # Adjust based on metadata
        if hasattr(event, "metadata"):
            # Emotional content in speeches
            if "emotional_tone" in event.metadata:
                tone = event.metadata["emotional_tone"]
                if tone == "positive":
                    impact += 0.3
                elif tone == "negative":
                    impact -= 0.3
                elif tone == "neutral":
                    impact += 0.0
        
        # Ensure the result is between -1 and 1
        return max(-1.0, min(1.0, impact))
    
    def _generate_event_tags(self, event: Event) -> List[str]:
        """
        Generate tags for an event.
        
        Args:
            event: The event to tag
            
        Returns:
            List of tags
        """
        tags = [event.event_type]
        
        # Add source as a tag if it's a string
        if isinstance(event.source, str):
            tags.append(event.source)
        elif hasattr(event.source, "name"):
            tags.append(event.source.name)
        elif isinstance(event.source, dict) and "name" in event.source:
            tags.append(event.source["name"])
        
        # Add metadata-based tags
        if hasattr(event, "metadata"):
            # Add topic as a tag
            if "topic" in event.metadata:
                tags.append(event.metadata["topic"])
            
            # Add stance as a tag
            if "stance" in event.metadata:
                tags.append(event.metadata["stance"])
        
        return tags
    
    def _calculate_reaction_importance(self, reaction_type: str) -> float:
        """
        Calculate the importance of a reaction.
        
        Args:
            reaction_type: Type of reaction
            
        Returns:
            Importance value between 0.0 and 1.0
        """
        # Base importance by reaction type
        return {
            "agreement": 0.4,
            "disagreement": 0.6,
            "interest": 0.3,
            "boredom": 0.2,
            "skepticism": 0.5,
            "surprise": 0.7,
            "anger": 0.8
        }.get(reaction_type, 0.4)
    
    def _calculate_reaction_emotional_impact(self, reaction_type: str) -> float:
        """
        Calculate the emotional impact of a reaction.
        
        Args:
            reaction_type: Type of reaction
            
        Returns:
            Emotional impact value between -1.0 and 1.0
        """
        # Emotional impact by reaction type
        return {
            "agreement": 0.5,
            "disagreement": -0.5,
            "interest": 0.3,
            "boredom": -0.2,
            "skepticism": -0.3,
            "surprise": 0.0,  # Surprise can be positive or negative
            "anger": -0.8
        }.get(reaction_type, 0.0)
    
    def _calculate_stance_change_importance(self, old_stance: str, new_stance: str) -> float:
        """
        Calculate the importance of a stance change.
        
        Args:
            old_stance: Previous stance
            new_stance: New stance
            
        Returns:
            Importance value between 0.0 and 1.0
        """
        # Map stances to numeric values
        stance_values = {
            "strongly_oppose": -2,
            "oppose": -1,
            "neutral": 0,
            "support": 1,
            "strongly_support": 2
        }
        
        # Calculate the magnitude of the change
        if old_stance in stance_values and new_stance in stance_values:
            old_value = stance_values[old_stance]
            new_value = stance_values[new_stance]
            change_magnitude = abs(new_value - old_value)
            
            # Scale to 0.0-1.0 range (max change is 4 steps)
            importance = 0.5 + (change_magnitude / 8.0)
        else:
            # Default importance for unknown stances
            importance = 0.6
        
        return importance
    
    def _calculate_stance_emotional_impact(self, old_stance: str, new_stance: str) -> float:
        """
        Calculate the emotional impact of a stance change.
        
        Args:
            old_stance: Previous stance
            new_stance: New stance
            
        Returns:
            Emotional impact value between -1.0 and 1.0
        """
        # Map stances to numeric values
        stance_values = {
            "strongly_oppose": -2,
            "oppose": -1,
            "neutral": 0,
            "support": 1,
            "strongly_support": 2
        }
        
        # Calculate the direction of the change
        if old_stance in stance_values and new_stance in stance_values:
            old_value = stance_values[old_stance]
            new_value = stance_values[new_stance]
            change = new_value - old_value
            
            # Scale to -1.0 to 1.0 range (max change is 4 steps)
            emotional_impact = change / 4.0
        else:
            # Default neutral impact for unknown stances
            emotional_impact = 0.0
        
        return emotional_impact