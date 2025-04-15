import pytest
from roman_senate.agents.agent_memory import AgentMemory

class TestAgentMemory:
    """Test suite for the AgentMemory class."""

    def test_init(self):
        """Test that AgentMemory initializes correctly."""
        memory = AgentMemory()
        assert hasattr(memory, 'relationship_scores')
        assert memory.relationship_scores == {}

    def test_get_relationship_score(self):
        """Test retrieving relationship scores using dict.get() method."""
        memory = AgentMemory()
        
        # Test with empty relationships
        assert memory.relationship_scores.get('Cicero', 0) == 0
        
        # Add a relationship and test again
        memory.relationship_scores['Cicero'] = 0.5
        assert memory.relationship_scores.get('Cicero', 0) == 0.5
        
        # Test with a default value for non-existent relationship
        assert memory.relationship_scores.get('Unknown Senator', 0) == 0
        assert memory.relationship_scores.get('Unknown Senator', -0.1) == -0.1

    def test_update_relationship(self):
        """Test updating relationship scores."""
        memory = AgentMemory()
        
        # Add a new relationship
        memory.update_relationship('Cicero', 0.3)
        assert 'Cicero' in memory.relationship_scores
        assert memory.relationship_scores['Cicero'] == 0.3
        
        # Update an existing relationship
        memory.update_relationship('Cicero', 0.2)
        assert memory.relationship_scores['Cicero'] == 0.5
        
        # Test negative update
        memory.update_relationship('Cicero', -0.7)
        # Use pytest.approx() for floating point comparisons to handle precision issues
        assert memory.relationship_scores['Cicero'] == pytest.approx(-0.2)