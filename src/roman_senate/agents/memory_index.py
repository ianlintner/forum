"""
Roman Senate AI Game
Memory Index Module

This module provides indexing capabilities for memory items to enable
efficient retrieval based on various criteria.
"""

from typing import Dict, List, Any, Set, Optional
import datetime
from collections import defaultdict

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
    """
    
    def __init__(self):
        """Initialize empty indices."""
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
        
        # Re-add all memories
        for memory in all_memories:
            self.add_memory(memory)
    
    def query(self, criteria: Dict[str, Any]) -> List[MemoryBase]:
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
                
        Returns:
            List of matching memory items
        """
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
            current_time = criteria.get("current_time", datetime.datetime.now())
            candidates = [m for m in candidates if m.get_current_strength(current_time) >= min_strength]
        
        # Sort by relevance if context is provided
        if "context" in criteria:
            context = criteria["context"]
            candidates.sort(
                key=lambda m: m.calculate_relevance(context),
                reverse=True
            )
        # Otherwise sort by recency
        else:
            candidates.sort(
                key=lambda m: m.timestamp,
                reverse=True
            )
        
        return candidates
    
    def get_memories_by_tag(self, tag: str) -> List[MemoryBase]:
        """Get all memories with a specific tag."""
        return self.tag_index.get(tag, [])
    
    def get_memories_by_senator(self, senator_name: str) -> List[MemoryBase]:
        """Get all memories related to a specific senator."""
        return self.senator_index.get(senator_name, [])
    
    def get_memories_by_event_type(self, event_type: str) -> List[MemoryBase]:
        """Get all memories of a specific event type."""
        return self.event_type_index.get(event_type, [])
    
    def get_memories_by_time_period(self, year: int, month: int) -> List[MemoryBase]:
        """Get all memories from a specific time period."""
        time_key = f"{year:04d}-{month:02d}"
        return self.time_index.get(time_key, [])
    
    def get_memories_by_importance(self, category: str) -> List[MemoryBase]:
        """Get all memories of a specific importance category."""
        return self.importance_index.get(category, [])
    
    def get_memories_by_topic(self, topic: str) -> List[MemoryBase]:
        """Get all memories related to a specific topic."""
        return self.topic_index.get(topic, [])
    
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
        current_time = datetime.datetime.now()
        sorted_memories = sorted(
            self.all_memories,
            key=lambda m: m.get_current_strength(current_time),
            reverse=True
        )
        return sorted_memories[:count]
    
    def prune_weak_memories(self, threshold: float = 0.1) -> int:
        """
        Remove memories that have decayed below the threshold.
        
        Args:
            threshold: Minimum strength to keep
            
        Returns:
            Number of memories removed
        """
        current_time = datetime.datetime.now()
        weak_memories = [
            m for m in self.all_memories
            if m.get_current_strength(current_time) < threshold
        ]
        
        for memory in weak_memories:
            self.remove_memory(memory)
        
        return len(weak_memories)