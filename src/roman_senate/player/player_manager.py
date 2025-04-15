#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Roman Senate AI Game
Player Manager Module

This module provides a manager class for handling player operations.
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path

from .player import Player

logger = logging.getLogger(__name__)

class PlayerManager:
    """Manages player data, persistence, and operations."""
    
    def __init__(self, save_dir: Optional[str] = None):
        """
        Initialize the player manager.
        
        Args:
            save_dir: Directory to save player data (default: ./data/saves/)
        """
        self.player = None
        
        # Set up save directory
        if save_dir is None:
            # Get the project base directory
            base_dir = Path(__file__).resolve().parent.parent.parent.parent
            self.save_dir = os.path.join(base_dir, "data", "saves")
        else:
            self.save_dir = save_dir
            
        # Create save directory if it doesn't exist
        os.makedirs(self.save_dir, exist_ok=True)
        logger.info(f"Player save directory: {self.save_dir}")
    
    def create_player(
        self,
        name: str,
        faction: str = "Populares",
        wealth: int = 100,
        influence: int = 25,
        reputation: int = 50,
        ancestry: str = "Plebeian",
        background: str = "Novus Homo (Self-made)"
    ) -> Player:
        """
        Create a new player.
        
        Args:
            name: Player's Roman name
            faction: Political faction (Populares or Optimates)
            wealth: Starting wealth (0-200)
            influence: Starting influence (0-100)
            reputation: Starting reputation (0-100)
            ancestry: Plebeian or Patrician
            background: Character background
            
        Returns:
            The newly created Player instance
        """
        self.player = Player(
            name=name,
            faction=faction,
            wealth=wealth,
            influence=influence,
            reputation=reputation,
            ancestry=ancestry,
            background=background
        )
        logger.info(f"Created new player: {name}")
        return self.player
    
    def save_player(self, filename: Optional[str] = None) -> str:
        """
        Save the current player to a file.
        
        Args:
            filename: Optional filename (default: player_<id>.json)
            
        Returns:
            Path to the saved file
            
        Raises:
            ValueError: If no player exists
        """
        if self.player is None:
            raise ValueError("No player to save")
        
        # Create filename if not provided
        if filename is None:
            filename = f"player_{self.player.id}.json"
        
        # Ensure .json extension
        if not filename.endswith(".json"):
            filename += ".json"
            
        # Create full path
        save_path = os.path.join(self.save_dir, filename)
        
        # Convert player to dictionary
        player_data = self.player.to_dict()
        
        # Save to file
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(player_data, f, indent=2)
            
        logger.info(f"Saved player to {save_path}")
        return save_path
    
    def load_player(self, filename: str) -> Player:
        """
        Load a player from a file.
        
        Args:
            filename: Path to the player save file
            
        Returns:
            The loaded Player instance
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the file is invalid
        """
        # If just the filename without path is given, prepend the save directory
        if not os.path.dirname(filename):
            load_path = os.path.join(self.save_dir, filename)
        else:
            load_path = filename
            
        # Ensure .json extension
        if not load_path.endswith(".json"):
            load_path += ".json"
        
        # Check if file exists
        if not os.path.isfile(load_path):
            raise FileNotFoundError(f"Player save file not found: {load_path}")
        
        # Load from file
        try:
            with open(load_path, 'r', encoding='utf-8') as f:
                player_data = json.load(f)
                
            # Create player from data
            self.player = Player.from_dict(player_data)
            logger.info(f"Loaded player {self.player.name} from {load_path}")
            return self.player
            
        except (json.JSONDecodeError, KeyError) as e:
            raise ValueError(f"Invalid player save file: {e}")
    
    def get_save_files(self) -> Dict[str, str]:
        """
        Get a dictionary of available save files.
        
        Returns:
            Dictionary mapping filenames to player names (where available)
        """
        saves = {}
        
        # List all JSON files in the save directory
        for filename in os.listdir(self.save_dir):
            if filename.endswith(".json"):
                file_path = os.path.join(self.save_dir, filename)
                
                # Try to extract player name
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        player_name = data.get("name", "Unknown")
                        saves[filename] = player_name
                except:
                    # If we can't read the file, just include the filename
                    saves[filename] = "Unknown Player"
        
        return saves
    
    def delete_save(self, filename: str) -> bool:
        """
        Delete a save file.
        
        Args:
            filename: Name of the save file to delete
            
        Returns:
            True if successful, False otherwise
        """
        # If just the filename without path is given, prepend the save directory
        if not os.path.dirname(filename):
            file_path = os.path.join(self.save_dir, filename)
        else:
            file_path = filename
            
        # Ensure .json extension
        if not file_path.endswith(".json"):
            file_path += ".json"
        
        # Check if file exists
        if os.path.isfile(file_path):
            os.remove(file_path)
            logger.info(f"Deleted save file: {file_path}")
            return True
        else:
            logger.warning(f"Save file not found: {file_path}")
            return False
            
    def has_active_player(self) -> bool:
        """
        Check if there is an active player.
        
        Returns:
            True if a player is loaded, False otherwise
        """
        return self.player is not None
            
    def get_player(self) -> Optional[Player]:
        """
        Get the current player.
        
        Returns:
            The current Player instance or None if no player is loaded
        """
        return self.player