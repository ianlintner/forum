"""
Roman Senate Simulation
Religious Event Generator Module

This module provides the ReligiousEventGenerator class, which generates religious events
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

class ReligiousEventGenerator(EventGenerator):
    """
    Generates religious events for the Roman Senate simulation.
    
    This generator creates events about religious affairs, including:
    - Religious ceremonies and festivals
    - Omens and portents
    - Temple dedications and repairs
    - Priestly appointments
    - Divine interventions and interpretations
    """
    
    def __init__(self, llm_provider: LLMProvider):
        """
        Initialize the religious event generator.
        
        Args:
            llm_provider: LLM provider for generating content
        """
        self.llm_provider = llm_provider
        self.religious_categories = [
            "ceremony", "omen", "temple", "priest", 
            "sacrifice", "festival", "prophecy", "divine_sign"
        ]
        # List of major Roman deities for reference
        self.roman_deities = [
            "Jupiter", "Juno", "Mars", "Venus", "Neptune", "Minerva", 
            "Apollo", "Diana", "Vulcan", "Vesta", "Mercury", "Ceres",
            "Bacchus", "Pluto", "Saturn", "Janus"
        ]
        logger.info("ReligiousEventGenerator initialized")
    
    async def generate_events(self, game_state: GameState, narrative_context: NarrativeContext) -> List[NarrativeEvent]:
        """
        Generate religious events based on the current game state and narrative context.
        
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
        
        # Get senators for potential inclusion in religious events
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
        
        # Select categories for this batch of religious events
        selected_categories = random.sample(
            self.religious_categories, 
            min(num_events, len(self.religious_categories))
        )
        
        # Generate each religious event
        for category in selected_categories:
            event = await self._generate_religious_event(
                category, current_date, game_state, 
                recent_event_descriptions, all_entities
            )
            if event:
                events.append(event)
        
        logger.debug(f"Generated {len(events)} religious events")
        return events
    
    async def _generate_religious_event(self, category: str, current_date: Dict[str, Any], 
                                game_state: GameState, recent_events: List[str],
                                entities: List[str]) -> Optional[NarrativeEvent]:
        """
        Generate a single religious event of the specified category.
        
        Args:
            category: The category of religious event to generate
            current_date: Dictionary with current date information
            game_state: The current game state
            recent_events: List of recent event descriptions
            entities: List of entity names to potentially include
            
        Returns:
            A narrative event or None if generation failed
        """
        # Build the prompt for the LLM
        prompt = self._build_religious_prompt(category, current_date, recent_events, entities)
        
        try:
            # Generate the religious event description - properly await the async method
            response = await self.llm_provider.generate_text(prompt)
            
            # Parse the response
            lines = response.strip().split('\n')
            title = lines[0].strip() if lines else "Religious Event"
            description = '\n'.join(lines[1:]).strip() if len(lines) > 1 else response.strip()
            
            # Extract entities mentioned in the description
            mentioned_entities = self._extract_entities(description, entities)
            
            # Determine significance (omens and prophecies are more significant)
            significance = 3 if category in ["omen", "prophecy", "divine_sign"] else 2
            
            # Extract deity information
            deity = self._extract_deity(description)
            
            # Create the event
            event = NarrativeEvent(
                id=str(uuid.uuid4()),
                event_type="religious_event",
                description=description,
                date={
                    "year": current_date["year"],
                    "month": current_date["month"],
                    "day": current_date["day"]
                },
                significance=significance,
                tags=[category, "religious", "divine"],
                entities=mentioned_entities,
                metadata={
                    "title": title,
                    "category": category,
                    "deity": deity,
                    "temple": self._extract_temple(description)
                }
            )
            
            return event
        except Exception as e:
            logger.error(f"Error generating religious event: {e}")
            return None
    
    def _build_religious_prompt(self, category: str, current_date: Dict[str, Any],
                              recent_events: List[str], entities: List[str]) -> str:
        """
        Build a prompt for generating a religious event.
        
        Args:
            category: The category of religious event to generate
            current_date: Dictionary with current date information
            recent_events: List of recent event descriptions
            entities: List of entity names to potentially include
            
        Returns:
            Prompt string for the LLM
        """
        # Category-specific context
        category_contexts = {
            "ceremony": "a religious ceremony or ritual performed in Rome",
            "omen": "an omen or portent observed and its interpretation",
            "temple": "activities at a temple, including dedications or repairs",
            "priest": "appointment or activities of priests or religious officials",
            "sacrifice": "a significant sacrifice made to the gods",
            "festival": "a religious festival or celebration",
            "prophecy": "a prophecy or prediction from religious authorities",
            "divine_sign": "signs believed to be from the gods and their interpretation"
        }
        
        category_context = category_contexts.get(category, "religious events in the Roman Republic")
        
        # Select a deity for this event
        deity = random.choice(self.roman_deities)
        
        # Select entities to potentially include
        religious_figures = random.sample(entities, min(2, len(entities))) if entities else []
        
        # Build the prompt
        prompt = f"""
        You are a religious chronicler in Ancient Rome during the late Republic period.
        Today is {current_date["formatted"]}.
        
        Generate an account about {category_context}.
        This should be a detailed description of a religious event that would be significant to Romans.
        
        Include specific details about:
        - The deity or deities involved (consider {deity} or other Roman gods)
        - The location (temple, sacred site, etc.)
        - Religious officials or participants
        - The significance or interpretation of the event
        
        Start with a brief title for the account, then provide the description.
        
        Recent events:
        {chr(10).join(recent_events) if recent_events else "No recent events."}
        
        """
        
        # Add religious figures if available
        if religious_figures:
            prompt += f"""
            You may reference these individuals as potential priests, augurs, or participants:
            {', '.join(religious_figures)}
            """
        
        prompt += """
        Keep the tone appropriate for a religious account in Ancient Rome. Be specific about
        religious practices, deities, and Roman religious beliefs. The account should be
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
    
    def _extract_deity(self, text: str) -> str:
        """
        Extract deity information from the text.
        
        Args:
            text: The text to analyze
            
        Returns:
            Deity name or "Unknown" if not found
        """
        for deity in self.roman_deities:
            if deity in text:
                return deity
        return "Various deities"
    
    def _extract_temple(self, text: str) -> str:
        """
        Extract temple information from the text.
        
        Args:
            text: The text to analyze
            
        Returns:
            Temple name or "Unknown" if not found
        """
        # In a more sophisticated implementation, this would use NER
        # For now, we'll just check for the word "Temple" and extract nearby text
        if "Temple" in text or "temple" in text:
            return "Temple mentioned"
        return "Unknown"