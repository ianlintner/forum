#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Roman Senate AI Game
Speech Generation Test Script

This script tests the integration between the debate system and 
the enhanced speech generation framework.
"""

import random
import os
import sys

# First import directly from speech_generation for enhanced speech generation
from speech_generation import generate_speech as enhanced_generate_speech

# Then import from debate for the integration functions
from debate import generate_speech, generate_multiple_speeches
from rich.console import Console
from rich.panel import Panel

console = Console()

def test_direct_enhanced_speech():
    """Test the enhanced speech generation module directly."""
    
    console.print("\n[bold cyan]Testing Direct Enhanced Speech Generation[/]\n")
    
    # Create a test senator
    test_senator = {
        "id": 1,
        "name": "Quintus Fabius",
        "faction": "Optimates",
        "traits": {
            "eloquence": 0.8,
            "corruption": 0.2,
            "loyalty": 0.9
        }
    }
    
    # Test topic
    test_topic = "Extending Roman citizenship to Italian allies"
    
    # Generate a speech using enhanced_generate_speech directly
    console.print("[yellow]Generating speech directly from speech_generation module...[/]")
    try:
        speech = enhanced_generate_speech(
            senator=test_senator,
            topic=test_topic,
            faction_stance={"Optimates": "oppose", "Populares": "support"},
            year=-91  # 91 BCE
        )
        
        # Display success
        console.print("[bold green]✓[/] Successfully generated speech directly from enhanced module!")
        
        # Show a sample of the speech content
        if speech and "text" in speech:
            preview = speech["text"][:200] + "..." if len(speech["text"]) > 200 else speech["text"]
            console.print(Panel(
                preview,
                title="[bold]Speech Preview",
                border_style="green"
            ))
        
        return speech
    except Exception as e:
        console.print(f"[bold red]Error generating speech directly: {str(e)}[/]")
        return None

def test_speech_generation():
    """Test the enhanced speech generation framework with a single senator."""
    
    console.print("\n[bold cyan]Testing Enhanced Speech Generation Framework via debate.py[/]\n")
    
    # Create a test senator
    test_senator = {
        "id": 1,
        "name": "Marcus Cato",
        "faction": "Optimates",
        "traits": {
            "eloquence": 0.8,
            "corruption": 0.2,
            "loyalty": 0.9
        }
    }
    
    # Test topic
    test_topic = "The expansion of citizenship to Italian allies"
    
    # Generate a speech using the enhanced framework
    console.print("[yellow]Generating speech using enhanced framework...[/]")
    speech = generate_speech(
        senator=test_senator,
        topic=test_topic,
        faction_stance={"Optimates": "oppose", "Populares": "support"},
        year=-91  # 91 BCE (Social War period)
    )
    
    # Display the generated speech
    console.print("\n[bold green]Generated Speech:[/]")
    console.print(Panel(
        speech["english_text"],
        title=f"[bold]{test_senator['name']} ({test_senator['faction']})",
        border_style="green",
        width=100
    ))
    
    # Display metadata
    console.print("\n[bold blue]Speech Metadata:[/]")
    metadata = {
        "Stance": speech.get("stance", "unknown"),
        "Archetype": speech.get("archetype", {}).get("primary", "unknown"),
        "Rhetorical Devices": ", ".join(speech.get("selected_devices", [])),
        "Latin Version Available": "Yes" if speech.get("latin_text") or speech.get("latin_version") else "No",
        "Evaluation Score": str(speech.get("evaluation", {}).get("overall_score", "N/A")) + "/100" if speech.get("evaluation") else "N/A"
    }
    
    for key, value in metadata.items():
        console.print(f"[cyan]{key}:[/] {value}")
    
    return speech

def test_multiple_speeches():
    """Test generating speeches for multiple senators."""
    
    console.print("\n[bold cyan]Testing Multiple Speech Generation[/]\n")
    
    # Create test senators
    test_senators = [
        {
            "id": 1,
            "name": "Marcus Cato",
            "faction": "Optimates",
            "traits": {"eloquence": 0.8, "corruption": 0.2, "loyalty": 0.9}
        },
        {
            "id": 2,
            "name": "Gaius Gracchus",
            "faction": "Populares",
            "traits": {"eloquence": 0.7, "corruption": 0.3, "loyalty": 0.6}
        },
        {
            "id": 3,
            "name": "Lucius Crassus",
            "faction": "Military",
            "traits": {"eloquence": 0.6, "corruption": 0.4, "loyalty": 0.8}
        }
    ]
    
    # Test topic
    test_topic = "Increasing the grain subsidy for Roman citizens"
    
    # Generate speeches for all senators
    speeches = generate_multiple_speeches(
        senators=test_senators,
        topic=test_topic,
        faction_stance={"Optimates": "oppose", "Populares": "support", "Military": "neutral"},
        year=-121  # 121 BCE
    )
    
    # Display summary of all speeches
    console.print("\n[bold green]Generated Speeches Summary:[/]")
    for i, speech in enumerate(speeches):
        senator = test_senators[i]
        console.print(f"[bold]{i+1}. {senator['name']} ({senator['faction']})[/]: {speech.get('stance', 'unknown')} stance, " + 
                     f"{len(speech.get('selected_devices', [])) if speech.get('selected_devices') else 'unknown'} rhetorical devices")
    
    return speeches

if __name__ == "__main__":
    console.print("[bold]Roman Senate Speech Generation Framework Tests[/]")
    console.print("--------------------------------------------------------")
    
    # First test direct access to the enhanced module
    direct_speech = test_direct_enhanced_speech()
    
    # Then test the integrated version through debate.py
    single_speech = test_speech_generation()
    multiple_speeches = test_multiple_speeches()
    
    # Report overall status
    if direct_speech and single_speech and multiple_speeches:
        console.print("\n[bold green]✓[/] All speech generation framework tests completed successfully!")
    else:
        console.print("\n[bold yellow]![/] Some tests may have had issues. Check output above for details.")