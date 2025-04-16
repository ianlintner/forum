#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test module for the Historical Events Database.
This module tests the functionality of the historical events database and related components.
"""

import pytest
from unittest.mock import MagicMock, patch
from typing import Dict, List, Any, Optional

from roman_senate.core.historical_events import (
    EventCategory, EventImportance, HistoricalEvent, HistoricalEventsDatabase,
    get_events_for_date, get_random_relevant_event, filter_events_by_type,
    filter_events_by_importance, get_announcements_for_current_date,
    historical_events_db
)
from roman_senate.core.roman_calendar import RomanDate


class TestHistoricalEvent:
    """Test suite for the HistoricalEvent class."""

    @pytest.fixture
    def sample_event(self):
        """Create a sample historical event for testing."""
        return HistoricalEvent(
            id=100,
            title="Test Event",
            description="This is a test historical event",
            year=-50,
            month=3,
            day=15,
            categories=[EventCategory.POLITICAL, EventCategory.MILITARY],
            importance=EventImportance.MAJOR,
            location="Rome",
            people_involved=["Caesar", "Cicero"],
            source="Test Source",
            narrative_hooks=["Test Hook 1", "Test Hook 2"]
        )

    def test_initialization(self, sample_event):
        """Test HistoricalEvent initialization."""
        assert sample_event.id == 100
        assert sample_event.title == "Test Event"
        assert sample_event.description == "This is a test historical event"
        assert sample_event.year == -50
        assert sample_event.month == 3
        assert sample_event.day == 15
        assert len(sample_event.categories) == 2
        assert EventCategory.POLITICAL in sample_event.categories
        assert EventCategory.MILITARY in sample_event.categories
        assert sample_event.importance == EventImportance.MAJOR
        assert sample_event.location == "Rome"
        assert len(sample_event.people_involved) == 2
        assert "Caesar" in sample_event.people_involved
        assert "Cicero" in sample_event.people_involved
        assert sample_event.source == "Test Source"
        assert len(sample_event.narrative_hooks) == 2

    def test_initialization_with_none_lists(self):
        """Test HistoricalEvent initialization with None for list fields."""
        event = HistoricalEvent(
            id=101,
            title="Test Event 2",
            description="Another test event",
            year=-49,
            categories=None,
            people_involved=None,
            narrative_hooks=None
        )
        
        # __post_init__ should initialize these as empty lists
        assert isinstance(event.categories, list)
        assert len(event.categories) == 0
        assert isinstance(event.people_involved, list)
        assert len(event.people_involved) == 0
        assert isinstance(event.narrative_hooks, list)
        assert len(event.narrative_hooks) == 0

    def test_has_exact_date(self, sample_event):
        """Test has_exact_date method."""
        assert sample_event.has_exact_date() is True
        
        # Create an event with only year and month
        event_no_day = HistoricalEvent(
            id=102,
            title="Test Event No Day",
            description="Test event without day",
            year=-48,
            month=4,
            day=None
        )
        assert event_no_day.has_exact_date() is False

    def test_has_month(self, sample_event):
        """Test has_month method."""
        assert sample_event.has_month() is True
        
        # Create an event with only year
        event_no_month = HistoricalEvent(
            id=103,
            title="Test Event No Month",
            description="Test event without month",
            year=-47,
            month=None
        )
        assert event_no_month.has_month() is False

    def test_format_date(self, sample_event):
        """Test format_date method."""
        # Full date (year, month, day)
        assert sample_event.format_date() == "March 15, 50 BCE"
        
        # Year and month only
        event_month_only = HistoricalEvent(
            id=104,
            title="Test Month Only",
            description="Test event with month only",
            year=-46,
            month=7,
            day=None
        )
        assert event_month_only.format_date() == "July, 46 BCE"
        
        # Year only
        event_year_only = HistoricalEvent(
            id=105,
            title="Test Year Only",
            description="Test event with year only",
            year=-45,
            month=None,
            day=None
        )
        assert event_year_only.format_date() == "45 BCE"
        
        # CE year
        event_ce = HistoricalEvent(
            id=106,
            title="Test CE Year",
            description="Test event with CE year",
            year=14,
            month=8,
            day=19
        )
        assert event_ce.format_date() == "August 19, 14 CE"

    def test_to_dict(self, sample_event):
        """Test to_dict method."""
        event_dict = sample_event.to_dict()
        
        assert event_dict["id"] == 100
        assert event_dict["title"] == "Test Event"
        assert event_dict["description"] == "This is a test historical event"
        assert event_dict["year"] == -50
        assert event_dict["month"] == 3
        assert event_dict["day"] == 15
        assert "political" in event_dict["categories"]
        assert "military" in event_dict["categories"]
        assert event_dict["importance"] == 3  # MAJOR = 3
        assert event_dict["location"] == "Rome"
        assert "Caesar" in event_dict["people_involved"]
        assert "Cicero" in event_dict["people_involved"]
        assert event_dict["source"] == "Test Source"
        assert "Test Hook 1" in event_dict["narrative_hooks"]

    def test_from_dict(self):
        """Test from_dict class method."""
        event_dict = {
            "id": 107,
            "title": "From Dict Test",
            "description": "Event created from dictionary",
            "year": -44,
            "month": 3,
            "day": 15,
            "categories": ["political", "religious"],
            "importance": 2,  # MODERATE = 2
            "location": "Senate House, Rome",
            "people_involved": ["Caesar", "Brutus"],
            "source": "Plutarch",
            "narrative_hooks": ["Betrayal", "Conspiracy"]
        }
        
        event = HistoricalEvent.from_dict(event_dict)
        
        assert event.id == 107
        assert event.title == "From Dict Test"
        assert event.year == -44
        assert event.month == 3
        assert event.day == 15
        assert len(event.categories) == 2
        assert EventCategory.POLITICAL in event.categories
        assert EventCategory.RELIGIOUS in event.categories
        assert event.importance == EventImportance.MODERATE
        assert event.location == "Senate House, Rome"
        assert "Caesar" in event.people_involved
        assert "Brutus" in event.people_involved
        assert "Betrayal" in event.narrative_hooks


class TestHistoricalEventsDatabase:
    """Test suite for the HistoricalEventsDatabase class."""

    @pytest.fixture
    def test_db(self):
        """Create a test database with a few events."""
        db = HistoricalEventsDatabase()
        # Clear the default events and add our test events
        db.events = []
        
        # Add some test events
        db.add_event(HistoricalEvent(
            id=1,
            title="Test Political Event",
            description="A political event",
            year=-50,
            month=3,
            day=15,
            categories=[EventCategory.POLITICAL],
            importance=EventImportance.MAJOR,
            location="Rome",
            people_involved=["Caesar"]
        ))
        
        db.add_event(HistoricalEvent(
            id=2,
            title="Test Military Event",
            description="A military event",
            year=-49,
            month=7,
            categories=[EventCategory.MILITARY],
            importance=EventImportance.MODERATE,
            location="Gaul",
            people_involved=["Caesar", "Vercingetorix"]
        ))
        
        db.add_event(HistoricalEvent(
            id=3,
            title="Test Religious Event",
            description="A religious event",
            year=-48,
            categories=[EventCategory.RELIGIOUS],
            importance=EventImportance.MINOR,
            location="Temple of Jupiter, Rome",
            people_involved=["Pontifex Maximus"]
        ))
        
        db.add_event(HistoricalEvent(
            id=4,
            title="Test Cultural Event",
            description="A cultural event",
            year=-50,
            month=5,
            day=1,
            categories=[EventCategory.CULTURAL],
            importance=EventImportance.BACKGROUND,
            location="Theater of Pompey, Rome"
        ))
        
        return db

    def test_initialization(self):
        """Test HistoricalEventsDatabase initialization."""
        db = HistoricalEventsDatabase()
        assert isinstance(db.events, list)
        assert len(db.events) > 0  # Should have some default events

    def test_add_event(self, test_db):
        """Test add_event method."""
        initial_count = len(test_db.events)
        
        new_event = HistoricalEvent(
            id=5,
            title="New Test Event",
            description="A newly added event",
            year=-47,
            categories=[EventCategory.ECONOMIC]
        )
        
        test_db.add_event(new_event)
        
        assert len(test_db.events) == initial_count + 1
        assert test_db.events[-1].id == 5
        assert test_db.events[-1].title == "New Test Event"

    def test_get_event_by_id(self, test_db):
        """Test get_event_by_id method."""
        event = test_db.get_event_by_id(2)
        
        assert event is not None
        assert event.id == 2
        assert event.title == "Test Military Event"
        
        # Test with non-existent ID
        assert test_db.get_event_by_id(999) is None

    def test_get_events_by_date(self, test_db):
        """Test get_events_by_date method."""
        # Test with year only
        events_year = test_db.get_events_by_date(year=-50)
        assert len(events_year) == 2
        assert any(e.title == "Test Political Event" for e in events_year)
        assert any(e.title == "Test Cultural Event" for e in events_year)
        
        # Test with year and month
        events_month = test_db.get_events_by_date(year=-50, month=3)
        assert len(events_month) == 1
        assert events_month[0].title == "Test Political Event"
        
        # Test with full date
        events_day = test_db.get_events_by_date(year=-50, month=3, day=15)
        assert len(events_day) == 1
        assert events_day[0].title == "Test Political Event"
        
        # Test with date that has no events
        events_none = test_db.get_events_by_date(year=-51)
        assert len(events_none) == 0

    def test_get_events_by_year_range(self, test_db):
        """Test get_events_by_year_range method."""
        events = test_db.get_events_by_year_range(-50, -49)
        assert len(events) == 3
        
        # Test with single year
        events_single = test_db.get_events_by_year_range(-48, -48)
        assert len(events_single) == 1
        assert events_single[0].title == "Test Religious Event"

    def test_get_events_by_category(self, test_db):
        """Test get_events_by_category method."""
        events = test_db.get_events_by_category(EventCategory.POLITICAL)
        assert len(events) == 1
        assert events[0].title == "Test Political Event"
        
        # Test with category that has no events
        events_none = test_db.get_events_by_category(EventCategory.LEGAL)
        assert len(events_none) == 0

    def test_get_events_by_importance(self, test_db):
        """Test get_events_by_importance method."""
        events = test_db.get_events_by_importance(EventImportance.MAJOR)
        assert len(events) == 1
        assert events[0].title == "Test Political Event"
        
        events_moderate = test_db.get_events_by_importance(EventImportance.MODERATE)
        assert len(events_moderate) == 1
        assert events_moderate[0].title == "Test Military Event"

    def test_filter_events(self, test_db):
        """Test filter_events method."""
        # Test filtering by year range
        events = test_db.filter_events(year_range=(-50, -49))
        assert len(events) == 3
        
        # Test filtering by categories
        events = test_db.filter_events(categories=[EventCategory.POLITICAL, EventCategory.MILITARY])
        assert len(events) == 2
        
        # Test filtering by importance
        # The implementation returns events with importance >= the specified importance
        events = test_db.filter_events(importance=EventImportance.MODERATE)
        # Should return MAJOR and MODERATE events (not MINOR or BACKGROUND)
        assert len(events) == 2
        assert any(e.importance == EventImportance.MAJOR for e in events)
        assert any(e.importance == EventImportance.MODERATE for e in events)
        assert not any(e.importance == EventImportance.MINOR for e in events)
        assert not any(e.importance == EventImportance.BACKGROUND for e in events)
        
        # Test filtering by people
        events = test_db.filter_events(people=["Caesar"])
        assert len(events) == 2
        
        # Test filtering by location
        events = test_db.filter_events(location="Rome")
        assert len(events) == 3
        
        # Test combined filters
        events = test_db.filter_events(
            year_range=(-50, -48),
            categories=[EventCategory.POLITICAL, EventCategory.RELIGIOUS],
            importance=EventImportance.MINOR,
            location="Rome"
        )
        # Should return events with importance >= MINOR in Rome with the specified categories
        assert len(events) == 2
        assert any(e.title == "Test Political Event" for e in events)
        assert any(e.title == "Test Religious Event" for e in events)

    def test_get_random_event(self, test_db):
        """Test get_random_event method."""
        # Test with no filters
        event = test_db.get_random_event()
        assert event is not None
        assert event.id in [1, 2, 3, 4]
        
        # Test with filters
        event = test_db.get_random_event(
            year_range=(-50, -50),
            categories=[EventCategory.POLITICAL]
        )
        assert event is not None
        assert event.id == 1
        assert event.title == "Test Political Event"
        
        # Test with filters that match no events
        event = test_db.get_random_event(
            year_range=(-60, -55)
        )
        assert event is None

    def test_get_relevant_events(self, test_db):
        """Test get_relevant_events method."""
        # Test with current year -45
        events = test_db.get_relevant_events(current_year=-45, timeframe=10, count=5)
        assert len(events) > 0
        
        # Test with categories filter
        events = test_db.get_relevant_events(
            current_year=-45,
            timeframe=10,
            count=5,
            categories=[EventCategory.MILITARY]
        )
        assert len(events) > 0
        assert all(EventCategory.MILITARY in e.categories for e in events)

    def test_get_events_for_crier(self, test_db):
        """Test get_events_for_crier method."""
        announcements = test_db.get_events_for_crier(current_year=-45, count=3)
        assert isinstance(announcements, list)
        assert len(announcements) > 0
        
        # Check announcement format
        for announcement in announcements:
            assert "title" in announcement
            assert "text" in announcement
            assert isinstance(announcement["title"], str)
            assert isinstance(announcement["text"], str)


class TestHistoricalEventsFunctions:
    """Test suite for the standalone functions in the historical_events module."""

    def test_get_events_for_date(self):
        """Test get_events_for_date function."""
        events = get_events_for_date(year=-44, month=3, day=15)
        assert isinstance(events, list)
        
        # There should be at least one event for the Ides of March
        if events:
            assert any("Caesar" in str(e.people_involved) for e in events)

    def test_get_random_relevant_event(self):
        """Test get_random_relevant_event function."""
        event = get_random_relevant_event(current_year=-45)
        
        # May return None if no events match, but if it returns something, check format
        if event:
            assert "title" in event
            assert "text" in event
            assert isinstance(event["title"], str)
            assert isinstance(event["text"], str)

    def test_filter_events_by_type(self):
        """Test filter_events_by_type function."""
        # Create some test events
        events = [
            HistoricalEvent(
                id=1,
                title="Political Test",
                description="Test",
                year=-50,
                categories=[EventCategory.POLITICAL]
            ),
            HistoricalEvent(
                id=2,
                title="Military Test",
                description="Test",
                year=-49,
                categories=[EventCategory.MILITARY]
            )
        ]
        
        # Filter by political
        filtered = filter_events_by_type(events, "political")
        assert len(filtered) == 1
        assert filtered[0].title == "Political Test"
        
        # Filter by non-existent type
        filtered = filter_events_by_type(events, "invalid_type")
        assert len(filtered) == 0

    def test_filter_events_by_importance(self):
        """Test filter_events_by_importance function."""
        # Create some test events
        events = [
            HistoricalEvent(
                id=1,
                title="Major Test",
                description="Test",
                year=-50,
                importance=EventImportance.MAJOR
            ),
            HistoricalEvent(
                id=2,
                title="Minor Test",
                description="Test",
                year=-49,
                importance=EventImportance.MINOR
            )
        ]
        
        # Filter by MAJOR
        filtered = filter_events_by_importance(events, "MAJOR")
        assert len(filtered) == 1
        assert filtered[0].title == "Major Test"
        
        # Filter by non-existent importance
        filtered = filter_events_by_importance(events, "INVALID")
        assert len(filtered) == 0

    def test_get_announcements_for_current_date(self):
        """Test get_announcements_for_current_date function."""
        announcements = get_announcements_for_current_date(
            current_year=-44,
            current_month=3,
            current_day=15,
            count=3
        )
        
        assert isinstance(announcements, list)
        # There should be announcements for the Ides of March
        assert len(announcements) > 0
        
        # Check announcement format
        for announcement in announcements:
            assert "title" in announcement
            assert "text" in announcement


class TestRomanCalendarIntegration:
    """Test integration with the Roman calendar system."""

    @pytest.fixture
    def mock_roman_date(self):
        """Create a mock RomanDate for testing."""
        mock_date = MagicMock(spec=RomanDate)
        mock_date.year = -44
        mock_date.month = 3
        mock_date.day = 15
        return mock_date

    def test_get_events_for_roman_date(self, mock_roman_date):
        """Test getting events for a RomanDate."""
        events = get_events_for_date(
            year=mock_roman_date.year,
            month=mock_roman_date.month,
            day=mock_roman_date.day
        )
        
        assert isinstance(events, list)
        # There should be events for the Ides of March 44 BCE
        if events:
            assert any("Caesar" in str(e.people_involved) for e in events)

    def test_announcements_for_roman_date(self, mock_roman_date):
        """Test getting announcements for a RomanDate."""
        announcements = get_announcements_for_current_date(
            current_year=mock_roman_date.year,
            current_month=mock_roman_date.month,
            current_day=mock_roman_date.day,
            count=3
        )
        
        assert isinstance(announcements, list)
        assert len(announcements) > 0