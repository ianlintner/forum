"""
Roman Senate Simulation for Agentic Game Framework.

This module implements the simulation runner for the Roman Senate domain.
"""

import asyncio
import logging
import random
from typing import Any, Dict, List, Optional, Set, Tuple

from src.agentic_game_framework.events.event_bus import EventBus
from src.agentic_game_framework.agents.agent_manager import AgentManager

from src.roman_senate.utils.llm.base import LLMProvider
from src.roman_senate_framework.domains.senate.agents.senator_agent import SenatorAgent
from src.roman_senate_framework.domains.senate.events.senate_events import (
    create_debate_start_event, create_debate_end_event, create_speaker_change_event
)
from src.roman_senate_framework.domains.senate.domain import register_senate_domain

logger = logging.getLogger(__name__)


class SenateSimulation:
    """
    Simulation runner for the Roman Senate domain.
    
    This class manages the simulation of Senate sessions, including debates,
    speeches, and voting.
    """
    
    def __init__(
        self,
        num_senators: int = 10,
        llm_provider: Optional[LLMProvider] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the Senate simulation.
        
        Args:
            num_senators: Number of senators to create
            llm_provider: LLM provider for generating content
            config: Optional configuration parameters
        """
        self.num_senators = num_senators
        self.llm_provider = llm_provider
        self.config = config or {}
        # Create and initialize the Senate domain
        self.senate_domain = register_senate_domain()
        
        
        # Create the event bus
        self.event_bus = EventBus()
        
        # Create the agent manager
        self.agent_manager = AgentManager()
        
        # Initialize senators
        self.senators = []
        
        # Default topics
        self.topics = self.config.get("topics", [
            "The expansion of Roman citizenship to Italian allies",
            "Funding for new aqueducts in Rome",
            "Military reforms proposed by the consul",
            "Land redistribution to veterans",
            "Grain subsidies for the urban poor"
        ])
        
        # Event history for tracking
        self.event_history = []
        
        # Subscribe to all events for logging
        self.event_bus.add_filter(self._log_event)
    
    def _log_event(self, event: Any) -> bool:
        """
        Log events and store in history.
        
        Args:
            event: The event to log
            
        Returns:
            True to allow event processing to continue
        """
        # Format and store the event
        formatted_event = {
            "id": event.get_id(),
            "type": event.event_type,
            "timestamp": event.timestamp.isoformat(),
            "source": event.source,
            "target": event.target,
            "data": event.data
        }
        self.event_history.append(formatted_event)
        
        # Log the event
        logger.info(f"Event: {event.event_type} from {event.source}")
        
        # Always allow event processing to continue
        return True
    
    def initialize_senators(self) -> None:
        """Initialize senator agents."""
        # Senator factions
        factions = self.config.get("factions", ["Optimates", "Populares", "Neutral"])
        
        # Senator names (could be loaded from a file or generated)
        praenomina = ["Marcus", "Gaius", "Lucius", "Publius", "Quintus", "Titus", "Gnaeus", "Sextus", "Aulus", "Decimus"]
        nomina = ["Cornelius", "Julius", "Claudius", "Valerius", "Fabius", "Aemilius", "Calpurnius", "Licinius", "Junius", "Domitius"]
        cognomina = ["Scipio", "Caesar", "Cicero", "Cato", "Brutus", "Sulla", "Crassus", "Rufus", "Longus", "Magnus"]
        
        # Create senators
        for i in range(self.num_senators):
            # Generate senator name
            if i < len(praenomina) and i < len(nomina) and i < len(cognomina):
                name = f"{praenomina[i]} {nomina[i]} {cognomina[i]}"
            else:
                name = f"Senator {chr(65 + i)}"  # A, B, C, etc.
            
            # Generate senator attributes
            faction = random.choice(factions)
            rank = random.randint(1, 5)
            
            # Create senator agent
            senator = SenatorAgent(
                name=name,
                faction=faction,
                rank=rank,
                llm_provider=self.llm_provider,
                event_bus=self.event_bus
            )
            # Add to list and register with agent manager
            self.senators.append(senator)
            self.agent_manager.add_agent(senator)
            
            
            logger.info(f"Created {faction} senator: {name} (Rank {rank})")
    
    async def run_debate(self, topic: str, rounds: int = 3) -> Dict[str, Any]:
        """
        Run a debate on a specific topic.
        
        Args:
            topic: The topic to debate
            rounds: Number of debate rounds
            
        Returns:
            Dict[str, Any]: Results of the debate
        """
        logger.info(f"Starting debate on topic: {topic}")
        
        # Create and publish debate start event
        debate_start = create_debate_start_event(topic)
        self.event_bus.publish(debate_start)
        
        # Wait for agents to process the event
        await asyncio.sleep(1)
        
        # Run debate rounds
        for round_num in range(rounds):
            logger.info(f"Debate round {round_num + 1}")
            
            # Let each senator speak in turn
            for senator in self.senators:
                # Announce speaker change
                speaker_change = create_speaker_change_event(
                    topic=topic,
                    speaker_id=senator.id
                )
                self.event_bus.publish(speaker_change)
                
                # Wait for agents to process the event
                await asyncio.sleep(0.5)
                
                # Generate actions for all agents
                events = self.agent_manager.update_all()
                for event in events:
                    self.event_bus.publish(event)
                
                # Wait for reactions and interjections
                await asyncio.sleep(2)
            
            # Short pause between rounds
            await asyncio.sleep(1)
        
        # Create and publish debate end event
        debate_end = create_debate_end_event(topic)
        self.event_bus.publish(debate_end)
        
        # Wait for agents to process the event
        await asyncio.sleep(1)
        
        logger.info(f"Debate on {topic} concluded")
        
        # Collect results
        results = {
            "topic": topic,
            "rounds": rounds,
            "speeches": self._count_events_by_type("senate.speech"),
            "reactions": self._count_events_by_type("senate.reaction"),
            "interjections": self._count_events_by_type("senate.interjection"),
            "relationships": self._count_events_by_type("senate.relationship"),
            "stances": self._collect_senator_stances(topic)
        }
        
        return results
    
    def _count_events_by_type(self, event_type: str) -> int:
        """
        Count events of a specific type.
        
        Args:
            event_type: The event type to count
            
        Returns:
            int: Number of events of that type
        """
        return sum(1 for e in self.event_history if e["type"] == event_type)
    
    def _collect_senator_stances(self, topic: str) -> Dict[str, str]:
        """
        Collect senator stances on a topic.
        
        Args:
            topic: The topic to collect stances for
            
        Returns:
            Dict[str, str]: Map of senator IDs to stances
        """
        stances = {}
        for senator in self.senators:
            if topic in senator.topic_stances:
                stances[senator.id] = senator.topic_stances[topic]
        return stances
    
    async def run_session(self, topics: Optional[List[str]] = None, rounds_per_topic: int = 3) -> List[Dict[str, Any]]:
        """
        Run a full Senate session with multiple debates.
        
        Args:
            topics: Optional list of topics to debate (uses default if None)
            rounds_per_topic: Number of debate rounds per topic
            
        Returns:
            List[Dict[str, Any]]: Results for each debate
        """
        logger.info("Starting Roman Senate session")
        
        # Initialize senators if not already done
        if not self.senators:
            self.initialize_senators()
        
        # Use provided topics or default
        debate_topics = topics or self.topics
        
        # Run debates for each topic
        results = []
        for topic in debate_topics:
            topic_results = await self.run_debate(topic, rounds_per_topic)
            results.append(topic_results)
        
        # Print summary
        self.print_summary()
        
        logger.info("Roman Senate session completed")
        return results
    
    def print_summary(self) -> None:
        """Print a summary of the simulation."""
        logger.info("=== Simulation Summary ===")
        
        # Count events by type
        event_counts = {}
        for event in self.event_history:
            event_type = event["type"]
            event_counts[event_type] = event_counts.get(event_type, 0) + 1
        
        # Print event counts
        logger.info("Event counts:")
        for event_type, count in event_counts.items():
            logger.info(f"  {event_type}: {count}")
        
        # Print senator participation
        logger.info("Senator participation:")
        for senator in self.senators:
            # Count speeches, reactions, and interjections
            speeches = sum(1 for e in self.event_history if e["type"] == "senate.speech" and e["source"] == senator.id)
            reactions = sum(1 for e in self.event_history if e["type"] == "senate.reaction" and e["source"] == senator.id)
            interjections = sum(1 for e in self.event_history if e["type"] == "senate.interjection" and e["source"] == senator.id)
            
            logger.info(f"  {senator.name} ({senator.faction}): {speeches} speeches, {reactions} reactions, {interjections} interjections")


async def run_simulation(
    num_senators: int = 10,
    topics: Optional[List[str]] = None,
    rounds_per_topic: int = 3,
    llm_provider: Optional[LLMProvider] = None,
    config: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Run a Roman Senate simulation.
    
    Args:
        num_senators: Number of senators to simulate
        topics: Optional list of topics to debate
        rounds_per_topic: Number of debate rounds per topic
        llm_provider: Optional LLM provider for generating content
        config: Optional configuration parameters
        
    Returns:
        List[Dict[str, Any]]: Results for each debate
    """
    # Create and run the simulation
    simulation = SenateSimulation(
        num_senators=num_senators,
        llm_provider=llm_provider,
        config=config
    )
    
    # Run the session
    results = await simulation.run_session(topics, rounds_per_topic)
    
    return results