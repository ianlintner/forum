#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Roman Senate AI Game
Player Manager Module

This module handles player senator selection, tracking, and interaction.
It manages which senator is controlled by the player and provides
functions to interact with and track the player's senator.
"""

import random
import time
from typing import Dict, List, Optional, Any
from rich.console import Console
from rich.panel import Panel
import utils

console = utils.console if hasattr(utils, 'console') else Console()

# Global variable to track the player's senator ID
player_senator_id = None

# Player interaction history
# Format: List of {"timestamp": time, "type": str, "details": Dict}
player_interaction_history = []

# Player progress and state
player_state = {
    "game_progress": 0.0,  # 0.0 to 1.0 indicating progress through the game
    "reputation": 0.5,     # 0.0 to 1.0 indicating senator's reputation
    "influence": 0.5,      # 0.0 to 1.0 indicating political influence
    "achievements": [],    # List of achievements unlocked
    "completed_debates": 0, # Number of debates participated in
    "successful_votes": 0,  # Number of successful vote outcomes
    "notes": {},           # Custom notes/reminders for the player
}


def initialize_player_senator(senators: List[Dict]) -> Dict:
    """
    Randomly selects a senator to be controlled by the player.
    
    Args:
        senators: List of senator dictionaries
        
    Returns:
        Dict: The selected player senator
    """
    global player_senator_id
    
    if not senators:
        console.print("[bold red]Error: No senators available to assign to player[/]")
        return {}
    
    # Select a random senator for the player
    player_senator = random.choice(senators)
    player_senator_id = player_senator.get("id", 0)
    
    # Mark this senator as player-controlled
    player_senator["is_player"] = True
    
    # Log the selection
    _log_interaction("senator_selected", {
        "senator_id": player_senator_id,
        "senator_name": player_senator.get("name", "Unknown"),
        "faction": player_senator.get("faction", "Unknown"),
    })
    
    # Display information about the player's senator
    display_player_senator_info(player_senator)
    
    return player_senator


def get_player_senator(senators: List[Dict]) -> Optional[Dict]:
    """
    Returns the player-controlled senator from a list of senators.
    
    Args:
        senators: List of senator dictionaries
        
    Returns:
        Dict or None: The player's senator or None if not found
    """
    global player_senator_id
    
    if player_senator_id is None:
        return None
    
    # Search for the player's senator in the list
    for senator in senators:
        if senator.get("id") == player_senator_id or senator.get("is_player", False):
            return senator
    
    # If not found, return None
    return None


def is_player_senator(senator: Dict) -> bool:
    """
    Checks if a senator is controlled by the player.
    
    Args:
        senator: Senator dictionary
        
    Returns:
        bool: True if the senator is controlled by the player
    """
    global player_senator_id
    
    if player_senator_id is None:
        return False
    
    return senator.get("id") == player_senator_id or senator.get("is_player", False)


def generate_player_introduction(senator: Dict) -> str:
    """
    Creates a brief introduction for the player's senator.
    
    Args:
        senator: Senator dictionary
        
    Returns:
        str: Introduction text for the player's senator
    """
    name = senator.get("name", "Unknown Senator")
    faction = senator.get("faction", "Unknown Faction")
    
    # Get senator traits with safe access
    traits = senator.get("traits", {}) or {}
    eloquence = traits.get("eloquence", 0.5)
    corruption = traits.get("corruption", 0.2)
    loyalty = traits.get("loyalty", 0.7)
    
    # Create trait descriptions
    trait_descriptions = []
    if eloquence > 0.7:
        trait_descriptions.append("eloquent speaker")
    elif eloquence < 0.3:
        trait_descriptions.append("plain speaker")
    
    if corruption > 0.7:
        trait_descriptions.append("politically pragmatic")
    elif corruption < 0.3:
        trait_descriptions.append("principled")
    
    if loyalty > 0.7:
        trait_descriptions.append("deeply loyal to your faction")
    elif loyalty < 0.3:
        trait_descriptions.append("independent-minded")
    
    # Join traits with commas and 'and'
    traits_text = ""
    if trait_descriptions:
        if len(trait_descriptions) == 1:
            traits_text = f"You are known as a {trait_descriptions[0]}."
        else:
            traits_text = f"You are known as a {', '.join(trait_descriptions[:-1])} and {trait_descriptions[-1]}."
    
    # Generate faction-specific context
    faction_context = {
        "Optimates": "Your faction represents the traditional aristocracy, favoring the Senate's authority and resisting popular reforms.",
        "Populares": "Your faction advocates for the common people, supporting land reform and greater political rights for plebeians.",
        "Military": "Your faction prioritizes Rome's military strength and expansion, supporting generals and campaigns.",
        "Religious": "Your faction emphasizes religious tradition and the role of omens and augury in political decisions.",
        "Merchant": "Your faction represents commercial interests, advocating for trade policies and economic growth."
    }.get(faction, "Your faction plays a significant role in the Senate's politics.")
    
    # Combine all elements into an introduction
    introduction = f"""
You are {name}, a distinguished Senator of the {faction} faction.
{traits_text}
{faction_context}

As a Roman Senator, you will participate in debates, forge alliances, and vote on crucial matters
affecting the Republic. Your decisions will influence Rome's future and your own political career.
    """
    
    return introduction.strip()


def display_player_senator_info(senator: Dict):
    """
    Displays detailed information about the player's senator.
    
    Args:
        senator: Senator dictionary
    """
    name = senator.get("name", "Unknown Senator")
    faction = senator.get("faction", "Unknown Faction")
    
    # Get traits with safe access
    traits = senator.get("traits", {}) or {}
    
    # Format trait values
    trait_values = []
    for trait_name, trait_value in traits.items():
        if trait_value is not None:
            value_display = f"{trait_value:.1f}" if isinstance(trait_value, float) else f"{trait_value}"
            trait_values.append(f"{trait_name.capitalize()}: {value_display}")
    
    # Create the introduction text
    introduction = generate_player_introduction(senator)
    
    # Create and display a panel with the senator information
    panel_content = f"[bold]{name}[/] ([italic]{faction}[/])\n\n"
    
    if trait_values:
        panel_content += "[underline]Traits:[/]\n"
        panel_content += "\n".join(f"• {trait}" for trait in trait_values)
        panel_content += "\n\n"
    
    panel_content += introduction
    
    console.print(
        Panel(
            panel_content,
            title="[bold green]Your Senator[/]",
            border_style="green",
            width=100,
        )
    )


def update_player_interaction_history(senator: Dict, interaction_type: str, details: Dict):
    """
    Tracks player actions and interactions.
    
    Args:
        senator: Senator dictionary
        interaction_type: Type of interaction (e.g., 'speech', 'vote', 'alliance')
        details: Additional details about the interaction
    """
    if not is_player_senator(senator):
        return
    
    _log_interaction(interaction_type, details)
    
    # Update player state based on interaction type
    if interaction_type == "debate_participation":
        player_state["completed_debates"] += 1
    elif interaction_type == "vote_success":
        player_state["successful_votes"] += 1
    elif interaction_type == "reputation_change":
        delta = details.get("delta", 0)
        player_state["reputation"] = max(0.0, min(1.0, player_state["reputation"] + delta))
    elif interaction_type == "influence_change":
        delta = details.get("delta", 0)
        player_state["influence"] = max(0.0, min(1.0, player_state["influence"] + delta))


def get_player_state() -> Dict:
    """
    Returns the current state of the player's progress.
    
    Returns:
        Dict: Player state dictionary
    """
    return player_state


def get_player_interaction_history() -> List[Dict]:
    """
    Returns the history of player interactions.
    
    Returns:
        List[Dict]: List of interaction records
    """
    return player_interaction_history


def add_player_note(key: str, note: Any):
    """
    Adds a note or reminder for the player.
    
    Args:
        key: Note identifier
        note: Note content (can be any type)
    """
    player_state["notes"][key] = note


def get_player_note(key: str) -> Any:
    """
    Retrieves a player note by key.
    
    Args:
        key: Note identifier
        
    Returns:
        Any: Note content or None if not found
    """
    return player_state["notes"].get(key)


def _log_interaction(interaction_type: str, details: Dict):
    """
    Internal function to log player interactions.
    
    Args:
        interaction_type: Type of interaction
        details: Interaction details
    """
    global player_interaction_history
    
    # Record the interaction with timestamp
    interaction_record = {
        "timestamp": time.time(),
        "type": interaction_type,
        "details": details
    }
    
    player_interaction_history.append(interaction_record)