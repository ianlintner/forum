"""
Tests for the relationship system components.

This module contains tests for the RelationshipMemoryItem, RelationshipChangeEvent,
RelationshipManager, and RelationshipAwareSenatorAgent classes.
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import MagicMock, patch

from src.roman_senate.agents.memory_items import RelationshipMemoryItem
from src.roman_senate.core.events import RelationshipChangeEvent, EventBus
from src.roman_senate.agents.relationship_manager import RelationshipManager
from src.roman_senate.agents.relationship_aware_senator_agent import RelationshipAwareSenatorAgent
from src.roman_senate.agents.enhanced_event_memory import EnhancedEventMemory


class TestRelationshipMemoryItem:
    """Tests for the RelationshipMemoryItem class."""
    
    def test_initialization(self):
        """Test that a RelationshipMemoryItem can be properly initialized."""
        # Create a relationship memory item
        rel_memory = RelationshipMemoryItem(
            senator_id="senator_cicero",
            target_senator_id="senator_caesar",
            relationship_type="political",
            relationship_value=0.5,
            timestamp=datetime.now(),
            importance=0.7,
            decay_rate=0.05,
            emotional_impact=0.3,
            context="Political alliance formed"
        )
        
        # Check that the attributes are set correctly
        assert rel_memory.senator_id == "senator_cicero"
        assert rel_memory.target_senator_id == "senator_caesar"
        assert rel_memory.relationship_type == "political"
        assert rel_memory.relationship_value == 0.5
        assert rel_memory.importance == 0.7
        assert rel_memory.decay_rate == 0.05
        assert rel_memory.emotional_impact == 0.3
        assert rel_memory.context == "Political alliance formed"
        
        # Check that the tags are set correctly
        assert "relationship" in rel_memory.tags
        assert "political" in rel_memory.tags
        assert "senator_caesar" in rel_memory.tags
    
    def test_to_dict_and_from_dict(self):
        """Test that a RelationshipMemoryItem can be converted to and from a dictionary."""
        # Create a relationship memory item
        original = RelationshipMemoryItem(
            senator_id="senator_cicero",
            target_senator_id="senator_caesar",
            relationship_type="political",
            relationship_value=0.5,
            timestamp=datetime.now(),
            importance=0.7,
            decay_rate=0.05,
            emotional_impact=0.3,
            context="Political alliance formed"
        )
        
        # Convert to dictionary
        data = original.to_dict()
        
        # Convert back to RelationshipMemoryItem
        reconstructed = RelationshipMemoryItem.from_dict(data)
        
        # Check that the attributes are preserved
        assert reconstructed.senator_id == original.senator_id
        assert reconstructed.target_senator_id == original.target_senator_id
        assert reconstructed.relationship_type == original.relationship_type
        assert reconstructed.relationship_value == original.relationship_value
        assert reconstructed.importance == original.importance
        assert reconstructed.decay_rate == original.decay_rate
        assert reconstructed.emotional_impact == original.emotional_impact
        assert reconstructed.context == original.context
        assert set(reconstructed.tags) == set(original.tags)


class TestRelationshipChangeEvent:
    """Tests for the RelationshipChangeEvent class."""
    
    def test_initialization(self):
        """Test that a RelationshipChangeEvent can be properly initialized."""
        # Create a relationship change event
        event = RelationshipChangeEvent(
            senator_id="senator_cicero",
            target_senator_id="senator_caesar",
            relationship_type="political",
            old_value=0.3,
            new_value=0.5,
            change_value=0.2,
            reason="Supported my proposal",
            source_event_id="event_123"
        )
        
        # Check that the attributes are set correctly
        assert event.senator_id == "senator_cicero"
        assert event.target_senator_id == "senator_caesar"
        assert event.relationship_type == "political"
        assert event.old_value == 0.3
        assert event.new_value == 0.5
        assert event.change_value == 0.2
        assert event.reason == "Supported my proposal"
        assert event.source_event_id == "event_123"
        assert event.event_type == "relationship_change"
        
        # Check that the metadata is set correctly
        assert event.metadata["senator_id"] == "senator_cicero"
        assert event.metadata["target_senator_id"] == "senator_caesar"
        assert event.metadata["relationship_type"] == "political"
        assert event.metadata["old_value"] == 0.3
        assert event.metadata["new_value"] == 0.5
        assert event.metadata["change_value"] == 0.2
        assert event.metadata["reason"] == "Supported my proposal"
        assert event.metadata["source_event_id"] == "event_123"
    
    def test_to_dict(self):
        """Test that a RelationshipChangeEvent can be converted to a dictionary."""
        # Create a relationship change event
        event = RelationshipChangeEvent(
            senator_id="senator_cicero",
            target_senator_id="senator_caesar",
            relationship_type="political",
            old_value=0.3,
            new_value=0.5,
            change_value=0.2,
            reason="Supported my proposal",
            source_event_id="event_123"
        )
        
        # Convert to dictionary
        data = event.to_dict()
        
        # Check that the dictionary contains the expected fields
        assert data["event_type"] == "relationship_change"
        assert data["senator_id"] == "senator_cicero"
        assert data["target_senator_id"] == "senator_caesar"
        assert data["relationship_type"] == "political"
        assert data["old_value"] == 0.3
        assert data["new_value"] == 0.5
        assert data["change_value"] == 0.2
        assert data["reason"] == "Supported my proposal"
        assert data["source_event_id"] == "event_123"


class TestRelationshipManager:
    """Tests for the RelationshipManager class."""
    
    @pytest.fixture
    def relationship_manager(self):
        """Create a RelationshipManager for testing."""
        # Create mock dependencies
        event_bus = MagicMock(spec=EventBus)
        memory = MagicMock(spec=EnhancedEventMemory)
        memory.memory_index = MagicMock()
        
        # Create the relationship manager
        manager = RelationshipManager(
            senator_id="senator_cicero",
            event_bus=event_bus,
            memory=memory
        )
        
        return manager
    
    def test_get_relationship_default(self, relationship_manager):
        """Test getting a relationship that doesn't exist returns 0."""
        # Get a relationship that doesn't exist
        value = relationship_manager.get_relationship("senator_caesar", "political")
        
        # Check that the default value is 0.0
        assert value == 0.0
    
    def test_update_relationship(self, relationship_manager):
        """Test updating a relationship."""
        # Update a relationship
        new_value = relationship_manager.update_relationship(
            "senator_caesar",
            "political",
            0.2,
            "Supported my proposal",
            publish_event=False
        )
        
        # Check that the relationship was updated in the cache
        assert relationship_manager.relationship_cache["political"]["senator_caesar"] == 0.2
        assert new_value == 0.2
        
        # Check that a memory item was created
        relationship_manager.memory.memory_index.add_memory.assert_called_once()
    
    def test_get_overall_relationship(self, relationship_manager):
        """Test getting the overall relationship."""
        # Set up some relationships
        relationship_manager.relationship_cache["political"]["senator_caesar"] = 0.5
        relationship_manager.relationship_cache["personal"]["senator_caesar"] = 0.3
        relationship_manager.relationship_cache["mentor"]["senator_caesar"] = 0.0
        relationship_manager.relationship_cache["rival"]["senator_caesar"] = -0.2
        relationship_manager.relationship_cache["family"]["senator_caesar"] = 0.0
        
        # Get the overall relationship
        overall = relationship_manager.get_overall_relationship("senator_caesar")
        
        # Calculate the expected value (weighted average)
        expected = (0.5 * 0.3) + (0.3 * 0.3) + (0.0 * 0.15) + (-0.2 * 0.2) + (0.0 * 0.05)
        
        # Check that the overall relationship is correct
        assert overall == pytest.approx(expected)
    
    def test_apply_time_decay(self, relationship_manager):
        """Test applying time decay to relationships."""
        # Set up some relationships
        relationship_manager.relationship_cache["political"]["senator_caesar"] = 0.5
        relationship_manager.relationship_cache["personal"]["senator_caesar"] = -0.3
        
        # Apply time decay
        relationship_manager.apply_time_decay(30)  # 30 days
        
        # Calculate expected values
        political_decay = 0.08 / 30 * 30  # Monthly rate to daily, times 30 days
        personal_decay = 0.04 / 30 * 30
        
        expected_political = 0.5 - political_decay
        expected_personal = -0.3 + personal_decay  # Negative values decay toward 0
        
        # Check that the relationships were decayed correctly
        assert relationship_manager.relationship_cache["political"]["senator_caesar"] == pytest.approx(expected_political)
        assert relationship_manager.relationship_cache["personal"]["senator_caesar"] == pytest.approx(expected_personal)


@pytest.mark.asyncio
class TestRelationshipAwareSenatorAgent:
    """Tests for the RelationshipAwareSenatorAgent class."""
    
    @pytest.fixture
    async def senator_agent(self):
        """Create a RelationshipAwareSenatorAgent for testing."""
        # Create mock dependencies
        llm_provider = MagicMock()
        event_bus = MagicMock(spec=EventBus)
        memory_manager = MagicMock()
        
        # Mock the decide_stance method of the parent class
        with patch('src.roman_senate.agents.enhanced_senator_agent.EnhancedSenatorAgent.decide_stance') as mock_decide_stance:
            mock_decide_stance.return_value = ("neutral", "I am neutral on this topic.")
            
            # Create the senator agent
            agent = RelationshipAwareSenatorAgent(
                senator={
                    "name": "Marcus Cicero",
                    "faction": "Optimates",
                    "id": "senator_cicero"
                },
                llm_provider=llm_provider,
                event_bus=event_bus,
                memory_manager=memory_manager
            )
            
            # Mock the relationship manager
            agent.relationship_manager = MagicMock(spec=RelationshipManager)
            agent.relationship_manager.get_overall_relationship.return_value = 0.0
            
            yield agent
    
    async def test_decide_stance_with_relationships(self, senator_agent):
        """Test that relationships influence stance decisions."""
        # Mock finding key senators
        senator_agent._find_key_senators_for_topic = MagicMock()
        senator_agent._find_key_senators_for_topic.return_value = {
            "senator_caesar": "support",
            "senator_cato": "oppose"
        }
        
        # Mock getting senator names
        senator_agent._get_senator_name = MagicMock()
        senator_agent._get_senator_name.side_effect = lambda id: id.replace("senator_", "").title()
        
        # Set up relationship influences
        senator_agent.relationship_manager.get_overall_relationship.side_effect = lambda id: 0.8 if id == "senator_caesar" else -0.4
        
        # Decide stance
        stance, reasoning = await senator_agent.decide_stance("Land Reform", {})
        
        # The base stance is neutral, but with Caesar (0.8) supporting and Cato (-0.4) opposing,
        # the influence should be positive and change the stance to support
        assert stance == "support"
        assert "influenced by" in reasoning
        assert "Caesar" in reasoning
        assert "Cato" in reasoning
    
    async def test_apply_time_effects(self, senator_agent):
        """Test applying time effects."""
        # Apply time effects
        senator_agent.apply_time_effects(30)
        
        # Check that relationship decay was applied
        senator_agent.relationship_manager.apply_time_decay.assert_called_once_with(30)


if __name__ == "__main__":
    pytest.main(["-xvs", __file__])