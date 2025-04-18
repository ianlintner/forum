#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test module for the ReligiousEventGenerator.
This module tests the functionality of the ReligiousEventGenerator class.
"""

import pytest
import uuid
from unittest.mock import MagicMock, patch, AsyncMock
from typing import Dict, List, Any

from roman_senate.agents.event_generators.religious_event_generator import ReligiousEventGenerator
from roman_senate.core.narrative_context import NarrativeContext, NarrativeEvent
from roman_senate.core.game_state import GameState
from roman_senate.core.roman_calendar import RomanCalendar
from roman_senate.utils.llm.base import LLMProvider


class TestReligiousEventGenerator:
    """Test suite for the ReligiousEventGenerator class."""

    @pytest.fixture
    def llm_provider(self):
        """Create a mock LLM provider."""
        mock_provider = MagicMock(spec=LLMProvider)
        mock_provider.generate_text = AsyncMock(return_value="Omen at the Temple of Jupiter\nThe priests at the Temple of Jupiter observed unusual lightning strikes during the night, which they have interpreted as a warning from the gods. The Senate has been advised to postpone any major decisions until proper sacrifices are made.")
        return mock_provider

    @pytest.fixture
    def game_state(self):
        """Create a mock GameState for testing."""
        mock_state = MagicMock(spec=GameState)
        mock_calendar = MagicMock(spec=RomanCalendar)
        mock_calendar.year = -46
        mock_calendar.current_month_idx = 5  # June (0-indexed)
        mock_calendar.current_day = 15
        mock_state.calendar = mock_calendar
        mock_state.get_formatted_date = MagicMock(return_value="Ides of June, 708 AUC")
        
        # Add some mock senators with proper name properties
        quintus_mock = MagicMock()
        quintus_mock.name = "Quintus Fabius"  # Set as property, not mock name
        
        caius_mock = MagicMock()
        caius_mock.name = "Caius Aurelius"
        
        marcus_mock = MagicMock()
        marcus_mock.name = "Marcus Tullius"
        
        mock_state.senators = [quintus_mock, caius_mock, marcus_mock]
        
        return mock_state

    @pytest.fixture
    def narrative_context(self):
        """Create a mock NarrativeContext for testing."""
        mock_context = MagicMock(spec=NarrativeContext)
        mock_context.get_recent_events = MagicMock(return_value=[
            NarrativeEvent(
                id=str(uuid.uuid4()),
                event_type="daily_event",
                description="A strange comet was seen in the night sky.",
                date={"year": -46, "month": 6, "day": 14},
                significance=2,
                tags=["omen", "daily"],
                entities=["Rome"],
                metadata={"title": "Strange Comet Sighting"}
            )
        ])
        mock_context.recurring_entities = {"Temple of Jupiter": 5, "Temple of Vesta": 3, "Pontifex Maximus": 4}
        return mock_context

    @pytest.fixture
    def religious_generator(self, llm_provider):
        """Create a ReligiousEventGenerator instance for testing."""
        return ReligiousEventGenerator(llm_provider)

    def test_initialization(self, llm_provider):
        """Test ReligiousEventGenerator initialization."""
        generator = ReligiousEventGenerator(llm_provider)
        assert generator.llm_provider == llm_provider
        assert hasattr(generator, 'religious_categories')
        assert isinstance(generator.religious_categories, list)
        assert len(generator.religious_categories) > 0
        assert "omen" in generator.religious_categories
        assert "ceremony" in generator.religious_categories  # Changed from "ritual" to "ceremony"

    @pytest.mark.asyncio
    async def test_generate_events(self, religious_generator, game_state, narrative_context):
        """Test generating religious events."""
        events = await religious_generator.generate_events(game_state, narrative_context)
        
        # Verify events were generated
        assert len(events) > 0
        
        # Check event properties
        for event in events:
            assert event.event_type == "religious_event"
            assert event.id is not None
            assert isinstance(event.description, str) and len(event.description) > 0
            assert event.date == {
                "year": game_state.calendar.year,
                "month": game_state.calendar.current_month_idx + 1,  # Convert to 1-based
                "day": game_state.calendar.current_day
            }
            assert event.significance >= 2  # Religious events should be significant
            assert "religious" in event.tags
            assert event.metadata.get("title") is not None
            assert event.metadata.get("category") in religious_generator.religious_categories
            assert "temple" in event.metadata  # Changed from "location" to "temple"

    @pytest.mark.asyncio
    async def test_generate_religious_event(self, religious_generator, game_state, narrative_context):
        """Test generating a specific religious event."""
        # Create test data
        category = "omen"
        current_date = {
            "year": game_state.calendar.year,
            "month": game_state.calendar.current_month_idx + 1,
            "day": game_state.calendar.current_day,
            "formatted": game_state.get_formatted_date()
        }
        recent_events = ["daily_event: A strange comet was seen in the night sky."]
        entities = ["Temple of Jupiter", "Pontifex Maximus", "Marcus Tullius"]
        
        # Generate a religious event
        event = await religious_generator._generate_religious_event(
            category, current_date, game_state, recent_events, entities
        )
        
        # Verify the event
        assert event is not None
        assert event.event_type == "religious_event"
        assert "omen" in event.tags
        assert event.significance >= 2  # Omens should be significant
        assert "Temple of Jupiter" in event.description
        assert "Omen" in event.metadata["title"]

    @pytest.mark.asyncio
    async def test_error_handling(self, religious_generator, game_state, narrative_context):
        """Test error handling during event generation."""
        # Make the LLM provider raise an exception
        religious_generator.llm_provider.generate_text.side_effect = Exception("Test error")
        
        # The generator should handle the error and return an empty list
        events = await religious_generator.generate_events(game_state, narrative_context)
        assert events == []
        
        # Test error handling in _generate_religious_event
        category = "omen"
        current_date = {
            "year": game_state.calendar.year,
            "month": game_state.calendar.current_month_idx + 1,
            "day": game_state.calendar.current_day,
            "formatted": game_state.get_formatted_date()
        }
        recent_events = ["daily_event: A strange comet was seen in the night sky."]
        entities = ["Temple of Jupiter", "Pontifex Maximus", "Marcus Tullius"]
        
        event = await religious_generator._generate_religious_event(
            category, current_date, game_state, recent_events, entities
        )
        assert event is None

    def test_extract_entities(self, religious_generator):
        """Test entity extraction from text."""
        text = "The Pontifex Maximus performed a ritual at the Temple of Jupiter, while Marcus Tullius observed."
        known_entities = ["Temple of Jupiter", "Pontifex Maximus", "Marcus Tullius", "Temple of Vesta"]
        
        entities = religious_generator._extract_entities(text, known_entities)
        
        assert "Temple of Jupiter" in entities
        assert "Pontifex Maximus" in entities
        assert "Marcus Tullius" in entities
        assert "Temple of Vesta" not in entities

    def test_extract_temple(self, religious_generator):
        """Test temple extraction from text."""
        text = "The ritual was performed at the Temple of Jupiter."
        temple = religious_generator._extract_temple(text)
        assert "Temple mentioned" in temple