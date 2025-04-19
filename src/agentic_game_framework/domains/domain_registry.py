"""
Domain Registry for Agentic Game Framework.

This module provides the registry for domain-specific components, allowing
the core framework to be extended for different game domains.
"""

from typing import Any, Dict, Optional, Set, Type


class DomainRegistry:
    """
    Registry of domain-specific components.
    
    The DomainRegistry maintains a mapping of component types and domains to
    their implementing classes. This allows the framework to:
    1. Register domain-specific implementations
    2. Retrieve the appropriate implementation for a domain
    3. Support multiple domains with different implementations
    
    This enables the core framework to be extended for various game domains
    without modifying the core code.
    """
    
    def __init__(self):
        """Initialize a new domain registry with empty registries."""
        # Map of (component_type, domain) -> implementing class
        self._components: Dict[tuple[str, str], Type] = {}
        
        # Set of registered domains
        self._domains: Set[str] = set()
        
        # Set of registered component types
        self._component_types: Set[str] = set()
    
    def register_component(
        self,
        component_type: str,
        domain: str,
        component_class: Type
    ) -> None:
        """
        Register a domain-specific component implementation.
        
        Args:
            component_type: Type of component (e.g., 'agent', 'event')
            domain: Domain identifier (e.g., 'politics', 'fantasy')
            component_class: Implementing class
            
        Raises:
            ValueError: If the component is already registered for this domain
        """
        key = (component_type, domain)
        if key in self._components:
            raise ValueError(
                f"Component type '{component_type}' is already registered for domain '{domain}'"
            )
            
        self._components[key] = component_class
        self._domains.add(domain)
        self._component_types.add(component_type)
    
    def get_component(
        self,
        component_type: str,
        domain: str,
        default: Optional[Type] = None
    ) -> Optional[Type]:
        """
        Get the implementing class for a component type in a domain.
        
        Args:
            component_type: Type of component
            domain: Domain identifier
            default: Default class to return if not found
            
        Returns:
            Optional[Type]: The implementing class, or default if not found
        """
        key = (component_type, domain)
        return self._components.get(key, default)
    
    def get_domains(self) -> Set[str]:
        """
        Get all registered domains.
        
        Returns:
            Set[str]: Set of domain identifiers
        """
        return self._domains.copy()
    
    def get_component_types(self) -> Set[str]:
        """
        Get all registered component types.
        
        Returns:
            Set[str]: Set of component type identifiers
        """
        return self._component_types.copy()
    
    def get_domain_components(self, domain: str) -> Dict[str, Type]:
        """
        Get all components registered for a domain.
        
        Args:
            domain: Domain identifier
            
        Returns:
            Dict[str, Type]: Map of component types to implementing classes
        """
        return {
            component_type: self._components[(component_type, domain)]
            for component_type in self._component_types
            if (component_type, domain) in self._components
        }
    
    def get_component_implementations(self, component_type: str) -> Dict[str, Type]:
        """
        Get all domain implementations of a component type.
        
        Args:
            component_type: Type of component
            
        Returns:
            Dict[str, Type]: Map of domains to implementing classes
        """
        return {
            domain: self._components[(component_type, domain)]
            for domain in self._domains
            if (component_type, domain) in self._components
        }
    
    def has_component(self, component_type: str, domain: str) -> bool:
        """
        Check if a component is registered for a domain.
        
        Args:
            component_type: Type of component
            domain: Domain identifier
            
        Returns:
            bool: True if registered, False otherwise
        """
        return (component_type, domain) in self._components
    
    def unregister_component(self, component_type: str, domain: str) -> bool:
        """
        Unregister a domain-specific component implementation.
        
        Args:
            component_type: Type of component
            domain: Domain identifier
            
        Returns:
            bool: True if unregistered, False if not found
        """
        key = (component_type, domain)
        if key not in self._components:
            return False
            
        del self._components[key]
        
        # Clean up domain and component type sets if needed
        if not any(domain == d for _, d in self._components.keys()):
            self._domains.remove(domain)
            
        if not any(component_type == c for c, _ in self._components.keys()):
            self._component_types.remove(component_type)
            
        return True
    
    def clear(self) -> None:
        """
        Clear all registered components.
        """
        self._components.clear()
        self._domains.clear()
        self._component_types.clear()


# Global instance for convenience
global_registry = DomainRegistry()


def register_component(component_type: str, domain: str, component_class: Type) -> None:
    """
    Register a component with the global registry.
    
    This is a convenience function for registering components without
    directly accessing the global registry.
    
    Args:
        component_type: Type of component
        domain: Domain identifier
        component_class: Implementing class
    """
    global_registry.register_component(component_type, domain, component_class)


def get_component(
    component_type: str,
    domain: str,
    default: Optional[Type] = None
) -> Optional[Type]:
    """
    Get a component from the global registry.
    
    This is a convenience function for retrieving components without
    directly accessing the global registry.
    
    Args:
        component_type: Type of component
        domain: Domain identifier
        default: Default class to return if not found
        
    Returns:
        Optional[Type]: The implementing class, or default if not found
    """
    return global_registry.get_component(component_type, domain, default)