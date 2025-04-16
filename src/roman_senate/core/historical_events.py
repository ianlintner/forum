#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Roman Senate Game
Historical Events Database

This module provides a database of historical events from Roman history
to be used by the StoryCrierAgent and other components that need
historical context.
"""

from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Optional, Union, Tuple, Any
import random
from datetime import datetime
import calendar

class EventCategory(Enum):
    """Categories of historical events."""
    POLITICAL = "political"           # Political events, elections, reforms
    MILITARY = "military"             # Battles, wars, military campaigns
    RELIGIOUS = "religious"           # Religious ceremonies, omens, festivals
    CULTURAL = "cultural"             # Cultural developments, games, plays
    ECONOMIC = "economic"             # Economic issues, trade, grain supplies
    SOCIAL = "social"                 # Social events, daily life
    LEGAL = "legal"                   # Legal developments, trials
    NATURAL = "natural"               # Natural events, disasters
    CONSTRUCTION = "construction"     # Building projects, infrastructure

class EventImportance(Enum):
    """Importance level of events."""
    MAJOR = 3       # Major historical event (battle of Actium, Caesar's assassination)
    MODERATE = 2    # Moderately significant event (consul election, important law)
    MINOR = 1       # Minor event (local issue, small celebration)
    BACKGROUND = 0  # Background detail, everyday occurrence
    
@dataclass
class HistoricalEvent:
    """
    Represents a historical event in Roman history.
    """
    id: int                      # Unique identifier
    title: str                   # Short title of the event
    description: str             # Full description
    year: int                    # Year (negative for BCE)
    month: Optional[int] = None  # Month (1-12, if known)
    day: Optional[int] = None    # Day (1-31, if known)
    categories: List[EventCategory] = None  # Categories this event falls under
    importance: EventImportance = EventImportance.MODERATE  # Importance level
    location: Optional[str] = None         # Where it happened
    people_involved: List[str] = None      # Key historical figures
    source: Optional[str] = None           # Historical source
    narrative_hooks: List[str] = None      # Ideas for narrative integration
    
    def __post_init__(self):
        """Initialize list fields that were passed as None."""
        if self.categories is None:
            self.categories = []
        if self.people_involved is None:
            self.people_involved = []
        if self.narrative_hooks is None:
            self.narrative_hooks = []
    
    def has_exact_date(self) -> bool:
        """Check if the event has a complete date (year, month, day)."""
        return self.year is not None and self.month is not None and self.day is not None
    
    def has_month(self) -> bool:
        """Check if the event has at least a month and year."""
        return self.year is not None and self.month is not None
    
    def format_date(self) -> str:
        """Format the event date as a string."""
        era = "BCE" if self.year < 0 else "CE"
        year_str = f"{abs(self.year)} {era}"
        
        if self.month is not None and self.day is not None:
            month_name = calendar.month_name[self.month]
            return f"{month_name} {self.day}, {year_str}"
        elif self.month is not None:
            month_name = calendar.month_name[self.month]
            return f"{month_name}, {year_str}"
        else:
            return year_str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the event to a dictionary for serialization."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "year": self.year,
            "month": self.month,
            "day": self.day,
            "categories": [cat.value for cat in self.categories],
            "importance": self.importance.value,
            "location": self.location,
            "people_involved": self.people_involved,
            "source": self.source,
            "narrative_hooks": self.narrative_hooks
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HistoricalEvent':
        """Create an event from a dictionary."""
        # Convert string categories back to enum values
        categories = []
        if "categories" in data:
            categories = [EventCategory(cat) for cat in data["categories"]]
        
        # Convert importance back to enum
        importance = EventImportance.MODERATE
        if "importance" in data:
            importance = EventImportance(data["importance"])
        
        return cls(
            id=data["id"],
            title=data["title"],
            description=data["description"],
            year=data["year"],
            month=data.get("month"),
            day=data.get("day"),
            categories=categories,
            importance=importance,
            location=data.get("location"),
            people_involved=data.get("people_involved", []),
            source=data.get("source"),
            narrative_hooks=data.get("narrative_hooks", [])
        )


class HistoricalEventsDatabase:
    """
    Database for historical events with query capabilities.
    """
    def __init__(self):
        """Initialize the events database with sample events."""
        self.events: List[HistoricalEvent] = []
        self._initialize_events()
    
    def _initialize_events(self):
        """Populate the database with historical events."""
        # Major historical events
        self.events = [
            # Major political events
            HistoricalEvent(
                id=1,
                title="Assassination of Julius Caesar",
                description="Julius Caesar was assassinated in the Senate House by a group of senators led by Marcus Junius Brutus and Gaius Cassius Longinus, who feared his growing power and monarchical tendencies.",
                year=-44,
                month=3,
                day=15,
                categories=[EventCategory.POLITICAL],
                importance=EventImportance.MAJOR,
                location="Senate House (Curia of Pompey), Rome",
                people_involved=["Julius Caesar", "Marcus Junius Brutus", "Gaius Cassius Longinus"],
                source="Plutarch's Lives, Suetonius' The Twelve Caesars",
                narrative_hooks=["Political tensions", "Fear of tyranny", "References to omens and warnings"]
            ),
            HistoricalEvent(
                id=2,
                title="First Triumvirate Formed",
                description="An informal political alliance formed between Julius Caesar, Pompey the Great, and Marcus Licinius Crassus, three prominent leaders who dominated Roman politics.",
                year=-60,
                categories=[EventCategory.POLITICAL],
                importance=EventImportance.MAJOR,
                location="Rome",
                people_involved=["Julius Caesar", "Pompey the Great", "Marcus Licinius Crassus"],
                narrative_hooks=["Political alliances", "Distribution of power", "Secret agreements"]
            ),
            # Major military events
            HistoricalEvent(
                id=3,
                title="Battle of Actium",
                description="Naval battle between Octavian's forces and those of Mark Antony and Cleopatra, resulting in victory for Octavian and paving the way for his establishment of the Roman Empire.",
                year=-31,
                month=9,
                day=2,
                categories=[EventCategory.MILITARY],
                importance=EventImportance.MAJOR,
                location="Gulf of Actium, Greece",
                people_involved=["Octavian (Augustus)", "Mark Antony", "Cleopatra VII"],
                narrative_hooks=["Naval strategies", "References to Egyptian influence", "Changing fate of Rome"]
            ),
            HistoricalEvent(
                id=4,
                title="Crossing of the Rubicon",
                description="Julius Caesar crossed the Rubicon River with his army, violating Roman law and effectively declaring civil war against Pompey and the Senate.",
                year=-49,
                month=1,
                day=10,
                categories=[EventCategory.MILITARY, EventCategory.POLITICAL],
                importance=EventImportance.MAJOR,
                location="Rubicon River, Northern Italy",
                people_involved=["Julius Caesar"],
                source="Suetonius, Plutarch",
                narrative_hooks=["Point of no return", "Defiance of the Senate", "Civil war"]
            ),
            
            # Moderate events - Political
            HistoricalEvent(
                id=5,
                title="Lex Gabinia Passed",
                description="Law granting Pompey extraordinary command to deal with the Mediterranean pirate threat, greatly expanding his power and setting a precedent for future commanders.",
                year=-67,
                categories=[EventCategory.POLITICAL, EventCategory.LEGAL],
                importance=EventImportance.MODERATE,
                location="Rome",
                people_involved=["Pompey the Great", "Aulus Gabinius"],
                narrative_hooks=["Debates about military command", "Expanding powers", "Pirate threats"]
            ),
            HistoricalEvent(
                id=6,
                title="Cicero Exposes Catiline Conspiracy",
                description="Consul Marcus Tullius Cicero exposed Lucius Sergius Catilina's conspiracy to overthrow the Roman Republic.",
                year=-63,
                month=11,
                categories=[EventCategory.POLITICAL],
                importance=EventImportance.MODERATE,
                location="Senate House, Rome",
                people_involved=["Marcus Tullius Cicero", "Lucius Sergius Catilina"],
                source="Cicero's Catiline Orations",
                narrative_hooks=["Political conspiracies", "Surveillance", "Threats to the Republic"]
            ),
            
            # Religious/Cultural events
            HistoricalEvent(
                id=7,
                title="Dedication of Temple of Jupiter Optimus Maximus",
                description="The main temple on the Capitoline Hill was re-dedicated after being destroyed in a fire, marking an important religious moment for Rome.",
                year=-69,
                categories=[EventCategory.RELIGIOUS, EventCategory.CULTURAL],
                importance=EventImportance.MODERATE,
                location="Capitoline Hill, Rome",
                people_involved=["Quintus Lutatius Catulus"],
                narrative_hooks=["Religious ceremonies", "Public celebrations", "Divine omens"]
            ),
            HistoricalEvent(
                id=8,
                title="Secular Games Celebration",
                description="Augustus revived the ancient Secular Games (Ludi Saeculares), a religious celebration held once every century, symbolizing the beginning of a new era under his rule.",
                year=-17,
                month=6,
                categories=[EventCategory.RELIGIOUS, EventCategory.CULTURAL],
                importance=EventImportance.MODERATE,
                location="Rome",
                people_involved=["Augustus"],
                narrative_hooks=["Ceremonial traditions", "Public spectacles", "Political symbolism"]
            ),
            
            # Economic/Social events
            HistoricalEvent(
                id=9,
                title="Grain Shortage Crisis",
                description="Severe grain shortage in Rome led to public unrest and forced political action to secure food supplies from the provinces.",
                year=-75,
                categories=[EventCategory.ECONOMIC, EventCategory.SOCIAL],
                importance=EventImportance.MODERATE,
                location="Rome",
                narrative_hooks=["Food security debates", "Public unrest", "Trade regulations"]
            ),
            HistoricalEvent(
                id=10,
                title="Lex Claudia Restricts Senatorial Trade",
                description="Law preventing senators from owning large ships, limiting their involvement in maritime trade and commercial activities.",
                year=-218,
                categories=[EventCategory.ECONOMIC, EventCategory.LEGAL, EventCategory.POLITICAL],
                importance=EventImportance.MODERATE,
                narrative_hooks=["Conflict of interest", "Class distinctions", "Commerce regulations"]
            ),
            
            # Minor events
            HistoricalEvent(
                id=11,
                title="Flood of the Tiber",
                description="The Tiber River flooded parts of Rome, causing damage to buildings and disrupting daily life in the city.",
                year=-54,
                month=11,
                categories=[EventCategory.NATURAL],
                importance=EventImportance.MINOR,
                location="Rome",
                narrative_hooks=["Natural disasters", "Public works", "Religious interpretations"]
            ),
            HistoricalEvent(
                id=12,
                title="Famous Gladiatorial Games of Crassus",
                description="Marcus Licinius Crassus sponsored elaborate gladiatorial games to gain public favor, featuring over 100 pairs of fighters.",
                year=-70,
                categories=[EventCategory.CULTURAL, EventCategory.SOCIAL],
                importance=EventImportance.MINOR,
                location="Roman Forum",
                people_involved=["Marcus Licinius Crassus"],
                narrative_hooks=["Public entertainment", "Political popularity", "Social gatherings"]
            ),
            HistoricalEvent(
                id=13,
                title="Cicero Purchases Grand Villa",
                description="Marcus Tullius Cicero purchased an expensive villa in Tusculum, causing some controversy due to questions about how he afforded it.",
                year=-68,
                categories=[EventCategory.SOCIAL],
                importance=EventImportance.MINOR,
                location="Tusculum",
                people_involved=["Marcus Tullius Cicero"],
                narrative_hooks=["Luxury debates", "Wealth display", "Political accusations"]
            ),
            
            # Background daily life events
            HistoricalEvent(
                id=14,
                title="Disruption of Market Day",
                description="A brawl between merchants disrupted the weekly market day in the Forum, requiring intervention by the urban cohorts.",
                year=-65,
                month=5,
                day=15,
                categories=[EventCategory.SOCIAL, EventCategory.ECONOMIC],
                importance=EventImportance.BACKGROUND,
                location="Roman Forum",
                narrative_hooks=["Daily commerce", "Urban security", "Market regulations"]
            ),
            HistoricalEvent(
                id=15,
                title="Praetor's Household Scandal",
                description="A minor scandal involving a praetor's household slave caught stealing from visitors became popular gossip in Rome.",
                year=-67,
                month=9,
                categories=[EventCategory.SOCIAL],
                importance=EventImportance.BACKGROUND,
                location="Rome",
                narrative_hooks=["Household management", "Slavery issues", "Social reputation"]
            ),
            HistoricalEvent(
                id=16,
                title="Popular Actor Performs New Comedy",
                description="The famous actor Roscius premiered a new comedy at the Theater of Pompey, drawing large crowds from all social classes.",
                year=-55,
                month=4,
                categories=[EventCategory.CULTURAL],
                importance=EventImportance.BACKGROUND,
                location="Theater of Pompey, Rome",
                people_involved=["Quintus Roscius Gallus"],
                narrative_hooks=["Entertainment culture", "Social mixing", "Popular arts"]
            ),
            
            # Events from different periods
            HistoricalEvent(
                id=17,
                title="Punic Peace Treaty Signed",
                description="Following the First Punic War, Rome and Carthage signed a peace treaty, with Carthage agreeing to evacuate Sicily and pay a war indemnity.",
                year=-241,
                categories=[EventCategory.POLITICAL, EventCategory.MILITARY],
                importance=EventImportance.MAJOR,
                location="Sicily",
                narrative_hooks=["International relations", "War consequences", "Mediterranean power"]
            ),
            HistoricalEvent(
                id=18,
                title="Sulla Marches on Rome",
                description="Lucius Cornelius Sulla became the first Roman general to march his legions into Rome itself, violating ancient tradition and setting a dangerous precedent.",
                year=-88,
                categories=[EventCategory.MILITARY, EventCategory.POLITICAL],
                importance=EventImportance.MAJOR,
                location="Rome",
                people_involved=["Lucius Cornelius Sulla"],
                narrative_hooks=["Military authority", "Constitutional crisis", "Civil conflict"]
            ),
            HistoricalEvent(
                id=19,
                title="Social War Begins",
                description="Italian allies (socii) rebelled against Rome, demanding citizenship rights and equal treatment, beginning the Social War.",
                year=-91,
                categories=[EventCategory.MILITARY, EventCategory.POLITICAL],
                importance=EventImportance.MAJOR,
                location="Italy",
                narrative_hooks=["Citizenship debates", "Italian relations", "Roman identity"]
            ),
            HistoricalEvent(
                id=20,
                title="Founding of Colonia Narbo Martius",
                description="Rome established its first colony in Gaul, creating an important trading center and military base.",
                year=-118,
                categories=[EventCategory.POLITICAL, EventCategory.ECONOMIC],
                importance=EventImportance.MODERATE,
                location="Narbo (modern Narbonne, France)",
                narrative_hooks=["Colonial expansion", "Trade networks", "Cultural interactions"]
            ),
            
            # Construction/Infrastructure
            HistoricalEvent(
                id=21,
                title="Completion of Aqua Marcia",
                description="Rome's longest aqueduct, the Aqua Marcia, was completed, significantly improving the city's water supply.",
                year=-144,
                categories=[EventCategory.CONSTRUCTION],
                importance=EventImportance.MODERATE,
                location="Rome",
                people_involved=["Quintus Marcius Rex"],
                narrative_hooks=["Infrastructure debates", "Public health", "Engineering marvels"]
            ),
            HistoricalEvent(
                id=22,
                title="Via Aemilia Completed",
                description="Construction of the Via Aemilia finished, connecting Ariminum to Placentia and improving transportation in northern Italy.",
                year=-187,
                categories=[EventCategory.CONSTRUCTION],
                importance=EventImportance.MODERATE,
                location="Northern Italy",
                people_involved=["Marcus Aemilius Lepidus"],
                narrative_hooks=["Road networks", "Military movement", "Trade facilitation"]
            ),
            
            # Legal developments
            HistoricalEvent(
                id=23,
                title="Trial of Verres",
                description="Cicero successfully prosecuted Gaius Verres for corruption during his governorship of Sicily, enhancing his reputation as an orator.",
                year=-70,
                month=8,
                categories=[EventCategory.LEGAL, EventCategory.POLITICAL],
                importance=EventImportance.MODERATE,
                location="Rome",
                people_involved=["Marcus Tullius Cicero", "Gaius Verres"],
                source="Cicero's Verrine Orations",
                narrative_hooks=["Provincial administration", "Corruption", "Legal oratory"]
            ),
            HistoricalEvent(
                id=24,
                title="Passage of Leges Liciniae Sextiae",
                description="Landmark laws that allowed plebeians to become consuls and regulated land ownership, reducing patrician dominance.",
                year=-367,
                categories=[EventCategory.LEGAL, EventCategory.POLITICAL, EventCategory.SOCIAL],
                importance=EventImportance.MAJOR,
                location="Rome",
                people_involved=["Gaius Licinius Stolo", "Lucius Sextius Lateranus"],
                narrative_hooks=["Class struggle", "Constitutional reform", "Power sharing"]
            ),
            
            # Religion and omens
            HistoricalEvent(
                id=25,
                title="Observation of Comet",
                description="A bright comet appeared in the night sky for several days, interpreted by priests as an omen related to political changes.",
                year=-87,
                month=7,
                categories=[EventCategory.RELIGIOUS, EventCategory.NATURAL],
                importance=EventImportance.MINOR,
                location="Rome",
                narrative_hooks=["Divine signs", "Astronomical phenomena", "Religious interpretations"]
            ),
            HistoricalEvent(
                id=26,
                title="Slave Uprising in Sicily",
                description="Beginning of a major slave revolt in Sicily led by Eunus, a Syrian slave who claimed prophetic powers.",
                year=-135,
                categories=[EventCategory.SOCIAL, EventCategory.MILITARY],
                importance=EventImportance.MODERATE,
                location="Sicily",
                people_involved=["Eunus"],
                narrative_hooks=["Slavery issues", "Provincial security", "Social unrest"]
            ),
            HistoricalEvent(
                id=27,
                title="Tiberius Gracchus Elected Tribune",
                description="Tiberius Gracchus was elected tribune of the plebs, beginning a period of reformist politics that would eventually lead to his assassination.",
                year=-133,
                categories=[EventCategory.POLITICAL],
                importance=EventImportance.MAJOR,
                location="Rome",
                people_involved=["Tiberius Gracchus"],
                narrative_hooks=["Land reform", "Popular politics", "Legislative activism"]
            ),
            HistoricalEvent(
                id=28,
                title="Mithridates Orders Massacre of Romans",
                description="King Mithridates VI of Pontus ordered the killing of all Roman and Italian citizens in Asia Minor, resulting in up to 80,000 deaths.",
                year=-88,
                categories=[EventCategory.MILITARY, EventCategory.POLITICAL],
                importance=EventImportance.MAJOR,
                location="Asia Minor",
                people_involved=["Mithridates VI"],
                narrative_hooks=["Foreign relations", "Eastern threats", "Diplomatic crisis"]
            ),
            HistoricalEvent(
                id=29,
                title="Caesar's Election as Pontifex Maximus",
                description="Julius Caesar was elected to the powerful religious position of Pontifex Maximus, despite being relatively young for the role.",
                year=-63,
                categories=[EventCategory.RELIGIOUS, EventCategory.POLITICAL],
                importance=EventImportance.MODERATE,
                location="Rome",
                people_involved=["Julius Caesar"],
                narrative_hooks=["Religious politics", "Career ambitions", "Populist tactics"]
            ),
            HistoricalEvent(
                id=30,
                title="Death of Clodius in Street Violence",
                description="Publius Clodius Pulcher, a populist politician, was killed in a violent clash with the gang of his rival Titus Annius Milo, leading to riots in Rome.",
                year=-52,
                month=1,
                day=18,
                categories=[EventCategory.POLITICAL, EventCategory.SOCIAL],
                importance=EventImportance.MODERATE,
                location="Via Appia, near Bovillae",
                people_involved=["Publius Clodius Pulcher", "Titus Annius Milo", "Marcus Tullius Cicero"],
                narrative_hooks=["Political violence", "Urban gangs", "Public order"]
            )
        ]
    
    def add_event(self, event: HistoricalEvent) -> None:
        """Add a new event to the database."""
        self.events.append(event)
    
    def get_event_by_id(self, event_id: int) -> Optional[HistoricalEvent]:
        """Get an event by its ID."""
        for event in self.events:
            if event.id == event_id:
                return event
        return None
    
    def get_events_by_date(self, year: int, month: Optional[int] = None, 
                          day: Optional[int] = None) -> List[HistoricalEvent]:
        """
        Get events for a specific date.
        
        Args:
            year: The year (negative for BCE)
            month: The month (1-12)
            day: The day (1-31)
            
        Returns:
            List of events matching the date criteria
        """
        results = []
        
        for event in self.events:
            # Match year
            if event.year != year:
                continue
                
            # If month is specified
            if month is not None:
                if event.month is None or event.month != month:
                    continue
                    
                # If day is specified
                if day is not None:
                    if event.day is None or event.day != day:
                        continue
            
            results.append(event)
            
        return results
    
    def get_events_by_year_range(self, start_year: int, end_year: int) -> List[HistoricalEvent]:
        """Get events within a range of years."""
        return [event for event in self.events 
                if start_year <= event.year <= end_year]
    
    def get_events_by_category(self, category: EventCategory) -> List[HistoricalEvent]:
        """Get events of a specific category."""
        return [event for event in self.events 
                if category in event.categories]
    
    def get_events_by_importance(self, importance: EventImportance) -> List[HistoricalEvent]:
        """Get events of a specific importance level."""
        return [event for event in self.events 
                if event.importance == importance]
    
    def filter_events(self, 
                     year_range: Optional[Tuple[int, int]] = None,
                     categories: Optional[List[EventCategory]] = None,
                     importance: Optional[EventImportance] = None,
                     people: Optional[List[str]] = None,
                     location: Optional[str] = None) -> List[HistoricalEvent]:
        """
        Filter events based on multiple criteria.
        
        Args:
            year_range: Optional tuple of (start_year, end_year)
            categories: Optional list of categories to include
            importance: Optional minimum importance level
            people: Optional list of people who must be involved
            location: Optional location to filter by
            
        Returns:
            List of events matching all specified criteria
        """
        results = self.events.copy()
        
        # Filter by year range
        if year_range:
            start_year, end_year = year_range
            results = [event for event in results 
                      if start_year <= event.year <= end_year]
        
        # Filter by categories
        if categories:
            filtered = []
            for event in results:
                if any(category in event.categories for category in categories):
                    filtered.append(event)
            results = filtered
        
        # Filter by importance
        if importance:
            results = [event for event in results 
                      if event.importance.value >= importance.value]
        
        # Filter by people involved
        if people:
            filtered = []
            for event in results:
                if any(person in event.people_involved for person in people):
                    filtered.append(event)
            results = filtered
        
        # Filter by location
        if location:
            results = [event for event in results 
                      if event.location and location.lower() in event.location.lower()]
        
        return results
    
    def get_random_event(self, 
                        year_range: Optional[Tuple[int, int]] = None,
                        categories: Optional[List[EventCategory]] = None,
                        min_importance: Optional[EventImportance] = None) -> Optional[HistoricalEvent]:
        """
        Get a random event, optionally filtered by criteria.
        
        Args:
            year_range: Optional tuple of (start_year, end_year)
            categories: Optional list of categories to include
            min_importance: Optional minimum importance level
            
        Returns:
            A random event matching the criteria, or None if no events match
        """
        filtered_events = self.filter_events(
            year_range=year_range,
            categories=categories,
            importance=min_importance
        )
        
        if not filtered_events:
            return None
            
        return random.choice(filtered_events)
    
    def get_relevant_events(self, current_year: int, 
                          timeframe: int = 10, 
                          count: int = 3,
                          categories: Optional[List[EventCategory]] = None) -> List[HistoricalEvent]:
        """
        Get historically relevant events that a StoryCrier might announce.
        
        Args:
            current_year: The current year in the simulation
            timeframe: How many years to look back for recent events and anniversaries
            count: Maximum number of events to return
            categories: Optional categories to filter by
            
        Returns:
            List of relevant historical events
        """
        relevant_events = []
        
        # Recent events (within the timeframe)
        start_year = current_year - timeframe
        recent_events = self.filter_events(
            year_range=(start_year, current_year),
            categories=categories
        )
        
        # Historical anniversaries (multiples of 5, 10, 25, 50, 100 years)
        anniversaries = []
        for years_ago in [5, 10, 25, 50, 100, 200, 500]:
            anniversary_year = current_year - years_ago
            anniversary_events = self.get_events_by_year_range(
                anniversary_year, anniversary_year
            )
            
            for event in anniversary_events:
                if categories is None or any(category in event.categories for category in categories):
                    event_copy = HistoricalEvent(
                        id=event.id,
                        title=f"{years_ago}-Year Anniversary: {event.title}",
                        description=event.description,
                        year=event.year,
                        month=event.month,
                        day=event.day,
                        categories=event.categories,
                        importance=event.importance,
                        location=event.location,
                        people_involved=event.people_involved,
                        source=event.source,
                        narrative_hooks=event.narrative_hooks
                    )
                    anniversaries.append(event_copy)
        
        # Combine recent events and anniversaries
        all_events = recent_events + anniversaries
        
        # Sort by importance, then by year (most recent first)
        all_events.sort(key=lambda e: (
            -e.importance.value,  # Higher importance first
            -(current_year - e.year)  # More recent first
        ))
        
        # Return the top events according to the count
        return all_events[:count]
    
    def get_events_for_crier(self, 
                           current_year: int,
                           current_month: Optional[int] = None,
                           current_day: Optional[int] = None,
                           count: int = 3) -> List[Dict[str, str]]:
        """
        Get events formatted specifically for the StoryCrierAgent to announce.
        
        Args:
            current_year: Current year in simulation
            current_month: Current month in simulation
            current_day: Current day in simulation
            count: Number of announcements to generate
            
        Returns:
            List of formatted announcement dictionaries
        """
        announcements = []
        
        # Try to get events for the specific date if month and day are provided
        date_specific_events = []
        if current_month is not None and current_day is not None:
            for year in range(-1000, current_year):  # Check historical events
                events = self.get_events_by_date(year, current_month, current_day)
                date_specific_events.extend(events)
        
        # Get recent and anniversary events
        relevant_events = self.get_relevant_events(current_year, count=10)
        
        # Combine date-specific and relevant events, prioritizing date_specific
        all_events = date_specific_events + relevant_events
        
        # Deduplicate by ID
        seen_ids = set()
        unique_events = []
        for event in all_events:
            if event.id not in seen_ids:
                seen_ids.add(event.id)
                unique_events.append(event)
        
        # Select the events to use for announcements
        selected_events = unique_events[:count]
        
        # Format each event as an announcement
        for event in selected_events:
            years_ago = current_year - event.year
            
            # Format the announcement based on how long ago it happened
            if years_ago == 0:
                time_text = "This very year"
            elif years_ago == 1:
                time_text = "Last year"
            elif years_ago < 10:
                time_text = f"{years_ago} years ago"
            else:
                time_text = f"In the year {abs(event.year)} {'BCE' if event.year < 0 else 'CE'}"
                
            # Add month and day if available
            if event.month is not None and event.day is not None:
                date_text = f"on the {event.day}th day of {calendar.month_name[event.month]}"
                time_text = f"{time_text}, {date_text}"
            elif event.month is not None:
                time_text = f"{time_text}, in {calendar.month_name[event.month]}"
            
            # Create the complete announcement
            if "Anniversary" in event.title:
                # For anniversaries, use a special format
                announcement = {
                    "title": event.title,
                    "text": f"{time_text}, {event.description} Today marks {years_ago} years since this momentous event."
                }
            else:
                announcement = {
                    "title": event.title,
                    "text": f"{time_text}, {event.description}"
                }
                
            announcements.append(announcement)
            
        return announcements


# Create a global instance of the database
historical_events_db = HistoricalEventsDatabase()


def get_events_for_date(year: int, month: Optional[int] = None, day: Optional[int] = None) -> List[HistoricalEvent]:
    """
    Retrieve events for a specific date.
    
    Args:
        year: Year (negative for BCE)
        month: Optional month (1-12)
        day: Optional day (1-31)
        
    Returns:
        List of events on that date
    """
    return historical_events_db.get_events_by_date(year, month, day)


def get_random_relevant_event(current_year: int, categories: Optional[List[str]] = None) -> Optional[Dict[str, str]]:
    """
    Get a random relevant historical event formatted for announcement.
    
    Args:
        current_year: Current year in the simulation
        categories: Optional list of category strings to filter by
        
    Returns:
        Formatted event announcement or None
    """
    # Convert string categories to enum values if provided
    enum_categories = None
    if categories:
        enum_categories = []
        for cat_str in categories:
            try:
                enum_categories.append(EventCategory(cat_str))
            except ValueError:
                pass
    
    # Get relevant events
    events = historical_events_db.get_relevant_events(
        current_year=current_year,
        categories=enum_categories,
        count=10  # Get several to choose from
    )
    
    if not events:
        return None
        
    # Choose a random event
    event = random.choice(events)
    
    # Format it as an announcement
    years_ago = current_year - event.year
    
    # Create the announcement text
    if years_ago == 0:
        time_text = "This very year"
    elif years_ago == 1:
        time_text = "Last year"
    elif years_ago < 10:
        time_text = f"{years_ago} years ago"
    else:
        time_text = f"In the year {abs(event.year)} {'BCE' if event.year < 0 else 'CE'}"
        
    # Add month and day if available
    if event.month is not None and event.day is not None:
        date_text = f"on the {event.day}th day of {calendar.month_name[event.month]}"
        time_text = f"{time_text}, {date_text}"
    elif event.month is not None:
        time_text = f"{time_text}, in {calendar.month_name[event.month]}"
    
    # Create the complete announcement
    return {
        "title": event.title,
        "text": f"{time_text}, {event.description}"
    }


def filter_events_by_type(events: List[HistoricalEvent], 
                         event_type: str) -> List[HistoricalEvent]:
    """
    Filter events by a specific type/category.
    
    Args:
        events: List of events to filter
        event_type: Category name to filter by
        
    Returns:
        Filtered list of events
    """
    try:
        category = EventCategory(event_type)
        return [event for event in events if category in event.categories]
    except ValueError:
        # If the event_type isn't a valid category, return an empty list
        return []


def filter_events_by_importance(events: List[HistoricalEvent], 
                              importance_level: str) -> List[HistoricalEvent]:
    """
    Filter events by importance level.
    
    Args:
        events: List of events to filter
        importance_level: Importance level name (MAJOR, MODERATE, MINOR, BACKGROUND)
        
    Returns:
        Filtered list of events
    """
    try:
        importance = EventImportance[importance_level.upper()]
        return [event for event in events if event.importance == importance]
    except KeyError:
        # If the importance_level isn't a valid enum value, return an empty list
        return []


def get_announcements_for_current_date(current_year: int, 
                                      current_month: Optional[int] = None, 
                                      current_day: Optional[int] = None, 
                                      count: int = 3) -> List[Dict[str, str]]:
    """
    Get announcements for the current date in the simulation.
    
    Args:
        current_year: Current year in simulation
        current_month: Current month (1-12)
        current_day: Current day (1-31)
        count: Number of announcements to generate
        
    Returns:
        List of formatted announcement dictionaries
    """
    return historical_events_db.get_events_for_crier(
        current_year=current_year,
        current_month=current_month,
        current_day=current_day,
        count=count
    )