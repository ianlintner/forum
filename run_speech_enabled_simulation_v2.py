#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Run a Roman Senate simulation with forced LLM-powered speeches.

This script modifies the debate flow to explicitly force each senator to generate
a speech using the LLM provider.
"""

import asyncio
import sys
import logging
import random
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
from src.roman_senate_framework.domains.senate.events.senate_events import (
    create_debate_start_event, create_debate_end_event, create_speaker_change_event,
    SpeechEvent
)

# Set up web integration if available
try:
    from src.roman_senate.web.integration import setup_event_bridge
    has_web_integration = True
except ImportError:
    has_web_integration = False

class ForcedSpeechSimulation(SenateSimulation):
    """Modified simulation that forces senators to generate speeches."""
    
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
                    speech_event = SpeechEvent(
                        speaker_id=senator.id,
                        content=content,
                        topic=topic,
                        stance=stance,
                        source=senator.id
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

async def run_forced_speech_simulation():
    """Run a simulation with forced speech generation."""
    print("Starting forced speech simulation with OpenAI...")
    
    # Create LLM provider with correct model name parameter
    llm_provider = get_llm_provider(provider_type="openai", model_name="gpt-3.5-turbo")
    print(f"Created provider: {llm_provider.__class__.__name__}")
    
    # Create event bus
    event_bus = EventBus()
    
    # Connect to web socket if server is running
    if has_web_integration:
        try:
            print("Connecting to web server...")
            setup_event_bridge(event_bus)
            print("Connected to web server successfully")
        except Exception as e:
            print(f"Warning: Could not connect to web server: {e}")
    
    # Create simulation
    simulation = ForcedSpeechSimulation(
        num_senators=3,  # Fewer senators for faster results
        llm_provider=llm_provider,
        config={"topics": ["The expansion of Roman citizenship to Italian allies"]}
    )
    
    # Run the session
    print("Running simulation with forced speech generation...")
    results = await simulation.run_session(rounds_per_topic=1)  # Just one round for demonstration
    
    # Print results
    print("\nSimulation Results:")
    for topic_result in results:
        print(f"\nTopic: {topic_result['topic']}")
        print(f"Speeches: {topic_result['speeches']}")
        print(f"Reactions: {topic_result['reactions']}")
        print(f"Interjections: {topic_result['interjections']}")
    
    return results

if __name__ == "__main__":
    asyncio.run(run_forced_speech_simulation())