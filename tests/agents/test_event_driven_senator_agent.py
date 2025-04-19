"""
Test module for EventDrivenSenatorAgent.

This module contains tests for the EventDrivenSenatorAgent class, which extends
the SenatorAgent with event-driven capabilities.
"""

import pytest
import asyncio
import random
from unittest.mock import MagicMock, AsyncMock, patch

from roman_senate.agents.event_driven_senator_agent import EventDrivenSenatorAgent
from roman_senate.agents.event_memory import EventMemory
from roman_senate.core.events.event_bus import EventBus
from roman_senate.core.events.debate_events import (
    DebateEvent,
    DebateEventType,
    SpeechEvent,
    ReactionEvent,
    InterjectionEvent,
    InterjectionType
)


class TestEventDrivenSenatorAgent:
    """Test suite for the EventDrivenSenatorAgent class."""
    
    @pytest.fixture
    def sample_senator(self):
        """Create a sample senator for testing."""
        return {
            "id": "senator_id",
            "name": "Test Senator",
            "faction": "Optimates",
            "rank": 3,
            "personality": {
                "ambition": 0.7,
                "loyalty": 0.5,
                "composure": 0.6
            }
        }
    
    @pytest.fixture
    def event_bus(self):
        """Create a mock event bus for testing."""
        mock_bus = MagicMock(spec=EventBus)
        mock_bus.subscribe = MagicMock()
        mock_bus.publish = AsyncMock()
        return mock_bus
    
    @pytest.fixture
    def llm_provider(self):
        """Create a mock LLM provider for testing."""
        mock_provider = MagicMock()
        mock_provider.generate_text = AsyncMock(return_value="Generated text")
        return mock_provider
    
    @pytest.fixture
    def senator_agent(self, sample_senator, llm_provider, event_bus):
        """Create an EventDrivenSenatorAgent for testing."""
        # Patch the EventMemory initialization
        with patch('roman_senate.agents.event_driven_senator_agent.EventMemory'):
            agent = EventDrivenSenatorAgent(sample_senator, llm_provider, event_bus)
            
            # Replace memory with a real EventMemory for testing
            agent.memory = EventMemory()
            
            # Manually set some properties to ensure consistent testing
            agent.current_stance = "neutral"
            agent.active_debate_topic = "Test Topic"
            
            return agent
    
    @pytest.fixture
    def sample_speaker(self):
        """Create a sample speaker for testing."""
        return {
            "id": "speaker_id",
            "name": "Test Speaker",
            "faction": "Populares",
            "rank": 2
        }
    
    @pytest.fixture
    def sample_speech_event(self, sample_speaker):
        """Create a sample speech event for testing."""
        return SpeechEvent(
            speaker=sample_speaker,
            topic="Test Topic",
            latin_content="Latin speech content",
            english_content="English speech content",
            stance="support",
            key_points=["Point 1", "Point 2"]
        )
    
    @pytest.fixture
    def sample_debate_start_event(self):
        """Create a sample debate start event for testing."""
        return DebateEvent(
            debate_event_type=DebateEventType.DEBATE_START,
            topic="Test Topic",
            metadata={
                "participant_count": 5,
                "participants": ["Senator A", "Senator B", "Test Senator", "Senator D", "Senator E"]
            }
        )
    
    def test_initialization(self, senator_agent, sample_senator, event_bus):
        """Test initialization of EventDrivenSenatorAgent."""
        # Check senator properties
        assert senator_agent.senator == sample_senator
        assert senator_agent.name == "Test Senator"
        assert senator_agent.faction == "Optimates"
        
        # Check initialization state
        assert senator_agent.current_stance is not None  # We set it manually in the fixture
        assert isinstance(senator_agent.memory, EventMemory)
        assert senator_agent.event_bus == event_bus
        assert senator_agent.debate_in_progress is False
        
        # Check event subscriptions
        event_bus.subscribe.assert_any_call("speech", senator_agent.handle_speech_event)
        event_bus.subscribe.assert_any_call("debate", senator_agent.handle_debate_event)
    
    @pytest.mark.asyncio
    async def test_handle_speech_event_own_speech(self, senator_agent, sample_senator):
        """Test handling own speech event (should be ignored)."""
        # Create a speech from the senator themselves
        own_speech = SpeechEvent(
            speaker=sample_senator,
            topic="Test Topic",
            latin_content="Latin content",
            english_content="English content",
            stance="support"
        )
        
        # Add spy on memory.record_event
        senator_agent.memory.record_event = MagicMock()
        
        # Handle the speech
        await senator_agent.handle_speech_event(own_speech)
        
        # Check that the speech was ignored (not recorded)
        senator_agent.memory.record_event.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_handle_speech_event(self, senator_agent, sample_speech_event):
        """Test handling a speech event from another senator."""
        # Patch internal methods to avoid random behavior and simplify testing
        with patch.object(senator_agent, '_should_react_to_speech', AsyncMock(return_value=False)), \
             patch.object(senator_agent, '_should_interject', AsyncMock(return_value=False)), \
             patch.object(senator_agent, '_consider_stance_change', AsyncMock()):
            
            # Add spy on memory methods
            senator_agent.memory.record_event = MagicMock()
            senator_agent.memory.add_interaction = MagicMock()
            
            # Handle the speech
            await senator_agent.handle_speech_event(sample_speech_event)
            
            # Check that the event was recorded
            senator_agent.memory.record_event.assert_called_once_with(sample_speech_event)
            
            # Check that the interaction was recorded
            senator_agent.memory.add_interaction.assert_called_once()
            args = senator_agent.memory.add_interaction.call_args[0]
            assert args[0] == "Test Speaker"
            assert args[1] == "heard_speech"
            assert args[2]["topic"] == "Test Topic"
            assert args[2]["stance"] == "support"
            
            # Check that the current speaker was updated
            assert senator_agent.current_speaker == sample_speech_event.speaker
            
            # Check that internal methods were called
            senator_agent._should_react_to_speech.assert_called_once_with(sample_speech_event)
            senator_agent._should_interject.assert_called_once_with(sample_speech_event)
            senator_agent._consider_stance_change.assert_called_once_with(sample_speech_event)
    
    @pytest.mark.asyncio
    async def test_handle_speech_event_with_reaction(self, senator_agent, sample_speech_event):
        """Test handling a speech event that triggers a reaction."""
        # Patch internal methods to force reaction but no interjection
        with patch.object(senator_agent, '_should_react_to_speech', AsyncMock(return_value=True)), \
             patch.object(senator_agent, '_should_interject', AsyncMock(return_value=False)), \
             patch.object(senator_agent, '_consider_stance_change', AsyncMock()), \
             patch.object(senator_agent, '_generate_and_publish_reaction', AsyncMock()):
            
            # Handle the speech
            await senator_agent.handle_speech_event(sample_speech_event)
            
            # Check that reaction was generated
            senator_agent._generate_and_publish_reaction.assert_called_once_with(sample_speech_event)
    
    @pytest.mark.asyncio
    async def test_handle_speech_event_with_interjection(self, senator_agent, sample_speech_event):
        """Test handling a speech event that triggers an interjection."""
        # Patch internal methods to force interjection but no reaction
        with patch.object(senator_agent, '_should_react_to_speech', AsyncMock(return_value=False)), \
             patch.object(senator_agent, '_should_interject', AsyncMock(return_value=True)), \
             patch.object(senator_agent, '_consider_stance_change', AsyncMock()), \
             patch.object(senator_agent, '_generate_and_publish_interjection', AsyncMock()):
            
            # Handle the speech
            await senator_agent.handle_speech_event(sample_speech_event)
            
            # Check that interjection was generated
            senator_agent._generate_and_publish_interjection.assert_called_once_with(sample_speech_event)
    
    @pytest.mark.asyncio
    async def test_handle_debate_start_event(self, senator_agent, sample_debate_start_event):
        """Test handling a debate start event."""
        # Add spy on memory.record_event
        senator_agent.memory.record_event = MagicMock()
        
        # Mock decide_stance to avoid actual LLM calls
        senator_agent.decide_stance = AsyncMock()
        
        # Handle the debate start event
        await senator_agent.handle_debate_event(sample_debate_start_event)
        
        # Check that the event was recorded
        senator_agent.memory.record_event.assert_called_once_with(sample_debate_start_event)
        
        # Check that debate state was updated
        assert senator_agent.debate_in_progress is True
        assert senator_agent.active_debate_topic == "Test Topic"
        
        # Check that stance was decided
        senator_agent.decide_stance.assert_called_once_with("Test Topic", {})
    
    @pytest.mark.asyncio
    async def test_handle_debate_end_event(self, senator_agent):
        """Test handling a debate end event."""
        # Set up debate in progress
        senator_agent.debate_in_progress = True
        senator_agent.active_debate_topic = "Test Topic"
        senator_agent.current_speaker = {"name": "Current Speaker"}
        
        # Create debate end event
        debate_end_event = DebateEvent(
            debate_event_type=DebateEventType.DEBATE_END,
            topic="Test Topic"
        )
        
        # Add spy on memory.record_event
        senator_agent.memory.record_event = MagicMock()
        
        # Handle the debate end event
        await senator_agent.handle_debate_event(debate_end_event)
        
        # Check that the event was recorded
        senator_agent.memory.record_event.assert_called_once_with(debate_end_event)
        
        # Check that debate state was updated
        assert senator_agent.debate_in_progress is False
        assert senator_agent.active_debate_topic is None
        assert senator_agent.current_speaker is None
    
    @pytest.mark.asyncio
    async def test_handle_speaker_change_event(self, senator_agent, sample_speaker):
        """Test handling a speaker change event."""
        # Create speaker change event
        speaker_change_event = DebateEvent(
            debate_event_type=DebateEventType.SPEAKER_CHANGE,
            topic="Test Topic",
            source=sample_speaker,
            metadata={
                "speaker_name": sample_speaker["name"],
                "speaker_faction": sample_speaker["faction"]
            }
        )
        
        # Add spy on memory.record_event
        senator_agent.memory.record_event = MagicMock()
        
        # Handle the speaker change event
        await senator_agent.handle_debate_event(speaker_change_event)
        
        # Check that the event was recorded
        senator_agent.memory.record_event.assert_called_once_with(speaker_change_event)
        
        # Check that current speaker was updated
        assert senator_agent.current_speaker == sample_speaker
    
    @pytest.mark.asyncio
    async def test_should_react_to_speech(self, senator_agent, sample_speech_event):
        """Test the logic for deciding whether to react to a speech."""
        # Mock random for deterministic testing
        with patch('random.random', return_value=0.1):  # Low value to ensure reaction
            # Default probability is 0.3, so this should return True
            result = await senator_agent._should_react_to_speech(sample_speech_event)
            assert result is True
        
        with patch('random.random', return_value=0.9):  # High value to ensure no reaction
            # Default probability is 0.3, so this should return False
            result = await senator_agent._should_react_to_speech(sample_speech_event)
            assert result is False
    
    @pytest.mark.asyncio
    async def test_should_interject(self, senator_agent, sample_speech_event):
        """Test the logic for deciding whether to interject during a speech."""
        # Mock random for deterministic testing
        with patch('random.random', return_value=0.05):  # Low value to ensure interjection
            # Default probability is 0.1, so this should return True
            result = await senator_agent._should_interject(sample_speech_event)
            assert result is True
        
        with patch('random.random', return_value=0.5):  # High value to ensure no interjection
            # Default probability is 0.1, so this should return False
            result = await senator_agent._should_interject(sample_speech_event)
            assert result is False
    
    @pytest.mark.asyncio
    async def test_generate_and_publish_reaction(self, senator_agent, sample_speech_event, event_bus):
        """Test generating and publishing a reaction."""
        # Patch _generate_reaction_content to return a predictable value
        with patch.object(senator_agent, '_generate_reaction_content', AsyncMock(return_value="Test reaction")):
            # Generate a reaction
            await senator_agent._generate_and_publish_reaction(sample_speech_event)
            
            # Check that reaction was published
            event_bus.publish.assert_called_once()
            published_event = event_bus.publish.call_args[0][0]
            
            assert isinstance(published_event, ReactionEvent)
            assert published_event.reactor == senator_agent.senator
            assert published_event.target_event_id == sample_speech_event.event_id
            assert published_event.content == "Test reaction"
            
            # Check that reaction was recorded in memory
            assert len(senator_agent.memory.reaction_history) == 1
            assert senator_agent.memory.reaction_history[0]["event_id"] == sample_speech_event.event_id
    
    @pytest.mark.asyncio
    async def test_generate_reaction_content(self, senator_agent, sample_speech_event):
        """Test generating reaction content."""
        # Test different reaction types
        reaction_types = ["agreement", "disagreement", "interest", "boredom", "skepticism", "neutral"]
        
        for reaction_type in reaction_types:
            content = await senator_agent._generate_reaction_content(sample_speech_event, reaction_type)
            
            # Check that content is a non-empty string
            assert isinstance(content, str)
            assert len(content) > 0
            
            # Check that speaker name is included in most types
            if reaction_type in ["agreement", "disagreement", "interest"]:
                assert "Test Speaker" in content
    
    @pytest.mark.asyncio
    async def test_generate_and_publish_interjection(self, senator_agent, sample_speech_event, event_bus):
        """Test generating and publishing an interjection."""
        # Patch internal methods to return predictable values
        with patch.object(senator_agent, '_determine_interjection_type', AsyncMock(return_value=InterjectionType.CHALLENGE)), \
             patch.object(senator_agent, '_generate_interjection_content', AsyncMock(return_value=("Latin content", "English content"))):
            
            # Generate an interjection
            await senator_agent._generate_and_publish_interjection(sample_speech_event)
            
            # Check that interjection was published
            event_bus.publish.assert_called_once()
            published_event = event_bus.publish.call_args[0][0]
            
            assert isinstance(published_event, InterjectionEvent)
            assert published_event.interjector == senator_agent.senator
            assert published_event.target_speaker == sample_speech_event.speaker
            assert published_event.interjection_type == InterjectionType.CHALLENGE
            assert published_event.latin_content == "Latin content"
            assert published_event.english_content == "English content"
            assert published_event.target_speech_id == sample_speech_event.speech_id
            
            # Check that interjection was recorded in memory
            senator_agent.memory.record_event.assert_called_once_with(published_event)
    
    @pytest.mark.asyncio
    async def test_determine_interjection_type(self, senator_agent, sample_speech_event):
        """Test determining the interjection type."""
        # Patch random.choices to return a predictable value
        with patch('random.choices', return_value=[InterjectionType.SUPPORT]):
            result = await senator_agent._determine_interjection_type(sample_speech_event)
            assert result == InterjectionType.SUPPORT
    
    @pytest.mark.asyncio
    async def test_generate_interjection_content(self, senator_agent):
        """Test generating interjection content."""
        # Test different interjection types
        for interjection_type in InterjectionType:
            latin, english = await senator_agent._generate_interjection_content(
                "Test Speaker",
                interjection_type
            )
            
            # Check that content is non-empty strings
            assert isinstance(latin, str)
            assert isinstance(english, str)
            assert len(latin) > 0
            assert len(english) > 0
    
    @pytest.mark.asyncio
    async def test_consider_stance_change_same_topic(self, senator_agent, sample_speech_event):
        """Test considering stance change when speech is on the same topic."""
        # Set up agent with current stance
        senator_agent.current_stance = "neutral"
        senator_agent.active_debate_topic = "Test Topic"
        
        # Mock random for deterministic testing - ensure stance change
        with patch('random.random', return_value=0.01):
            # Consider stance change
            await senator_agent._consider_stance_change(sample_speech_event)
            
            # Since sample_speech_event has "support" stance, and we were "neutral",
            # agent should adopt "support" stance
            assert senator_agent.current_stance == "support"
            
            # Check that stance change was recorded
            assert "Test Topic" in senator_agent.memory.stance_changes
            change = senator_agent.memory.stance_changes["Test Topic"][0]
            assert change["old_stance"] == "neutral"
            assert change["new_stance"] == "support"
    
    @pytest.mark.asyncio
    async def test_consider_stance_change_different_topic(self, senator_agent, sample_speech_event):
        """Test considering stance change when speech is on a different topic."""
        # Set up agent with current stance on a different topic
        senator_agent.current_stance = "oppose"
        senator_agent.active_debate_topic = "Different Topic"
        
        # Consider stance change
        await senator_agent._consider_stance_change(sample_speech_event)
        
        # Should not change stance for a different topic
        assert senator_agent.current_stance == "oppose"
    
    @pytest.mark.asyncio
    async def test_consider_stance_change_no_stance(self, senator_agent, sample_speech_event):
        """Test considering stance change when agent has no stance."""
        # Set up agent with no stance
        senator_agent.current_stance = None
        senator_agent.active_debate_topic = "Test Topic"
        
        # Consider stance change
        await senator_agent._consider_stance_change(sample_speech_event)
        
        # Should not change from None
        assert senator_agent.current_stance is None
    
    @pytest.mark.asyncio
    async def test_consider_stance_change_already_agrees(self, senator_agent, sample_speech_event):
        """Test considering stance change when agent already agrees with the speaker."""
        # Set up agent with same stance as speech
        senator_agent.current_stance = "support"
        senator_agent.active_debate_topic = "Test Topic"
        
        # Mock random for deterministic testing - ensure stance change attempt
        with patch('random.random', return_value=0.01):
            # Consider stance change
            await senator_agent._consider_stance_change(sample_speech_event)
            
            # Should not change when already in agreement
            assert senator_agent.current_stance == "support"
    
    @pytest.mark.asyncio
    async def test_consider_stance_change_disagreement_to_neutral(self, senator_agent, sample_speech_event):
        """Test considering stance change from disagreement to neutral."""
        # Set up agent with opposing stance
        senator_agent.current_stance = "oppose"
        senator_agent.active_debate_topic = "Test Topic"
        
        # Mock random for deterministic testing - ensure stance change
        with patch('random.random', return_value=0.01):
            # Consider stance change
            await senator_agent._consider_stance_change(sample_speech_event)
            
            # Should change from oppose to neutral, not directly to support
            assert senator_agent.current_stance == "neutral"