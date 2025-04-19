"""
Roman Senate AI Game - Relationship Manager

This module provides a relationship manager for tracking and managing relationships
between senators in the Roman Senate simulation.

Part of the Migration Plan: Phase 3 - Relationship System.
"""

import json
import os
import logging
import uuid
from typing import Dict, List, Optional, Set, Tuple, Type, Any, Union

from ..core.events import EventBus, BaseEvent, RomanEvent
from ..utils.persistence import ensure_directory_exists

logger = logging.getLogger(__name__)


class SenatorRelationship:
    """
    Represents a relationship between two senators.
    
    This class tracks the strength, history, and attributes of a relationship
    between two senators, with methods to update the relationship based on events.
    """
    
    def __init__(
        self,
        senator_a_id: str,
        senator_b_id: str,
        relationship_type: str = "political",
        strength: float = 0.0,
        attributes: Optional[Dict[str, Any]] = None,
        relationship_id: Optional[str] = None
    ):
        """
        Initialize a new senator relationship.
        
        Args:
            senator_a_id: ID of the first senator
            senator_b_id: ID of the second senator
            relationship_type: Type of relationship (political, family, etc.)
            strength: Initial strength (-1.0 to 1.0)
            attributes: Additional relationship attributes
            relationship_id: Unique identifier (generated if not provided)
        """
        # Ensure consistent ordering of senator IDs
        if senator_a_id > senator_b_id:
            senator_a_id, senator_b_id = senator_b_id, senator_a_id
            
        self.senator_a_id = senator_a_id
        self.senator_b_id = senator_b_id
        self.relationship_type = relationship_type
        self.strength = max(-1.0, min(1.0, strength))  # Clamp to [-1.0, 1.0]
        self.attributes = attributes or {}
        self.id = relationship_id or str(uuid.uuid4())
        self._history: List[Dict[str, Any]] = []
        
    def update(self, event: BaseEvent) -> bool:
        """
        Update the relationship based on an event.
        
        Args:
            event: The event that might affect the relationship
            
        Returns:
            bool: True if the relationship was updated, False otherwise
        """
        # Check if event involves both senators
        if not self._event_involves_both_senators(event):
            return False
            
        # Check if event has a relationship_impact field
        impact = event.data.get("relationship_impact", 0.0)
        if impact != 0.0:
            reason = event.data.get("relationship_reason", f"Event: {event.event_type}")
            self.update_strength(impact, reason)
            return True
            
        return False
        
    def update_strength(self, delta: float, reason: Optional[str] = None) -> None:
        """
        Update the relationship strength.
        
        Args:
            delta: Change in strength
            reason: Optional reason for the change
        """
        old_strength = self.strength
        self.strength = max(-1.0, min(1.0, self.strength + delta))
        
        # Record in history
        self._history.append({
            "timestamp": str(uuid.uuid1().time),
            "old_strength": old_strength,
            "new_strength": self.strength,
            "delta": delta,
            "reason": reason
        })
        
        logger.debug(
            f"Relationship {self.id} updated: {old_strength:.2f} -> {self.strength:.2f} "
            f"({delta:+.2f}) because '{reason}'"
        )
        
    def get_sentiment(self) -> float:
        """
        Get the sentiment between the senators.
        
        Returns:
            float: Sentiment score (-1.0 to 1.0)
        """
        return self.strength
        
    def get_attribute(self, key: str, default: Any = None) -> Any:
        """
        Get a relationship attribute.
        
        Args:
            key: The attribute key
            default: Default value if attribute doesn't exist
            
        Returns:
            Any: The attribute value or default
        """
        return self.attributes.get(key, default)
        
    def set_attribute(self, key: str, value: Any) -> None:
        """
        Set a relationship attribute.
        
        Args:
            key: The attribute key
            value: The attribute value
        """
        self.attributes[key] = value
        
    def get_history(self) -> List[Dict[str, Any]]:
        """
        Get the relationship update history.
        
        Returns:
            List[Dict[str, Any]]: List of history entries
        """
        return self._history.copy()
        
    def involves_senator(self, senator_id: str) -> bool:
        """
        Check if this relationship involves a specific senator.
        
        Args:
            senator_id: The senator ID to check
            
        Returns:
            bool: True if the senator is part of this relationship
        """
        return senator_id == self.senator_a_id or senator_id == self.senator_b_id
        
    def get_other_senator_id(self, senator_id: str) -> Optional[str]:
        """
        Get the ID of the other senator in the relationship.
        
        Args:
            senator_id: ID of one senator in the relationship
            
        Returns:
            Optional[str]: ID of the other senator, or None if the given senator is not in the relationship
        """
        if senator_id == self.senator_a_id:
            return self.senator_b_id
        elif senator_id == self.senator_b_id:
            return self.senator_a_id
        else:
            return None
            
    def _event_involves_both_senators(self, event: BaseEvent) -> bool:
        """
        Check if an event involves both senators in the relationship.
        
        Args:
            event: The event to check
            
        Returns:
            bool: True if both senators are involved
        """
        involved_senators = set()
        
        # Check source
        if event.source and (event.source == self.senator_a_id or event.source == self.senator_b_id):
            involved_senators.add(event.source)
            
        # Check target
        if event.target and (event.target == self.senator_a_id or event.target == self.senator_b_id):
            involved_senators.add(event.target)
            
        # Check participants in data
        participants = event.data.get("participants", [])
        if isinstance(participants, list):
            for participant in participants:
                if participant == self.senator_a_id or participant == self.senator_b_id:
                    involved_senators.add(participant)
                    
        return len(involved_senators) == 2
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the relationship to a dictionary representation.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the relationship
        """
        return {
            "id": self.id,
            "senator_a_id": self.senator_a_id,
            "senator_b_id": self.senator_b_id,
            "relationship_type": self.relationship_type,
            "strength": self.strength,
            "attributes": self.attributes,
            "history": self._history
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SenatorRelationship':
        """
        Create a relationship from a dictionary representation.
        
        Args:
            data: Dictionary containing relationship data
            
        Returns:
            SenatorRelationship: A new relationship instance
            
        Raises:
            ValueError: If the dictionary is missing required fields
        """
        required_fields = ["senator_a_id", "senator_b_id", "relationship_type"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Relationship dictionary must contain '{field}'")
                
        relationship = cls(
            senator_a_id=data["senator_a_id"],
            senator_b_id=data["senator_b_id"],
            relationship_type=data["relationship_type"],
            strength=data.get("strength", 0.0),
            attributes=data.get("attributes", {}),
            relationship_id=data.get("id")
        )
        
        # Restore history
        relationship._history = data.get("history", [])
        
        return relationship
        
    def __str__(self) -> str:
        """
        Get a string representation of the relationship.
        
        Returns:
            str: String representation
        """
        return (f"{self.relationship_type} between {self.senator_a_id} and "
                f"{self.senator_b_id} (strength: {self.strength:.2f})")


class RelationshipManager:
    """
    Manager for collections of senator relationships.
    
    The RelationshipManager maintains a registry of senator relationship instances
    and provides methods for adding, removing, retrieving, and updating relationships.
    It also handles:
    1. Connecting relationships to the event bus
    2. Distributing events to the appropriate relationships
    3. Persisting relationships to storage
    
    This centralizes relationship management and simplifies relationship-event interactions.
    """
    
    def __init__(
        self,
        event_bus: Optional[EventBus] = None,
        storage_dir: Optional[str] = None
    ):
        """
        Initialize a new relationship manager.
        
        Args:
            event_bus: Optional event bus to connect relationships to
            storage_dir: Optional directory for relationship persistence
        """
        # Map of relationship_id -> relationship instance
        self._relationships: Dict[str, SenatorRelationship] = {}
        
        # Map of senator_id -> set of relationship_ids
        self._senator_relationships: Dict[str, Set[str]] = {}
        
        # Map of (senator_a_id, senator_b_id) -> relationship_id
        self._senator_pair_index: Dict[Tuple[str, str], str] = {}
        
        # Map of relationship_type -> set of relationship_ids
        self._type_index: Dict[str, Set[str]] = {}
        
        # Event bus for relationship-event interactions
        self._event_bus = event_bus
        
        # Storage directory for persistence
        self._storage_dir = storage_dir
        
        # Create storage directory if specified and doesn't exist
        if storage_dir:
            ensure_directory_exists(storage_dir)
            
        # Register with event bus if provided
        if event_bus:
            self._register_with_event_bus()
            
        logger.info(f"Relationship manager initialized with storage at {storage_dir}")
        
    def add_relationship(self, relationship: SenatorRelationship) -> None:
        """
        Add a relationship to the manager.
        
        Args:
            relationship: The relationship to add
            
        Raises:
            ValueError: If a relationship between these senators already exists
        """
        # Check if relationship between these senators already exists
        senator_pair = self._get_senator_pair_key(
            relationship.senator_a_id, 
            relationship.senator_b_id
        )
        
        if senator_pair in self._senator_pair_index:
            existing_id = self._senator_pair_index[senator_pair]
            raise ValueError(
                f"Relationship already exists between {relationship.senator_a_id} and "
                f"{relationship.senator_b_id} (ID: {existing_id})"
            )
            
        # Add to primary storage
        self._relationships[relationship.id] = relationship
        
        # Update senator index
        for senator_id in [relationship.senator_a_id, relationship.senator_b_id]:
            if senator_id not in self._senator_relationships:
                self._senator_relationships[senator_id] = set()
            self._senator_relationships[senator_id].add(relationship.id)
            
        # Update senator pair index
        self._senator_pair_index[senator_pair] = relationship.id
        
        # Update type index
        rel_type = relationship.relationship_type
        if rel_type not in self._type_index:
            self._type_index[rel_type] = set()
        self._type_index[rel_type].add(relationship.id)
        
        logger.debug(
            f"Added relationship {relationship.id} between "
            f"{relationship.senator_a_id} and {relationship.senator_b_id}"
        )
        
    def remove_relationship(self, relationship_id: str) -> Optional[SenatorRelationship]:
        """
        Remove a relationship from the manager.
        
        Args:
            relationship_id: ID of the relationship to remove
            
        Returns:
            Optional[SenatorRelationship]: The removed relationship, or None if not found
        """
        if relationship_id not in self._relationships:
            return None
            
        relationship = self._relationships.pop(relationship_id)
        
        # Update senator index
        for senator_id in [relationship.senator_a_id, relationship.senator_b_id]:
            if senator_id in self._senator_relationships and relationship_id in self._senator_relationships[senator_id]:
                self._senator_relationships[senator_id].remove(relationship_id)
                if not self._senator_relationships[senator_id]:
                    del self._senator_relationships[senator_id]
                    
        # Update senator pair index
        senator_pair = self._get_senator_pair_key(
            relationship.senator_a_id, 
            relationship.senator_b_id
        )
        if senator_pair in self._senator_pair_index:
            del self._senator_pair_index[senator_pair]
            
        # Update type index
        rel_type = relationship.relationship_type
        if rel_type in self._type_index and relationship_id in self._type_index[rel_type]:
            self._type_index[rel_type].remove(relationship_id)
            if not self._type_index[rel_type]:
                del self._type_index[rel_type]
                
        logger.debug(f"Removed relationship {relationship_id}")
        
        return relationship
        
    def get_relationship(self, relationship_id: str) -> Optional[SenatorRelationship]:
        """
        Get a relationship by ID.
        
        Args:
            relationship_id: ID of the relationship to retrieve
            
        Returns:
            Optional[SenatorRelationship]: The relationship, or None if not found
        """
        return self._relationships.get(relationship_id)
        
    def get_relationship_between(
        self, 
        senator_a_id: str, 
        senator_b_id: str
    ) -> Optional[SenatorRelationship]:
        """
        Get the relationship between two senators.
        
        Args:
            senator_a_id: ID of the first senator
            senator_b_id: ID of the second senator
            
        Returns:
            Optional[SenatorRelationship]: The relationship, or None if not found
        """
        senator_pair = self._get_senator_pair_key(senator_a_id, senator_b_id)
        relationship_id = self._senator_pair_index.get(senator_pair)
        
        if relationship_id:
            return self._relationships.get(relationship_id)
            
        return None
        
    def get_senator_relationships(self, senator_id: str) -> List[SenatorRelationship]:
        """
        Get all relationships involving a senator.
        
        Args:
            senator_id: ID of the senator
            
        Returns:
            List[SenatorRelationship]: List of relationships
        """
        if senator_id not in self._senator_relationships:
            return []
            
        return [
            self._relationships[rel_id]
            for rel_id in self._senator_relationships[senator_id]
            if rel_id in self._relationships
        ]
        
    def get_relationships_by_type(self, relationship_type: str) -> List[SenatorRelationship]:
        """
        Get all relationships of a specific type.
        
        Args:
            relationship_type: Type of relationships to retrieve
            
        Returns:
            List[SenatorRelationship]: List of relationships
        """
        if relationship_type not in self._type_index:
            return []
            
        return [
            self._relationships[rel_id]
            for rel_id in self._type_index[relationship_type]
            if rel_id in self._relationships
        ]
        
    def get_all_relationships(self) -> List[SenatorRelationship]:
        """
        Get all relationships managed by this manager.
        
        Returns:
            List[SenatorRelationship]: List of all relationships
        """
        return list(self._relationships.values())
        
    def create_relationship(
        self,
        senator_a_id: str,
        senator_b_id: str,
        relationship_type: str = "political",
        strength: float = 0.0,
        attributes: Optional[Dict[str, any]] = None
    ) -> SenatorRelationship:
        """
        Create and add a new relationship.
        
        Args:
            senator_a_id: ID of the first senator
            senator_b_id: ID of the second senator
            relationship_type: Type of relationship
            strength: Initial strength (-1.0 to 1.0)
            attributes: Additional relationship attributes
            
        Returns:
            SenatorRelationship: The created relationship
            
        Raises:
            ValueError: If a relationship between these senators already exists
        """
        # Check if relationship already exists
        if self.get_relationship_between(senator_a_id, senator_b_id):
            raise ValueError(f"Relationship already exists between {senator_a_id} and {senator_b_id}")
            
        # Create the relationship
        relationship = SenatorRelationship(
            senator_a_id=senator_a_id,
            senator_b_id=senator_b_id,
            relationship_type=relationship_type,
            strength=strength,
            attributes=attributes
        )
        
        # Add to manager
        self.add_relationship(relationship)
        
        return relationship
        
    def update_relationships(self, event: BaseEvent) -> int:
        """
        Update all relevant relationships based on an event.
        
        Args:
            event: The event to process
            
        Returns:
            int: Number of relationships updated
        """
        updated_count = 0
        
        # Determine which senators are involved in the event
        involved_senators = self._get_involved_senators(event)
        
        # Update relationships between involved senators
        for i, senator_a_id in enumerate(involved_senators):
            for senator_b_id in involved_senators[i+1:]:
                relationship = self.get_relationship_between(senator_a_id, senator_b_id)
                
                if relationship and relationship.update(event):
                    updated_count += 1
                    
        return updated_count
        
    def get_relationship_sentiment(
        self, 
        senator_a_id: str, 
        senator_b_id: str
    ) -> float:
        """
        Get the sentiment between two senators.
        
        Args:
            senator_a_id: ID of the first senator
            senator_b_id: ID of the second senator
            
        Returns:
            float: Sentiment score (-1.0 to 1.0), 0.0 if no relationship exists
        """
        relationship = self.get_relationship_between(senator_a_id, senator_b_id)
        if relationship:
            return relationship.get_sentiment()
        return 0.0
        
    def get_strongest_allies(
        self, 
        senator_id: str, 
        limit: int = 5
    ) -> List[Tuple[str, float]]:
        """
        Get a senator's strongest allies.
        
        Args:
            senator_id: ID of the senator
            limit: Maximum number of allies to return
            
        Returns:
            List[Tuple[str, float]]: List of (ally_id, sentiment) pairs, sorted by sentiment
        """
        relationships = self.get_senator_relationships(senator_id)
        
        # Filter for positive relationships and sort by strength
        allies = [
            (rel.get_other_senator_id(senator_id), rel.get_sentiment())
            for rel in relationships
            if rel.get_sentiment() > 0
        ]
        
        allies.sort(key=lambda x: x[1], reverse=True)
        return allies[:limit]
        
    def get_strongest_rivals(
        self, 
        senator_id: str, 
        limit: int = 5
    ) -> List[Tuple[str, float]]:
        """
        Get a senator's strongest rivals.
        
        Args:
            senator_id: ID of the senator
            limit: Maximum number of rivals to return
            
        Returns:
            List[Tuple[str, float]]: List of (rival_id, sentiment) pairs, sorted by sentiment
        """
        relationships = self.get_senator_relationships(senator_id)
        
        # Filter for negative relationships and sort by strength (most negative first)
        rivals = [
            (rel.get_other_senator_id(senator_id), rel.get_sentiment())
            for rel in relationships
            if rel.get_sentiment() < 0
        ]
        
        rivals.sort(key=lambda x: x[1])
        return rivals[:limit]
        
    def _get_involved_senators(self, event: BaseEvent) -> List[str]:
        """
        Get all senators involved in an event.
        
        Args:
            event: The event to analyze
            
        Returns:
            List[str]: List of involved senator IDs
        """
        involved_senators = set()
        
        # Check source
        if event.source:
            involved_senators.add(event.source)
            
        # Check target
        if event.target:
            involved_senators.add(event.target)
            
        # Check participants in data
        participants = event.data.get("participants", [])
        if isinstance(participants, list):
            for participant in participants:
                involved_senators.add(participant)
                
        return list(involved_senators)
        
    def _get_senator_pair_key(self, senator_a_id: str, senator_b_id: str) -> Tuple[str, str]:
        """
        Get a consistent key for a senator pair.
        
        This ensures that (A,B) and (B,A) map to the same key.
        
        Args:
            senator_a_id: ID of the first senator
            senator_b_id: ID of the second senator
            
        Returns:
            Tuple[str, str]: Sorted tuple of senator IDs
        """
        return tuple(sorted([senator_a_id, senator_b_id]))
        
    def _register_with_event_bus(self) -> None:
        """
        Register with the event bus to receive events.
        """
        if not self._event_bus:
            return
            
        # Create a handler that will update relationships
        class RelationshipEventHandler:
            def __init__(self, relationship_manager: RelationshipManager):
                self.relationship_manager = relationship_manager
                
            def handle_event(self, event: BaseEvent) -> None:
                self.relationship_manager.update_relationships(event)
                
        # Subscribe to all events
        handler = RelationshipEventHandler(self)
        self._event_bus.subscribe("*", handler.handle_event)
        logger.info("Relationship manager registered with event bus")
        
    def save_relationships(self, file_path: Optional[str] = None) -> bool:
        """
        Save all relationships to a file.
        
        Args:
            file_path: Path to save to (defaults to storage_dir/relationships.json)
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not file_path and not self._storage_dir:
            return False
            
        try:
            # Convert relationships to dictionaries
            relationship_dicts = [rel.to_dict() for rel in self._relationships.values()]
            
            # Create the file path
            if not file_path:
                file_path = os.path.join(self._storage_dir, "relationships.json")
                ensure_directory_exists(os.path.dirname(file_path))
                
            # Save to file
            with open(file_path, 'w') as f:
                json.dump(relationship_dicts, f, indent=2)
                
            logger.info(f"Saved {len(relationship_dicts)} relationships to {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving relationships: {e}")
            return False
            
    def load_relationships(self, file_path: Optional[str] = None) -> bool:
        """
        Load relationships from a file.
        
        Args:
            file_path: Path to load from (defaults to storage_dir/relationships.json)
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not file_path and not self._storage_dir:
            return False
            
        if not file_path:
            file_path = os.path.join(self._storage_dir, "relationships.json")
            
        if not os.path.exists(file_path):
            logger.warning(f"Relationship file not found: {file_path}")
            return False
            
        try:
            # Load from file
            with open(file_path, 'r') as f:
                relationship_dicts = json.load(f)
                
            # Clear existing relationships
            self._relationships.clear()
            self._senator_relationships.clear()
            self._senator_pair_index.clear()
            self._type_index.clear()
            
            # Convert dictionaries to relationships and add them
            for rel_dict in relationship_dicts:
                relationship = SenatorRelationship.from_dict(rel_dict)
                self.add_relationship(relationship)
                
            logger.info(f"Loaded {len(relationship_dicts)} relationships from {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error loading relationships: {e}")
            return False
            
    def clear(self) -> None:
        """
        Clear all relationships from the manager.
        """
        self._relationships.clear()
        self._senator_relationships.clear()
        self._senator_pair_index.clear()
        self._type_index.clear()
        logger.info("All relationships cleared from manager")