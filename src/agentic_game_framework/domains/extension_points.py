"""
Extension Points for Agentic Game Framework.

This module defines the interfaces for domain-specific extensions, allowing
the core framework to be extended in a structured way.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Set, Type

from ..agents.base_agent import BaseAgent
from ..events.base import BaseEvent
from ..memory.memory_interface import MemoryItem
from ..relationships.base_relationship import BaseRelationship


class DomainExtensionPoint(ABC):
    """
    Base class for all domain extension points.
    
    Extension points define interfaces that domain-specific implementations
    must adhere to, ensuring compatibility with the core framework.
    """
    
    @classmethod
    @abstractmethod
    def get_extension_point_id(cls) -> str:
        """
        Get the unique identifier for this extension point.
        
        Returns:
            str: Extension point identifier
        """
        pass


class EventTypeRegistry(DomainExtensionPoint):
    """
    Extension point for registering domain-specific event types.
    
    This allows domains to define their own event types and handlers
    while maintaining compatibility with the core event system.
    """
    
    @classmethod
    def get_extension_point_id(cls) -> str:
        return "event_type_registry"
    
    @abstractmethod
    def register_event_types(self) -> Dict[str, Type[BaseEvent]]:
        """
        Register domain-specific event types.
        
        Returns:
            Dict[str, Type[BaseEvent]]: Map of event type IDs to event classes
        """
        pass
    
    @abstractmethod
    def get_event_type_metadata(self, event_type: str) -> Dict[str, Any]:
        """
        Get metadata for a specific event type.
        
        Args:
            event_type: Event type identifier
            
        Returns:
            Dict[str, Any]: Metadata for the event type
        """
        pass


class AgentBehaviorExtension(DomainExtensionPoint):
    """
    Extension point for domain-specific agent behaviors.
    
    This allows domains to define custom behaviors for agents
    without modifying the core agent system.
    """
    
    @classmethod
    def get_extension_point_id(cls) -> str:
        return "agent_behavior_extension"
    
    @abstractmethod
    def extend_agent(self, agent: BaseAgent) -> None:
        """
        Extend an agent with domain-specific behaviors.
        
        Args:
            agent: The agent to extend
        """
        pass
    
    @abstractmethod
    def process_domain_event(self, agent: BaseAgent, event: BaseEvent) -> None:
        """
        Process a domain-specific event for an agent.
        
        Args:
            agent: The agent processing the event
            event: The event to process
        """
        pass
    
    @abstractmethod
    def generate_domain_actions(self, agent: BaseAgent) -> List[BaseEvent]:
        """
        Generate domain-specific actions for an agent.
        
        Args:
            agent: The agent generating actions
            
        Returns:
            List[BaseEvent]: List of generated events
        """
        pass


class MemoryTypeExtension(DomainExtensionPoint):
    """
    Extension point for domain-specific memory types.
    
    This allows domains to define custom memory types and retrieval
    mechanisms without modifying the core memory system.
    """
    
    @classmethod
    def get_extension_point_id(cls) -> str:
        return "memory_type_extension"
    
    @abstractmethod
    def register_memory_types(self) -> Dict[str, Type[MemoryItem]]:
        """
        Register domain-specific memory types.
        
        Returns:
            Dict[str, Type[MemoryItem]]: Map of memory type IDs to memory classes
        """
        pass
    
    @abstractmethod
    def create_memory_from_event(self, event: BaseEvent) -> Optional[MemoryItem]:
        """
        Create a domain-specific memory from an event.
        
        Args:
            event: The event to create a memory from
            
        Returns:
            Optional[MemoryItem]: The created memory, or None if not applicable
        """
        pass
    
    @abstractmethod
    def enhance_memory_retrieval(
        self,
        query: Dict[str, Any],
        memories: List[MemoryItem]
    ) -> List[MemoryItem]:
        """
        Enhance memory retrieval with domain-specific logic.
        
        Args:
            query: The retrieval query
            memories: The initially retrieved memories
            
        Returns:
            List[MemoryItem]: The enhanced list of memories
        """
        pass


class RelationshipTypeExtension(DomainExtensionPoint):
    """
    Extension point for domain-specific relationship types.
    
    This allows domains to define custom relationship types and dynamics
    without modifying the core relationship system.
    """
    
    @classmethod
    def get_extension_point_id(cls) -> str:
        return "relationship_type_extension"
    
    @abstractmethod
    def register_relationship_types(self) -> Dict[str, Type[BaseRelationship]]:
        """
        Register domain-specific relationship types.
        
        Returns:
            Dict[str, Type[BaseRelationship]]: Map of relationship type IDs to relationship classes
        """
        pass
    
    @abstractmethod
    def create_default_relationships(
        self,
        agent_ids: List[str]
    ) -> List[BaseRelationship]:
        """
        Create default relationships between agents.
        
        Args:
            agent_ids: List of agent IDs
            
        Returns:
            List[BaseRelationship]: List of created relationships
        """
        pass
    
    @abstractmethod
    def get_relationship_dynamics(
        self,
        relationship_type: str
    ) -> Dict[str, Any]:
        """
        Get dynamics information for a relationship type.
        
        Args:
            relationship_type: Relationship type identifier
            
        Returns:
            Dict[str, Any]: Dynamics information
        """
        pass


class DomainConfigExtension(DomainExtensionPoint):
    """
    Extension point for domain-specific configuration.
    
    This allows domains to define their own configuration parameters
    and validation logic.
    """
    
    @classmethod
    def get_extension_point_id(cls) -> str:
        return "domain_config_extension"
    
    @abstractmethod
    def get_default_config(self) -> Dict[str, Any]:
        """
        Get the default configuration for this domain.
        
        Returns:
            Dict[str, Any]: Default configuration
        """
        pass
    
    @abstractmethod
    def validate_config(self, config: Dict[str, Any]) -> List[str]:
        """
        Validate a configuration for this domain.
        
        Args:
            config: The configuration to validate
            
        Returns:
            List[str]: List of validation errors, empty if valid
        """
        pass
    
    @abstractmethod
    def apply_config(self, config: Dict[str, Any]) -> None:
        """
        Apply a configuration to this domain.
        
        Args:
            config: The configuration to apply
        """
        pass


class DomainExtensionManager:
    """
    Manager for domain extension points.
    
    The DomainExtensionManager maintains a registry of extension point
    implementations for different domains and provides methods for
    retrieving and using them.
    """
    
    def __init__(self):
        """Initialize a new domain extension manager with empty registries."""
        # Map of (extension_point_id, domain) -> implementing instance
        self._extensions: Dict[tuple[str, str], DomainExtensionPoint] = {}
        
        # Set of registered domains
        self._domains: Set[str] = set()
        
        # Set of registered extension point IDs
        self._extension_point_ids: Set[str] = set()
    
    def register_extension(
        self,
        extension: DomainExtensionPoint,
        domain: str
    ) -> None:
        """
        Register a domain extension point implementation.
        
        Args:
            extension: The extension point implementation
            domain: Domain identifier
            
        Raises:
            ValueError: If the extension is already registered for this domain
        """
        extension_id = extension.get_extension_point_id()
        key = (extension_id, domain)
        
        if key in self._extensions:
            raise ValueError(
                f"Extension point '{extension_id}' is already registered for domain '{domain}'"
            )
            
        self._extensions[key] = extension
        self._domains.add(domain)
        self._extension_point_ids.add(extension_id)
    
    def get_extension(
        self,
        extension_id: str,
        domain: str
    ) -> Optional[DomainExtensionPoint]:
        """
        Get an extension point implementation for a domain.
        
        Args:
            extension_id: Extension point identifier
            domain: Domain identifier
            
        Returns:
            Optional[DomainExtensionPoint]: The extension implementation, or None if not found
        """
        key = (extension_id, domain)
        return self._extensions.get(key)
    
    def get_domains(self) -> Set[str]:
        """
        Get all registered domains.
        
        Returns:
            Set[str]: Set of domain identifiers
        """
        return self._domains.copy()
    
    def get_extension_point_ids(self) -> Set[str]:
        """
        Get all registered extension point IDs.
        
        Returns:
            Set[str]: Set of extension point identifiers
        """
        return self._extension_point_ids.copy()
    
    def get_domain_extensions(self, domain: str) -> Dict[str, DomainExtensionPoint]:
        """
        Get all extensions registered for a domain.
        
        Args:
            domain: Domain identifier
            
        Returns:
            Dict[str, DomainExtensionPoint]: Map of extension IDs to implementations
        """
        return {
            extension_id: self._extensions[(extension_id, domain)]
            for extension_id in self._extension_point_ids
            if (extension_id, domain) in self._extensions
        }
    
    def get_extension_implementations(
        self,
        extension_id: str
    ) -> Dict[str, DomainExtensionPoint]:
        """
        Get all domain implementations of an extension point.
        
        Args:
            extension_id: Extension point identifier
            
        Returns:
            Dict[str, DomainExtensionPoint]: Map of domains to implementations
        """
        return {
            domain: self._extensions[(extension_id, domain)]
            for domain in self._domains
            if (extension_id, domain) in self._extensions
        }
    
    def has_extension(self, extension_id: str, domain: str) -> bool:
        """
        Check if an extension is registered for a domain.
        
        Args:
            extension_id: Extension point identifier
            domain: Domain identifier
            
        Returns:
            bool: True if registered, False otherwise
        """
        return (extension_id, domain) in self._extensions
    
    def unregister_extension(self, extension_id: str, domain: str) -> bool:
        """
        Unregister a domain extension point implementation.
        
        Args:
            extension_id: Extension point identifier
            domain: Domain identifier
            
        Returns:
            bool: True if unregistered, False if not found
        """
        key = (extension_id, domain)
        if key not in self._extensions:
            return False
            
        del self._extensions[key]
        
        # Clean up domain and extension point ID sets if needed
        if not any(domain == d for _, d in self._extensions.keys()):
            self._domains.remove(domain)
            
        if not any(extension_id == e for e, _ in self._extensions.keys()):
            self._extension_point_ids.remove(extension_id)
            
        return True
    
    def clear(self) -> None:
        """
        Clear all registered extensions.
        """
        self._extensions.clear()
        self._domains.clear()
        self._extension_point_ids.clear()


# Global instance for convenience
global_extension_manager = DomainExtensionManager()


def register_extension(extension: DomainExtensionPoint, domain: str) -> None:
    """
    Register an extension with the global manager.
    
    This is a convenience function for registering extensions without
    directly accessing the global manager.
    
    Args:
        extension: The extension point implementation
        domain: Domain identifier
    """
    global_extension_manager.register_extension(extension, domain)


def get_extension(extension_id: str, domain: str) -> Optional[DomainExtensionPoint]:
    """
    Get an extension from the global manager.
    
    This is a convenience function for retrieving extensions without
    directly accessing the global manager.
    
    Args:
        extension_id: Extension point identifier
        domain: Domain identifier
        
    Returns:
        Optional[DomainExtensionPoint]: The extension implementation, or None if not found
    """
    return global_extension_manager.get_extension(extension_id, domain)