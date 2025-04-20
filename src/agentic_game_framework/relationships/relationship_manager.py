"""
Relationship Manager for Agentic Game Framework.

This module provides the manager class for handling collections of relationships,
including adding, removing, retrieving, and updating relationships.
"""
import json
import logging
import os
import time
from typing import Dict, List, Optional, Set, Tuple, Type, Any, Callable

from ..events.base import BaseEvent
from ..events.event_bus import EventBus
from .base_relationship import BaseRelationship, SimpleRelationship

# Set up module logger
logger = logging.getLogger(__name__)


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
        storage_dir: Optional[str] = None,
        enable_caching: bool = True,
        event_filtering: bool = True
    ):
        """
        Initialize a new relationship manager.
        
        Args:
            event_bus: Optional event bus to connect relationships to
            default_relationship_class: Default class to use for new relationships
            storage_dir: Optional directory for relationship persistence
            enable_caching: Whether to enable results caching for lookups
            event_filtering: Whether to filter events by relevance
        """
        # Map of relationship_id -> relationship instance
        self._relationships: Dict[str, BaseRelationship] = {}
        
        # Map of agent_id -> set of relationship_ids
        self._agent_relationships: Dict[str, Set[str]] = {}
        
        # Map of (agent_a_id, agent_b_id) -> relationship_id
        self._agent_pair_index: Dict[Tuple[str, str], str] = {}
        
        # Map of relationship_type -> set of relationship_ids
        self._type_index: Dict[str, Set[str]] = {}
        
        # Cache for frequent lookups
        self._lookup_cache: Dict[str, Tuple[float, Any]] = {}
        self._cache_ttl = 10.0  # seconds
        self._enable_caching = enable_caching
        self._event_filtering = event_filtering
        
        # Performance metrics
        self._metrics = {
            "relationships_added": 0,
            "relationships_removed": 0,
            "relationships_updated": 0,
            "cache_hits": 0,
            "lookup_operations": 0,
            "events_processed": 0,
            "events_filtered_out": 0,
            "last_operation_time": 0.0
        }
        
        # Event bus for relationship-event interactions
        self._event_bus = event_bus
        
        # Default class for new relationships
        self._default_relationship_class = default_relationship_class
        
        # Storage directory for persistence
        self._storage_dir = storage_dir
        
        # Event type filters for specific relationship types
        self._event_filters: Dict[str, Callable[[BaseEvent], bool]] = {}
        
        # Create storage directory if specified and doesn't exist
        if storage_dir and not os.path.exists(storage_dir):
            os.makedirs(storage_dir)
            
        # Register with event bus if provided
        if event_bus:
            self._register_with_event_bus()
            
        logger.info(f"Initialized RelationshipManager with caching={'enabled' if enable_caching else 'disabled'} " +
                  f"and event_filtering={'enabled' if event_filtering else 'disabled'}")
    
    def add_relationship(self, relationship: BaseRelationship) -> None:
        """
        Add a relationship to the manager.
        
        Args:
            relationship: The relationship to add
            
        Raises:
            ValueError: If a relationship between these agents already exists
        """
        start_time = time.time()
        
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
        
        # Update metrics
        self._metrics["relationships_added"] += 1
        
        # Clear relevant cache entries if caching is enabled
        if self._enable_caching:
            agent_a_id, agent_b_id = relationship.agent_a_id, relationship.agent_b_id
            cache_keys_to_clear = []
            
            # Remove all cache entries involving these agents
            for key in self._lookup_cache.keys():
                if (f"agent:{agent_a_id}" in key or
                    f"agent:{agent_b_id}" in key or
                    f"type:{rel_type}" in key):
                    cache_keys_to_clear.append(key)
                    
            for key in cache_keys_to_clear:
                self._lookup_cache.pop(key, None)
                
            if cache_keys_to_clear:
                logger.debug(f"Cleared {len(cache_keys_to_clear)} cache entries after adding relationship")
        
        # Log operation time
        operation_time = time.time() - start_time
        self._metrics["last_operation_time"] = operation_time
        if operation_time > 0.01:  # Log slow operations
            logger.debug(f"Slow relationship add: {relationship.id} took {operation_time:.4f}s")
    
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
        start_time = time.time()
        self._metrics["lookup_operations"] += 1
        
        # Check cache if enabled
        if self._enable_caching:
            cache_key = f"rel_between:{agent_a_id}:{agent_b_id}"
            if cache_key in self._lookup_cache:
                cache_time, cached_result = self._lookup_cache[cache_key]
                if time.time() - cache_time < self._cache_ttl:
                    self._metrics["cache_hits"] += 1
                    return cached_result
                    
        # Lookup relationship
        agent_pair = self._get_agent_pair_key(agent_a_id, agent_b_id)
        relationship_id = self._agent_pair_index.get(agent_pair)
        
        result = None
        if relationship_id:
            result = self._relationships.get(relationship_id)
        
        # Store in cache if enabled
        if self._enable_caching:
            cache_key = f"rel_between:{agent_a_id}:{agent_b_id}"
            self._lookup_cache[cache_key] = (time.time(), result)
            
            # Limit cache size
            if len(self._lookup_cache) > 1000:  # Arbitrary but reasonable limit
                # Remove oldest 20% of entries
                oldest_keys = sorted(
                    self._lookup_cache.keys(),
                    key=lambda k: self._lookup_cache[k][0]
                )[:int(len(self._lookup_cache) * 0.2)]
                for key in oldest_keys:
                    del self._lookup_cache[key]
        
        # Update metrics
        operation_time = time.time() - start_time
        self._metrics["last_operation_time"] = operation_time
            
        return result
    
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
        start_time = time.time()
        self._metrics["events_processed"] += 1
        
        # Skip processing if no agents are involved
        if not event.source and not event.target and not event.data.get("participants"):
            self._metrics["events_filtered_out"] += 1
            return 0
        
        # Apply event filters if enabled
        if self._event_filtering:
            # Filter events by type for specific relationship types
            event_type = event.event_type
            # Skip events that we know don't affect relationships
            if event_type.startswith("system.") or event_type.startswith("log."):
                self._metrics["events_filtered_out"] += 1
                return 0
                
            # Apply custom filters if any
            for rel_type, filter_func in self._event_filters.items():
                if not filter_func(event):
                    # This event doesn't apply to this relationship type
                    continue
        
        updated_count = 0
        
        # Determine which agents are involved in the event
        involved_agents = self._get_involved_agents(event)
        
        # Skip if less than 2 agents involved
        if len(involved_agents) < 2:
            self._metrics["events_filtered_out"] += 1
            return 0
            
        # Track relationships to update
        to_update = []
        
        # Find relationships between involved agents
        for i, agent_a_id in enumerate(involved_agents):
            for agent_b_id in involved_agents[i+1:]:
                relationship = self.get_relationship_between(agent_a_id, agent_b_id)
                if relationship:
                    to_update.append(relationship)
        
        # Update identified relationships
        for relationship in to_update:
            if relationship.update(event):
                updated_count += 1
                self._metrics["relationships_updated"] += 1
                
                # Clear relevant cache entries if caching is enabled
                if self._enable_caching:
                    cache_keys_to_clear = []
                    agent_a_id, agent_b_id = relationship.agent_a_id, relationship.agent_b_id
                    rel_type = relationship.relationship_type
                    
                    # Remove all cache entries involving these agents
                    for key in self._lookup_cache.keys():
                        if (f"agent:{agent_a_id}" in key or
                            f"agent:{agent_b_id}" in key or
                            f"rel_between:{agent_a_id}" in key or
                            f"rel_between:{agent_b_id}" in key or
                            f"type:{rel_type}" in key):
                            cache_keys_to_clear.append(key)
                            
                    for key in cache_keys_to_clear:
                        self._lookup_cache.pop(key, None)
        
        # Log slow event processing
        operation_time = time.time() - start_time
        self._metrics["last_operation_time"] = operation_time
        
        if operation_time > 0.05:  # Log slow event processing
            logger.debug(f"Slow relationship update: {event.event_type} affected {updated_count} relationships, took {operation_time:.4f}s")
            
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