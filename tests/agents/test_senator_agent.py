import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from roman_senate.agents.senator_agent import SenatorAgent
from roman_senate.agents.agent_memory import AgentMemory

class TestSenatorAgent:
    """Test suite for the SenatorAgent class."""

    @pytest.fixture
    def sample_senator_dict(self):
        """Return a sample senator dictionary."""
        return {
            "name": "Cicero",
            "faction": "Optimates"
        }

    @pytest.fixture
    def llm_provider(self):
        """Create a mock LLM provider."""
        mock_provider = MagicMock()
        mock_provider.generate_text = AsyncMock()
        return mock_provider

    def test_init(self, sample_senator_dict, llm_provider):
        """Test SenatorAgent initialization."""
        agent = SenatorAgent(sample_senator_dict, llm_provider)
        assert agent.senator == sample_senator_dict
        assert agent.name == "Cicero"
        assert agent.faction == "Optimates"
        assert agent.llm_provider == llm_provider
        assert isinstance(agent.memory, AgentMemory)

    def test_relationship_score_access(self, sample_senator_dict, llm_provider):
        """Test relationship score access using dict.get() method."""
        agent = SenatorAgent(sample_senator_dict, llm_provider)
        
        # Set up relationships in memory
        agent.memory.relationship_scores = {
            "Caesar": 0.7,
            "Cato": -0.3
        }
        
        # Test accessing existing relationships
        assert agent.memory.relationship_scores.get("Caesar", 0) == 0.7
        assert agent.memory.relationship_scores.get("Cato", 0) == -0.3
        
        # Test accessing non-existent relationship (should return default 0)
        assert agent.memory.relationship_scores.get("Unknown Senator", 0) == 0

    @pytest.mark.asyncio
    async def test_generate_interjection_relationship_access(self, sample_senator_dict, llm_provider):
        """Test relationship access in the generate_interjection method."""
        agent = SenatorAgent(sample_senator_dict, llm_provider)
        
        # Set up relationships
        agent.memory.relationship_scores = {"Caesar": 0.5}
        
        # Set up expected return values for mocked methods
        agent._should_interject = MagicMock(return_value=True)
        agent._determine_interjection_type = MagicMock()
        agent._determine_interjection_timing = MagicMock()
        agent._generate_interjection_content = AsyncMock(return_value=("Latin content", "English content"))
        agent._calculate_interjection_intensity = MagicMock(return_value=0.5)
        
        # Create speech content
        speech_content = {
            "faction": "Populares",
            "stance": "oppose",
            "content": "Test speech"
        }
        
        # Call the method
        await agent.generate_interjection("Caesar", speech_content, {})
        
        # Verify relationship was accessed correctly via relationship_scores.get
        agent._should_interject.assert_called_once_with("Caesar", speech_content)