"""
Roman Senate Simulation
Mundane Event Generator Module

This module provides the MundaneEventGenerator class, which generates everyday
background events for the Roman Senate simulation to enhance narrative immersion.
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

class MundaneEventGenerator(EventGenerator):
    """
    Generates mundane everyday background events for the Roman Senate simulation.
    
    This generator creates small, colorful details about everyday life in Rome to enhance
    narrative immersion, including:
    - Market/trade activity
    - Weather and seasonal observations
    - Public facilities (baths, theaters)
    - Food and culinary news
    - Street life and common people's activities
    """
    
    def __init__(self, llm_provider: LLMProvider):
        """
        Initialize the mundane event generator.
        
        Args:
            llm_provider: LLM provider for generating content
        """
        self.llm_provider = llm_provider
        self.event_categories = [
            "market", "weather", "public_facilities", "food", "street_life",
            "crafts", "transport", "household", "fashion", "pets"
        ]
        logger.info("MundaneEventGenerator initialized")
    
    async def generate_events(self, game_state: GameState, narrative_context: NarrativeContext) -> List[NarrativeEvent]:
        """
        Generate mundane background events based on the current game state and narrative context.
        
        Args:
            game_state: The current game state
            narrative_context: The current narrative context
            
        Returns:
            List of generated narrative events
        """
        events = []
        
        # Determine how many events to generate (2-4)
        num_events = random.randint(2, 4)
        
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
            event = await self._generate_mundane_event(
                category, current_date, game_state, 
                recent_event_descriptions, recurring_entities
            )
            if event:
                events.append(event)
        
        logger.debug(f"Generated {len(events)} mundane events")
        return events
    
    async def _generate_mundane_event(self, category: str, current_date: Dict[str, Any], 
                              game_state: GameState, recent_events: List[str],
                              recurring_entities: List[str]) -> Optional[NarrativeEvent]:
        """
        Generate a single mundane event of the specified category.
        
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
            title = lines[0].strip() if lines else "Mundane Event"
            description = '\n'.join(lines[1:]).strip() if len(lines) > 1 else response.strip()
            
            # Extract entities mentioned in the description
            entities = self._extract_entities(description, recurring_entities)
            
            # Create the event
            event = NarrativeEvent(
                id=str(uuid.uuid4()),
                event_type="mundane_event",
                description=description,
                date={
                    "year": current_date["year"],
                    "month": current_date["month"],
                    "day": current_date["day"]
                },
                significance=1,  # Mundane events are low significance
                tags=[category, "mundane", "background"],
                entities=entities,
                metadata={
                    "title": title,
                    "category": category
                }
            )
            
            return event
        except Exception as e:
            logger.error(f"Error generating mundane event: {e}")
            return None
    
    def _build_event_prompt(self, category: str, current_date: Dict[str, Any],
                           recent_events: List[str], recurring_entities: List[str]) -> str:
        """
        Build a prompt for generating a mundane event.
        
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
            "market": "market prices, trade news, merchant activities, or small economic developments",
            "weather": "weather conditions, seasonal changes, or natural phenomena affecting daily life",
            "public_facilities": "public baths, theaters, forums, or other public spaces and their activities",
            "food": "food availability, culinary trends, or dining habits in Rome",
            "street_life": "street performers, minor disputes, or everyday interactions between common people",
            "crafts": "artisans, craftspeople, or small workshops and their activities",
            "transport": "carts, animals, or transportation within the city or nearby areas",
            "household": "domestic life, servants, or household management among Romans",
            "fashion": "clothing trends, accessories, or appearance-related observations",
            "pets": "domestic animals, exotic pets, or animal-related anecdotes"
        }
        
        category_context = category_contexts.get(category, "everyday life in Rome")
        
        # Build the prompt
        prompt = f"""
        You are a keen observer of everyday life in Ancient Rome during the late Republic period.
        Today is {current_date["formatted"]}.
        
        Generate a brief, colorful detail (1-2 sentences) about {category_context}.
        This should be a minor background event that provides color and atmosphere to the simulation.
        
        The event should:
        - Be historically plausible for Ancient Rome
        - Focus on mundane, everyday details that add texture to the narrative
        - Use appropriate Roman terminology and references
        - Not directly affect Senate business but provide background context
        - Be specific and vivid rather than generic
        
        Examples of good mundane events:
        - "A shipment of peafowl livers was delivered at the port. I am certain the overseer will take some for himself."
        - "The price of olive oil has increased slightly in the market. Merchants blame poor weather in Sicily."
        - "Street performers near the Forum are drawing large crowds with their new acrobatic routine."
        - "A minor dispute between two shopkeepers in the cloth district was resolved by a passing centurion."
        - "The public baths are especially crowded today due to the unseasonably hot weather."
        
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
        Keep the tone appropriate for the historical setting and make the detail feel authentic
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