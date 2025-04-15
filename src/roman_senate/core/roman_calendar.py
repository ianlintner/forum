#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Roman Senate Game
Roman Calendar Module

This module implements a historically accurate Roman calendar system with
both pre-Julian and Julian calendar support, special days, and Senate meeting rules.
"""

from enum import Enum
import random
from typing import List, Dict, Tuple, Optional, Any, Union


class CalendarType(Enum):
    """Calendar system type."""
    PRE_JULIAN = "pre_julian"  # Traditional calendar (before 45 BCE)
    JULIAN = "julian"          # Julian calendar reform (45 BCE and after)


class DateFormat(Enum):
    """Date display format options."""
    MODERN = "modern"              # e.g., "15 March 100 BCE"
    ROMAN_FULL = "roman_full"      # e.g., "ante diem XVI Kalendas Apriles"
    ROMAN_ABBREVIATED = "roman_abbreviated"  # e.g., "a.d. XVI Kal. Apr."
    CONSULAR = "consular"          # e.g., "In the consulship of Marcus and Gaius"


class DayClassification(Enum):
    """Roman day classifications affecting legal and religious activities."""
    FASTUS = "F"       # Legal business permitted
    NEFASTUS = "N"     # Legal business forbidden
    COMITIALIS = "C"   # Public assemblies permitted
    INTERCISUS = "IN"  # Split day (morning/evening nefastus, midday fastus)
    RELIGIOSUS = "RE"  # Unlucky days
    FESTUS = "FE"      # Festival days


# Month definitions for pre-Julian calendar
# In the pre-Julian calendar, the year started with March (Martius)
ROMAN_MONTHS_PRE_JULIAN = [
    {
        "name": "Martius", 
        "english": "March", 
        "days": 31, 
        "position": 1,
        "kalends": 1,
        "nones": 7,   # 7th day of March
        "ides": 15    # 15th day of March
    },
    {
        "name": "Aprilis", 
        "english": "April", 
        "days": 29, 
        "position": 2,
        "kalends": 1,
        "nones": 5,   # 5th day
        "ides": 13    # 13th day
    },
    {
        "name": "Maius", 
        "english": "May", 
        "days": 31, 
        "position": 3,
        "kalends": 1,
        "nones": 7,
        "ides": 15
    },
    {
        "name": "Iunius", 
        "english": "June", 
        "days": 29, 
        "position": 4,
        "kalends": 1,
        "nones": 5,
        "ides": 13
    },
    {
        "name": "Quintilis", 
        "english": "July", 
        "days": 31, 
        "position": 5,
        "kalends": 1,
        "nones": 7,
        "ides": 15
    },
    {
        "name": "Sextilis", 
        "english": "August", 
        "days": 29, 
        "position": 6,
        "kalends": 1,
        "nones": 5,
        "ides": 13
    },
    {
        "name": "September", 
        "english": "September", 
        "days": 29, 
        "position": 7,
        "kalends": 1,
        "nones": 5,
        "ides": 13
    },
    {
        "name": "October", 
        "english": "October", 
        "days": 31, 
        "position": 8,
        "kalends": 1,
        "nones": 7,
        "ides": 15
    },
    {
        "name": "November", 
        "english": "November", 
        "days": 29, 
        "position": 9,
        "kalends": 1,
        "nones": 5,
        "ides": 13
    },
    {
        "name": "December", 
        "english": "December", 
        "days": 29, 
        "position": 10,
        "kalends": 1,
        "nones": 5,
        "ides": 13
    },
    {
        "name": "Ianuarius", 
        "english": "January", 
        "days": 29, 
        "position": 11,
        "kalends": 1,
        "nones": 5,
        "ides": 13
    },
    {
        "name": "Februarius", 
        "english": "February", 
        "days": 28, 
        "position": 12,
        "kalends": 1,
        "nones": 5,
        "ides": 13
    }
]

# Month definitions for Julian calendar
# In the Julian calendar, the year started with January (Ianuarius)
ROMAN_MONTHS_JULIAN = [
    {
        "name": "Ianuarius", 
        "english": "January", 
        "days": 31, 
        "position": 1,
        "kalends": 1,
        "nones": 5,
        "ides": 13
    },
    {
        "name": "Februarius", 
        "english": "February", 
        "days": 28,  # 29 in leap years
        "position": 2,
        "kalends": 1,
        "nones": 5,
        "ides": 13
    },
    {
        "name": "Martius", 
        "english": "March", 
        "days": 31, 
        "position": 3,
        "kalends": 1,
        "nones": 7,
        "ides": 15
    },
    {
        "name": "Aprilis", 
        "english": "April", 
        "days": 30, 
        "position": 4,
        "kalends": 1,
        "nones": 5,
        "ides": 13
    },
    {
        "name": "Maius", 
        "english": "May", 
        "days": 31, 
        "position": 5,
        "kalends": 1,
        "nones": 7,
        "ides": 15
    },
    {
        "name": "Iunius", 
        "english": "June", 
        "days": 30, 
        "position": 6,
        "kalends": 1,
        "nones": 5,
        "ides": 13
    },
    {
        "name": "Quintilis", 
        "english": "July", 
        "days": 31, 
        "position": 7,
        "kalends": 1,
        "nones": 7,
        "ides": 15
    },
    {
        "name": "Sextilis", 
        "english": "August", 
        "days": 31, 
        "position": 8,
        "kalends": 1,
        "nones": 5,
        "ides": 13
    },
    {
        "name": "September", 
        "english": "September", 
        "days": 30, 
        "position": 9,
        "kalends": 1,
        "nones": 5,
        "ides": 13
    },
    {
        "name": "October", 
        "english": "October", 
        "days": 31, 
        "position": 10,
        "kalends": 1,
        "nones": 7,
        "ides": 15
    },
    {
        "name": "November", 
        "english": "November", 
        "days": 30, 
        "position": 11,
        "kalends": 1,
        "nones": 5,
        "ides": 13
    },
    {
        "name": "December", 
        "english": "December", 
        "days": 31, 
        "position": 12,
        "kalends": 1,
        "nones": 5,
        "ides": 13
    }
]

# Example special days definitions
# This would be expanded with a more complete dataset in a production system
SPECIAL_DAYS = {
    "Martius": [
        {
            "day": 1, 
            "name": "Kalendae Martiae", 
            "classification": DayClassification.FESTUS,
            "description": "New Year's Day in the ancient calendar, sacred to Mars",
            "deity": "Mars",
            "affects_senate": True,
            "senate_can_meet": False,
            "gameplay_effects": ["increased_military_support", "special_ceremony"]
        },
        {
            "day": 9, 
            "name": "Anna Perenna", 
            "classification": DayClassification.FESTUS,
            "description": "Festival to the goddess Anna Perenna",
            "deity": "Anna Perenna",
            "affects_senate": True,
            "senate_can_meet": False,
            "gameplay_effects": ["public_celebrations", "increased_plebeian_support"]
        },
        {
            "day": 15, 
            "name": "Idus Martiae", 
            "classification": DayClassification.NEFASTUS,
            "description": "The Ides of March, sacred to Jupiter",
            "deity": "Jupiter",
            "affects_senate": False,
            "senate_can_meet": True,
            "gameplay_effects": ["political_tension", "assassination_risk"]
        },
        {
            "day": 17, 
            "name": "Liberalia", 
            "classification": DayClassification.FESTUS,
            "description": "Festival to Liber Pater",
            "deity": "Liber",
            "affects_senate": True,
            "senate_can_meet": False,
            "gameplay_effects": ["coming_of_age_ceremonies", "wine_consumption"]
        }
    ],
    "Aprilis": [
        {
            "day": 1,
            "name": "Kalendae Aprilis",
            "classification": DayClassification.NEFASTUS,
            "description": "Kalends of April, Veneralia festival honoring Venus",
            "deity": "Venus",
            "affects_senate": True,
            "senate_can_meet": False,
            "gameplay_effects": ["increased_female_influence", "romantic_intrigues"]
        },
        {
            "day": 15, 
            "name": "Fordicidia", 
            "classification": DayClassification.FESTUS,
            "description": "Sacrifice of pregnant cows to Earth goddess",
            "deity": "Tellus",
            "affects_senate": True,
            "senate_can_meet": False,
            "gameplay_effects": ["agricultural_focus", "fertility_rites"]
        }
    ],
    "Ianuarius": [
        {
            "day": 1,
            "name": "Kalendae Ianuariae",
            "classification": DayClassification.FESTUS,
            "description": "New Year in Julian calendar, sacred to Janus",
            "deity": "Janus",
            "affects_senate": True,
            "senate_can_meet": False,
            "gameplay_effects": ["oath_renewals", "new_year_celebrations"]
        },
        {
            "day": 9,
            "name": "Agonalia",
            "classification": DayClassification.FESTUS,
            "description": "Festival dedicated to Janus",
            "deity": "Janus",
            "affects_senate": True,
            "senate_can_meet": False,
            "gameplay_effects": ["religious_observance"]
        }
    ]
}

# Define days when Senate meetings are allowed
SENATE_MEETING_RULES = {
    "allowed_classifications": [
        DayClassification.FASTUS, 
        DayClassification.COMITIALIS
    ],
    "forbidden_days": [
        # Specific day/month combinations when Senate cannot meet
        {"month": "Martius", "day": 1},    # Kalendae of March
        {"month": "Ianuarius", "day": 1},  # Kalendae of January
        {"month": "Aprilis", "day": 15},   # Fordicidia
    ],
    "exceptions": [
        # Exceptions when Senate can meet despite normal rules
        {"month": "Martius", "day": 15},   # Ides of March (historical precedent)
    ]
}


class SpecialDay:
    """
    Represents a special day in the Roman calendar.
    """
    def __init__(self, day, name, classification, description, deity=None, 
                 affects_senate=False, senate_can_meet=True, gameplay_effects=None):
        self.day = day                      # Day of the month (1-31)
        self.name = name                    # Name of the special day
        self.classification = classification  # DayClassification enum
        self.description = description      # Description of the day
        self.deity = deity                  # Associated deity (if any)
        self.affects_senate = affects_senate  # Whether it affects Senate meetings
        self.senate_can_meet = senate_can_meet  # Whether Senate can meet on this day
        self.gameplay_effects = gameplay_effects or []  # List of gameplay effects


class Month:
    """
    Represents a month in the Roman calendar.
    """
    def __init__(self, name, english, days, position, kalends, nones, ides):
        self.name = name                # Latin name (e.g., "Martius")
        self.english = english          # English name (e.g., "March")
        self.days = days                # Number of days in the month
        self.position = position        # Position in the year (1-12)
        self.kalends = kalends          # Day of Kalends (always 1)
        self.nones = nones              # Day of Nones (5th or 7th)
        self.ides = ides                # Day of Ides (13th or 15th)
        self.special_days = []          # List of SpecialDay objects
    
    def get_special_day(self, day):
        """Return special day for the given day number, or None if not special."""
        for special_day in self.special_days:
            if special_day.day == day:
                return special_day
        return None
    
    def day_classification(self, day):
        """Return the classification for the given day."""
        special_day = self.get_special_day(day)
        if special_day:
            return special_day.classification
        # Default classification if no special day is defined
        return DayClassification.FASTUS


class RomanDate:
    """
    Represents a date in the Roman calendar.
    """
    def __init__(self, year, month, day, calendar_type=CalendarType.PRE_JULIAN, consuls=None):
        self.year = year              # Numeric year (negative for BCE)
        self.month = month            # Month object
        self.day = day                # Day of month (1-31)
        self.calendar_type = calendar_type  # CalendarType enum
        self.consuls = consuls or []  # List of consul names for the year
    
    def format(self, format_type=DateFormat.MODERN):
        """Format the date according to the specified format type."""
        if format_type == DateFormat.MODERN:
            return self._format_modern()
        elif format_type == DateFormat.ROMAN_FULL:
            return self._format_roman_full()
        elif format_type == DateFormat.ROMAN_ABBREVIATED:
            return self._format_roman_abbreviated()
        elif format_type == DateFormat.CONSULAR:
            return self._format_consular()
        else:
            raise ValueError(f"Unknown format type: {format_type}")
    
    def _format_modern(self):
        """Format date in modern style: '15 March 100 BCE'"""
        era = "BCE" if self.year < 0 else "CE"
        return f"{self.day} {self.month.english} {abs(self.year)} {era}"
    
    def _format_roman_full(self):
        """Format date in full Roman style."""
        # Special cases for Kalends, Nones, and Ides
        if self.day == 1:
            return f"Kalendae {self.month.name}"
        elif self.day == self.month.nones:
            return f"Nonae {self.month.name}"
        elif self.day == self.month.ides:
            return f"Idus {self.month.name}"
        
        # For days before Nones
        if self.day < self.month.nones:
            count = self.month.nones - self.day + 1
            return f"ante diem {self._roman_numeral(count)} Nonas {self.month.name}"
        
        # For days before Ides
        if self.day < self.month.ides:
            count = self.month.ides - self.day + 1
            return f"ante diem {self._roman_numeral(count)} Idus {self.month.name}"
        
        # For days before Kalends of next month
        # Get the next month data
        months_data = ROMAN_MONTHS_PRE_JULIAN if self.calendar_type == CalendarType.PRE_JULIAN else ROMAN_MONTHS_JULIAN
        next_month_pos = self.month.position % len(months_data) + 1
        next_month_data = next((m for m in months_data if m["position"] == next_month_pos), None)
        
        if not next_month_data:
            return f"Invalid date - no next month found"
        
        next_month_name = next_month_data["name"]
        
        # Calculate days until Kalends of next month
        days_in_month = self.month.days
        count = days_in_month - self.day + 2  # +2 because Romans counted inclusively
        
        return f"ante diem {self._roman_numeral(count)} Kalendas {next_month_name}"
    
    def _format_roman_abbreviated(self):
        """Format date in abbreviated Roman style."""
        # Get the full format first
        full = self._format_roman_full()
        
        # Replace keywords with abbreviations
        abbreviations = {
            "ante diem": "a.d.",
            "Kalendae": "Kal.",
            "Nonas": "Non.",
            "Idus": "Id.",
            "Kalendas": "Kal."
        }
        
        for full_text, abbr in abbreviations.items():
            full = full.replace(full_text, abbr)
        
        # Abbreviate month names (take first 3 letters)
        months_data = ROMAN_MONTHS_PRE_JULIAN + ROMAN_MONTHS_JULIAN
        for month_data in months_data:
            month_name = month_data["name"]
            if month_name in full:
                full = full.replace(month_name, month_name[:3] + ".")
        
        return full
    
    def _format_consular(self):
        """Format date using the consulship year."""
        if not self.consuls or len(self.consuls) == 0:
            return f"In an unknown consulship, {abs(self.year)} BCE" if self.year < 0 else f"In an unknown consulship, {self.year} CE"
        
        if len(self.consuls) == 1:
            return f"In the consulship of {self.consuls[0]}, {abs(self.year)} BCE" if self.year < 0 else f"In the consulship of {self.consuls[0]}, {self.year} CE"
        
        return f"In the consulship of {self.consuls[0]} and {self.consuls[1]}, {abs(self.year)} BCE" if self.year < 0 else f"In the consulship of {self.consuls[0]} and {self.consuls[1]}, {self.year} CE"
    
    def _roman_numeral(self, num):
        """Convert an integer to a Roman numeral string."""
        # Implementation of converting numbers to Roman numerals
        val = [
            1000, 900, 500, 400,
            100, 90, 50, 40,
            10, 9, 5, 4,
            1
        ]
        syms = [
            "M", "CM", "D", "CD",
            "C", "XC", "L", "XL",
            "X", "IX", "V", "IV",
            "I"
        ]
        roman_num = ''
        i = 0
        while num > 0:
            for _ in range(num // val[i]):
                roman_num += syms[i]
                num -= val[i]
            i += 1
        return roman_num


class RomanCalendar:
    """
    Main calendar system that manages dates and transitions.
    """
    def __init__(self, year, calendar_type=None):
        self.year = year
        
        # Automatically determine calendar type based on year if not specified
        if calendar_type is None:
            self.calendar_type = CalendarType.JULIAN if year >= -45 else CalendarType.PRE_JULIAN
        else:
            self.calendar_type = calendar_type
        
        # Initialize months based on calendar type
        if self.calendar_type == CalendarType.PRE_JULIAN:
            self.months = self._initialize_months(ROMAN_MONTHS_PRE_JULIAN)
            self.current_month_idx = 0  # Martius (March) is first month in pre-Julian
        else:
            self.months = self._initialize_months(ROMAN_MONTHS_JULIAN)
            self.current_month_idx = 0  # Ianuarius (January) is first month in Julian
        
        self.current_month = self.months[self.current_month_idx]
        self.current_day = 1  # Start on the first day
        
        # Generate consuls for the year
        self.consuls = self._generate_consuls()
    
    def _initialize_months(self, month_data_list):
        """Initialize Month objects with special days."""
        months = []
        for month_data in month_data_list:
            month = Month(
                month_data["name"],
                month_data["english"],
                month_data["days"],
                month_data["position"],
                month_data["kalends"],
                month_data["nones"],
                month_data["ides"]
            )
            
            # Add special days for this month if defined
            if month.name in SPECIAL_DAYS:
                for special_day_data in SPECIAL_DAYS[month.name]:
                    special_day = SpecialDay(
                        day=special_day_data["day"],
                        name=special_day_data["name"],
                        classification=special_day_data["classification"],
                        description=special_day_data["description"],
                        deity=special_day_data.get("deity"),
                        affects_senate=special_day_data.get("affects_senate", False),
                        senate_can_meet=special_day_data.get("senate_can_meet", True),
                        gameplay_effects=special_day_data.get("gameplay_effects", [])
                    )
                    month.special_days.append(special_day)
            
            months.append(month)
        return months
    
    def _generate_consuls(self):
        """Generate consul names for the current year."""
        # This would ideally pull from a historical database
        # For now, use placeholder names based on the year
        consuls = []
        abs_year = abs(self.year)
        
        # Some known historical consuls
        if self.year == -100:
            consuls = ["Gaius Marius", "Lucius Valerius Flaccus"]
        elif self.year == -99:
            consuls = ["Marcus Antonius", "Aulus Postumius Albinus"]
        elif self.year == -63:
            consuls = ["Marcus Tullius Cicero", "Gaius Antonius Hybrida"]
        elif self.year == -59:
            consuls = ["Gaius Julius Caesar", "Marcus Calpurnius Bibulus"]
        else:
            # Generate placeholders for years without specific historical data
            praenomina = ["Gaius", "Marcus", "Lucius", "Quintus", "Publius", "Titus", "Gnaeus"]
            nomina = ["Julius", "Claudius", "Cornelius", "Valerius", "Fabius", "Calpurnius", "Aemilius"]
            cognomina = ["Maximus", "Rufus", "Felix", "Bassus", "Severus", "Flaccus", "Crassus"]
            
            # Seed the RNG with the year for consistency
            rng = random.Random(abs_year)
            
            for i in range(2):  # Two consuls
                praenomen = rng.choice(praenomina)
                nomen = rng.choice(nomina)
                cognomen = rng.choice(cognomina)
                consuls.append(f"{praenomen} {nomen} {cognomen}")
        
        return consuls
    
    def get_current_date(self):
        """Get the current date as a RomanDate object."""
        return RomanDate(
            year=self.year,
            month=self.current_month,
            day=self.current_day,
            calendar_type=self.calendar_type,
            consuls=self.consuls
        )
    
    def format_current_date(self, format_type=DateFormat.MODERN):
        """Format the current date using the specified format."""
        date = self.get_current_date()
        return date.format(format_type)
    
    def advance_day(self, days=1):
        """
        Advance the calendar by the specified number of days.
        Returns a list of special days encountered.
        """
        special_days_encountered = []
        
        for _ in range(days):
            # Check if current day is special before advancing
            special_day = self.current_month.get_special_day(self.current_day)
            if special_day:
                special_days_encountered.append(special_day)
            
            # Advance to next day
            self.current_day += 1
            
            # Check if we need to move to the next month
            if self.current_day > self.current_month.days:
                self.current_day = 1
                self.current_month_idx = (self.current_month_idx + 1) % len(self.months)
                self.current_month = self.months[self.current_month_idx]
                
                # If we've wrapped around to the first month, increment the year
                if (self.calendar_type == CalendarType.PRE_JULIAN and self.current_month.name == "Martius" and self.current_month_idx == 0) or \
                   (self.calendar_type == CalendarType.JULIAN and self.current_month.name == "Ianuarius" and self.current_month_idx == 0):
                    self.year += 1
                    
                    # Check if we need to switch calendar systems at 45 BCE
                    if self.year == -45 and self.calendar_type == CalendarType.PRE_JULIAN:
                        self.calendar_type = CalendarType.JULIAN
                        self.months = self._initialize_months(ROMAN_MONTHS_JULIAN)
                        self.current_month = self.months[0]  # Ianuarius
                    
                    # Update consuls for the new year
                    self.consuls = self._generate_consuls()
        
        return special_days_encountered
    
    def can_hold_senate_session(self):
        """
        Check if the Senate can meet on the current day.
        Returns (bool, reason) tuple.
        """
        # Check if it's a special day that affects the Senate
        special_day = self.current_month.get_special_day(self.current_day)
        if special_day and special_day.affects_senate:
            if not special_day.senate_can_meet:
                return False, f"The Senate cannot meet during {special_day.name} ({special_day.description})"
        
        # Check day classification
        day_class = self.current_month.day_classification(self.current_day)
        if day_class not in SENATE_MEETING_RULES["allowed_classifications"]:
            return False, f"The Senate cannot meet on a dies {day_class.name.lower()} day"
        
        # Check specific forbidden days
        for forbidden in SENATE_MEETING_RULES["forbidden_days"]:
            if forbidden["month"] == self.current_month.name and forbidden["day"] == self.current_day:
                return False, f"The Senate traditionally does not meet on this day"
        
        # Check exceptions
        for exception in SENATE_MEETING_RULES["exceptions"]:
            if exception["month"] == self.current_month.name and exception["day"] == self.current_day:
                return True, "The Senate can meet due to exceptional circumstances"
        
        return True, "The Senate can meet on this day"
    
    def get_next_senate_day(self):
        """
        Find the next day when the Senate can meet.
        Returns a RomanDate object.
        """
        # Create a copy of the current calendar state
        temp_calendar = RomanCalendar(self.year, self.calendar_type)
        temp_calendar.current_month_idx = self.current_month_idx
        temp_calendar.current_month = self.months[self.current_month_idx]
        temp_calendar.current_day = self.current_day
        temp_calendar.consuls = self.consuls.copy()
        
        # Advance days until we find a valid Senate day
        max_days_to_check = 30  # Prevent infinite loop
        for i in range(1, max_days_to_check + 1):
            temp_calendar.advance_day()
            can_meet, _ = temp_calendar.can_hold_senate_session()
            if can_meet:
                return temp_calendar.get_current_date()
        
        # If we couldn't find a day within the limit, return None
        return None
    
    def get_special_events_for_current_day(self):
        """Get special events for the current day."""
        special_day = self.current_month.get_special_day(self.current_day)
        if not special_day:
            return []
        
        return [
            {
                "name": special_day.name,
                "description": special_day.description,
                "deity": special_day.deity,
                "effects": special_day.gameplay_effects
            }
        ]
    
    def is_leap_year(self):
        """
        Check if the current year is a leap year.
        In the Julian calendar, leap years occur every 4 years.
        The pre-Julian calendar had intercalary months, but not regular leap days.
        """
        # Only Julian calendar has leap years
        if self.calendar_type != CalendarType.JULIAN:
            return False
        
        # Julian leap year rule (every 4 years)
        # Note: The historical implementation of leap years in early Julian calendar was erratic
        # For simplicity, we use the standard every 4 years rule
        return self.year % 4 == 0