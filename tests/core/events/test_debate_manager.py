"""
Tests for the debate manager.

These tests verify that the DebateManager correctly orchestrates 
debate events and maintains debate state.
"""

import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch

from src.roman_senate.core.events.base import BaseEvent
from src.roman_senate.core.events.debate_events import (
    DebateStartedEvent,
    DebateEndedEvent,
    SpeechStartedEvent,
    SpeechEndedEvent,
    InterjectionEvent,
    VoteRequestedEvent,
    DebateTopicChangedEvent
)
from src.roman_senate.core.events.debate_manager import DebateManager, DebateSession


class TestDebateSession(unittest.TestCase):
    """Tests for the DebateSession class."""
    
    def test_debate_session_initialization(self):
        """Test DebateSession initializes with correct attributes."""
        topic = "Roman Infrastructure"
        initiator = "Marcus Agrippa"
        participants = ["Cicero", "Cato", "Caesar"]
        
        session = DebateSession(topic, initiator, participants)
        
        self.assertEqual(session.topic, topic)
        self.assertEqual(session.initiator, initiator)
        # Initiator should always be included in participants
        self.assertEqual(session.participants, set(participants) | {initiator})
        self.assertIsNotNone(session.start_time)
        self.assertIsNone(session.current_speaker)
        self.assertIsNone(session.speech_start_time)
        self.assertEqual(session.speeches_delivered, {})
        self.assertEqual(session.interjections, [])
        self.assertTrue(session.is_active)
    
    def test_add_participant(self):
        """Test adding a participant to the debate."""
        session = DebateSession("Test Topic", "Initiator")
        
        session.add_participant("New Senator")
        
        self.assertIn("New Senator", session.participants)
    
    def test_remove_participant(self):
        """Test removing a participant from the debate."""
        session = DebateSession("Test Topic", "Initiator", ["Senator1", "Senator2"])
        
        session.remove_participant("Senator1")
        
        self.assertNotIn("Senator1", session.participants)
        self.assertIn("Senator2", session.participants)
    
    def test_start_speech(self):
        """Test recording a senator starting to speak."""
        session = DebateSession("Test Topic", "Initiator")
        
        session.start_speech("Orator")
        
        self.assertEqual(session.current_speaker, "Orator")
        self.assertIsNotNone(session.speech_start_time)
        self.assertIn("Orator", session.participants)
    
    def test_end_speech(self):
        """Test recording a senator finishing speaking."""
        session = DebateSession("Test Topic", "Initiator")
        
        # Start a speech
        session.start_speech("Orator")
        
        # End the speech
        duration = session.end_speech("Orator")
        
        self.assertIsNone(session.current_speaker)
        self.assertIsNone(session.speech_start_time)
        self.assertEqual(session.speeches_delivered["Orator"], 1)
        self.assertIsNotNone(duration)  # Should return some duration
    
    def test_record_interjection(self):
        """Test recording an interjection during a speech."""
        session = DebateSession("Test Topic", "Initiator")
        
        # Start a speech
        session.start_speech("MainSpeaker")
        
        # Record an interjection
        session.record_interjection("Interrupter", "MainSpeaker", "question")
        
        self.assertEqual(len(session.interjections), 1)
        self.assertEqual(session.interjections[0], ("Interrupter", "MainSpeaker", "question"))
        self.assertIn("Interrupter", session.participants)
    
    def test_change_topic(self):
        """Test changing the debate topic."""
        session = DebateSession("Old Topic", "Initiator")
        
        session.change_topic("New Topic")
        
        self.assertEqual(session.topic, "New Topic")
    
    def test_end_debate(self):
        """Test ending the debate and getting statistics."""
        session = DebateSession("Test Topic", "Initiator", ["Senator1", "Senator2"])
        
        # Add some activity
        session.start_speech("Senator1")
        session.end_speech("Senator1")
        session.start_speech("Senator2")
        session.end_speech("Senator2")
        session.start_speech("Senator1")
        session.end_speech("Senator1")
        
        stats = session.end_debate()
        
        self.assertFalse(session.is_active)
        self.assertEqual(stats["topic"], "Test Topic")
        self.assertEqual(stats["initiator"], "Initiator")
        self.assertEqual(set(stats["participants"]), {"Initiator", "Senator1", "Senator2"})
        self.assertEqual(stats["speech_count"], 3)
        self.assertEqual(stats["most_active_speaker"], "Senator1")


class TestDebateManager(unittest.TestCase):
    """Tests for the DebateManager class."""
    
    def setUp(self):
        """Set up test environment before each test."""
        self.event_bus = MagicMock()
        self.manager = DebateManager(self.event_bus)
    
    def test_initialization(self):
        """Test DebateManager initializes correctly."""
        self.assertEqual(self.manager.active_debates, {})
        self.assertEqual(self.manager.event_bus, self.event_bus)
        
        # Verify subscriptions
        expected_subscriptions = [
            "DEBATE_STARTED", "DEBATE_ENDED", "SPEECH_STARTED", 
            "SPEECH_ENDED", "INTERJECTION", "VOTE_REQUESTED", "TOPIC_CHANGED"
        ]
        
        # Check that each expected subscription was made
        for event_type in expected_subscriptions:
            self.event_bus.subscribe.assert_any_call(event_type, self.manager)
    
    def test_handle_debate_started(self):
        """Test handling a debate started event."""
        event = DebateStartedEvent(
            topic="Test Topic",
            initiator="Initiator",
            participants=["Senator1", "Senator2"]
        )
        
        self.manager.handle_event(event)
        
        self.assertIn("Test Topic", self.manager.active_debates)
        debate = self.manager.active_debates["Test Topic"]
        self.assertEqual(debate.topic, "Test Topic")
        self.assertEqual(debate.initiator, "Initiator")
        self.assertEqual(debate.participants, {"Initiator", "Senator1", "Senator2"})
    
    def test_handle_debate_ended(self):
        """Test handling a debate ended event."""
        # First start a debate
        start_event = DebateStartedEvent(
            topic="Test Topic",
            initiator="Initiator"
        )
        self.manager.handle_event(start_event)
        
        # Then end it
        end_event = DebateEndedEvent(
            topic="Test Topic",
            outcome="Consensus reached"
        )
        self.manager.handle_event(end_event)
        
        # The debate should be removed from active debates
        self.assertNotIn("Test Topic", self.manager.active_debates)
    
    def test_handle_speech_started(self):
        """Test handling a speech started event."""
        # Start a debate
        start_event = DebateStartedEvent(
            topic="Test Topic",
            initiator="Initiator"
        )
        self.manager.handle_event(start_event)
        
        # Start a speech
        speech_event = SpeechStartedEvent(
            speaker="Orator",
            topic="Test Topic"
        )
        self.manager.handle_event(speech_event)
        
        # Check that the speech was recorded
        debate = self.manager.active_debates["Test Topic"]
        self.assertEqual(debate.current_speaker, "Orator")
        self.assertIsNotNone(debate.speech_start_time)
    
    def test_handle_speech_ended(self):
        """Test handling a speech ended event."""
        # Set up a debate with an active speech
        start_event = DebateStartedEvent(
            topic="Test Topic",
            initiator="Initiator"
        )
        self.manager.handle_event(start_event)
        
        speech_start_event = SpeechStartedEvent(
            speaker="Orator",
            topic="Test Topic"
        )
        self.manager.handle_event(speech_start_event)
        
        # End the speech
        speech_end_event = SpeechEndedEvent(
            speaker="Orator",
            topic="Test Topic"
        )
        self.manager.handle_event(speech_end_event)
        
        # Check that the speech was ended
        debate = self.manager.active_debates["Test Topic"]
        self.assertIsNone(debate.current_speaker)
        self.assertIsNone(debate.speech_start_time)
        self.assertEqual(debate.speeches_delivered["Orator"], 1)
    
    def test_handle_interjection(self):
        """Test handling an interjection event."""
        # Set up a debate with an active speech
        start_event = DebateStartedEvent(
            topic="Test Topic",
            initiator="Initiator"
        )
        self.manager.handle_event(start_event)
        
        speech_start_event = SpeechStartedEvent(
            speaker="MainSpeaker",
            topic="Test Topic"
        )
        self.manager.handle_event(speech_start_event)
        
        # Record an interjection
        interjection_event = InterjectionEvent(
            speaker="Interrupter",
            target_speaker="MainSpeaker",
            content_type="question"
        )
        self.manager.handle_event(interjection_event)
        
        # Check that the interjection was recorded
        debate = self.manager.active_debates["Test Topic"]
        self.assertEqual(len(debate.interjections), 1)
        self.assertEqual(debate.interjections[0], ("Interrupter", "MainSpeaker", "question"))
    
    def test_handle_topic_changed(self):
        """Test handling a topic changed event."""
        # Start a debate
        start_event = DebateStartedEvent(
            topic="Old Topic",
            initiator="Initiator"
        )
        self.manager.handle_event(start_event)
        
        # Change the topic
        change_event = DebateTopicChangedEvent(
            old_topic="Old Topic",
            new_topic="New Topic",
            initiator="Changer"
        )
        self.manager.handle_event(change_event)
        
        # Check that the topic was changed and debate moved
        self.assertNotIn("Old Topic", self.manager.active_debates)
        self.assertIn("New Topic", self.manager.active_debates)
        self.assertEqual(self.manager.active_debates["New Topic"].topic, "New Topic")
    
    def test_start_debate(self):
        """Test starting a new debate through the manager."""
        self.manager.start_debate(
            topic="Test Topic",
            initiator="Initiator",
            participants=["Senator1", "Senator2"]
        )
        
        # Check that the event was published
        self.event_bus.publish.assert_called_once()
        published_event = self.event_bus.publish.call_args[0][0]
        self.assertIsInstance(published_event, DebateStartedEvent)
        self.assertEqual(published_event.topic, "Test Topic")
        self.assertEqual(published_event.initiator, "Initiator")
        self.assertEqual(published_event.participants, ["Senator1", "Senator2"])
    
    def test_end_debate(self):
        """Test ending a debate through the manager."""
        # First start a debate
        start_event = DebateStartedEvent(
            topic="Test Topic",
            initiator="Initiator"
        )
        self.manager.handle_event(start_event)
        
        # End the debate
        self.manager.end_debate(
            topic="Test Topic",
            outcome="Motion passed"
        )
        
        # Check that the event was published
        self.event_bus.publish.assert_called_once()
        published_event = self.event_bus.publish.call_args[0][0]
        self.assertIsInstance(published_event, DebateEndedEvent)
        self.assertEqual(published_event.topic, "Test Topic")
        self.assertEqual(published_event.outcome, "Motion passed")
    
    def test_get_active_debates(self):
        """Test retrieving list of active debates."""
        # Start two debates
        start_event1 = DebateStartedEvent(
            topic="Topic 1",
            initiator="Initiator 1"
        )
        start_event2 = DebateStartedEvent(
            topic="Topic 2",
            initiator="Initiator 2"
        )
        self.manager.handle_event(start_event1)
        self.manager.handle_event(start_event2)
        
        # Get active debates
        active_debates = self.manager.get_active_debates()
        
        # Check result
        self.assertEqual(set(active_debates), {"Topic 1", "Topic 2"})
    
    def test_is_debate_active(self):
        """Test checking if a debate is active."""
        # Start a debate
        start_event = DebateStartedEvent(
            topic="Test Topic",
            initiator="Initiator"
        )
        self.manager.handle_event(start_event)
        
        # Check active state
        self.assertTrue(self.manager.is_debate_active("Test Topic"))
        self.assertFalse(self.manager.is_debate_active("Nonexistent Topic"))
    
    def test_get_debate_participants(self):
        """Test retrieving debate participants."""
        # Start a debate
        start_event = DebateStartedEvent(
            topic="Test Topic",
            initiator="Initiator",
            participants=["Senator1", "Senator2"]
        )
        self.manager.handle_event(start_event)
        
        # Get participants
        participants = self.manager.get_debate_participants("Test Topic")
        
        # Check result
        self.assertEqual(set(participants), {"Initiator", "Senator1", "Senator2"})
        self.assertIsNone(self.manager.get_debate_participants("Nonexistent Topic"))
    
    def test_get_current_speaker(self):
        """Test retrieving the current speaker for a debate."""
        # Start a debate
        start_event = DebateStartedEvent(
            topic="Test Topic",
            initiator="Initiator"
        )
        self.manager.handle_event(start_event)
        
        # Start a speech
        speech_event = SpeechStartedEvent(
            speaker="Orator",
            topic="Test Topic"
        )
        self.manager.handle_event(speech_event)
        
        # Get current speaker
        speaker = self.manager.get_current_speaker("Test Topic")
        
        # Check result
        self.assertEqual(speaker, "Orator")
        self.assertIsNone(self.manager.get_current_speaker("Nonexistent Topic"))


if __name__ == "__main__":
    unittest.main()