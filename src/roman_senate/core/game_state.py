#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Roman Senate Game
Game State Module

This module manages the global game state for the Roman Senate simulation.
"""

from typing import List, Dict, Any


class GameState:
    """
    Manages global game state for the Roman Senate simulation.
    Stores information about senators, topics, votes, and game history.
    """
    
    def __init__(self):
        """Initialize a new game state."""
        self.game_history = []
        self.senators = []
        self.current_topic = None
        self.year = None
        self.voting_results = []
        
    def add_topic_result(self, topic, votes):
        """
        Add a topic result to the game history.
        
        Args:
            topic: The topic that was debated
            votes: The voting results
        """
        self.game_history.append({
            'topic': topic,
            'votes': votes,
            'year': self.year,
            'year_display': f"{abs(self.year)} BCE" if self.year else "Unknown"
        })
        
    def reset(self):
        """Reset the game state for a new session."""
        self.__init__()


# Create a global instance of the game state
game_state = GameState()