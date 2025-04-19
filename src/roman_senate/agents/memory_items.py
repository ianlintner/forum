"""
Roman Senate AI Game
Memory Items Module

This module defines specialized memory item classes that inherit from MemoryBase.
These classes represent different types of memories that senators can have.
"""

from typing import Dict, Any, Optional, List
import datetime

from .memory_base import MemoryBase


class EventMemoryItem(MemoryBase):
    """
    Memory of an observed event.
    
    Stores details about an event that a senator witnessed or participated in.
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
        emotional_impact: float = 0.0
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
        """
        super().__init__(timestamp, importance, decay_rate, tags, emotional_impact)
        self.event_id = event_id
        self.event_type = event_type
        self.source = source
        self.metadata = metadata
    
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
            emotional_impact=data.get("emotional_impact", 0.0)
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
        emotional_impact: float = 0.0
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
        """
        super().__init__(timestamp, importance, decay_rate, tags, emotional_impact)
        self.event_id = event_id
        self.reaction_type = reaction_type
        self.content = content
    
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
            emotional_impact=data.get("emotional_impact", 0.0)
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
        emotional_impact: float = 0.0
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
        """
        # Add topic to tags if not already present
        tags = tags or []
        if topic not in tags:
            tags.append(topic)
            
        super().__init__(timestamp, importance, decay_rate, tags, emotional_impact)
        self.topic = topic
        self.old_stance = old_stance
        self.new_stance = new_stance
        self.reason = reason
        self.event_id = event_id
    
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
            emotional_impact=data.get("emotional_impact", 0.0)
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
        emotional_impact: float = 0.0
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
        """
        # Add senator name to tags if not already present
        tags = tags or []
        if senator_name not in tags:
            tags.append(senator_name)
            
        # Set emotional impact based on relationship impact if not provided
        if emotional_impact == 0.0:
            emotional_impact = impact  # Positive/negative impact = positive/negative emotion
            
        super().__init__(timestamp, importance, decay_rate, tags, emotional_impact)
        self.senator_name = senator_name
        self.event_id = event_id
        self.impact = impact
        self.reason = reason
    
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
            emotional_impact=data.get("emotional_impact", 0.0)
        )


class RelationshipMemoryItem(MemoryBase):
    """
    Memory of a relationship between two senators of a specific type.
    
    Stores details about the relationship value, type, and context.
    """
    
    def __init__(
        self,
        senator_id: str,
        target_senator_id: str,
        relationship_type: str,  # "political", "personal", "mentor", "rival", "family"
        relationship_value: float,
        timestamp: Optional[datetime.datetime] = None,
        importance: float = 0.6,
        decay_rate: float = 0.05,
        tags: Optional[List[str]] = None,
        emotional_impact: float = 0.0,
        context: str = ""
    ):
        """
        Initialize a relationship memory item.
        
        Args:
            senator_id: ID of the senator who has this relationship
            target_senator_id: ID of the target senator in the relationship
            relationship_type: Type of relationship (political, personal, etc.)
            relationship_value: Value of the relationship (-1.0 to 1.0)
            timestamp: When the relationship was recorded/updated
            importance: How important the relationship is
            decay_rate: How quickly the memory fades
            tags: List of tags for categorizing the memory
            emotional_impact: Emotional significance
            context: Context or reason for the relationship value
        """
        # Add relationship to tags if not already present
        tags = tags or []
        if "relationship" not in tags:
            tags.append("relationship")
        if relationship_type not in tags:
            tags.append(relationship_type)
        if target_senator_id not in tags:
            tags.append(target_senator_id)
            
        super().__init__(timestamp, importance, decay_rate, tags, emotional_impact)
        self.senator_id = senator_id
        self.target_senator_id = target_senator_id
        self.relationship_type = relationship_type
        self.relationship_value = relationship_value
        self.context = context
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        data = super().to_dict()
        data.update({
            "senator_id": self.senator_id,
            "target_senator_id": self.target_senator_id,
            "relationship_type": self.relationship_type,
            "relationship_value": self.relationship_value,
            "context": self.context
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RelationshipMemoryItem':
        """Create from dictionary representation."""
        # Parse timestamp from ISO format
        timestamp = datetime.datetime.fromisoformat(data["timestamp"])
        
        return cls(
            senator_id=data["senator_id"],
            target_senator_id=data["target_senator_id"],
            relationship_type=data["relationship_type"],
            relationship_value=data["relationship_value"],
            timestamp=timestamp,
            importance=data.get("importance", 0.6),
            decay_rate=data.get("decay_rate", 0.05),
            tags=data.get("tags", []),
            emotional_impact=data.get("emotional_impact", 0.0),
            context=data.get("context", "")
        )