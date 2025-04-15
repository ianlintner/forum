#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Roman Senate AI Game - Senate Session Tests
Tests for the Senate session core functionality using Latin function names.
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from roman_senate.core.game_state import game_state
import asyncio

from roman_senate.core.senate_session import SenateSession
from roman_senate.core.topic_generator import flatten_topics_by_category


# --- Senate Session Tests ---

def test_creatio_senatus():
    """
    Test creating a Senate session with the proper parameters.
    (Test Senate creation)
    """
    # Create a Senate session
    with patch('roman_senate.core.senators.initialize_senate') as mock_gen_senators:
        # Mock senator generation
        mock_gen_senators.return_value = [
            {"id": 1, "name": "Cicero", "faction": "Optimates"},
            {"id": 2, "name": "Caesar", "faction": "Populares"},
            {"id": 3, "name": "Cato", "faction": "Optimates"},
        ]
        
        # Create session
        mock_game_state = MagicMock()  # Create a mock game_state object
        session = SenateSession(
            senators_list=mock_gen_senators.return_value,
            year=-50,
            game_state=mock_game_state
        )
        
        # Verify
        assert session.year == -50
        assert session.player_name == "Marcus"
        assert session.player_faction == "Optimates"
        assert len(session.senators) == 3
        assert session.current_debate_round == 0
        assert session.current_topic_index == 0


@pytest.mark.asyncio
async def test_preparatio_sessionis():
    """
    Test preparing a Senate session by loading topics.
    (Test session preparation)
    """
    # Create a Senate session
    with patch('roman_senate.core.senators.initialize_senate') as mock_gen_senators, \
         patch('roman_senate.core.topic_generator.get_topics_for_year') as mock_get_topics:
        
        # Mock senator generation
        mock_gen_senators.return_value = [
            {"id": 1, "name": "Cicero", "faction": "Optimates"},
            {"id": 2, "name": "Caesar", "faction": "Populares"},
        ]
        
        # Mock topic generation
        topics_by_category = {
            "Military funding": ["Fund the legion"],
            "Public projects": ["Build an aqueduct"]
        }
        mock_get_topics.return_value = topics_by_category
        
        # Create session
        mock_game_state = MagicMock()
        session = SenateSession(
            senators_list=mock_gen_senators.return_value,
            year=-50,
            game_state=mock_game_state
        )
        
        # Prepare the session
        await session.prepare_session(topic_count=2)
        
        # Verify
        assert mock_get_topics.called
        assert len(session.topics) == 2
        assert session.is_prepared == True


def test_selectio_oratoris():
    """
    Test selecting the next orator for a debate.
    (Test orator selection)
    """
    # Create a Senate session with mocked senators
    with patch('roman_senate.core.senators.initialize_senate') as mock_gen_senators:
        # Mock senator generation
        senators = [
            {"id": 1, "name": "Cicero", "faction": "Optimates"},
            {"id": 2, "name": "Caesar", "faction": "Populares"},
            {"id": 3, "name": "Cato", "faction": "Optimates"},
        ]
        mock_gen_senators.return_value = senators
        
        # Create session
        mock_game_state = MagicMock()
        session = SenateSession(
            senators_list=mock_gen_senators.return_value,
            year=-50,
            game_state=mock_game_state
        )
        
        # Mock the debate state
        session.topics = [{"text": "Topic 1"}, {"text": "Topic 2"}]
        session.current_debate = {
            "topic": "Topic 1",
            "speeches": [],
            "speaking_order": [1, 2, 3],  # IDs of senators
            "current_speaker_index": 0,
            "votes": {"support": 0, "oppose": 0, "abstain": 0},
            "result": None
        }
        
        # Test getting next orator
        next_senator = session.get_next_orator()
        assert next_senator["id"] == 1  # First in speaking order
        assert session.current_debate["current_speaker_index"] == 1  # Incremented
        
        # Next orator
        next_senator = session.get_next_orator()
        assert next_senator["id"] == 2  # Second in speaking order
        assert session.current_debate["current_speaker_index"] == 2
        
        # Test completion of speaking order
        next_senator = session.get_next_orator()
        assert next_senator["id"] == 3  # Last in speaking order
        assert session.current_debate["current_speaker_index"] == 3
        
        # Should return None when all senators have spoken
        next_senator = session.get_next_orator()
        assert next_senator is None


def test_initium_controversiae():
    """
    Test initializing a debate round.
    (Test debate initialization)
    """
    # Create a Senate session with mocked senators
    with patch('roman_senate.core.senators.initialize_senate') as mock_gen_senators, \
         patch('random.shuffle') as mock_shuffle:
        
        # Mock senator generation
        senators = [
            {"id": 1, "name": "Cicero", "faction": "Optimates"},
            {"id": 2, "name": "Caesar", "faction": "Populares"},
            {"id": 3, "name": "Cato", "faction": "Optimates"},
        ]
        mock_gen_senators.return_value = senators
        
        # Make random.shuffle do nothing (predictable for testing)
        mock_shuffle.side_effect = lambda x: x
        
        # Create session
        mock_game_state = MagicMock()
        session = SenateSession(
            senators_list=mock_gen_senators.return_value,
            year=-50,
            game_state=mock_game_state
        )
        
        # Setup topics
        session.topics = [{"text": "Topic 1", "category": "Military"}, 
                          {"text": "Topic 2", "category": "Public"}]
        session.current_topic_index = 0
        
        # Initialize debate
        session.initialize_debate_round()
        
        # Verify
        assert session.current_debate_round == 1
        assert "topic" in session.current_debate
        assert session.current_debate["topic"] == "Topic 1"
        assert "speeches" in session.current_debate
        assert len(session.current_debate["speeches"]) == 0
        assert "speaking_order" in session.current_debate
        assert len(session.current_debate["speaking_order"]) == 3
        assert "current_speaker_index" in session.current_debate
        assert session.current_debate["current_speaker_index"] == 0
        assert "votes" in session.current_debate
        assert all(vote_type in session.current_debate["votes"] for vote_type in ["support", "oppose", "abstain"])


@pytest.mark.asyncio
async def test_generatio_orationis_senatoris():
    """
    Test generating a speech for a senator.
    (Test senator speech generation)
    """
    # Create a Senate session with mocked senators
    with patch('roman_senate.core.senators.initialize_senate') as mock_gen_senators, \
         patch('roman_senate.speech.speech_generator.generate_speech') as mock_generate_speech:
        
        # Mock senator generation
        senators = [
            {"id": 1, "name": "Cicero", "faction": "Optimates"},
            {"id": 2, "name": "Caesar", "faction": "Populares"},
        ]
        mock_gen_senators.return_value = senators
        
        # Mock speech generation
        mock_speech = {
            "text": "Mocked speech content",
            "senator_name": "Cicero",
            "senator_id": 1,
            "faction": "Optimates",
            "stance": "support",
            "points": ["Point 1", "Point 2"]
        }
        mock_generate_speech.return_value = mock_speech
        
        # Create session
        mock_game_state = MagicMock()
        session = SenateSession(
            senators_list=mock_gen_senators.return_value,
            year=-50,
            game_state=mock_game_state
        )
        
        # Setup debate state
        session.topics = [{"text": "Topic 1", "category": "Military"}]
        session.current_debate = {
            "topic": "Topic 1",
            "speeches": [],
            "speaking_order": [1, 2],
            "current_speaker_index": 0,
            "votes": {"support": 0, "oppose": 0, "abstain": 0},
            "result": None
        }
        
        # Generate speech
        senator = session.senators[0]  # Cicero
        speech = await session.generate_speech_for_senator(senator)
        
        # Verify
        assert speech == mock_speech
        assert mock_generate_speech.called
        mock_generate_speech.assert_called_with(
            senator=senator,
            topic="Topic 1",
            faction_stance=None,
            year=-50,
            responding_to=None,
            previous_speeches=[],
            use_llm=True
        )


def test_processum_votorum():
    """
    Test processing votes for a debate topic.
    (Test vote processing)
    """
    # Create a Senate session with mocked senators
    with patch('roman_senate.core.senators.initialize_senate') as mock_gen_senators, \
         patch('random.random') as mock_random:
        
        # Mock senator generation
        senators = [
            {"id": 1, "name": "Cicero", "faction": "Optimates"},
            {"id": 2, "name": "Caesar", "faction": "Populares"},
            {"id": 3, "name": "Cato", "faction": "Optimates"},
            {"id": 4, "name": "Brutus", "faction": "Optimates"},
            {"id": 5, "name": "Antonius", "faction": "Populares"},
        ]
        mock_gen_senators.return_value = senators
        
        # Configure random to give predictable voting pattern
        mock_random.side_effect = [0.1, 0.6, 0.9, 0.3, 0.7]  # First 3 return values < 0.5 (support), next 2 > 0.5 (oppose)
        
        # Create session
        mock_game_state = MagicMock()
        session = SenateSession(
            senators_list=mock_gen_senators.return_value,
            year=-50,
            game_state=mock_game_state
        )
        
        # Setup debate state with speeches
        session.current_debate = {
            "topic": "Topic 1",
            "speeches": [
                {"senator_id": 1, "stance": "support", "text": "Speech 1"},
                {"senator_id": 2, "stance": "oppose", "text": "Speech 2"},
                {"senator_id": 3, "stance": "support", "text": "Speech 3"},
            ],
            "votes": {"support": 0, "oppose": 0, "abstain": 0},
            "result": None
        }
        
        # Process votes
        session.process_votes()
        
        # Verify votes
        votes = session.current_debate["votes"]
        assert votes["support"] == 3  # 3 senators voted support
        assert votes["oppose"] == 2   # 2 senators voted oppose
        assert votes["abstain"] == 0  # 0 senators abstained
        assert session.current_debate["result"] == "passed"  # More support than oppose


def test_completio_sessionis():
    """
    Test completing a Senate session.
    (Test session completion)
    """
    # Create a Senate session with mocked senators
    with patch('roman_senate.core.senators.initialize_senate') as mock_gen_senators:
        # Mock senator generation
        senators = [
            {"id": 1, "name": "Cicero", "faction": "Optimates"},
            {"id": 2, "name": "Caesar", "faction": "Populares"},
        ]
        mock_gen_senators.return_value = senators
        
        # Create session
        mock_game_state = MagicMock()
        session = SenateSession(
            senators_list=mock_gen_senators.return_value,
            year=-50,
            game_state=mock_game_state
        )
        
        # Setup completed debates
        session.debates = [
            {
                "topic": "Topic 1",
                "speeches": [{"senator_id": 1, "stance": "support"}],
                "votes": {"support": 2, "oppose": 0, "abstain": 0},
                "result": "passed"
            },
            {
                "topic": "Topic 2",
                "speeches": [{"senator_id": 2, "stance": "oppose"}],
                "votes": {"support": 0, "oppose": 2, "abstain": 0},
                "result": "rejected"
            }
        ]
        
        # Complete session
        session_summary = session.get_session_summary()
        
        # Verify summary
        assert len(session_summary["debates"]) == 2
        assert session_summary["debates"][0]["result"] == "passed"
        assert session_summary["debates"][1]["result"] == "rejected"
        assert "passed_count" in session_summary
        assert "rejected_count" in session_summary
        assert session_summary["passed_count"] == 1
        assert session_summary["rejected_count"] == 1


def test_transitio_ad_topicum_novum():
    """
    Test transitioning to a new topic.
    (Test transition to new topic)
    """
    # Create a Senate session with mocked senators
    with patch('roman_senate.core.senators.initialize_senate') as mock_gen_senators:
        # Mock senator generation
        senators = [
            {"id": 1, "name": "Cicero", "faction": "Optimates"},
            {"id": 2, "name": "Caesar", "faction": "Populares"},
        ]
        mock_gen_senators.return_value = senators
        
        # Create session
        mock_game_state = MagicMock()
        session = SenateSession(
            senators_list=mock_gen_senators.return_value,
            year=-50,
            game_state=mock_game_state
        )
        
        # Setup topics and current debate
        session.topics = [
            {"text": "Topic 1", "category": "Military"},
            {"text": "Topic 2", "category": "Public"}
        ]
        session.current_topic_index = 0
        session.current_debate = {
            "topic": "Topic 1",
            "speeches": [{"senator_id": 1, "stance": "support"}],
            "votes": {"support": 2, "oppose": 0, "abstain": 0},
            "result": "passed"
        }
        
        # Save current debate to debates list
        session.debates.append(session.current_debate)
        
        # Transition to next topic
        has_next = session.advance_to_next_topic()
        
        # Verify
        assert has_next == True
        assert session.current_topic_index == 1
        assert session.current_debate is None
        
        # Initialize new debate
        session.initialize_debate_round()
        assert session.current_debate["topic"] == "Topic 2"
        
        # Test advancing past the last topic
        session.current_topic_index = 1
        has_next = session.advance_to_next_topic()
        assert has_next == False