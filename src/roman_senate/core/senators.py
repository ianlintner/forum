#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Roman Senate Game
Senators Module

This module handles the creation and management of senator characters
with distinct personalities, factions, and traits.
"""

import random
from typing import List, Dict, Optional
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
import time

console = Console()

# Senator factions
FACTIONS = ["Optimates", "Populares", "Military", "Religious", "Merchant"]

# Roman praenomina (first names)
ROMAN_FIRST_NAMES = [
    "Marcus", "Gaius", "Lucius", "Publius", "Quintus", 
    "Titus", "Gnaeus", "Aulus", "Decimus", "Servius"
]

# Roman nomina (family/clan names)
ROMAN_FAMILY_NAMES = [
    "Aurelius", "Julius", "Claudius", "Cornelius", "Flavius",
    "Valerius", "Tullius", "Antonius", "Calpurnius", "Domitius",
    "Fabius", "Licinius", "Marius", "Pompeius", "Sempronius"
]

# Roman cognomina (personal surnames)
ROMAN_COGNOMINA = [
    "Maximus", "Rufus", "Magnus", "Longus", "Crassus",
    "Cicero", "Caesar", "Scipio", "Cato", "Sulla",
    "Brutus", "Flaccus", "Pius", "Gallus", "Scaevola"
]


def initialize_senate(senator_count: int = 10) -> List[Dict]:
    """
    Initialize the senate with AI senators.
    
    Args:
        senator_count (int): Number of senators to create
        
    Returns:
        List[Dict]: List of senator dictionaries
    """
    console.print("\n[bold cyan]Initializing the Roman Senate...[/]")
    
    senators = []
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold green]Creating senator profiles...[/]"),
        console=console,
    ) as progress:
        task = progress.add_task("Working...", total=senator_count)
        
        for i in range(senator_count):
            # Generate unique name
            first_name = random.choice(ROMAN_FIRST_NAMES)
            family_name = random.choice(ROMAN_FAMILY_NAMES)
            
            # 50% chance to add a cognomen
            if random.random() < 0.5:
                cognomen = random.choice(ROMAN_COGNOMINA)
                full_name = f"{first_name} {family_name} {cognomen}"
            else:
                full_name = f"{first_name} {family_name}"
            
            # Randomly assign faction
            faction = random.choice(FACTIONS)
            
            # Generate personality traits with some variance based on faction
            traits = generate_traits_for_faction(faction)
            
            # Generate senator background
            background = generate_senator_background(faction, traits)
            
            # Create senator profile
            senator = {
                "id": i + 1,
                "name": full_name,
                "faction": faction,
                "influence": random.randint(1, 10),
                "traits": traits,
                "background": background
            }
            
            senators.append(senator)
            progress.update(task, advance=1)
            time.sleep(0.2)  # Simulated delay for effect
    
    console.print(
        "[bold green]✓[/] Senate initialized with [bold cyan]{}[/] senators.\n".format(
            len(senators)
        )
    )
    return senators


def generate_traits_for_faction(faction: str) -> Dict[str, float]:
    """
    Generate traits with some bias based on faction.
    
    Args:
        faction (str): Senator's faction
        
    Returns:
        Dict[str, float]: Dictionary of traits and their values
    """
    # Base traits with random values
    traits = {
        "eloquence": random.uniform(0.3, 0.8),  # Speaking ability
        "loyalty": random.uniform(0.3, 0.8),    # Faction loyalty
        "corruption": random.uniform(0.1, 0.7), # Corruptibility
        "ambition": random.uniform(0.4, 0.9),   # Personal ambition
        "traditionalism": random.uniform(0.3, 0.7)  # Respect for tradition
    }
    
    # Adjust traits based on faction tendencies
    if faction == "Optimates":
        traits["loyalty"] += 0.1
        traits["traditionalism"] += 0.2
        traits["corruption"] += 0.1  # Often corrupt to maintain power
    elif faction == "Populares":
        traits["eloquence"] += 0.1  # Good at speaking to crowds
        traits["ambition"] += 0.1
        traits["traditionalism"] -= 0.1
    elif faction == "Military":
        traits["loyalty"] += 0.1
        traits["corruption"] -= 0.1
        traits["ambition"] += 0.2
    elif faction == "Religious":
        traits["traditionalism"] += 0.2
        traits["corruption"] -= 0.1
        traits["loyalty"] += 0.1
    elif faction == "Merchant":
        traits["corruption"] += 0.1
        traits["eloquence"] += 0.1
        traits["ambition"] += 0.1
    
    # Ensure all values are between 0 and 1
    for trait in traits:
        traits[trait] = max(0.0, min(1.0, traits[trait]))
    
    return traits


def generate_senator_background(faction: str, traits: Dict[str, float]) -> str:
    """
    Generate a background story for a senator based on faction and traits.
    
    Args:
        faction (str): Senator's faction
        traits (Dict[str, float]): Senator's personality traits
        
    Returns:
        str: Background story
    """
    backgrounds = {
        "Optimates": [
            "Comes from one of Rome's oldest patrician families.",
            "A wealthy landowner with estates throughout Italy.",
            "Descended from a line of consuls dating back generations.",
            "Staunchly defends the traditional privileges of the Senate."
        ],
        "Populares": [
            "Rose from a modest plebeian background through political talent.",
            "Gained popularity by advocating for the common citizens.",
            "Built a power base by supporting agrarian reforms.",
            "Challenges the traditional power structure of Rome's elite families."
        ],
        "Military": [
            "Distinguished in campaigns against Gallic tribes.",
            "Veteran of the legions who earned citizenship through service.",
            "Former military tribune with connections to influential generals.",
            "Earned military decorations in the service of Rome."
        ],
        "Religious": [
            "Formerly a priest in the cult of Jupiter.",
            "Serves as a pontifex in Rome's religious hierarchy.",
            "Known for strict adherence to religious observances.",
            "Claims to have received divine omens guiding political decisions."
        ],
        "Merchant": [
            "Wealthy trader with businesses throughout the Mediterranean.",
            "Owns several shipping companies operating from Ostia.",
            "Made a fortune in the grain trade with Egypt.",
            "Represents the interests of Rome's growing commercial class."
        ]
    }
    
    # Select a background based on faction
    background = random.choice(backgrounds.get(faction, backgrounds["Optimates"]))
    
    # Add a trait-based characteristic
    trait_descriptions = []
    
    if traits["eloquence"] > 0.7:
        trait_descriptions.append("Known for moving speeches in the Senate.")
    elif traits["eloquence"] < 0.4:
        trait_descriptions.append("Prefers action to lengthy debates.")
        
    if traits["loyalty"] > 0.7:
        trait_descriptions.append(f"Steadfastly loyal to the {faction} faction.")
    elif traits["loyalty"] < 0.4:
        trait_descriptions.append("Known to shift political allegiances when convenient.")
        
    if traits["corruption"] > 0.7:
        trait_descriptions.append("Rumored to accept bribes for political favors.")
    elif traits["corruption"] < 0.3:
        trait_descriptions.append("Has a reputation for unusual honesty in politics.")
        
    if traits["ambition"] > 0.7:
        trait_descriptions.append("Openly ambitious about holding higher office.")
    
    if traits["traditionalism"] > 0.7:
        trait_descriptions.append("Staunchly defends the mos maiorum (ancestral customs).")
    elif traits["traditionalism"] < 0.3:
        trait_descriptions.append("Known for proposing reforms to Roman traditions.")
    
    # Add one or two trait descriptions if available
    if trait_descriptions:
        background += " " + random.choice(trait_descriptions)
        
        # 30% chance to add a second trait description
        if len(trait_descriptions) > 1 and random.random() < 0.3:
            remaining_traits = [t for t in trait_descriptions if t not in background]
            if remaining_traits:
                background += " " + random.choice(remaining_traits)
    
    return background


def get_senator_by_id(senators: List[Dict], senator_id: int) -> Optional[Dict]:
    """
    Find a senator by their ID.
    
    Args:
        senators (List[Dict]): List of senator dictionaries
        senator_id (int): ID of the senator to find
        
    Returns:
        Optional[Dict]: Senator dictionary or None if not found
    """
    for senator in senators:
        if senator.get("id") == senator_id:
            return senator
    return None


def get_senators_by_faction(senators: List[Dict], faction: str) -> List[Dict]:
    """
    Get all senators belonging to a specific faction.
    
    Args:
        senators (List[Dict]): List of senator dictionaries
        faction (str): Faction to filter by
        
    Returns:
        List[Dict]: List of senators in the specified faction
    """
    return [s for s in senators if s.get("faction") == faction]


def display_senators_info(senators: List[Dict]):
    """
    Display information about all senators.
    
    Args:
        senators (List[Dict]): List of senator dictionaries
    """
    from rich.table import Table
    
    console.print("\n[bold cyan]Roman Senate Membership[/]")

    # Group senators by faction
    factions = {}
    for senator in senators:
        faction = senator["faction"]
        if faction not in factions:
            factions[faction] = []
        factions[faction].append(senator)

    # Display senators by faction
    for faction, members in factions.items():
        console.print(f"\n[bold]{faction} Faction[/] ({len(members)} members)")

        table = Table(show_header=True)
        table.add_column("Name", style="cyan")
        table.add_column("Influence", justify="center")
        table.add_column("Traits")
        table.add_column("Background", style="dim")

        for senator in members:
            traits_str = ", ".join(
                [f"{k}: {v:.1f}" for k, v in senator["traits"].items()]
            )
            table.add_row(
                senator["name"], 
                str(senator["influence"]), 
                traits_str,
                senator.get("background", "")
            )

        console.print(table)