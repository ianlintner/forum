#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Integrated Roman Senate Server

This server combines the Roman Senate web interface with automatic
speech-enabled simulation that starts when users connect.
"""

import asyncio
import logging
import sys
import time
import random
import os
from typing import Optional, Dict, Any, List, Set, Tuple

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("senate_server.log"),
    ]
)
logger = logging.getLogger(__name__)

# Import the web server components
from src.roman_senate.web.server import (
    app, websocket_manager, EventSerializer, 
    WebSocketEventHandler, setup_event_handler
)

# Import the simulation components
from src.roman_senate.utils.llm.base import LLMProvider
from src.roman_senate.utils.llm.factory import get_llm_provider
from src.roman_senate.utils.portrait_generator import PortraitGenerator
from src.roman_senate_framework.domains.senate.simulation import SenateSimulation
from src.roman_senate_framework.domains.senate.agents.speech_enabled_senator import SpeechEnabledSenator
from src.agentic_game_framework.events.event_bus import EventBus
from src.roman_senate_framework.domains.senate.events.senate_events import (
    create_debate_start_event, create_debate_end_event, create_speaker_change_event,
    SpeechEvent
)
from src.roman_senate.web.integration import setup_event_bridge
from src.roman_senate.web.portrait_server import setup_portrait_endpoints
from src.roman_senate.web.portrait_testing import setup_portrait_testing_endpoints

# Import the forced speech simulation
class ForcedSpeechSimulation(SenateSimulation):
    """Modified simulation that forces senators to generate speeches."""
    
    def __init__(
        self,
        num_senators: int = 10,
        llm_provider: Optional[LLMProvider] = None,
        event_bus: Optional[EventBus] = None,
        portrait_generator: Optional[PortraitGenerator] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the Senate simulation with a custom event bus.
        
        Args:
            num_senators: Number of senators to create
            llm_provider: LLM provider for generating content
            event_bus: Optional external event bus to use instead of creating one
            config: Optional configuration parameters
        """
        # Initialize parent without the event_bus parameter
        super().__init__(
            num_senators=num_senators,
            llm_provider=llm_provider,
            config=config
        )
        
        # Set up portrait generator
        self.portrait_generator = portrait_generator
        
        # Replace the parent's event bus with our custom one if provided
        if event_bus is not None:
            # Store the original event bus logging handler
            original_log_handler = self._log_event
            
            # Replace the event bus
            self.event_bus = event_bus
            
            # Make sure our _log_event method is registered with the new event bus
            self.event_bus.add_filter(original_log_handler)
            
            logger.info("Using custom event bus for simulation")
    
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
            
            # Generate portrait if we have a portrait generator
            portrait_url = None
            if self.portrait_generator:
                try:
                    # Generate portrait if it doesn't exist yet
                    if not self.portrait_generator.portrait_exists(name, faction):
                        self.portrait_generator.generate_portrait(name, faction)
                    
                    # Get the URL for the portrait
                    portrait_url = self.portrait_generator.get_portrait_url(name, faction)
                    logger.info(f"Portrait URL for {name}: {portrait_url}")
                except Exception as e:
                    logger.error(f"Error generating portrait for {name}: {e}")
            
            # Create speech-enabled senator agent
            senator = SpeechEnabledSenator(
                name=name,
                faction=faction,
                rank=rank,
                llm_provider=self.llm_provider,
                event_bus=self.event_bus
            )
            
            # Add portrait URL to senator state
            if portrait_url:
                senator.state["portrait_url"] = portrait_url
            # Add to list and register with agent manager
            self.senators.append(senator)
            self.agent_manager.add_agent(senator)
            
            logger.info(f"Created speech-enabled {faction} senator: {name} (Rank {rank})")
            
    async def run_debate(self, topic: str, rounds: int = 3) -> Dict[str, Any]:
        """
        OVERRIDDEN: Run a debate with forced speech generation.
        
        Args:
            topic: The topic to debate
            rounds: Number of debate rounds
            
        Returns:
            Dict[str, Any]: Results of the debate
        """
        logger.info(f"Starting debate on topic: {topic}")
        
        # Create and publish debate start event
        debate_start = create_debate_start_event(topic, source_id=self.id)
        self.event_bus.publish(debate_start)
        
        # Ensure all senators have a stance
        for senator in self.senators:
            if topic not in senator.topic_stances:
                stance = senator.decide_stance(topic)
                logger.info(f"Senator {senator.name} ({senator.faction}) decided to {stance} topic: {topic}")
        
        # Run debate rounds
        for round_num in range(rounds):
            logger.info(f"Debate round {round_num + 1}")
            
            # Shuffle the senators for this round
            debating_senators = list(self.senators)
            random.shuffle(debating_senators)
            
            # Force each senator to speak
            for senator in debating_senators:
                # Update the senator's state to indicate they should speak
                senator.state["debate_in_progress"] = True
                senator.state["active_debate_topic"] = topic
                senator.state["current_speaker"] = senator.id
                
                # Announce speaker change
                speaker_change = create_speaker_change_event(
                    topic=topic,
                    speaker_id=senator.id,
                    source_id=self.id
                )
                self.event_bus.publish(speaker_change)
                
                # Generate a speech using LLM
                # Get or decide stance on the topic
                stance = senator.topic_stances.get(topic, "neutral")
                
                logger.info(f"Forcing speech from {senator.name} ({senator.faction}, {stance}) on topic: {topic}")
                
                # Generate speech content using the LLM
                try:
                    # Generate speech using the LLM
                    prompt = f"""Generate a 3-5 sentence speech for Roman Senator {senator.name} of the {senator.faction} faction who {stance}s the topic: "{topic}".
                    
                    The speech should reflect the senator's faction ({senator.faction}), rank ({senator.rank}), and stance ({stance}).
                    
                    The speech should include appropriate Latin phrases, rhetorical devices, and references to Roman history and politics.
                    
                    SPEECH:"""
                    
                    # Use sync version for compatibility, but this should be async in production
                    content = senator.llm_provider.generate_completion(prompt)
                    logger.info(f"Generated LLM speech for {senator.name}")
                    
                    # Create and publish the speech event
                    # Include portrait URL in speech event if available
                    portrait_url = senator.state.get("portrait_url")
                    
                    # Create additional data for the speech event
                    speech_data = {
                        "senator_name": senator.name,
                        "faction": senator.faction,
                        "rank": senator.rank
                    }
                    
                    # Add portrait URL if available
                    if portrait_url:
                        speech_data["portrait_url"] = portrait_url
                    
                    speech_event = SpeechEvent(
                        speaker_id=senator.id,
                        content=content,
                        topic=topic,
                        stance=stance,
                        source=senator.id,
                        data=speech_data
                    )
                    
                    self.event_bus.publish(speech_event)
                    logger.info(f"Published speech from {senator.name}")
                    
                    # Update stats for the senator
                    import time
                    senator.state["last_speech_time"] = time.time()
                    senator.state["speeches_given"] = senator.state.get("speeches_given", 0) + 1
                    
                    # Add to event history
                    self.event_history.append({
                        "id": speech_event.get_id(),
                        "type": "senate.speech",
                        "timestamp": speech_event.timestamp.isoformat(),
                        "source": speech_event.source,
                        "data": {
                            "topic": topic,
                            "stance": stance,
                            "content": content
                        }
                    })
                    
                except Exception as e:
                    logger.error(f"Error generating speech: {e}")
                
                # Wait for reactions and interjections
                await asyncio.sleep(2)
            
            # Short pause between rounds
            await asyncio.sleep(1)
        
        # Create and publish debate end event
        debate_end = create_debate_end_event(topic, source_id=self.id)
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


class IntegratedSenateServer:
    """
    Enhanced Roman Senate server that automatically starts simulations
    when clients connect to the WebSocket.
    """
    
    def __init__(
        self,
        num_senators: int = 4,
        debate_rounds: int = 2,
        auto_start_delay: float = 3.0,
        provider_type: str = "openai",
        model_name: str = "gpt-3.5-turbo",
        portraits_dir: str = "portraits"
    ):
        """
        Initialize the integrated server.
        
        Args:
            num_senators: Number of senators in the simulation
            debate_rounds: Number of debate rounds per topic
            auto_start_delay: Delay in seconds before starting a simulation after a connection
            provider_type: LLM provider type
            model_name: LLM model name
        """
        self.num_senators = num_senators
        self.debate_rounds = debate_rounds
        self.auto_start_delay = auto_start_delay
        self.provider_type = provider_type
        self.model_name = model_name
        self.portraits_dir = portraits_dir
        
        # Flag to track if a simulation is already running
        self.simulation_running = False
        
        # Create event bus for simulation events
        self.event_bus = EventBus()
        
        # Set up LLM provider
        self.llm_provider = get_llm_provider(
            provider_type=provider_type,
            model_name=model_name
        )
        
        # Set up portrait generator
        self.portrait_generator = PortraitGenerator(
            portraits_dir=portraits_dir,
            model="dall-e-3"  # Use DALL-E 3 for high-quality portraits
        )
        
        # Set up a custom websocket manager that triggers simulations
        self.setup_websocket_handler()
        
        # Set up event bridge to forward events to WebSocket clients
        setup_event_bridge(self.event_bus)
        
        logger.info(f"Integrated Senate Server initialized with {num_senators} senators and {debate_rounds} debate rounds")
    
    def setup_websocket_handler(self):
        """Set up custom WebSocket connection handler to detect new connections."""
        # Store the original connect method
        original_connect = websocket_manager.connect
        
        # Define a new connect method that starts a simulation after accepting the connection
        async def enhanced_connect(websocket: WebSocket) -> int:
            # Call the original connect method
            connection_id = await original_connect(websocket)
            
            # Log connection
            logger.info(f"Client connected (ID: {connection_id}). Starting simulation soon...")
            
            # Schedule simulation start after a delay
            asyncio.create_task(self.auto_start_simulation())
            
            return connection_id
        
        # Replace the original connect method with our enhanced version
        websocket_manager.connect = enhanced_connect
        
        logger.info("Enhanced WebSocket connection handler set up")
    
    async def auto_start_simulation(self):
        """Automatically start a simulation after a brief delay."""
        # Wait for configured delay
        await asyncio.sleep(self.auto_start_delay)
        
        # Check if a simulation is already running
        if self.simulation_running:
            logger.info("Simulation already running - not starting a new one")
            return
        
        # Check if we have any connections
        if not websocket_manager.active_connections:
            logger.info("No active connections - not starting simulation")
            return
        
        # Set the flag to prevent multiple simulations
        self.simulation_running = True
        
        try:
            # Notify clients that a simulation is starting
            await websocket_manager.broadcast(
                '{"type": "simulation_auto_starting", "message": "Automatically starting Roman Senate simulation", '
                f'"timestamp": "{time.strftime("%Y-%m-%dT%H:%M:%S")}", '
                f'"data": {{"num_senators": {self.num_senators}, "debate_rounds": {self.debate_rounds}}}}}'
            )
            
            # Run the simulation
            logger.info(f"Auto-starting simulation with {self.num_senators} senators and {self.debate_rounds} debate rounds")
            simulation_task = asyncio.create_task(self.run_simulation())
            
            # Add cleanup when done
            simulation_task.add_done_callback(lambda _: self.cleanup_simulation())
            
        except Exception as e:
            logger.error(f"Error starting simulation: {e}")
            self.simulation_running = False
    
    def cleanup_simulation(self):
        """Reset the simulation running flag when a simulation finishes."""
        self.simulation_running = False
        logger.info("Simulation completed - ready to start a new one on next connection")
    
    async def run_simulation(self) -> Dict[str, Any]:
        """Run a speech-enabled simulation."""
        logger.info("Starting speech-enabled simulation...")
        
        # Define debate topics
        topics = [
            "The expansion of Roman citizenship to Italian allies",
            "Reforming the grain distribution system",
            "Increasing the size of the Roman military"
        ]
        
        # Create simulation
        simulation = ForcedSpeechSimulation(
            num_senators=self.num_senators,
            llm_provider=self.llm_provider,
            event_bus=self.event_bus,
            portrait_generator=self.portrait_generator,
            config={"topics": topics[:2]}  # Choose 2 topics for faster demo
        )
        
        # Run the session
        logger.info("Running Senate simulation session...")
        results = await simulation.run_session(rounds_per_topic=self.debate_rounds)
        
        # Log results
        logger.info(f"Simulation completed with results: {results}")
        
        return results


async def run_integrated_server(host: str = "0.0.0.0", port: int = 8000):
    """
    Run the integrated Roman Senate server.
    
    Args:
        host: Host to bind to
        port: Port to bind to
    """
    # Create the integrated server
    integrated_server = IntegratedSenateServer(
        num_senators=4,  # Using 4 senators for a balanced debate
        debate_rounds=2,  # 2 rounds per topic for reasonable length
        auto_start_delay=3.0,  # Wait 3 seconds after connection before starting
        provider_type="openai",
        model_name="gpt-3.5-turbo"
    )
    
    # Set simulation attribute on app to access simulation state
    setattr(app, "integrated_server", integrated_server)
    
    # Define a flag on the app to track simulation status
    setattr(app, "simulation_running", False)
    
    # Set up portrait endpoints with absolute path
    portraits_dir = os.path.abspath(integrated_server.portraits_dir)
    logger.info(f"Setting up portrait endpoints with directory: {portraits_dir}")
    setup_portrait_endpoints(app, portraits_dir=portraits_dir)
    setup_portrait_testing_endpoints(app, integrated_server.portrait_generator)
    
    # Also mount portraits directly as static files as a backup
    app.mount("/portraits", StaticFiles(directory=portraits_dir), name="portraits_direct")
    
    # Start the FastAPI server
    config = uvicorn.Config(app, host=host, port=port)
    server = uvicorn.Server(config)
    
    logger.info(f"Starting Integrated Roman Senate Server on http://{host}:{port}")
    await server.serve()


def run_server():
    """
    Run the integrated server (synchronous wrapper for command-line use)
    """
    logger.info("Starting Integrated Roman Senate Server...")
    asyncio.run(run_integrated_server())


if __name__ == "__main__":
    # Run the integrated server
    run_server()