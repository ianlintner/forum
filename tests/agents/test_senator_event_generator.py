#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test module for the SenatorEventGenerator.
This module tests the functionality of the SenatorEventGenerator class.
"""

import pytest
import uuid
import random
from unittest.mock import MagicMock, patch, AsyncMock
from typing import Dict, List, Any

from roman_senate.agents.event_generators.senator_event_generator import SenatorEventGenerator
from roman_senate.core.narrative_context import NarrativeContext, NarrativeEvent
from roman_senate.core.game_state import GameState
from roman_senate.core.roman_calendar import RomanCalendar
from roman_senate.utils.llm.base import LLMProvider


class TestSenatorEventGenerator:
    """Test suite for the SenatorEventGenerator class."""

    @pytest.fixture
    def llm_provider(self):
        """Create a mock LLM provider."""
        mock_provider = MagicMock(spec=LLMProvider)
        mock_provider.generate_text = AsyncMock(return_value="Cicero's New Villa\nMarcus Tullius Cicero has completed construction on his new countryside villa near Tusculum, showcasing his growing wealth and status. Several prominent senators attended the housewarming celebration.")
        return mock_provider

    @pytest.fixture
    def game_state(self):
        """Create a mock GameState for testing."""
        mock_state = MagicMock(spec=GameState)
        mock_calendar = MagicMock(spec=RomanCalendar)
        mock_calendar.year = -50
        mock_calendar.current_month_idx = 4  # May (0-indexed)
        mock_calendar.current_day = 10
        mock_state.calendar = mock_calendar
        mock_state.get_formatted_date = MagicMock(return_value="10th day of May, 704 AUC")
        
        # Add some mock senators with proper name properties
        cicero_mock = MagicMock()
        cicero_mock.name = "Cicero"  # Set as property, not mock name
        
        cato_mock = MagicMock()
        cato_mock.name = "Cato"
        
        atticus_mock = MagicMock()
        atticus_mock.name = "Atticus"
        
        caesar_mock = MagicMock()
        caesar_mock.name = "Caesar"
        
        mock_state.senators = [cicero_mock, cato_mock, atticus_mock, caesar_mock]
        
        return mock_state

    @pytest.fixture
    def narrative_context(self):
        """Create a mock NarrativeContext for testing."""
        mock_context = MagicMock(spec=NarrativeContext)
        mock_context.get_recent_events = MagicMock(return_value=[
            NarrativeEvent(
                id=str(uuid.uuid4()),
                event_type="daily_event",
                description="The Senate debated a new land reform bill.",
                date={"year": -50, "month": 5, "day": 9},
                significance=2,
                tags=["politics", "daily"],
                entities=["Senate", "Cicero"],
                metadata={"title": "Land Reform Debate"}
            )
        ])
        mock_context.recurring_entities = {"Cicero": 5, "Cato": 3, "Caesar": 4, "Senate": 6}
        return mock_context

    @pytest.fixture
    def senator_generator(self, llm_provider):
        """Create a SenatorEventGenerator instance for testing."""
        return SenatorEventGenerator(llm_provider)

    def test_initialization(self, llm_provider):
        """Test SenatorEventGenerator initialization."""
        generator = SenatorEventGenerator(llm_provider)
        assert generator.llm_provider == llm_provider
        assert hasattr(generator, 'senator_event_categories')
        assert isinstance(generator.senator_event_categories, list)
        assert len(generator.senator_event_categories) > 0
        assert "personal" in generator.senator_event_categories
        assert "political" in generator.senator_event_categories

    @pytest.mark.asyncio
    async def test_generate_events(self, senator_generator, game_state, narrative_context):
        """Test generating senator events."""
        events = await senator_generator.generate_events(game_state, narrative_context)
        
        # Verify events were generated
        assert len(events) > 0
        
        # Check event properties
        for event in events:
            assert event.event_type == "senator_event"
            assert event.id is not None
            assert isinstance(event.description, str) and len(event.description) > 0
            assert event.date == {
                "year": game_state.calendar.year,
                "month": game_state.calendar.current_month_idx + 1,  # Convert to 1-based
                "day": game_state.calendar.current_day
            }
            assert event.significance >= 1  # Senator events can vary in significance
            assert len(event.tags) > 0  # Should have at least one tag
            assert event.metadata.get("title") is not None
            assert event.metadata.get("category") in senator_generator.senator_event_categories
            assert len(event.entities) > 0  # Should involve at least one entity

    @pytest.mark.asyncio
    async def test_generate_senator_event(self, senator_generator, game_state, narrative_context):
        """Test generating a specific senator event."""
        # Create test data
        category = "personal"
        focus_senator = "Cicero"  # Added focus_senator parameter
        current_date = {
            "year": game_state.calendar.year,
            "month": game_state.calendar.current_month_idx + 1,
            "day": game_state.calendar.current_day,
            "formatted": game_state.get_formatted_date()
        }
        recent_events = ["daily_event: The Senate debated a new land reform bill."]
        entities = ["Cicero", "Cato", "Caesar", "Senate"]
        
        # Generate a senator event
        event = await senator_generator._generate_senator_event(
            category, focus_senator, current_date, game_state, recent_events, entities
        )
        
        # Verify the event
        assert event is not None
        assert event.event_type == "senator_event"
        assert "personal" in event.tags
        assert "Cicero" in event.description
        assert "Cicero" in event.metadata["title"]

    @pytest.mark.asyncio
    async def test_error_handling(self, senator_generator, game_state, narrative_context):
        """Test error handling during event generation."""
        # Make the LLM provider raise an exception
        senator_generator.llm_provider.generate_text.side_effect = Exception("Test error")
        
        # The generator should handle the error and return an empty list
        events = await senator_generator.generate_events(game_state, narrative_context)
        assert events == []
        
        # Test error handling in _generate_senator_event
        category = "personal"
        focus_senator = "Cicero"  # Added focus_senator parameter
        current_date = {
            "year": game_state.calendar.year,
            "month": game_state.calendar.current_month_idx + 1,
            "day": game_state.calendar.current_day,
            "formatted": game_state.get_formatted_date()
        }
        recent_events = ["daily_event: The Senate debated a new land reform bill."]
        entities = ["Cicero", "Cato", "Caesar", "Senate"]
        
        event = await senator_generator._generate_senator_event(
            category, focus_senator, current_date, game_state, recent_events, entities
        )
        assert event is None

    def test_extract_entities(self, senator_generator):
        """Test entity extraction from text."""
        text = "Cicero spoke in the Senate, with Caesar and Cato in attendance."
        known_entities = ["Cicero", "Caesar", "Cato", "Senate", "Atticus"]
        
        entities = senator_generator._extract_entities(text, known_entities)
        
        assert "Cicero" in entities
        assert "Caesar" in entities
        assert "Cato" in entities
        assert "Senate" in entities
        assert "Atticus" not in entities

    def test_random_senator_selection(self, senator_generator, game_state):
        """Test random senator selection for events."""
        # Get senator names from game_state
        senator_names = [senator.name for senator in game_state.senators]
        
        # Mock the random.choice function
        with patch('random.choice') as mock_choice:
            mock_choice.return_value = "Cicero"
            
            # Call the mocked function
            selected = mock_choice(senator_names)
            
            # Verify the selection
            assert selected == "Cicero"
            mock_choice.assert_called_with(senator_names)