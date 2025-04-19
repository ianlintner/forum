"""
Memory Interface for Agentic Game Framework.

This module defines the core interfaces for memory implementations that allow
agents to store, retrieve, and manage their experiences and knowledge.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union

from ..events.base import BaseEvent


class MemoryItem:
    """
    Base class for memory entries.
    
    Memory items represent discrete pieces of information that agents can
    remember, such as events, facts, or experiences. Each item has an ID,
    timestamp, content, importance score, and optional associations.
    
    Attributes:
        id (str): Unique identifier for the memory
        timestamp (float): When the memory was created/occurred
        content (Any): The actual content of the memory
        importance (float): How important this memory is (0.0-1.0)
        associations (Dict[str, Any]): Related concepts or metadata
    """
    
    def __init__(
        self,
        memory_id: str,
        timestamp: float,
        content: Any,
        importance: float = 0.5,
        associations: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a new memory item.
        
        Args:
            memory_id: Unique identifier for the memory
            timestamp: When the memory was created/occurred
            content: The actual content of the memory
            importance: How important this memory is (0.0-1.0)
            associations: Related concepts or metadata
        """
        self.id = memory_id
        self.timestamp = timestamp
        self.content = content
        self.importance = max(0.0, min(1.0, importance))  # Clamp to [0.0, 1.0]
        self.associations = associations or {}
    
    def update_importance(self, new_importance: float) -> None:
        """
        Update the importance score of this memory.
        
        Args:
            new_importance: New importance score (0.0-1.0)
        """
        self.importance = max(0.0, min(1.0, new_importance))
    
    def add_association(self, key: str, value: Any) -> None:
        """
        Add a new association to this memory.
        
        Args:
            key: Association key
            value: Association value
        """
        self.associations[key] = value
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the memory item to a dictionary representation.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the memory item
        """
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "content": self.content,
            "importance": self.importance,
            "associations": self.associations
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryItem':
        """
        Create a memory item from a dictionary representation.
        
        Args:
            data: Dictionary containing memory item data
            
        Returns:
            MemoryItem: A new memory item instance
            
        Raises:
            ValueError: If the dictionary is missing required fields
        """
        required_fields = ["id", "timestamp", "content"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Memory item dictionary must contain '{field}'")
                
        return cls(
            memory_id=data["id"],
            timestamp=data["timestamp"],
            content=data["content"],
            importance=data.get("importance", 0.5),
            associations=data.get("associations", {})
        )


class EventMemoryItem(MemoryItem):
    """
    Memory item specifically for storing events.
    
    This specialized memory item is designed to store event information,
    making it easier to retrieve and process event-related memories.
    
    Attributes:
        event_type (str): The type of the stored event
        source (Optional[str]): The source of the event
        target (Optional[str]): The target of the event
    """
    
    def __init__(
        self,
        memory_id: str,
        timestamp: float,
        event: BaseEvent,
        importance: float = 0.5,
        associations: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a new event memory item.
        
        Args:
            memory_id: Unique identifier for the memory
            timestamp: When the memory was created/occurred
            event: The event to store
            importance: How important this memory is (0.0-1.0)
            associations: Related concepts or metadata
        """
        super().__init__(
            memory_id=memory_id,
            timestamp=timestamp,
            content=event.to_dict(),
            importance=importance,
            associations=associations or {}
        )
        self.event_type = event.event_type
        self.source = event.source
        self.target = event.target
        
        # Add event-specific associations
        self.add_association("event_type", event.event_type)
        if event.source:
            self.add_association("source", event.source)
        if event.target:
            self.add_association("target", event.target)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EventMemoryItem':
        """
        Create an event memory item from a dictionary representation.
        
        Args:
            data: Dictionary containing memory item data
            
        Returns:
            EventMemoryItem: A new event memory item instance
            
        Raises:
            ValueError: If the dictionary is missing required fields
        """
        memory_item = super().from_dict(data)
        
        # Extract event-specific fields
        event_data = memory_item.content
        memory_item.event_type = event_data.get("event_type")
        memory_item.source = event_data.get("source")
        memory_item.target = event_data.get("target")
        
        return memory_item


class MemoryInterface(ABC):
    """
    Abstract interface for memory implementations.
    
    This interface defines the core operations that any memory system must
    support, including adding memories, retrieving memories based on queries,
    and forgetting memories.
    """
    
    @abstractmethod
    def add_memory(self, memory_item: MemoryItem) -> str:
        """
        Add a new memory item to the memory store.
        
        Args:
            memory_item: The memory item to add
            
        Returns:
            str: The ID of the added memory item
        """
        pass
    
    @abstractmethod
    def retrieve_memories(
        self, 
        query: Dict[str, Any], 
        limit: Optional[int] = None,
        importance_threshold: Optional[float] = None
    ) -> List[MemoryItem]:
        """
        Retrieve memories that match the given query.
        
        Args:
            query: Dictionary of search criteria
            limit: Maximum number of memories to return
            importance_threshold: Minimum importance score for returned memories
            
        Returns:
            List[MemoryItem]: List of matching memory items
        """
        pass
    
    @abstractmethod
    def get_memory(self, memory_id: str) -> Optional[MemoryItem]:
        """
        Get a specific memory by ID.
        
        Args:
            memory_id: ID of the memory to retrieve
            
        Returns:
            Optional[MemoryItem]: The memory item, or None if not found
        """
        pass
    
    @abstractmethod
    def update_memory(self, memory_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update a memory item.
        
        Args:
            memory_id: ID of the memory to update
            updates: Dictionary of fields to update
            
        Returns:
            bool: True if the memory was updated, False if not found
        """
        pass
    
    @abstractmethod
    def forget(self, memory_id: str) -> bool:
        """
        Remove a memory from the memory store.
        
        Args:
            memory_id: ID of the memory to forget
            
        Returns:
            bool: True if the memory was forgotten, False if not found
        """
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """
        Clear all memories from the memory store.
        """
        pass