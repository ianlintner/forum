#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Roman Senate Game
Game State Module

This module manages the global game state for the Roman Senate simulation,
including calendar tracking, senators, topics, and voting history.
"""

from typing import List, Dict, Any, Optional, Tuple, Union

from .roman_calendar import RomanCalendar, CalendarType, DateFormat


class GameState:
    """
    Manages global game state for the Roman Senate simulation.
    Stores information about senators, topics, votes, and game history.
    """
    
    def __init__(self):
        """Initialize a new game state."""
        self.game_history = []
        self.senators = []
        self.current_topic = None
        self.year = None
        self.voting_results = []
        self.calendar = None  # Calendar will be initialized when year is set
        
    def add_topic_result(self, topic, votes):
        """
        Add a topic result to the game history.
        
        Args:
            topic: The topic that was debated
            votes: The voting results
        """
        self.game_history.append({
            'topic': topic,
            'votes': votes,
            'year': self.year,
            'year_display': f"{abs(self.year)} BCE" if self.year else "Unknown"
        })
        
    def reset(self, year=None):
        """
        Reset the game state for a new session.
        
        Args:
            year: Optional year to set (negative for BCE)
        """
        old_year = self.year
        self.__init__()
        self.year = year or old_year or -100  # Default to 100 BCE if no year specified
        self.initialize_calendar(self.year)
        
    def initialize_calendar(self, year=None, calendar_type=None):
        """
        Initialize the Roman calendar with the current game year.
        
        Args:
            year: Year to use (negative for BCE, defaults to game state year)
            calendar_type: Optional calendar type override (auto-detected by year if None)
            
        Returns:
            The initialized calendar
        """
        if year is None:
            year = self.year or -100  # Default to 100 BCE
        
        # Create the calendar
        self.calendar = RomanCalendar(year, calendar_type)
        return self.calendar
    
    def advance_day(self, days=1):
        """
        Advance the calendar by the specified number of days.
        
        Args:
            days: Number of days to advance
            
        Returns:
            List of special days encountered
        """
        if self.calendar is None:
            self.initialize_calendar()
        
        return self.calendar.advance_day(days)
    
    def get_formatted_date(self, format_type=DateFormat.MODERN):
        """
        Get the current date formatted according to the specified type.
        
        Args:
            format_type: DateFormat enum specifying the format style
            
        Returns:
            Formatted date string
        """
        if self.calendar is None:
            self.initialize_calendar()
        
        return self.calendar.format_current_date(format_type)
    
    def can_hold_senate_session(self):
        """
        Check if a senate session can be held on the current calendar day.
        
        Returns:
            Tuple of (bool, reason) indicating if session can be held and why
        """
        if self.calendar is None:
            self.initialize_calendar()
        
        return self.calendar.can_hold_senate_session()


# Create a global instance of the game state
game_state = GameState()