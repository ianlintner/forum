"""
Roman Senate Simulation
Military Event Generator Module

This module provides the MilitaryEventGenerator class, which generates military events
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

class MilitaryEventGenerator(EventGenerator):
    """
    Generates military events for the Roman Senate simulation.
    
    This generator creates events about military affairs, including:
    - Battles and skirmishes
    - Troop movements and deployments
    - Military campaigns and strategies
    - Victories and defeats
    - Military appointments and promotions
    """
    
    def __init__(self, llm_provider: LLMProvider):
        """
        Initialize the military event generator.
        
        Args:
            llm_provider: LLM provider for generating content
        """
        self.llm_provider = llm_provider
        self.military_categories = [
            "battle", "troop_movement", "campaign", "appointment", 
            "siege", "naval", "victory", "defeat"
        ]
        logger.info("MilitaryEventGenerator initialized")
    
    async def generate_events(self, game_state: GameState, narrative_context: NarrativeContext) -> List[NarrativeEvent]:
        """
        Generate military events based on the current game state and narrative context.
        
        Args:
            game_state: The current game state
            narrative_context: The current narrative context
            
        Returns:
            List of generated narrative events
        """
        events = []
        
        # Determine how many events to generate (1-2)
        num_events = random.randint(1, 2)
        
        # Get current date information
        current_date = {
            "year": game_state.calendar.year,
            "month": game_state.calendar.current_month_idx + 1,  # Convert to 1-based month
            "day": game_state.calendar.current_day,
            "formatted": game_state.get_formatted_date()
        }
        
        # Get senators for potential inclusion in military events
        senators = game_state.senators
        senator_names = [senator.name for senator in senators] if senators else []
        
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
        
        # Combine senator names and recurring entities
        all_entities = list(set(senator_names + recurring_entities))
        
        # Select categories for this batch of military events
        selected_categories = random.sample(
            self.military_categories, 
            min(num_events, len(self.military_categories))
        )
        
        # Generate each military event
        for category in selected_categories:
            event = await self._generate_military_event(
                category, current_date, game_state, 
                recent_event_descriptions, all_entities
            )
            if event:
                events.append(event)
        
        logger.debug(f"Generated {len(events)} military events")
        return events
    
    async def _generate_military_event(self, category: str, current_date: Dict[str, Any], 
                               game_state: GameState, recent_events: List[str],
                               entities: List[str]) -> Optional[NarrativeEvent]:
        """
        Generate a single military event of the specified category.
        
        Args:
            category: The category of military event to generate
            current_date: Dictionary with current date information
            game_state: The current game state
            recent_events: List of recent event descriptions
            entities: List of entity names to potentially include
            
        Returns:
            A narrative event or None if generation failed
        """
        # Build the prompt for the LLM
        prompt = self._build_military_prompt(category, current_date, recent_events, entities)
        
        try:
            # Generate the military event description - properly await the async method
            response = await self.llm_provider.generate_text(prompt)
            
            # Parse the response
            lines = response.strip().split('\n')
            title = lines[0].strip() if lines else "Military Event"
            description = '\n'.join(lines[1:]).strip() if len(lines) > 1 else response.strip()
            
            # Extract entities mentioned in the description
            mentioned_entities = self._extract_entities(description, entities)
            
            # Determine significance (military events are generally more significant)
            significance = 3 if category in ["battle", "victory", "defeat", "siege"] else 2
            
            # Create the event
            event = NarrativeEvent(
                id=str(uuid.uuid4()),
                event_type="military_event",
                description=description,
                date={
                    "year": current_date["year"],
                    "month": current_date["month"],
                    "day": current_date["day"]
                },
                significance=significance,
                tags=[category, "military", "war"],
                entities=mentioned_entities,
                metadata={
                    "title": title,
                    "category": category,
                    "location": self._extract_location(description)
                }
            )
            
            return event
        except Exception as e:
            logger.error(f"Error generating military event: {e}")
            return None
    
    def _build_military_prompt(self, category: str, current_date: Dict[str, Any],
                             recent_events: List[str], entities: List[str]) -> str:
        """
        Build a prompt for generating a military event.
        
        Args:
            category: The category of military event to generate
            current_date: Dictionary with current date information
            recent_events: List of recent event descriptions
            entities: List of entity names to potentially include
            
        Returns:
            Prompt string for the LLM
        """
        # Category-specific context
        category_contexts = {
            "battle": "a battle or skirmish between Roman forces and enemies",
            "troop_movement": "movement or deployment of Roman legions or auxiliary forces",
            "campaign": "a military campaign or strategic operation",
            "appointment": "appointment or promotion of military commanders",
            "siege": "a siege of a city or fortress",
            "naval": "naval operations or sea battles",
            "victory": "a Roman military victory",
            "defeat": "a Roman military setback or defeat"
        }
        
        category_context = category_contexts.get(category, "military events in the Roman Republic")
        
        # Select entities to potentially include
        commanders = random.sample(entities, min(2, len(entities))) if entities else []
        
        # Build the prompt
        prompt = f"""
        You are a military correspondent in Ancient Rome during the late Republic period.
        Today is {current_date["formatted"]}.
        
        Generate a report about {category_context}.
        This should be a detailed account of a military event that would be of interest to the Senate.
        
        Include specific details about:
        - Location of the event
        - Military commanders involved
        - Forces engaged (legions, cohorts, etc.)
        - Outcome or current status
        
        Start with a brief title for the report, then provide the description.
        
        Recent events:
        {chr(10).join(recent_events) if recent_events else "No recent events."}
        
        """
        
        # Add commanders if available
        if commanders:
            prompt += f"""
            You may reference these individuals as potential commanders or officials:
            {', '.join(commanders)}
            """
        
        prompt += """
        Keep the tone appropriate for a military report in Ancient Rome. Be specific about
        locations, troop numbers, and tactical details. The report should be historically
        plausible for the late Roman Republic period.
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
        
        return entities
    
    def _extract_location(self, text: str) -> str:
        """
        Extract location information from the text.
        
        Args:
            text: The text to analyze
            
        Returns:
            Location string or "Unknown" if not found
        """
        # In a more sophisticated implementation, this would use NER
        # For now, we'll just return a placeholder
        return "Various locations"