import pytest
from unittest.mock import MagicMock, patch, AsyncMock
import asyncio
from roman_senate.agents.environment import SenateEnvironment
from roman_senate.core.interjection import InterjectionType
from roman_senate.agents.senator_agent import SenatorAgent
from roman_senate.agents.agent_memory import AgentMemory

class TestIntegration:
    """Integration tests for the Senate simulation."""

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
        environment = SenateEnvironment(mock_llm_provider)
        environment.initialize_agents(sample_senators)
        environment.set_topics([sample_topic])
        environment.current_topic = sample_topic
        
        # Override conduct_debate to simulate a debate with relationship updates
        async def mock_conduct_debate(**kwargs):
            speeches = []
            
            # For each senator, generate a speech
            for agent in environment.agents:
                # Set the current stance based on the mocked response
                agent.current_stance = "support" if agent.name in ["Cicero", "Cato"] else "oppose"
                
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
                        # Process the reaction using the real method to test relationship access
                        await reactor._generate_interjection_content(
                            agent.name,
                            {"faction": agent.faction, "stance": agent.current_stance},
                            InterjectionType.ACCLAMATION  # Use proper enum instead of empty dict
                        )
                        
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
                            reactor.memory.update_relationship(agent.name, relationship_updates[key])
            
            return speeches
        
        # Patch the conduct_debate method
        with patch("roman_senate.core.debate.conduct_debate", mock_conduct_debate):
            # Run the debate (this will use our mocked conduct_debate)
            debate_result = await environment.run_debate(sample_topic)
            
            # Run the vote (this will test the vote mapping fix)
            vote_result = debate_result["vote_result"]
            
            # TEST 1: Verify relationship scores were correctly stored and accessed
            # Check Cato has positive relationship with Cicero from speech reaction
            cato = environment.get_senator_agent("Cato")
            assert cato.memory.relationship_scores.get("Cicero", 0) > 0
            
            # Check Caesar has negative relationships with both Optimates
            caesar = environment.get_senator_agent("Caesar")
            assert caesar.memory.relationship_scores.get("Cicero", 0) < 0
            assert caesar.memory.relationship_scores.get("Cato", 0) < 0
            
            # TEST 2: Verify vote mapping worked correctly
            assert vote_result["votes"]["for"] == 2  # Cicero and Cato voted "support" -> mapped to "for"
            assert vote_result["votes"]["against"] == 1  # Caesar voted "oppose" -> mapped to "against"
            assert vote_result["outcome"] == "PASSED"  # 2 for vs 1 against = passed
            
            # Verify voting record reflects correct votes
            for record in vote_result["voting_record"]:
                if record["senator"] in ["Cicero", "Cato"]:
                    assert record["vote"] == "support"
                elif record["senator"] == "Caesar":
                    assert record["vote"] == "oppose"