#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Temporary fix script to run OpenAI-powered simulation.
This bypasses the parameter name mismatch between CLI and OpenAIProvider.
"""

import asyncio
import os
import logging
import sys
from src.roman_senate.utils.llm.factory import get_llm_provider
from src.roman_senate_framework.domains.senate.simulation import run_simulation
from src.roman_senate.utils.logging_utils import setup_logging

# Set up logging
logger = setup_logging(log_level="DEBUG")

# Add a print handler to see output in real-time
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

async def run_fixed_simulation():
    print("Starting OpenAI-powered simulation...")
    
    # Create provider with the correct parameter name (model_name not model)
    provider = get_llm_provider(provider_type="openai", model_name="gpt-3.5-turbo")
    print(f"Created provider: {provider.__class__.__name__}")
    
    # Create event bus (if needed)
    from src.agentic_game_framework.events.event_bus import EventBus
    event_bus = EventBus() 
    
    # Connect to web socket if server is running
    try:
        print("Attempting to connect simulation to running web server...")
        from src.roman_senate.web.integration import setup_event_bridge
        setup_event_bridge(event_bus)
        print("Connected to web server successfully")
    except Exception as e:
        print(f"Warning: Could not connect to web server: {e}")
    
    # Run the simulation with the provider
    print("Running simulation...")
    results = await run_simulation(
        num_senators=4,
        rounds_per_topic=2,
        topics=["The expansion of Roman citizenship to Italian allies"],
        llm_provider=provider
    )
    
    # Print results
    print("\nSimulation Results:")
    for topic_result in results:
        print(f"\nTopic: {topic_result['topic']}")
        print(f"Speeches: {topic_result['speeches']}")
        print(f"Reactions: {topic_result['reactions']}")
        print(f"Interjections: {topic_result['interjections']}")
    
    return results

if __name__ == "__main__":
    # Run the fixed simulation
    asyncio.run(run_fixed_simulation())