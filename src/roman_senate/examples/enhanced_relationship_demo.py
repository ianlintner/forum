#!/usr/bin/env python3
"""
Roman Senate AI Game
Enhanced Relationship System Integration Demo

This script demonstrates the integration of the relationship system with the event system,
memory persistence, and enhanced senator agent features. It showcases:

1. Setting up a complete simulation environment with multiple senators
2. Creating initial relationships between senators with different dimensions
3. Simulating events that trigger relationship changes
4. Showing how senators' decisions change based on relationships
5. Demonstrating the persistence of relationships across simulated time periods
6. Illustrating relationship decay over time and how it affects decisions
7. Logging key events and relationship changes for easier tracking
"""

import asyncio
import logging
import datetime
import os
import random
import sys
from typing import Dict, List, Any, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Import required modules
from ..utils.llm.base import LLMProvider
from ..core.events import (
    EventBus, 
    SpeechEvent, 
    ReactionEvent, 
    InterjectionEvent,
    InterjectionType,
    DebateEvent,
    DebateEventType,
    RelationshipChangeEvent
)
from ..agents.relationship_aware_senator_agent import RelationshipAwareSenatorAgent
from ..agents.memory_persistence_manager import MemoryPersistenceManager


class MockLLMProvider(LLMProvider):
    """Mock LLM provider for demonstration purposes."""
    
    async def generate_text(self, prompt: str) -> str:
        """Return a mock response based on the prompt."""
        # Stance decisions based on topic and faction
        if "stance" in prompt.lower():
            if "land reform" in prompt.lower():
                if "populares" in prompt.lower():
                    return "As a Populares senator, I strongly support land reform as it benefits the common people.\n\nfor"
                elif "optimates" in prompt.lower():
                    return "As an Optimates senator, I oppose this land reform proposal.\n\nagainst"
                else:
                    return "I must carefully consider both sides of this issue.\n\nneutral"
            elif "military funding" in prompt.lower():
                if "optimates" in prompt.lower():
                    return "Increased military funding is essential for Rome's security.\n\nfor"
                else:
                    return "We must balance military needs with domestic priorities.\n\nneutral"
        return "I shall consider this matter carefully."


async def create_senators() -> List[RelationshipAwareSenatorAgent]:
    """Create senators with the relationship-aware system."""
    # Create shared components
    event_bus = EventBus()
    llm_provider = MockLLMProvider()
    
    # Create a memory persistence manager with a dedicated test directory
    memory_dir = os.path.join("saves", "test_integration_demo")
    os.makedirs(memory_dir, exist_ok=True)
    memory_manager = MemoryPersistenceManager(base_path=memory_dir)
    
    # Create senators with different factions and ranks
    senators = [
        RelationshipAwareSenatorAgent(
            senator={
                "name": "Marcus Cicero",
                "faction": "Optimates",
                "rank": 4,
                "id": "senator_cicero"
            },
            llm_provider=llm_provider,
            event_bus=event_bus,
            memory_manager=memory_manager
        ),
        RelationshipAwareSenatorAgent(
            senator={
                "name": "Gaius Julius Caesar",
                "faction": "Populares",
                "rank": 5,
                "id": "senator_caesar"
            },
            llm_provider=llm_provider,
            event_bus=event_bus,
            memory_manager=memory_manager
        ),
        RelationshipAwareSenatorAgent(
            senator={
                "name": "Marcus Cato",
                "faction": "Optimates",
                "rank": 3,
                "id": "senator_cato"
            },
            llm_provider=llm_provider,
            event_bus=event_bus,
            memory_manager=memory_manager
        ),
        RelationshipAwareSenatorAgent(
            senator={
                "name": "Publius Clodius",
                "faction": "Populares",
                "rank": 3,
                "id": "senator_clodius"
            },
            llm_provider=llm_provider,
            event_bus=event_bus,
            memory_manager=memory_manager
        )
    ]
    
    logger.info(f"Created {len(senators)} senators for the simulation")
    return senators


async def setup_initial_relationships(senators: List[RelationshipAwareSenatorAgent]):
    """Set up initial relationships between senators with different dimensions."""
    # Get senators by ID for easier reference
    senator_dict = {s.senator["id"]: s for s in senators}
    cicero = senator_dict["senator_cicero"]
    caesar = senator_dict["senator_caesar"]
    cato = senator_dict["senator_cato"]
    clodius = senator_dict["senator_clodius"]
    
    logger.info("=== SETTING UP INITIAL RELATIONSHIPS ===")
    
    # Set up Cicero's relationships
    logger.info("Setting up Cicero's relationships:")
    cicero.relationship_manager.update_relationship(
        "senator_caesar", "political", -0.4, "Political rivalry but respect for abilities"
    )
    cicero.relationship_manager.update_relationship(
        "senator_caesar", "personal", 0.2, "Personal respect despite political differences"
    )
    cicero.relationship_manager.update_relationship(
        "senator_cato", "political", 0.7, "Strong political alliance with fellow Optimate"
    )
    cicero.relationship_manager.update_relationship(
        "senator_cato", "personal", 0.5, "Personal friendship and shared values"
    )
    cicero.relationship_manager.update_relationship(
        "senator_clodius", "political", -0.8, "Bitter political enemy"
    )
    cicero.relationship_manager.update_relationship(
        "senator_clodius", "personal", -0.9, "Personal hatred after Clodius' actions"
    )
    
    # Set up Caesar's relationships
    logger.info("Setting up Caesar's relationships:")
    caesar.relationship_manager.update_relationship(
        "senator_cicero", "political", -0.4, "Political opposition but recognizes influence"
    )
    caesar.relationship_manager.update_relationship(
        "senator_cicero", "personal", 0.1, "Grudging personal respect for intellect"
    )
    caesar.relationship_manager.update_relationship(
        "senator_cato", "political", -0.7, "Strong political opposition from Optimate"
    )
    caesar.relationship_manager.update_relationship(
        "senator_cato", "personal", -0.3, "Personal dislike due to Cato's rigid moralism"
    )
    caesar.relationship_manager.update_relationship(
        "senator_clodius", "political", 0.6, "Political alliance with fellow Populare"
    )
    caesar.relationship_manager.update_relationship(
        "senator_clodius", "personal", 0.4, "Personal friendship and useful political tool"
    )
    
    # Add mentor relationships
    logger.info("Setting up mentor relationships:")
    cicero.relationship_manager.update_relationship(
        "senator_cato", "mentor", 0.3, "Occasional political mentorship"
    )
    caesar.relationship_manager.update_relationship(
        "senator_clodius", "mentor", 0.6, "Political mentorship and guidance"
    )


async def display_relationship_network(senators: List[RelationshipAwareSenatorAgent]):
    """Display the current relationship network between senators."""
    logger.info("\n=== RELATIONSHIP NETWORK ===")
    
    # For each senator, show their relationships with others
    for senator in senators:
        name = senator.name
        logger.info(f"\n{name}'s Relationships:")
        
        for other_senator in senators:
            if other_senator.senator["id"] == senator.senator["id"]:
                continue  # Skip self
                
            other_name = other_senator.name
            
            # Get relationship values
            political = senator.relationship_manager.get_relationship(
                other_senator.senator["id"], "political"
            )
            personal = senator.relationship_manager.get_relationship(
                other_senator.senator["id"], "personal"
            )
            overall = senator.relationship_manager.get_overall_relationship(
                other_senator.senator["id"]
            )
            
            # Format relationship values
            relationship_str = f"Political: {political:+.2f}, Personal: {personal:+.2f}, Overall: {overall:+.2f}"
            logger.info(f"  → {other_name}: {relationship_str}")


async def simulate_debate(senators: List[RelationshipAwareSenatorAgent], topic: str):
    """Simulate a debate on a given topic and observe relationship changes."""
    logger.info(f"\n=== SIMULATING DEBATE ON {topic.upper()} ===")
    
    # Get senators by ID for easier reference
    senator_dict = {s.senator["id"]: s for s in senators}
    
    # Start debate event
    debate_start_event = DebateEvent(
        debate_event_type=DebateEventType.DEBATE_START,
        topic=topic,
        presiding_magistrate=senator_dict["senator_cicero"].senator
    )
    await senator_dict["senator_cicero"].event_bus.publish(debate_start_event)
    logger.info(f"Debate started on topic: {topic}")
    
    # Record initial stances
    initial_stances = {}
    logger.info("\nInitial stances:")
    for senator in senators:
        stance, reasoning = await senator.decide_stance(topic, {})
        initial_stances[senator.senator["id"]] = stance
        logger.info(f"{senator.name} ({senator.faction}): {stance} - {reasoning}")
    
    # Each senator gives a speech
    for senator in senators:
        logger.info(f"\n{senator.name} is speaking")
        
        # Get stance
        stance = initial_stances[senator.senator["id"]]
        
        # Create and publish speech event
        speech_event = SpeechEvent(
            speaker=senator.senator,
            topic=topic,
            latin_content=f"Latin speech by {senator.name}...",
            english_content=f"I, {senator.name}, speak on {topic} with a {stance} stance.",
            stance=stance,
            key_points=[f"Point from {senator.name} on {topic}"]
        )
        await senator.event_bus.publish(speech_event)
        
        # Allow time for event processing
        await asyncio.sleep(0.1)
        
        # Generate reactions from other senators
        for reactor in senators:
            if reactor.senator["id"] == senator.senator["id"]:
                continue  # Skip self
            
            # Get relationship to determine reaction
            relationship = reactor.relationship_manager.get_overall_relationship(senator.senator["id"])
            reactor_stance = initial_stances[reactor.senator["id"]]
            
            # Determine reaction type based on relationship and stance alignment
            if reactor_stance == stance:
                reaction_type = "agreement"
            elif relationship > 0.3:
                reaction_type = "interest"
            elif relationship < -0.3:
                reaction_type = "disagreement"
            else:
                reaction_type = "skepticism"
            
            # Create and publish reaction event
            reaction_event = ReactionEvent(
                reactor=reactor.senator,
                target_event_id=speech_event.event_id,
                reaction_type=reaction_type,
                content=f"Reaction from {reactor.name}: {reaction_type}"
            )
            await reactor.event_bus.publish(reaction_event)
            logger.info(f"  {reactor.name} reacted with: {reaction_type}")
            
            # Allow time for event processing
            await asyncio.sleep(0.1)
    
    # End debate event
    debate_end_event = DebateEvent(
        debate_event_type=DebateEventType.DEBATE_END,
        topic=topic,
        presiding_magistrate=senator_dict["senator_cicero"].senator
    )
    await senator_dict["senator_cicero"].event_bus.publish(debate_end_event)
    logger.info(f"Debate ended on topic: {topic}")
    
    # Check for stance changes
    logger.info("\nFinal stances after debate:")
    for senator in senators:
        new_stance, reasoning = await senator.decide_stance(topic, {})
        if new_stance != initial_stances[senator.senator["id"]]:
            logger.info(f"{senator.name}: CHANGED from {initial_stances[senator.senator['id']]} to {new_stance}")
        else:
            logger.info(f"{senator.name}: UNCHANGED {new_stance}")


async def demonstrate_relationship_decay(senators: List[RelationshipAwareSenatorAgent], days_elapsed: int):
    """Demonstrate relationship decay over time."""
    logger.info(f"\n=== DEMONSTRATING RELATIONSHIP DECAY OVER {days_elapsed} DAYS ===")
    
    # Display relationships before decay
    await display_relationship_network(senators)
    
    # Apply time effects to all senators
    for senator in senators:
        await senator.apply_time_effects(days_elapsed)
    
    logger.info(f"\nSimulated {days_elapsed} days passing...")
    
    # Display relationships after decay
    await display_relationship_network(senators)


async def demonstrate_memory_persistence(senators: List[RelationshipAwareSenatorAgent]):
    """Demonstrate persistence of relationships across simulation restarts."""
    logger.info("\n=== DEMONSTRATING MEMORY PERSISTENCE ===")
    
    # Get senators by ID for easier reference
    senator_dict = {s.senator["id"]: s for s in senators}
    cicero = senator_dict["senator_cicero"]
    
    # Save current memory state
    logger.info("Saving current memory state...")
    for senator in senators:
        senator.memory_manager.save_memory(senator.senator["id"], senator.memory)
    
    # Display current relationship
    caesar_rel = cicero.relationship_manager.get_overall_relationship("senator_caesar")
    logger.info(f"Current Cicero-Caesar relationship: {caesar_rel:.2f}")
    
    # Create new senator instances (simulating restart)
    logger.info("Creating new senator instances (simulating restart)...")
    new_senators = await create_senators()
    new_senator_dict = {s.senator["id"]: s for s in new_senators}
    new_cicero = new_senator_dict["senator_cicero"]
    
    # Load memory from persistence
    logger.info("Loading memory from persistence...")
    for senator in new_senators:
        senator.memory_manager.load_memory(senator.senator["id"], senator.memory)
        # Reload relationships from memory
        senator.relationship_manager._load_relationships_from_memory()
    
    # Display relationship after reload
    new_caesar_rel = new_cicero.relationship_manager.get_overall_relationship("senator_caesar")
    logger.info(f"Cicero-Caesar relationship after reload: {new_caesar_rel:.2f}")


async def demonstrate_relationship_based_decisions(senators: List[RelationshipAwareSenatorAgent]):
    """Demonstrate how relationships influence senator decisions."""
    logger.info("\n=== DEMONSTRATING RELATIONSHIP-INFLUENCED DECISIONS ===")
    
    # Get senators by ID for easier reference
    senator_dict = {s.senator["id"]: s for s in senators}
    cicero = senator_dict["senator_cicero"]
    caesar = senator_dict["senator_caesar"]
    
    # Topics for decision making
    topics = ["Land Reform Act", "Military Funding Increase"]
    
    # Show initial relationship
    political_rel = cicero.relationship_manager.get_relationship("senator_caesar", "political")
    personal_rel = cicero.relationship_manager.get_relationship("senator_caesar", "personal")
    overall_rel = cicero.relationship_manager.get_overall_relationship("senator_caesar")
    logger.info(f"Initial Cicero-Caesar relationship: Political {political_rel:.2f}, Personal {personal_rel:.2f}, Overall {overall_rel:.2f}")
    
    # Record initial decisions
    logger.info("\nInitial decisions:")
    initial_decisions = {}
    for topic in topics:
        stance, reasoning = await cicero.decide_stance(topic, {})
        initial_decisions[topic] = stance
        logger.info(f"Cicero on {topic}: {stance} - {reasoning}")
    
    # Temporarily modify relationship to be strongly positive
    logger.info("\nTemporarily modifying Cicero-Caesar relationship to be strongly positive...")
    cicero.relationship_manager.update_relationship(
        "senator_caesar", "political", 0.9, "Temporary modification for demonstration"
    )
    cicero.relationship_manager.update_relationship(
        "senator_caesar", "personal", 0.8, "Temporary modification for demonstration"
    )
    
    # Record decisions after relationship change
    logger.info("\nDecisions after relationship change:")
    for topic in topics:
        stance, reasoning = await cicero.decide_stance(topic, {})
        logger.info(f"Cicero on {topic}: {stance} - {reasoning}")
        if stance != initial_decisions[topic]:
            logger.info(f"  CHANGED from {initial_decisions[topic]} to {stance} due to relationship influence")
        else:
            logger.info(f"  UNCHANGED from initial stance")


async def main():
    """Run the enhanced relationship system integration demo."""
    logger.info("Starting enhanced relationship system integration demo")
    
    # Create senators
    senators = await create_senators()
    
    # Set up initial relationships
    await setup_initial_relationships(senators)
    
    # Display initial relationship network
    await display_relationship_network(senators)
    
    # Simulate a debate on land reform
    await simulate_debate(senators, "Land Reform Act")
    
    # Display relationships after debate
    await display_relationship_network(senators)
    
    # Demonstrate relationship decay
    await demonstrate_relationship_decay(senators, 180)  # 6 months
    
    # Demonstrate memory persistence
    await demonstrate_memory_persistence(senators)
    
    # Demonstrate relationship-based decisions
    await demonstrate_relationship_based_decisions(senators)
    
    logger.info("\nEnhanced relationship system integration demo completed")


if __name__ == "__main__":
    asyncio.run(main())
