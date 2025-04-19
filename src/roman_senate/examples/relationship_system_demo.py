"""
Roman Senate AI Game
Relationship System Demo

This script demonstrates the usage of the new relationship system,
showing how to create relationship-aware senator agents, update relationships,
and observe how relationships influence decision making.
"""

import asyncio
import logging
import datetime
from typing import Dict, List, Any

from ..utils.llm.base import LLMProvider
from ..core.events import EventBus, SpeechEvent
from ..agents.relationship_aware_senator_agent import RelationshipAwareSenatorAgent
from ..agents.memory_persistence_manager import MemoryPersistenceManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MockLLMProvider(LLMProvider):
    """Mock LLM provider for demonstration purposes."""
    
    async def generate_text(self, prompt: str) -> str:
        """Return a mock response based on the prompt."""
        if "stance" in prompt.lower():
            if "land reform" in prompt.lower():
                if "populares" in prompt.lower():
                    return "As a Populares senator, I strongly support land reform as it benefits the common people and addresses wealth inequality.\n\nfor"
                elif "optimates" in prompt.lower():
                    return "As an Optimates senator, I oppose this land reform proposal as it undermines traditional property rights and the authority of the Senate.\n\nagainst"
                else:
                    return "I must carefully consider both sides of this issue. While land reform could help many citizens, we must respect existing property rights.\n\nneutral"
            elif "military funding" in prompt.lower():
                if "optimates" in prompt.lower():
                    return "Increased military funding is essential for Rome's security and expansion. Our legions must remain strong.\n\nfor"
                else:
                    return "While our military is important, we must balance this with domestic needs and not overburden the treasury.\n\nneutral"
        return "I shall consider this matter carefully."


async def create_test_senators() -> List[RelationshipAwareSenatorAgent]:
    """Create test senators with the relationship-aware system."""
    # Create shared components
    event_bus = EventBus()
    llm_provider = MockLLMProvider()
    memory_manager = MemoryPersistenceManager(base_path="./test_memories")
    
    # Create senators
    senators = [
        RelationshipAwareSenatorAgent(
            senator={
                "name": "Marcus Cicero",
                "faction": "Optimates",
                "rank": 3,
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
                "rank": 4,
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
                "rank": 2,
                "id": "senator_clodius"
            },
            llm_provider=llm_provider,
            event_bus=event_bus,
            memory_manager=memory_manager
        )
    ]
    
    return senators


async def setup_initial_relationships(senators: List[RelationshipAwareSenatorAgent]):
    """Set up initial relationships between senators."""
    # Get senators by ID for easier reference
    senator_dict = {s.senator["id"]: s for s in senators}
    cicero = senator_dict["senator_cicero"]
    caesar = senator_dict["senator_caesar"]
    cato = senator_dict["senator_cato"]
    clodius = senator_dict["senator_clodius"]
    
    # Set up Cicero's relationships
    cicero.relationship_manager.update_relationship(
        "senator_caesar", "political", -0.3, "Political rivalry"
    )
    cicero.relationship_manager.update_relationship(
        "senator_caesar", "personal", 0.2, "Personal respect despite political differences"
    )
    cicero.relationship_manager.update_relationship(
        "senator_cato", "political", 0.7, "Strong political alliance"
    )
    cicero.relationship_manager.update_relationship(
        "senator_cato", "personal", 0.5, "Personal friendship"
    )
    cicero.relationship_manager.update_relationship(
        "senator_clodius", "political", -0.8, "Bitter political enemy"
    )
    cicero.relationship_manager.update_relationship(
        "senator_clodius", "personal", -0.9, "Personal hatred"
    )
    
    # Set up Caesar's relationships
    caesar.relationship_manager.update_relationship(
        "senator_cicero", "political", -0.4, "Political opposition"
    )
    caesar.relationship_manager.update_relationship(
        "senator_cicero", "personal", 0.1, "Grudging personal respect"
    )
    caesar.relationship_manager.update_relationship(
        "senator_cato", "political", -0.7, "Strong political opposition"
    )
    caesar.relationship_manager.update_relationship(
        "senator_cato", "personal", -0.3, "Personal dislike"
    )
    caesar.relationship_manager.update_relationship(
        "senator_clodius", "political", 0.6, "Political alliance"
    )
    caesar.relationship_manager.update_relationship(
        "senator_clodius", "personal", 0.4, "Personal friendship"
    )
    
    # Set up Cato's relationships
    cato.relationship_manager.update_relationship(
        "senator_cicero", "political", 0.6, "Political alliance"
    )
    cato.relationship_manager.update_relationship(
        "senator_cicero", "personal", 0.4, "Personal friendship"
    )
    cato.relationship_manager.update_relationship(
        "senator_caesar", "political", -0.8, "Strong political opposition"
    )
    cato.relationship_manager.update_relationship(
        "senator_caesar", "personal", -0.5, "Personal dislike"
    )
    cato.relationship_manager.update_relationship(
        "senator_clodius", "political", -0.6, "Political opposition"
    )
    cato.relationship_manager.update_relationship(
        "senator_clodius", "personal", -0.4, "Personal dislike"
    )
    
    # Set up Clodius's relationships
    clodius.relationship_manager.update_relationship(
        "senator_cicero", "political", -0.9, "Bitter political enemy"
    )
    clodius.relationship_manager.update_relationship(
        "senator_cicero", "personal", -0.9, "Personal hatred"
    )
    clodius.relationship_manager.update_relationship(
        "senator_caesar", "political", 0.7, "Political alliance"
    )
    clodius.relationship_manager.update_relationship(
        "senator_caesar", "personal", 0.5, "Personal friendship"
    )
    clodius.relationship_manager.update_relationship(
        "senator_cato", "political", -0.7, "Political opposition"
    )
    clodius.relationship_manager.update_relationship(
        "senator_cato", "personal", -0.5, "Personal dislike"
    )


async def demonstrate_stance_decisions(senators: List[RelationshipAwareSenatorAgent]):
    """Demonstrate how relationships influence stance decisions."""
    logger.info("=== DEMONSTRATING RELATIONSHIP-INFLUENCED STANCE DECISIONS ===")
    
    # Get senators by ID for easier reference
    senator_dict = {s.senator["id"]: s for s in senators}
    
    # Topics for debate
    topics = [
        "Land Reform Act",
        "Military Funding Increase"
    ]
    
    # Have each senator decide their stance on each topic
    for topic in topics:
        logger.info(f"\nTopic: {topic}")
        
        for senator in senators:
            stance, reasoning = await senator.decide_stance(topic, {})
            logger.info(f"{senator.name} ({senator.faction}): {stance} - {reasoning}")
            
            # Show relationship influences
            for other_senator in senators:
                if other_senator.senator["id"] != senator.senator["id"]:
                    rel = senator.relationship_manager.get_overall_relationship(other_senator.senator["id"])
                    logger.info(f"  Relationship with {other_senator.name}: {rel:.2f}")


async def demonstrate_relationship_decay(senators: List[RelationshipAwareSenatorAgent]):
    """Demonstrate relationship decay over time."""
    logger.info("\n=== DEMONSTRATING RELATIONSHIP DECAY OVER TIME ===")
    
    # Get senators by ID for easier reference
    senator_dict = {s.senator["id"]: s for s in senators}
    cicero = senator_dict["senator_cicero"]
    caesar = senator_dict["senator_caesar"]
    
    # Show initial relationship
    political_rel = cicero.relationship_manager.get_relationship("senator_caesar", "political")
    personal_rel = cicero.relationship_manager.get_relationship("senator_caesar", "personal")
    logger.info(f"Initial Cicero-Caesar relationship: Political {political_rel:.2f}, Personal {personal_rel:.2f}")
    
    # Apply time decay (6 months)
    days_elapsed = 180
    logger.info(f"Simulating {days_elapsed} days passing...")
    cicero.apply_time_effects(days_elapsed)
    
    # Show decayed relationship
    political_rel = cicero.relationship_manager.get_relationship("senator_caesar", "political")
    personal_rel = cicero.relationship_manager.get_relationship("senator_caesar", "personal")
    logger.info(f"After decay Cicero-Caesar relationship: Political {political_rel:.2f}, Personal {personal_rel:.2f}")


async def demonstrate_relationship_events(senators: List[RelationshipAwareSenatorAgent]):
    """Demonstrate relationship changes from events."""
    logger.info("\n=== DEMONSTRATING RELATIONSHIP CHANGES FROM EVENTS ===")
    
    # Get senators by ID for easier reference
    senator_dict = {s.senator["id"]: s for s in senators}
    cicero = senator_dict["senator_cicero"]
    caesar = senator_dict["senator_caesar"]
    
    # Show initial relationship
    political_rel = cicero.relationship_manager.get_relationship("senator_caesar", "political")
    personal_rel = cicero.relationship_manager.get_relationship("senator_caesar", "personal")
    logger.info(f"Initial Cicero-Caesar relationship: Political {political_rel:.2f}, Personal {personal_rel:.2f}")
    
    # Create a speech event from Caesar
    speech_event = SpeechEvent(
        speaker=caesar.senator,
        topic="Military Funding Increase",
        latin_content="Lorem ipsum dolor sit amet...",
        english_content="I strongly support increasing military funding to strengthen Rome's legions.",
        stance="support",
        key_points=["Military strength is essential", "Current funding is insufficient"]
    )
    
    # Publish the event
    await cicero.event_bus.publish(speech_event)
    
    # Allow time for event processing
    await asyncio.sleep(0.1)
    
    # Show updated relationship
    political_rel = cicero.relationship_manager.get_relationship("senator_caesar", "political")
    personal_rel = cicero.relationship_manager.get_relationship("senator_caesar", "personal")
    logger.info(f"After Caesar's speech, Cicero-Caesar relationship: Political {political_rel:.2f}, Personal {personal_rel:.2f}")


async def main():
    """Run the relationship system demonstration."""
    logger.info("Starting relationship system demonstration")
    
    # Create test senators
    senators = await create_test_senators()
    logger.info(f"Created {len(senators)} test senators")
    
    # Set up initial relationships
    await setup_initial_relationships(senators)
    logger.info("Set up initial relationships")
    
    # Demonstrate stance decisions influenced by relationships
    await demonstrate_stance_decisions(senators)
    
    # Demonstrate relationship decay
    await demonstrate_relationship_decay(senators)
    
    # Demonstrate relationship changes from events
    await demonstrate_relationship_events(senators)
    
    logger.info("\nRelationship system demonstration completed")


if __name__ == "__main__":
    asyncio.run(main())