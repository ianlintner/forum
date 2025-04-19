#!/usr/bin/env python3
"""
Roman Senate Simulation
Event System Demo

This script demonstrates the event-driven architecture for the Roman Senate simulation.
It creates a simple debate with senators who react to speeches and interject.
"""

import asyncio
import logging
import random
import sys
from typing import Dict, List, Any

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

# Add parent directory to path to allow imports
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.roman_senate.core.events import (
    EventBus, 
    DebateEvent, 
    DebateEventType,
    SpeechEvent,
    ReactionEvent,
    InterjectionEvent,
    InterjectionType,
    DebateManager
)
from src.roman_senate.agents.event_driven_senator_agent import EventDrivenSenatorAgent
from src.roman_senate.utils.llm.mock_provider import MockLLMProvider

# Create mock senators
def create_mock_senators(count: int = 5) -> List[Dict[str, Any]]:
    """Create mock senator data for testing."""
    factions = ["Optimates", "Populares", "Equites"]
    senators = []
    
    for i in range(count):
        senators.append({
            "id": i,
            "name": f"Senator {chr(65 + i)}",  # A, B, C, etc.
            "faction": random.choice(factions),
            "rank": random.randint(1, 5),
            "influence": random.randint(1, 10),
            "oratory": random.randint(1, 10)
        })
    
    return senators

async def run_demo():
    """Run the event system demonstration."""
    # Create event bus
    event_bus = EventBus()
    
    # Create mock LLM provider
    llm_provider = MockLLMProvider()
    
    # Create mock game state
    game_state = {"calendar": {"year": -50, "month": 3, "day": 15}}
    
    # Create debate manager
    debate_manager = DebateManager(event_bus, game_state)
    
    # Create senators
    senator_data = create_mock_senators(5)
    
    # Create senator agents
    senator_agents = [
        EventDrivenSenatorAgent(senator, llm_provider, event_bus)
        for senator in senator_data
    ]
    
    # Set up a debate topic
    topic = "The expansion of Roman territories in Gaul"
    
    # Start the debate
    logging.info(f"Starting debate on: {topic}")
    await debate_manager.start_debate(topic, senator_data)
    
    # Let each senator speak
    for i, senator in enumerate(senator_data):
        logging.info(f"\n{'-'*40}\n{senator['name']} is speaking\n{'-'*40}")
        
        # Set as current speaker
        await debate_manager.next_speaker()
        
        # Generate a stance for the senator
        stance = random.choice(["support", "oppose", "neutral"])
        
        # Generate mock speech content
        latin_content = f"Latin speech by {senator['name']} on {topic} with {stance} stance."
        english_content = f"English speech by {senator['name']} on {topic}. This senator takes a {stance} position because of their faction's interests and personal beliefs."
        
        # Publish the speech event
        speech_event = await debate_manager.publish_speech(
            speaker=senator,
            topic=topic,
            latin_content=latin_content,
            english_content=english_content,
            stance=stance
        )
        
        # Wait for reactions and interjections
        await asyncio.sleep(1)
        
    # End the debate
    await debate_manager.end_debate()
    logging.info("Debate ended")
    
    # Print summary of events
    logging.info("\nEvent Summary:")
    for i, event in enumerate(event_bus.published_events):
        if isinstance(event, SpeechEvent):
            logging.info(f"Speech by {event.speaker['name']} ({event.stance})")
        elif isinstance(event, ReactionEvent):
            logging.info(f"  Reaction from {event.reactor['name']}: {event.reaction_type} - {event.content}")
        elif isinstance(event, InterjectionEvent):
            logging.info(f"  Interjection from {event.interjector['name']}: {event.interjection_type.value} - {event.english_content}")
        elif isinstance(event, DebateEvent):
            logging.info(f"Debate event: {event.debate_event_type.value}")

if __name__ == "__main__":
    asyncio.run(run_demo())