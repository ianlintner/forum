#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Roman Senate AI Game
Player UI Module

This module provides user interface for player interactions.
"""

import logging
from typing import Dict, List, Any, Optional, Union, Tuple
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.columns import Columns
from rich.text import Text
from rich.box import ROUNDED, HEAVY_EDGE

from .player import Player

logger = logging.getLogger(__name__)
console = Console()

class PlayerUI:
    """User interface for player interactions."""
    
    def __init__(self, player: Optional[Player] = None):
        """
        Initialize the Player UI.
        
        Args:
            player: Optional Player instance to associate with this UI
        """
        self.player = player
        self.console = console
        logger.info("PlayerUI initialized")
    
    def set_player(self, player: Player):
        """
        Set the player associated with this UI.
        
        Args:
            player: The Player instance
        """
        self.player = player
        logger.debug(f"PlayerUI now associated with player: {player.name}")
    
    def display_welcome(self):
        """Display the welcome screen."""
        self.console.print()
        self.console.print(Panel(
            "[bold yellow]ROMAN SENATE[/bold yellow]\n\n"
            "[bold]Welcome to the political arena of Ancient Rome![/bold]\n\n"
            "Navigate the treacherous politics of the late Republic era as you "
            "debate, negotiate, and scheme your way to power and influence.\n\n"
            "[dim]Developed as part of the Roman Senate AI Game[/dim]",
            title="[bold]AVE SENATOR![/bold]",
            border_style="red",
            expand=False,
            width=80,
            box=HEAVY_EDGE
        ))
        self.console.print()
    
    def display_player_status(self):
        """Display the player's current status."""
        if self.player is None:
            self.console.print("[yellow]No player data available.[/yellow]")
            return
        
        # Create main player info panel
        player_table = Table(show_header=False, box=ROUNDED, border_style="blue")
        player_table.add_column("Attribute", style="cyan")
        player_table.add_column("Value", style="white")
        
        player_table.add_row("Name", f"[bold]{self.player.name}[/bold]")
        player_table.add_row("Faction", f"[bold]{self.player.faction}[/bold]")
        player_table.add_row("Ancestry", self.player.ancestry)
        player_table.add_row("Background", self.player.background)
        if self.player.current_office:
            player_table.add_row("Current Office", f"[bold green]{self.player.current_office}[/bold green]")
        
        # Create stats panel
        stats_table = Table(show_header=False, box=ROUNDED, border_style="blue")
        stats_table.add_column("Stat", style="cyan")
        stats_table.add_column("Value", style="white")
        
        # Wealth with color coding
        wealth_value = self.player.wealth
        wealth_color = "green" if wealth_value > 150 else "yellow" if wealth_value > 75 else "red"
        stats_table.add_row("Wealth", f"[{wealth_color}]{wealth_value}/200[/{wealth_color}]")
        
        # Influence with color coding
        influence_value = self.player.influence
        influence_color = "green" if influence_value > 75 else "yellow" if influence_value > 40 else "red"
        stats_table.add_row("Influence", f"[{influence_color}]{influence_value}/100[/{influence_color}]")
        
        # Reputation with color coding
        reputation_value = self.player.reputation
        reputation_color = "green" if reputation_value > 75 else "yellow" if reputation_value > 40 else "red"
        stats_table.add_row("Reputation", f"[{reputation_color}]{reputation_value}/100[/{reputation_color}]")
        
        stats_table.add_row("Political Capital", f"[magenta]{self.player.political_capital}[/magenta]")
        
        # Create skills panel
        skills_table = Table(show_header=False, box=ROUNDED, border_style="blue")
        skills_table.add_column("Skill", style="cyan")
        skills_table.add_column("Level", style="white")
        
        for skill, level in self.player.skills.items():
            skill_name = skill.capitalize()
            skill_bar = "•" * level + "◦" * (10 - level)
            skills_table.add_row(skill_name, f"{skill_bar} ({level}/10)")
        
        # Layout the panels
        self.console.print()
        self.console.print(Panel(player_table, title="[bold]Player Information[/bold]", border_style="blue"))
        self.console.print()
        
        # Display stats and skills side by side
        self.console.print(Columns([
            Panel(stats_table, title="[bold]Status[/bold]", border_style="blue", width=40),
            Panel(skills_table, title="[bold]Skills[/bold]", border_style="blue", width=40)
        ]))
        
        # Display special abilities if any
        if self.player.special_abilities:
            abilities_table = Table(show_header=True, box=ROUNDED, border_style="magenta")
            abilities_table.add_column("Ability", style="magenta bold")
            abilities_table.add_column("Description", style="white")
            abilities_table.add_column("Effect", style="green")
            
            for ability in self.player.special_abilities:
                abilities_table.add_row(
                    ability["name"],
                    ability["description"],
                    ability["effect"]
                )
            
            self.console.print()
            self.console.print(Panel(abilities_table, title="[bold]Special Abilities[/bold]", border_style="magenta"))
    
    def display_relationship_status(self, senators: Dict[str, Any]):
        """
        Display the player's relationships with other senators.
        
        Args:
            senators: Dictionary of senator data keyed by senator_id
        """
        if self.player is None or not self.player.relationships:
            self.console.print("[yellow]No relationship data available.[/yellow]")
            return
        
        relationships_table = Table(show_header=True, box=ROUNDED)
        relationships_table.add_column("Senator", style="cyan")
        relationships_table.add_column("Faction", style="white")
        relationships_table.add_column("Relationship", style="white")
        relationships_table.add_column("Status", style="white")
        
        for senator_id, relationship_score in self.player.relationships.items():
            # Skip if we don't have this senator in our data
            if senator_id not in senators:
                continue
                
            senator = senators[senator_id]
            name = senator.get("name", "Unknown")
            faction = senator.get("faction", "Unknown")
            
            # Determine relationship status text and color
            if relationship_score >= 80:
                status_text = "Strong Ally"
                status_color = "green"
            elif relationship_score >= 60:
                status_text = "Ally"
                status_color = "green3"
            elif relationship_score >= 45:
                status_text = "Friendly"
                status_color = "green_yellow"
            elif relationship_score >= 35:
                status_text = "Neutral"
                status_color = "yellow"
            elif relationship_score >= 20:
                status_text = "Unfriendly"
                status_color = "orange3"
            else:
                status_text = "Hostile"
                status_color = "red"
                
            # Create a visual representation of the relationship
            relationship_bar = "█" * (relationship_score // 10)
            relationship_bar = f"[{status_color}]{relationship_bar}[/{status_color}]"
            
            relationships_table.add_row(
                name,
                faction,
                relationship_bar,
                f"[{status_color}]{status_text}[/{status_color}]"
            )
        
        self.console.print()
        self.console.print(Panel(
            relationships_table,
            title="[bold]Your Relationships[/bold]",
            border_style="blue"
        ))
    
    def display_speech_options(
        self,
        topic: str,
        options: List[Dict[str, str]]
    ) -> int:
        """
        Display speech options and get player choice.
        
        Args:
            topic: The current debate topic
            options: List of speech option dictionaries with:
                     - 'id': Option identifier
                     - 'title': Option title
                     - 'description': Option description
                     - 'effect': Effect description
                     
        Returns:
            Index of the selected option
        """
        self.console.print()
        self.console.print(Panel(
            f"[bold]{topic}[/bold]",
            title="[bold]Current Debate Topic[/bold]",
            border_style="yellow"
        ))
        
        self.console.print("\n[bold cyan]Choose Your Approach:[/bold cyan]")
        
        # Display each option
        for i, option in enumerate(options, 1):
            self.console.print(Panel(
                f"[bold]{option['title']}[/bold]\n\n"
                f"{option['description']}\n\n"
                f"[dim]Effect: {option['effect']}[/dim]",
                title=f"[bold]Option {i}[/bold]",
                border_style="blue",
                width=80
            ))
            self.console.print()
        
        # Get player choice
        choice = 0
        while choice < 1 or choice > len(options):
            try:
                choice = IntPrompt.ask(
                    "Enter your choice [bold cyan](1-" + str(len(options)) + ")[/bold cyan]",
                    console=self.console
                )
                if choice < 1 or choice > len(options):
                    self.console.print("[bold red]Invalid choice. Please try again.[/bold red]")
            except (ValueError, KeyboardInterrupt):
                self.console.print("[bold red]Invalid input. Please enter a number.[/bold red]")
        
        # Return the zero-based index
        return choice - 1
    
    def display_interjection_options(
        self,
        speaker: str,
        speech_segment: str,
        options: List[Dict[str, str]]
    ) -> int:
        """
        Display interjection options and get player choice.
        
        Args:
            speaker: Name of the current speaker
            speech_segment: The speech segment to interject on
            options: List of interjection option dictionaries with:
                     - 'id': Option identifier
                     - 'title': Option title
                     - 'description': Option description
                     - 'cost': Political capital cost
                     - 'effect': Effect description
                     
        Returns:
            Index of the selected option (0 for none)
        """
        self.console.print()
        self.console.print(Panel(
            f"[italic]{speech_segment}[/italic]",
            title=f"[bold]{speaker} is speaking...[/bold]",
            border_style="yellow"
        ))
        
        self.console.print("\n[bold cyan]Interjection Options:[/bold cyan]")
        self.console.print("[dim](You have [magenta]" + str(self.player.political_capital) + "[/magenta] political capital)[/dim]")
        
        # Option 0 is always "Continue listening"
        self.console.print(Panel(
            "Continue listening without interjecting",
            title=f"[bold]Option 0[/bold]",
            border_style="green",
            width=80
        ))
        
        # Display each interjection option
        for i, option in enumerate(options, 1):
            cost = option.get('cost', 0)
            cost_str = f"[bold red]Cost: {cost} political capital[/bold red]"
            
            self.console.print(Panel(
                f"[bold]{option['title']}[/bold]\n\n"
                f"{option['description']}\n\n"
                f"{cost_str}\n"
                f"[dim]Effect: {option['effect']}[/dim]",
                title=f"[bold]Option {i}[/bold]",
                border_style="blue" if self.player.political_capital >= cost else "red",
                width=80
            ))
        
        # Get player choice
        max_choice = len(options)
        choice = -1
        while choice < 0 or choice > max_choice:
            try:
                choice = IntPrompt.ask(
                    "Enter your choice [bold cyan](0-" + str(max_choice) + ")[/bold cyan]",
                    console=self.console
                )
                
                if choice < 0 or choice > max_choice:
                    self.console.print("[bold red]Invalid choice. Please try again.[/bold red]")
                elif choice > 0:
                    # Check if player has enough political capital
                    cost = options[choice-1].get('cost', 0)
                    if self.player.political_capital < cost:
                        self.console.print(
                            f"[bold red]Not enough political capital. You need {cost} but have "
                            f"only {self.player.political_capital}.[/bold red]"
                        )
                        choice = -1  # Reset choice to ask again
            except (ValueError, KeyboardInterrupt):
                self.console.print("[bold red]Invalid input. Please enter a number.[/bold red]")
        
        # Return the selected option (0 for none, otherwise index in options list)
        return choice - 1 if choice > 0 else -1
    
    def display_vote_options(self, proposal: str, context: Dict[str, Any]) -> str:
        """
        Display voting options and get player's vote.
        
        Args:
            proposal: The proposal being voted on
            context: Additional context for the vote
            
        Returns:
            The player's vote: "aye", "nay", or "abstain"
        """
        self.console.print()
        self.console.print(Panel(
            f"[bold]{proposal}[/bold]",
            title="[bold]Vote on Proposal[/bold]",
            border_style="yellow"
        ))
        
        # Display any relevant context
        if context.get('description'):
            self.console.print(Panel(
                context.get('description'),
                title="[bold]Background[/bold]",
                border_style="blue"
            ))
        
        # Display voting options
        vote_table = Table(show_header=True, box=ROUNDED)
        vote_table.add_column("Option", style="cyan bold")
        vote_table.add_column("Description", style="white")
        
        vote_table.add_row(
            "Aye (Y)",
            "Vote in favor of the proposal"
        )
        vote_table.add_row(
            "Nay (N)",
            "Vote against the proposal"
        )
        vote_table.add_row(
            "Abstain (A)",
            "Abstain from voting"
        )
        
        self.console.print(vote_table)
        
        # Get player's vote
        valid_votes = {
            'y': 'aye',
            'n': 'nay',
            'a': 'abstain',
            'aye': 'aye',
            'nay': 'nay',
            'abstain': 'abstain'
        }
        
        vote = None
        while vote not in valid_votes:
            vote = Prompt.ask(
                "Enter your vote",
                choices=list(valid_votes.keys()),
                default="a"
            ).lower()
        
        return valid_votes[vote]
    
    def display_political_action_menu(self, actions: List[Dict[str, Any]]) -> int:
        """
        Display available political actions and get player choice.
        
        Args:
            actions: List of action dictionaries with:
                     - 'id': Action identifier
                     - 'name': Action name
                     - 'description': Action description
                     - 'cost': Cost dictionary (can include wealth, influence, etc.)
                     - 'requirements': Requirements dictionary
                     - 'available': Whether the action is available
                     
        Returns:
            Index of the selected action or -1 for cancel
        """
        self.console.print()
        self.console.print(Panel(
            "Choose an action to influence Senate politics",
            title="[bold]Political Actions[/bold]",
            border_style="magenta"
        ))
        
        # Display each action
        for i, action in enumerate(actions, 1):
            # Check if action is available
            available = action.get('available', True)
            
            # Format costs
            costs = action.get('cost', {})
            cost_strings = []
            for resource, amount in costs.items():
                resource_name = resource.capitalize()
                cost_strings.append(f"{resource_name}: {amount}")
                
            cost_display = ", ".join(cost_strings) if cost_strings else "No cost"
            
            # Create requirements text
            requirements = action.get('requirements', {})
            req_strings = []
            for req, value in requirements.items():
                req_strings.append(f"{req.capitalize()}: {value}")
                
            req_display = ", ".join(req_strings) if req_strings else "None"
            
            # Set appropriate style based on availability
            border_style = "blue" if available else "red"
            
            self.console.print(Panel(
                f"[bold]{action['name']}[/bold]\n\n"
                f"{action['description']}\n\n"
                f"[bold cyan]Cost:[/bold cyan] {cost_display}\n"
                f"[bold cyan]Requirements:[/bold cyan] {req_display}",
                title=f"[bold]Option {i}[/bold]",
                border_style=border_style,
                width=80
            ))
        
        # Add cancel option
        self.console.print(Panel(
            "Return to previous menu",
            title=f"[bold]Cancel (0)[/bold]",
            border_style="green",
            width=80
        ))
        
        # Get player choice
        choice = -1
        max_choice = len(actions)
        while choice < 0 or choice > max_choice:
            try:
                choice = IntPrompt.ask(
                    "Enter your choice [bold cyan](0-" + str(max_choice) + ")[/bold cyan]",
                    console=self.console
                )
                
                if choice < 0 or choice > max_choice:
                    self.console.print("[bold red]Invalid choice. Please try again.[/bold red]")
                elif choice > 0 and not actions[choice-1].get('available', True):
                    self.console.print("[bold red]This action is not available to you.[/bold red]")
                    choice = -1  # Reset choice to ask again
            except (ValueError, KeyboardInterrupt):
                self.console.print("[bold red]Invalid input. Please enter a number.[/bold red]")
        
        # Return the index (0-based) of the selected action or -1 for cancel
        return choice - 1 if choice > 0 else -1
    
    def display_loading(self, message: str = "Processing..."):
        """
        Display a loading spinner with a message.
        
        Args:
            message: The message to display
            
        Returns:
            A Progress context manager that can be used in a with statement
        """
        return Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            console=self.console
        )
    
    def prompt_for_name(self) -> str:
        """
        Prompt the player for their character name.
        
        Returns:
            The entered name
        """
        self.console.print()
        self.console.print(Panel(
            "What name shall you be known by in the Senate?",
            title="[bold]Your Identity[/bold]",
            border_style="blue"
        ))
        
        name = ""
        while not name:
            name = Prompt.ask("Enter your Roman name")
            if not name:
                self.console.print("[bold red]You must enter a name.[/bold red]")
        
        return name
    
    def prompt_for_faction(self) -> str:
        """
        Prompt the player for their faction allegiance.
        
        Returns:
            The selected faction
        """
        self.console.print()
        self.console.print(Panel(
            "[bold]Populares:[/bold] Champions of the common people. Seek reforms to benefit the masses.\n\n"
            "[bold]Optimates:[/bold] Traditionalists who support the aristocracy. Seek to preserve the power of the Senate.",
            title="[bold]Choose Your Faction[/bold]",
            border_style="blue"
        ))
        
        faction = Prompt.ask(
            "Choose your faction",
            choices=["Populares", "Optimates"],
            default="Populares"
        )
        
        return faction
    
    def prompt_for_background(self) -> Tuple[str, str]:
        """
        Prompt the player for their character background.
        
        Returns:
            Tuple of (ancestry, background)
        """
        self.console.print()
        self.console.print(Panel(
            "[bold]Patrician:[/bold] Born to one of Rome's ancient noble families. Higher starting influence and wealth.\n\n"
            "[bold]Plebeian:[/bold] Not born to the aristocracy. Higher starting reputation with common people.",
            title="[bold]Choose Your Ancestry[/bold]",
            border_style="blue"
        ))
        
        ancestry = Prompt.ask(
            "Choose your ancestry",
            choices=["Patrician", "Plebeian"],
            default="Plebeian"
        )
        
        # Different background options based on ancestry
        backgrounds = {
            "Patrician": [
                "Ancient Family (Old aristocracy, respected but somewhat out of touch)",
                "Military Heritage (Family known for military service)",
                "Wealthy Merchants (New money, not as respected but very wealthy)"
            ],
            "Plebeian": [
                "Novus Homo (Self-made, first of family to enter politics)",
                "Military Veteran (Rose through the ranks of the legions)",
                "Successful Merchant (Built wealth through trade)"
            ]
        }
        
        self.console.print()
        self.console.print(Panel(
            "\n".join(f"[bold]{i+1}.[/bold] {bg}" for i, bg in enumerate(backgrounds[ancestry])),
            title=f"[bold]Choose Your Background ({ancestry})[/bold]",
            border_style="blue"
        ))
        
        bg_index = 0
        while bg_index < 1 or bg_index > len(backgrounds[ancestry]):
            try:
                bg_index = IntPrompt.ask(
                    f"Choose your background (1-{len(backgrounds[ancestry])})",
                    console=self.console
                )
                if bg_index < 1 or bg_index > len(backgrounds[ancestry]):
                    self.console.print("[bold red]Invalid choice. Please try again.[/bold red]")
            except (ValueError, KeyboardInterrupt):
                self.console.print("[bold red]Invalid input. Please enter a number.[/bold red]")
                
        background = backgrounds[ancestry][bg_index-1]
        
        return ancestry, background
    
    def confirm_character(self, character_data: Dict[str, Any]) -> bool:
        """
        Display character summary and confirm with player.
        
        Args:
            character_data: Dictionary with character creation data
            
        Returns:
            True if confirmed, False to recreate
        """
        self.console.print()
        self.console.print(Panel(
            f"[bold]Name:[/bold] {character_data['name']}\n"
            f"[bold]Faction:[/bold] {character_data['faction']}\n"
            f"[bold]Ancestry:[/bold] {character_data['ancestry']}\n"
            f"[bold]Background:[/bold] {character_data['background']}\n\n"
            f"[bold]Starting Attributes:[/bold]\n"
            f"  Wealth: {character_data['wealth']}\n"
            f"  Influence: {character_data['influence']}\n"
            f"  Reputation: {character_data['reputation']}",
            title="[bold]Character Summary[/bold]",
            border_style="blue"
        ))
        
        return Confirm.ask("Confirm this character?", default=True)