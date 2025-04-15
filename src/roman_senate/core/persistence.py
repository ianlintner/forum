"""
Roman Senate AI Game
Persistence Module

This module handles saving and loading game state for the Roman Senate simulation.
It provides functionality to serialize and deserialize all components of the simulation,
including senators, their memories, debate history, and all game state.
"""

import os
import json
import datetime
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

from ..core.game_state import game_state, GameState
from ..core.roman_calendar import CalendarType
from ..utils.llm.factory import get_llm_provider

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
SAVE_DIR = "saves"
VERSION = "1.0.0"  # Used for save file compatibility


def ensure_save_directory():
    """Ensure the save directory exists."""
    save_path = Path(SAVE_DIR)
    save_path.mkdir(exist_ok=True)
    return save_path


def get_save_files() -> List[Dict[str, Any]]:
    """
    Get a list of available save files with metadata.
    
    Returns:
        List of save file info dictionaries
    """
    save_path = ensure_save_directory()
    save_files = []
    
    for file_path in save_path.glob("*.json"):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            # Extract metadata
            metadata = {
                "filename": file_path.name,
                "full_path": str(file_path),
                "created": data.get("metadata", {}).get("created", "Unknown"),
                "version": data.get("metadata", {}).get("version", "Unknown"),
                "year": data.get("game_state", {}).get("year", "Unknown"),
                "senator_count": len(data.get("game_state", {}).get("senators", [])),
                "topics_resolved": len(data.get("game_state", {}).get("game_history", [])),
            }
            save_files.append(metadata)
        except Exception as e:
            logger.error(f"Error reading save file {file_path}: {e}")
    
    # Sort by creation date (newest first)
    save_files.sort(key=lambda x: x["created"], reverse=True)
    return save_files


def save_game(filename: Optional[str] = None) -> str:
    """
    Save the current game state to a file.
    
    Args:
        filename: Optional custom filename, defaults to timestamp-based name
        
    Returns:
        Path to the saved file
    """
    # Create default filename if not provided
    if not filename:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"senate_save_{timestamp}.json"
    
    # Ensure .json extension
    if not filename.endswith(".json"):
        filename += ".json"
    
    # Ensure save directory exists
    save_path = ensure_save_directory()
    full_path = save_path / filename
    
    # Create the save data structure
    save_data = {
        "metadata": {
            "version": VERSION,
            "created": datetime.datetime.now().isoformat(),
            "filename": filename
        },
        "game_state": serialize_game_state(game_state)
    }
    
    # Write the save file
    with open(full_path, "w", encoding="utf-8") as f:
        json.dump(save_data, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Game saved to {full_path}")
    return str(full_path)


def load_game(filename: str) -> bool:
    """
    Load a game from a save file.
    
    Args:
        filename: The name of the save file to load
        
    Returns:
        True if loaded successfully, False otherwise
    """
    save_path = ensure_save_directory()
    
    # If filename doesn't include path, assume it's in the save directory
    if not os.path.dirname(filename):
        full_path = save_path / filename
    else:
        full_path = Path(filename)
    
    # Ensure .json extension
    if not str(full_path).endswith(".json"):
        full_path = Path(f"{full_path}.json")
    
    try:
        with open(full_path, "r", encoding="utf-8") as f:
            save_data = json.load(f)
        
        # Check version compatibility
        if not is_compatible_version(save_data.get("metadata", {}).get("version", "0.0.0")):
            logger.error(f"Incompatible save file version: {save_data.get('metadata', {}).get('version')}")
            return False
        
        # Deserialize game state
        deserialize_game_state(save_data.get("game_state", {}))
        
        logger.info(f"Game loaded from {full_path}")
        return True
    except Exception as e:
        logger.error(f"Error loading game from {full_path}: {e}")
        return False


def auto_save() -> str:
    """
    Perform an automatic save.
    
    Returns:
        Path to the auto-save file
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"auto_save_{timestamp}.json"
    return save_game(filename)


def is_compatible_version(version: str) -> bool:
    """
    Check if the save file version is compatible with the current version.
    
    Args:
        version: Version string from the save file
        
    Returns:
        True if compatible, False otherwise
    """
    # For now, we only check major version compatibility
    try:
        save_major = version.split(".")[0]
        current_major = VERSION.split(".")[0]
        return save_major == current_major
    except:
        return False


def serialize_game_state(game_state: GameState) -> Dict[str, Any]:
    """
    Serialize the game state object to a dictionary.
    
    Args:
        game_state: The GameState object to serialize
        
    Returns:
        Dictionary representation of the game state
    """
    state_dict = {
        "game_history": game_state.game_history,
        "current_topic": game_state.current_topic,
        "year": game_state.year,
        "voting_results": game_state.voting_results,
        "senators": [serialize_senator(senator) for senator in game_state.senators],
        # Add calendar serialization
        "calendar": serialize_calendar(game_state.calendar) if game_state.calendar else None
    }
    return state_dict


def deserialize_game_state(state_dict: Dict[str, Any]) -> None:
    """
    Deserialize a game state dictionary into the global game state.
    
    Args:
        state_dict: Dictionary containing the game state data
    """
    # Reset the game state
    game_state.reset()
    
    # Set basic properties
    game_state.game_history = state_dict.get("game_history", [])
    game_state.current_topic = state_dict.get("current_topic")
    game_state.year = state_dict.get("year")
    game_state.voting_results = state_dict.get("voting_results", [])
    
    # Deserialize senators
    senator_dicts = state_dict.get("senators", [])
    game_state.senators = [deserialize_senator(senator_dict) for senator_dict in senator_dicts]
    
    # Deserialize calendar if present
    calendar_dict = state_dict.get("calendar")
    if calendar_dict:
        deserialize_calendar(game_state, calendar_dict)


def serialize_senator(senator: Dict[str, Any]) -> Dict[str, Any]:
    """
    Serialize a senator dictionary, including memory if it exists.
    
    Args:
        senator: The senator dictionary to serialize
        
    Returns:
        Dictionary representation of the senator
    """
    senator_copy = senator.copy()
    
    # If this is a SenatorAgent instance, handle memory
    if hasattr(senator, 'memory') and hasattr(senator, 'senator'):
        senator_copy = senator.senator.copy()
        senator_copy["memory"] = serialize_agent_memory(senator.memory)
        senator_copy["current_stance"] = senator.current_stance
    # If this is just a senator dict from a SenatorAgent, check for memory attribute
    elif isinstance(senator, dict) and "memory" in senator:
        memory_obj = senator["memory"]
        if hasattr(memory_obj, 'observations'):
            senator_copy["memory"] = serialize_agent_memory(memory_obj)
    
    return senator_copy


def deserialize_senator(senator_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deserialize a senator dictionary, including memory if present.
    
    Args:
        senator_dict: Dictionary representation of the senator
        
    Returns:
        Reconstructed senator dictionary
    """
    senator_copy = senator_dict.copy()
    
    # Handle memory if present
    if "memory" in senator_dict:
        memory_dict = senator_dict["memory"]
        if isinstance(memory_dict, dict):
            from ..agents.agent_memory import AgentMemory
            memory = AgentMemory()
            deserialize_agent_memory(memory, memory_dict)
            senator_copy["memory"] = memory
    
    return senator_copy


def serialize_agent_memory(memory) -> Dict[str, Any]:
    """
    Serialize an AgentMemory object to a dictionary.
    
    Args:
        memory: The AgentMemory object to serialize
        
    Returns:
        Dictionary representation of the memory
    """
    return {
        "observations": memory.observations,
        "interactions": memory.interactions,
        "voting_history": memory.voting_history,
        "debate_history": memory.debate_history,
        "relationship_scores": memory.relationship_scores
    }


def deserialize_agent_memory(memory, memory_dict: Dict[str, Any]) -> None:
    """
    Deserialize a memory dictionary into an AgentMemory object.
    
    Args:
        memory: The AgentMemory object to update
        memory_dict: Dictionary containing the memory data
    """
    memory.observations = memory_dict.get("observations", [])
    memory.interactions = memory_dict.get("interactions", {})
    memory.voting_history = memory_dict.get("voting_history", {})
    memory.debate_history = memory_dict.get("debate_history", [])
    memory.relationship_scores = memory_dict.get("relationship_scores", {})


def serialize_calendar(calendar) -> Dict[str, Any]:
    """
    Serialize the calendar object to a dictionary.
    
    Args:
        calendar: The RomanCalendar object to serialize
        
    Returns:
        Dictionary representation of the calendar
    """
    if not calendar:
        return None
    
    return {
        "year": calendar.year,
        "calendar_type": calendar.calendar_type.value,
        "current_month_idx": calendar.current_month_idx,
        "current_day": calendar.current_day,
        "consuls": calendar.consuls
    }


def deserialize_calendar(game_state, calendar_dict: Dict[str, Any]) -> None:
    """
    Deserialize a calendar dictionary into the game state.
    
    Args:
        game_state: The GameState object to update
        calendar_dict: Dictionary containing the calendar data
    """
    year = calendar_dict.get("year", game_state.year)
    calendar_type_str = calendar_dict.get("calendar_type", "pre_julian")
    calendar_type = CalendarType.PRE_JULIAN if calendar_type_str == "pre_julian" else CalendarType.JULIAN
    
    # Initialize the calendar
    game_state.initialize_calendar(year, calendar_type)
    
    # Set the current state
    game_state.calendar.current_month_idx = calendar_dict.get("current_month_idx", 0)
    game_state.calendar.current_month = game_state.calendar.months[game_state.calendar.current_month_idx]
    game_state.calendar.current_day = calendar_dict.get("current_day", 1)
    game_state.calendar.consuls = calendar_dict.get("consuls", [])