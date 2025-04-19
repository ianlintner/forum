"""
Pytest configuration for the Agentic Game Framework tests.

This module contains fixtures and configuration for pytest.
"""

import pytest
import sys
import os

# Add the src directory to the Python path so that imports work correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture
def event_bus():
    """Fixture providing a fresh EventBus instance."""
    from src.agentic_game_framework.events.event_bus import EventBus
    return EventBus()


@pytest.fixture
def agent_factory():
    """Fixture providing a fresh AgentFactory instance."""
    from src.agentic_game_framework.agents.agent_factory import AgentFactory
    return AgentFactory()


@pytest.fixture
def agent_manager(event_bus):
    """Fixture providing a fresh AgentManager instance connected to the event bus."""
    from src.agentic_game_framework.agents.agent_manager import AgentManager
    return AgentManager(event_bus)


@pytest.fixture
def relationship_manager(event_bus):
    """Fixture providing a fresh RelationshipManager instance connected to the event bus."""
    from src.agentic_game_framework.relationships.relationship_manager import RelationshipManager
    return RelationshipManager(event_bus)


@pytest.fixture
def memory_store():
    """Fixture providing a fresh MemoryStore instance."""
    from src.agentic_game_framework.memory.persistence import MemoryStore
    return MemoryStore("test_agent")


@pytest.fixture
def simple_agent():
    """Fixture providing a SimpleAgent instance for testing."""
    from src.agentic_game_framework.examples.simple_simulation import SimpleAgent
    return SimpleAgent("TestAgent")


@pytest.fixture
def domain_registry():
    """Fixture providing a fresh DomainRegistry instance."""
    from src.agentic_game_framework.domains.domain_registry import DomainRegistry
    return DomainRegistry()


@pytest.fixture
def extension_manager():
    """Fixture providing a fresh DomainExtensionManager instance."""
    from src.agentic_game_framework.domains.extension_points import DomainExtensionManager
    return DomainExtensionManager()