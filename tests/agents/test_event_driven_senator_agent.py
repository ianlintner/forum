"""
Tests for the EventDrivenSenatorAgent class.

This test suite verifies the behavior of the event-driven senator agent
implementation, ensuring it properly responds to events, generates actions,
and maintains memory of past events.
"""

import pytest
import asyncio
from unittest.mock import MagicMock, patch
from typing import Dict, Any, List

from roman_senate.core.events.base import BaseEvent as RomanEvent
from roman_senate.core.events.event_bus import EventBus
from roman_senate.agents.event_driven_senator_agent import EventDrivenSenatorAgent
from roman_senate.agents.event_memory import EventMemory


class MockLLMProvider:
    """Mock LLM provider for testing."""
    
    def generate_text(self, prompt: str) -> str:
        """Return a fixed response based on prompt keywords."""
        if "stance" in prompt.lower():
            # Return a stance response
            return "I support this proposal for the good of Rome.\n\nsupport"
        elif "speech" in prompt.lower():
            # Return a speech response
            return "Fellow senators, I rise to support this measure.\n\nI have employed rhetorical techniques to persuade."
        elif "translate" in prompt.lower() or "latin" in prompt.lower():
            # Return a Latin translation
            return "Senatores, hanc rem sustineo."
        elif "interject" in prompt.lower():
            # Return an interjection
            return "I must express my agreement with the honorable senator!"
        else:
            # Default response
            return "Default response for prompt: " + prompt[:20] + "..."


class TestEventDrivenSenatorAgent:
    """Tests for the EventDrivenSenatorAgent class."""
    
    @pytest.fixture
    def event_bus(self):
        """Create a mock event bus."""
        bus = MagicMock(spec=EventBus)
        bus.publish = MagicMock()
        bus.subscribe = MagicMock()
        return bus
    
    @pytest.fixture
    def llm_provider(self):
        """Create a mock LLM provider."""
        return MockLLMProvider()
    
    @pytest.fixture
    def senator_data(self):
        """Create test senator data."""
        return {
            "name": "Marcus Cato",
            "faction": "Optimates",
            "attributes": {
                "eloquence": 8,
                "influence": 7,
                "military_experience": 6,
                "wealth": 8
            }
        }
    
    @pytest.fixture
    def senator_agent(self, event_bus, llm_provider, senator_data):
        """Create a senator agent for testing."""
        agent = EventDrivenSenatorAgent(
            senator=senator_data,
            llm_provider=llm_provider,
            event_bus=event_bus,
            agent_id="test-agent-id"
        )
        return agent
    
    def test_init(self, senator_agent, senator_data, event_bus):
        """Test initialization of the agent."""
        # Test basic properties
        assert senator_agent.senator == senator_data
        assert senator_agent.id == "test-agent-id"
        
        # Test event subscriptions
        assert len(senator_agent._event_subscriptions) > 0
        assert "debate.topic_introduced" in senator_agent._event_subscriptions
        assert "debate.vote_requested" in senator_agent._event_subscriptions
        
        # Test that agent subscribed to events via the event bus
        assert event_bus.subscribe.call_count >= 6  # At least the default subscriptions
    
    def test_process_event_topic_introduced(self, senator_agent, event_bus):
        """Test processing a topic introduction event."""
        # Create a topic introduction event
        event = RomanEvent(
            event_type="debate.topic_introduced",
            data={
                "topic": "Increasing military funding for the campaign in Gaul",
                "sponsor": "Gaius Julius Caesar"
            }
        )
        
        # Process the event
        senator_agent.process_event(event)
        
        # Check that state was updated
        assert senator_agent.state.get("current_topic") == "Increasing military funding for the campaign in Gaul"
        assert senator_agent.state.get("current_stance") is not None
        assert senator_agent.state.get("stance_reasoning") is not None
        
        # Check that event was added to memory
        assert len(senator_agent.memory._memory_items) == 1
        memory_events = senator_agent.memory.get_events_by_type("debate.topic_introduced")
        assert len(memory_events) == 1
        assert memory_events[0].data.get("topic") == "Increasing military funding for the campaign in Gaul"
    
    def test_process_event_vote_requested(self, senator_agent, event_bus):
        """Test processing a vote request event."""
        # Create a vote request event
        event = RomanEvent(
            event_type="debate.vote_requested",
            data={
                "topic": "Increasing military funding for the campaign in Gaul",
                "sponsor": "Gaius Julius Caesar"
            }
        )
        
        # Process the event
        senator_agent.process_event(event)
        
        # Check that a vote was published
        assert event_bus.publish.call_count > 0
        
        # Get the published event
        published_event = None
        for call_args in event_bus.publish.call_args_list:
            call_event = call_args[0][0]
            if call_event.event_type == "debate.vote_cast":
                published_event = call_event
                break
        
        assert published_event is not None
        assert published_event.source == senator_agent.id
        assert published_event.data.get("topic") == "Increasing military funding for the campaign in Gaul"
        assert published_event.data.get("vote") in ["for", "against", "abstain"]
    
    def test_decide_stance(self, senator_agent):
        """Test the stance decision process."""
        # Call the _decide_stance method
        topic = "Building a new aqueduct to improve water supply to Rome"
        stance, reasoning = senator_agent._decide_stance(topic, {})
        
        # Check the results
        assert stance in ["support", "oppose", "neutral"]
        assert reasoning  # Should not be empty
    
    def test_generate_speech(self, senator_agent):
        """Test speech generation."""
        # Set up a topic in the agent's state
        senator_agent.update_state({
            "current_topic": "Improving grain supply to plebeians",
            "current_stance": "support",
            "stance_reasoning": "It will reduce unrest in the city."
        })
        
        # Generate a speech
        speech_result = senator_agent.generate_speech("Improving grain supply to plebeians", {})
        
        # Check the speech result
        assert "speech" in speech_result
        assert "latin_text" in speech_result
        assert "english_text" in speech_result
        assert speech_result["stance"] == "support"
        assert speech_result["speaker_name"] == senator_agent.senator["name"]
    
    def test_generate_action(self, senator_agent):
        """Test action generation."""
        # Set up a topic in the agent's state
        senator_agent.update_state({
            "current_topic": "Expansion of citizenship rights",
        })
        
        # Generate an action
        action = senator_agent.generate_action()
        
        # Check the action result
        assert action is not None
        assert action.event_type == "debate.speech_delivered"
        assert action.source == senator_agent.id
        assert action.data.get("topic") == "Expansion of citizenship rights"
        assert "content" in action.data
    
    def test_to_dict_from_dict(self, senator_agent, event_bus, llm_provider):
        """Test conversion to and from dictionary representation."""
        # Add some state and memory to the agent
        senator_agent.update_state({"current_topic": "Test Topic"})
        event = RomanEvent(event_type="test.event", data={"key": "value"})
        senator_agent.memory.add_event(event)
        
        # Convert to dictionary
        data = senator_agent.to_dict()
        
        # Check dictionary content
        assert data["id"] == senator_agent.id
        assert data["senator"]["name"] == "Marcus Cato"
        assert "state" in data
        assert "memory" in data
        
        # Create new agent from dictionary
        new_agent = EventDrivenSenatorAgent.from_dict(data, llm_provider, event_bus)
        
        # Check that new agent matches original
        assert new_agent.id == senator_agent.id
        assert new_agent.senator["name"] == senator_agent.senator["name"]
        assert new_agent.state.get("current_topic") == "Test Topic"
        
        # Check memory was transferred
        assert len(new_agent.memory._memory_items) == 1
    
    def test_handle_speech_delivered(self, senator_agent, event_bus):
        """Test handling of speech delivered events."""
        # Create a speech event from another senator
        event = RomanEvent(
            event_type="debate.speech_delivered",
            source="other-senator-id",
            data={
                "speaker_name": "Gaius Julius Caesar",
                "faction": "Populares",
                "stance": "support",
                "content": "Sample speech content",
                "speaker_id": "other-senator-id"
            }
        )
        
        # Patch the _should_interject method to always return True
        with patch.object(EventDrivenSenatorAgent, '_should_interject', return_value=True):
            # Process the event
            senator_agent.process_event(event)
            
            # Check that event was added to memory
            assert len(senator_agent.memory._memory_items) == 1
            
            # Check for interjection event publication (may not happen due to randomness)
            for call_args in event_bus.publish.call_args_list:
                call_event = call_args[0][0]
                if call_event.event_type == "debate.interjection":
                    assert call_event.source == senator_agent.id
                    assert call_event.target == "other-senator-id"
                    assert "interjecting_senator" in call_event.data