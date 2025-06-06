"""
Memory Index for Agentic Game Framework.

This module provides an efficient indexing and retrieval system for agent memories,
allowing for fast querying based on various criteria.
"""

import logging
import time
from collections import defaultdict
from functools import lru_cache
from typing import Any, Dict, List, Optional, Set, Tuple, FrozenSet, Hashable

from .memory_interface import MemoryItem

# Set up module logger
logger = logging.getLogger(__name__)

class MemoryIndex:
    """
    Efficient memory retrieval system.
    
    The MemoryIndex maintains multiple indices for different memory attributes,
    allowing for fast retrieval based on various criteria. It supports:
    1. Indexing by timestamp
    2. Indexing by importance
    3. Indexing by associations
    4. Full-text search (basic implementation)
    
    This enables efficient memory retrieval without scanning all memories.
    """
    
    def __init__(self, enable_caching: bool = True, cache_size: int = 128):
        """
        Initialize a new memory index with empty indices.
        
        Args:
            enable_caching: Whether to enable LRU caching for search operations
            cache_size: Maximum size of LRU caches
        """
        # Primary storage: memory_id -> memory_item
        self._memories: Dict[str, MemoryItem] = {}
        
        # Timestamp index: sorted list of (timestamp, memory_id) tuples
        self._timestamp_index: List[Tuple[float, str]] = []
        
        # Importance index: importance_level -> set of memory_ids
        # We bucket importance into 10 levels (0.0-0.1, 0.1-0.2, etc.)
        self._importance_index: Dict[int, Set[str]] = defaultdict(set)
        
        # Association index: (key, value) -> set of memory_ids
        self._association_index: Dict[Tuple[str, Hashable], Set[str]] = defaultdict(set)
        
        # Text index: word -> set of memory_ids
        self._text_index: Dict[str, Set[str]] = defaultdict(set)
        
        # Performance metrics
        self._metrics = {
            "index_operations": 0,
            "search_operations": 0,
            "cache_hits": 0,
            "total_memories": 0,
            "last_search_time": 0.0
        }
        
        # Caching parameters
        self._enable_caching = enable_caching
        self._cache_size = cache_size
        
        # Query cache for faster repeated searches
        self._query_cache: Dict[str, Tuple[float, List[MemoryItem]]] = {}
        self._cache_ttl = 5.0  # seconds
            
        logger.info(f"Initialized MemoryIndex with caching={'enabled' if enable_caching else 'disabled'}")
    
    def index_memory(self, memory_item: MemoryItem) -> None:
        """
        Index a memory item for efficient retrieval.
        
        Args:
            memory_item: The memory item to index
        """
        start_time = time.time()
        memory_id = memory_item.id
        
        # Store in primary storage
        self._memories[memory_id] = memory_item
        
        # Index by timestamp
        timestamp_entry = (memory_item.timestamp, memory_id)
        self._insert_sorted(self._timestamp_index, timestamp_entry)
        
        # Index by importance
        importance_bucket = int(memory_item.importance * 10)
        self._importance_index[importance_bucket].add(memory_id)
        
        # Index by associations
        for key, value in memory_item.associations.items():
            if isinstance(value, (str, int, float, bool)):
                self._association_index[(key, value)].add(memory_id)
        
        # Index by text content
        if isinstance(memory_item.content, str):
            self._index_text(memory_id, memory_item.content)
        elif isinstance(memory_item.content, dict):
            # For dictionaries (like event data), index string values
            for key, value in memory_item.content.items():
                if isinstance(value, str):
                    # Index with key context for better search results
                    self._index_text(memory_id, f"{key}: {value}")
        
        # Update metrics
        self._metrics["index_operations"] += 1
        self._metrics["total_memories"] = len(self._memories)
        
        # Clear query cache since indices have changed
        if self._enable_caching:
            self._query_cache.clear()
            logger.debug(f"Cache cleared due to indexing of memory {memory_id}")
            
        indexing_time = time.time() - start_time
        if indexing_time > 0.01:  # Log slow indexing operations
            logger.debug(f"Slow memory indexing: {memory_id} took {indexing_time:.4f}s")
    
    def _index_text(self, memory_id: str, text: str) -> None:
        """
        Index the text content of a memory.
        
        Args:
            memory_id: ID of the memory
            text: Text content to index
        """
        # Simple tokenization (split by whitespace and remove punctuation)
        words = text.lower().split()
        words = [word.strip('.,;:!?()[]{}"\'-') for word in words]
        
        # Add to text index
        for word in words:
            if word and len(word) > 2:  # Skip short words
                self._text_index[word].add(memory_id)
    
    def _insert_sorted(
        self, 
        index: List[Tuple[float, str]], 
        entry: Tuple[float, str]
    ) -> None:
        """
        Insert an entry into a sorted index.
        
        Args:
            index: The sorted index to insert into
            entry: The entry to insert
        """
        # Binary search to find insertion point
        low, high = 0, len(index)
        while low < high:
            mid = (low + high) // 2
            if index[mid][0] < entry[0]:
                low = mid + 1
            else:
                high = mid
                
        index.insert(low, entry)
    
    def remove_memory(self, memory_id: str) -> bool:
        """
        Remove a memory from all indices.
        
        Args:
            memory_id: ID of the memory to remove
            
        Returns:
            bool: True if the memory was removed, False if not found
        """
        if memory_id not in self._memories:
            return False
            
        memory_item = self._memories.pop(memory_id)
        
        # Remove from timestamp index
        for i, (_, mid) in enumerate(self._timestamp_index):
            if mid == memory_id:
                self._timestamp_index.pop(i)
                break
        
        # Remove from importance index
        importance_bucket = int(memory_item.importance * 10)
        if memory_id in self._importance_index[importance_bucket]:
            self._importance_index[importance_bucket].remove(memory_id)
            
        # Remove from association index
        for key, value in memory_item.associations.items():
            if isinstance(value, (str, int, float, bool)):
                index_key = (key, value)
                if index_key in self._association_index and memory_id in self._association_index[index_key]:
                    self._association_index[index_key].remove(memory_id)
                    
        # Remove from text index
        for word, memory_ids in list(self._text_index.items()):
            if memory_id in memory_ids:
                memory_ids.remove(memory_id)
                if not memory_ids:
                    del self._text_index[word]
                    
        return True
    
    def update_memory(self, memory_item: MemoryItem) -> bool:
        """
        Update a memory in all indices.
        
        This removes the old indices and adds new ones.
        
        Args:
            memory_item: The updated memory item
            
        Returns:
            bool: True if the memory was updated, False if not found
        """
        memory_id = memory_item.id
        if memory_id not in self._memories:
            return False
            
        # Remove old indices
        self.remove_memory(memory_id)
        
        # Add new indices
        self.index_memory(memory_item)
        
        return True
    
    def search(
        self,
        query: Dict[str, Any],
        limit: Optional[int] = None,
        importance_threshold: Optional[float] = None
    ) -> List[MemoryItem]:
        """
        Search for memories that match the query.
        
        Args:
            query: Dictionary of search criteria
            limit: Maximum number of memories to return
            importance_threshold: Minimum importance score
            
        Returns:
            List[MemoryItem]: List of matching memory items
        """
        start_time = time.time()
        self._metrics["search_operations"] += 1
        
        # Create a cache key from the query parameters
        if self._enable_caching:
            # Convert query to a hashable representation
            try:
                cache_parts = []
                for k, v in sorted(query.items()):
                    if isinstance(v, (str, int, float, bool)):
                        cache_parts.append(f"{k}:{v}")
                    elif isinstance(v, dict):
                        cache_parts.append(f"{k}:{hash(frozenset(v.items()))}")
                
                cache_key = f"query({'|'.join(cache_parts)})|limit:{limit}|importance:{importance_threshold}"
                
                # Check cache
                if cache_key in self._query_cache:
                    cache_time, cached_results = self._query_cache[cache_key]
                    if time.time() - cache_time < self._cache_ttl:
                        self._metrics["cache_hits"] += 1
                        self._metrics["last_search_time"] = time.time() - start_time
                        logger.debug(f"Cache hit for query: {cache_key[:50]}...")
                        return cached_results
            except (TypeError, ValueError):
                # If cache key creation fails, proceed without caching
                logger.debug("Failed to create cache key, proceeding without caching")
        
        # Start with all memory IDs
        result_ids: Optional[Set[str]] = None
        
        # Filter by timestamp range
        if "timestamp_min" in query or "timestamp_max" in query:
            timestamp_min = query.get("timestamp_min", 0)
            timestamp_max = query.get("timestamp_max", float("inf"))
            
            timestamp_ids = self._search_timestamp_range(timestamp_min, timestamp_max)
            result_ids = timestamp_ids if result_ids is None else result_ids.intersection(timestamp_ids)
            
            if result_ids is not None and len(result_ids) == 0:
                return []
        
        # Filter by importance
        if "importance_min" in query:
            importance_min = query["importance_min"]
            importance_ids = self._search_importance(importance_min)
            result_ids = importance_ids if result_ids is None else result_ids.intersection(importance_ids)
            
            if result_ids is not None and len(result_ids) == 0:
                return []
        
        # Filter by associations
        if "associations" in query:
            associations = query["associations"]
            association_ids = self._search_associations(associations)
            result_ids = association_ids if result_ids is None else result_ids.intersection(association_ids)
            
            if result_ids is not None and len(result_ids) == 0:
                return []
        
        # Filter by text search
        if "text" in query:
            text = query["text"]
            text_ids = self._search_text(text)
            result_ids = text_ids if result_ids is None else result_ids.intersection(text_ids)
            
            if result_ids is not None and len(result_ids) == 0:
                return []
        
        # If no filters applied, use all memories
        if result_ids is None:
            result_ids = set(self._memories.keys())
        
        # Apply importance threshold if specified
        if importance_threshold is not None:
            result_ids = {
                memory_id for memory_id in result_ids
                if self._memories[memory_id].importance >= importance_threshold
            }
        
        # Convert IDs to memory items
        results = [self._memories[memory_id] for memory_id in result_ids]
        
        # Sort by recency (newest first)
        results.sort(key=lambda memory: memory.timestamp, reverse=True)
        
        # Apply limit if specified
        if limit is not None:
            results = results[:limit]
        
        # Store in cache if caching is enabled
        if self._enable_caching:
            try:
                # Check if we created a cache key earlier
                if 'cache_key' in locals():
                    # Store limited results in cache
                    self._query_cache[cache_key] = (time.time(), results)
                    
                    # Limit cache size
                    if len(self._query_cache) > self._cache_size:
                        # Remove oldest entries
                        oldest_keys = sorted(self._query_cache.keys(),
                                          key=lambda k: self._query_cache[k][0])[:len(self._query_cache) - self._cache_size]
                        for key in oldest_keys:
                            del self._query_cache[key]
            except (NameError, TypeError):
                # Cache key wasn't created earlier, skip caching
                pass
        
        # Record metrics
        self._metrics["last_search_time"] = time.time() - start_time
        if time.time() - start_time > 0.1:  # Log slow search operations
            logger.warning(f"Slow search operation: {time.time() - start_time:.4f}s for {len(results)} results")
            
        return results
    
    def _search_timestamp_range(self, min_time: float, max_time: float) -> Set[str]:
        """
        Find memories within a timestamp range.
        
        Args:
            min_time: Minimum timestamp
            max_time: Maximum timestamp
            
        Returns:
            Set[str]: Set of matching memory IDs
        """
        result_ids = set()
        
        # Binary search for start index
        start_idx = 0
        end_idx = len(self._timestamp_index)
        while start_idx < end_idx:
            mid = (start_idx + end_idx) // 2
            if self._timestamp_index[mid][0] < min_time:
                start_idx = mid + 1
            else:
                end_idx = mid
        
        # Collect all memories in range
        for i in range(start_idx, len(self._timestamp_index)):
            timestamp, memory_id = self._timestamp_index[i]
            if timestamp > max_time:
                break
            result_ids.add(memory_id)
            
        return result_ids
    
    def _search_importance(self, min_importance: float) -> Set[str]:
        """
        Find memories with importance above a threshold.
        
        Args:
            min_importance: Minimum importance score
            
        Returns:
            Set[str]: Set of matching memory IDs
        """
        result_ids = set()
        min_bucket = int(min_importance * 10)
        
        # Collect all memories in buckets >= min_bucket
        for bucket in range(min_bucket, 11):
            result_ids.update(self._importance_index[bucket])
            
        return result_ids
    
    def _search_associations(self, associations: Dict[str, Any]) -> Set[str]:
        """
        Find memories with matching associations.
        
        Args:
            associations: Dictionary of association key-value pairs to match
            
        Returns:
            Set[str]: Set of matching memory IDs
        """
        result_ids: Optional[Set[str]] = None
        
        for key, value in associations.items():
            index_key = (key, value)
            if index_key in self._association_index:
                matching_ids = self._association_index[index_key]
                result_ids = matching_ids if result_ids is None else result_ids.intersection(matching_ids)
                
                if result_ids is not None and len(result_ids) == 0:
                    break
        
        return result_ids or set()
    
    def _search_text(self, text: str) -> Set[str]:
        """
        Find memories with matching text content.
        
        Args:
            text: Text to search for
            
        Returns:
            Set[str]: Set of matching memory IDs
        """
        # Simple tokenization
        words = text.lower().split()
        words = [word.strip('.,;:!?()[]{}"\'-') for word in words]
        words = [word for word in words if word and len(word) > 2]
        
        if not words:
            return set()
        
        # Find memories containing all words
        result_ids: Optional[Set[str]] = None
        
        for word in words:
            if word in self._text_index:
                matching_ids = self._text_index[word]
                result_ids = matching_ids if result_ids is None else result_ids.intersection(matching_ids)
                
                if result_ids is not None and len(result_ids) == 0:
                    break
        
        return result_ids or set()
    
    def get_memory(self, memory_id: str) -> Optional[MemoryItem]:
        """
        Get a memory by ID.
        
        Args:
            memory_id: ID of the memory to retrieve
            
        Returns:
            Optional[MemoryItem]: The memory item, or None if not found
        """
        return self._memories.get(memory_id)
    
    def get_all_memories(self) -> List[MemoryItem]:
        """
        Get all memories in the index.
        
        Returns:
            List[MemoryItem]: List of all memory items
        """
        return list(self._memories.values())
    
    def clear(self) -> None:
        """
        Clear all memories from the index.
        """
        self._memories.clear()
        self._timestamp_index.clear()
        self._importance_index.clear()
        self._association_index.clear()
        self._text_index.clear()