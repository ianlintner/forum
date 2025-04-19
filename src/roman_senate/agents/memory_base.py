"""
Roman Senate AI Game
Memory Base Module

This module defines the base memory structure for all memory types in the system.
It provides functionality for memory strength calculation, decay, and serialization.
"""

import datetime
from typing import Dict, Any, Optional, List
import math
import json


class MemoryBase:
    """
    Base class for all memory items in the system.
    
    Provides common functionality for memory strength calculation,
    decay over time, and serialization/deserialization.
    """
    
    def __init__(
        self,
        timestamp: Optional[datetime.datetime] = None,
        importance: float = 0.5,
        decay_rate: float = 0.1,
        tags: Optional[List[str]] = None,
        emotional_impact: float = 0.0
    ):
        """
        Initialize a base memory item.
        
        Args:
            timestamp: When the memory was created (defaults to now)
            importance: How important the memory is (0.0 to 1.0)
            decay_rate: How quickly the memory fades (0.0 to 1.0)
            tags: List of tags for categorizing the memory
            emotional_impact: Emotional significance (-1.0 to 1.0)
        """
        self.timestamp = timestamp or datetime.datetime.now()
        self.importance = max(0.0, min(1.0, importance))  # Clamp between 0 and 1
        self.decay_rate = max(0.0, min(1.0, decay_rate))  # Clamp between 0 and 1
        self.tags = tags or []
        self.emotional_impact = max(-1.0, min(1.0, emotional_impact))  # Clamp between -1 and 1
        
    def get_current_strength(self, current_time: Optional[datetime.datetime] = None) -> float:
        """
        Calculate the current strength of this memory based on time elapsed and importance.
        
        Args:
            current_time: The current time (defaults to now)
            
        Returns:
            A value between 0.0 and 1.0 representing memory strength
        """
        current_time = current_time or datetime.datetime.now()
        
        # Calculate time elapsed in days
        time_delta = current_time - self.timestamp
        days_elapsed = time_delta.total_seconds() / (24 * 60 * 60)
        
        # Apply decay formula: strength = importance * e^(-decay_rate * days)
        # This creates an exponential decay curve
        strength = self.importance * math.exp(-self.decay_rate * days_elapsed)
        
        # Apply emotional impact as a modifier (strong emotions strengthen memories)
        emotional_modifier = 1.0 + (abs(self.emotional_impact) * 0.5)
        strength *= emotional_modifier
        
        # Ensure the result is between 0 and 1
        return max(0.0, min(1.0, strength))
    
    def is_core_memory(self) -> bool:
        """
        Check if this is a core memory that should never decay.
        
        Returns:
            True if this is a core memory, False otherwise
        """
        return self.decay_rate == 0.0 and self.importance >= 0.9
    
    def memory_category(self) -> str:
        """
        Get the category of this memory based on importance and decay.
        
        Returns:
            One of: "core", "long_term", "medium_term", "short_term"
        """
        if self.is_core_memory():
            return "core"
        elif self.importance >= 0.7:
            return "long_term"
        elif self.importance >= 0.4:
            return "medium_term"
        else:
            return "short_term"
    
    def calculate_relevance(self, context: Dict[str, Any]) -> float:
        """
        Calculate how relevant this memory is to a given context.
        
        Args:
            context: Dictionary of context information
            
        Returns:
            A value between 0.0 and 1.0 representing relevance
        """
        relevance = 0.0
        
        # Check for tag matches
        context_tags = context.get("tags", [])
        matching_tags = set(self.tags).intersection(set(context_tags))
        if matching_tags:
            relevance += 0.3 * (len(matching_tags) / max(len(self.tags), len(context_tags)))
        
        # Check for topic matches
        if "topic" in context and hasattr(self, "topic"):
            if context["topic"] == getattr(self, "topic"):
                relevance += 0.3
        
        # Check for senator matches
        if "senator_name" in context and hasattr(self, "senator_name"):
            if context["senator_name"] == getattr(self, "senator_name"):
                relevance += 0.4
        
        # Add strength as a factor
        current_strength = self.get_current_strength()
        relevance = (relevance * 0.7) + (current_strength * 0.3)
        
        return max(0.0, min(1.0, relevance))
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the memory to a dictionary for serialization.
        
        Returns:
            Dictionary representation of the memory
        """
        return {
            "timestamp": self.timestamp.isoformat(),
            "importance": self.importance,
            "decay_rate": self.decay_rate,
            "tags": self.tags,
            "emotional_impact": self.emotional_impact,
            "memory_type": self.__class__.__name__
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryBase':
        """
        Create a memory from a dictionary representation.
        
        Args:
            data: Dictionary containing memory data
            
        Returns:
            A new MemoryBase instance
        """
        # Parse timestamp from ISO format
        timestamp = datetime.datetime.fromisoformat(data["timestamp"])
        
        return cls(
            timestamp=timestamp,
            importance=data.get("importance", 0.5),
            decay_rate=data.get("decay_rate", 0.1),
            tags=data.get("tags", []),
            emotional_impact=data.get("emotional_impact", 0.0)
        )