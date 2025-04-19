"""
Base Agent System for Agentic Game Framework.

This module defines the core agent classes and interfaces that form the foundation
of the agent-based architecture used throughout the framework.
"""

import uuid
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Set

from ..events.base import BaseEvent


class BaseAgent(ABC):
    """
    Abstract base class for all agents in the system.
    
    Agents are autonomous entities that can process events, make decisions,
    generate actions, and maintain internal state. This class defines the
    common interface and behavior for all agent types.
    
    Attributes:
        id (str): Unique identifier for the agent
        name (str): Human-readable name for the agent
        attributes (Dict[str, Any]): Agent-specific attributes
        state (Dict[str, Any]): Current internal state of the agent
    """
    
    def __init__(
        self,
        name: str,
        attributes: Optional[Dict[str, Any]] = None,
        agent_id: Optional[str] = None,
        initial_state: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a new agent.
        
        Args:
            name: Human-readable name for the agent
            attributes: Agent-specific attributes
            agent_id: Unique identifier (generated if not provided)
            initial_state: Initial internal state
        """
        self.id = agent_id or str(uuid.uuid4())
        self.name = name
        self.attributes = attributes or {}
        self.state = initial_state or {}
        self._event_subscriptions: Set[str] = set()
    
    @abstractmethod
    def process_event(self, event: BaseEvent) -> None:
        """
        Process an incoming event.
        
        This method is called when an event the agent is subscribed to occurs.
        Agents should implement this method to update their internal state,
        make decisions, and potentially generate new events or actions.
        
        Args:
            event: The event to process
        """
        pass
    
    @abstractmethod
    def generate_action(self) -> Optional[BaseEvent]:
        """
        Generate an action based on the agent's current state.
        
        This method is called periodically to allow the agent to take initiative
        and generate actions without direct external stimuli. The action is
        typically represented as a new event.
        
        Returns:
            Optional[BaseEvent]: An event representing the action, or None if no action
        """
        pass
    
    def update_state(self, updates: Dict[str, Any]) -> None:
        """
        Update the agent's internal state.
        
        Args:
            updates: Dictionary of state variables to update
        """
        self.state.update(updates)
    
    def get_state(self) -> Dict[str, Any]:
        """
        Get the agent's current internal state.
        
        Returns:
            Dict[str, Any]: The current state
        """
        return self.state.copy()
    
    def get_attribute(self, key: str, default: Any = None) -> Any:
        """
        Get an agent attribute.
        
        Args:
            key: The attribute key
            default: Default value if attribute doesn't exist
            
        Returns:
            Any: The attribute value or default
        """
        return self.attributes.get(key, default)
    
    def set_attribute(self, key: str, value: Any) -> None:
        """
        Set an agent attribute.
        
        Args:
            key: The attribute key
            value: The attribute value
        """
        self.attributes[key] = value
    
    def subscribe_to_event(self, event_type: str) -> None:
        """
        Add an event type to the agent's subscriptions.
        
        Args:
            event_type: The event type to subscribe to
        """
        self._event_subscriptions.add(event_type)
    
    def unsubscribe_from_event(self, event_type: str) -> None:
        """
        Remove an event type from the agent's subscriptions.
        
        Args:
            event_type: The event type to unsubscribe from
        """
        if event_type in self._event_subscriptions:
            self._event_subscriptions.remove(event_type)
    
    def get_subscriptions(self) -> Set[str]:
        """
        Get all event types the agent is subscribed to.
        
        Returns:
            Set[str]: Set of event type strings
        """
        return self._event_subscriptions.copy()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the agent to a dictionary representation.
        
        This is useful for serialization, persistence, and transmission.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the agent
        """
        return {
            "id": self.id,
            "name": self.name,
            "attributes": self.attributes,
            "state": self.state,
            "event_subscriptions": list(self._event_subscriptions)
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseAgent':
        """
        Create an agent from a dictionary representation.
        
        Args:
            data: Dictionary containing agent data
            
        Returns:
            BaseAgent: A new agent instance
            
        Raises:
            ValueError: If the dictionary is missing required fields
        """
        if "name" not in data:
            raise ValueError("Agent dictionary must contain 'name'")
            
        agent = cls(
            name=data["name"],
            attributes=data.get("attributes", {}),
            agent_id=data.get("id"),
            initial_state=data.get("state", {})
        )
        
        # Restore subscriptions
        for event_type in data.get("event_subscriptions", []):
            agent.subscribe_to_event(event_type)
            
        return agent
    
    def __str__(self) -> str:
        """
        Get a string representation of the agent.
        
        Returns:
            str: String representation
        """
        return f"{self.name} (id: {self.id})"