"""
Roman Senate AI Game
Story Crier Agent Module

This module defines the town crier agent that announces historical events
and provides context at the start of each day in the simulation.
"""

import random
from typing import Dict, List, Optional, Any
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from ..core.historical_events import get_announcements_for_current_date, historical_events_db
from ..utils.llm.base import LLMProvider

console = Console()

class StoryCrierAgent:
    """
    Agent implementation of a Roman town crier who announces historical events.
    
    The StoryCrierAgent retrieves relevant historical events from the database
    based on the current date in the simulation and creates announcements for them.
    These announcements provide historical context and flavor to the simulation.
    """
    
    def __init__(self, llm_provider: Optional[LLMProvider] = None):
        """
        Initialize a story crier agent.
        
        Args:
            llm_provider: Optional LLM provider for enhanced announcements
        """
        self.llm_provider = llm_provider
        self.announcements_cache = {}  # Cache announcements by date
        
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