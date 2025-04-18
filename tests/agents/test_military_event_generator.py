#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test module for the MilitaryEventGenerator.
This module tests the functionality of the MilitaryEventGenerator class.
"""

import pytest
import uuid
from unittest.mock import MagicMock, patch, AsyncMock
from typing import Dict, List, Any

from roman_senate.agents.event_generators.military_event_generator import MilitaryEventGenerator
from roman_senate.core.narrative_context import NarrativeContext, NarrativeEvent
from roman_senate.core.game_state import GameState
from roman_senate.core.roman_calendar import RomanCalendar
from roman_senate.utils.llm.base import LLMProvider


class TestMilitaryEventGenerator:
    """Test suite for the MilitaryEventGenerator class."""

    @pytest.fixture
    def llm_provider(self):
        """Create a mock LLM provider."""
        mock_provider = MagicMock(spec=LLMProvider)
        mock_provider.generate_text = AsyncMock(return_value="Battle of Thapsus\nCaesar's forces decisively defeated the Pompeian forces led by Metellus Scipio and Cato the Younger near Thapsus in North Africa. The legion XV Apollinaris showed exceptional valor on the left flank.")
        return mock_provider

    @pytest.fixture
    def game_state(self):
        """Create a mock GameState for testing."""
        mock_state = MagicMock(spec=GameState)
        mock_calendar = MagicMock(spec=RomanCalendar)
        mock_calendar.year = -46
        mock_calendar.current_month_idx = 3  # April (0-indexed)
        mock_calendar.current_day = 6
        mock_state.calendar = mock_calendar
        mock_state.get_formatted_date = MagicMock(return_value="6th day of April, 708 AUC")
        
        # Add some mock senators with proper name properties
        cicero_mock = MagicMock()
        cicero_mock.name = "Cicero"  # Set as property, not mock name
        
        cato_mock = MagicMock()
        cato_mock.name = "Cato"
        
        caesar_mock = MagicMock()
        caesar_mock.name = "Caesar"
        
        mock_state.senators = [cicero_mock, cato_mock, caesar_mock]
        
        return mock_state

    @pytest.fixture
    def narrative_context(self):
        """Create a mock NarrativeContext for testing."""
        mock_context = MagicMock(spec=NarrativeContext)
        mock_context.get_recent_events = MagicMock(return_value=[
            NarrativeEvent(
                id=str(uuid.uuid4()),
                event_type="daily_event",
                description="A shipment of grain arrived from Egypt.",
                date={"year": -46, "month": 4, "day": 5},
                significance=1,
                tags=["market", "daily"],
                entities=["Alexandria"],
                metadata={"title": "Grain Shipment Arrives"}
            )
        ])
        mock_context.recurring_entities = {"Caesar": 5, "Cicero": 3, "Legion X": 2}
        return mock_context

    @pytest.fixture
    def military_generator(self, llm_provider):
        """Create a MilitaryEventGenerator instance for testing."""
        return MilitaryEventGenerator(llm_provider)

    def test_initialization(self, llm_provider):
        """Test MilitaryEventGenerator initialization."""
        generator = MilitaryEventGenerator(llm_provider)
        assert generator.llm_provider == llm_provider
        assert hasattr(generator, 'military_categories')
        assert isinstance(generator.military_categories, list)
        assert len(generator.military_categories) > 0
        assert "battle" in generator.military_categories
        assert "troop_movement" in generator.military_categories

    @pytest.mark.asyncio
    async def test_generate_events(self, military_generator, game_state, narrative_context):
        """Test generating military events."""
        events = await military_generator.generate_events(game_state, narrative_context)
        
        # Verify events were generated
        assert len(events) > 0
        
        # Check event properties
        for event in events:
            assert event.event_type == "military_event"
            assert event.id is not None
            assert isinstance(event.description, str) and len(event.description) > 0
            assert event.date == {
                "year": game_state.calendar.year,
                "month": game_state.calendar.current_month_idx + 1,  # Convert to 1-based
                "day": game_state.calendar.current_day
            }
            assert event.significance >= 2  # Military events should be significant
            assert "military" in event.tags
            assert event.metadata.get("title") is not None
            assert event.metadata.get("category") in military_generator.military_categories
            assert "location" in event.metadata

    @pytest.mark.asyncio
    async def test_generate_military_event(self, military_generator, game_state, narrative_context):
        """Test generating a specific military event."""
        # Create test data
        category = "battle"
        current_date = {
            "year": game_state.calendar.year,
            "month": game_state.calendar.current_month_idx + 1,
            "day": game_state.calendar.current_day,
            "formatted": game_state.get_formatted_date()
        }
        recent_events = ["daily_event: A shipment of grain arrived from Egypt."]
        entities = ["Caesar", "Cicero", "Legion X"]
        
        # Generate a military event
        event = await military_generator._generate_military_event(
            category, current_date, game_state, recent_events, entities
        )
        
        # Verify the event
        assert event is not None
        assert event.event_type == "military_event"
        assert "battle" in event.tags
        assert event.significance == 3  # Battle should be high significance
        assert "Battle of Thapsus" in event.metadata["title"]
        assert "Caesar" in event.description

    @pytest.mark.asyncio
    async def test_error_handling(self, military_generator, game_state, narrative_context):
        """Test error handling during event generation."""
        # Make the LLM provider raise an exception
        military_generator.llm_provider.generate_text.side_effect = Exception("Test error")
        
        # The generator should handle the error and return an empty list
        events = await military_generator.generate_events(game_state, narrative_context)
        assert events == []
        
        # Test error handling in _generate_military_event
        category = "battle"
        current_date = {
            "year": game_state.calendar.year,
            "month": game_state.calendar.current_month_idx + 1,
            "day": game_state.calendar.current_day,
            "formatted": game_state.get_formatted_date()
        }
        recent_events = ["daily_event: A shipment of grain arrived from Egypt."]
        entities = ["Caesar", "Cicero", "Legion X"]
        
        event = await military_generator._generate_military_event(
            category, current_date, game_state, recent_events, entities
        )
        assert event is None

    def test_extract_entities(self, military_generator):
        """Test entity extraction from text."""
        text = "Caesar ordered Legion X to march to Rome, where Cicero awaited their arrival."
        known_entities = ["Caesar", "Cicero", "Legion X", "Pompey"]
        
        entities = military_generator._extract_entities(text, known_entities)
        
        assert "Caesar" in entities
        assert "Cicero" in entities
        assert "Legion X" in entities
        assert "Pompey" not in entities

    def test_extract_location(self, military_generator):
        """Test location extraction from text."""
        text = "The battle took place near Rome."
        location = military_generator._extract_location(text)
        assert location == "Various locations"  # Default implementation returns this