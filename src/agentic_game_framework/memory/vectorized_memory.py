"""
Vectorized Memory for Agentic Game Framework.

This module extends the memory system with vector storage capabilities,
allowing for semantic retrieval of memories.
"""

import time
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np

from ..knowledge.vector_store import VectorStore, VectorStoreConfig
from .memory_interface import MemoryItem, MemoryInterface
from .memory_index import MemoryIndex


class VectorizedMemory(MemoryInterface):
    """
    Memory implementation with vector storage capabilities.
    
    This class extends the basic memory system with vector embeddings,
    allowing for semantic search and retrieval of memories based on
    their content similarity.
    
    Attributes:
        index: Memory index for efficient retrieval
        vector_store: Vector store for semantic search
    """
    
    def __init__(
        self,
        vector_store: Optional[VectorStore] = None,
        vector_store_config: Optional[VectorStoreConfig] = None
    ):
        """Initialize a new vectorized memory.
        
        Args:
            vector_store: Existing vector store to use (creates new one if None)
            vector_store_config: Configuration for the vector store (if creating a new one)
        """
        self.index = MemoryIndex()
        self.vector_store = vector_store or VectorStore(vector_store_config)
        self._memory_to_vector_id: Dict[str, str] = {}  # Maps memory IDs to vector store IDs
    
    def add_memory(self, memory_item: MemoryItem) -> str:
        """Add a new memory item to the memory store.
        
        This method adds the memory to both the index and the vector store.
        
        Args:
            memory_item: The memory item to add
            
        Returns:
            str: The ID of the added memory item
        """
        # Add to index
        self.index.index_memory(memory_item)
        
        # Add to vector store
        content = self._get_memory_content(memory_item)
        metadata = {
            "memory_id": memory_item.id,
            "timestamp": memory_item.timestamp,
            "importance": memory_item.importance
        }
        metadata.update(memory_item.associations)
        
        vector_id = self.vector_store.add_text(content, metadata)
        self._memory_to_vector_id[memory_item.id] = vector_id
        
        return memory_item.id
    
    def retrieve_memories(
        self,
        query: Dict[str, Any],
        limit: Optional[int] = None,
        importance_threshold: Optional[float] = None
    ) -> List[MemoryItem]:
        """Retrieve memories that match the given query.
        
        Args:
            query: Dictionary of search criteria
            limit: Maximum number of memories to return
            importance_threshold: Minimum importance score for returned memories
            
        Returns:
            List[MemoryItem]: List of matching memory items
        """
        # Use the index for standard queries
        return self.index.search(query, limit, importance_threshold)
    
    def retrieve_semantic(
        self,
        text_query: str,
        limit: int = 5,
        importance_threshold: Optional[float] = None
    ) -> List[Tuple[MemoryItem, float]]:
        """Retrieve memories based on semantic similarity.
        
        Args:
            text_query: The text query to search for
            limit: Maximum number of memories to return
            importance_threshold: Minimum importance score for returned memories
            
        Returns:
            List[Tuple[MemoryItem, float]]: List of (memory, similarity) tuples
        """
        # Apply importance filter if specified
        filter_metadata = None
        if importance_threshold is not None:
            filter_metadata = {"importance": {"$gte": importance_threshold}}
        
        # Search in vector store
        results = self.vector_store.search(text_query, limit, filter_metadata)
        
        # Convert to memory items
        memory_results = []
        for content, similarity in results:
            memory_id = self._get_memory_id_from_result(content)
            if memory_id:
                memory_item = self.get_memory(memory_id)
                if memory_item:
                    memory_results.append((memory_item, similarity))
        
        return memory_results
    
    def get_memory(self, memory_id: str) -> Optional[MemoryItem]:
        """Get a specific memory by ID.
        
        Args:
            memory_id: ID of the memory to retrieve
            
        Returns:
            Optional[MemoryItem]: The memory item, or None if not found
        """
        return self.index.get_memory(memory_id)
    
    def update_memory(self, memory_id: str, updates: Dict[str, Any]) -> bool:
        """Update a memory item.
        
        Args:
            memory_id: ID of the memory to update
            updates: Dictionary of fields to update
            
        Returns:
            bool: True if the memory was updated, False if not found
        """
        # Get the current memory
        memory_item = self.get_memory(memory_id)
        if not memory_item:
            return False
        
        # Update the memory in the index
        for key, value in updates.items():
            if key == "importance":
                memory_item.update_importance(value)
            elif key == "associations":
                for assoc_key, assoc_value in value.items():
                    memory_item.add_association(assoc_key, assoc_value)
            elif hasattr(memory_item, key):
                setattr(memory_item, key, value)
        
        self.index.update_memory(memory_item)
        
        # Update in vector store if it exists there
        if memory_id in self._memory_to_vector_id:
            vector_id = self._memory_to_vector_id[memory_id]
            content = self._get_memory_content(memory_item)
            metadata = {
                "memory_id": memory_item.id,
                "timestamp": memory_item.timestamp,
                "importance": memory_item.importance
            }
            metadata.update(memory_item.associations)
            
            # Since we can't directly update in most vector stores,
            # we delete and re-add
            self.vector_store.delete_item(vector_id)
            new_vector_id = self.vector_store.add_text(content, metadata)
            self._memory_to_vector_id[memory_id] = new_vector_id
        
        return True
    
    def forget(self, memory_id: str) -> bool:
        """Remove a memory from the store.
        
        Args:
            memory_id: ID of the memory to forget
            
        Returns:
            bool: True if the memory was forgotten, False if not found
        """
        # Remove from index
        result = self.index.remove_memory(memory_id)
        
        # Remove from vector store
        if memory_id in self._memory_to_vector_id:
            vector_id = self._memory_to_vector_id[memory_id]
            self.vector_store.delete_item(vector_id)
            del self._memory_to_vector_id[memory_id]
        
        return result
    
    def clear(self) -> None:
        """Clear all memories."""
        self.index.clear()
        self.vector_store.clear()
        self._memory_to_vector_id.clear()
    
    def consolidate_memories(
        self,
        threshold: float = 0.8,
        max_memories: int = 100,
        retention_policy: str = "importance"
    ) -> int:
        """Consolidate similar memories to prevent memory overload.
        
        Args:
            threshold: Similarity threshold for consolidation (0.0-1.0)
            max_memories: Maximum number of memories to keep
            retention_policy: Policy for deciding which memories to keep
                ("importance", "recency", or "both")
            
        Returns:
            int: Number of memories removed
        """
        # Get all memories
        all_memories = self.index.get_all_memories()
        
        # If we're under the limit, no need to consolidate
        if len(all_memories) <= max_memories:
            return 0
        
        # Sort memories based on retention policy
        if retention_policy == "importance":
            all_memories.sort(key=lambda m: m.importance, reverse=True)
        elif retention_policy == "recency":
            all_memories.sort(key=lambda m: m.timestamp, reverse=True)
        else:  # "both"
            # Combine importance and recency
            current_time = time.time()
            max_age = current_time - min(m.timestamp for m in all_memories)
            if max_age == 0:
                max_age = 1  # Avoid division by zero
            
            # Score = 0.7 * importance + 0.3 * recency
            all_memories.sort(key=lambda m: (
                0.7 * m.importance + 
                0.3 * (1 - (current_time - m.timestamp) / max_age)
            ), reverse=True)
        
        # Keep the top memories based on the policy
        memories_to_keep = all_memories[:max_memories]
        memories_to_remove = all_memories[max_memories:]
        
        # Remove the excess memories
        for memory in memories_to_remove:
            self.forget(memory.id)
        
        return len(memories_to_remove)
    
    def save(self, path: str) -> bool:
        """Save the memory store to disk.
        
        Args:
            path: Path to save to
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Save vector store
        vector_result = self.vector_store.save(f"{path}_vectors")
        
        # We would also save the index and mapping here
        # For now, we'll just return the vector store result
        return vector_result
    
    def load(self, path: str) -> bool:
        """Load the memory store from disk.
        
        Args:
            path: Path to load from
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Load vector store
        vector_result = self.vector_store.load(f"{path}_vectors")
        
        # We would also load the index and mapping here
        # For now, we'll just return the vector store result
        return vector_result
    
    def _get_memory_content(self, memory_item: MemoryItem) -> str:
        """Extract textual content from a memory item for vectorization.
        
        Args:
            memory_item: The memory item
            
        Returns:
            str: Textual content of the memory
        """
        if isinstance(memory_item.content, str):
            return memory_item.content
        elif isinstance(memory_item.content, dict):
            # For dictionaries (like event data), concatenate string values
            return " ".join(str(v) for v in memory_item.content.values() if v)
        else:
            # Fallback for other types
            return str(memory_item.content)
    
    def _get_memory_id_from_result(self, content: str) -> Optional[str]:
        """Extract memory ID from a vector search result.
        
        Args:
            content: Content from the search result
            
        Returns:
            Optional[str]: Memory ID, or None if not found
        """
        # In a real implementation, we would use the metadata
        # For now, we'll search through our mapping
        for memory_id, vector_id in self._memory_to_vector_id.items():
            memory = self.get_memory(memory_id)
            if memory and self._get_memory_content(memory) == content:
                return memory_id
        return None
