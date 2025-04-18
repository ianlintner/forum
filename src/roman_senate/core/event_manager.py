"""
Roman Senate Simulation
Event Manager Module

This module provides the EventManager class, which manages event generators and processors
for the AI-generated narrative system.
"""

import logging
import uuid
import asyncio
from typing import Dict, List, Any, Optional, Type, Callable, TYPE_CHECKING
from abc import ABC, abstractmethod

from .narrative_context import NarrativeContext, NarrativeEvent
if TYPE_CHECKING:
    from .game_state import GameState

logger = logging.getLogger(__name__)

class EventGenerator(ABC):
    """Base class for all event generators."""
    
    @abstractmethod
    async def generate_events(self, game_state: 'GameState', narrative_context: NarrativeContext) -> List[NarrativeEvent]:
        """
        Generate narrative events based on the current game state and narrative context.
        
        Args:
            game_state: The current game state
            narrative_context: The current narrative context
            
        Returns:
            List of generated narrative events
        """
        pass


class EventProcessor(ABC):
    """Base class for all event processors."""
    
    @abstractmethod
    def process_event(self, event: NarrativeEvent, game_state: 'GameState', narrative_context: NarrativeContext) -> NarrativeEvent:
        """
        Process a narrative event to ensure consistency and manage relationships.
        
        Args:
            event: The narrative event to process
            game_state: The current game state
            narrative_context: The current narrative context
            
        Returns:
            The processed narrative event
        """
        pass


class EventManager:
    """
    Manages event generators and processors for the narrative system.
    
    This class is responsible for:
    1. Registering event generators and processors
    2. Coordinating event generation
    3. Processing events through the appropriate processors
    4. Adding processed events to the narrative context
    """
    
    def __init__(self, game_state: 'GameState', narrative_context: NarrativeContext):
        """
        Initialize the event manager.
        
        Args:
            game_state: The game state to use
            narrative_context: The narrative context to use
        """
        self.game_state = game_state
        self.narrative_context = narrative_context
        self.generators: Dict[str, EventGenerator] = {}
        self.processors: Dict[str, EventProcessor] = {}
        self.event_type_processors: Dict[str, List[str]] = {}  # Maps event types to processor IDs
        logger.info("EventManager initialized")
    
    def register_generator(self, generator_id: str, generator: EventGenerator) -> None:
        """
        Register an event generator.
        
        Args:
            generator_id: Unique identifier for the generator
            generator: The event generator instance
        """
        self.generators[generator_id] = generator
        logger.debug(f"Registered event generator: {generator_id}")
    
    def register_processor(self, processor_id: str, processor: EventProcessor, event_types: List[str] = None) -> None:
        """
        Register an event processor.
        
        Args:
            processor_id: Unique identifier for the processor
            processor: The event processor instance
            event_types: Optional list of event types this processor handles
        """
        self.processors[processor_id] = processor
        
        # Register processor for specific event types if provided
        if event_types:
            for event_type in event_types:
                if event_type not in self.event_type_processors:
                    self.event_type_processors[event_type] = []
                self.event_type_processors[event_type].append(processor_id)
        
        logger.debug(f"Registered event processor: {processor_id}")
    
    async def generate_events(self, generator_ids: Optional[List[str]] = None) -> List[NarrativeEvent]:
        """
        Generate events using the registered generators.
        
        Args:
            generator_ids: Optional list of generator IDs to use (uses all if None)
            
        Returns:
            List of generated and processed events
        """
        all_events = []
        
        # Determine which generators to use
        generators_to_use = self.generators
        if generator_ids:
            generators_to_use = {gid: self.generators[gid] for gid in generator_ids if gid in self.generators}
        
        # Generate events from each generator
        for generator_id, generator in generators_to_use.items():
            try:
                # Properly await the async generator
                events = await generator.generate_events(self.game_state, self.narrative_context)
                logger.debug(f"Generator {generator_id} produced {len(events)} events")
                
                # Process and add each event
                for event in events:
                    processed_event = self.process_event(event)
                    self.narrative_context.add_event(processed_event)
                    all_events.append(processed_event)
            except Exception as e:
                logger.error(f"Error generating events with {generator_id}: {e}")
        
        return all_events
    
    def process_event(self, event: NarrativeEvent) -> NarrativeEvent:
        """
        Process an event through all relevant processors.
        
        Args:
            event: The event to process
            
        Returns:
            The processed event
        """
        current_event = event
        
        # Get processors for this event type
        processor_ids = self.event_type_processors.get(event.event_type, [])
        
        # If no specific processors for this event type, use all processors
        if not processor_ids:
            processor_ids = list(self.processors.keys())
        
        # Process the event through each processor
        for processor_id in processor_ids:
            try:
                processor = self.processors[processor_id]
                current_event = processor.process_event(
                    current_event, self.game_state, self.narrative_context
                )
            except Exception as e:
                logger.error(f"Error processing event with {processor_id}: {e}")
        
        return current_event
    
    def create_event(self, event_type: str, description: str, significance: int = 1, 
                    tags: List[str] = None, entities: List[str] = None, 
                    metadata: Dict[str, Any] = None) -> NarrativeEvent:
        """
        Create a new narrative event with the current date.
        
        Args:
            event_type: The type of event
            description: Description of the event
            significance: Importance of the event (1-5)
            tags: Optional list of tags
            entities: Optional list of entities involved
            metadata: Optional additional metadata
            
        Returns:
            The created narrative event
        """
        # Get current date from game state
        current_date = {
            "year": self.game_state.calendar.year,
            "month": self.game_state.calendar.month,
            "day": self.game_state.calendar.day
        }
        
        # Create a unique ID for the event
        event_id = str(uuid.uuid4())
        
        # Create the event
        event = NarrativeEvent(
            id=event_id,
            event_type=event_type,
            description=description,
            date=current_date,
            significance=significance,
            tags=tags or [],
            entities=entities or [],
            metadata=metadata or {}
        )
        
        return event