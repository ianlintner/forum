#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test module for the Roman Calendar system.
This module tests the functionality of the RomanCalendar class and related components.
"""

import pytest
from datetime import datetime
from pathlib import Path

from roman_senate.core.roman_calendar import (
    RomanCalendar, RomanDate, Month, SpecialDay,
    CalendarType, DateFormat, DayClassification,
    ROMAN_MONTHS_PRE_JULIAN, ROMAN_MONTHS_JULIAN, SPECIAL_DAYS
)
from roman_senate.core.game_state import GameState, game_state
from roman_senate.core.persistence import (
    serialize_calendar, deserialize_calendar,
    serialize_game_state, deserialize_game_state
)


# --- Fixtures ---

@pytest.fixture
def pre_julian_calendar():
    """Create a pre-Julian calendar instance for testing."""
    return RomanCalendar(year=-100)  # 100 BCE


@pytest.fixture
def julian_calendar():
    """Create a Julian calendar instance for testing."""
    return RomanCalendar(year=-44, calendar_type=CalendarType.JULIAN)  # 44 BCE, Julian calendar


@pytest.fixture
def reset_game_state():
    """Reset the game state before and after tests."""
    # Save the original state
    orig_year = game_state.year
    orig_calendar = game_state.calendar
    
    # Reset for test
    game_state.reset(year=-55)  # 55 BCE
    
    yield game_state
    
    # Restore original or reset to defaults
    if orig_year and orig_calendar:
        game_state.year = orig_year
        game_state.calendar = orig_calendar
    else:
        game_state.reset()


# --- Test Calendar Initialization ---

def test_pre_julian_calendar_init(pre_julian_calendar):
    """Test initialization of a pre-Julian calendar."""
    assert pre_julian_calendar.year == -100
    assert pre_julian_calendar.calendar_type == CalendarType.PRE_JULIAN
    assert pre_julian_calendar.current_month_idx == 0
    assert pre_julian_calendar.current_day == 1
    assert pre_julian_calendar.current_month.name == "Martius"  # First month in pre-Julian
    assert len(pre_julian_calendar.months) == 12
    assert len(pre_julian_calendar.consuls) == 2  # Should have 2 consuls


def test_julian_calendar_init(julian_calendar):
    """Test initialization of a Julian calendar."""
    assert julian_calendar.year == -44
    assert julian_calendar.calendar_type == CalendarType.JULIAN
    assert julian_calendar.current_month_idx == 0
    assert julian_calendar.current_day == 1
    assert julian_calendar.current_month.name == "Ianuarius"  # First month in Julian
    assert len(julian_calendar.months) == 12


def test_calendar_type_auto_detection():
    """Test that calendar type is auto-detected based on year."""
    # Before 45 BCE should be pre-Julian
    calendar1 = RomanCalendar(year=-46)
    assert calendar1.calendar_type == CalendarType.PRE_JULIAN
    
    # 45 BCE and after should be Julian
    calendar2 = RomanCalendar(year=-45)
    assert calendar2.calendar_type == CalendarType.JULIAN
    
    calendar3 = RomanCalendar(year=-44)
    assert calendar3.calendar_type == CalendarType.JULIAN


def test_month_initialization():
    """Test that months are properly initialized with special days."""
    calendar = RomanCalendar(year=-50)
    
    # Check that Martius has special days
    march = next(m for m in calendar.months if m.name == "Martius")
    assert len(march.special_days) > 0
    
    # Check Kalendae Martiae
    kalends = march.get_special_day(1)
    assert kalends is not None
    assert kalends.name == "Kalendae Martiae"
    assert kalends.classification == DayClassification.FESTUS


# --- Test Date Formatting ---

def test_roman_date_modern_format(pre_julian_calendar):
    """Test modern date formatting."""
    date = pre_julian_calendar.get_current_date()
    formatted = date.format(DateFormat.MODERN)
    assert formatted == "1 March 100 BCE"


def test_roman_date_roman_full_format(pre_julian_calendar):
    """Test full Roman date formatting."""
    date = pre_julian_calendar.get_current_date()
    formatted = date.format(DateFormat.ROMAN_FULL)
    assert formatted == "Kalendae Martius"


def test_roman_date_abbreviated_format(pre_julian_calendar):
    """Test abbreviated Roman date formatting."""
    date = pre_julian_calendar.get_current_date()
    formatted = date.format(DateFormat.ROMAN_ABBREVIATED)
    assert "Kal." in formatted
    assert "Mar." in formatted


def test_roman_date_consular_format(pre_julian_calendar):
    """Test consular date formatting."""
    date = pre_julian_calendar.get_current_date()
    formatted = date.format(DateFormat.CONSULAR)
    assert "In the consulship of" in formatted
    assert "100 BCE" in formatted


def test_invalid_date_format(pre_julian_calendar):
    """Test that an invalid date format raises ValueError."""
    date = pre_julian_calendar.get_current_date()
    with pytest.raises(ValueError):
        date.format("invalid_format")


def test_format_current_date(pre_julian_calendar):
    """Test the calendar's format_current_date method."""
    formatted = pre_julian_calendar.format_current_date(DateFormat.MODERN)
    assert formatted == "1 March 100 BCE"


# --- Test Calendar Progression ---

def test_advance_day_basic(pre_julian_calendar):
    """Test basic day advancement."""
    assert pre_julian_calendar.current_day == 1
    assert pre_julian_calendar.current_month.name == "Martius"
    
    special_days = pre_julian_calendar.advance_day()
    
    assert pre_julian_calendar.current_day == 2
    assert pre_julian_calendar.current_month.name == "Martius"
    
    # Special day might be returned if day 1 is a special day
    assert isinstance(special_days, list)


def test_advance_multiple_days(pre_julian_calendar):
    """Test advancing multiple days at once."""
    assert pre_julian_calendar.current_day == 1
    
    special_days = pre_julian_calendar.advance_day(days=5)
    
    assert pre_julian_calendar.current_day == 6
    # Should include any special days encountered
    assert isinstance(special_days, list)


def test_month_transition(pre_julian_calendar):
    """Test transitioning to the next month."""
    # Move to the end of Martius (day 31)
    for _ in range(30):  # Already on day 1, so advance 30 more
        pre_julian_calendar.advance_day()
    
    assert pre_julian_calendar.current_day == 31
    assert pre_julian_calendar.current_month.name == "Martius"
    
    # Advance one more day to transition to Aprilis
    pre_julian_calendar.advance_day()
    
    assert pre_julian_calendar.current_day == 1
    assert pre_julian_calendar.current_month.name == "Aprilis"


def test_year_transition(pre_julian_calendar):
    """Test transitioning to the next year."""
    # The pre-Julian calendar starts with Martius (March)
    # We need to advance through all 12 months to complete a year
    
    # Start date should be 1 Martius -100
    assert pre_julian_calendar.year == -100
    assert pre_julian_calendar.current_month.name == "Martius"
    assert pre_julian_calendar.current_day == 1
    
    # Advance through the entire year (for each month, advance to last day and then one more)
    days_in_year = sum(month["days"] for month in ROMAN_MONTHS_PRE_JULIAN)
    for _ in range(days_in_year):
        pre_julian_calendar.advance_day()
    
    # Should be back to 1 Martius but in the next year (-99)
    assert pre_julian_calendar.year == -99
    assert pre_julian_calendar.current_month.name == "Martius"
    assert pre_julian_calendar.current_day == 1


def test_calendar_transition():
    """Test transition from pre-Julian to Julian calendar at 45 BCE."""
    # Set up a calendar close to the transition year
    calendar = RomanCalendar(year=-46)
    assert calendar.calendar_type == CalendarType.PRE_JULIAN
    
    # Find how many days to the end of the year
    # Go through each month and accumulate days
    days_to_advance = 0
    current_month_idx = calendar.current_month_idx
    
    # Add days from current month (minus days already passed)
    days_to_advance += calendar.months[current_month_idx].days - calendar.current_day + 1
    
    # Add days from remaining months
    for month_idx in range(current_month_idx + 1, len(calendar.months)):
        days_to_advance += calendar.months[month_idx].days
    
    calendar.advance_day(days_to_advance)
    
    # Should now be in year -45
    assert calendar.year == -45
    # Calendar type should now be Julian
    assert calendar.calendar_type == CalendarType.JULIAN


# --- Test Special Days ---

def test_special_day_detection(pre_julian_calendar):
    """Test detection of special days."""
    # 15th of March is the Ides of March, a special day
    # First ensure we're in Martius
    assert pre_julian_calendar.current_month.name == "Martius"
    
    # Advance to the 15th
    while pre_julian_calendar.current_day != 15:
        pre_julian_calendar.advance_day()
    
    # Check that it's identified as a special day
    special_day = pre_julian_calendar.current_month.get_special_day(15)
    assert special_day is not None
    assert special_day.name == "Idus Martiae"
    
    # Test get_special_events_for_current_day
    events = pre_julian_calendar.get_special_events_for_current_day()
    assert len(events) > 0
    assert events[0]["name"] == "Idus Martiae"


def test_special_day_classification(pre_julian_calendar):
    """Test day classification system."""
    # Test a day that we know has a classification
    march = next(m for m in pre_julian_calendar.months if m.name == "Martius")
    
    # Check day 15 (Ides of March)
    ides_day_class = march.day_classification(15)
    assert ides_day_class == DayClassification.NEFASTUS


# --- Test Senate Meeting Rules ---

def test_senate_can_meet(pre_julian_calendar):
    """Test determination if Senate can meet on a given day."""
    # Start on day 1 of Martius
    assert pre_julian_calendar.current_day == 1
    assert pre_julian_calendar.current_month.name == "Martius"
    
    can_meet, reason = pre_julian_calendar.can_hold_senate_session()
    
    # Validate that we get a boolean and explanation
    assert isinstance(can_meet, bool)
    assert isinstance(reason, str)
    
    # Test a day when Senate cannot meet (Ides of March is NEFASTUS)
    # Advance to the Ides
    while pre_julian_calendar.current_day != 15:
        pre_julian_calendar.advance_day()
    
    can_meet, reason = pre_julian_calendar.can_hold_senate_session()
    # In implementation, NEFASTUS classification check happens before exceptions check,
    # so despite being in 'exceptions' list, it returns False
    assert can_meet is False
    assert "cannot" in reason.lower()


def test_get_next_senate_day(pre_julian_calendar):
    """Test finding the next valid Senate meeting day."""
    next_date = pre_julian_calendar.get_next_senate_day()
    
    assert next_date is not None
    assert isinstance(next_date, RomanDate)
    
    # Create a temp calendar with the returned date
    temp_calendar = RomanCalendar(next_date.year, next_date.calendar_type)
    month_idx = next((i for i, m in enumerate(temp_calendar.months) if m.name == next_date.month.name), 0)
    temp_calendar.current_month_idx = month_idx
    temp_calendar.current_month = next_date.month
    temp_calendar.current_day = next_date.day
    
    # Verify this is truly a day when Senate can meet
    can_meet, _ = temp_calendar.can_hold_senate_session()
    assert can_meet is True


# --- Test GameState Integration ---

def test_game_state_calendar_initialization(reset_game_state):
    """Test initializing calendar from game state."""
    # game_state should have been reset with year -55 BCE
    assert reset_game_state.year == -55
    
    # Initialize calendar
    calendar = reset_game_state.initialize_calendar()
    
    assert calendar is not None
    assert calendar.year == -55
    # As of -55 BCE, the calendar should be pre-Julian
    assert calendar.calendar_type == CalendarType.PRE_JULIAN


def test_game_state_calendar_operations(reset_game_state):
    """Test calendar operations via game state."""
    # Ensure calendar is initialized
    if not reset_game_state.calendar:
        reset_game_state.initialize_calendar()
    
    # Test advance_day
    special_days = reset_game_state.advance_day()
    assert isinstance(special_days, list)
    
    # Test get_formatted_date
    date_str = reset_game_state.get_formatted_date(DateFormat.MODERN)
    assert isinstance(date_str, str)
    assert "BCE" in date_str
    
    # Test can_hold_senate_session
    can_meet, reason = reset_game_state.can_hold_senate_session()
    assert isinstance(can_meet, bool)
    assert isinstance(reason, str)


def test_override_calendar_type(reset_game_state):
    """Test overriding the auto-detected calendar type."""
    # Even though -55 BCE would be pre-Julian, we can override it
    calendar = reset_game_state.initialize_calendar(
        year=-55, 
        calendar_type=CalendarType.JULIAN
    )
    
    assert calendar.calendar_type == CalendarType.JULIAN
    assert calendar.current_month.name == "Ianuarius"  # Julian starts with January


# --- Test Serialization/Deserialization ---

def test_calendar_serialization(pre_julian_calendar):
    """Test serializing a calendar to a dictionary."""
    # First advance a few days to get a non-default state
    pre_julian_calendar.advance_day(10)
    
    # Serialize
    calendar_dict = serialize_calendar(pre_julian_calendar)
    
    assert calendar_dict is not None
    assert calendar_dict["year"] == -100
    assert calendar_dict["calendar_type"] == "pre_julian"
    assert calendar_dict["current_day"] == 11  # We advanced 10 days from day 1
    assert calendar_dict["current_month_idx"] == 0  # Still in Martius (first month)
    assert isinstance(calendar_dict["consuls"], list)
    assert len(calendar_dict["consuls"]) == 2


def test_calendar_deserialization(reset_game_state):
    """Test deserializing a calendar from a dictionary."""
    # Create a calendar dictionary
    calendar_dict = {
        "year": -63,  # Year of Cicero's consulship
        "calendar_type": "pre_julian",
        "current_month_idx": 2,  # Maius (3rd month in pre-Julian)
        "current_day": 15,  # Ides of May
        "consuls": ["Marcus Tullius Cicero", "Gaius Antonius Hybrida"]
    }
    
    # Deserialize
    deserialize_calendar(reset_game_state, calendar_dict)
    
    # Check that the calendar was properly reconstructed
    assert reset_game_state.calendar is not None
    assert reset_game_state.calendar.year == -63
    assert reset_game_state.calendar.calendar_type == CalendarType.PRE_JULIAN
    assert reset_game_state.calendar.current_month_idx == 2
    assert reset_game_state.calendar.current_day == 15
    assert reset_game_state.calendar.current_month.name == "Maius"
    assert len(reset_game_state.calendar.consuls) == 2
    assert "Cicero" in reset_game_state.calendar.consuls[0]


def test_game_state_with_calendar_serialization(reset_game_state):
    """Test full game state serialization including calendar."""
    # Ensure we have a calendar
    reset_game_state.initialize_calendar()
    
    # Advance a bit to get a non-default state
    reset_game_state.advance_day(5)
    
    # Serialize the game state
    state_dict = serialize_game_state(reset_game_state)
    
    # Check that calendar data is included
    assert "calendar" in state_dict
    assert state_dict["calendar"] is not None
    assert state_dict["calendar"]["year"] == -55
    assert state_dict["calendar"]["current_day"] == 6  # Advanced 5 days from day 1
    
    # Now reset and deserialize
    original_calendar = reset_game_state.calendar
    reset_game_state.calendar = None
    
    deserialize_game_state(state_dict)
    
    # Check that calendar was restored
    assert reset_game_state.calendar is not None
    assert reset_game_state.calendar.year == -55
    assert reset_game_state.calendar.current_day == 6


def test_leap_year_detection():
    """Test detection of leap years."""
    # In Julian calendar, every 4th year should be a leap year
    # Non-leap year
    calendar1 = RomanCalendar(year=-43, calendar_type=CalendarType.JULIAN)
    assert calendar1.is_leap_year() is False
    
    # Leap year (divisible by 4)
    calendar2 = RomanCalendar(year=-44, calendar_type=CalendarType.JULIAN)
    assert calendar2.is_leap_year() is True
    
    # Pre-Julian calendar doesn't have leap years
    calendar3 = RomanCalendar(year=-48, calendar_type=CalendarType.PRE_JULIAN)
    assert calendar3.is_leap_year() is False