import pytest
from unittest.mock import MagicMock, patch, AsyncMock
import asyncio
from roman_senate.agents.environment import SenateEnvironment
from roman_senate.agents.senator_agent import SenatorAgent

class TestEnvironment:
    """Test suite for the SenateEnvironment class."""

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

    @pytest.fixture
    def environment(self, mock_llm_provider):
        """Create a SenateEnvironment instance."""
        return SenateEnvironment(mock_llm_provider)

    def test_initialize_agents(self, environment, sample_senators):
        """Test agent initialization."""
        environment.initialize_agents(sample_senators)
        assert len(environment.agents) == 3
        assert all(isinstance(agent, SenatorAgent) for agent in environment.agents)
        assert [agent.name for agent in environment.agents] == ["Cicero", "Caesar", "Cato"]

    def test_set_topics(self, environment):
        """Test setting debate topics."""
        topics = [
            {"text": "Topic 1", "category": "Category 1"},
            ("Topic 2", "Category 2")  # Test tuple format
        ]
        environment.set_topics(topics)
        assert len(environment.topics) == 2
        assert all(isinstance(topic, dict) for topic in environment.topics)
        assert environment.topics[0]["text"] == "Topic 1"
        assert environment.topics[1]["text"] == "Topic 2"

    @pytest.mark.asyncio
    async def test_vote_mapping(self, environment, sample_senators, sample_topic):
        """Test vote mapping from 'support'/'oppose' to 'for'/'against'."""
        # Initialize environment
        environment.initialize_agents(sample_senators)
        environment.set_topics([sample_topic])
        environment.current_topic = sample_topic
        
        # Mock the vote method on senator agents
        for i, agent in enumerate(environment.agents):
            # Set different vote returns: "support", "oppose", "abstain"
            vote_returns = ["support", "oppose", "support"]
            agent.vote = AsyncMock(return_value=(vote_returns[i], "Mock reasoning"))
        
        # Run the vote with testing flag to disable random abstentions
        result = await environment.run_vote(sample_topic["text"], {}, testing=True)
        
        # Check that votes were properly mapped
        assert result["votes"]["for"] == 2  # 2 "support" votes should map to "for"
        assert result["votes"]["against"] == 1  # 1 "oppose" vote should map to "against"
        assert result["votes"]["abstain"] == 0  # No abstentions in this test
        assert result["total"] == 3
        assert result["outcome"] == "PASSED"  # 2 for vs 1 against = passed
        
        # Verify voting record contains correctly mapped votes
        voting_record = result["voting_record"]
        assert len(voting_record) == 3
        
        # Check senator votes were correctly recorded
        senator_votes = {record["senator"]: record["vote"] for record in voting_record}
        assert senator_votes["Cicero"] == "support"
        assert senator_votes["Caesar"] == "oppose"
        assert senator_votes["Cato"] == "support"

    @pytest.mark.asyncio
    async def test_vote_with_abstentions(self, environment, sample_senators, sample_topic):
        """Test vote counting with abstentions."""
        # Initialize environment
        environment.initialize_agents(sample_senators)
        environment.set_topics([sample_topic])
        environment.current_topic = sample_topic
        
        # Mock the vote method on senator agents
        for i, agent in enumerate(environment.agents):
            # Set different vote returns: "support", "oppose", "abstain"
            vote_returns = ["support", "oppose", "abstain"]
            agent.vote = AsyncMock(return_value=(vote_returns[i], "Mock reasoning"))
        
        # Run the vote
        result = await environment.run_vote(sample_topic["text"], {})
        
        # Check that votes were properly mapped and counted
        assert result["votes"]["for"] == 1  # 1 "support" vote should map to "for"
        assert result["votes"]["against"] == 1  # 1 "oppose" vote should map to "against"
        assert result["votes"]["abstain"] == 1  # 1 abstention
        assert result["total"] == 3
        
        # Verify voting record contains correct votes
        voting_record = result["voting_record"]
        assert len(voting_record) == 3
        
        # Check senator votes were correctly recorded
        senator_votes = {record["senator"]: record["vote"] for record in voting_record}
        assert senator_votes["Cicero"] == "support"
        assert senator_votes["Caesar"] == "oppose"
        assert senator_votes["Cato"] == "abstain"