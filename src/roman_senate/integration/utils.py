"""
Utility Functions for Roman Senate Framework Integration.

This module provides helper functions and utilities to support the integration
between the Roman Senate and agentic_game_framework systems.

Part of the Migration Plan: Phase 4 - Integration Layer.
"""

from typing import Dict, Any, Optional, Union, Type, Callable
from datetime import datetime
import uuid
import logging
from functools import lru_cache

from agentic_game_framework.memory.memory_interface import MemoryInterface as FrameworkMemoryInterface
from agentic_game_framework.memory.memory_interface import MemoryItem as FrameworkMemoryItem

from ..agents.memory_base import BaseMemory
from ..agents.agent_memory import AgentMemory
from ..agents.event_memory import EventMemory
from ..agents.enhanced_event_memory import EnhancedEventMemory


logger = logging.getLogger(__name__)


def convert_roman_timestamp(timestamp: datetime) -> datetime:
    """
    Convert a Roman Senate timestamp to agentic_game_framework format.
    
    Both systems use datetime objects, but this function is a placeholder
    for any transformations that might be needed.
    
    Args:
        timestamp: Roman Senate timestamp
        
    Returns:
        datetime: agentic_game_framework compatible timestamp
    """
    # Currently both systems use datetime objects directly,
    # but this is a placeholder for any conversion that might be needed
    return timestamp


def convert_framework_timestamp(timestamp: datetime) -> datetime:
    """
    Convert an agentic_game_framework timestamp to Roman Senate format.
    
    Both systems use datetime objects, but this function is a placeholder
    for any transformations that might be needed.
    
    Args:
        timestamp: agentic_game_framework timestamp
        
    Returns:
        datetime: Roman Senate compatible timestamp
    """
    # Currently both systems use datetime objects directly,
    # but this is a placeholder for any conversion that might be needed
    return timestamp


@lru_cache(maxsize=100)
def get_roman_event_type(framework_event_type: str, mappings: Optional[Dict[str, str]] = None) -> str:
    """
    Get the corresponding Roman Senate event type for a framework event type.
    
    Args:
        framework_event_type: agentic_game_framework event type
        mappings: Optional mappings dictionary (framework_type -> roman_type)
        
    Returns:
        str: Corresponding Roman Senate event type, or the original if no mapping exists
    """
    if mappings and framework_event_type in mappings:
        return mappings[framework_event_type]
    return framework_event_type


@lru_cache(maxsize=100)
def get_framework_event_type(roman_event_type: str, mappings: Optional[Dict[str, str]] = None) -> str:
    """
    Get the corresponding agentic_game_framework event type for a Roman event type.
    
    Args:
        roman_event_type: Roman Senate event type
        mappings: Optional mappings dictionary (roman_type -> framework_type)
        
    Returns:
        str: Corresponding agentic_game_framework event type, or the original if no mapping exists
    """
    if mappings and roman_event_type in mappings:
        return mappings[roman_event_type]
    return roman_event_type


def get_memory_adapter(
    roman_memory: Union[BaseMemory, AgentMemory, EventMemory, EnhancedEventMemory]
) -> FrameworkMemoryInterface:
    """
    Create a memory adapter that exposes a Roman memory system through the framework interface.
    
    Args:
        roman_memory: Roman Senate memory system
        
    Returns:
        FrameworkMemoryInterface: Adapter implementing the framework interface
    """
    
    class RomanMemoryAdapter(FrameworkMemoryInterface):
        """
        Adapter that presents a Roman memory system as a framework memory interface.
        
        This adapter allows framework components to interact with Roman memory
        systems using the framework's memory interface.
        
        Attributes:
            memory: The underlying Roman memory system
        """
        
        def __init__(self, memory: Union[BaseMemory, AgentMemory, EventMemory, EnhancedEventMemory]):
            """
            Initialize the adapter.
            
            Args:
                memory: The Roman memory system to adapt
            """
            self.memory = memory
        
        def add_memory(self, memory_item: FrameworkMemoryItem) -> str:
            """
            Add a new memory item to the memory store.
            
            Args:
                memory_item: The framework memory item to add
                
            Returns:
                str: The ID of the added memory item
            """
            # Convert to Roman memory item
            memory_dict = memory_item.to_dict()
            
            # Add to Roman memory
            if hasattr(self.memory, 'add_memory_item'):
                # For EventMemory and EnhancedEventMemory
                return self.memory.add_memory_item(
                    content=memory_dict["content"],
                    importance=memory_dict["importance"],
                    metadata=memory_dict.get("associations", {})
                )
            elif hasattr(self.memory, 'add_memory'):
                # For AgentMemory
                return self.memory.add_memory(
                    memory_content=memory_dict["content"],
                    importance=memory_dict["importance"],
                    metadata=memory_dict.get("associations", {})
                )
            else:
                # For BaseMemory (simpler interface)
                self.memory.memories.append({
                    "id": memory_dict["id"],
                    "content": memory_dict["content"],
                    "timestamp": memory_dict["timestamp"],
                    "importance": memory_dict["importance"],
                })
                return memory_dict["id"]
        
        def retrieve_memories(
            self, 
            query: Dict[str, Any], 
            limit: Optional[int] = None,
            importance_threshold: Optional[float] = None
        ) -> list:
            """
            Retrieve memories that match the given query.
            
            Args:
                query: Dictionary of search criteria
                limit: Maximum number of memories to return
                importance_threshold: Minimum importance score for returned memories
                
            Returns:
                list: List of matching memory items
            """
            # Convert query to Roman format
            roman_query = {}
            
            # Map common query parameters
            if "keyword" in query:
                roman_query["keyword"] = query["keyword"]
            if "after" in query:
                roman_query["after"] = query["after"]
            if "before" in query:
                roman_query["before"] = query["before"]
            
            # Add any metadata criteria
            for key, value in query.items():
                if key not in ["keyword", "after", "before"]:
                    if "metadata" not in roman_query:
                        roman_query["metadata"] = {}
                    roman_query["metadata"][key] = value
            
            # Query Roman memory
            if hasattr(self.memory, 'query_memories'):
                # For EnhancedEventMemory
                memories = self.memory.query_memories(
                    query=roman_query,
                    limit=limit,
                    min_importance=importance_threshold
                )
            elif hasattr(self.memory, 'get_memories_by_query'):
                # For EventMemory
                memories = self.memory.get_memories_by_query(
                    query=roman_query,
                    limit=limit
                )
            elif hasattr(self.memory, 'get_memories'):
                # For AgentMemory
                memories = self.memory.get_memories(limit=limit or 100)
                
                # Apply importance filter manually
                if importance_threshold is not None:
                    memories = [m for m in memories if m.get('importance', 0) >= importance_threshold]
            else:
                # For BaseMemory (simpler interface)
                memories = self.memory.memories
                
                # Apply importance filter manually
                if importance_threshold is not None:
                    memories = [m for m in memories if m.get('importance', 0) >= importance_threshold]
                
                # Apply limit
                if limit is not None:
                    memories = memories[:limit]
            
            # Convert to framework memory items
            result = []
            for memory in memories:
                # Create a framework memory item
                if isinstance(memory, dict):
                    item = FrameworkMemoryItem(
                        memory_id=memory.get("id", str(uuid.uuid4())),
                        timestamp=memory.get("timestamp", datetime.now().timestamp()),
                        content=memory.get("content", ""),
                        importance=memory.get("importance", 0.5),
                        associations=memory.get("metadata", {})
                    )
                else:
                    # Handle cases where memory might be an object
                    item = FrameworkMemoryItem(
                        memory_id=getattr(memory, "id", str(uuid.uuid4())),
                        timestamp=getattr(memory, "timestamp", datetime.now().timestamp()),
                        content=getattr(memory, "content", ""),
                        importance=getattr(memory, "importance", 0.5),
                        associations=getattr(memory, "metadata", {})
                    )
                result.append(item)
            
            return result
        
        def get_memory(self, memory_id: str) -> Optional[FrameworkMemoryItem]:
            """
            Get a specific memory by ID.
            
            Args:
                memory_id: ID of the memory to retrieve
                
            Returns:
                Optional[FrameworkMemoryItem]: The memory item, or None if not found
            """
            # Query the Roman memory system
            if hasattr(self.memory, 'get_memory_by_id'):
                # For EnhancedEventMemory and EventMemory
                memory = self.memory.get_memory_by_id(memory_id)
            elif hasattr(self.memory, 'get_memory'):
                # For AgentMemory
                memory = self.memory.get_memory(memory_id)
            else:
                # For BaseMemory (simpler interface)
                memory = next((m for m in self.memory.memories if m.get("id") == memory_id), None)
            
            if memory is None:
                return None
            
            # Convert to framework memory item
            if isinstance(memory, dict):
                return FrameworkMemoryItem(
                    memory_id=memory.get("id", memory_id),
                    timestamp=memory.get("timestamp", datetime.now().timestamp()),
                    content=memory.get("content", ""),
                    importance=memory.get("importance", 0.5),
                    associations=memory.get("metadata", {})
                )
            else:
                # Handle cases where memory might be an object
                return FrameworkMemoryItem(
                    memory_id=getattr(memory, "id", memory_id),
                    timestamp=getattr(memory, "timestamp", datetime.now().timestamp()),
                    content=getattr(memory, "content", ""),
                    importance=getattr(memory, "importance", 0.5),
                    associations=getattr(memory, "metadata", {})
                )
        
        def update_memory(self, memory_id: str, updates: Dict[str, Any]) -> bool:
            """
            Update a memory item.
            
            Args:
                memory_id: ID of the memory to update
                updates: Dictionary of fields to update
                
            Returns:
                bool: True if the memory was updated, False if not found
            """
            # Update in the Roman memory system
            if hasattr(self.memory, 'update_memory'):
                # For EnhancedEventMemory
                return self.memory.update_memory(memory_id, updates)
            else:
                # For other memory types, find and update manually
                if hasattr(self.memory, 'get_memory_by_id'):
                    memory = self.memory.get_memory_by_id(memory_id)
                elif hasattr(self.memory, 'get_memory'):
                    memory = self.memory.get_memory(memory_id)
                else:
                    # For BaseMemory (simpler interface)
                    memory_index = next((i for i, m in enumerate(self.memory.memories) 
                                        if m.get("id") == memory_id), -1)
                    if memory_index >= 0:
                        # Update the memory
                        for key, value in updates.items():
                            self.memory.memories[memory_index][key] = value
                        return True
                    return False
                
                if memory is None:
                    return False
                
                # Update the memory
                if isinstance(memory, dict):
                    for key, value in updates.items():
                        memory[key] = value
                else:
                    # Handle cases where memory might be an object
                    for key, value in updates.items():
                        if hasattr(memory, key):
                            setattr(memory, key, value)
                
                return True
        
        def forget(self, memory_id: str) -> bool:
            """
            Remove a memory item.
            
            Args:
                memory_id: ID of the memory to remove
                
            Returns:
                bool: True if the memory was removed, False if not found
            """
            # Remove from the Roman memory system
            if hasattr(self.memory, 'remove_memory'):
                # For EnhancedEventMemory
                return self.memory.remove_memory(memory_id)
            elif hasattr(self.memory, 'forget'):
                # For some potential memory implementations
                return self.memory.forget(memory_id)
            else:
                # For other memory types, find and remove manually
                if hasattr(self.memory, 'memories'):
                    # For BaseMemory (simpler interface)
                    memory_index = next((i for i, m in enumerate(self.memory.memories) 
                                        if m.get("id") == memory_id), -1)
                    if memory_index >= 0:
                        self.memory.memories.pop(memory_index)
                        return True
                
                return False
        
        def clear(self) -> None:
            """
            Clear all memories.
            """
            # Clear the Roman memory system
            if hasattr(self.memory, 'clear'):
                self.memory.clear()
            elif hasattr(self.memory, 'clear_memories'):
                self.memory.clear_memories()
            elif hasattr(self.memory, 'memories'):
                # For BaseMemory (simpler interface)
                self.memory.memories = []
    
    # Return an instance of the adapter
    return RomanMemoryAdapter(roman_memory)


def create_bidirectional_memory_adapter(
    roman_memory: Union[BaseMemory, AgentMemory, EventMemory, EnhancedEventMemory],
    framework_memory: FrameworkMemoryInterface
) -> Callable[[FrameworkMemoryItem], None]:
    """
    Create a bidirectional memory adapter that synchronizes memories between systems.
    
    This function returns a synchronization function that can be used to propagate
    memory changes from one system to the other.
    
    Args:
        roman_memory: Roman Senate memory system
        framework_memory: agentic_game_framework memory system
        
    Returns:
        Callable: Function to synchronize a memory item to both systems
    """
    # Create adapter for Roman memory
    roman_adapter = get_memory_adapter(roman_memory)
    
    def sync_memory(memory_item: FrameworkMemoryItem) -> None:
        """
        Synchronize a memory item to both memory systems.
        
        Args:
            memory_item: The memory item to synchronize
        """
        # Add to Framework memory
        framework_memory.add_memory(memory_item)
        
        # Add to Roman memory
        roman_adapter.add_memory(memory_item)
    
    return sync_memory


def generate_unique_id(prefix: str = "") -> str:
    """
    Generate a unique ID, optionally with a prefix.
    
    Args:
        prefix: Optional prefix for the ID
        
    Returns:
        str: Unique ID
    """
    return f"{prefix}{str(uuid.uuid4())}"