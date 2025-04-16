#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test module for the StoryCrierAgent.
This module tests the functionality of the StoryCrierAgent class.
"""

import pytest
from unittest.mock import MagicMock, patch
from typing import Dict, List, Any

from roman_senate.agents.story_crier_agent import StoryCrierAgent
from roman_senate.core.roman_calendar import RomanDate


class TestStoryCrierAgent:
    """Test suite for the StoryCrierAgent class."""

    @pytest.fixture
    def llm_provider(self):
        """Create a mock LLM provider."""
        mock_provider = MagicMock()
        mock_provider.generate_text = MagicMock(return_value="Mock announcement text")
        return mock_provider

    @pytest.fixture
    def story_crier(self, llm_provider):
        """Create a StoryCrierAgent instance for testing."""
        return StoryCrierAgent(llm_provider)

    @pytest.fixture
    def roman_date(self):
        """Create a sample RomanDate for testing."""
        mock_date = MagicMock(spec=RomanDate)
        mock_date.year = -50
        mock_date.month = 3
        mock_date.day = 15
        mock_date.to_string = MagicMock(return_value="Kalendae Martius, 704 AUC")
        return mock_date

    @pytest.fixture
    def sample_announcements(self):
        """Create sample announcements for testing."""
        return [
            {
                "title": "Battle of Pharsalus",
                "text": "Caesar defeated Pompey in a decisive battle of the civil war."
            },
            {
                "title": "Senate Reform",
                "text": "New reforms to the Senate procedures were announced today."
            }
        ]

    def test_initialization(self, llm_provider):
        """Test StoryCrierAgent initialization."""
        agent = StoryCrierAgent(llm_provider)
        assert agent.llm_provider == llm_provider
        assert hasattr(agent, 'announcements_cache')
        assert isinstance(agent.announcements_cache, dict)

    @pytest.mark.asyncio
    async def test_generate_announcements(self, story_crier, roman_date):
        """Test generating announcements for a date."""
        # Mock the get_announcements_for_current_date function
        with patch('roman_senate.agents.story_crier_agent.get_announcements_for_current_date') as mock_get:
            mock_get.return_value = [
                {"title": "Test Event", "text": "Test description"}
            ]
            
            # Call the method
            announcements = await story_crier.generate_announcements(
                year=roman_date.year,
                month=roman_date.month,
                day=roman_date.day,
                count=3
            )
            
            # Verify the function was called with the correct parameters
            mock_get.assert_called_once_with(
                current_year=roman_date.year,
                current_month=roman_date.month,
                current_day=roman_date.day,
                count=3
            )
            
            # Check the result
            assert len(announcements) == 1
            assert announcements[0]["title"] == "Test Event"
            assert announcements[0]["text"] == "Test description"
            
            # Test caching
            cache_key = f"{roman_date.year}_{roman_date.month}_{roman_date.day}"
            assert cache_key in story_crier.announcements_cache
            
            # Call again to test cache
            mock_get.reset_mock()
            cached_announcements = await story_crier.generate_announcements(
                year=roman_date.year,
                month=roman_date.month,
                day=roman_date.day
            )
            
            # Should use cache, not call the function again
            mock_get.assert_not_called()
            assert cached_announcements == announcements

    def test_display_announcements(self, story_crier, sample_announcements):
        """Test displaying announcements."""
        # This is mostly a visual function, so we just ensure it doesn't error
        with patch('roman_senate.agents.story_crier_agent.console.print') as mock_print:
            story_crier.display_announcements(sample_announcements)
            
            # Verify console.print was called multiple times
            assert mock_print.call_count > 0
            
            # Test with empty announcements
            mock_print.reset_mock()
            story_crier.display_announcements([])
            mock_print.assert_not_called()