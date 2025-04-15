"""
Roman Senate AI Game
Test Persistence Module

This module contains tests for the game state persistence functionality.
"""

import os
import json
import pytest
from pathlib import Path

from roman_senate.core.game_state import game_state, GameState
from roman_senate.core import senators
from roman_senate.core.persistence import (
    save_game, load_game, get_save_files, ensure_save_directory,
    serialize_game_state, deserialize_game_state
)


@pytest.fixture
def setup_game_state():
    """Set up a test game state."""
    # Reset game state
    game_state.reset()
    
    # Set basic properties
    game_state.year = -44  # 44 BCE (year of Caesar's assassination)
    game_state.current_topic = "Should Caesar be named dictator for life?"
    
    # Create some test senators
    senate_members = senators.initialize_senate(5)  # Small number for tests
    game_state.senators = senate_members
    
    # Add some voting results
    game_state.add_topic_result(
        "Should Rome expand further into Gaul?",
        {"outcome": "PASSED", "votes": {"for": 3, "against": 2, "abstain": 0}}
    )
    
    yield game_state
    
    # Cleanup - reset game state after test
    game_state.reset()


@pytest.fixture
def mock_save_dir(monkeypatch, tmp_path):
    """Use a temporary directory for saves during tests."""
    # Create a subdirectory in the temp directory for saves
    save_path = tmp_path / "test_saves"
    save_path.mkdir()
    
    # Patch the SAVE_DIR constant
    import roman_senate.core.persistence
    monkeypatch.setattr(roman_senate.core.persistence, "SAVE_DIR", str(save_path))
    
    return save_path


def test_ensure_save_directory(mock_save_dir):
    """Test that the save directory is created if it doesn't exist."""
    # Delete the directory to test creation
    Path(mock_save_dir).rmdir()
    
    # Call function to recreate it
    path = ensure_save_directory()
    
    # Check that directory exists
    assert Path(path).exists()
    assert Path(path).is_dir()


def test_save_and_load_game(setup_game_state, mock_save_dir):
    """Test saving and loading a game."""
    # Save the game
    filename = "test_save.json"
    saved_path = save_game(filename)
    
    # Verify the file exists
    assert Path(saved_path).exists()
    
    # Reset game state
    game_state.reset()
    assert not game_state.senators  # Confirm reset worked
    
    # Load the game
    load_result = load_game(filename)
    
    # Check load was successful
    assert load_result is True
    
    # Verify state was restored
    assert game_state.year == -44
    assert game_state.current_topic == "Should Caesar be named dictator for life?"
    assert len(game_state.senators) == 5
    assert len(game_state.game_history) == 1
    assert game_state.game_history[0]["topic"] == "Should Rome expand further into Gaul?"
    assert game_state.game_history[0]["votes"]["outcome"] == "PASSED"


def test_get_save_files(mock_save_dir):
    """Test listing save files."""
    # Create a couple of test save files
    save1 = mock_save_dir / "save1.json"
    save2 = mock_save_dir / "save2.json"
    
    # Write minimal valid content to the files
    save1_content = {
        "metadata": {"created": "2025-04-15T10:00:00", "version": "1.0.0"},
        "game_state": {"year": -44, "senators": [{"name": "Cicero"}], "game_history": []}
    }
    
    save2_content = {
        "metadata": {"created": "2025-04-15T11:00:00", "version": "1.0.0"},
        "game_state": {
            "year": -50,
            "senators": [{"name": "Caesar"}, {"name": "Brutus"}],
            "game_history": [{"topic": "Test"}]
        }
    }
    
    with open(save1, 'w') as f:
        json.dump(save1_content, f)
        
    with open(save2, 'w') as f:
        json.dump(save2_content, f)
        
    # Get save files
    save_files = get_save_files()
    
    # Check results
    assert len(save_files) == 2
    # Files should be sorted newest first
    assert save_files[0]["filename"] == "save2.json"
    assert save_files[1]["filename"] == "save1.json"
    assert save_files[0]["year"] == -50
    assert save_files[1]["year"] == -44
    assert save_files[0]["senator_count"] == 2
    assert save_files[1]["senator_count"] == 1
    assert save_files[0]["topics_resolved"] == 1
    assert save_files[1]["topics_resolved"] == 0


def test_serialization(setup_game_state):
    """Test game state serialization and deserialization."""
    # Serialize game state
    state_dict = serialize_game_state(game_state)
    
    # Verify serialized data
    assert state_dict["year"] == -44
    assert state_dict["current_topic"] == "Should Caesar be named dictator for life?"
    assert len(state_dict["senators"]) == 5
    assert len(state_dict["game_history"]) == 1
    
    # Reset game state
    game_state.reset()
    
    # Deserialize
    deserialize_game_state(state_dict)
    
    # Verify deserialized state
    assert game_state.year == -44
    assert game_state.current_topic == "Should Caesar be named dictator for life?"
    assert len(game_state.senators) == 5
    assert len(game_state.game_history) == 1