"""
Relationship Manager for Agentic Game Framework.

This module provides the manager class for handling collections of relationships,
including adding, removing, retrieving, and updating relationships.
"""

import json
import os
from typing import Dict, List, Optional, Set, Tuple, Type

from ..events.base import BaseEvent
from ..events.event_bus import EventBus
from .base_relationship import BaseRelationship, SimpleRelationship


class RelationshipManager:
    """
    Manager for collections of relationships.
    
    The RelationshipManager maintains a registry of relationship instances and provides
    methods for adding, removing, retrieving, and updating relationships. It also handles:
    1. Connecting relationships to the event bus
    2. Distributing events to the appropriate relationships
    3. Persisting relationships to storage
    
    This centralizes relationship management and simplifies relationship-event interactions.
    """
    
    def __init__(
        self,
        event_bus: Optional[EventBus] = None,
        default_relationship_class: Type[BaseRelationship] = SimpleRelationship,
        storage_dir: Optional[str] = None
    ):
        """
        Initialize a new relationship manager.
        
        Args:
            event_bus: Optional event bus to connect relationships to
            default_relationship_class: Default class to use for new relationships
            storage_dir: Optional directory for relationship persistence
        """
        # Map of relationship_id -> relationship instance
        self._relationships: Dict[str, BaseRelationship] = {}
        
        # Map of agent_id -> set of relationship_ids
        self._agent_relationships: Dict[str, Set[str]] = {}
        
        # Map of (agent_a_id, agent_b_id) -> relationship_id
        self._agent_pair_index: Dict[Tuple[str, str], str] = {}
        
        # Map of relationship_type -> set of relationship_ids
        self._type_index: Dict[str, Set[str]] = {}
        
        # Event bus for relationship-event interactions
        self._event_bus = event_bus
        
        # Default class for new relationships
        self._default_relationship_class = default_relationship_class
        
        # Storage directory for persistence
        self._storage_dir = storage_dir
        
        # Create storage directory if specified and doesn't exist
        if storage_dir and not os.path.exists(storage_dir):
            os.makedirs(storage_dir)
            
        # Register with event bus if provided
        if event_bus:
            self._register_with_event_bus()
    
    def add_relationship(self, relationship: BaseRelationship) -> None:
        """
        Add a relationship to the manager.
        
        Args:
            relationship: The relationship to add
            
        Raises:
            ValueError: If a relationship between these agents already exists
        """
        # Check if relationship between these agents already exists
        agent_pair = self._get_agent_pair_key(relationship.agent_a_id, relationship.agent_b_id)
        if agent_pair in self._agent_pair_index:
            existing_id = self._agent_pair_index[agent_pair]
            raise ValueError(
                f"Relationship already exists between {relationship.agent_a_id} and "
                f"{relationship.agent_b_id} (ID: {existing_id})"
            )
            
        # Add to primary storage
        self._relationships[relationship.id] = relationship
        
        # Update agent index
        for agent_id in [relationship.agent_a_id, relationship.agent_b_id]:
            if agent_id not in self._agent_relationships:
                self._agent_relationships[agent_id] = set()
            self._agent_relationships[agent_id].add(relationship.id)
            
        # Update agent pair index
        self._agent_pair_index[agent_pair] = relationship.id
        
        # Update type index
        rel_type = relationship.relationship_type
        if rel_type not in self._type_index:
            self._type_index[rel_type] = set()
        self._type_index[rel_type].add(relationship.id)
    
    def remove_relationship(self, relationship_id: str) -> Optional[BaseRelationship]:
        """
        Remove a relationship from the manager.
        
        Args:
            relationship_id: ID of the relationship to remove
            
        Returns:
            Optional[BaseRelationship]: The removed relationship, or None if not found
        """
        if relationship_id not in self._relationships:
            return None
            
        relationship = self._relationships.pop(relationship_id)
        
        # Update agent index
        for agent_id in [relationship.agent_a_id, relationship.agent_b_id]:
            if agent_id in self._agent_relationships and relationship_id in self._agent_relationships[agent_id]:
                self._agent_relationships[agent_id].remove(relationship_id)
                if not self._agent_relationships[agent_id]:
                    del self._agent_relationships[agent_id]
                    
        # Update agent pair index
        agent_pair = self._get_agent_pair_key(relationship.agent_a_id, relationship.agent_b_id)
        if agent_pair in self._agent_pair_index:
            del self._agent_pair_index[agent_pair]
            
        # Update type index
        rel_type = relationship.relationship_type
        if rel_type in self._type_index and relationship_id in self._type_index[rel_type]:
            self._type_index[rel_type].remove(relationship_id)
            if not self._type_index[rel_type]:
                del self._type_index[rel_type]
                
        return relationship
    
    def get_relationship(self, relationship_id: str) -> Optional[BaseRelationship]:
        """
        Get a relationship by ID.
        
        Args:
            relationship_id: ID of the relationship to retrieve
            
        Returns:
            Optional[BaseRelationship]: The relationship, or None if not found
        """
        return self._relationships.get(relationship_id)
    
    def get_relationship_between(self, agent_a_id: str, agent_b_id: str) -> Optional[BaseRelationship]:
        """
        Get the relationship between two agents.
        
        Args:
            agent_a_id: ID of the first agent
            agent_b_id: ID of the second agent
            
        Returns:
            Optional[BaseRelationship]: The relationship, or None if not found
        """
        agent_pair = self._get_agent_pair_key(agent_a_id, agent_b_id)
        relationship_id = self._agent_pair_index.get(agent_pair)
        
        if relationship_id:
            return self._relationships.get(relationship_id)
            
        return None
    
    def get_agent_relationships(self, agent_id: str) -> List[BaseRelationship]:
        """
        Get all relationships involving an agent.
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            List[BaseRelationship]: List of relationships
        """
        if agent_id not in self._agent_relationships:
            return []
            
        return [
            self._relationships[rel_id]
            for rel_id in self._agent_relationships[agent_id]
            if rel_id in self._relationships
        ]
    
    def get_relationships_by_type(self, relationship_type: str) -> List[BaseRelationship]:
        """
        Get all relationships of a specific type.
        
        Args:
            relationship_type: Type of relationships to retrieve
            
        Returns:
            List[BaseRelationship]: List of relationships
        """
        if relationship_type not in self._type_index:
            return []
            
        return [
            self._relationships[rel_id]
            for rel_id in self._type_index[relationship_type]
            if rel_id in self._relationships
        ]
    
    def get_all_relationships(self) -> List[BaseRelationship]:
        """
        Get all relationships managed by this manager.
        
        Returns:
            List[BaseRelationship]: List of all relationships
        """
        return list(self._relationships.values())
    
    def create_relationship(
        self,
        agent_a_id: str,
        agent_b_id: str,
        relationship_type: str,
        strength: float = 0.0,
        attributes: Optional[Dict[str, any]] = None,
        relationship_class: Optional[Type[BaseRelationship]] = None
    ) -> BaseRelationship:
        """
        Create and add a new relationship.
        
        Args:
            agent_a_id: ID of the first agent
            agent_b_id: ID of the second agent
            relationship_type: Type of relationship
            strength: Initial strength (-1.0 to 1.0)
            attributes: Additional relationship attributes
            relationship_class: Class to use (defaults to manager's default)
            
        Returns:
            BaseRelationship: The created relationship
            
        Raises:
            ValueError: If a relationship between these agents already exists
        """
        # Check if relationship already exists
        if self.get_relationship_between(agent_a_id, agent_b_id):
            raise ValueError(f"Relationship already exists between {agent_a_id} and {agent_b_id}")
            
        # Create the relationship
        rel_class = relationship_class or self._default_relationship_class
        relationship = rel_class(
            agent_a_id=agent_a_id,
            agent_b_id=agent_b_id,
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
        
        # Determine which agents are involved in the event
        involved_agents = self._get_involved_agents(event)
        
        # Update relationships between involved agents
        for i, agent_a_id in enumerate(involved_agents):
            for agent_b_id in involved_agents[i+1:]:
                relationship = self.get_relationship_between(agent_a_id, agent_b_id)
                
                if relationship and relationship.update(event):
                    updated_count += 1
                    
        return updated_count
    
    def _get_involved_agents(self, event: BaseEvent) -> List[str]:
        """
        Get all agents involved in an event.
        
        Args:
            event: The event to analyze
            
        Returns:
            List[str]: List of involved agent IDs
        """
        involved_agents = set()
        
        # Check source
        if event.source:
            involved_agents.add(event.source)
            
        # Check target
        if event.target:
            involved_agents.add(event.target)
            
        # Check participants in data
        participants = event.data.get("participants", [])
        if isinstance(participants, list):
            for participant in participants:
                involved_agents.add(participant)
                
        return list(involved_agents)
    
    def _get_agent_pair_key(self, agent_a_id: str, agent_b_id: str) -> Tuple[str, str]:
        """
        Get a consistent key for an agent pair.
        
        This ensures that (A,B) and (B,A) map to the same key.
        
        Args:
            agent_a_id: ID of the first agent
            agent_b_id: ID of the second agent
            
        Returns:
            Tuple[str, str]: Sorted tuple of agent IDs
        """
        return tuple(sorted([agent_a_id, agent_b_id]))
    
    def _register_with_event_bus(self) -> None:
        """
        Register with the event bus to receive events.
        """
        if not self._event_bus:
            return
            
        # Create a handler that will update relationships
        class RelationshipEventHandler:
            def __init__(self, relationship_manager):
                self.relationship_manager = relationship_manager
            
            def handle_event(self, event):
                self.relationship_manager.update_relationships(event)
        
        # Subscribe to all events
        handler = RelationshipEventHandler(self)
        self._event_bus.subscribe_to_all(handler)
    
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
                
            # Save to file
            with open(file_path, 'w') as f:
                json.dump(relationship_dicts, f, indent=2)
                
            return True
        except Exception as e:
            # In a real system, we would log this error
            print(f"Error saving relationships: {e}")
            return False
    
    def load_relationships(
        self,
        file_path: Optional[str] = None,
        relationship_class: Optional[Type[BaseRelationship]] = None
    ) -> bool:
        """
        Load relationships from a file.
        
        Args:
            file_path: Path to load from (defaults to storage_dir/relationships.json)
            relationship_class: Class to use for instantiation
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not file_path and not self._storage_dir:
            return False
            
        if not file_path:
            file_path = os.path.join(self._storage_dir, "relationships.json")
            
        if not os.path.exists(file_path):
            return False
            
        try:
            # Load from file
            with open(file_path, 'r') as f:
                relationship_dicts = json.load(f)
                
            # Clear existing relationships
            self._relationships.clear()
            self._agent_relationships.clear()
            self._agent_pair_index.clear()
            self._type_index.clear()
            
            # Convert dictionaries to relationships and add them
            rel_class = relationship_class or self._default_relationship_class
            for rel_dict in relationship_dicts:
                relationship = rel_class.from_dict(rel_dict)
                self.add_relationship(relationship)
                
            return True
        except Exception as e:
            # In a real system, we would log this error
            print(f"Error loading relationships: {e}")
            return False
    
    def clear(self) -> None:
        """
        Clear all relationships from the manager.
        """
        self._relationships.clear()
        self._agent_relationships.clear()
        self._agent_pair_index.clear()
        self._type_index.clear()