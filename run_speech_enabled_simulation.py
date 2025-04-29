#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Run a Roman Senate simulation with LLM-powered speeches.

This script runs the simulation with speech-enabled senators that actually
use the LLM provider to generate speech content.
"""

import asyncio
import sys
import logging
from typing import Optional, List, Dict, Any

# Configure logging
from src.roman_senate.utils.logging_utils import setup_logging
logger = setup_logging()

# Add console handler for better visibility
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Import the needed components
from src.roman_senate.utils.llm.factory import get_llm_provider
from src.roman_senate_framework.domains.senate.simulation import SenateSimulation
from src.roman_senate_framework.domains.senate.agents.speech_enabled_senator import SpeechEnabledSenator
from src.agentic_game_framework.events.event_bus import EventBus

# Set up web integration if available
try:
    from src.roman_senate.web.integration import setup_event_bridge
    has_web_integration = True
except ImportError:
    has_web_integration = False

class SpeechEnabledSimulation(SenateSimulation):
    """Modified simulation that uses speech-enabled senators."""
    
    def initialize_senators(self) -> None:
        """Override to use speech-enabled senators."""
        # Senator factions
        factions = self.config.get("factions", ["Optimates", "Populares", "Neutral"])
        
        # Senator names
        praenomina = ["Marcus", "Gaius", "Lucius", "Publius", "Quintus"]
        nomina = ["Cornelius", "Julius", "Claudius", "Valerius", "Fabius"]
        cognomina = ["Scipio", "Caesar", "Cicero", "Cato", "Brutus"]
        
        # Create senators
        for i in range(self.num_senators):
            # Generate senator name
            if i < len(praenomina) and i < len(nomina) and i < len(cognomina):
                name = f"{praenomina[i]} {nomina[i]} {cognomina[i]}"
            else:
                name = f"Senator {chr(65 + i)}"  # A, B, C, etc.
            
            # Generate senator attributes
            faction = factions[i % len(factions)]
            rank = (i % 5) + 1  # Rank 1-5
            
            # Create speech-enabled senator agent
            senator = SpeechEnabledSenator(
                name=name,
                faction=faction,
                rank=rank,
                llm_provider=self.llm_provider,
                event_bus=self.event_bus
            )
            # Add to list and register with agent manager
            self.senators.append(senator)
            self.agent_manager.add_agent(senator)
            
            logger.info(f"Created speech-enabled {faction} senator: {name} (Rank {rank})")

async def run_speech_simulation(
    num_senators: int = 4,
    topics: Optional[List[str]] = None,
    rounds_per_topic: int = 2,
    provider_type: str = "openai",
    model_name: str = "gpt-3.5-turbo"
) -> List[Dict[str, Any]]:
    """
    Run a Roman Senate simulation with speech-enabled senators.
    
    Args:
        num_senators: Number of senators to simulate
        topics: Optional list of topics to debate
        rounds_per_topic: Number of debate rounds per topic
        provider_type: LLM provider type ("openai", "ollama", or "mock")
        model_name: Model name to use
        
    Returns:
        List[Dict[str, Any]]: Results for each debate
    """
    print(f"Starting speech-enabled simulation with {provider_type} provider...")
    
    # Create LLM provider
    llm_provider = get_llm_provider(provider_type=provider_type, model_name=model_name)
    print(f"Created provider: {llm_provider.__class__.__name__}")
    
    # Create event bus
    event_bus = EventBus()
    
    # Connect to web socket if server is running and integration is available
    if has_web_integration:
        try:
            print("Connecting to web server...")
            setup_event_bridge(event_bus)
            print("Connected to web server successfully")
        except Exception as e:
            print(f"Warning: Could not connect to web server: {e}")
    
    # Default topics if none provided
    if not topics:
        topics = ["The expansion of Roman citizenship to Italian allies"]
    
    # Create and run the simulation
    simulation = SpeechEnabledSimulation(
        num_senators=num_senators,
        llm_provider=llm_provider,
        config={"topics": topics}
    )
    
    # Run the session
    print(f"Running simulation with {num_senators} senators on {len(topics)} topics...")
    results = await simulation.run_session(topics, rounds_per_topic)
    
    # Print results
    print("\nSimulation Results:")
    for topic_result in results:
        print(f"\nTopic: {topic_result['topic']}")
        print(f"Speeches: {topic_result['speeches']}")
        print(f"Reactions: {topic_result['reactions']}")
        print(f"Interjections: {topic_result['interjections']}")
        
    return results

if __name__ == "__main__":
    asyncio.run(run_speech_simulation())