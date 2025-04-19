"""
Base Relationship System for Agentic Game Framework.

This module defines the core relationship classes and interfaces that form the foundation
of the relationship-based architecture used throughout the framework.
"""

import uuid
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Set, Tuple

from ..events.base import BaseEvent


class BaseRelationship(ABC):
    """
    Abstract base class for all agent relationships in the system.
    
    Relationships represent connections between agents, including their type,
    strength, and attributes. They can be updated based on events and provide
    sentiment analysis between agents.
    
    Attributes:
        agent_a_id (str): ID of the first agent in the relationship
        agent_b_id (str): ID of the second agent in the relationship
        relationship_type (str): Type of relationship
        strength (float): Strength of the relationship (-1.0 to 1.0)
        attributes (Dict[str, Any]): Additional relationship attributes
    """
    
    def __init__(
        self,
        agent_a_id: str,
        agent_b_id: str,
        relationship_type: str,
        strength: float = 0.0,
        attributes: Optional[Dict[str, Any]] = None,
        relationship_id: Optional[str] = None
    ):
        """
        Initialize a new relationship.
        
        Args:
            agent_a_id: ID of the first agent
            agent_b_id: ID of the second agent
            relationship_type: Type of relationship
            strength: Initial strength (-1.0 to 1.0)
            attributes: Additional relationship attributes
            relationship_id: Unique identifier (generated if not provided)
        """
        # Ensure consistent ordering of agent IDs
        if agent_a_id > agent_b_id:
            agent_a_id, agent_b_id = agent_b_id, agent_a_id
            
        self.agent_a_id = agent_a_id
        self.agent_b_id = agent_b_id
        self.relationship_type = relationship_type
        self.strength = max(-1.0, min(1.0, strength))  # Clamp to [-1.0, 1.0]
        self.attributes = attributes or {}
        self.id = relationship_id or str(uuid.uuid4())
        self._history: List[Dict[str, Any]] = []
    
    @abstractmethod
    def update(self, event: BaseEvent) -> bool:
        """
        Update the relationship based on an event.
        
        This method should analyze the event and update the relationship's
        strength and attributes accordingly.
        
        Args:
            event: The event that might affect the relationship
            
        Returns:
            bool: True if the relationship was updated, False otherwise
        """
        pass
    
    def get_sentiment(self) -> float:
        """
        Get the sentiment between the agents.
        
        The sentiment is a measure of how positively or negatively the agents
        feel about each other, based on the relationship strength and type.
        
        Returns:
            float: Sentiment score (-1.0 to 1.0)
        """
        return self.strength
    
    def get_attribute(self, key: str, default: Any = None) -> Any:
        """
        Get a relationship attribute.
        
        Args:
            key: The attribute key
            default: Default value if attribute doesn't exist
            
        Returns:
            Any: The attribute value or default
        """
        return self.attributes.get(key, default)
    
    def set_attribute(self, key: str, value: Any) -> None:
        """
        Set a relationship attribute.
        
        Args:
            key: The attribute key
            value: The attribute value
        """
        self.attributes[key] = value
    
    def update_strength(self, delta: float, reason: Optional[str] = None) -> None:
        """
        Update the relationship strength.
        
        Args:
            delta: Change in strength
            reason: Optional reason for the change
        """
        old_strength = self.strength
        self.strength = max(-1.0, min(1.0, self.strength + delta))
        
        # Record in history
        self._history.append({
            "timestamp": uuid.uuid1().time,
            "old_strength": old_strength,
            "new_strength": self.strength,
            "delta": delta,
            "reason": reason
        })
    
    def get_history(self) -> List[Dict[str, Any]]:
        """
        Get the relationship update history.
        
        Returns:
            List[Dict[str, Any]]: List of history entries
        """
        return self._history.copy()
    
    def involves_agent(self, agent_id: str) -> bool:
        """
        Check if this relationship involves a specific agent.
        
        Args:
            agent_id: The agent ID to check
            
        Returns:
            bool: True if the agent is part of this relationship
        """
        return agent_id == self.agent_a_id or agent_id == self.agent_b_id
    
    def get_other_agent_id(self, agent_id: str) -> Optional[str]:
        """
        Get the ID of the other agent in the relationship.
        
        Args:
            agent_id: ID of one agent in the relationship
            
        Returns:
            Optional[str]: ID of the other agent, or None if the given agent is not in the relationship
        """
        if agent_id == self.agent_a_id:
            return self.agent_b_id
        elif agent_id == self.agent_b_id:
            return self.agent_a_id
        else:
            return None
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the relationship to a dictionary representation.
        
        This is useful for serialization, persistence, and transmission.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the relationship
        """
        return {
            "id": self.id,
            "agent_a_id": self.agent_a_id,
            "agent_b_id": self.agent_b_id,
            "relationship_type": self.relationship_type,
            "strength": self.strength,
            "attributes": self.attributes,
            "history": self._history
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseRelationship':
        """
        Create a relationship from a dictionary representation.
        
        Args:
            data: Dictionary containing relationship data
            
        Returns:
            BaseRelationship: A new relationship instance
            
        Raises:
            ValueError: If the dictionary is missing required fields
        """
        required_fields = ["agent_a_id", "agent_b_id", "relationship_type"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Relationship dictionary must contain '{field}'")
                
        relationship = cls(
            agent_a_id=data["agent_a_id"],
            agent_b_id=data["agent_b_id"],
            relationship_type=data["relationship_type"],
            strength=data.get("strength", 0.0),
            attributes=data.get("attributes", {}),
            relationship_id=data.get("id")
        )
        
        # Restore history
        relationship._history = data.get("history", [])
        
        return relationship
    
    def __str__(self) -> str:
        """
        Get a string representation of the relationship.
        
        Returns:
            str: String representation
        """
        return f"{self.relationship_type} between {self.agent_a_id} and {self.agent_b_id} (strength: {self.strength:.2f})"


class SimpleRelationship(BaseRelationship):
    """
    Simple implementation of a relationship.
    
    This concrete implementation provides basic relationship functionality
    with simple event-based updates.
    """
    
    def update(self, event: BaseEvent) -> bool:
        """
        Update the relationship based on an event.
        
        This simple implementation checks if the event involves both agents
        and updates the relationship strength based on event data.
        
        Args:
            event: The event that might affect the relationship
            
        Returns:
            bool: True if the relationship was updated, False otherwise
        """
        # Check if event involves both agents
        if not self._event_involves_both_agents(event):
            return False
            
        # Check if event has a relationship_impact field
        impact = event.data.get("relationship_impact", 0.0)
        if impact != 0.0:
            reason = event.data.get("relationship_reason", f"Event: {event.event_type}")
            self.update_strength(impact, reason)
            return True
            
        return False
    
    def _event_involves_both_agents(self, event: BaseEvent) -> bool:
        """
        Check if an event involves both agents in the relationship.
        
        Args:
            event: The event to check
            
        Returns:
            bool: True if both agents are involved
        """
        involved_agents = set()
        
        # Check source
        if event.source and (event.source == self.agent_a_id or event.source == self.agent_b_id):
            involved_agents.add(event.source)
            
        # Check target
        if event.target and (event.target == self.agent_a_id or event.target == self.agent_b_id):
            involved_agents.add(event.target)
            
        # Check participants in data
        participants = event.data.get("participants", [])
        if isinstance(participants, list):
            for participant in participants:
                if participant == self.agent_a_id or participant == self.agent_b_id:
                    involved_agents.add(participant)
                    
        return len(involved_agents) == 2