"""
Debug version of the integration test to diagnose relationship system issues.
"""

import pytest
import logging
from unittest.mock import MagicMock, patch, AsyncMock
import asyncio
from roman_senate.agents.environment import SenateEnvironment
from roman_senate.core.interjection import InterjectionType
from roman_senate.agents.senator_agent import SenatorAgent
from roman_senate.agents.agent_memory import AgentMemory
from roman_senate.agents.relationship_aware_senator_agent import RelationshipAwareSenatorAgent
from roman_senate.core.events.event_bus import EventBus

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class TestIntegrationDebug:
    """Debug version of integration tests for the Senate simulation."""

    @pytest.fixture
    def mock_llm_provider(self):
        """Create a mock LLM provider."""
        provider = MagicMock()
        provider.generate_text = AsyncMock()
        return provider

    @pytest.fixture
    def sample_senators(self):
        """Return a list of sample senator dictionaries."""
        return [
            {"name": "Cicero", "faction": "Optimates"},
            {"name": "Caesar", "faction": "Populares"},
            {"name": "Cato", "faction": "Optimates"}
        ]

    @pytest.fixture
    def sample_topic(self):
        """Return a sample topic."""
        return {"text": "Should we expand Rome's territory?", "category": "Foreign Policy"}

    @pytest.mark.asyncio
    async def test_debate_and_vote_integration(self, mock_llm_provider, sample_senators, sample_topic):
        """
        Integration test for the full debate and vote process, testing both relationship score access
        and vote mapping fixes.
        """
        # Setup mock responses
        mock_llm_provider.generate_text.side_effect = [
            # First 3 calls: decide_stance for each senator
            '{"stance": "support", "reasoning": "Expansion is necessary for security."}',
            '{"stance": "oppose", "reasoning": "We should focus on internal affairs."}',
            '{"stance": "support", "reasoning": "Rome\'s destiny is to expand."}',
            
            # Next 3 calls: speech generation for each senator
            '{"latin": "Latin speech 1", "english": "Expansion serves Rome\'s interests."}',
            '{"latin": "Latin speech 2", "english": "Expansion is too costly."}',
            '{"latin": "Latin speech 3", "english": "I support expansion."}',
            
            # Next 6 calls: reactions to speeches (3 senators reacting to 2 other speeches)
            '{"reaction": "positive", "score_change": 0.2}',  # Cicero's reaction to Caesar's speech
            '{"reaction": "positive", "score_change": 0.3}',  # Cicero's reaction to Cato's speech
            '{"reaction": "negative", "score_change": -0.2}', # Caesar's reaction to Cicero's speech
            '{"reaction": "negative", "score_change": -0.3}', # Caesar's reaction to Cato's speech
            '{"reaction": "positive", "score_change": 0.4}',  # Cato's reaction to Cicero's speech
            '{"reaction": "negative", "score_change": -0.1}', # Cato's reaction to Caesar's speech
            
            # Final 3 calls: votes
            '{"vote": "support", "reasoning": "I maintain my position."}',
            '{"vote": "oppose", "reasoning": "I maintain my position."}',
            '{"vote": "support", "reasoning": "I maintain my position."}'
        ]
        
        # Initialize environment
        logger.info("Initializing environment")
        environment = SenateEnvironment(mock_llm_provider)
        
        # Log the type of environment and agent class being used
        logger.info(f"Environment type: {type(environment).__name__}")
        logger.info(f"Default agent class: {SenatorAgent.__name__}")
        
        # Initialize agents
        environment.initialize_agents(sample_senators)
        
        # Log agent types
        for agent in environment.agents:
            logger.info(f"Agent {agent.name} type: {type(agent).__name__}")
            logger.info(f"Agent {agent.name} memory type: {type(agent.memory).__name__}")
        
        environment.set_topics([sample_topic])
        environment.current_topic = sample_topic
        
        # Override conduct_debate to simulate a debate with relationship updates
        async def mock_conduct_debate(**kwargs):
            speeches = []
            logger.info("Starting mock debate")
            
            # For each senator, generate a speech
            for agent in environment.agents:
                # Set the current stance based on the mocked response
                agent.current_stance = "support" if agent.name in ["Cicero", "Cato"] else "oppose"
                logger.info(f"Senator {agent.name} stance: {agent.current_stance}")
                
                # Use a simplified speech dict
                speech = {
                    "senator_name": agent.name,
                    "faction": agent.faction,
                    "stance": agent.current_stance,
                    "content": f"{agent.name}'s speech on expansion"
                }
                speeches.append(speech)
                
                # For each other senator, generate a reaction to this speech
                for reactor in environment.agents:
                    if reactor.name != agent.name:
                        logger.info(f"Generating reaction: {reactor.name} reacting to {agent.name}")
                        
                        # Process the reaction using the real method to test relationship access
                        try:
                            await reactor._generate_interjection_content(
                                agent.name,
                                {"faction": agent.faction, "stance": agent.current_stance},
                                InterjectionType.ACCLAMATION  # Use proper enum instead of empty dict
                            )
                        except Exception as e:
                            logger.error(f"Error generating interjection: {str(e)}")
                        
                        # Simulate relationship updates between all senators
                        # This tests the fix for using relationship_scores.get()
                        
                        # Define the relationship update pattern for better test control
                        relationship_updates = {
                            # Format: (speaker, listener): update_value
                            ("Cicero", "Caesar"): -0.2,
                            ("Cicero", "Cato"): 0.4,
                            ("Caesar", "Cicero"): -0.2,
                            ("Caesar", "Cato"): -0.3,
                            ("Cato", "Cicero"): 0.3,
                            ("Cato", "Caesar"): -0.2
                        }
                        
                        # Apply the predefined relationship update
                        key = (agent.name, reactor.name)
                        if key in relationship_updates:
                            logger.info(f"Updating relationship: {reactor.name} -> {agent.name}: {relationship_updates[key]}")
                            try:
                                reactor.memory.update_relationship(agent.name, relationship_updates[key])
                                # Log the updated relationship score
                                score = reactor.memory.relationship_scores.get(agent.name, 0)
                                logger.info(f"New relationship score: {reactor.name} -> {agent.name}: {score}")
                            except Exception as e:
                                logger.error(f"Error updating relationship: {str(e)}")
            
            logger.info("Mock debate completed")
            return speeches
        
        # Patch the conduct_debate method
        with patch("roman_senate.core.debate.conduct_debate", mock_conduct_debate):
            # Run the debate (this will use our mocked conduct_debate)
            logger.info("Running debate")
            debate_result = await environment.run_debate(sample_topic)
            
            # Run the vote (this will test the vote mapping fix)
            logger.info("Getting vote result")
            vote_result = debate_result["vote_result"]
            
            # Log vote results
            logger.info(f"Vote result: {vote_result}")
            
            # TEST 1: Verify relationship scores were correctly stored and accessed
            # Check Cato has positive relationship with Cicero from speech reaction
            logger.info("Checking relationship scores")
            cato = environment.get_senator_agent("Cato")
            cicero_score = cato.memory.relationship_scores.get("Cicero", 0)
            logger.info(f"Cato -> Cicero relationship score: {cicero_score}")
            
            # Check Caesar has negative relationships with both Optimates
            caesar = environment.get_senator_agent("Caesar")
            caesar_cicero_score = caesar.memory.relationship_scores.get("Cicero", 0)
            caesar_cato_score = caesar.memory.relationship_scores.get("Cato", 0)
            logger.info(f"Caesar -> Cicero relationship score: {caesar_cicero_score}")
            logger.info(f"Caesar -> Cato relationship score: {caesar_cato_score}")
            
            # Log all relationship scores for all agents
            logger.info("All relationship scores:")
            for agent in environment.agents:
                logger.info(f"{agent.name} relationships:")
                for other_senator, score in agent.memory.relationship_scores.items():
                    logger.info(f"  -> {other_senator}: {score}")
            
            # TEST 2: Verify vote mapping worked correctly
            logger.info("Checking vote mapping")
            logger.info(f"Votes for: {vote_result['votes']['for']}")
            logger.info(f"Votes against: {vote_result['votes']['against']}")
            logger.info(f"Outcome: {vote_result['outcome']}")
            
            # Log voting record
            logger.info("Voting record:")
            for record in vote_result["voting_record"]:
                logger.info(f"  {record['senator']} voted {record['vote']}")
            
            # Run assertions with detailed error messages
            try:
                # Relationship score assertions
                assert cato.memory.relationship_scores.get("Cicero", 0) > 0, "Cato should have positive relationship with Cicero"
                assert caesar.memory.relationship_scores.get("Cicero", 0) < 0, "Caesar should have negative relationship with Cicero"
                assert caesar.memory.relationship_scores.get("Cato", 0) < 0, "Caesar should have negative relationship with Cato"
                
                # Vote mapping assertions
                assert vote_result["votes"]["for"] == 2, "Should have 2 votes for (Cicero and Cato)"
                assert vote_result["votes"]["against"] == 1, "Should have 1 vote against (Caesar)"
                assert vote_result["outcome"] == "PASSED", "Outcome should be PASSED"
                
                # Voting record assertions
                for record in vote_result["voting_record"]:
                    if record["senator"] in ["Cicero", "Cato"]:
                        assert record["vote"] == "support", f"{record['senator']} should have voted 'support'"
                    elif record["senator"] == "Caesar":
                        assert record["vote"] == "oppose", "Caesar should have voted 'oppose'"
                
                logger.info("All assertions passed!")
            except AssertionError as e:
                logger.error(f"Assertion failed: {str(e)}")
                # Re-raise to fail the test
                raise