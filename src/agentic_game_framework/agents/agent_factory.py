"""
Agent Factory for Agentic Game Framework.

This module provides the factory class for creating agent instances based on
registered agent types and configurations.
"""

from typing import Any, Callable, Dict, Optional, Type

from .base_agent import BaseAgent


class AgentFactory:
    """
    Factory for creating agent instances.
    
    The AgentFactory maintains a registry of agent types and provides methods
    for creating new agent instances based on configurations. It supports:
    1. Registering new agent types
    2. Creating agents from configurations
    3. Applying templates to agent configurations
    
    This allows for flexible agent creation without hardcoding agent types.
    """
    
    def __init__(self):
        """Initialize a new agent factory with an empty type registry."""
        # Map of agent_type -> agent class
        self._agent_types: Dict[str, Type[BaseAgent]] = {}
        # Map of template_name -> template function
        self._templates: Dict[str, Callable[[Dict[str, Any]], Dict[str, Any]]] = {}
    
    def register_agent_type(self, agent_type: str, agent_class: Type[BaseAgent]) -> None:
        """
        Register a new agent type.
        
        Args:
            agent_type: String identifier for the agent type
            agent_class: Class to instantiate for this agent type
            
        Raises:
            ValueError: If agent_type is already registered
        """
        if agent_type in self._agent_types:
            raise ValueError(f"Agent type '{agent_type}' is already registered")
            
        self._agent_types[agent_type] = agent_class
    
    def register_template(
        self, 
        template_name: str, 
        template_func: Callable[[Dict[str, Any]], Dict[str, Any]]
    ) -> None:
        """
        Register a template function for agent configuration.
        
        Templates are functions that take a base configuration and return
        a modified configuration with default values or additional settings.
        
        Args:
            template_name: String identifier for the template
            template_func: Function that transforms a configuration dict
            
        Raises:
            ValueError: If template_name is already registered
        """
        if template_name in self._templates:
            raise ValueError(f"Template '{template_name}' is already registered")
            
        self._templates[template_name] = template_func
    
    def create_agent(
        self, 
        agent_type: str, 
        config: Dict[str, Any], 
        template_name: Optional[str] = None
    ) -> BaseAgent:
        """
        Create a new agent instance.
        
        Args:
            agent_type: Type of agent to create
            config: Configuration dictionary for the agent
            template_name: Optional template to apply to the configuration
            
        Returns:
            BaseAgent: A new agent instance
            
        Raises:
            ValueError: If agent_type is not registered
            ValueError: If template_name is specified but not registered
        """
        if agent_type not in self._agent_types:
            raise ValueError(f"Unknown agent type: {agent_type}")
            
        # Apply template if specified
        if template_name:
            if template_name not in self._templates:
                raise ValueError(f"Unknown template: {template_name}")
                
            config = self._templates[template_name](config.copy())
            
        # Create the agent instance
        agent_class = self._agent_types[agent_type]
        return agent_class(**config)
    
    def get_registered_types(self) -> Dict[str, Type[BaseAgent]]:
        """
        Get all registered agent types.
        
        Returns:
            Dict[str, Type[BaseAgent]]: Map of agent type names to classes
        """
        return self._agent_types.copy()
    
    def get_registered_templates(self) -> Dict[str, Callable[[Dict[str, Any]], Dict[str, Any]]]:
        """
        Get all registered templates.
        
        Returns:
            Dict[str, Callable]: Map of template names to template functions
        """
        return self._templates.copy()