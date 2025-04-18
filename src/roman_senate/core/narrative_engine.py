"""
Roman Senate Simulation
Narrative Engine Module

This module provides the NarrativeEngine class, which serves as the central controller
for narrative generation in the Roman Senate simulation.
"""

import logging
import random
import asyncio
from typing import Dict, List, Any, Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from .game_state import GameState
from .narrative_context import NarrativeContext, NarrativeEvent
from .event_manager import EventManager
from ..utils.llm.base import LLMProvider

logger = logging.getLogger(__name__)

class NarrativeEngine:
    """
    Central controller for narrative generation in the Roman Senate simulation.
    
    This class is responsible for:
    1. Coordinating the generation of narrative events
    2. Managing the narrative context
    3. Integrating with the game state
    4. Providing narrative content to other components
    """
    
    def __init__(self, game_state: 'GameState', llm_provider: LLMProvider):
        """
        Initialize the narrative engine.
        
        Args:
            game_state: The game state to use
            llm_provider: The LLM provider for generating content
        """
        self.game_state = game_state
        self.llm_provider = llm_provider
        self.narrative_context = NarrativeContext()
        self.event_manager = EventManager(game_state, self.narrative_context)
        self._initialize_components()
        logger.info("NarrativeEngine initialized")
    
    def _initialize_components(self) -> None:
        """Initialize and register event generators and processors."""
        # Import here to avoid circular imports
        from ..agents.event_generators.daily_event_generator import DailyEventGenerator
        from ..agents.event_generators.rumor_event_generator import RumorEventGenerator
        from ..agents.event_generators.military_event_generator import MilitaryEventGenerator
        from ..agents.event_generators.religious_event_generator import ReligiousEventGenerator
        from ..agents.event_generators.senator_event_generator import SenatorEventGenerator
        from ..agents.event_generators.mundane_event_generator import MundaneEventGenerator
        from ..agents.event_processors.consistency_processor import ConsistencyProcessor
        from ..agents.event_processors.relationship_processor import RelationshipProcessor
        
        # Register event generators
        self.event_manager.register_generator(
            "daily_events", 
            DailyEventGenerator(self.llm_provider)
        )
        self.event_manager.register_generator(
            "rumors", 
            RumorEventGenerator(self.llm_provider)
        )
        self.event_manager.register_generator(
            "military_events", 
            MilitaryEventGenerator(self.llm_provider)
        )
        self.event_manager.register_generator(
            "religious_events", 
            ReligiousEventGenerator(self.llm_provider)
        )
        self.event_manager.register_generator(
            "senator_events", 
            SenatorEventGenerator(self.llm_provider)
        )
        self.event_manager.register_generator(
            "mundane_events", 
            MundaneEventGenerator(self.llm_provider)
        )
        
        # Register event processors
        self.event_manager.register_processor(
            "consistency", 
            ConsistencyProcessor(),
            ["daily_event", "rumor", "military_event", "religious_event", "senator_event", "mundane_event", "interaction"]
        )
        self.event_manager.register_processor(
            "relationships", 
            RelationshipProcessor(),
            ["interaction", "rumor", "senator_event"]
        )
    
    async def generate_daily_narrative(self) -> List[NarrativeEvent]:
        """
        Generate the daily narrative content.
        
        Returns:
            List of generated narrative events
        """
        # Generate events using all registered generators
        events = await self.event_manager.generate_events()
        
        # Log the generation
        logger.info(f"Generated {len(events)} narrative events for the day")
        
        return events
    
    async def generate_targeted_narrative(self, event_types: List[str], count: int = 1) -> List[NarrativeEvent]:
        """
        Generate targeted narrative content of specific types.
        
        Args:
            event_types: List of event types to generate
            count: Number of events to generate for each type
            
        Returns:
            List of generated narrative events
        """
        all_events = []
        
        # Map event types to generator IDs
        type_to_generator = {
            "daily_event": "daily_events",
            "rumor": "rumors",
            "military_event": "military_events",
            "religious_event": "religious_events",
            "senator_event": "senator_events",
            "mundane_event": "mundane_events"
        }
        
        # Generate events for each requested type
        for event_type in event_types:
            generator_id = type_to_generator.get(event_type)
            if not generator_id:
                logger.warning(f"No generator found for event type: {event_type}")
                continue
                
            # Generate events using the specific generator
            events = await self.event_manager.generate_events([generator_id])
            
            # Take only the requested count
            events = events[:count]
            all_events.extend(events)
        
        return all_events
    
    def get_narrative_summary(self) -> str:
        """
        Get a summary of the current narrative.
        
        Returns:
            String summary of the narrative context
        """
        return self.narrative_context.get_narrative_summary()
    
    def get_relevant_events(self, entity: Optional[str] = None, 
                           tags: Optional[List[str]] = None,
                           count: int = 5) -> List[NarrativeEvent]:
        """
        Get events relevant to the specified criteria.
        
        Args:
            entity: Optional entity to filter by
            tags: Optional list of tags to filter by
            count: Maximum number of events to return
            
        Returns:
            List of relevant narrative events
        """
        # Start with all events
        events = self.narrative_context.events
        
        # Filter by entity if specified
        if entity:
            events = [e for e in events if entity in e.entities]
        
        # Filter by tags if specified
        if tags:
            events = [e for e in events if any(tag in e.tags for tag in tags)]
        
        # Sort by significance and recency
        events.sort(key=lambda e: (e.significance, e.timestamp), reverse=True)
        
        # Return the top events
        return events[:count]
    
    def save_narrative_context(self, filename: Optional[str] = None) -> str:
        """
        Save the narrative context to a file.
        
        Args:
            filename: Optional custom filename
            
        Returns:
            Path to the saved file
        """
        return self.narrative_context.save(filename)
    
    def load_narrative_context(self, filename: str) -> bool:
        """
        Load narrative context from a file.
        
        Args:
            filename: The name of the file to load
            
        Returns:
            True if loaded successfully, False otherwise
        """
        return self.narrative_context.load(filename)
    
    def integrate_with_game_state(self) -> None:
        """
        Integrate narrative events with the game state.
        
        This method adds relevant narrative events to the game state's
        historical events database for use by other components.
        """
        # Get recent narrative events
        recent_events = self.narrative_context.get_recent_events()
        
        # Convert narrative events to historical events and add to game state
        for event in recent_events:
            # Create a historical event from the narrative event
            from .historical_events import HistoricalEvent, EventImportance
            
            # Extract date components
            year = event.date.get('year', self.game_state.calendar.year)
            month = event.date.get('month')
            day = event.date.get('day')
            
            # Map significance (1-5) to importance (1-3)
            significance_map = {1: 1, 2: 1, 3: 2, 4: 2, 5: 3}
            importance_value = significance_map.get(event.significance, 1)
            
            # Generate a unique ID for the historical event
            event_id = random.randint(1000, 9999)
            
            # Create the historical event with the correct parameters
            historical_event = HistoricalEvent(
                id=event_id,
                title=event.metadata.get('title', f"{event.event_type.capitalize()} Event"),
                description=event.description,
                year=year,
                month=month,
                day=day,
                importance=EventImportance(importance_value)
            )
            
            # Add to game state
            self.game_state.add_historical_event(historical_event)