"""
Roman Senate Simulation
Daily Event Generator Module

This module provides the DailyEventGenerator class, which generates daily events
for the Roman Senate simulation.
"""

import logging
import random
import uuid
from typing import Dict, List, Any, Optional

from roman_senate.core.game_state import GameState
from roman_senate.core.narrative_context import NarrativeContext, NarrativeEvent
from roman_senate.core.event_manager import EventGenerator
from roman_senate.utils.llm.base import LLMProvider

logger = logging.getLogger(__name__)

class DailyEventGenerator(EventGenerator):
    """
    Generates daily events for the Roman Senate simulation.
    
    This generator creates events about daily life in Rome, including:
    - Market activities and trade
    - Weather and natural phenomena
    - Religious ceremonies and omens
    - Public gatherings and entertainment
    - Minor crimes and disturbances
    """
    
    def __init__(self, llm_provider: LLMProvider):
        """
        Initialize the daily event generator.
        
        Args:
            llm_provider: LLM provider for generating content
        """
        self.llm_provider = llm_provider
        self.event_categories = [
            "market", "weather", "religious", "entertainment", 
            "crime", "visitor", "construction", "health"
        ]
        logger.info("DailyEventGenerator initialized")
    
    async def generate_events(self, game_state: GameState, narrative_context: NarrativeContext) -> List[NarrativeEvent]:
        """
        Generate daily events based on the current game state and narrative context.
        
        Args:
            game_state: The current game state
            narrative_context: The current narrative context
            
        Returns:
            List of generated narrative events
        """
        events = []
        
        # Determine how many events to generate (1-3)
        num_events = random.randint(1, 3)
        
        # Get current date information
        current_date = {
            "year": game_state.calendar.year,
            "month": game_state.calendar.current_month_idx + 1,  # Convert to 1-based month
            "day": game_state.calendar.current_day,
            "formatted": game_state.get_formatted_date()
        }
        
        # Get recent events for context
        recent_events = narrative_context.get_recent_events(3)
        recent_event_descriptions = [
            f"{e.event_type}: {e.description}" for e in recent_events
        ]
        
        # Get recurring entities for continuity
        top_entities = sorted(
            narrative_context.recurring_entities.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:5]
        recurring_entities = [entity for entity, _ in top_entities]
        
        # Select categories for this batch of events
        selected_categories = random.sample(
            self.event_categories, 
            min(num_events, len(self.event_categories))
        )
        
        # Generate each event
        for category in selected_categories:
            event = await self._generate_daily_event(
                category, current_date, game_state, 
                recent_event_descriptions, recurring_entities
            )
            if event:
                events.append(event)
        
        logger.debug(f"Generated {len(events)} daily events")
        return events
    
    async def _generate_daily_event(self, category: str, current_date: Dict[str, Any], 
                             game_state: GameState, recent_events: List[str],
                             recurring_entities: List[str]) -> Optional[NarrativeEvent]:
        """
        Generate a single daily event of the specified category.
        
        Args:
            category: The category of event to generate
            current_date: Dictionary with current date information
            game_state: The current game state
            recent_events: List of recent event descriptions
            recurring_entities: List of recurring entity names
            
        Returns:
            A narrative event or None if generation failed
        """
        # Build the prompt for the LLM
        prompt = self._build_event_prompt(category, current_date, recent_events, recurring_entities)
        
        try:
            # Generate the event description - properly await the async method
            response = await self.llm_provider.generate_text(prompt)
            
            # Parse the response
            lines = response.strip().split('\n')
            title = lines[0].strip() if lines else "Daily Event"
            description = '\n'.join(lines[1:]).strip() if len(lines) > 1 else response.strip()
            
            # Extract entities mentioned in the description
            entities = self._extract_entities(description, recurring_entities)
            
            # Create the event
            event = NarrativeEvent(
                id=str(uuid.uuid4()),
                event_type="daily_event",
                description=description,
                date={
                    "year": current_date["year"],
                    "month": current_date["month"],
                    "day": current_date["day"]
                },
                significance=1,  # Daily events are low significance
                tags=[category, "daily"],
                entities=entities,
                metadata={
                    "title": title,
                    "category": category
                }
            )
            
            return event
        except Exception as e:
            logger.error(f"Error generating daily event: {e}")
            return None
    
    def _build_event_prompt(self, category: str, current_date: Dict[str, Any],
                           recent_events: List[str], recurring_entities: List[str]) -> str:
        """
        Build a prompt for generating a daily event.
        
        Args:
            category: The category of event to generate
            current_date: Dictionary with current date information
            recent_events: List of recent event descriptions
            recurring_entities: List of recurring entity names
            
        Returns:
            Prompt string for the LLM
        """
        # Category-specific context
        category_contexts = {
            "market": "market prices, trade news, merchant activities, or economic developments",
            "weather": "weather conditions, seasonal changes, or natural phenomena affecting daily life",
            "religious": "religious ceremonies, omens, sacrifices, or priestly activities",
            "entertainment": "games, theater performances, public speeches, or other entertainment",
            "crime": "minor crimes, disturbances, or legal disputes in the city",
            "visitor": "arrivals of notable visitors, delegations, or travelers to Rome",
            "construction": "ongoing construction projects, repairs, or urban developments",
            "health": "public health matters, diseases, or medical practices"
        }
        
        category_context = category_contexts.get(category, "daily events in Rome")
        
        # Build the prompt
        prompt = f"""
        You are a town crier in Ancient Rome during the late Republic period.
        Today is {current_date["formatted"]}.
        
        Generate a brief news announcement (1-2 paragraphs) about {category_context}.
        This should be a minor event that provides color and atmosphere to the simulation.
        
        The event should be historically plausible for Ancient Rome and should not directly
        affect Senate business but provide background context.
        
        Start with a brief title, then provide the description.
        
        Recent events:
        {chr(10).join(recent_events) if recent_events else "No recent events."}
        
        """
        
        # Add recurring entities if available
        if recurring_entities:
            prompt += f"""
            You may optionally reference these recurring characters in your announcement:
            {', '.join(recurring_entities)}
            """
        
        prompt += """
        Keep the tone appropriate for the historical setting and make the news feel authentic
        to Ancient Rome. Don't include modern concepts or anachronisms.
        """
        
        return prompt
    
    def _extract_entities(self, text: str, known_entities: List[str]) -> List[str]:
        """
        Extract entities mentioned in the text.
        
        Args:
            text: The text to analyze
            known_entities: List of known entities to look for
            
        Returns:
            List of entity names found in the text
        """
        entities = []
        
        # Check for known entities
        for entity in known_entities:
            if entity in text:
                entities.append(entity)
        
        # In a more advanced implementation, we could use NER here
        # For now, we'll just return the known entities found
        
        return entities