"""
Tests for debate-specific event types.

These tests verify that all debate event classes properly initialize,
store data, and provide appropriate property accessors.
"""

import unittest
from datetime import datetime
import uuid

from src.roman_senate.core.events.base import BaseEvent, RomanEvent
from src.roman_senate.core.events.debate_events import (
    DebateStartedEvent,
    DebateEndedEvent,
    SpeechStartedEvent,
    SpeechEndedEvent,
    InterjectionEvent,
    VoteRequestedEvent,
    DebateTopicChangedEvent
)


class TestDebateEvents(unittest.TestCase):
    """Tests for all debate-related event classes."""
    
    def test_debate_started_event(self):
        """Test DebateStartedEvent initialization and properties."""
        topic = "Roman Infrastructure"
        initiator = "Marcus Agrippa"
        participants = ["Cicero", "Cato", "Caesar"]
        source = "test_source"
        
        event = DebateStartedEvent(
            topic=topic,
            initiator=initiator,
            participants=participants,
            source=source
        )
        
        # Check inheritance
        self.assertIsInstance(event, BaseEvent)
        self.assertIsInstance(event, RomanEvent)
        
        # Check event type
        self.assertEqual(event.event_type, "DEBATE_STARTED")
        
        # Check properties
        self.assertEqual(event.topic, topic)
        self.assertEqual(event.initiator, initiator)
        self.assertEqual(event.participants, participants)
        self.assertEqual(event.source, source)
        
        # Check data dictionary
        self.assertIn("topic", event.data)
        self.assertIn("initiator", event.data)
        self.assertIn("participants", event.data)
    
    def test_debate_ended_event(self):
        """Test DebateEndedEvent initialization and properties."""
        topic = "Roman Infrastructure"
        outcome = "Motion passed"
        duration_minutes = 120
        source = "test_source"
        
        event = DebateEndedEvent(
            topic=topic,
            outcome=outcome,
            duration_minutes=duration_minutes,
            source=source
        )
        
        # Check inheritance
        self.assertIsInstance(event, BaseEvent)
        self.assertIsInstance(event, RomanEvent)
        
        # Check event type
        self.assertEqual(event.event_type, "DEBATE_ENDED")
        
        # Check properties
        self.assertEqual(event.topic, topic)
        self.assertEqual(event.outcome, outcome)
        self.assertEqual(event.duration_minutes, duration_minutes)
        self.assertEqual(event.source, source)
        
        # Check data dictionary
        self.assertIn("topic", event.data)
        self.assertIn("outcome", event.data)
        self.assertIn("duration_minutes", event.data)
    
    def test_speech_started_event(self):
        """Test SpeechStartedEvent initialization and properties."""
        speaker = "Cicero"
        topic = "Against Catiline"
        position = "Opposition"
        source = "test_source"
        
        event = SpeechStartedEvent(
            speaker=speaker,
            topic=topic,
            position=position,
            source=source
        )
        
        # Check inheritance
        self.assertIsInstance(event, BaseEvent)
        self.assertIsInstance(event, RomanEvent)
        
        # Check event type
        self.assertEqual(event.event_type, "SPEECH_STARTED")
        
        # Check properties
        self.assertEqual(event.speaker, speaker)
        self.assertEqual(event.topic, topic)
        self.assertEqual(event.position, position)
        self.assertEqual(event.source, source)
        
        # Check data dictionary
        self.assertIn("speaker", event.data)
        self.assertIn("topic", event.data)
        self.assertIn("position", event.data)
    
    def test_speech_ended_event(self):
        """Test SpeechEndedEvent initialization and properties."""
        speaker = "Cicero"
        topic = "Against Catiline"
        duration_minutes = 45
        impact = 0.85
        source = "test_source"
        
        event = SpeechEndedEvent(
            speaker=speaker,
            topic=topic,
            duration_minutes=duration_minutes,
            impact=impact,
            source=source
        )
        
        # Check inheritance
        self.assertIsInstance(event, BaseEvent)
        self.assertIsInstance(event, RomanEvent)
        
        # Check event type
        self.assertEqual(event.event_type, "SPEECH_ENDED")
        
        # Check properties
        self.assertEqual(event.speaker, speaker)
        self.assertEqual(event.topic, topic)
        self.assertEqual(event.duration_minutes, duration_minutes)
        self.assertEqual(event.impact, impact)
        self.assertEqual(event.source, source)
        
        # Check data dictionary
        self.assertIn("speaker", event.data)
        self.assertIn("topic", event.data)
        self.assertIn("duration_minutes", event.data)
        self.assertIn("impact", event.data)
    
    def test_interjection_event(self):
        """Test InterjectionEvent initialization and properties."""
        speaker = "Brutus"
        target_speaker = "Caesar"
        content_type = "objection"
        source = "test_source"
        
        event = InterjectionEvent(
            speaker=speaker,
            target_speaker=target_speaker,
            content_type=content_type,
            source=source
        )
        
        # Check inheritance
        self.assertIsInstance(event, BaseEvent)
        self.assertIsInstance(event, RomanEvent)
        
        # Check event type
        self.assertEqual(event.event_type, "INTERJECTION")
        
        # Check properties
        self.assertEqual(event.speaker, speaker)
        self.assertEqual(event.target_speaker, target_speaker)
        self.assertEqual(event.content_type, content_type)
        self.assertEqual(event.source, source)
        
        # Check data dictionary
        self.assertIn("speaker", event.data)
        self.assertIn("target_speaker", event.data)
        self.assertIn("content_type", event.data)
    
    def test_vote_requested_event(self):
        """Test VoteRequestedEvent initialization and properties."""
        topic = "Military Funding"
        requester = "Cato"
        vote_type = "division"
        source = "test_source"
        
        event = VoteRequestedEvent(
            topic=topic,
            requester=requester,
            vote_type=vote_type,
            source=source
        )
        
        # Check inheritance
        self.assertIsInstance(event, BaseEvent)
        self.assertIsInstance(event, RomanEvent)
        
        # Check event type
        self.assertEqual(event.event_type, "VOTE_REQUESTED")
        
        # Check properties
        self.assertEqual(event.topic, topic)
        self.assertEqual(event.requester, requester)
        self.assertEqual(event.vote_type, vote_type)
        self.assertEqual(event.source, source)
        
        # Check data dictionary
        self.assertIn("topic", event.data)
        self.assertIn("requester", event.data)
        self.assertIn("vote_type", event.data)
    
    def test_debate_topic_changed_event(self):
        """Test DebateTopicChangedEvent initialization and properties."""
        old_topic = "Military Funding"
        new_topic = "Foreign Policy"
        initiator = "Caesar"
        source = "test_source"
        
        event = DebateTopicChangedEvent(
            old_topic=old_topic,
            new_topic=new_topic,
            initiator=initiator,
            source=source
        )
        
        # Check inheritance
        self.assertIsInstance(event, BaseEvent)
        self.assertIsInstance(event, RomanEvent)
        
        # Check event type
        self.assertEqual(event.event_type, "TOPIC_CHANGED")
        
        # Check properties
        self.assertEqual(event.old_topic, old_topic)
        self.assertEqual(event.new_topic, new_topic)
        self.assertEqual(event.initiator, initiator)
        self.assertEqual(event.source, source)
        
        # Check data dictionary
        self.assertIn("old_topic", event.data)
        self.assertIn("new_topic", event.data)
        self.assertIn("initiator", event.data)


if __name__ == "__main__":
    unittest.main()