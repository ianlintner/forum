"""
Roman Senate Simulation
Consistency Processor Module

This module provides the ConsistencyProcessor class, which ensures narrative consistency
across generated events.
"""

import logging
from typing import Dict, List, Any, Set

from roman_senate.core.game_state import GameState
from roman_senate.core.narrative_context import NarrativeContext, NarrativeEvent
from roman_senate.core.event_manager import EventProcessor

logger = logging.getLogger(__name__)

class ConsistencyProcessor(EventProcessor):
    """
    Ensures narrative consistency across generated events.
    
    This processor:
    1. Checks for contradictions with existing events
    2. Ensures historical accuracy based on the game state
    3. Maintains consistent entity references
    4. Adjusts event details to fit the narrative context
    """
    
    def __init__(self):
        """Initialize the consistency processor."""
        self.contradiction_types = {
            "location": self._check_location_contradiction,
            "time": self._check_time_contradiction,
            "action": self._check_action_contradiction,
            "status": self._check_status_contradiction
        }
        logger.info("ConsistencyProcessor initialized")
    
    def process_event(self, event: NarrativeEvent, game_state: GameState, 
                     narrative_context: NarrativeContext) -> NarrativeEvent:
        """
        Process a narrative event to ensure consistency.
        
        Args:
            event: The narrative event to process
            game_state: The current game state
            narrative_context: The current narrative context
            
        Returns:
            The processed narrative event
        """
        # Check for contradictions with recent events
        contradictions = self._find_contradictions(event, narrative_context)
        
        # If contradictions found, adjust the event
        if contradictions:
            event = self._resolve_contradictions(event, contradictions, narrative_context)
        
        # Ensure historical accuracy
        event = self._ensure_historical_accuracy(event, game_state)
        
        # Maintain consistent entity references
        event = self._maintain_entity_consistency(event, narrative_context)
        
        logger.debug(f"Processed event for consistency: {event.id}")
        return event
    
    def _find_contradictions(self, event: NarrativeEvent, 
                            narrative_context: NarrativeContext) -> Dict[str, Any]:
        """
        Find contradictions between the event and existing narrative context.
        
        Args:
            event: The event to check
            narrative_context: The narrative context to check against
            
        Returns:
            Dictionary of contradiction types and details
        """
        contradictions = {}
        
        # Get recent events to check against
        recent_events = narrative_context.get_recent_events(10)
        
        # Check each type of contradiction
        for contradiction_type, check_function in self.contradiction_types.items():
            contradiction = check_function(event, recent_events)
            if contradiction:
                contradictions[contradiction_type] = contradiction
        
        return contradictions
    
    def _check_location_contradiction(self, event: NarrativeEvent, 
                                     recent_events: List[NarrativeEvent]) -> Dict[str, Any]:
        """
        Check for location contradictions.
        
        Args:
            event: The event to check
            recent_events: Recent events to check against
            
        Returns:
            Contradiction details or None
        """
        # This is a simplified implementation
        # In a full implementation, we would check if an entity is mentioned as being
        # in different locations at the same time
        
        # For now, we'll just return None (no contradictions)
        return None
    
    def _check_time_contradiction(self, event: NarrativeEvent, 
                                 recent_events: List[NarrativeEvent]) -> Dict[str, Any]:
        """
        Check for time contradictions.
        
        Args:
            event: The event to check
            recent_events: Recent events to check against
            
        Returns:
            Contradiction details or None
        """
        # This is a simplified implementation
        # In a full implementation, we would check for temporal inconsistencies
        
        # For now, we'll just return None (no contradictions)
        return None
    
    def _check_action_contradiction(self, event: NarrativeEvent, 
                                   recent_events: List[NarrativeEvent]) -> Dict[str, Any]:
        """
        Check for action contradictions.
        
        Args:
            event: The event to check
            recent_events: Recent events to check against
            
        Returns:
            Contradiction details or None
        """
        # This is a simplified implementation
        # In a full implementation, we would check if actions contradict each other
        
        # For now, we'll just return None (no contradictions)
        return None
    
    def _check_status_contradiction(self, event: NarrativeEvent, 
                                   recent_events: List[NarrativeEvent]) -> Dict[str, Any]:
        """
        Check for status contradictions.
        
        Args:
            event: The event to check
            recent_events: Recent events to check against
            
        Returns:
            Contradiction details or None
        """
        # This is a simplified implementation
        # In a full implementation, we would check if entity statuses contradict each other
        
        # For now, we'll just return None (no contradictions)
        return None
    
    def _resolve_contradictions(self, event: NarrativeEvent, 
                               contradictions: Dict[str, Any],
                               narrative_context: NarrativeContext) -> NarrativeEvent:
        """
        Resolve contradictions by adjusting the event.
        
        Args:
            event: The event to adjust
            contradictions: Dictionary of contradiction types and details
            narrative_context: The narrative context
            
        Returns:
            The adjusted event
        """
        # This is a simplified implementation
        # In a full implementation, we would make specific adjustments based on
        # the type of contradiction
        
        # For now, we'll just add a note to the metadata
        if not event.metadata:
            event.metadata = {}
        
        event.metadata["contradictions_resolved"] = list(contradictions.keys())
        
        return event
    
    def _ensure_historical_accuracy(self, event: NarrativeEvent, 
                                   game_state: GameState) -> NarrativeEvent:
        """
        Ensure the event is historically accurate based on the game state.
        
        Args:
            event: The event to check
            game_state: The current game state
            
        Returns:
            The adjusted event
        """
        # This is a simplified implementation
        # In a full implementation, we would check against historical facts
        
        # For now, we'll just return the event unchanged
        return event
    
    def _maintain_entity_consistency(self, event: NarrativeEvent,
                                    narrative_context: NarrativeContext) -> NarrativeEvent:
        """
        Maintain consistent entity references.
        
        Args:
            event: The event to adjust
            narrative_context: The narrative context
            
        Returns:
            The adjusted event
        """
        # Get all known entities
        known_entities: Set[str] = set(narrative_context.recurring_entities.keys())
        
        # Check if any entities in this event are similar to known entities
        # but not exactly the same (e.g., "Marcus Tullius" vs "Marcus Tullius Cicero")
        for entity in event.entities:
            if entity not in known_entities:
                # Check for partial matches
                for known_entity in known_entities:
                    if (entity in known_entity or known_entity in entity) and entity != known_entity:
                        # Replace with the known entity name
                        event.description = event.description.replace(entity, known_entity)
                        # Update the entity list
                        event.entities.remove(entity)
                        if known_entity not in event.entities:
                            event.entities.append(known_entity)
                        break
        
        return event