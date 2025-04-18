"""
Roman Senate AI Game
Story Crier Agent Module

This module defines the town crier agent that announces historical events
and provides context at the start of each day in the simulation.
"""

import random
from typing import Dict, List, Optional, Any, TYPE_CHECKING
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from ..core.historical_events import get_announcements_for_current_date, historical_events_db
if TYPE_CHECKING:
    from ..core.game_state import GameState
from ..core.narrative_engine import NarrativeEngine
from ..core.narrative_context import NarrativeEvent
from ..utils.llm.base import LLMProvider

console = Console()

class StoryCrierAgent:
    """
    Agent implementation of a Roman town crier who announces historical events.
    
    The StoryCrierAgent retrieves relevant historical events from the database
    based on the current date in the simulation and creates announcements for them.
    These announcements provide historical context and flavor to the simulation.
    
    It can also use the NarrativeEngine to generate rich, contextual narrative content.
    """
    
    def __init__(self, llm_provider: Optional[LLMProvider] = None, game_state: Optional['GameState'] = None):
        """
        Initialize a story crier agent.
        
        Args:
            llm_provider: Optional LLM provider for enhanced announcements
            game_state: Optional game state for narrative generation
        """
        self.llm_provider = llm_provider
        self.game_state = game_state
        self.announcements_cache = {}  # Cache announcements by date
        
        # Initialize narrative engine if we have both dependencies
        self.narrative_engine = None
        if llm_provider and game_state:
            self.narrative_engine = NarrativeEngine(game_state, llm_provider)
        
    async def generate_announcements(
        self, 
        year: int, 
        month: Optional[int] = None, 
        day: Optional[int] = None,
        count: int = 3
    ) -> List[Dict[str, str]]:
        """
        Generate announcements for the current date.
        
        Args:
            year: Current year in the simulation (negative for BCE)
            month: Current month (1-12, if known)
            day: Current day (1-31, if known)
            count: Number of announcements to generate
            
        Returns:
            List of announcement dictionaries with 'title' and 'text' fields
        """
        # Create a cache key for this date
        cache_key = f"{year}_{month}_{day}"
        
        # Check if we have cached announcements for this date
        if cache_key in self.announcements_cache:
            return self.announcements_cache[cache_key]
        
        # Try to use narrative engine if available
        if self.narrative_engine and self.llm_provider:
            try:
                narrative_events = self.generate_narrative_content(count)
                if narrative_events:
                    # Convert narrative events to announcements format
                    announcements = []
                    for event in narrative_events:
                        announcements.append({
                            "title": event.get("title", "Announcement"),
                            "text": event.get("content", "")
                        })
                    
                    # Cache and return the announcements
                    self.announcements_cache[cache_key] = announcements
                    return announcements
            except Exception as e:
                console.print(f"[yellow]Warning: Narrative engine failed, falling back to historical events.[/]")
        
        # Get announcements from historical events database
        announcements = get_announcements_for_current_date(
            current_year=year,
            current_month=month,
            current_day=day,
            count=count
        )
        
        # If no announcements found, create at least one generic announcement
        if not announcements:
            announcements = [{
                "title": "A Quiet Day in Rome",
                "text": f"Today in the year {abs(year)} {'BCE' if year < 0 else 'CE'}, "
                        f"the Senate gathers as usual for its deliberations. "
                        f"No significant historical events are recorded for this day."
            }]
        
        # Cache the announcements for this date
        self.announcements_cache[cache_key] = announcements
        
        return announcements
    
    def display_announcements(self, announcements: List[Dict[str, str]]) -> None:
        """
        Display announcements with distinctive styling.
        
        Args:
            announcements: List of announcement dictionaries with 'title' and 'text' fields
        """
        if not announcements:
            return
            
        console.print()
        console.print("[bold yellow]𝕿𝖍𝖊 𝕿𝖔𝖜𝖓 𝕮𝖗𝖎𝖊𝖗 𝕬𝖓𝖓𝖔𝖚𝖓𝖈𝖊𝖒𝖊𝖓𝖙𝖘[/]")
        console.print("[yellow]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/]")
        
        for announcement in announcements:
            title = announcement.get("title", "Announcement")
            text = announcement.get("text", "")
            
            # Create a styled announcement panel with distinct appearance
            panel_content = Text()
            panel_content.append(text, style="italic")
            
            panel = Panel(
                panel_content,
                title=f"[bold]{title}[/]",
                border_style="yellow",
                padding=(1, 2),
                width=100,
                title_align="center"
            )
            
            console.print(panel)
            console.print()
    
    def generate_narrative_content(self, count: int = 3) -> List[Dict[str, Any]]:
        """
        Generate narrative content using the NarrativeEngine.
        
        Args:
            count: Number of narrative events to generate
            
        Returns:
            List of narrative event dictionaries
        """
        if not self.narrative_engine:
            return []
            
        # Generate daily narrative content
        events = self.narrative_engine.generate_daily_narrative()
        
        # Limit to the requested count
        events = events[:count]
        
        # Convert to dictionaries for display
        event_dicts = []
        for event in events:
            event_dict = {
                "title": event.metadata.get("title", event.event_type.capitalize()),
                "content": event.description,
                "type": event.event_type,
                "tags": event.tags
            }
            event_dicts.append(event_dict)
        
        return event_dicts
    
    def generate_daily_news(self) -> str:
        """
        Generate the daily news for Rome based on the current game state.
        
        Returns:
            A string containing the daily news
        """
        if not self.narrative_engine or not self.game_state:
            return "No news to report today."
            
        # Generate a daily event using the narrative engine
        events = self.narrative_engine.generate_targeted_narrative(["daily_event"], 1)
        
        # If we got an event from the narrative engine, use it
        if events:
            return events[0].description
        
        return "The day passes quietly in Rome."
    
    def generate_rumors(self) -> str:
        """
        Generate rumors and gossip circulating in Rome.
        
        Returns:
            A string containing rumors and gossip
        """
        if not self.narrative_engine or not self.game_state:
            return "No rumors circulating today."
            
        # Generate a rumor using the narrative engine
        events = self.narrative_engine.generate_targeted_narrative(["rumor"], 1)
        
        # If we got an event from the narrative engine, use it
        if events:
            return events[0].description
        
        return "The streets of Rome are unusually quiet with gossip today."