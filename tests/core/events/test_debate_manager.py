"""
Test module for DebateManager.

This module contains tests for the DebateManager class, which coordinates
debates using the event-driven architecture.
"""

import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch

from roman_senate.core.events.event_bus import EventBus
from roman_senate.core.events.debate_manager import DebateManager
from roman_senate.core.events.debate_events import (
    DebateEvent,
    DebateEventType,
    SpeechEvent,
    ReactionEvent,
    InterjectionEvent,
    InterjectionType
)


class TestDebateManager:
    """Test suite for the DebateManager class."""
    
    @pytest.fixture
    def event_bus(self):
        """Create a mock event bus for testing."""
        mock_bus = MagicMock(spec=EventBus)
        mock_bus.publish = AsyncMock()
        mock_bus.subscribe = MagicMock()
        return mock_bus
    
    @pytest.fixture
    def game_state(self):
        """Create a mock game state for testing."""
        return MagicMock()
    
    @pytest.fixture
    def debate_manager(self, event_bus, game_state):
        """Create a DebateManager for testing."""
        return DebateManager(event_bus, game_state)
    
    @pytest.fixture
    def sample_senators(self):
        """Create a list of sample senators for testing."""
        return [
            {"id": "senator1", "name": "Senator One", "faction": "Optimates", "rank": 3},
            {"id": "senator2", "name": "Senator Two", "faction": "Populares", "rank": 2},
            {"id": "senator3", "name": "Senator Three", "faction": "Optimates", "rank": 1}
        ]
    
    def test_initialization(self, debate_manager, event_bus):
        """Test initialization of the DebateManager."""
        # Check initial state
        assert debate_manager.event_bus == event_bus
        assert debate_manager.current_debate_topic is None
        assert debate_manager.current_speaker is None
        assert debate_manager.registered_speakers == []
        assert debate_manager.debate_in_progress is False
        
        # Check event subscriptions
        event_bus.subscribe.assert_any_call(InterjectionEvent.TYPE, debate_manager.handle_interjection)
        event_bus.subscribe.assert_any_call(ReactionEvent.TYPE, debate_manager.handle_reaction)
    
    @pytest.mark.asyncio
    async def test_start_debate(self, debate_manager, event_bus, sample_senators):
        """Test starting a debate."""
        # Start debate
        await debate_manager.start_debate("Test Topic", sample_senators)
        
        # Check debate state
        assert debate_manager.debate_in_progress is True
        assert debate_manager.current_debate_topic == "Test Topic"
        assert debate_manager.registered_speakers == sample_senators
        
        # Check event publication
        event_bus.publish.assert_called_once()
        published_event = event_bus.publish.call_args[0][0]
        
        assert isinstance(published_event, DebateEvent)
        assert published_event.debate_event_type == DebateEventType.DEBATE_START
        assert published_event.metadata["topic"] == "Test Topic"
        assert published_event.metadata["participant_count"] == 3
        assert "Senator One" in published_event.metadata["participants"]
        assert "Senator Two" in published_event.metadata["participants"]
        assert "Senator Three" in published_event.metadata["participants"]
    
    @pytest.mark.asyncio
    async def test_start_debate_already_in_progress(self, debate_manager, event_bus, sample_senators):
        """Test starting a debate when one is already in progress."""
        # Start first debate
        await debate_manager.start_debate("First Topic", sample_senators)
        event_bus.publish.reset_mock()
        
        # Try to start second debate
        await debate_manager.start_debate("Second Topic", sample_senators)
        
        # Check that state wasn't changed and no event was published
        assert debate_manager.current_debate_topic == "First Topic"
        event_bus.publish.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_end_debate(self, debate_manager, event_bus, sample_senators):
        """Test ending a debate."""
        # Start debate
        await debate_manager.start_debate("Test Topic", sample_senators)
        event_bus.publish.reset_mock()
        
        # End debate
        await debate_manager.end_debate()
        
        # Check debate state
        assert debate_manager.debate_in_progress is False
        assert debate_manager.current_debate_topic is None
        assert debate_manager.current_speaker is None
        assert debate_manager.registered_speakers == []
        
        # Check event publication
        event_bus.publish.assert_called_once()
        published_event = event_bus.publish.call_args[0][0]
        
        assert isinstance(published_event, DebateEvent)
        assert published_event.debate_event_type == DebateEventType.DEBATE_END
        assert published_event.metadata["topic"] == "Test Topic"
        assert published_event.metadata["participant_count"] == 3
    
    @pytest.mark.asyncio
    async def test_end_debate_not_in_progress(self, debate_manager, event_bus):
        """Test ending a debate when none is in progress."""
        # End debate without starting one
        await debate_manager.end_debate()
        
        # Check that no event was published
        event_bus.publish.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_register_speaker(self, debate_manager, sample_senators):
        """Test registering a speaker."""
        # Register a speaker
        new_speaker = {"id": "senator4", "name": "Senator Four", "faction": "Populares"}
        await debate_manager.register_speaker(new_speaker)
        
        # Check that speaker was added
        assert new_speaker in debate_manager.registered_speakers
    
    @pytest.mark.asyncio
    async def test_register_speaker_duplicate(self, debate_manager, sample_senators):
        """Test registering a speaker that's already registered."""
        # Register speakers
        for senator in sample_senators:
            await debate_manager.register_speaker(senator)
        
        # Register a speaker again
        await debate_manager.register_speaker(sample_senators[0])
        
        # Check that speaker wasn't added again
        assert debate_manager.registered_speakers.count(sample_senators[0]) == 1
    
    @pytest.mark.asyncio
    async def test_next_speaker(self, debate_manager, event_bus, sample_senators):
        """Test getting the next speaker."""
        # Register speakers
        for senator in sample_senators:
            await debate_manager.register_speaker(senator)
        
        # Get next speaker
        next_speaker = await debate_manager.next_speaker()
        
        # Check that correct speaker was returned and set as current
        assert next_speaker == sample_senators[0]
        assert debate_manager.current_speaker == sample_senators[0]
        
        # Check that speaker was removed from list
        assert sample_senators[0] not in debate_manager.registered_speakers
        
        # Check event publication
        event_bus.publish.assert_called_once()
        published_event = event_bus.publish.call_args[0][0]
        
        assert isinstance(published_event, DebateEvent)
        assert published_event.debate_event_type == DebateEventType.SPEAKER_CHANGE
        assert published_event.source == sample_senators[0]
        assert published_event.metadata["speaker_name"] == "Senator One"
        assert published_event.metadata["speaker_faction"] == "Optimates"
    
    @pytest.mark.asyncio
    async def test_next_speaker_empty(self, debate_manager, event_bus):
        """Test getting the next speaker when none are registered."""
        # Get next speaker with empty list
        next_speaker = await debate_manager.next_speaker()
        
        # Check that none was returned
        assert next_speaker is None
        
        # Check that no event was published
        event_bus.publish.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_publish_speech(self, debate_manager, event_bus, sample_senators):
        """Test publishing a speech event."""
        with patch('roman_senate.core.events.debate_manager.add_to_debate_history') as mock_add_history:
            # Publish speech
            speech_event = await debate_manager.publish_speech(
                speaker=sample_senators[0],
                topic="Test Topic",
                latin_content="Latin content",
                english_content="English content",
                stance="support",
                key_points=["Point 1", "Point 2"]
            )
            
            # Check event publication
            event_bus.publish.assert_called_once()
            published_event = event_bus.publish.call_args[0][0]
            
            assert isinstance(published_event, SpeechEvent)
            assert published_event == speech_event
            assert published_event.speaker == sample_senators[0]
            assert published_event.metadata["topic"] == "Test Topic"
            assert published_event.latin_content == "Latin content"
            assert published_event.english_content == "English content"
            assert published_event.stance == "support"
            assert published_event.key_points == ["Point 1", "Point 2"]
            
            # Check debate history update
            mock_add_history.assert_called_once()
            history_data = mock_add_history.call_args[0][0]
            
            assert history_data["senator_id"] == "senator1"
            assert history_data["senator_name"] == "Senator One"
            assert history_data["faction"] == "Optimates"
            assert history_data["stance"] == "support"
            assert "Latin content" in history_data["speech"]
            assert "English content" in history_data["speech"]
            assert history_data["key_points"] == ["Point 1", "Point 2"]
    
    @pytest.mark.asyncio
    async def test_handle_interjection_higher_rank(self, debate_manager, sample_senators, caplog):
        """Test handling an interjection from a higher-ranked senator."""
        # Set up debate state
        debate_manager.debate_in_progress = True
        debate_manager.current_speaker = sample_senators[2]  # Rank 1
        
        # Create interjection from higher-ranked senator
        interjection = InterjectionEvent(
            interjector=sample_senators[0],  # Rank 3
            target_speaker=sample_senators[2],
            interjection_type=InterjectionType.CHALLENGE,
            latin_content="Latin interjection",
            english_content="English interjection"
        )
        
        # Handle interjection
        with caplog.at_level("INFO"):
            await debate_manager.handle_interjection(interjection)
            
            # Check that interjection was allowed (logged)
            assert "INTERJECTION: English interjection" in caplog.text
            assert "Allowed: True" in caplog.text
    
    @pytest.mark.asyncio
    async def test_handle_interjection_lower_rank(self, debate_manager, sample_senators, caplog):
        """Test handling an interjection from a lower-ranked senator."""
        # Set up debate state
        debate_manager.debate_in_progress = True
        debate_manager.current_speaker = sample_senators[0]  # Rank 3
        
        # Create interjection from lower-ranked senator
        interjection = InterjectionEvent(
            interjector=sample_senators[2],  # Rank 1
            target_speaker=sample_senators[0],
            interjection_type=InterjectionType.CHALLENGE,
            latin_content="Latin interjection",
            english_content="English interjection"
        )
        
        # Handle interjection
        with caplog.at_level("INFO"):
            await debate_manager.handle_interjection(interjection)
            
            # Check that interjection was not allowed
            assert "INTERJECTION: English interjection" not in caplog.text
            assert "Allowed: False" in caplog.text
    
    @pytest.mark.asyncio
    async def test_handle_interjection_equal_rank_procedural(self, debate_manager, sample_senators, caplog):
        """Test handling a procedural interjection from an equal-ranked senator."""
        # Set up two senators with equal rank
        senator1 = {"id": "senator1", "name": "Senator One", "faction": "Optimates", "rank": 2}
        senator2 = {"id": "senator2", "name": "Senator Two", "faction": "Populares", "rank": 2}
        
        # Set up debate state
        debate_manager.debate_in_progress = True
        debate_manager.current_speaker = senator1
        
        # Create procedural interjection from equal-ranked senator
        interjection = InterjectionEvent(
            interjector=senator2,
            target_speaker=senator1,
            interjection_type=InterjectionType.PROCEDURAL,
            latin_content="Ad ordinem!",
            english_content="Point of order!"
        )
        
        # Handle interjection
        with caplog.at_level("INFO"):
            await debate_manager.handle_interjection(interjection)
            
            # Check that procedural interjection was allowed
            assert "INTERJECTION: Point of order!" in caplog.text
            assert "Allowed: True" in caplog.text
    
    @pytest.mark.asyncio
    async def test_handle_interjection_equal_rank_non_procedural(self, debate_manager, sample_senators, caplog):
        """Test handling a non-procedural interjection from an equal-ranked senator."""
        # Set up two senators with equal rank
        senator1 = {"id": "senator1", "name": "Senator One", "faction": "Optimates", "rank": 2}
        senator2 = {"id": "senator2", "name": "Senator Two", "faction": "Populares", "rank": 2}
        
        # Set up debate state
        debate_manager.debate_in_progress = True
        debate_manager.current_speaker = senator1
        
        # Create non-procedural interjection from equal-ranked senator
        interjection = InterjectionEvent(
            interjector=senator2,
            target_speaker=senator1,
            interjection_type=InterjectionType.CHALLENGE,
            latin_content="Nego!",
            english_content="I disagree!"
        )
        
        # Handle interjection
        with caplog.at_level("INFO"):
            await debate_manager.handle_interjection(interjection)
            
            # Check that non-procedural interjection was not allowed
            assert "INTERJECTION: I disagree!" not in caplog.text
            assert "Allowed: False" in caplog.text
    
    @pytest.mark.asyncio
    async def test_handle_interjection_no_debate(self, debate_manager, sample_senators, caplog):
        """Test handling an interjection when no debate is in progress."""
        # Ensure no debate is in progress
        debate_manager.debate_in_progress = False
        
        # Create interjection
        interjection = InterjectionEvent(
            interjector=sample_senators[0],
            target_speaker=sample_senators[1],
            interjection_type=InterjectionType.CHALLENGE,
            latin_content="Latin interjection",
            english_content="English interjection"
        )
        
        # Handle interjection
        with caplog.at_level("WARNING"):
            await debate_manager.handle_interjection(interjection)
            
            # Check warning was logged
            assert "Interjection received but no debate in progress" in caplog.text
    
    @pytest.mark.asyncio
    async def test_handle_reaction(self, debate_manager, sample_senators, caplog):
        """Test handling a reaction event."""
        # Set up debate state
        debate_manager.debate_in_progress = True
        
        # Create target event
        target_event = SpeechEvent(
            speaker=sample_senators[0],
            topic="Test Topic",
            latin_content="Latin content",
            english_content="English content",
            stance="support"
        )
        
        # Create reaction
        reaction = ReactionEvent(
            reactor=sample_senators[1],
            target_event=target_event,
            reaction_type="agreement",
            content="Nods in agreement"
        )
        
        # Handle reaction
        with caplog.at_level("INFO"):
            await debate_manager.handle_reaction(reaction)
            
            # Check that reaction was logged
            assert "Reaction from Senator Two" in caplog.text
            assert "agreement - Nods in agreement" in caplog.text
    
    @pytest.mark.asyncio
    async def test_handle_reaction_no_debate(self, debate_manager, sample_senators, caplog):
        """Test handling a reaction when no debate is in progress."""
        # Ensure no debate is in progress
        debate_manager.debate_in_progress = False
        
        # Create target event
        target_event = SpeechEvent(
            speaker=sample_senators[0],
            topic="Test Topic",
            latin_content="Latin content",
            english_content="English content",
            stance="support"
        )
        
        # Create reaction
        reaction = ReactionEvent(
            reactor=sample_senators[1],
            target_event=target_event,
            reaction_type="agreement",
            content="Nods in agreement"
        )
        
        # Handle reaction
        with caplog.at_level("WARNING"):
            await debate_manager.handle_reaction(reaction)
            
            # Check warning was logged
            assert "Reaction received but no debate in progress" in caplog.text
    
    @pytest.mark.asyncio
    async def test_conduct_debate(self, debate_manager, event_bus, sample_senators):
        """Test conducting a full debate."""
        with patch('roman_senate.core.events.debate_manager.display_speech') as mock_display, \
             patch('roman_senate.core.events.debate_manager.add_to_debate_history') as mock_add_history:
            # Conduct debate
            speeches = await debate_manager.conduct_debate("Test Topic", sample_senators)
            
            # Check debate start/end events
            assert event_bus.publish.call_count >= 2 + len(sample_senators)  # start + end + speeches
            
            # Check that all senators got to speak
            assert len(speeches) == 3
            for i, senator in enumerate(sample_senators):
                assert speeches[i]["senator_id"] == senator["id"]
                assert speeches[i]["senator_name"] == senator["name"]
                
            # Check that display_speech was called for each speech
            assert mock_display.call_count == 3
            
            # Check that debate was properly ended
            assert debate_manager.debate_in_progress is False
            assert debate_manager.current_debate_topic is None
            assert debate_manager.current_speaker is None
            assert debate_manager.registered_speakers == []