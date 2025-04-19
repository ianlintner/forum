"""
Roman Senate AI Game
Memory Index Module

This module provides indexing capabilities for memory items to enable
efficient retrieval based on various criteria.

Part of the Phase 3 Migration: Memory System - Adapting or extending agentic_game_framework.memory
"""

from typing import Dict, List, Any, Set, Optional, Union, Tuple
import datetime
from collections import defaultdict

from agentic_game_framework.memory.memory_index import MemoryIndex as FrameworkMemoryIndex
from .memory_base import MemoryBase


class MemoryIndex:
    """
    Indexes memory items for efficient retrieval.
    
    Maintains multiple indices for different query types:
    - By tag
    - By senator
    - By event type
    - By time period
    - By importance
    - By topic
    
    This class adapts the functionality of agentic_game_framework.memory.MemoryIndex
    while maintaining the specialized functionality needed for the Roman Senate simulation.
    """
    
    def __init__(self, use_framework_index: bool = True):
        """
        Initialize empty indices.
        
        Args:
            use_framework_index: Whether to use the framework's memory index as well
        """
        # Index by tag
        self.tag_index: Dict[str, List[MemoryBase]] = defaultdict(list)
        
        # Index by senator name
        self.senator_index: Dict[str, List[MemoryBase]] = defaultdict(list)
        
        # Index by event type
        self.event_type_index: Dict[str, List[MemoryBase]] = defaultdict(list)
        
        # Index by time period (year-month)
        self.time_index: Dict[str, List[MemoryBase]] = defaultdict(list)
        
        # Index by importance category
        self.importance_index: Dict[str, List[MemoryBase]] = {
            "core": [],
            "long_term": [],
            "medium_term": [],
            "short_term": []
        }
        
        # Index by topic
        self.topic_index: Dict[str, List[MemoryBase]] = defaultdict(list)
        
        # Track all memories for full scans when needed
        self.all_memories: List[MemoryBase] = []
        
        # Optional framework memory index for advanced searching
        self.use_framework_index = use_framework_index
        self.framework_index = FrameworkMemoryIndex() if use_framework_index else None
    
    def add_memory(self, memory: MemoryBase) -> None:
        """
        Add a memory item to all relevant indices.
        
        Args:
            memory: The memory item to index
        """
        # Add to all memories list
        self.all_memories.append(memory)
        
        # Index by tags
        for tag in memory.tags:
            self.tag_index[tag].append(memory)
        
        # Index by senator if applicable
        if hasattr(memory, "senator_name"):
            self.senator_index[getattr(memory, "senator_name")].append(memory)
        
        # Index by source if it's an event memory
        if hasattr(memory, "source"):
            self.senator_index[getattr(memory, "source")].append(memory)
        
        # Index by event type if applicable
        if hasattr(memory, "event_type"):
            self.event_type_index[getattr(memory, "event_type")].append(memory)
        
        # Index by time period (year-month)
        time_key = memory.timestamp.strftime("%Y-%m")
        self.time_index[time_key].append(memory)
        
        # Index by importance category
        category = memory.memory_category()
        self.importance_index[category].append(memory)
        
        # Index by topic if applicable
        if hasattr(memory, "topic"):
            self.topic_index[getattr(memory, "topic")].append(memory)
        
        # Add to framework index if using it
        if self.use_framework_index and self.framework_index:
            # Convert to framework memory item and index it
            framework_item = memory.to_framework_memory_item()
            self.framework_index.index_memory(framework_item)
    
    def remove_memory(self, memory: MemoryBase) -> None:
        """
        Remove a memory item from all indices.
        
        Args:
            memory: The memory item to remove
        """
        # Remove from all memories list
        if memory in self.all_memories:
            self.all_memories.remove(memory)
        
        # Remove from tag index
        for tag in memory.tags:
            if memory in self.tag_index[tag]:
                self.tag_index[tag].remove(memory)
        
        # Remove from senator index if applicable
        if hasattr(memory, "senator_name"):
            senator_name = getattr(memory, "senator_name")
            if memory in self.senator_index[senator_name]:
                self.senator_index[senator_name].remove(memory)
        
        # Remove from source index if it's an event memory
        if hasattr(memory, "source"):
            source = getattr(memory, "source")
            if memory in self.senator_index[source]:
                self.senator_index[source].remove(memory)
        
        # Remove from event type index if applicable
        if hasattr(memory, "event_type"):
            event_type = getattr(memory, "event_type")
            if memory in self.event_type_index[event_type]:
                self.event_type_index[event_type].remove(memory)
        
        # Remove from time index
        time_key = memory.timestamp.strftime("%Y-%m")
        if memory in self.time_index[time_key]:
            self.time_index[time_key].remove(memory)
        
        # Remove from importance index
        category = memory.memory_category()
        if memory in self.importance_index[category]:
            self.importance_index[category].remove(memory)
        
        # Remove from topic index if applicable
        if hasattr(memory, "topic"):
            topic = getattr(memory, "topic")
            if memory in self.topic_index[topic]:
                self.topic_index[topic].remove(memory)
        
        # Remove from framework index if using it
        if self.use_framework_index and self.framework_index:
            self.framework_index.remove_memory(memory.id)
    
    def update_indices(self) -> None:
        """
        Update all indices based on current memory states.
        
        This is useful after memory decay has changed categories.
        """
        # Store all memories
        all_memories = self.all_memories.copy()
        
        # Clear all indices
        self.tag_index.clear()
        self.senator_index.clear()
        self.event_type_index.clear()
        self.time_index.clear()
        self.importance_index = {
            "core": [],
            "long_term": [],
            "medium_term": [],
            "short_term": []
        }
        self.topic_index.clear()
        self.all_memories.clear()
        
        # Clear framework index if using it
        if self.use_framework_index and self.framework_index:
            self.framework_index.clear()
        
        # Re-add all memories
        for memory in all_memories:
            self.add_memory(memory)
    
    def query(self, criteria: Dict[str, Any], current_time: Optional[datetime.datetime] = None) -> List[MemoryBase]:
        """
        Query memories based on multiple criteria.
        
        Args:
            criteria: Dictionary of query criteria, which can include:
                - tags: List of tags (all must match)
                - senator_name: Senator name
                - event_type: Event type
                - time_start: Start timestamp
                - time_end: End timestamp
                - importance_category: One of "core", "long_term", "medium_term", "short_term"
                - topic: Topic
                - min_strength: Minimum memory strength
                - text: Text to search for in content (uses framework index if available)
            current_time: Optional current time for strength calculations
                
        Returns:
            List of matching memory items
        """
        # Check if we can use the framework index for this query
        if (self.use_framework_index and self.framework_index and 
            criteria.get("text") and not any(k in criteria for k in ("tags", "senator_name", "event_type", "importance_category", "topic"))):
            # Simple text query, delegate to framework index
            return self._framework_text_query(criteria)
        
        # Default to our specialized indexing
        candidate_sets: List[Set[MemoryBase]] = []
        
        # Filter by tags if specified
        if "tags" in criteria and criteria["tags"]:
            tag_matches: Set[MemoryBase] = set()
            for tag in criteria["tags"]:
                if tag in self.tag_index:
                    # For the first tag, initialize the set
                    if not tag_matches:
                        tag_matches = set(self.tag_index[tag])
                    # For subsequent tags, take the intersection
                    else:
                        tag_matches &= set(self.tag_index[tag])
            candidate_sets.append(tag_matches)
        
        # Filter by senator name if specified
        if "senator_name" in criteria and criteria["senator_name"]:
            senator_name = criteria["senator_name"]
            if senator_name in self.senator_index:
                candidate_sets.append(set(self.senator_index[senator_name]))
        
        # Filter by event type if specified
        if "event_type" in criteria and criteria["event_type"]:
            event_type = criteria["event_type"]
            if event_type in self.event_type_index:
                candidate_sets.append(set(self.event_type_index[event_type]))
        
        # Filter by importance category if specified
        if "importance_category" in criteria and criteria["importance_category"]:
            category = criteria["importance_category"]
            if category in self.importance_index:
                candidate_sets.append(set(self.importance_index[category]))
        
        # Filter by topic if specified
        if "topic" in criteria and criteria["topic"]:
            topic = criteria["topic"]
            if topic in self.topic_index:
                candidate_sets.append(set(self.topic_index[topic]))
        
        # If we have candidate sets, find the intersection
        if candidate_sets:
            # Start with the first set
            result_set = candidate_sets[0]
            # Take intersection with each subsequent set
            for s in candidate_sets[1:]:
                result_set &= s
            candidates = list(result_set)
        else:
            # If no specific criteria matched, use all memories
            candidates = self.all_memories.copy()
        
        # Apply time range filter if specified
        if "time_start" in criteria or "time_end" in criteria:
            time_start = criteria.get("time_start")
            time_end = criteria.get("time_end", datetime.datetime.now())
            
            if time_start:
                candidates = [m for m in candidates if m.timestamp >= time_start]
            if time_end:
                candidates = [m for m in candidates if m.timestamp <= time_end]
        
        # Apply minimum strength filter if specified
        if "min_strength" in criteria:
            min_strength = criteria["min_strength"]
            current_time = current_time or datetime.datetime.now()
            candidates = [m for m in candidates if m.get_current_strength(current_time) >= min_strength]
        
        # Sort by relevance if context is provided
        if "context" in criteria:
            context = criteria["context"]
            candidates.sort(key=lambda m: m.calculate_relevance(context), reverse=True)
        # Otherwise sort by recency (newest first)
        else:
            candidates.sort(key=lambda m: m.timestamp, reverse=True)
        
        # Apply limit if specified
        if "limit" in criteria and criteria["limit"] is not None:
            limit = criteria["limit"]
            candidates = candidates[:limit]
        
        return candidates
    
    def _framework_text_query(self, criteria: Dict[str, Any]) -> List[MemoryBase]:
        """
        Perform a text query using the framework index.
        
        Args:
            criteria: Dictionary containing text query criteria
            
        Returns:
            List of matching memory items
        """
        if not self.framework_index:
            return []
        
        # Create a query for the framework index
        framework_query = {}
        
        # Add text search
        if "text" in criteria:
            framework_query["text"] = criteria["text"]
        
        # Add timestamp range if present
        if "time_start" in criteria:
            if isinstance(criteria["time_start"], datetime.datetime):
                framework_query["timestamp_min"] = criteria["time_start"].timestamp()
            else:
                framework_query["timestamp_min"] = criteria["time_start"]
                
        if "time_end" in criteria:
            if isinstance(criteria["time_end"], datetime.datetime):
                framework_query["timestamp_max"] = criteria["time_end"].timestamp()
            else:
                framework_query["timestamp_max"] = criteria["time_end"]
        
        # Add importance threshold if present
        if "min_strength" in criteria:
            framework_query["importance_min"] = criteria["min_strength"]
        
        # Get limit if present
        limit = criteria.get("limit")
        
        # Execute query in framework index
        framework_results = self.framework_index.search(
            framework_query,
            limit=limit,
            importance_threshold=criteria.get("min_strength")
        )
        
        # Convert results back to our memory items
        result_memories = []
        for framework_memory in framework_results:
            # Find the corresponding memory in our all_memories list
            for memory in self.all_memories:
                if memory.id == framework_memory.id:
                    result_memories.append(memory)
                    break
        
        return result_memories
    
    def get_memories_by_time_period(self, year: int, month: int) -> List[MemoryBase]:
        """
        Get memories from a specific time period.
        
        Args:
            year: The year
            month: The month (1-12)
            
        Returns:
            List of memories from that time period
        """
        time_key = f"{year:04d}-{month:02d}"
        return self.time_index.get(time_key, [])
    
    def get_recent_memories(self, count: int = 10) -> List[MemoryBase]:
        """Get the most recent memories."""
        sorted_memories = sorted(
            self.all_memories,
            key=lambda m: m.timestamp,
            reverse=True
        )
        return sorted_memories[:count]
    
    def get_strongest_memories(self, count: int = 10) -> List[MemoryBase]:
        """Get the strongest memories based on current strength."""
        sorted_memories = sorted(
            self.all_memories,
            key=lambda m: m.get_current_strength(),
            reverse=True
        )
        return sorted_memories[:count]
    
    def prune_weak_memories(self, threshold: float = 0.1) -> int:
        """
        Remove memories with strength below the threshold.
        
        Args:
            threshold: Minimum strength to keep
            
        Returns:
            Number of memories removed
        """
        current_time = datetime.datetime.now()
        
        # Find weak memories
        weak_memories = [
            memory for memory in self.all_memories
            if memory.get_current_strength(current_time) < threshold
            and not memory.is_core_memory()
        ]
        
        # Remove weak memories
        for memory in weak_memories:
            self.remove_memory(memory)
        
        return len(weak_memories)
    
    def get_memory(self, memory_id: str) -> Optional[MemoryBase]:
        """
        Get a memory by ID.
        
        Args:
            memory_id: ID of the memory to retrieve
            
        Returns:
            The memory item, or None if not found
        """
        for memory in self.all_memories:
            if memory.id == memory_id:
                return memory
        return None
    
    def update_memory(self, memory: MemoryBase) -> bool:
        """
        Update a memory's indices.
        
        Args:
            memory: The updated memory
            
        Returns:
            True if updated successfully, False if memory not found
        """
        # Remove old entry and add updated one
        old_memory = self.get_memory(memory.id)
        if old_memory:
            self.remove_memory(old_memory)
            self.add_memory(memory)
            return True
        return False
    
    def clear(self) -> None:
        """Clear all memories and indices."""
        self.tag_index.clear()
        self.senator_index.clear()
        self.event_type_index.clear()
        self.time_index.clear()
        self.importance_index = {
            "core": [],
            "long_term": [],
            "medium_term": [],
            "short_term": []
        }
        self.topic_index.clear()
        self.all_memories.clear()
        
        if self.use_framework_index and self.framework_index:
            self.framework_index.clear()