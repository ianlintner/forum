"""
Roman Senate Simulation
Senator Event Generator Module

This module provides the SenatorEventGenerator class, which generates personal events
involving senators for the Roman Senate simulation.
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

class SenatorEventGenerator(EventGenerator):
    """
    Generates personal events involving senators for the Roman Senate simulation.
    
    This generator creates events about individual senators, including:
    - Personal achievements and milestones
    - Family events (marriages, births, deaths)
    - Property acquisitions or losses
    - Personal scandals or triumphs
    - Health issues or recoveries
    - Political maneuvers outside the Senate
    """
    
    def __init__(self, llm_provider: LLMProvider):
        """
        Initialize the senator event generator.
        
        Args:
            llm_provider: LLM provider for generating content
        """
        self.llm_provider = llm_provider
        self.senator_event_categories = [
            "family", "property", "achievement", "scandal", 
            "health", "political", "travel", "personal"
        ]
        logger.info("SenatorEventGenerator initialized")
    
    async def generate_events(self, game_state: GameState, narrative_context: NarrativeContext) -> List[NarrativeEvent]:
        """
        Generate senator events based on the current game state and narrative context.
        
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
        
        # Get senators for inclusion in events
        senators = game_state.senators
        senator_names = [senator.name for senator in senators] if senators else []
        
        # If no senators available, we can't generate senator events
        if not senator_names:
            logger.warning("No senators available for senator events")
            return events
        
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
        
        # Select categories for this batch of senator events
        selected_categories = random.sample(
            self.senator_event_categories, 
            min(num_events, len(self.senator_event_categories))
        )
        
        # Generate each senator event
        for category in selected_categories:
            # Select a random senator as the focus of this event
            focus_senator = random.choice(senator_names)
            
            event = await self._generate_senator_event(
                category, focus_senator, current_date, game_state, 
                recent_event_descriptions, all_entities
            )
            if event:
                events.append(event)
        
        logger.debug(f"Generated {len(events)} senator events")
        return events
    
    async def _generate_senator_event(self, category: str, focus_senator: str, 
                              current_date: Dict[str, Any], game_state: GameState, 
                              recent_events: List[str], entities: List[str]) -> Optional[NarrativeEvent]:
        """
        Generate a single senator event of the specified category.
        
        Args:
            category: The category of senator event to generate
            focus_senator: The senator who is the focus of this event
            current_date: Dictionary with current date information
            game_state: The current game state
            recent_events: List of recent event descriptions
            entities: List of entity names to potentially include
            
        Returns:
            A narrative event or None if generation failed
        """
        # Build the prompt for the LLM
        prompt = self._build_senator_prompt(category, focus_senator, current_date, recent_events, entities)
        
        try:
            # Generate the senator event description - properly await the async method
            response = await self.llm_provider.generate_text(prompt)
            
            # Parse the response
            lines = response.strip().split('\n')
            title = lines[0].strip() if lines else f"Senator {focus_senator} Event"
            description = '\n'.join(lines[1:]).strip() if len(lines) > 1 else response.strip()
            
            # Extract entities mentioned in the description
            mentioned_entities = self._extract_entities(description, entities)
            
            # Ensure the focus senator is included in the entities
            if focus_senator not in mentioned_entities:
                mentioned_entities.append(focus_senator)
            
            # Determine significance (scandals and major political events are more significant)
            significance = 3 if category in ["scandal", "political"] else 2
            
            # Create the event
            event = NarrativeEvent(
                id=str(uuid.uuid4()),
                event_type="senator_event",
                description=description,
                date={
                    "year": current_date["year"],
                    "month": current_date["month"],
                    "day": current_date["day"]
                },
                significance=significance,
                tags=[category, "senator", "personal"],
                entities=mentioned_entities,
                metadata={
                    "title": title,
                    "category": category,
                    "focus_senator": focus_senator,
                    "relationships": self._extract_relationships(description, focus_senator, entities)
                }
            )
            
            return event
        except Exception as e:
            logger.error(f"Error generating senator event: {e}")
            return None
    
    def _build_senator_prompt(self, category: str, focus_senator: str, 
                            current_date: Dict[str, Any], recent_events: List[str], 
                            entities: List[str]) -> str:
        """
        Build a prompt for generating a senator event.
        
        Args:
            category: The category of senator event to generate
            focus_senator: The senator who is the focus of this event
            current_date: Dictionary with current date information
            recent_events: List of recent event descriptions
            entities: List of entity names to potentially include
            
        Returns:
            Prompt string for the LLM
        """
        # Category-specific context
        category_contexts = {
            "family": "a family event (marriage, birth, death, etc.) involving the senator's household",
            "property": "property acquisition, construction, or loss involving the senator's estates",
            "achievement": "a personal achievement or milestone in the senator's life",
            "scandal": "a personal scandal or controversy involving the senator",
            "health": "health issues, recovery, or medical treatment of the senator",
            "political": "political maneuvering or activities outside the Senate",
            "travel": "travel, journeys, or visits by the senator",
            "personal": "personal activities, hobbies, or interests of the senator"
        }
        
        category_context = category_contexts.get(category, "personal events in a senator's life")
        
        # Select other entities to potentially include
        other_entities = [e for e in entities if e != focus_senator]
        related_entities = random.sample(other_entities, min(2, len(other_entities))) if other_entities else []
        
        # Build the prompt
        prompt = f"""
        You are a personal chronicler in Ancient Rome during the late Republic period.
        Today is {current_date["formatted"]}.
        
        Generate an account about {category_context} for Senator {focus_senator}.
        This should be a detailed description of a personal event that would affect the senator's life or reputation.
        
        Include specific details about:
        - The nature of the event
        - How it affects the senator personally
        - Any other individuals involved
        - Potential implications for the senator's standing or future
        
        Start with a brief title for the account, then provide the description.
        
        Recent events:
        {chr(10).join(recent_events) if recent_events else "No recent events."}
        
        """
        
        # Add related entities if available
        if related_entities:
            prompt += f"""
            You may reference these individuals as potential family members, friends, or associates:
            {', '.join(related_entities)}
            """
        
        prompt += """
        Keep the tone appropriate for a personal account in Ancient Rome. Be specific about
        Roman customs, family structures, and social expectations. The account should be
        historically plausible for the late Roman Republic period.
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
    
    def _extract_relationships(self, text: str, focus_senator: str, entities: List[str]) -> List[Dict[str, Any]]:
        """
        Extract relationship information from the text.
        
        Args:
            text: The text to analyze
            focus_senator: The main senator in the event
            entities: List of entity names to check for relationships
            
        Returns:
            List of relationship dictionaries
        """
        relationships = []
        
        # Find other entities mentioned in the text
        mentioned_entities = [e for e in entities if e != focus_senator and e in text]
        
        # Create a simple relationship for each mentioned entity
        for entity in mentioned_entities:
            # In a more sophisticated implementation, we would analyze the text
            # to determine relationship type and strength
            relationships.append({
                "entity1": focus_senator,
                "entity2": entity,
                "type": "associated",
                "strength": 1
            })
        
        return relationships