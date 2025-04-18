"""
Roman Senate Simulation
Relationship Processor Module

This module provides the RelationshipProcessor class, which manages relationships
between entities in the narrative.
"""

import logging
import random
from typing import Dict, List, Any, Tuple, Set

from roman_senate.core.game_state import GameState
from roman_senate.core.narrative_context import NarrativeContext, NarrativeEvent
from roman_senate.core.event_manager import EventProcessor

logger = logging.getLogger(__name__)

class RelationshipProcessor(EventProcessor):
    """
    Manages relationships between entities in the narrative.
    
    This processor:
    1. Tracks relationships between entities
    2. Updates relationship status based on events
    3. Ensures relationship consistency
    4. Connects events to Senate topics when appropriate
    """
    
    def __init__(self):
        """Initialize the relationship processor."""
        self.relationship_types = [
            "ally", "rival", "friend", "enemy", "patron", "client",
            "family", "colleague", "competitor", "neutral"
        ]
        self.relationship_strengths = {
            "strong": 3,
            "moderate": 2,
            "weak": 1
        }
        logger.info("RelationshipProcessor initialized")
    
    def process_event(self, event: NarrativeEvent, game_state: GameState, 
                     narrative_context: NarrativeContext) -> NarrativeEvent:
        """
        Process a narrative event to manage relationships.
        
        Args:
            event: The narrative event to process
            game_state: The current game state
            narrative_context: The current narrative context
            
        Returns:
            The processed narrative event
        """
        # Only process events with multiple entities
        if len(event.entities) < 2:
            return event
        
        # Extract relationships from the event
        relationships = self._extract_relationships(event)
        
        # Update the event with relationship information
        event = self._update_event_with_relationships(event, relationships)
        
        # Connect to Senate topics if appropriate
        event = self._connect_to_senate_topics(event, game_state)
        
        logger.debug(f"Processed event for relationships: {event.id}")
        return event
    
    def _extract_relationships(self, event: NarrativeEvent) -> List[Dict[str, Any]]:
        """
        Extract relationships from the event description.
        
        Args:
            event: The event to analyze
            
        Returns:
            List of relationship dictionaries
        """
        relationships = []
        entities = event.entities
        
        # For each pair of entities, determine if there's a relationship
        for i in range(len(entities)):
            for j in range(i + 1, len(entities)):
                entity1 = entities[i]
                entity2 = entities[j]
                
                # Check if both entities are mentioned in the description
                if entity1 in event.description and entity2 in event.description:
                    # Determine relationship type and strength
                    relationship_type, strength = self._determine_relationship(
                        entity1, entity2, event.description, event.event_type
                    )
                    
                    # Add the relationship
                    relationships.append({
                        "entity1": entity1,
                        "entity2": entity2,
                        "type": relationship_type,
                        "strength": strength,
                        "source_event": event.id
                    })
        
        return relationships
    
    def _determine_relationship(self, entity1: str, entity2: str, 
                               description: str, event_type: str) -> Tuple[str, str]:
        """
        Determine the relationship type and strength between two entities.
        
        Args:
            entity1: First entity
            entity2: Second entity
            description: Event description
            event_type: Type of event
            
        Returns:
            Tuple of (relationship_type, strength)
        """
        # This is a simplified implementation
        # In a full implementation, we would use NLP to analyze the description
        # and determine the relationship type and strength
        
        # For now, we'll use some heuristics based on the event type and keywords
        
        # Default relationship
        relationship_type = "neutral"
        strength = "weak"
        
        # Check for keywords indicating relationships
        if "ally" in description or "alliance" in description or "support" in description:
            relationship_type = "ally"
            strength = "moderate"
        elif "rival" in description or "rivalry" in description or "oppose" in description:
            relationship_type = "rival"
            strength = "moderate"
        elif "friend" in description or "friendship" in description:
            relationship_type = "friend"
            strength = "moderate"
        elif "enemy" in description or "enmity" in description or "hatred" in description:
            relationship_type = "enemy"
            strength = "strong"
        elif "patron" in description or "patronage" in description:
            relationship_type = "patron"
            strength = "strong"
        elif "client" in description or "clientage" in description:
            relationship_type = "client"
            strength = "strong"
        elif "family" in description or "relative" in description or "kin" in description:
            relationship_type = "family"
            strength = "strong"
        elif "colleague" in description or "collaboration" in description:
            relationship_type = "colleague"
            strength = "moderate"
        elif "compete" in description or "competition" in description:
            relationship_type = "competitor"
            strength = "moderate"
        
        # Adjust based on event type
        if event_type == "rumor":
            # Rumors might exaggerate relationships
            if random.random() < 0.3:  # 30% chance to strengthen
                strength_levels = list(self.relationship_strengths.keys())
                current_index = strength_levels.index(strength)
                if current_index < len(strength_levels) - 1:
                    strength = strength_levels[current_index + 1]
        
        return relationship_type, strength
    
    def _update_event_with_relationships(self, event: NarrativeEvent, 
                                        relationships: List[Dict[str, Any]]) -> NarrativeEvent:
        """
        Update the event with relationship information.
        
        Args:
            event: The event to update
            relationships: List of relationship dictionaries
            
        Returns:
            The updated event
        """
        if not event.metadata:
            event.metadata = {}
        
        # Add relationships to metadata
        event.metadata["relationships"] = relationships
        
        # Add relationship tags
        for relationship in relationships:
            relationship_tag = f"relationship:{relationship['type']}"
            if relationship_tag not in event.tags:
                event.tags.append(relationship_tag)
        
        return event
    
    def _connect_to_senate_topics(self, event: NarrativeEvent, 
                                 game_state: GameState) -> NarrativeEvent:
        """
        Connect the event to Senate topics when appropriate.
        
        Args:
            event: The event to connect
            game_state: The current game state
            
        Returns:
            The updated event
        """
        # This is a simplified implementation
        # In a full implementation, we would analyze the event and determine
        # if it's related to any current Senate topics
        
        # For now, we'll just check if the event mentions any current topic
        current_topic = game_state.current_topic
        if current_topic and isinstance(current_topic, dict) and "title" in current_topic:
            topic_title = current_topic["title"]
            
            # Check if the topic is mentioned in the event description
            if topic_title.lower() in event.description.lower():
                if not event.metadata:
                    event.metadata = {}
                
                # Add connection to Senate topic
                event.metadata["senate_topic"] = topic_title
                
                # Add tag
                if "senate_topic" not in event.tags:
                    event.tags.append("senate_topic")
        
        return event