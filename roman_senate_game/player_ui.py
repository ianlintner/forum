#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Roman Senate AI Game
Player UI Module

This module handles the user interface elements specifically for player interactions.
It provides functions to display options to the player, capture player input,
and format text output for a consistent and immersive experience.
"""

import random
import sys
from typing import Dict, List, Optional, Tuple, Union, Any

from rich.panel import Panel
from rich.console import Console
from rich.text import Text
from rich.columns import Columns
from rich.prompt import Prompt, IntPrompt, Confirm
from rich.style import Style
from rich.box import Box, ROUNDED

import utils
from logging_utils import get_logger

# Initialize console and logger
console = utils.console if hasattr(utils, 'console') else Console()
logger = get_logger()

# Define UI color scheme for consistency
UI_COLORS = {
    "support": "green",
    "neutral": "yellow",
    "oppose": "red",
    "abstain": "dim",
    "speech": "cyan",
    "interjection": "magenta",
    "vote": "blue",
    "player": "bright_green",
    "error": "bright_red",
    "heading": "bright_cyan",
    "subheading": "cyan",
    "highlight": "bright_white",
    "preview": "dim"
}

def display_player_introduction(intro_text: str) -> None:
    """
    Displays the player's senator introduction in a formatted panel.
    
    Args:
        intro_text: Introductory text describing the player's senator
    """
    panel = Panel(
        Text(intro_text),
        title="[bold green]Your Senator[/]",
        border_style=UI_COLORS["player"],
        width=100,
        box=ROUNDED
    )
    
    console.print("\n")
    console.print(panel)
    console.print("\n[bold]Press Enter to continue...[/]", style=UI_COLORS["highlight"])
    input()  # Wait for user input before continuing

def present_speech_options(options: List[Dict], topic: str) -> Dict:
    """
    Displays speech options to the player and returns their choice.
    
    Args:
        options: List of dictionaries with speech options
                Each option should contain 'id', 'stance', 'summary' keys
        topic: The current debate topic
        
    Returns:
        Dict: The selected speech option
    """
    console.print(f"\n[bold {UI_COLORS['heading']}]SPEECH OPTIONS ON:[/] [italic]{topic}[/]")
    console.print("[bold]Choose how you will address the Senate:[/]")
    
    # Create panels for each option
    panels = []
    for i, option in enumerate(options, 1):
        stance = option.get('stance', 'neutral')
        stance_color = UI_COLORS.get(stance, UI_COLORS['neutral'])
        stance_label = stance.upper()
        
        option_preview = format_speech_preview(option)
        
        panel_content = Text()
        panel_content.append(f"[bold]{stance_label}[/]\n\n")
        panel_content.append(option_preview)
        
        panel = Panel(
            panel_content,
            title=f"[bold]Option {i}[/]",
            border_style=stance_color,
            width=45
        )
        panels.append(panel)
    
    # Add abstain option
    abstain_panel = Panel(
        "[italic]You choose not to speak on this matter.[/]",
        title="[bold]Abstain[/]",
        border_style=UI_COLORS['abstain'],
        width=45
    )
    panels.append(abstain_panel)
    
    # Display options in a grid layout (2 columns)
    column_pairs = []
    for i in range(0, len(panels), 2):
        row_panels = panels[i:i+2]
        if len(row_panels) == 1:
            # Add empty panel if odd number to maintain grid
            row_panels.append(Panel("", border_style="black", width=45))
        column_pairs.append(Columns(row_panels))
    
    for column_pair in column_pairs:
        console.print(column_pair)
    
    # Get user selection
    valid_choices = list(range(1, len(options) + 1))
    
    while True:
        choice_text = f"[{UI_COLORS['highlight']}]Enter choice (1-{len(options)}, or 0 to abstain):[/] "
        choice = _get_valid_input(choice_text, valid_choices + [0])
        
        if choice == 0:
            return {"action": "abstain"}
        else:
            return options[choice - 1]

def present_interjection_options(options: List[Dict], current_speaker: Dict) -> Dict:
    """
    Displays interjection options to the player when another senator is speaking.
    
    Args:
        options: List of dictionaries with interjection options
                Each option should contain 'id', 'type', 'preview', and 'impact' keys
        current_speaker: Information about the senator currently speaking
        
    Returns:
        Dict: The selected interjection option or abstain choice
    """
    console.print(f"\n[bold {UI_COLORS['heading']}]INTERJECTION OPTIONS[/]")
    console.print(f"[bold]Senator {current_speaker.get('name', 'Unknown')} is speaking. Do you wish to interject?[/]")
    
    # Create panels for each option
    panels = []
    for i, option in enumerate(options, 1):
        interjection_type = option.get('type', 'unknown')
        impact = option.get('impact', 'unknown')
        
        # Determine appropriate color based on interjection type
        if interjection_type == "acclamation":
            color = "green"
            type_text = "ACCLAIM"
        elif interjection_type == "objection":
            color = "red"
            type_text = "OBJECT"
        elif interjection_type == "procedural":
            color = "yellow"
            type_text = "POINT OF ORDER"
        elif interjection_type == "emotional":
            color = "magenta"
            type_text = "EMOTIONAL"
        else:
            color = "blue"
            type_text = "INTERJECT"
        
        panel_content = Text()
        panel_content.append(f"[bold {color}]{type_text}[/]\n\n")
        panel_content.append(option.get('preview', 'No preview available'))
        panel_content.append(f"\n\n[italic]Impact: {impact}[/]")
        
        panel = Panel(
            panel_content,
            title=f"[bold]Option {i}[/]",
            border_style=color,
            width=45
        )
        panels.append(panel)
    
    # Add remain silent option
    silent_panel = Panel(
        "[italic]You remain silent and let the speaker continue.[/]",
        title="[bold]Remain Silent[/]",
        border_style=UI_COLORS['abstain'],
        width=45
    )
    panels.append(silent_panel)
    
    # Display options in a grid layout (2 columns)
    column_pairs = []
    for i in range(0, len(panels), 2):
        row_panels = panels[i:i+2]
        if len(row_panels) == 1:
            row_panels.append(Panel("", border_style="black", width=45))
        column_pairs.append(Columns(row_panels))
    
    for column_pair in column_pairs:
        console.print(column_pair)
    
    # Get user selection
    valid_choices = list(range(1, len(options) + 1))
    
    while True:
        choice_text = f"[{UI_COLORS['highlight']}]Enter choice (1-{len(options)}, or 0 to remain silent):[/] "
        choice = _get_valid_input(choice_text, valid_choices + [0])
        
        if choice == 0:
            return {"action": "remain_silent"}
        else:
            return options[choice - 1]

def present_voting_options(topic: str) -> Dict:
    """
    Displays voting options to the player and returns their choice.
    
    Args:
        topic: The topic being voted on
        
    Returns:
        Dict: The selected vote option with stance and any additional info
    """
    console.print(f"\n[bold {UI_COLORS['heading']}]VOTING ON:[/] [italic]{topic}[/]")
    console.print("[bold]Cast your vote in this matter:[/]")
    
    # Create panels for each voting option
    support_panel = Panel(
        "[bold green]SUPPORT[/]\n\nVote in favor of this proposal.",
        title="[bold]Support[/]",
        border_style="green",
        width=32
    )
    
    oppose_panel = Panel(
        "[bold red]OPPOSE[/]\n\nVote against this proposal.",
        title="[bold]Oppose[/]",
        border_style="red", 
        width=32
    )
    
    abstain_panel = Panel(
        "[bold yellow]ABSTAIN[/]\n\nRefrain from voting on this matter.",
        title="[bold]Abstain[/]",
        border_style="yellow",
        width=32
    )
    
    # Display options in a row
    console.print(Columns([support_panel, oppose_panel, abstain_panel]))
    
    # Get user selection
    choice_text = f"[{UI_COLORS['highlight']}]Enter choice (1-Support, 2-Oppose, 3-Abstain):[/] "
    choice = _get_valid_input(choice_text, [1, 2, 3])
    
    if choice == 1:
        return {"stance": "support", "decision": "support"}
    elif choice == 2:
        return {"stance": "oppose", "decision": "oppose"}
    else:
        return {"stance": "neutral", "decision": "abstain"}

def format_speech_preview(speech_option: Dict) -> Text:
    """
    Creates a formatted preview of a speech option for display in UI.
    
    Args:
        speech_option: Dictionary containing speech option details
        
    Returns:
        Text: Formatted Rich Text object with the preview
    """
    preview = Text()
    
    # Add summary if available
    if 'summary' in speech_option:
        preview.append(speech_option['summary'] + "\n\n")
    
    # Add key points if available
    if 'key_points' in speech_option and speech_option['key_points']:
        preview.append("[bold]Key points:[/]\n")
        for point in speech_option['key_points']:
            preview.append(f"• {point}\n")
        preview.append("\n")
    
    # Add style/approach if available
    if 'style' in speech_option:
        preview.append(f"[italic]Style: {speech_option['style']}[/]\n")
    
    # Add rhetorical devices if available
    if 'rhetorical_devices' in speech_option and speech_option['rhetorical_devices']:
        devices = ", ".join(speech_option['rhetorical_devices'])
        preview.append(f"[italic]Rhetorical devices: {devices}[/]\n")
    
    return preview

def display_player_action_result(result: Dict, action_type: str) -> None:
    """
    Displays the result of a player's action in a formatted way.
    
    Args:
        result: Dictionary with the result details
        action_type: Type of action ("speech", "interjection", "vote")
    """
    # Choose title and color based on action type
    if action_type == "speech":
        title = "[bold]YOUR SPEECH[/]"
        color = UI_COLORS["speech"]
    elif action_type == "interjection":
        title = "[bold]YOUR INTERJECTION[/]"
        color = UI_COLORS["interjection"]
    elif action_type == "vote":
        title = "[bold]YOUR VOTE[/]"
        color = UI_COLORS["vote"]
    else:
        title = "[bold]ACTION RESULT[/]"
        color = UI_COLORS["highlight"]
    
    # Create content based on what's available in the result
    content = Text()
    
    # Handle text content
    if 'text' in result:
        content.append(result['text'] + "\n\n")
    elif 'content' in result:
        content.append(result['content'] + "\n\n")
    
    # Handle impacts/effects
    if 'effects' in result and result['effects']:
        content.append("[bold]Effects:[/]\n")
        for effect in result['effects']:
            content.append(f"• {effect}\n")
    
    # Handle reactions if available
    if 'reactions' in result and result['reactions']:
        content.append("\n[bold]Reactions:[/]\n")
        for reaction in result['reactions']:
            content.append(f"• {reaction}\n")
    
    # Create and display panel
    panel = Panel(
        content,
        title=title,
        border_style=color,
        width=100
    )
    
    console.print("\n")
    console.print(panel)

def display_error(message: str) -> None:
    """
    Displays an error message to the player.
    
    Args:
        message: The error message to display
    """
    console.print(f"[bold {UI_COLORS['error']}]ERROR:[/] {message}")

def _get_valid_input(prompt: str, valid_options: List[int]) -> int:
    """
    Helper function to get validated integer input from the user.
    
    Args:
        prompt: The prompt to display
        valid_options: List of valid integer options
        
    Returns:
        int: The validated user input
    """
    while True:
        try:
            console.print(prompt, end="")
            user_input = input().strip()
            
            # Handle empty input
            if not user_input:
                display_error(f"Please enter a number between {min(valid_options)} and {max(valid_options)}.")
                continue
                
            choice = int(user_input)
            if choice in valid_options:
                return choice
            else:
                display_error(f"Invalid option. Please enter a number between {min(valid_options)} and {max(valid_options)}.")
        except ValueError:
            display_error("Please enter a valid number.")

def confirm_action(prompt: str) -> bool:
    """
    Asks the player to confirm an action.
    
    Args:
        prompt: The confirmation prompt to display
        
    Returns:
        bool: True if confirmed, False otherwise
    """
    console.print(f"\n[bold]{prompt} (y/n)[/] ", end="")
    
    while True:
        response = input().strip().lower()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        else:
            display_error("Please enter 'y' or 'n'.")