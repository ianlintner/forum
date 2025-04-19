"""
Roman Senate Simulation
Relationship Events Module

This module defines event types specific to senator relationships, including
relationship changes and relationship-based decisions.
"""

from typing import Any, Dict, Optional

from .base import Event


class RelationshipChangeEvent(Event):
    """
    Event representing a change in relationship between two senators.
    
    This event is triggered when a relationship value changes, either due to
    direct interaction, event reactions, or natural decay over time.
    """
    
    TYPE = "relationship_change"
    
    def __init__(
        self,
        senator_id: str,
        target_senator_id: str,
        relationship_type: str,
        old_value: float,
        new_value: float,
        change_value: float,
        reason: str,
        source_event_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a relationship change event.
        
        Args:
            senator_id: ID of the senator whose relationship is changing
            target_senator_id: ID of the target senator in the relationship
            relationship_type: Type of relationship (political, personal, etc.)
            old_value: Previous relationship value
            new_value: New relationship value
            change_value: The amount of change
            reason: Reason for the relationship change
            source_event_id: Optional ID of the event that caused this change
            metadata: Additional event-specific data
        """
        super().__init__(
            event_type=self.TYPE,
            source={"id": senator_id},
            metadata=metadata or {}
        )
        self.senator_id = senator_id
        self.target_senator_id = target_senator_id
        self.relationship_type = relationship_type
        self.old_value = old_value
        self.new_value = new_value
        self.change_value = change_value
        self.reason = reason
        self.source_event_id = source_event_id
        
        # Add relationship-specific metadata
        self.metadata.update({
            "senator_id": senator_id,
            "target_senator_id": target_senator_id,
            "relationship_type": relationship_type,
            "old_value": old_value,
            "new_value": new_value,
            "change_value": change_value,
            "reason": reason
        })
        
        if source_event_id:
            self.metadata["source_event_id"] = source_event_id
            
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, including relationship-specific fields."""
        data = super().to_dict()
        data.update({
            "senator_id": self.senator_id,
            "target_senator_id": self.target_senator_id,
            "relationship_type": self.relationship_type,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "change_value": self.change_value,
            "reason": self.reason
        })
        
        if self.source_event_id:
            data["source_event_id"] = self.source_event_id
            
        return data