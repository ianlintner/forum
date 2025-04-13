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
from typing import Dict, List
from rich.panel import Panel
from rich.text import Text
from rich.console import Console
import utils

console = utils.console

def generate_speech(senator: Dict, topic: str, faction_stance: Dict = None) -> Dict:
    """
    Generate an AI-powered speech for a senator based on their identity and the debate topic.
    
    Args:
        senator (Dict): The senator data including name, faction, and traits
        topic (str): The current debate topic
        faction_stance (Dict, optional): Faction stances on the topic for consistency
        
    Returns:
        Dict: Speech data including the full text, key points, and stance
    """
    # Determine the senator's likely stance based on faction and personality
    # Default stances if none provided
    if not faction_stance:
        faction_stance = {
            "Optimates": random.choice(["oppose", "oppose", "neutral"]),
            "Populares": random.choice(["support", "support", "neutral"]),
            "Military": random.choice(["support", "oppose", "neutral"]),
            "Religious": random.choice(["oppose", "neutral", "support"]),
            "Merchant": random.choice(["support", "neutral", "oppose"])
        }
    
    stance = faction_stance.get(senator["faction"], random.choice(["support", "oppose", "neutral"]))
    
    # Senator personality factors
    eloquence = senator["traits"]["eloquence"]
    corruption = senator["traits"]["corruption"]
    
    # Create a prompt for the AI based on senator details
    prompt = f"""
    You are {senator['name']}, a Roman Senator of the {senator['faction']} faction during the late Republic era.
    
    Your eloquence is {eloquence:.1f}/1.0 and your corruption level is {corruption:.1f}/1.0.
    
    Write a SHORT speech (3-4 sentences maximum) addressing the Senate on this topic:
    "{topic}"
    
    Your stance is to {stance} the proposal.
    
    The speech should:
    - Use historically appropriate Roman language and references
    - Include at least one rhetorical flourish
    - Reflect your faction's interests
    - Be in first person
    - Begin with a formal address like "Senators of Rome" or "Fellow patricians"
    - End with a clear statement of your position
    
    Speech:
    """
    
    # Get AI-generated speech
    speech_text = utils.call_openai_api(
        prompt=prompt,
        temperature=0.8,
        max_tokens=250
    )
    
    # Fallback if API call fails
    if not speech_text or speech_text == "The senator makes a compelling argument.":
        # Generate fallback speech
        stance_phrases = {
            "support": [
                f"Fellow senators, I strongly support this measure on {topic}.",
                f"Rome's glory depends on our approval of this matter."
            ],
            "oppose": [
                f"I must oppose this proposal regarding {topic}.",
                f"For the good of Rome, we must reject this measure."
            ],
            "neutral": [
                f"This matter requires careful deliberation before we decide.",
                f"I call for more discussion on the implications of this proposal."
            ]
        }
        
        opening = random.choice([
            "Senators of Rome,", 
            "Fellow patricians,",
            "Esteemed colleagues,",
            "Noble representatives of our Republic,"
        ])
        
        faction_interest = {
            "Optimates": "the traditions of our ancestors",
            "Populares": "the welfare of the common people",
            "Military": "the strength of our legions",
            "Religious": "the will of the gods",
            "Merchant": "Rome's commercial interests"
        }
        
        main_point = random.choice(stance_phrases[stance])
        
        # Get faction interest or default
        default_interest = "Rome's future"
        interest_phrase = faction_interest.get(senator["faction"], default_interest)
        interest = f"As we consider {interest_phrase}, we must act wisely."
        
        speech_text = f"{opening} {main_point} {interest} {random.choice(stance_phrases[stance])}"
    
    # Return the speech data
    return {
        "full_text": speech_text.strip(),
        "stance": stance,
        "key_points": speech_text.split(". ")[:2]  # First two sentences as key points
    }

def generate_position_summary(senator: Dict, speech: Dict, topic: str) -> str:
    """
    Generate a plain English summary of the senator's position.
    
    Args:
        senator (Dict): The senator data
        speech (Dict): The speech data including stance and full text
        topic (str): The debate topic
        
    Returns:
        str: A plain English summary of the senator's position
    """
    # Stances in plain English
    stance_descriptions = {
        "support": "supports",
        "oppose": "opposes",
        "neutral": "is undecided about"
    }
    
    # Faction motivations
    faction_motivations = {
        "Optimates": "conserving traditional Roman values and aristocratic privilege",
        "Populares": "addressing the needs of common citizens and reform",
        "Military": "strengthening Rome's military power and security",
        "Religious": "maintaining religious traditions and divine favor",
        "Merchant": "promoting trade and economic prosperity"
    }
    
    # Basic reasoning factors based on senator traits
    reasoning = []
    if senator["traits"]["eloquence"] > 0.8:
        reasoning.append("persuasive oratory skills")
    if senator["traits"]["loyalty"] > 0.8:
        reasoning.append("strong faction loyalty")
    if senator["traits"]["corruption"] > 0.3:
        reasoning.append("potential personal gain")
    if not reasoning:
        reasoning.append("personal conviction")
    
    # Build the summary
    stance_text = stance_descriptions.get(speech["stance"], "has mixed feelings about")
    motivation = faction_motivations.get(senator["faction"], "political considerations")
    reasoning_text = " and ".join(reasoning)
    
    summary = f"Senator {senator['name']} {stance_text} the proposal on {topic}, motivated by {motivation}. "
    summary += f"Their position is primarily based on {reasoning_text}."
    
    # Add voting prediction
    if speech["stance"] == "support":
        summary += " They will likely vote FOR the measure."
    elif speech["stance"] == "oppose":
        summary += " They will likely vote AGAINST the measure."
    else:
        summary += " Their vote could go either way."
        
    return summary

def display_speech(senator: Dict, speech: Dict, topic: str = ""):
    """
    Display a senator's speech in an immersive format with plain English summary.
    
    Args:
        senator (Dict): The senator data
        speech (Dict): The speech data including full text
        topic (str): The debate topic (optional)
    """
    # Format senator name and faction
    senator_title = f"{senator['name']} ({senator['faction']})"
    console.print(f"\n[bold cyan]{senator_title}[/]")
    
    # Display the speech in a styled panel
    stance_colors = {
        "support": "green",
        "oppose": "red",
        "neutral": "yellow"
    }
    border_style = stance_colors.get(speech["stance"], "blue")
    
    # Create panel with speech text
    speech_panel = Panel(
        Text(speech["full_text"], style="italic"),
        border_style=border_style,
        title=senator_title,
        title_align="left",
        width=100
    )
    console.print(speech_panel)
    
    # Generate and display position summary
    if topic:
        summary = generate_position_summary(senator, speech, topic)
        stance_tag = {
            "support": "[bold green]FOR[/]",
            "oppose": "[bold red]AGAINST[/]",
            "neutral": "[bold yellow]UNDECIDED[/]"
        }.get(speech["stance"], "[bold blue]COMPLEX[/]")
        
        summary_text = f"Position: {stance_tag} | {summary}"
        summary_panel = Panel(
            Text(summary_text),
            border_style="dim",
            title="Plain English Summary",
            title_align="left",
            width=100
        )
        console.print(summary_panel)