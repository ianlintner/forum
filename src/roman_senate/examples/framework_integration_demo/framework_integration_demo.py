"""
Framework Integration Demo for Roman Senate.

This module demonstrates the integration between the Roman Senate simulation
and the agentic_game_framework architecture, showcasing:
1. Event bridging between both systems
2. Agent bridging between both systems
3. Memory integration between systems
4. How relationships are maintained across system boundaries

Part of the Migration Plan: Phase 4 - Integration Layer.
"""

import logging
import time
from datetime import datetime
from typing import Dict, Any, List, Optional

# Roman Senate imports
from roman_senate.core.events.base import BaseEvent as RomanBaseEvent
from roman_senate.core.events.event_bus import EventBus as RomanEventBus
from roman_senate.agents.enhanced_senator_agent import EnhancedSenatorAgent
from roman_senate.utils.llm.mock import MockLLMProvider
from roman_senate.agents.relationship_manager import RelationshipManager

# agentic_game_framework imports
from agentic_game_framework.events.base import BaseEvent as FrameworkBaseEvent
from agentic_game_framework.events.event_bus import EventBus as FrameworkEventBus
from agentic_game_framework.agents.base_agent import BaseAgent as FrameworkBaseAgent
from agentic_game_framework.memory.memory_interface import MemoryItem

# Integration layer imports
from roman_senate.integration.framework_events import (
    EventBridgeAdapter,
    RomanToFrameworkEventAdapter,
    FrameworkToRomanEventAdapter
)
from roman_senate.integration.framework_agents import (
    AgentBridgeAdapter,
    RomanToFrameworkAgentAdapter,
    FrameworkToRomanAgentAdapter
)
from roman_senate.integration.utils import (
    get_memory_adapter,
    create_bidirectional_memory_adapter
)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SimpleFrameworkAgent(FrameworkBaseAgent):
    """
    Simple agent implementation for the agentic_game_framework.
    
    This agent logs events it receives and can generate simple actions.
    """
    
    def __init__(self, name: str, agent_id: Optional[str] = None):
        """Initialize a new simple agent."""
        super().__init__(
            name=name,
            agent_id=agent_id,
            attributes={"type": "simple_agent", "faction": "Optimates"}
        )
        # Subscribe to all debate events
        self.subscribe_to_event("debate_started")
        self.subscribe_to_event("speech_started")
        self.subscribe_to_event("vote_started")
        self.last_processed_event = None
    
    def process_event(self, event: FrameworkBaseEvent) -> None:
        """Process an incoming event."""
        logger.info(f"[FRAMEWORK AGENT] {self.name} received event: {event.event_type}")
        self.last_processed_event = event
        
        # Update state based on event
        if event.event_type == "debate_started":
            self.update_state({"debate_topic": event.data.get("topic", "Unknown topic")})
        elif event.event_type == "speech_started":
            self.update_state({"current_speaker": event.source})
    
    def generate_action(self) -> Optional[FrameworkBaseEvent]:
        """Generate an action based on the agent's current state."""
        if self.last_processed_event and self.last_processed_event.event_type == "speech_started":
            # React to someone's speech
            return FrameworkBaseEvent(
                event_type="reaction",
                source=self.id,
                target=self.state.get("current_speaker"),
                data={
                    "reaction_type": "applause" if "Optimates" in self.last_processed_event.data.get("faction", "") else "disapproval",
                    "strength": 0.7
                }
            )
        return None


def create_roman_senator(name: str, faction: str) -> EnhancedSenatorAgent:
    """Create a Roman senator agent."""
    senator_data = {
        "name": name,
        "faction": faction,
        "age": 45,
        "wealth": 80,
        "military_experience": 10,
        "oratory_skill": 75,
        "political_influence": 70
    }
    
    # Create event bus and other components
    event_bus = RomanEventBus()
    llm_provider = MockLLMProvider()
    relationship_manager = RelationshipManager(event_bus)
    
    # Create the senator agent
    senator = EnhancedSenatorAgent(
        senator=senator_data,
        llm_provider=llm_provider,
        event_bus=event_bus,
        relationship_manager=relationship_manager
    )
    
    return senator


def demonstrate_integration():
    """
    Demonstrate the integration between Roman Senate and agentic_game_framework.
    """
    logger.info("Starting Framework Integration Demo")
    
    # Create event buses for both systems
    roman_event_bus = RomanEventBus()
    framework_event_bus = FrameworkEventBus()
    
    # Create event mapping (Roman event types -> Framework event types)
    event_mappings = {
        "debate_started": "debate_started",
        "debate_ended": "debate_ended",
        "speech_started": "speech_started",
        "speech_ended": "speech_ended",
        "vote_started": "vote_started",
        "vote_ended": "vote_ended",
        "reaction": "reaction"
    }
    
    # Create event bridge
    logger.info("Setting up event bridge between systems")
    event_bridge = EventBridgeAdapter(
        roman_event_bus=roman_event_bus,
        framework_event_bus=framework_event_bus,
        event_type_mappings=event_mappings
    )
    
    # Create agent bridge
    logger.info("Setting up agent bridge between systems")
    agent_bridge = AgentBridgeAdapter(
        roman_event_bus=roman_event_bus,
        framework_event_bus=framework_event_bus,
        event_type_mappings=event_mappings
    )
    
    # Create Roman senators
    logger.info("Creating Roman Senate agents")
    cicero = create_roman_senator("Cicero", "Optimates")
    caesar = create_roman_senator("Caesar", "Populares")
    
    # Create Framework agents
    logger.info("Creating agentic_game_framework agents")
    brutus = SimpleFrameworkAgent(name="Brutus")
    cato = SimpleFrameworkAgent(name="Cato")
    
    # Register agents with the bridge
    logger.info("Registering agents with the bridge")
    framework_cicero = agent_bridge.register_roman_agent(cicero)
    framework_caesar = agent_bridge.register_roman_agent(caesar)
    
    roman_brutus = agent_bridge.register_framework_agent(brutus)
    roman_cato = agent_bridge.register_framework_agent(cato)
    
    # Create relationships between agents
    logger.info("Creating relationships between agents")
    cicero.create_relationship(
        other_senator_id=caesar.senator["id"],
        relationship_type="political",
        strength=-0.7  # Cicero opposes Caesar
    )
    
    cicero.create_relationship(
        other_senator_id=roman_brutus.senator["id"],
        relationship_type="political",
        strength=0.8  # Cicero allies with Brutus
    )
    
    # Setup memory integration
    logger.info("Setting up memory integration")
    cicero_memory_adapter = get_memory_adapter(cicero.memory)
    
    # Demonstrate events flowing between systems
    logger.info("\n\n--- DEMONSTRATING EVENT FLOW ---\n")
    
    # Starting a debate (from Roman system)
    logger.info("Starting a debate from Roman system")
    debate_event = RomanBaseEvent(
        event_type="debate_started",
        source="consul",
        data={
            "topic": "Should we grant Caesar extended command in Gaul?",
            "importance": "high"
        }
    )
    roman_event_bus.publish(debate_event)
    
    # Allow time for event propagation and processing
    time.sleep(0.5)
    
    # Check that Framework agents received the event
    logger.info(f"Brutus state after debate started: {brutus.get_state()}")
    
    # Speech event (from Framework system)
    logger.info("\nStarting a speech from Framework system")
    speech_event = FrameworkBaseEvent(
        event_type="speech_started",
        source=brutus.id,
        data={
            "topic": "Should we grant Caesar extended command in Gaul?",
            "stance": "against",
            "faction": "Optimates"
        }
    )
    framework_event_bus.publish(speech_event)
    
    # Allow time for event propagation and processing
    time.sleep(0.5)
    
    # Demonstrate memory sharing
    logger.info("\n\n--- DEMONSTRATING MEMORY SHARING ---\n")
    
    # Add memory to Framework agent
    memory_item = MemoryItem(
        memory_id="memory_1",
        timestamp=datetime.now().timestamp(),
        content="Caesar aims to gain more power through his conquests in Gaul.",
        importance=0.9,
        associations={"person": "Caesar", "topic": "Gaul"}
    )
    
    # Add to Framework agent's memory and sync to Roman agent
    logger.info("Adding memory to Framework agent and syncing to Roman agent")
    cicero_memory_adapter.add_memory(memory_item)
    
    # Query the memory from Roman agent
    logger.info("Querying memory from Roman agent")
    roman_memories = cicero.memory.query_memories(
        query={"keyword": "Caesar"}
    )
    
    for memory in roman_memories:
        logger.info(f"Retrieved memory: {memory}")
    
    # Demonstrate relationship queries
    logger.info("\n\n--- DEMONSTRATING RELATIONSHIP INTEGRATION ---\n")
    
    # Check relationships from Roman agent
    cicero_allies = cicero.get_allies()
    cicero_rivals = cicero.get_rivals()
    
    logger.info(f"Cicero's allies: {cicero_allies}")
    logger.info(f"Cicero's rivals: {cicero_rivals}")
    
    # Complete demonstration
    logger.info("\n\nFramework Integration Demo completed successfully!")


if __name__ == "__main__":
    demonstrate_integration()