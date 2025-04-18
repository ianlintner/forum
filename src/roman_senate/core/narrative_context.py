"""
Roman Senate Simulation
Narrative Context Module

This module provides the NarrativeContext class, which maintains narrative memory
and history for the AI-generated narrative system.
"""

import logging
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path

from .roman_calendar import RomanCalendar

logger = logging.getLogger(__name__)

@dataclass
class NarrativeEvent:
    """Represents a narrative event in the simulation."""
    id: str
    event_type: str
    description: str
    date: Dict[str, Any]  # Stores year, month, day
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    significance: int = 1  # 1-5 scale of importance
    tags: List[str] = field(default_factory=list)
    entities: List[str] = field(default_factory=list)  # People, places, etc.
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the event to a dictionary for serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NarrativeEvent':
        """Create an event from a dictionary."""
        return cls(**data)


class NarrativeContext:
    """
    Maintains narrative memory and history for the simulation.
    
    This class is responsible for:
    1. Storing narrative events
    2. Providing context for event generation
    3. Persisting narrative history between sessions
    4. Retrieving relevant past events
    """
    
    def __init__(self, save_dir: str = "saves/narrative"):
        """Initialize the narrative context."""
        self.events: List[NarrativeEvent] = []
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)
        self.current_narrative_themes: List[str] = []
        self.recurring_entities: Dict[str, int] = {}  # Entity name -> frequency count
        logger.info("NarrativeContext initialized")
    
    def add_event(self, event: NarrativeEvent) -> None:
        """
        Add a new narrative event to the context.
        
        Args:
            event: The narrative event to add
        """
        self.events.append(event)
        
        # Update recurring entities
        for entity in event.entities:
            self.recurring_entities[entity] = self.recurring_entities.get(entity, 0) + 1
        
        # Update narrative themes based on event tags
        for tag in event.tags:
            if tag not in self.current_narrative_themes:
                self.current_narrative_themes.append(tag)
                
        logger.debug(f"Added narrative event: {event.event_type} - {event.id}")
    
    def get_recent_events(self, count: int = 5) -> List[NarrativeEvent]:
        """
        Get the most recent narrative events.
        
        Args:
            count: Number of events to retrieve
            
        Returns:
            List of recent narrative events
        """
        return sorted(self.events, key=lambda e: e.timestamp, reverse=True)[:count]
    
    def get_events_by_type(self, event_type: str) -> List[NarrativeEvent]:
        """
        Get events of a specific type.
        
        Args:
            event_type: The type of events to retrieve
            
        Returns:
            List of events matching the specified type
        """
        return [e for e in self.events if e.event_type == event_type]
    
    def get_events_by_tag(self, tag: str) -> List[NarrativeEvent]:
        """
        Get events with a specific tag.
        
        Args:
            tag: The tag to search for
            
        Returns:
            List of events with the specified tag
        """
        return [e for e in self.events if tag in e.tags]
    
    def get_events_by_entity(self, entity: str) -> List[NarrativeEvent]:
        """
        Get events involving a specific entity.
        
        Args:
            entity: The entity to search for
            
        Returns:
            List of events involving the specified entity
        """
        return [e for e in self.events if entity in e.entities]
    
    def get_events_by_date(self, calendar: RomanCalendar) -> List[NarrativeEvent]:
        """
        Get events that occurred on the same date as the provided calendar.
        
        Args:
            calendar: The calendar containing the date to match
            
        Returns:
            List of events matching the date
        """
        return [
            e for e in self.events 
            if (e.date.get('year') == calendar.year and 
                e.date.get('month') == calendar.month and 
                e.date.get('day') == calendar.day)
        ]
    
    def get_narrative_summary(self, max_events: int = 10) -> str:
        """
        Generate a summary of the current narrative context.
        
        Args:
            max_events: Maximum number of events to include in the summary
            
        Returns:
            A string summarizing the narrative context
        """
        if not self.events:
            return "No narrative events have occurred yet."
        
        recent_events = self.get_recent_events(max_events)
        
        summary = "Recent events:\n"
        for event in recent_events:
            summary += f"- {event.event_type}: {event.description}\n"
        
        summary += "\nRecurring entities:\n"
        sorted_entities = sorted(self.recurring_entities.items(), key=lambda x: x[1], reverse=True)
        for entity, count in sorted_entities[:5]:
            summary += f"- {entity} (mentioned {count} times)\n"
        
        summary += "\nCurrent narrative themes:\n"
        for theme in self.current_narrative_themes[:5]:
            summary += f"- {theme}\n"
        
        return summary
    
    def save(self, filename: Optional[str] = None) -> str:
        """
        Save the narrative context to a file.
        
        Args:
            filename: Optional custom filename
            
        Returns:
            Path to the saved file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"narrative_context_{timestamp}.json"
        
        # Ensure .json extension
        if not filename.endswith(".json"):
            filename += ".json"
        
        save_path = self.save_dir / filename
        
        # Create the save data
        save_data = {
            "events": [event.to_dict() for event in self.events],
            "current_narrative_themes": self.current_narrative_themes,
            "recurring_entities": self.recurring_entities,
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "event_count": len(self.events)
            }
        }
        
        # Write to file
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(save_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Narrative context saved to {save_path}")
        return str(save_path)
    
    def load(self, filename: str) -> bool:
        """
        Load narrative context from a file.
        
        Args:
            filename: The name of the file to load
            
        Returns:
            True if loaded successfully, False otherwise
        """
        # If filename doesn't include path, assume it's in the save directory
        if not Path(filename).is_absolute():
            load_path = self.save_dir / filename
        else:
            load_path = Path(filename)
        
        # Ensure .json extension
        if not str(load_path).endswith(".json"):
            load_path = Path(f"{load_path}.json")
        
        try:
            with open(load_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Load events
            self.events = [NarrativeEvent.from_dict(event_data) for event_data in data.get("events", [])]
            
            # Load other data
            self.current_narrative_themes = data.get("current_narrative_themes", [])
            self.recurring_entities = data.get("recurring_entities", {})
            
            logger.info(f"Narrative context loaded from {load_path}")
            return True
        except Exception as e:
            logger.error(f"Error loading narrative context from {load_path}: {e}")
            return False