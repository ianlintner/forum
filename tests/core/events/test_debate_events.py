"""
Test module for debate event classes.

This module contains unit tests for the debate-specific event classes:
- DebateEvent
- SpeechEvent
- ReactionEvent
- InterjectionEvent
"""

import pytest
from roman_senate.core.events.base import Event
from roman_senate.core.events.debate_events import (
    DebateEvent,
    DebateEventType,
    SpeechEvent,
    ReactionEvent,
    InterjectionEvent,
    InterjectionType
)


class TestDebateEventType:
    """Test suite for the DebateEventType enum."""
    
    def test_debate_event_types(self):
        """Test that all expected debate event types are defined."""
        assert DebateEventType.DEBATE_START.value == "debate_start"
        assert DebateEventType.DEBATE_END.value == "debate_end"
        assert DebateEventType.SPEAKER_CHANGE.value == "speaker_change"
        assert DebateEventType.TOPIC_CHANGE.value == "topic_change"


class TestInterjectionType:
    """Test suite for the InterjectionType enum."""
    
    def test_interjection_types(self):
        """Test that all expected interjection types are defined."""
        assert InterjectionType.SUPPORT.value == "support"
        assert InterjectionType.CHALLENGE.value == "challenge"
        assert InterjectionType.PROCEDURAL.value == "procedural"
        assert InterjectionType.EMOTIONAL.value == "emotional"
        assert InterjectionType.INFORMATIONAL.value == "informational"


class TestDebateEvent:
    """Test suite for the DebateEvent class."""
    
    @pytest.fixture
    def sample_debate_event(self):
        """Create a sample debate event for testing."""
        return DebateEvent(
            debate_event_type=DebateEventType.DEBATE_START,
            topic="Test topic",
            source={"name": "Test source"},
            metadata={"key": "value"}
        )
    
    def test_initialization(self, sample_debate_event):
        """Test initialization of a DebateEvent."""
        # Check base Event properties
        assert sample_debate_event.event_type == "debate"
        assert sample_debate_event.source == {"name": "Test source"}
        
        # Check DebateEvent-specific properties
        assert sample_debate_event.debate_event_type == DebateEventType.DEBATE_START
        assert sample_debate_event.metadata["topic"] == "Test topic"
        assert sample_debate_event.metadata["debate_event_type"] == "debate_start"
        assert sample_debate_event.metadata["key"] == "value"
    
    def test_initialization_without_topic(self):
        """Test initialization without a topic."""
        event = DebateEvent(
            debate_event_type=DebateEventType.DEBATE_END,
            source={"name": "Test source"}
        )
        
        # Check base Event properties
        assert event.event_type == "debate"
        assert event.source == {"name": "Test source"}
        
        # Check DebateEvent-specific properties
        assert event.debate_event_type == DebateEventType.DEBATE_END
        assert "topic" not in event.metadata
        assert event.metadata["debate_event_type"] == "debate_end"
    
    def test_to_dict(self, sample_debate_event):
        """Test the to_dict method."""
        event_dict = sample_debate_event.to_dict()
        
        # Check base Event properties
        assert event_dict["event_type"] == "debate"
        assert event_dict["source"] == "Test source"
        
        # Check DebateEvent-specific properties
        assert event_dict["debate_event_type"] == "debate_start"
        assert event_dict["metadata"]["topic"] == "Test topic"
        assert event_dict["metadata"]["debate_event_type"] == "debate_start"
        assert event_dict["metadata"]["key"] == "value"


class TestSpeechEvent:
    """Test suite for the SpeechEvent class."""
    
    @pytest.fixture
    def sample_speaker(self):
        """Create a sample speaker for testing."""
        return {
            "id": "speaker_id",
            "name": "Test speaker",
            "faction": "Test faction",
            "rank": 3
        }
    
    @pytest.fixture
    def sample_speech_event(self, sample_speaker):
        """Create a sample speech event for testing."""
        return SpeechEvent(
            speaker=sample_speaker,
            topic="Test topic",
            latin_content="Latin speech content",
            english_content="English speech content",
            stance="support",
            key_points=["Point 1", "Point 2"]
        )
    
    def test_initialization(self, sample_speech_event, sample_speaker):
        """Test initialization of a SpeechEvent."""
        # Check base Event properties
        assert sample_speech_event.event_type == "speech"
        assert sample_speech_event.source == sample_speaker
        
        # Check SpeechEvent-specific properties
        assert sample_speech_event.speech_id == sample_speech_event.event_id
        assert sample_speech_event.speaker == sample_speaker
        assert sample_speech_event.latin_content == "Latin speech content"
        assert sample_speech_event.english_content == "English speech content"
        assert sample_speech_event.stance == "support"
        assert sample_speech_event.key_points == ["Point 1", "Point 2"]
        
        # Check metadata
        assert sample_speech_event.metadata["topic"] == "Test topic"
        assert sample_speech_event.metadata["stance"] == "support"
        assert sample_speech_event.metadata["speaker_name"] == "Test speaker"
        assert sample_speech_event.metadata["speaker_faction"] == "Test faction"
    
    def test_initialization_without_key_points(self, sample_speaker):
        """Test initialization without key points."""
        event = SpeechEvent(
            speaker=sample_speaker,
            topic="Test topic",
            latin_content="Latin speech content",
            english_content="English speech content",
            stance="oppose"
        )
        
        # Check key_points defaults to empty list
        assert event.key_points == []
    
    def test_to_dict(self, sample_speech_event, sample_speaker):
        """Test the to_dict method."""
        event_dict = sample_speech_event.to_dict()
        
        # Check base Event properties
        assert event_dict["event_type"] == "speech"
        assert event_dict["source"] == "Test speaker"
        
        # Check SpeechEvent-specific properties
        assert event_dict["speech_id"] == sample_speech_event.event_id
        assert event_dict["latin_content"] == "Latin speech content"
        assert event_dict["english_content"] == "English speech content"
        assert event_dict["stance"] == "support"
        assert event_dict["key_points"] == ["Point 1", "Point 2"]
        
        # Check speaker information
        assert event_dict["speaker"]["id"] == "speaker_id"
        assert event_dict["speaker"]["name"] == "Test speaker"
        assert event_dict["speaker"]["faction"] == "Test faction"


class TestReactionEvent:
    """Test suite for the ReactionEvent class."""
    
    @pytest.fixture
    def sample_reactor(self):
        """Create a sample reactor for testing."""
        return {
            "id": "reactor_id",
            "name": "Test reactor",
            "faction": "Test faction"
        }
    
    @pytest.fixture
    def sample_target_event(self, sample_speaker):
        """Create a sample target event for testing."""
        return SpeechEvent(
            speaker=sample_speaker,
            topic="Test topic",
            latin_content="Latin speech content",
            english_content="English speech content",
            stance="support"
        )
    
    @pytest.fixture
    def sample_speaker(self):
        """Create a sample speaker for testing."""
        return {
            "id": "speaker_id",
            "name": "Test speaker",
            "faction": "Test faction"
        }
    
    @pytest.fixture
    def sample_reaction_event(self, sample_reactor, sample_target_event):
        """Create a sample reaction event for testing."""
        return ReactionEvent(
            reactor=sample_reactor,
            target_event=sample_target_event,
            reaction_type="agreement",
            content="Nods in agreement"
        )
    
    def test_initialization(self, sample_reaction_event, sample_reactor, sample_target_event):
        """Test initialization of a ReactionEvent."""
        # Check base Event properties
        assert sample_reaction_event.event_type == "reaction"
        assert sample_reaction_event.source == sample_reactor
        
        # Check ReactionEvent-specific properties
        assert sample_reaction_event.reactor == sample_reactor
        assert sample_reaction_event.target_event_id == sample_target_event.event_id
        assert sample_reaction_event.target_event_type == sample_target_event.event_type
        assert sample_reaction_event.reaction_type == "agreement"
        assert sample_reaction_event.content == "Nods in agreement"
        
        # Check metadata
        assert sample_reaction_event.metadata["reactor_name"] == "Test reactor"
        assert sample_reaction_event.metadata["reactor_faction"] == "Test faction"
        assert sample_reaction_event.metadata["target_event_id"] == sample_target_event.event_id
        assert sample_reaction_event.metadata["target_event_type"] == "speech"
        assert sample_reaction_event.metadata["reaction_type"] == "agreement"
        assert sample_reaction_event.metadata["target_speaker"] == "Test speaker"
    
    def test_to_dict(self, sample_reaction_event, sample_reactor, sample_target_event):
        """Test the to_dict method."""
        event_dict = sample_reaction_event.to_dict()
        
        # Check base Event properties
        assert event_dict["event_type"] == "reaction"
        assert event_dict["source"] == "Test reactor"
        
        # Check ReactionEvent-specific properties
        assert event_dict["reactor"]["id"] == "reactor_id"
        assert event_dict["reactor"]["name"] == "Test reactor"
        assert event_dict["reactor"]["faction"] == "Test faction"
        assert event_dict["target_event_id"] == sample_target_event.event_id
        assert event_dict["target_event_type"] == "speech"
        assert event_dict["reaction_type"] == "agreement"
        assert event_dict["content"] == "Nods in agreement"
    
    def test_reaction_to_non_speech_event(self, sample_reactor):
        """Test creating a reaction to a non-speech event."""
        target_event = Event(event_type="test_event")
        
        reaction_event = ReactionEvent(
            reactor=sample_reactor,
            target_event=target_event,
            reaction_type="interest",
            content="Looks interested"
        )
        
        # Check target event information
        assert reaction_event.target_event_id == target_event.event_id
        assert reaction_event.target_event_type == "test_event"
        
        # Check metadata doesn't include target_speaker
        assert "target_speaker" not in reaction_event.metadata


class TestInterjectionEvent:
    """Test suite for the InterjectionEvent class."""
    
    @pytest.fixture
    def sample_interjector(self):
        """Create a sample interjector for testing."""
        return {
            "id": "interjector_id",
            "name": "Test interjector",
            "faction": "Test faction",
            "rank": 2
        }
    
    @pytest.fixture
    def sample_target_speaker(self):
        """Create a sample target speaker for testing."""
        return {
            "id": "speaker_id",
            "name": "Test speaker",
            "faction": "Test faction",
            "rank": 1
        }
    
    @pytest.fixture
    def sample_interjection_event(self, sample_interjector, sample_target_speaker):
        """Create a sample interjection event for testing."""
        return InterjectionEvent(
            interjector=sample_interjector,
            target_speaker=sample_target_speaker,
            interjection_type=InterjectionType.CHALLENGE,
            latin_content="Latin interjection content",
            english_content="English interjection content",
            target_speech_id="speech_id",
            causes_disruption=True
        )
    
    def test_initialization(self, sample_interjection_event, sample_interjector, sample_target_speaker):
        """Test initialization of an InterjectionEvent."""
        # Check base Event properties
        assert sample_interjection_event.event_type == "interjection"
        assert sample_interjection_event.source == sample_interjector
        
        # Check InterjectionEvent-specific properties
        assert sample_interjection_event.interjector == sample_interjector
        assert sample_interjection_event.target_speaker == sample_target_speaker
        assert sample_interjection_event.interjection_type == InterjectionType.CHALLENGE
        assert sample_interjection_event.latin_content == "Latin interjection content"
        assert sample_interjection_event.english_content == "English interjection content"
        assert sample_interjection_event.target_speech_id == "speech_id"
        assert sample_interjection_event.causes_disruption is True
        
        # Check priority calculation
        assert sample_interjection_event.priority == 2  # Based on interjector rank
        
        # Check metadata
        assert sample_interjection_event.metadata["interjector_name"] == "Test interjector"
        assert sample_interjection_event.metadata["interjector_faction"] == "Test faction"
        assert sample_interjection_event.metadata["target_speaker_name"] == "Test speaker"
        assert sample_interjection_event.metadata["interjection_type"] == "challenge"
        assert sample_interjection_event.metadata["causes_disruption"] is True
        assert sample_interjection_event.metadata["target_speech_id"] == "speech_id"
    
    def test_initialization_without_speech_id(self, sample_interjector, sample_target_speaker):
        """Test initialization without a target speech ID."""
        event = InterjectionEvent(
            interjector=sample_interjector,
            target_speaker=sample_target_speaker,
            interjection_type=InterjectionType.SUPPORT,
            latin_content="Latin interjection content",
            english_content="English interjection content"
        )
        
        # Check target_speech_id is None
        assert event.target_speech_id is None
        
        # Check metadata doesn't include target_speech_id
        assert "target_speech_id" not in event.metadata
    
    def test_procedural_interjection_priority(self, sample_interjector, sample_target_speaker):
        """Test that procedural interjections get higher priority."""
        event = InterjectionEvent(
            interjector=sample_interjector,
            target_speaker=sample_target_speaker,
            interjection_type=InterjectionType.PROCEDURAL,
            latin_content="Latin interjection content",
            english_content="English interjection content"
        )
        
        # Priority should be rank + 10 for procedural
        assert event.priority == 12  # 2 (rank) + 10
    
    def test_to_dict(self, sample_interjection_event, sample_interjector, sample_target_speaker):
        """Test the to_dict method."""
        event_dict = sample_interjection_event.to_dict()
        
        # Check base Event properties
        assert event_dict["event_type"] == "interjection"
        assert event_dict["source"] == "Test interjector"
        
        # Check InterjectionEvent-specific properties
        assert event_dict["interjector"]["id"] == "interjector_id"
        assert event_dict["interjector"]["name"] == "Test interjector"
        assert event_dict["interjector"]["faction"] == "Test faction"
        assert event_dict["target_speaker"]["id"] == "speaker_id"
        assert event_dict["target_speaker"]["name"] == "Test speaker"
        assert event_dict["target_speaker"]["faction"] == "Test faction"
        assert event_dict["interjection_type"] == "challenge"
        assert event_dict["latin_content"] == "Latin interjection content"
        assert event_dict["english_content"] == "English interjection content"
        assert event_dict["causes_disruption"] is True
        assert event_dict["target_speech_id"] == "speech_id"