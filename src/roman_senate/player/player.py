#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Roman Senate AI Game
Player Module

This module handles player-specific functionality and interactions.
"""

import logging
from typing import Dict, List, Any, Optional
import uuid

logger = logging.getLogger(__name__)

class Player:
    """Represents the human player in the Senate game."""
    
    def __init__(
        self,
        name: str,
        faction: str = "Populares",
        wealth: int = 100,
        influence: int = 25,
        reputation: int = 50,
        ancestry: str = "Plebeian",
        background: str = "Novus Homo (Self-made)",
    ):
        """
        Initialize a new Player.
        
        Args:
            name: Player's Roman name
            faction: Political faction (Populares or Optimates)
            wealth: Starting wealth (0-200)
            influence: Starting influence (0-100)
            reputation: Starting reputation (0-100)
            ancestry: Plebeian or Patrician
            background: Character background
        """
        self.id = str(uuid.uuid4())
        self.name = name
        self.faction = faction
        self.wealth = max(0, min(200, wealth))  # Clamp between 0-200
        self.influence = max(0, min(100, influence))  # Clamp between 0-100
        self.reputation = max(0, min(100, reputation))  # Clamp between 0-100
        self.ancestry = ancestry
        self.background = background
        
        # Track relationships with other senators (NPC)
        self.relationships = {}
        
        # Political capital is spent on influencing votes and making deals
        self.political_capital = 10
        
        # Skills and abilities
        self.skills = {
            "oratory": 3,  # Speaking ability
            "intrigue": 2,  # Ability to gather information and plot
            "administration": 2,  # Governance skill
            "military": 1,  # Military expertise
            "commerce": 2,  # Business and trade skill
        }
        
        # Special abilities unlock at certain skill levels
        self.special_abilities = []
        self.update_special_abilities()
        
        # Track player's political history
        self.political_history = []
        
        # Track current political position if any
        self.current_office = None
        
        logger.info(f"Player character created: {self.name} of the {self.faction}")

    def update_special_abilities(self):
        """Update special abilities based on current skills."""
        self.special_abilities = []
        
        # Oratory abilities
        if self.skills["oratory"] >= 3:
            self.special_abilities.append({
                "name": "Persuasive Argument",
                "description": "Can sway undecided senators more effectively",
                "effect": "Doubles influence when persuading neutral senators"
            })
        
        if self.skills["oratory"] >= 5:
            self.special_abilities.append({
                "name": "Master Orator",
                "description": "Speeches have increased impact on all senators",
                "effect": "Speech influence bonus +50%"
            })
        
        # Intrigue abilities
        if self.skills["intrigue"] >= 3:
            self.special_abilities.append({
                "name": "Information Network",
                "description": "Obtain information about senators' positions before debates",
                "effect": "Reveals voting intentions of 3 random senators before debate"
            })
        
        # Military abilities
        if self.skills["military"] >= 4:
            self.special_abilities.append({
                "name": "Military Prestige",
                "description": "Experience in the field lends weight to military matters",
                "effect": "+25% influence in military-related debates"
            })
        
        # Commerce abilities
        if self.skills["commerce"] >= 4:
            self.special_abilities.append({
                "name": "Wealthy Connections",
                "description": "Connections with merchants and tax farmers",
                "effect": "Gain 25% more wealth from economic activities"
            })

    def gain_experience(self, skill: str, amount: int = 1):
        """
        Increase player skill through experience.
        
        Args:
            skill: The skill to improve
            amount: Amount to increase the skill
        """
        if skill in self.skills:
            self.skills[skill] = min(10, self.skills[skill] + amount)
            logger.info(f"Player {self.name} gained {amount} in {skill}")
            
            # Check if new abilities are unlocked
            previous_abilities = len(self.special_abilities)
            self.update_special_abilities()
            if len(self.special_abilities) > previous_abilities:
                logger.info(f"Player {self.name} unlocked new abilities!")
                return True  # Unlocked new ability
        return False
    
    def change_reputation(self, amount: int):
        """
        Change player reputation.
        
        Args:
            amount: Amount to change (positive or negative)
        """
        old_reputation = self.reputation
        self.reputation = max(0, min(100, self.reputation + amount))
        change = self.reputation - old_reputation
        logger.info(f"Player {self.name} reputation changed by {change} to {self.reputation}")
    
    def change_influence(self, amount: int):
        """
        Change player influence.
        
        Args:
            amount: Amount to change (positive or negative)
        """
        old_influence = self.influence
        self.influence = max(0, min(100, self.influence + amount))
        change = self.influence - old_influence
        logger.info(f"Player {self.name} influence changed by {change} to {self.influence}")
    
    def change_wealth(self, amount: int):
        """
        Change player wealth.
        
        Args:
            amount: Amount to change (positive or negative)
        """
        old_wealth = self.wealth
        self.wealth = max(0, min(200, self.wealth + amount))
        change = self.wealth - old_wealth
        logger.info(f"Player {self.name} wealth changed by {change} to {self.wealth}")
    
    def update_relationship(self, senator_id: str, change: int):
        """
        Update relationship with another senator.
        
        Args:
            senator_id: ID of the senator
            change: Amount to change relationship (-10 to +10)
        """
        if senator_id not in self.relationships:
            # Starting neutral (50)
            self.relationships[senator_id] = 50
        
        # Update relationship score (0-100)
        old_value = self.relationships[senator_id]
        self.relationships[senator_id] = max(0, min(100, self.relationships[senator_id] + change))
        new_value = self.relationships[senator_id]
        
        logger.info(f"Relationship with senator {senator_id} changed by {change} to {new_value}")
    
    def spend_political_capital(self, amount: int) -> bool:
        """
        Spend political capital to influence game events.
        
        Args:
            amount: Amount to spend
            
        Returns:
            True if successful, False if not enough capital
        """
        if self.political_capital >= amount:
            self.political_capital -= amount
            logger.info(f"Player spent {amount} political capital, {self.political_capital} remaining")
            return True
        else:
            logger.info(f"Insufficient political capital: needed {amount}, has {self.political_capital}")
            return False
    
    def gain_political_capital(self, amount: int):
        """
        Gain political capital.
        
        Args:
            amount: Amount to gain
        """
        self.political_capital += amount
        logger.info(f"Player gained {amount} political capital, now has {self.political_capital}")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert player data to a dictionary.
        
        Returns:
            Dictionary representation of player data
        """
        return {
            "id": self.id,
            "name": self.name,
            "faction": self.faction,
            "wealth": self.wealth,
            "influence": self.influence,
            "reputation": self.reputation,
            "ancestry": self.ancestry,
            "background": self.background,
            "political_capital": self.political_capital,
            "skills": self.skills,
            "special_abilities": self.special_abilities,
            "current_office": self.current_office,
            "relationships": self.relationships
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Player':
        """
        Create a Player instance from a dictionary.
        
        Args:
            data: Dictionary containing player data
            
        Returns:
            A new Player instance
        """
        player = cls(
            name=data.get("name", "Unknown"),
            faction=data.get("faction", "Populares"),
            wealth=data.get("wealth", 100),
            influence=data.get("influence", 25),
            reputation=data.get("reputation", 50),
            ancestry=data.get("ancestry", "Plebeian"),
            background=data.get("background", "Novus Homo (Self-made)")
        )
        
        # Restore additional attributes
        player.id = data.get("id", player.id)
        player.political_capital = data.get("political_capital", player.political_capital)
        player.skills = data.get("skills", player.skills)
        player.current_office = data.get("current_office", None)
        player.relationships = data.get("relationships", {})
        
        # Recalculate special abilities
        player.update_special_abilities()
        
        return player