"""
Roman Senate AI Game
Memory Items Module

This module defines specialized memory item classes that inherit from MemoryBase.
These classes represent different types of memories that senators can have.

Part of the Phase 3 Migration: Memory System - Adapting or extending agentic_game_framework.memory
"""

from typing import Dict, Any, Optional, List, Union
import datetime
import uuid

from agentic_game_framework.memory.memory_interface import EventMemoryItem as FrameworkEventMemoryItem
from ..core.events import Event
from .memory_base import MemoryBase


class EventMemoryItem(MemoryBase):
    """
    Memory of an observed event.
    
    Stores details about an event that a senator witnessed or participated in.
    
    This extends MemoryBase and is compatible with the framework's EventMemoryItem.
    """
    
    def __init__(
        self,
        event_id: str,
        event_type: str,
        source: str,
        metadata: Dict[str, Any],
        timestamp: Optional[datetime.datetime] = None,
        importance: float = 0.5,
        decay_rate: float = 0.1,
        tags: Optional[List[str]] = None,
        emotional_impact: float = 0.0,
        memory_id: Optional[str] = None,
        associations: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize an event memory item.
        
        Args:
            event_id: Unique identifier for the event
            event_type: Type of event
            source: Source of the event (usually a senator name)
            metadata: Additional event data
            timestamp: When the event occurred
            importance: How important the event is
            decay_rate: How quickly the memory fades
            tags: List of tags for categorizing the memory
            emotional_impact: Emotional significance
            memory_id: Optional unique identifier for the memory
            associations: Optional related concepts or metadata
        """
        # Add event type to tags if not already present
        tags = tags or []
        if event_type not in tags:
            tags.append(event_type)
        
        # Add source to tags if not already present and it's a string
        if source and isinstance(source, str) and source not in tags:
            tags.append(source)
        
        # Generate memory ID if not provided
        if not memory_id:
            memory_id = f"event_{event_id}_{uuid.uuid4().hex[:8]}"
            
        # Initialize base memory
        super().__init__(timestamp, importance, decay_rate, tags, emotional_impact, memory_id, associations)
        
        self.event_id = event_id
        self.event_type = event_type
        self.source = source
        self.metadata = metadata
        
        # Add event-specific associations
        self.add_association("event_type", event_type)
        self.add_association("source", source)
        self.add_association("event_id", event_id)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        data = super().to_dict()
        data.update({
            "event_id": self.event_id,
            "event_type": self.event_type,
            "source": self.source,
            "metadata": self.metadata
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EventMemoryItem':
        """Create from dictionary representation."""
        # Parse timestamp from ISO format
        timestamp = datetime.datetime.fromisoformat(data["timestamp"])
        
        return cls(
            event_id=data["event_id"],
            event_type=data["event_type"],
            source=data["source"],
            metadata=data["metadata"],
            timestamp=timestamp,
            importance=data.get("importance", 0.5),
            decay_rate=data.get("decay_rate", 0.1),
            tags=data.get("tags", []),
            emotional_impact=data.get("emotional_impact", 0.0),
            memory_id=data.get("id"),
            associations=data.get("associations", {})
        )
    
    @classmethod
    def from_event(cls, event: Event, importance: float = 0.5, decay_rate: float = 0.1, emotional_impact: float = 0.0) -> 'EventMemoryItem':
        """
        Create an event memory item from an Event object.
        
        Args:
            event: The event to create a memory from
            importance: How important the event is
            decay_rate: How quickly the memory fades
            emotional_impact: Emotional significance
            
        Returns:
            EventMemoryItem: A new event memory item
        """
        # Extract source name properly from different source types
        source_repr = "Unknown"
        if event.source:
            if isinstance(event.source, dict) and "name" in event.source:
                source_repr = event.source["name"]
            else:
                source_repr = getattr(event.source, "name", str(event.source))
        
        # Parse the timestamp
        if isinstance(event.timestamp, str):
            timestamp = datetime.datetime.fromisoformat(event.timestamp)
        elif isinstance(event.timestamp, datetime.datetime):
            timestamp = event.timestamp
        else:
            timestamp = datetime.datetime.now()
        
        # Create the event memory
        return cls(
            event_id=event.event_id,
            event_type=event.event_type,
            source=source_repr,
            metadata=event.metadata.copy(),
            timestamp=timestamp,
            importance=importance,
            decay_rate=decay_rate,
            emotional_impact=emotional_impact
        )
    
    def to_framework_event_memory_item(self) -> FrameworkEventMemoryItem:
        """
        Convert to a framework EventMemoryItem for compatibility.
        
        Returns:
            FrameworkEventMemoryItem: Compatible event memory item for the framework
        """
        # Create a simulated event dict in the format expected by the framework
        event_dict = {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "source": self.source,
            "target": self.metadata.get("target"),
            "timestamp": self.timestamp.timestamp(),
            "metadata": self.metadata
        }
        
        # Create and return a framework event memory item
        return FrameworkEventMemoryItem(
            memory_id=self.id,
            timestamp=self.timestamp.timestamp(),
            event=event_dict,
            importance=self.importance,
            associations=self.associations
        )
    
    @classmethod
    def from_framework_event_memory_item(cls, framework_item: FrameworkEventMemoryItem) -> 'EventMemoryItem':
        """
        Create from a framework EventMemoryItem for compatibility.
        
        Args:
            framework_item: Framework event memory item
            
        Returns:
            EventMemoryItem: Converted event memory item
        """
        # Extract the event data
        event_data = framework_item.content
        
        # Convert timestamp from float to datetime if needed
        if isinstance(event_data.get("timestamp"), float):
            timestamp = datetime.datetime.fromtimestamp(event_data["timestamp"])
        elif isinstance(event_data.get("timestamp"), str):
            timestamp = datetime.datetime.fromisoformat(event_data["timestamp"])
        else:
            timestamp = datetime.datetime.fromtimestamp(framework_item.timestamp)
        
        return cls(
            event_id=event_data.get("event_id", str(uuid.uuid4())),
            event_type=event_data.get("event_type", "unknown"),
            source=event_data.get("source", "unknown"),
            metadata=event_data.get("metadata", {}),
            timestamp=timestamp,
            importance=framework_item.importance,
            associations=framework_item.associations,
            memory_id=framework_item.id
        )


class ReactionMemoryItem(MemoryBase):
    """
    Memory of a reaction to an event.
    
    Stores details about how a senator reacted to an event.
    """
    
    def __init__(
        self,
        event_id: str,
        reaction_type: str,
        content: str,
        timestamp: Optional[datetime.datetime] = None,
        importance: float = 0.5,
        decay_rate: float = 0.1,
        tags: Optional[List[str]] = None,
        emotional_impact: float = 0.0,
        memory_id: Optional[str] = None,
        associations: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a reaction memory item.
        
        Args:
            event_id: ID of the event being reacted to
            reaction_type: Type of reaction
            content: Content of the reaction
            timestamp: When the reaction occurred
            importance: How important the reaction is
            decay_rate: How quickly the memory fades
            tags: List of tags for categorizing the memory
            emotional_impact: Emotional significance
            memory_id: Optional unique identifier for the memory
            associations: Optional related concepts or metadata
        """
        # Add reaction type to tags if not already present
        tags = tags or []
        if "reaction" not in tags:
            tags.append("reaction")
        if reaction_type not in tags:
            tags.append(reaction_type)
        
        # Generate memory ID if not provided
        if not memory_id:
            memory_id = f"reaction_{event_id}_{uuid.uuid4().hex[:8]}"
            
        super().__init__(timestamp, importance, decay_rate, tags, emotional_impact, memory_id, associations)
        self.event_id = event_id
        self.reaction_type = reaction_type
        self.content = content
        
        # Add reaction-specific associations
        self.add_association("reaction_type", reaction_type)
        self.add_association("event_id", event_id)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        data = super().to_dict()
        data.update({
            "event_id": self.event_id,
            "reaction_type": self.reaction_type,
            "content": self.content
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ReactionMemoryItem':
        """Create from dictionary representation."""
        # Parse timestamp from ISO format
        timestamp = datetime.datetime.fromisoformat(data["timestamp"])
        
        return cls(
            event_id=data["event_id"],
            reaction_type=data["reaction_type"],
            content=data["content"],
            timestamp=timestamp,
            importance=data.get("importance", 0.5),
            decay_rate=data.get("decay_rate", 0.1),
            tags=data.get("tags", []),
            emotional_impact=data.get("emotional_impact", 0.0),
            memory_id=data.get("id"),
            associations=data.get("associations", {})
        )


class StanceChangeMemoryItem(MemoryBase):
    """
    Memory of a change in stance on a topic.
    
    Stores details about how and why a senator changed their stance.
    """
    
    def __init__(
        self,
        topic: str,
        old_stance: str,
        new_stance: str,
        reason: str,
        event_id: Optional[str] = None,
        timestamp: Optional[datetime.datetime] = None,
        importance: float = 0.7,  # Stance changes are typically important
        decay_rate: float = 0.05,  # And decay slowly
        tags: Optional[List[str]] = None,
        emotional_impact: float = 0.0,
        memory_id: Optional[str] = None,
        associations: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a stance change memory item.
        
        Args:
            topic: The topic the stance is about
            old_stance: Previous stance
            new_stance: New stance
            reason: Reason for the change
            event_id: Optional ID of the event that triggered the change
            timestamp: When the stance change occurred
            importance: How important the stance change is
            decay_rate: How quickly the memory fades
            tags: List of tags for categorizing the memory
            emotional_impact: Emotional significance
            memory_id: Optional unique identifier for the memory
            associations: Optional related concepts or metadata
        """
        # Add topic to tags if not already present
        tags = tags or []
        if topic not in tags:
            tags.append(topic)
        if "stance_change" not in tags:
            tags.append("stance_change")
            
        # Generate memory ID if not provided
        if not memory_id:
            memory_id = f"stance_{topic}_{uuid.uuid4().hex[:8]}"
            
        super().__init__(timestamp, importance, decay_rate, tags, emotional_impact, memory_id, associations)
        self.topic = topic
        self.old_stance = old_stance
        self.new_stance = new_stance
        self.reason = reason
        self.event_id = event_id
        
        # Add stance-specific associations
        self.add_association("topic", topic)
        self.add_association("old_stance", old_stance)
        self.add_association("new_stance", new_stance)
        if event_id:
            self.add_association("event_id", event_id)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        data = super().to_dict()
        data.update({
            "topic": self.topic,
            "old_stance": self.old_stance,
            "new_stance": self.new_stance,
            "reason": self.reason
        })
        if self.event_id:
            data["event_id"] = self.event_id
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StanceChangeMemoryItem':
        """Create from dictionary representation."""
        # Parse timestamp from ISO format
        timestamp = datetime.datetime.fromisoformat(data["timestamp"])
        
        return cls(
            topic=data["topic"],
            old_stance=data["old_stance"],
            new_stance=data["new_stance"],
            reason=data["reason"],
            event_id=data.get("event_id"),
            timestamp=timestamp,
            importance=data.get("importance", 0.7),
            decay_rate=data.get("decay_rate", 0.05),
            tags=data.get("tags", []),
            emotional_impact=data.get("emotional_impact", 0.0),
            memory_id=data.get("id"),
            associations=data.get("associations", {})
        )


class RelationshipImpactItem(MemoryBase):
    """
    Memory of how an event impacted a relationship with another senator.
    
    Stores details about relationship changes and their causes.
    """
    
    def __init__(
        self,
        senator_name: str,
        event_id: str,
        impact: float,
        reason: str,
        timestamp: Optional[datetime.datetime] = None,
        importance: float = 0.6,  # Relationship impacts are fairly important
        decay_rate: float = 0.08,  # And decay moderately
        tags: Optional[List[str]] = None,
        emotional_impact: float = 0.0,
        memory_id: Optional[str] = None,
        associations: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a relationship impact memory item.
        
        Args:
            senator_name: Name of the senator
            event_id: ID of the event that affected the relationship
            impact: Impact on relationship score
            reason: Reason for the impact
            timestamp: When the impact occurred
            importance: How important the relationship impact is
            decay_rate: How quickly the memory fades
            tags: List of tags for categorizing the memory
            emotional_impact: Emotional significance
            memory_id: Optional unique identifier for the memory
            associations: Optional related concepts or metadata
        """
        # Add relationship and senator to tags if not already present
        tags = tags or []
        if "relationship" not in tags:
            tags.append("relationship")
        if senator_name not in tags:
            tags.append(senator_name)
            
        # Generate memory ID if not provided
        if not memory_id:
            memory_id = f"relationship_{senator_name}_{uuid.uuid4().hex[:8]}"
            
        super().__init__(timestamp, importance, decay_rate, tags, emotional_impact, memory_id, associations)
        self.senator_name = senator_name
        self.event_id = event_id
        self.impact = impact
        self.reason = reason
        
        # Add relationship-specific associations
        self.add_association("senator_name", senator_name)
        self.add_association("event_id", event_id)
        self.add_association("impact", impact)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        data = super().to_dict()
        data.update({
            "senator_name": self.senator_name,
            "event_id": self.event_id,
            "impact": self.impact,
            "reason": self.reason
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RelationshipImpactItem':
        """Create from dictionary representation."""
        # Parse timestamp from ISO format
        timestamp = datetime.datetime.fromisoformat(data["timestamp"])
        
        return cls(
            senator_name=data["senator_name"],
            event_id=data["event_id"],
            impact=data["impact"],
            reason=data["reason"],
            timestamp=timestamp,
            importance=data.get("importance", 0.6),
            decay_rate=data.get("decay_rate", 0.08),
            tags=data.get("tags", []),
            emotional_impact=data.get("emotional_impact", 0.0),
            memory_id=data.get("id"),
            associations=data.get("associations", {})
        )


class RelationshipMemoryItem(MemoryBase):
    """
    Memory of a relationship with another senator.
    
    Stores details about the relationship itself, separate from specific impacts.
    """
    
    def __init__(
        self,
        senator_name: str,
        relationship_score: float,
        relationship_type: str,
        history_summary: str,
        timestamp: Optional[datetime.datetime] = None,
        importance: float = 0.7,  # Relationships are important
        decay_rate: float = 0.03,  # And decay very slowly
        tags: Optional[List[str]] = None,
        emotional_impact: float = 0.0,
        memory_id: Optional[str] = None,
        associations: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a relationship memory item.
        
        Args:
            senator_name: Name of the senator
            relationship_score: Current relationship score
            relationship_type: Type of relationship (ally, rival, etc.)
            history_summary: Summary of the relationship history
            timestamp: When the relationship was last updated
            importance: How important the relationship is
            decay_rate: How quickly the memory fades
            tags: List of tags for categorizing the memory
            emotional_impact: Emotional significance
            memory_id: Optional unique identifier for the memory
            associations: Optional related concepts or metadata
        """
        # Add relationship and senator to tags if not already present
        tags = tags or []
        if "relationship" not in tags:
            tags.append("relationship")
        if senator_name not in tags:
            tags.append(senator_name)
        if relationship_type not in tags:
            tags.append(relationship_type)
            
        # Generate memory ID if not provided
        if not memory_id:
            memory_id = f"relationship_summary_{senator_name}_{uuid.uuid4().hex[:8]}"
            
        super().__init__(timestamp, importance, decay_rate, tags, emotional_impact, memory_id, associations)
        self.senator_name = senator_name
        self.relationship_score = relationship_score
        self.relationship_type = relationship_type
        self.history_summary = history_summary
        
        # Add relationship-specific associations
        self.add_association("senator_name", senator_name)
        self.add_association("relationship_type", relationship_type)
        self.add_association("relationship_score", relationship_score)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        data = super().to_dict()
        data.update({
            "senator_name": self.senator_name,
            "relationship_score": self.relationship_score,
            "relationship_type": self.relationship_type,
            "history_summary": self.history_summary
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RelationshipMemoryItem':
        """Create from dictionary representation."""
        # Parse timestamp from ISO format
        timestamp = datetime.datetime.fromisoformat(data["timestamp"])
        
        return cls(
            senator_name=data["senator_name"],
            relationship_score=data["relationship_score"],
            relationship_type=data["relationship_type"],
            history_summary=data["history_summary"],
            timestamp=timestamp,
            importance=data.get("importance", 0.7),
            decay_rate=data.get("decay_rate", 0.03),
            tags=data.get("tags", []),
            emotional_impact=data.get("emotional_impact", 0.0),
            memory_id=data.get("id"),
            associations=data.get("associations", {})
        )


# Register memory item types for proper serialization/deserialization
MEMORY_ITEM_TYPES = {
    "EventMemoryItem": EventMemoryItem,
    "ReactionMemoryItem": ReactionMemoryItem,
    "StanceChangeMemoryItem": StanceChangeMemoryItem,
    "RelationshipImpactItem": RelationshipImpactItem,
    "RelationshipMemoryItem": RelationshipMemoryItem
}


def create_memory_from_dict(data: Dict[str, Any]) -> MemoryBase:
    """
    Create the appropriate memory item based on type information in the data.
    
    Args:
        data: Dictionary containing memory data
        
    Returns:
        MemoryBase: A new memory item of the appropriate type
        
    Raises:
        ValueError: If the memory type is unknown
    """
    memory_type = data.get("memory_type")
    if not memory_type:
        # Default to base memory type
        return MemoryBase.from_dict(data)
    
    if memory_type not in MEMORY_ITEM_TYPES:
        raise ValueError(f"Unknown memory type: {memory_type}")
    
    return MEMORY_ITEM_TYPES[memory_type].from_dict(data)