"""
Roman Senate Simulation
Rumor Event Generator Module

This module provides the RumorEventGenerator class, which generates rumors and gossip
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

class RumorEventGenerator(EventGenerator):
    """
    Generates rumors and gossip for the Roman Senate simulation.
    
    This generator creates events about rumors circulating in Rome, including:
    - Political alliances and rivalries
    - Personal scandals and gossip
    - Speculation about foreign affairs
    - Whispers about financial dealings
    - Rumors about religious omens
    """
    
    def __init__(self, llm_provider: LLMProvider):
        """
        Initialize the rumor event generator.
        
        Args:
            llm_provider: LLM provider for generating content
        """
        self.llm_provider = llm_provider
        self.rumor_categories = [
            "political", "personal", "foreign", "financial", 
            "religious", "military", "conspiracy"
        ]
        logger.info("RumorEventGenerator initialized")
    
    async def generate_events(self, game_state: GameState, narrative_context: NarrativeContext) -> List[NarrativeEvent]:
        """
        Generate rumors based on the current game state and narrative context.
        
        Args:
            game_state: The current game state
            narrative_context: The current narrative context
            
        Returns:
            List of generated narrative events
        """
        events = []
        
        # Determine how many rumors to generate (1-2)
        num_rumors = random.randint(1, 2)
        
        # Get current date information
        current_date = {
            "year": game_state.calendar.year,
            "month": game_state.calendar.current_month_idx + 1,  # Convert to 1-based month
            "day": game_state.calendar.current_day,
            "formatted": game_state.get_formatted_date()
        }
        
        # Get senators for potential inclusion in rumors
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
        
        # Select categories for this batch of rumors
        selected_categories = random.sample(
            self.rumor_categories, 
            min(num_rumors, len(self.rumor_categories))
        )
        
        # Generate each rumor
        for category in selected_categories:
            event = await self._generate_rumor(
                category, current_date, game_state, 
                recent_event_descriptions, all_entities
            )
            if event:
                events.append(event)
        
        logger.debug(f"Generated {len(events)} rumors")
        return events
    
    async def _generate_rumor(self, category: str, current_date: Dict[str, Any], 
                       game_state: GameState, recent_events: List[str],
                       entities: List[str]) -> Optional[NarrativeEvent]:
        """
        Generate a single rumor of the specified category.
        
        Args:
            category: The category of rumor to generate
            current_date: Dictionary with current date information
            game_state: The current game state
            recent_events: List of recent event descriptions
            entities: List of entity names to potentially include
            
        Returns:
            A narrative event or None if generation failed
        """
        # Build the prompt for the LLM
        prompt = self._build_rumor_prompt(category, current_date, recent_events, entities)
        
        try:
            # Generate the rumor description - properly await the async method
            response = await self.llm_provider.generate_text(prompt)
            
            # Parse the response
            lines = response.strip().split('\n')
            title = lines[0].strip() if lines else "Rumor"
            description = '\n'.join(lines[1:]).strip() if len(lines) > 1 else response.strip()
            
            # Extract entities mentioned in the description
            mentioned_entities = self._extract_entities(description, entities)
            
            # Determine significance (rumors are slightly more significant than daily events)
            significance = 2 if "conspiracy" in category or "political" in category else 1
            
            # Create the event
            event = NarrativeEvent(
                id=str(uuid.uuid4()),
                event_type="rumor",
                description=description,
                date={
                    "year": current_date["year"],
                    "month": current_date["month"],
                    "day": current_date["day"]
                },
                significance=significance,
                tags=[category, "rumor", "gossip"],
                entities=mentioned_entities,
                metadata={
                    "title": title,
                    "category": category,
                    "veracity": random.random()  # 0-1 value representing how true the rumor is
                }
            )
            
            return event
        except Exception as e:
            logger.error(f"Error generating rumor: {e}")
            return None
    
    def _build_rumor_prompt(self, category: str, current_date: Dict[str, Any],
                           recent_events: List[str], entities: List[str]) -> str:
        """
        Build a prompt for generating a rumor.
        
        Args:
            category: The category of rumor to generate
            current_date: Dictionary with current date information
            recent_events: List of recent event descriptions
            entities: List of entity names to potentially include
            
        Returns:
            Prompt string for the LLM
        """
        # Category-specific context
        category_contexts = {
            "political": "political alliances, rivalries, or ambitions among senators or political figures",
            "personal": "personal scandals, relationships, or gossip about notable Romans",
            "foreign": "foreign affairs, diplomatic relations, or events in other parts of the Republic",
            "financial": "financial dealings, property transactions, or economic matters",
            "religious": "religious omens, divine signs, or priestly matters",
            "military": "military affairs, troop movements, or conflicts",
            "conspiracy": "whispered conspiracies, secret plots, or clandestine activities"
        }
        
        category_context = category_contexts.get(category, "rumors circulating in Rome")
        
        # Select entities to potentially include
        featured_entities = random.sample(entities, min(3, len(entities))) if entities else []
        
        # Build the prompt
        prompt = f"""
        You are a gossipmonger in Ancient Rome during the late Republic period.
        Today is {current_date["formatted"]}.
        
        Generate a rumor or piece of gossip about {category_context}.
        This should be a minor social event or speculation that adds color to the simulation.
        
        Start with a brief title for the rumor, then provide the description.
        
        Recent events:
        {chr(10).join(recent_events) if recent_events else "No recent events."}
        
        """
        
        # Add entities if available
        if featured_entities:
            prompt += f"""
            You may reference these individuals in your rumor if appropriate:
            {', '.join(featured_entities)}
            """
        
        prompt += """
        Keep the tone appropriate for the historical setting. Make the rumor feel authentic
        to Ancient Rome while being subtle and not too scandalous. The rumor should be
        plausible but not necessarily true.
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