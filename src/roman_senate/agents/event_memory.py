"""
Roman Senate AI Game
Event Memory Module

This module provides a specialized memory system for tracking and retrieving
events within the Roman Senate simulation. It adapts the agentic_game_framework
memory interface to work with the Roman Senate event system.

Part of the Migration Plan: Phase 2 - Agent System Migration.
"""

import uuid
import datetime
from typing import Dict, List, Any, Optional, Set, Union

from agentic_game_framework.memory.memory_interface import MemoryInterface, EventMemoryItem as FrameworkEventMemoryItem

from ..core.events.base import BaseEvent as RomanEvent
from .memory_base import MemoryBase
from .memory_index import MemoryIndex


class EventMemoryItem(MemoryBase):
    """
    Memory item specifically for storing Roman Senate events.
    
    This specialized memory item integrates the framework's EventMemoryItem
    concepts with the Roman Senate's MemoryBase system, creating a bridge
    between the two architectures.
    
    Attributes:
        event_type (str): The type of the stored event
        source (Optional[str]): The source of the event (typically a senator or component)
        target (Optional[str]): The target of the event (if applicable)
        content (Dict[str, Any]): The event data
        timestamp (datetime): When the event occurred
        importance (float): How important this memory is (0.0 to 1.0)
        decay_rate (float): How quickly the memory fades (0.0 to 1.0)
        tags (List[str]): List of tags for categorizing the memory
        emotional_impact (float): Emotional significance (-1.0 to 1.0)
    """
    
    def __init__(
        self,
        event: RomanEvent,
        importance: float = 0.5,
        decay_rate: float = 0.1,
        tags: Optional[List[str]] = None,
        emotional_impact: float = 0.0,
        memory_id: Optional[str] = None
    ):
        """
        Initialize a new event memory item.
        
        Args:
            event: The Roman event to store
            importance: How important this memory is (0.0 to 1.0)
            decay_rate: How quickly the memory fades (0.0 to 1.0)
            tags: List of tags for categorizing the memory
            emotional_impact: Emotional significance (-1.0 to 1.0)
            memory_id: Unique identifier (generated if not provided)
        """
        # Convert timestamp from event to datetime if needed
        if isinstance(event.timestamp, datetime.datetime):
            timestamp = event.timestamp
        else:
            # Handle the case where timestamp might be a different format
            timestamp = datetime.datetime.now()
        
        # Initialize base memory attributes
        super().__init__(
            timestamp=timestamp,
            importance=importance,
            decay_rate=decay_rate,
            tags=tags or [],
            emotional_impact=emotional_impact
        )
        
        # Store event-specific fields
        self.memory_id = memory_id or str(uuid.uuid4())
        self.event_type = event.event_type
        self.source = event.source
        self.target = event.target
        self.content = event.to_dict()
        
        # Add event metadata as tags if not already present
        self._add_event_tags(event)
    
    def _add_event_tags(self, event: RomanEvent) -> None:
        """
        Add relevant event metadata as tags.
        
        Args:
            event: The event to extract tags from
        """
        # Add event type as a tag
        if self.event_type and self.event_type not in self.tags:
            self.tags.append(self.event_type)
            
        # Add source as a tag if available
        if self.source and self.source not in self.tags:
            self.tags.append(f"source:{self.source}")
            
        # Add target as a tag if available
        if self.target and self.target not in self.tags:
            self.tags.append(f"target:{self.target}")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the memory item to a dictionary for serialization.
        
        Returns:
            Dictionary representation of the memory item
        """
        data = super().to_dict()
        data.update({
            "memory_id": self.memory_id,
            "event_type": self.event_type,
            "source": self.source,
            "target": self.target,
            "content": self.content
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EventMemoryItem':
        """
        Create an event memory item from a dictionary representation.
        
        This method is used for deserializing stored memory items.
        
        Args:
            data: Dictionary containing event memory data
            
        Returns:
            A new EventMemoryItem instance
            
        Raises:
            ValueError: If the dictionary is missing required fields
        """
        # Extract required fields for recreating an event
        if "content" not in data:
            raise ValueError("Event memory dictionary must contain 'content'")
            
        # Create a dummy event from the content
        # In a real implementation, we would reconstruct the actual event
        # but for deserialization purposes, we'll use a simplified approach
        from ..core.events.base import RomanEvent
        event = RomanEvent(
            event_type=data.get("event_type", "unknown"),
            source=data.get("source"),
            target=data.get("target"),
            data=data.get("content", {})
        )
        
        # Parse timestamp
        timestamp = datetime.datetime.fromisoformat(data["timestamp"])
        event.timestamp = timestamp
        
        # Create memory item
        memory = cls(
            event=event,
            importance=data.get("importance", 0.5),
            decay_rate=data.get("decay_rate", 0.1),
            tags=data.get("tags", []),
            emotional_impact=data.get("emotional_impact", 0.0),
            memory_id=data.get("memory_id")
        )
        
        return memory
    
    def get_event(self) -> RomanEvent:
        """
        Reconstruct the original event from this memory item.
        
        Returns:
            RomanEvent: The original event
        """
        from ..core.events.base import RomanEvent
        event = RomanEvent(
            event_type=self.event_type,
            source=self.source,
            target=self.target,
            data=self.content.get("data", {})
        )
        event.timestamp = self.timestamp
        return event


class EventMemory(MemoryInterface):
    """
    Memory system for tracking and retrieving events.
    
    This implementation adapts the agentic_game_framework's MemoryInterface
    to work with the Roman Senate's event system and memory architecture.
    It uses a MemoryIndex for efficient retrieval.
    """
    
    def __init__(self, owner_id: Optional[str] = None):
        """
        Initialize a new event memory system.
        
        Args:
            owner_id: Optional identifier for the owner of this memory system
        """
        self.owner_id = owner_id
        self.index = MemoryIndex()
        self._memory_items: Dict[str, EventMemoryItem] = {}
    
    def add_memory(self, memory_item: Union[EventMemoryItem, FrameworkEventMemoryItem]) -> str:
        """
        Add a new memory item to the memory store.
        
        This method accepts either a Roman Senate EventMemoryItem or a
        framework EventMemoryItem, adapting the latter if necessary.
        
        Args:
            memory_item: The memory item to add
            
        Returns:
            str: The ID of the added memory item
            
        Raises:
            TypeError: If memory_item is not a supported type
        """
        # Handle framework EventMemoryItem if provided
        if isinstance(memory_item, FrameworkEventMemoryItem):
            # Extract event data from framework memory item
            event_data = memory_item.content
            
            # Create a Roman event from the framework event data
            from ..core.events.base import RomanEvent
            event = RomanEvent(
                event_type=event_data.get("event_type", "unknown"),
                source=event_data.get("source"),
                target=event_data.get("target"),
                data=event_data.get("data", {})
            )
            
            # Convert to a Roman Senate EventMemoryItem
            memory_item = EventMemoryItem(
                event=event,
                importance=memory_item.importance,
                memory_id=memory_item.id
            )
        elif not isinstance(memory_item, EventMemoryItem):
            raise TypeError("Memory item must be an EventMemoryItem")
        
        # Store the memory item
        memory_id = memory_item.memory_id
        self._memory_items[memory_id] = memory_item
        
        # Add to the index
        self.index.add_memory(memory_item)
        
        return memory_id
    
    def add_event(self, event: RomanEvent, importance: float = 0.5) -> str:
        """
        Add an event directly to the memory store.
        
        This is a convenience method that creates an EventMemoryItem from the event.
        
        Args:
            event: The event to store
            importance: How important this memory is (0.0 to 1.0)
            
        Returns:
            str: The ID of the added memory item
        """
        memory_item = EventMemoryItem(event=event, importance=importance)
        return self.add_memory(memory_item)
    
    def retrieve_memories(
        self, 
        query: Dict[str, Any], 
        limit: Optional[int] = None,
        importance_threshold: Optional[float] = None
    ) -> List[EventMemoryItem]:
        """
        Retrieve memories that match the given query.
        
        Args:
            query: Dictionary of search criteria
            limit: Maximum number of memories to return
            importance_threshold: Minimum importance score for returned memories
            
        Returns:
            List[EventMemoryItem]: List of matching memory items
        """
        # Map query parameters to memory index criteria
        index_criteria = {}
        
        # Map common fields
        if "event_type" in query:
            index_criteria["event_type"] = query["event_type"]
        if "source" in query:
            index_criteria["senator_name"] = query["source"]
        if "target" in query:
            index_criteria["tags"] = [f"target:{query['target']}"]
        if "time_start" in query:
            index_criteria["time_start"] = query["time_start"]
        if "time_end" in query:
            index_criteria["time_end"] = query["time_end"]
        if importance_threshold is not None:
            index_criteria["min_strength"] = importance_threshold
            
        # Execute query
        results = self.index.query(index_criteria)
        
        # Filter for EventMemoryItem instances only
        event_memories = [m for m in results if isinstance(m, EventMemoryItem)]
        
        # Apply limit if specified
        if limit is not None and limit > 0:
            event_memories = event_memories[:limit]
            
        return event_memories
    
    def get_memory(self, memory_id: str) -> Optional[EventMemoryItem]:
        """
        Get a specific memory by ID.
        
        Args:
            memory_id: ID of the memory to retrieve
            
        Returns:
            Optional[EventMemoryItem]: The memory item, or None if not found
        """
        return self._memory_items.get(memory_id)
    
    def update_memory(self, memory_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update a memory item.
        
        Args:
            memory_id: ID of the memory to update
            updates: Dictionary of fields to update
            
        Returns:
            bool: True if the memory was updated, False if not found
        """
        memory_item = self.get_memory(memory_id)
        if not memory_item:
            return False
            
        # Apply updates
        for key, value in updates.items():
            if hasattr(memory_item, key):
                setattr(memory_item, key, value)
                
        # If importance or decay_rate changed, update indices
        if "importance" in updates or "decay_rate" in updates:
            self.index.update_indices()
            
        return True
    
    def forget(self, memory_id: str) -> bool:
        """
        Remove a memory item from the store.
        
        Args:
            memory_id: ID of the memory to remove
            
        Returns:
            bool: True if the memory was removed, False if not found
        """
        memory_item = self._memory_items.pop(memory_id, None)
        if memory_item:
            self.index.remove_memory(memory_item)
            return True
        return False
    
    def clear(self) -> None:
        """
        Remove all memories from the store.
        """
        self._memory_items.clear()
        self.index = MemoryIndex()
    
    def get_events_by_type(self, event_type: str, limit: Optional[int] = None) -> List[RomanEvent]:
        """
        Get events of a specific type.
        
        Args:
            event_type: The event type to retrieve
            limit: Maximum number of events to return
            
        Returns:
            List[RomanEvent]: List of matching events
        """
        memories = self.retrieve_memories({"event_type": event_type}, limit=limit)
        return [memory.get_event() for memory in memories]
    
    def get_events_by_source(self, source: str, limit: Optional[int] = None) -> List[RomanEvent]:
        """
        Get events from a specific source.
        
        Args:
            source: The source to retrieve events from
            limit: Maximum number of events to return
            
        Returns:
            List[RomanEvent]: List of matching events
        """
        memories = self.retrieve_memories({"source": source}, limit=limit)
        return [memory.get_event() for memory in memories]
    
    def get_events_by_target(self, target: str, limit: Optional[int] = None) -> List[RomanEvent]:
        """
        Get events targeting a specific entity.
        
        Args:
            target: The target to retrieve events for
            limit: Maximum number of events to return
            
        Returns:
            List[RomanEvent]: List of matching events
        """
        memories = self.retrieve_memories({"target": target}, limit=limit)
        return [memory.get_event() for memory in memories]
    
    def get_recent_events(self, limit: int = 10) -> List[RomanEvent]:
        """
        Get the most recent events.
        
        Args:
            limit: Maximum number of events to return
            
        Returns:
            List[RomanEvent]: List of recent events
        """
        # Sort all event memories by timestamp (newest first)
        sorted_memories = sorted(
            [m for m in self._memory_items.values()],
            key=lambda m: m.timestamp,
            reverse=True
        )
        
        # Apply limit
        recent_memories = sorted_memories[:limit]
        
        # Convert to events
        return [memory.get_event() for memory in recent_memories]
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the event memory to a dictionary for serialization.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the event memory
        """
        return {
            "owner_id": self.owner_id,
            "memory_items": {
                memory_id: memory.to_dict()
                for memory_id, memory in self._memory_items.items()
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EventMemory':
        """
        Create an event memory from a dictionary representation.
        
        Args:
            data: Dictionary containing event memory data
            
        Returns:
            EventMemory: A new event memory instance
        """
        memory = cls(owner_id=data.get("owner_id"))
        
        # Restore memory items
        for memory_id, memory_data in data.get("memory_items", {}).items():
            memory_item = EventMemoryItem.from_dict(memory_data)
            memory._memory_items[memory_id] = memory_item
            memory.index.add_memory(memory_item)
            
        return memory