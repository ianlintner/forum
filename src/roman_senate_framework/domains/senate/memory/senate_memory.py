"""
Roman Senate Memory Types for Agentic Game Framework.

This module implements memory types specific to the Roman Senate domain.
"""

import logging
import time
from typing import Any, Dict, List, Optional, Set, Type

from src.agentic_game_framework.memory.memory_interface import MemoryItem
from src.agentic_game_framework.events.base import BaseEvent

logger = logging.getLogger(__name__)


class SenateMemoryItem(MemoryItem):
    """Base class for all Senate-specific memory items."""
    
    def __init__(
        self,
        memory_id: str,
        timestamp: float,
        event: Optional[BaseEvent] = None,
        importance: float = 0.5,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a Senate memory item.
        
        Args:
            memory_id: Unique identifier for this memory
            timestamp: Creation time of the memory
            event: Optional event that generated this memory
            importance: Importance score (0.0 to 1.0)
            metadata: Additional metadata
        """
        super().__init__(
            memory_id=memory_id,
            timestamp=timestamp,
            importance=importance,
            metadata=metadata or {}
        )
        self.event = event
        
        # Extract event data if provided
        if event:
            self.extract_from_event(event)
    
    def extract_from_event(self, event: BaseEvent) -> None:
        """
        Extract data from an event to populate memory fields.
        
        Args:
            event: The event to extract data from
        """
        # Base implementation just stores the event type
        self.metadata["event_type"] = event.event_type
        self.metadata["event_id"] = event.get_id()
        self.metadata["event_source"] = event.source
        self.metadata["event_target"] = event.target
    
    def get_embedding_text(self) -> str:
        """
        Get text representation for embedding.
        
        Returns:
            str: Text representation of this memory
        """
        # Base implementation just returns a simple description
        return f"Memory of {self.metadata.get('event_type', 'unknown event')} at {time.ctime(self.timestamp)}"
    
    def get_retrieval_score(self, query: Dict[str, Any]) -> float:
        """
        Calculate retrieval score for a query.
        
        Args:
            query: Query parameters
            
        Returns:
            float: Retrieval score (0.0 to 1.0)
        """
        # Base implementation just uses importance
        return self.importance


class SpeechMemory(SenateMemoryItem):
    """Memory of a speech given in the Senate."""
    
    def __init__(
        self,
        memory_id: str,
        timestamp: float,
        event: Optional[BaseEvent] = None,
        importance: float = 0.7,
        metadata: Optional[Dict[str, Any]] = None,
        speaker_id: Optional[str] = None,
        topic: Optional[str] = None,
        stance: Optional[str] = None,
        content: Optional[str] = None
    ):
        """
        Initialize a speech memory.
        
        Args:
            memory_id: Unique identifier for this memory
            timestamp: Creation time of the memory
            event: Optional event that generated this memory
            importance: Importance score (0.0 to 1.0)
            metadata: Additional metadata
            speaker_id: ID of the speaker
            topic: Topic of the speech
            stance: Stance taken in the speech
            content: Content of the speech
        """
        super().__init__(
            memory_id=memory_id,
            timestamp=timestamp,
            event=event,
            importance=importance,
            metadata=metadata or {}
        )
        
        # Speech-specific data
        self.speech_data = {
            "speaker_id": speaker_id,
            "topic": topic,
            "stance": stance,
            "content": content
        }
        
        # If these weren't provided but event was, extract from event
        if event and event.event_type == "senate.speech":
            self.extract_from_event(event)
    
    def extract_from_event(self, event: BaseEvent) -> None:
        """
        Extract data from a speech event.
        
        Args:
            event: The speech event
        """
        super().extract_from_event(event)
        
        if event.event_type == "senate.speech":
            self.speech_data["speaker_id"] = event.data.get("speaker_id")
            self.speech_data["topic"] = event.data.get("topic")
            self.speech_data["stance"] = event.data.get("stance")
            self.speech_data["content"] = event.data.get("content")
    
    def get_embedding_text(self) -> str:
        """
        Get text representation for embedding.
        
        Returns:
            str: Text representation of this memory
        """
        speaker = self.speech_data.get("speaker_id", "unknown speaker")
        topic = self.speech_data.get("topic", "unknown topic")
        stance = self.speech_data.get("stance", "unknown stance")
        content = self.speech_data.get("content", "")
        
        return f"Speech by {speaker} on {topic} with {stance} stance: {content}"
    
    def get_retrieval_score(self, query: Dict[str, Any]) -> float:
        """
        Calculate retrieval score for a query.
        
        Args:
            query: Query parameters
            
        Returns:
            float: Retrieval score (0.0 to 1.0)
        """
        base_score = self.importance
        
        # Boost score for matching parameters
        if "speaker_id" in query and query["speaker_id"] == self.speech_data.get("speaker_id"):
            base_score += 0.2
        
        if "topic" in query and query["topic"] == self.speech_data.get("topic"):
            base_score += 0.3
        
        if "stance" in query and query["stance"] == self.speech_data.get("stance"):
            base_score += 0.1
        
        # Cap at 1.0
        return min(base_score, 1.0)


class DebateMemory(SenateMemoryItem):
    """Memory of a debate in the Senate."""
    
    def __init__(
        self,
        memory_id: str,
        timestamp: float,
        event: Optional[BaseEvent] = None,
        importance: float = 0.6,
        metadata: Optional[Dict[str, Any]] = None,
        debate_event_type: Optional[str] = None,
        topic: Optional[str] = None
    ):
        """
        Initialize a debate memory.
        
        Args:
            memory_id: Unique identifier for this memory
            timestamp: Creation time of the memory
            event: Optional event that generated this memory
            importance: Importance score (0.0 to 1.0)
            metadata: Additional metadata
            debate_event_type: Type of debate event
            topic: Topic of the debate
        """
        super().__init__(
            memory_id=memory_id,
            timestamp=timestamp,
            event=event,
            importance=importance,
            metadata=metadata or {}
        )
        
        # Debate-specific data
        self.debate_data = {
            "debate_event_type": debate_event_type,
            "topic": topic
        }
        
        # If these weren't provided but event was, extract from event
        if event and event.event_type == "senate.debate":
            self.extract_from_event(event)
    
    def extract_from_event(self, event: BaseEvent) -> None:
        """
        Extract data from a debate event.
        
        Args:
            event: The debate event
        """
        super().extract_from_event(event)
        
        if event.event_type == "senate.debate":
            self.debate_data["debate_event_type"] = event.data.get("debate_event_type")
            self.debate_data["topic"] = event.data.get("topic")
            
            # For speaker change events, record the speaker
            if event.data.get("debate_event_type") == "speaker_change":
                self.debate_data["speaker_id"] = event.data.get("speaker_id")
    
    def get_embedding_text(self) -> str:
        """
        Get text representation for embedding.
        
        Returns:
            str: Text representation of this memory
        """
        event_type = self.debate_data.get("debate_event_type", "unknown event")
        topic = self.debate_data.get("topic", "unknown topic")
        
        text = f"Debate event: {event_type} on topic {topic}"
        
        # Add speaker info if available
        if "speaker_id" in self.debate_data:
            text += f" with speaker {self.debate_data['speaker_id']}"
        
        return text
    
    def get_retrieval_score(self, query: Dict[str, Any]) -> float:
        """
        Calculate retrieval score for a query.
        
        Args:
            query: Query parameters
            
        Returns:
            float: Retrieval score (0.0 to 1.0)
        """
        base_score = self.importance
        
        # Boost score for matching parameters
        if "topic" in query and query["topic"] == self.debate_data.get("topic"):
            base_score += 0.3
        
        if "debate_event_type" in query and query["debate_event_type"] == self.debate_data.get("debate_event_type"):
            base_score += 0.2
        
        if "speaker_id" in query and "speaker_id" in self.debate_data and query["speaker_id"] == self.debate_data.get("speaker_id"):
            base_score += 0.2
        
        # Cap at 1.0
        return min(base_score, 1.0)


class RelationshipMemory(SenateMemoryItem):
    """Memory of a relationship change in the Senate."""
    
    def __init__(
        self,
        memory_id: str,
        timestamp: float,
        event: Optional[BaseEvent] = None,
        importance: float = 0.8,
        metadata: Optional[Dict[str, Any]] = None,
        source_id: Optional[str] = None,
        target_id: Optional[str] = None,
        relationship_event_type: Optional[str] = None,
        relationship_type: Optional[str] = None,
        change_value: Optional[float] = None,
        reason: Optional[str] = None
    ):
        """
        Initialize a relationship memory.
        
        Args:
            memory_id: Unique identifier for this memory
            timestamp: Creation time of the memory
            event: Optional event that generated this memory
            importance: Importance score (0.0 to 1.0)
            metadata: Additional metadata
            source_id: ID of the source agent
            target_id: ID of the target agent
            relationship_event_type: Type of relationship event
            relationship_type: Type of relationship
            change_value: Value of the relationship change
            reason: Reason for the relationship change
        """
        super().__init__(
            memory_id=memory_id,
            timestamp=timestamp,
            event=event,
            importance=importance,
            metadata=metadata or {}
        )
        
        # Relationship-specific data
        self.relationship_data = {
            "source_id": source_id,
            "target_id": target_id,
            "relationship_event_type": relationship_event_type,
            "relationship_type": relationship_type,
            "change_value": change_value,
            "reason": reason
        }
        
        # If these weren't provided but event was, extract from event
        if event and event.event_type == "senate.relationship":
            self.extract_from_event(event)
    
    def extract_from_event(self, event: BaseEvent) -> None:
        """
        Extract data from a relationship event.
        
        Args:
            event: The relationship event
        """
        super().extract_from_event(event)
        
        if event.event_type == "senate.relationship":
            self.relationship_data["source_id"] = event.data.get("source_id")
            self.relationship_data["target_id"] = event.data.get("target_id")
            self.relationship_data["relationship_event_type"] = event.data.get("relationship_event_type")
            self.relationship_data["relationship_type"] = event.data.get("relationship_type")
            self.relationship_data["change_value"] = event.data.get("change_value")
            self.relationship_data["reason"] = event.data.get("reason")
    
    def get_embedding_text(self) -> str:
        """
        Get text representation for embedding.
        
        Returns:
            str: Text representation of this memory
        """
        source = self.relationship_data.get("source_id", "unknown source")
        target = self.relationship_data.get("target_id", "unknown target")
        rel_type = self.relationship_data.get("relationship_type", "unknown type")
        event_type = self.relationship_data.get("relationship_event_type", "change")
        change = self.relationship_data.get("change_value", 0)
        reason = self.relationship_data.get("reason", "unknown reason")
        
        direction = "improved" if change > 0 else "worsened"
        
        return f"Relationship {event_type} between {source} and {target}: {rel_type} relationship {direction} by {abs(change)} because {reason}"
    
    def get_retrieval_score(self, query: Dict[str, Any]) -> float:
        """
        Calculate retrieval score for a query.
        
        Args:
            query: Query parameters
            
        Returns:
            float: Retrieval score (0.0 to 1.0)
        """
        base_score = self.importance
        
        # Boost score for matching parameters
        if "source_id" in query and query["source_id"] == self.relationship_data.get("source_id"):
            base_score += 0.2
        
        if "target_id" in query and query["target_id"] == self.relationship_data.get("target_id"):
            base_score += 0.2
        
        if "relationship_type" in query and query["relationship_type"] == self.relationship_data.get("relationship_type"):
            base_score += 0.1
        
        # Special case: if querying for either party in the relationship
        if "agent_id" in query:
            if query["agent_id"] == self.relationship_data.get("source_id") or query["agent_id"] == self.relationship_data.get("target_id"):
                base_score += 0.3
        
        # Cap at 1.0
        return min(base_score, 1.0)