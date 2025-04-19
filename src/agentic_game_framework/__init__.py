"""
Agentic Game Framework

A domain-agnostic framework for building agent-based game systems and simulations.
"""

# Version information
__version__ = '0.1.0'

# Import core components for easier access
from .events.base import BaseEvent, EventHandler
from .events.event_bus import EventBus

from .agents.base_agent import BaseAgent
from .agents.agent_factory import AgentFactory
from .agents.agent_manager import AgentManager

from .memory.memory_interface import MemoryItem, MemoryInterface, EventMemoryItem
from .memory.memory_index import MemoryIndex
from .memory.persistence import MemoryPersistenceManager, MemoryStore

from .relationships.base_relationship import BaseRelationship, SimpleRelationship
from .relationships.relationship_manager import RelationshipManager

from .domains.domain_registry import DomainRegistry, register_component, get_component
from .domains.extension_points import (
    DomainExtensionPoint, 
    EventTypeRegistry,
    AgentBehaviorExtension,
    MemoryTypeExtension,
    RelationshipTypeExtension,
    DomainConfigExtension,
    DomainExtensionManager,
    register_extension,
    get_extension
)

# Expose key utilities
from .utils.helpers import (
    generate_id,
    timestamp_now,
    datetime_now,
    ensure_dir,
    load_json,
    save_json
)

# Package structure information
__all__ = [
    # Version
    '__version__',
    
    # Event System
    'BaseEvent',
    'EventHandler',
    'EventBus',
    
    # Agent System
    'BaseAgent',
    'AgentFactory',
    'AgentManager',
    
    # Memory System
    'MemoryItem',
    'MemoryInterface',
    'EventMemoryItem',
    'MemoryIndex',
    'MemoryPersistenceManager',
    'MemoryStore',
    
    # Relationship System
    'BaseRelationship',
    'SimpleRelationship',
    'RelationshipManager',
    
    # Domain Adaptation
    'DomainRegistry',
    'register_component',
    'get_component',
    'DomainExtensionPoint',
    'EventTypeRegistry',
    'AgentBehaviorExtension',
    'MemoryTypeExtension',
    'RelationshipTypeExtension',
    'DomainConfigExtension',
    'DomainExtensionManager',
    'register_extension',
    'get_extension',
    
    # Utilities
    'generate_id',
    'timestamp_now',
    'datetime_now',
    'ensure_dir',
    'load_json',
    'save_json'
]