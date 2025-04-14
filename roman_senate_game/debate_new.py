#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Roman Senate AI Game
Debate Module

This module handles the debate mechanics of the Roman Senate simulation.
It manages the flow of arguments, rebuttals, and procedural rules
during senate deliberations.
"""

import random
import time
from typing import Dict, List, Optional, Tuple, Any
from collections import defaultdict
from rich.panel import Panel
from rich.text import Text
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
import utils

console = utils.console

def conduct_debate(topic: str, senators_list: List[Dict], rounds: int = 3, topic_category: str = None):
    """
    Conduct a debate on the given topic with interactive responses between senators.
    
    Args:
        topic (str): The topic to debate
        senators_list (List[Dict]): List of senators participating
        rounds (int): Number of debate rounds
        topic_category (str, optional): Category of the topic (e.g., Military funding)
    """
    # Reset debate state for a new debate
    reset_debate_state()
    
    # Handle case where topic might be None
    topic_display = topic if topic else "Unknown Topic"
    
    # Create a more informative debate introduction
    if topic_category:
        introduction = f"The Senate will now debate on a matter of [bold yellow]{topic_category}[/]:\n[italic]{topic_display}[/]"
    else:
        introduction = f"The Senate will now debate:\n[italic]{topic_display}[/]"
    
    # Display the debate panel with category context
    console.print(Panel(introduction, title="[bold cyan]SENATE DEBATE BEGINS[/]", border_style="cyan", width=100))

    debate_summary = []
    
    # Track which senators have already responded to which others to prevent loops
    responded_pairs = set()  # (responder_id, target_id) pairs
    
    # Generate faction stances for consistency
    faction_stances = {
        "Optimates": random.choice(["oppose", "oppose", "neutral"]),
        "Populares": random.choice(["support", "support", "neutral"]),
        "Military": random.choice(["support", "oppose", "neutral"]),
        "Religious": random.choice(["oppose", "neutral", "support"]),
        "Merchant": random.choice(["support", "neutral", "oppose"])
    }

    # Keep track of all previous speeches for context
    previous_speeches = []
    
    for round_num in range(1, rounds + 1):
        console.print(f"\n[bold blue]Round {round_num} of Debate[/]")

        # Select speakers for this round
        speakers = random.sample(senators_list, min(3, len(senators_list)))

        # Process each speaker sequentially
        for senator in speakers:
            thought_text = f"[bold]{senator['name']} ({senator['faction']}) is preparing to speak...[/]"
            console.print(thought_text)
            
            # Determine if this senator should respond to a previous speaker
            responding_to = None
            if previous_speeches and (round_num > 1 or len(previous_speeches) >= 2):
                for prev_speech in reversed(previous_speeches):  # Check most recent first
                    prev_senator_id = prev_speech.get("senator_id")
                    current_senator_id = senator.get("id")
                    
                    # Skip if they've already responded to each other
                    if prev_senator_id and current_senator_id:
                        pair = (current_senator_id, prev_senator_id)
                        if pair in responded_pairs:
                            continue
                    
                    # Calculate response probability based on stance agreement/disagreement
                    response_chance = 0.2  # Base chance
                    
                    if prev_speech.get("faction") == senator.get("faction"):
                        response_chance += 0.1  # More likely to respond to same faction
                    
                    # Strongly agree/disagree increases chance to respond
                    if prev_speech.get("stance") == senator.get("faction"):
                        response_chance += 0.2  # Same stance, more likely to support
                    elif prev_speech.get("stance") != senator.get("faction") and prev_speech.get("stance") != "neutral":
                        response_chance += 0.3  # Opposing stance, more likely to rebut
                    
                    # Check if random chance triggers a response
                    if random.random() < response_chance:
                        responding_to = prev_speech
                        
                        # Record that this senator has responded to prevent loops
                        if prev_senator_id and current_senator_id:
                            responded_pairs.add((current_senator_id, prev_senator_id))
                        break

            # Generate senator's speech
            speech = generate_speech(
                senator,
                topic,
                faction_stances,
                game_state.year,
                responding_to=responding_to,
                previous_speeches=previous_speeches
            )
            
            # Display the speech
            display_speech(senator, speech, topic)
            
            # Add to debate summary and previous speeches
            debate_summary.append(speech)
            previous_speeches.append(speech)
            
            # Pause for readability
            time.sleep(1)

    console.print("\n[bold green]✓[/] Debate concluded.\n")
    return debate_summary