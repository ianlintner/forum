"""
Agent Bridging between Roman Senate and agentic_game_framework.

This module provides adapter classes that allow agents from the Roman Senate 
simulation to interact with agents from the agentic_game_framework and vice versa.

Part of the Migration Plan: Phase 4 - Integration Layer.
"""

from typing import Dict, Any, Optional, List, Set, Type, Union, cast
from datetime import datetime
import uuid
import logging
from abc import ABC, abstractmethod

from agentic_game_framework.agents.base_agent import BaseAgent as FrameworkBaseAgent
from agentic_game_framework.events.base import BaseEvent as FrameworkBaseEvent
from agentic_game_framework.events.event_bus import EventBus as FrameworkEventBus

from ..agents.event_driven_senator_agent import EventDrivenSenatorAgent
from ..agents.enhanced_senator_agent import EnhancedSenatorAgent
from ..core.events.base import BaseEvent as RomanBaseEvent
from ..core.events.event_bus import EventBus as RomanEventBus

from .framework_events import RomanToFrameworkEventAdapter, FrameworkToRomanEventAdapter


logger = logging.getLogger(__name__)


class AgentBridgeAdapter:
    """
    Bridge between Roman Senate and agentic_game_framework agent systems.
    
    This adapter creates proxy agents in each system that represent agents
    from the other system, allowing them to interact seamlessly.
    
    Attributes:
        roman_event_bus: The Roman Senate event bus
        framework_event_bus: The agentic_game_framework event bus
        roman_to_framework_adapters: Map of Roman agent ID to its Framework adapter
        framework_to_roman_adapters: Map of Framework agent ID to its Roman adapter
    """
    
    def __init__(
        self,
        roman_event_bus: RomanEventBus,
        framework_event_bus: FrameworkEventBus,
        event_type_mappings: Optional[Dict[str, str]] = None
    ):
        """
        Initialize the agent bridge.
        
        Args:
            roman_event_bus: The Roman Senate event bus
            framework_event_bus: The agentic_game_framework event bus
            event_type_mappings: Optional mappings between event types.
                Keys are Roman event types, values are Framework event types.
        """
        self.roman_event_bus = roman_event_bus
        self.framework_event_bus = framework_event_bus
        self.event_type_mappings = event_type_mappings or {}
        
        # Create event adapters
        self.roman_to_framework_event_adapter = RomanToFrameworkEventAdapter(self.event_type_mappings)
        self.framework_to_roman_event_adapter = FrameworkToRomanEventAdapter(
            {v: k for k, v in self.event_type_mappings.items()})
        
        # Maps to track agent adapters
        self.roman_to_framework_adapters: Dict[str, RomanToFrameworkAgentAdapter] = {}
        self.framework_to_roman_adapters: Dict[str, FrameworkToRomanAgentAdapter] = {}
    
    def register_roman_agent(self, agent: Union[EventDrivenSenatorAgent, EnhancedSenatorAgent]) -> FrameworkBaseAgent:
        """
        Register a Roman Senate agent and create a Framework adapter for it.
        
        Args:
            agent: The Roman Senate agent to register
            
        Returns:
            FrameworkBaseAgent: The Framework adapter representing the Roman agent
        """
        agent_id = agent.senator["id"]
        
        # Check if already registered
        if agent_id in self.roman_to_framework_adapters:
            return self.roman_to_framework_adapters[agent_id]
        
        # Create adapter
        adapter = RomanToFrameworkAgentAdapter(
            agent=agent,
            framework_event_bus=self.framework_event_bus,
            event_adapter=self.roman_to_framework_event_adapter
        )
        
        # Store in map
        self.roman_to_framework_adapters[agent_id] = adapter
        
        return adapter
    
    def register_framework_agent(self, agent: FrameworkBaseAgent) -> EnhancedSenatorAgent:
        """
        Register a Framework agent and create a Roman adapter for it.
        
        Args:
            agent: The Framework agent to register
            
        Returns:
            EnhancedSenatorAgent: The Roman adapter representing the Framework agent
        """
        agent_id = agent.id
        
        # Check if already registered
        if agent_id in self.framework_to_roman_adapters:
            return self.framework_to_roman_adapters[agent_id]
        
        # Create adapter
        adapter = FrameworkToRomanAgentAdapter(
            agent=agent,
            roman_event_bus=self.roman_event_bus,
            event_adapter=self.framework_to_roman_event_adapter
        )
        
        # Store in map
        self.framework_to_roman_adapters[agent_id] = adapter
        
        return adapter
    
    def get_framework_agent(self, roman_agent_id: str) -> Optional[FrameworkBaseAgent]:
        """
        Get the Framework adapter for a Roman agent.
        
        Args:
            roman_agent_id: ID of the Roman agent
            
        Returns:
            Optional[FrameworkBaseAgent]: The Framework adapter, or None if not found
        """
        return self.roman_to_framework_adapters.get(roman_agent_id)
    
    def get_roman_agent(self, framework_agent_id: str) -> Optional[EnhancedSenatorAgent]:
        """
        Get the Roman adapter for a Framework agent.
        
        Args:
            framework_agent_id: ID of the Framework agent
            
        Returns:
            Optional[EnhancedSenatorAgent]: The Roman adapter, or None if not found
        """
        return self.framework_to_roman_adapters.get(framework_agent_id)


class RomanToFrameworkAgentAdapter(FrameworkBaseAgent):
    """
    Adapter that represents a Roman Senate agent in the agentic_game_framework.
    
    This adapter translates between the different agent interfaces, forwarding
    events and actions between the two systems.
    
    Attributes:
        roman_agent: The Roman Senate agent being adapted
        framework_event_bus: The agentic_game_framework event bus
        event_adapter: Adapter for converting events
    """
    
    def __init__(
        self,
        agent: Union[EventDrivenSenatorAgent, EnhancedSenatorAgent],
        framework_event_bus: FrameworkEventBus,
        event_adapter: RomanToFrameworkEventAdapter
    ):
        """
        Initialize the adapter.
        
        Args:
            agent: The Roman Senate agent to adapt
            framework_event_bus: The agentic_game_framework event bus
            event_adapter: Adapter for converting events
        """
        super().__init__(
            name=agent.senator["name"],
            agent_id=agent.senator["id"],
            attributes=self._convert_attributes(agent.senator),
            initial_state=self._convert_state(agent)
        )
        
        self.roman_agent = agent
        self.framework_event_bus = framework_event_bus
        self.event_adapter = event_adapter
        
        # Subscribe to the same events as the Roman agent
        self._setup_event_subscriptions()
    
    def process_event(self, event: FrameworkBaseEvent) -> None:
        """
        Process a Framework event by forwarding it to the Roman agent.
        
        Args:
            event: The Framework event to process
        """
        from .framework_events import FrameworkToRomanEventAdapter
        
        # Create a temporary adapter for this specific event
        adapter = FrameworkToRomanEventAdapter()
        
        # Convert the event
        roman_event = adapter.adapt(event)
        
        if roman_event:
            # Forward to the Roman agent's event handling
            self.roman_agent.event_bus.publish(roman_event)
    
    def generate_action(self) -> Optional[FrameworkBaseEvent]:
        """
        Generate an action by querying the Roman agent.
        
        This method is called by the Framework when the agent should take initiative.
        
        Returns:
            Optional[FrameworkBaseEvent]: An event representing the action, or None
        """
        # Roman agents don't have a direct equivalent to generate_action,
        # so this is a placeholder that could be customized based on needs
        return None
    
    def _convert_attributes(self, senator_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert Roman senator attributes to Framework agent attributes.
        
        Args:
            senator_data: The Roman senator data
            
        Returns:
            Dict[str, Any]: Converted attributes
        """
        # Copy relevant senator attributes
        attributes = {}
        
        # Include key senator properties
        for key in ["name", "faction", "age", "wealth", "military_experience", 
                    "oratory_skill", "political_influence"]:
            if key in senator_data:
                attributes[key] = senator_data[key]
        
        # Add special marker for integration
        attributes["is_roman_senator_adapter"] = True
        
        return attributes
    
    def _convert_state(self, agent: Union[EventDrivenSenatorAgent, EnhancedSenatorAgent]) -> Dict[str, Any]:
        """
        Convert Roman agent state to Framework agent state.
        
        Args:
            agent: The Roman agent
            
        Returns:
            Dict[str, Any]: Converted state
        """
        state = {
            "current_stance": agent.current_stance,
            "debate_in_progress": agent.debate_in_progress,
        }
        
        if hasattr(agent, "active_debate_topic") and agent.active_debate_topic:
            state["active_debate_topic"] = agent.active_debate_topic
            
        if hasattr(agent, "current_speaker") and agent.current_speaker:
            state["current_speaker"] = agent.current_speaker
            
        return state
    
    def _setup_event_subscriptions(self) -> None:
        """Set up event subscriptions based on the Roman agent's subscriptions."""
        # Subscribe to all events that the Roman agent is subscribed to
        # This is a simplified approach - in a real system you might want
        # to be more selective about which events to subscribe to
        if isinstance(self.roman_agent, EventDrivenSenatorAgent):
            # These are event types the senator normally cares about
            debate_events = [
                "debate_started", "debate_ended", "speech_started", 
                "speech_ended", "vote_started", "vote_ended"
            ]
            
            for event_type in debate_events:
                self.subscribe_to_event(event_type)


class FrameworkToRomanAgentAdapter(EnhancedSenatorAgent):
    """
    Adapter that represents a Framework agent as a Roman Senate agent.
    
    This adapter translates between the different agent interfaces, forwarding
    events and actions between the two systems.
    
    Attributes:
        framework_agent: The Framework agent being adapted
        roman_event_bus: The Roman Senate event bus
        event_adapter: Adapter for converting events
    """
    
    def __init__(
        self,
        agent: FrameworkBaseAgent,
        roman_event_bus: RomanEventBus,
        event_adapter: FrameworkToRomanEventAdapter
    ):
        """
        Initialize the adapter.
        
        Args:
            agent: The Framework agent to adapt
            roman_event_bus: The Roman Senate event bus
            event_adapter: Adapter for converting events
        """
        # Create senator data from framework agent
        senator_data = self._create_senator_data(agent)
        
        # We need a minimal constructor that bypasses some of the normal initialization
        # because we're creating this adapter on the fly
        from ..utils.llm.mock import MockLLMProvider
        
        # Call the superclass constructor with minimal required arguments
        super().__init__(
            senator=senator_data,
            llm_provider=MockLLMProvider(),  # Use a mock LLM provider
            event_bus=roman_event_bus
        )
        
        self.framework_agent = agent
        self.event_adapter = event_adapter
        
        # Override event handling to forward to framework agent
        self._setup_event_forwarding()
    
    def _create_senator_data(self, agent: FrameworkBaseAgent) -> Dict[str, Any]:
        """
        Create Roman senator data from a Framework agent.
        
        Args:
            agent: The Framework agent
            
        Returns:
            Dict[str, Any]: Senator data
        """
        senator_data = {
            "id": agent.id,
            "name": agent.name,
        }
        
        # Add attributes from the framework agent
        for key, value in agent.attributes.items():
            if key not in senator_data:
                senator_data[key] = value
        
        # Provide defaults for required senator attributes
        if "faction" not in senator_data:
            senator_data["faction"] = "Unknown"
        
        if "oratory_skill" not in senator_data:
            senator_data["oratory_skill"] = 50
        
        if "political_influence" not in senator_data:
            senator_data["political_influence"] = 50
        
        return senator_data
    
    def _setup_event_forwarding(self) -> None:
        """Set up event forwarding to the Framework agent."""
        # Override the handle_event method to forward events
        original_handle_event = self.handle_event
        
        def forward_event(event):
            # Convert the event to Framework format
            framework_event = self.event_adapter.adapt(event)
            
            if framework_event:
                # Forward to Framework agent
                self.framework_agent.process_event(framework_event)
            
            # Also let the adapter handle the event normally
            original_handle_event(event)
        
        # Replace the method
        self.handle_event = forward_event