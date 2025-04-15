#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Roman Senate AI Game
Player Test Module

This script demonstrates and tests the player-related functionality.
"""

import os
import sys
import asyncio
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Ensure the package is importable
script_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(script_dir)))
sys.path.insert(0, base_dir)

# Import player components
from roman_senate.player import Player, PlayerManager, PlayerUI, PlayerActions
from roman_senate.utils.config import LLM_PROVIDER, LLM_MODEL

async def test_player_creation():
    """Test player creation and management."""
    # Initialize components
    player_manager = PlayerManager()
    ui = PlayerUI()
    
    # Display welcome
    ui.display_welcome()
    
    # Create a new player
    player = player_manager.create_player(
        name="Marcus Tullius",
        faction="Populares",
        wealth=120,
        influence=35,
        reputation=60,
        ancestry="Plebeian",
        background="Novus Homo (Self-made)"
    )
    
    # Associate UI with player
    ui.set_player(player)
    
    # Display player status
    ui.display_player_status()
    
    # Save player
    save_path = player_manager.save_player()
    print(f"Player saved to: {save_path}")
    
    # Create a new player manager and load saved player
    new_manager = PlayerManager()
    loaded_player = new_manager.load_player(save_path.split('/')[-1])
    
    # Show loaded player
    ui.set_player(loaded_player)
    print("\nLoaded player data:")
    ui.display_player_status()
    
    return player, ui

async def test_player_speech(player: Player, ui: PlayerUI):
    """Test player speech generation."""
    # Initialize player actions
    player_actions = PlayerActions(player, ui)
    
    # Set up a test topic
    test_topic = "Whether Rome should increase the grain dole for plebeians"
    
    # Generate and show player speech
    print(f"\n\n--- DEBATE TOPIC: {test_topic} ---")
    speech_result = await player_actions.make_speech(
        topic=test_topic,
        stance="support",
        context={"faction_support": "Populares generally support this measure"}
    )
    
    # Display speech information
    print("\n\nYOUR SPEECH:")
    print("-" * 80)
    print(speech_result["speech"]["content"])
    print("-" * 80)
    print(f"Impact: {speech_result['impact']}")
    
    if speech_result.get('skill_improved'):
        print(f"Your oratory skill has improved! New level: {player.skills['oratory']}")
    
    # Test player vote
    vote_result = player_actions.cast_vote(
        proposal="Increase the grain dole by 25% for all eligible plebeians",
        context={
            "description": "The Senate is voting on whether to increase the grain dole distributed to Rome's citizens."
        }
    )
    
    print(f"\nYou voted: {vote_result['vote']} on the proposal.")
    
    # Update player stats to demonstrate changes
    player.change_reputation(5)
    player.change_influence(3)
    player.gain_political_capital(2)
    
    print("\nUpdated player status after debate:")
    ui.display_player_status()

async def test_player_interjection(player: Player, ui: PlayerUI):
    """Test player interjection functionality."""
    # Initialize player actions
    player_actions = PlayerActions(player, ui)
    
    # Set up test data
    test_speaker = "Appius Claudius"
    test_segment = ("The very idea of increasing the grain dole is preposterous! "
                  "It will only drain our treasury and encourage idleness among the plebs. "
                  "Our grandfathers would never have approved of such wasteful largesse!")
    test_topic = "Whether Rome should increase the grain dole for plebeians"
    
    print(f"\n\n--- {test_speaker} IS SPEAKING ---")
    
    # Test interjection
    interjection_result = await player_actions.make_interjection(
        speaker=test_speaker,
        speech_segment=test_segment,
        topic=test_topic
    )
    
    if interjection_result.get("interjected", False):
        print("\nYOUR INTERJECTION:")
        print("-" * 80)
        print(interjection_result["interjection"]["content"])
        print("-" * 80)
        print(f"Impact: {interjection_result['impact']}")
        
        # Show skill improvements
        skills_improved = interjection_result.get("skills_improved", {})
        for skill, improved in skills_improved.items():
            if improved:
                print(f"Your {skill} skill has improved! New level: {player.skills[skill]}")
    else:
        print("\nYou chose not to interject.")
    
    # Update player stats to demonstrate changes
    player.change_reputation(-2)  # Interjections can be seen as disruptive
    
    print("\nUpdated player status after interjection:")
    ui.display_player_status()

async def test_political_actions(player: Player, ui: PlayerUI):
    """Test player political actions."""
    # Initialize player actions
    player_actions = PlayerActions(player, ui)
    
    # Set up test political actions
    test_actions = [
        {
            "id": 1,
            "name": "Host a Private Dinner",
            "description": "Invite influential senators to your home for a dinner and discussion.",
            "cost": {"wealth": 10, "political_capital": 1},
            "requirements": {"oratory": 2},
            "effects": {"influence": 5, "relationships": {"senator123": 5, "senator456": 3}},
            "available": True
        },
        {
            "id": 2,
            "name": "Fund Public Games",
            "description": "Sponsor games or gladiatorial contests to gain popularity.",
            "cost": {"wealth": 30, "political_capital": 2},
            "requirements": {"wealth": 50},
            "effects": {"reputation": 10, "influence": 5},
            "available": player.wealth >= 50
        },
        {
            "id": 3,
            "name": "Bribe Official",
            "description": "Offer payment to a Senate official for favorable treatment.",
            "cost": {"wealth": 20, "political_capital": 3},
            "requirements": {"intrigue": 3},
            "effects": {"reputation": -5, "influence": 8},
            "available": player.skills.get("intrigue", 0) >= 3
        }
    ]
    
    print("\n\n--- POLITICAL ACTIONS ---")
    
    # Test political action
    action_result = player_actions.perform_political_action(
        available_actions=test_actions
    )
    
    if action_result.get("action_performed", False):
        print(f"\nYou performed the action: {action_result['action']}")
        print(f"Costs paid: {action_result['costs_paid']}")
        print(f"Effects applied: {action_result['effects_applied']}")
    else:
        print("\nYou chose not to perform any political action.")
    
    print("\nUpdated player status after political action:")
    ui.display_player_status()

async def main():
    """Main function to run all tests."""
    print(f"Using LLM Provider: {LLM_PROVIDER}, Model: {LLM_MODEL}")
    
    try:
        # Test player creation and management
        player, ui = await test_player_creation()
        
        # Test player speech functionality
        await test_player_speech(player, ui)
        
        # Test player interjection functionality
        await test_player_interjection(player, ui)
        
        # Test political actions
        await test_political_actions(player, ui)
        
        print("\n\nPlayer testing completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during player testing: {e}", exc_info=True)
        print(f"\nError encountered: {e}")

if __name__ == "__main__":
    asyncio.run(main())