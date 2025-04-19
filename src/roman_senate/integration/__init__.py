"""
Integration Layer between Roman Senate and agentic_game_framework.

This package provides adapter classes and utilities that bridge the 
Roman Senate simulation components with the agentic_game_framework architecture.

The integration layer enables:
- Events to flow between both systems
- Agents from one system to interact with agents from the other
- Memory to be shared or synchronized between systems
- Relationships to be maintained consistently

Part of the Migration Plan: Phase 4 - Integration Layer.
"""

from .framework_events import (
    EventBridgeAdapter,
    RomanToFrameworkEventAdapter,
    FrameworkToRomanEventAdapter,
)

from .framework_agents import (
    AgentBridgeAdapter,
    RomanToFrameworkAgentAdapter,
    FrameworkToRomanAgentAdapter,
)

from .utils import (
    convert_roman_timestamp,
    convert_framework_timestamp,
    get_roman_event_type,
    get_framework_event_type,
    get_memory_adapter,
)

__all__ = [
    'EventBridgeAdapter',
    'RomanToFrameworkEventAdapter',
    'FrameworkToRomanEventAdapter',
    'AgentBridgeAdapter',
    'RomanToFrameworkAgentAdapter',
    'FrameworkToRomanAgentAdapter',
    'convert_roman_timestamp',
    'convert_framework_timestamp',
    'get_roman_event_type',
    'get_framework_event_type',
    'get_memory_adapter'
]