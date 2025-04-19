"""
Memory Persistence for Agentic Game Framework.

This module provides functionality for saving and loading agent memories
to and from persistent storage.
"""

import json
import os
from typing import Any, Dict, List, Optional, Type

from .memory_interface import MemoryItem


class MemoryPersistenceManager:
    """
    Handles saving and loading memories to/from persistent storage.
    
    The MemoryPersistenceManager provides a standardized way to persist agent
    memories across sessions. It supports:
    1. Saving memories to JSON files
    2. Loading memories from JSON files
    3. Managing memory versioning
    
    This ensures that agent memories can be preserved between runs.
    """
    
    def __init__(
        self,
        storage_dir: str,
        memory_class: Type[MemoryItem] = MemoryItem,
        create_dir: bool = True
    ):
        """
        Initialize a new memory persistence manager.
        
        Args:
            storage_dir: Directory to store memory files
            memory_class: Class to use for memory instantiation
            create_dir: Whether to create the storage directory if it doesn't exist
        """
        self.storage_dir = storage_dir
        self.memory_class = memory_class
        
        if create_dir and not os.path.exists(storage_dir):
            os.makedirs(storage_dir)
    
    def save_memories(self, agent_id: str, memories: List[MemoryItem]) -> bool:
        """
        Save a list of memories to a file.
        
        Args:
            agent_id: ID of the agent these memories belong to
            memories: List of memory items to save
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Convert memories to dictionaries
            memory_dicts = [memory.to_dict() for memory in memories]
            
            # Create the file path
            file_path = os.path.join(self.storage_dir, f"{agent_id}_memories.json")
            
            # Save to file
            with open(file_path, 'w') as f:
                json.dump(memory_dicts, f, indent=2)
                
            return True
        except Exception as e:
            # In a real system, we would log this error
            print(f"Error saving memories for agent {agent_id}: {e}")
            return False
    
    def load_memories(self, agent_id: str) -> List[MemoryItem]:
        """
        Load memories from a file.
        
        Args:
            agent_id: ID of the agent to load memories for
            
        Returns:
            List[MemoryItem]: List of loaded memory items
        """
        file_path = os.path.join(self.storage_dir, f"{agent_id}_memories.json")
        
        if not os.path.exists(file_path):
            return []
            
        try:
            # Load from file
            with open(file_path, 'r') as f:
                memory_dicts = json.load(f)
                
            # Convert dictionaries to memory items
            memories = [self.memory_class.from_dict(memory_dict) for memory_dict in memory_dicts]
            
            return memories
        except Exception as e:
            # In a real system, we would log this error
            print(f"Error loading memories for agent {agent_id}: {e}")
            return []
    
    def delete_memories(self, agent_id: str) -> bool:
        """
        Delete all memories for an agent.
        
        Args:
            agent_id: ID of the agent to delete memories for
            
        Returns:
            bool: True if successful, False otherwise
        """
        file_path = os.path.join(self.storage_dir, f"{agent_id}_memories.json")
        
        if not os.path.exists(file_path):
            return True
            
        try:
            os.remove(file_path)
            return True
        except Exception as e:
            # In a real system, we would log this error
            print(f"Error deleting memories for agent {agent_id}: {e}")
            return False
    
    def backup_memories(self, agent_id: str, backup_suffix: str = "backup") -> bool:
        """
        Create a backup of an agent's memories.
        
        Args:
            agent_id: ID of the agent to backup memories for
            backup_suffix: Suffix to add to the backup file name
            
        Returns:
            bool: True if successful, False otherwise
        """
        file_path = os.path.join(self.storage_dir, f"{agent_id}_memories.json")
        backup_path = os.path.join(self.storage_dir, f"{agent_id}_memories_{backup_suffix}.json")
        
        if not os.path.exists(file_path):
            return False
            
        try:
            # Read the original file
            with open(file_path, 'r') as f:
                content = f.read()
                
            # Write to backup file
            with open(backup_path, 'w') as f:
                f.write(content)
                
            return True
        except Exception as e:
            # In a real system, we would log this error
            print(f"Error backing up memories for agent {agent_id}: {e}")
            return False
    
    def list_agent_ids(self) -> List[str]:
        """
        List all agent IDs with saved memories.
        
        Returns:
            List[str]: List of agent IDs
        """
        try:
            # Get all files in the storage directory
            files = os.listdir(self.storage_dir)
            
            # Filter for memory files and extract agent IDs
            agent_ids = []
            for file in files:
                if file.endswith("_memories.json"):
                    agent_id = file.replace("_memories.json", "")
                    agent_ids.append(agent_id)
                    
            return agent_ids
        except Exception as e:
            # In a real system, we would log this error
            print(f"Error listing agent IDs: {e}")
            return []


class MemoryStore:
    """
    In-memory implementation of the MemoryInterface with persistence support.
    
    The MemoryStore combines the MemoryInterface with persistence capabilities,
    allowing memories to be stored in memory during runtime and saved/loaded
    to/from disk as needed.
    """
    
    def __init__(
        self,
        agent_id: str,
        persistence_manager: Optional[MemoryPersistenceManager] = None,
        auto_save: bool = False
    ):
        """
        Initialize a new memory store.
        
        Args:
            agent_id: ID of the agent this store belongs to
            persistence_manager: Optional manager for saving/loading memories
            auto_save: Whether to automatically save after modifications
        """
        self.agent_id = agent_id
        self.persistence_manager = persistence_manager
        self.auto_save = auto_save
        
        # Map of memory_id -> memory_item
        self._memories: Dict[str, MemoryItem] = {}
        
        # Load memories if persistence manager is provided
        if persistence_manager:
            self._load_memories()
    
    def add_memory(self, memory_item: MemoryItem) -> str:
        """
        Add a new memory item to the store.
        
        Args:
            memory_item: The memory item to add
            
        Returns:
            str: The ID of the added memory item
        """
        memory_id = memory_item.id
        self._memories[memory_id] = memory_item
        
        if self.auto_save and self.persistence_manager:
            self._save_memories()
            
        return memory_id
    
    def get_memory(self, memory_id: str) -> Optional[MemoryItem]:
        """
        Get a specific memory by ID.
        
        Args:
            memory_id: ID of the memory to retrieve
            
        Returns:
            Optional[MemoryItem]: The memory item, or None if not found
        """
        return self._memories.get(memory_id)
    
    def update_memory(self, memory_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update a memory item.
        
        Args:
            memory_id: ID of the memory to update
            updates: Dictionary of fields to update
            
        Returns:
            bool: True if the memory was updated, False if not found
        """
        if memory_id not in self._memories:
            return False
            
        memory = self._memories[memory_id]
        
        # Update importance if specified
        if "importance" in updates:
            memory.update_importance(updates["importance"])
            
        # Update associations if specified
        if "associations" in updates:
            for key, value in updates["associations"].items():
                memory.add_association(key, value)
                
        # Update content if specified
        if "content" in updates:
            memory.content = updates["content"]
            
        if self.auto_save and self.persistence_manager:
            self._save_memories()
            
        return True
    
    def forget(self, memory_id: str) -> bool:
        """
        Remove a memory from the store.
        
        Args:
            memory_id: ID of the memory to forget
            
        Returns:
            bool: True if the memory was forgotten, False if not found
        """
        if memory_id not in self._memories:
            return False
            
        del self._memories[memory_id]
        
        if self.auto_save and self.persistence_manager:
            self._save_memories()
            
        return True
    
    def retrieve_memories(
        self, 
        query: Dict[str, Any], 
        limit: Optional[int] = None,
        importance_threshold: Optional[float] = None
    ) -> List[MemoryItem]:
        """
        Retrieve memories that match the given query.
        
        This is a simple implementation that scans all memories.
        For more efficient retrieval, use a MemoryIndex.
        
        Args:
            query: Dictionary of search criteria
            limit: Maximum number of memories to return
            importance_threshold: Minimum importance score for returned memories
            
        Returns:
            List[MemoryItem]: List of matching memory items
        """
        results = []
        
        for memory in self._memories.values():
            # Skip if below importance threshold
            if importance_threshold is not None and memory.importance < importance_threshold:
                continue
                
            # Check if memory matches query
            if self._matches_query(memory, query):
                results.append(memory)
                
        # Sort by recency (newest first)
        results.sort(key=lambda memory: memory.timestamp, reverse=True)
        
        # Apply limit if specified
        if limit is not None:
            results = results[:limit]
            
        return results
    
    def _matches_query(self, memory: MemoryItem, query: Dict[str, Any]) -> bool:
        """
        Check if a memory matches a query.
        
        Args:
            memory: The memory to check
            query: Dictionary of search criteria
            
        Returns:
            bool: True if the memory matches the query
        """
        # Check timestamp range
        if "timestamp_min" in query and memory.timestamp < query["timestamp_min"]:
            return False
        if "timestamp_max" in query and memory.timestamp > query["timestamp_max"]:
            return False
            
        # Check importance
        if "importance_min" in query and memory.importance < query["importance_min"]:
            return False
            
        # Check associations
        if "associations" in query:
            for key, value in query["associations"].items():
                if key not in memory.associations or memory.associations[key] != value:
                    return False
                    
        # Check text content (simple substring search)
        if "text" in query and isinstance(query["text"], str):
            text = query["text"].lower()
            
            # Check in content if it's a string
            if isinstance(memory.content, str):
                if text not in memory.content.lower():
                    return False
            # Check in content values if it's a dictionary
            elif isinstance(memory.content, dict):
                found = False
                for value in memory.content.values():
                    if isinstance(value, str) and text in value.lower():
                        found = True
                        break
                if not found:
                    return False
                    
        return True
    
    def clear(self) -> None:
        """
        Clear all memories from the store.
        """
        self._memories.clear()
        
        if self.auto_save and self.persistence_manager:
            self._save_memories()
    
    def get_all_memories(self) -> List[MemoryItem]:
        """
        Get all memories in the store.
        
        Returns:
            List[MemoryItem]: List of all memory items
        """
        return list(self._memories.values())
    
    def save(self) -> bool:
        """
        Save all memories to persistent storage.
        
        Returns:
            bool: True if successful, False otherwise
        """
        return self._save_memories()
    
    def _save_memories(self) -> bool:
        """
        Save all memories to persistent storage.
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.persistence_manager:
            return False
            
        return self.persistence_manager.save_memories(
            self.agent_id,
            list(self._memories.values())
        )
    
    def _load_memories(self) -> None:
        """
        Load memories from persistent storage.
        """
        if not self.persistence_manager:
            return
            
        memories = self.persistence_manager.load_memories(self.agent_id)
        
        for memory in memories:
            self._memories[memory.id] = memory