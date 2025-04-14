#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Roman Senate AI Game
Speech Generator Module

This module orchestrates the generation of speeches for Roman senators,
leveraging the archetype system, rhetorical devices, and historical context.
"""

import random
import re
from typing import Dict, List, Optional, Any, Tuple
import time

# Import submodules
from . import archetype_system
from . import rhetorical_devices
from . import historical_context
from . import classical_structure
from . import latin_flourishes
from . import speech_evaluation

# Try to import the original speech generation function for fallback compatibility
try:
    from debate import generate_speech as original_generate_speech
    ORIGINAL_FUNCTION_AVAILABLE = True
except ImportError:
    ORIGINAL_FUNCTION_AVAILABLE = False

def generate_speech(
    senator: Dict,
    topic: str,
    faction_stance: Dict = None,
    year: int = None,
    responding_to: Optional[Dict] = None,
    previous_speeches: Optional[List[Dict]] = None,
) -> Dict:
    """
    Generate an enhanced speech for a Roman senator based on their identity, faction,
    personality archetype, and the historical context.
    
    Args:
        senator: Senator information including traits and faction
        topic: The debate topic
        faction_stance: Faction stances on the topic for consistency
        year: The year in Roman history (negative for BCE)
        responding_to: Senator/speech being directly responded to
        previous_speeches: Previous speeches in this debate
        
    Returns:
        Dict: Speech data including the full Latin and English texts, key points,
              rhetorical devices used, historical references included, and scoring
              information for future processing.
    """
    # Use default year if not provided
    if year is None:
        year = -80  # Default to late Republic
    
    # 1. Determine senator's archetype
    archetype_info = archetype_system.determine_archetype(senator)
    
    # 2. Generate speech parameters based on archetype
    speech_params = archetype_system.generate_archetype_parameters(senator, archetype_info)
    
    # 3. Get historical context for the year
    hist_context = historical_context.get_historical_context_for_speech(year, topic)
    
    # 4. Generate a structured speech according to classical rhetoric
    speech_structure = classical_structure.generate_speech_structure(
        senator,
        topic,
        speech_params,
        hist_context,
        responding_to
    )
    
    # 5. Expand the structure into actual content
    expanded_structure = classical_structure.expand_speech_structure(
        speech_structure,
        topic,
        speech_params,
        hist_context
    )
    
    # 6. Assemble the basic speech text
    basic_speech_text = classical_structure.assemble_full_speech(expanded_structure)
    
    # 7. Select and apply rhetorical devices
    eloquence = senator.get("traits", {}).get("eloquence", 0.5)
    selected_devices = archetype_system.select_rhetorical_devices(
        speech_params,
        eloquence,
        count=max(1, int(eloquence * 4))  # More eloquent senators use more devices
    )
    
    enhanced_speech_text, device_descriptions = rhetorical_devices.apply_multiple_devices(
        basic_speech_text,
        selected_devices
    )
    
    # 8. Add Latin flourishes
    latin_usage_level = speech_params.get("latin_patterns", {}).get("frequency", 0.5)
    english_with_latin = latin_flourishes.add_latin_flourish(
        enhanced_speech_text,
        flourish_level=latin_usage_level,
        archetype=archetype_info["primary"]
    )
    
    # 9. Generate a Latin version if appropriate
    latin_version = latin_flourishes.generate_latin_speech_version(
        enhanced_speech_text,
        archetype_info["primary"],
        latin_usage_level
    )
    
    # 10. Add Latin opening
    final_speech_text = latin_flourishes.add_latin_opening(english_with_latin, year)
    
    # 11. Determine stance on topic based on faction and archetype
    stance = determine_stance(topic, senator, speech_params, faction_stance)
    
    # 12. Evaluate speech quality
    speech_data = {
        "text": final_speech_text,
        "senator_name": senator.get("name", "Unknown Senator"),
        "senator_id": senator.get("id", 0),
        "faction": senator.get("faction", ""),
        "topic": topic,
        "stance": stance,
        "year": year,
        "archetype": archetype_info,
        "selected_devices": selected_devices,
        "device_descriptions": device_descriptions,
        "speech_structure": {k: v.get("content", "") for k, v in expanded_structure.items()},
        "latin_version": latin_version,
        "points": extract_key_points(final_speech_text, 3),
        "mentioned_senators": extract_mentioned_senators(final_speech_text, previous_speeches),
        "responding_to": responding_to.get("senator_id") if responding_to else None
    }
    
    # Evaluate the speech
    evaluation = speech_evaluation.evaluate_speech(final_speech_text, speech_data)
    speech_data["evaluation"] = evaluation
    
    # Check if we're using the extended version or need to maintain backward compatibility
    if ORIGINAL_FUNCTION_AVAILABLE and random.random() < 0.3:
        # Occasionally use the original function for variety (30% chance)
        try:
            original_speech = original_generate_speech(
                senator=senator,
                topic=topic,
                faction_stance=faction_stance,
                year=year,
                responding_to=responding_to,
                previous_speeches=previous_speeches
            )
            
            # Enhance the original speech with our metadata
            original_speech.update({
                "archetype": archetype_info,
                "selected_devices": selected_devices,
                "evaluation": evaluation,
                "speech_structure": {k: v.get("content", "") for k, v in expanded_structure.items()},
                "latin_version": latin_version
            })
            
            return original_speech
        except Exception:
            # If original function fails, continue with our implementation
            pass
    
    return speech_data

def determine_stance(topic: str, senator: Dict, speech_params: Dict, faction_stance: Dict = None) -> str:
    """
    Determine the senator's stance on the topic based on faction, archetype, and traits.
    
    Args:
        topic: Debate topic
        senator: Senator information
        speech_params: Generated speech parameters
        faction_stance: Known faction stances
        
    Returns:
        String indicating stance ("support", "oppose", or "neutral/mixed")
    """
    faction = senator.get("faction", "")
    archetype = speech_params.get("primary", "traditionalist")
    
    # Check if faction stance is provided
    if faction_stance and faction in faction_stance:
        # 70% chance to follow faction line
        if random.random() < 0.7:
            return faction_stance[faction]
    
    # Archetype tendencies
    archetype_bias = {
        "traditionalist": {"support": 0.3, "oppose": 0.5, "neutral": 0.2},
        "pragmatist": {"support": 0.4, "oppose": 0.3, "neutral": 0.3},
        "philosopher": {"support": 0.3, "oppose": 0.3, "neutral": 0.4},
        "populist": {"support": 0.5, "oppose": 0.4, "neutral": 0.1},
        "militarist": {"support": 0.4, "oppose": 0.5, "neutral": 0.1}
    }
    
    # Get the bias for this archetype
    bias = archetype_bias.get(archetype, {"support": 0.33, "oppose": 0.33, "neutral": 0.34})
    
    # Use the bias to determine stance
    rand = random.random()
    if rand < bias["support"]:
        return "support"
    elif rand < bias["support"] + bias["oppose"]:
        return "oppose"
    else:
        return "neutral"

def extract_key_points(speech_text: str, count: int = 3) -> List[str]:
    """
    Extract key points from a speech for summary.
    
    Args:
        speech_text: Full speech text
        count: Number of key points to extract
        
    Returns:
        List of key point strings
    """
    # Split into sentences
    sentences = re.split(r'[.!?]\s+', speech_text)
    sentences = [s.strip() + "." for s in sentences if s.strip()]
    
    if len(sentences) <= count:
        return sentences
    
    # Extract significant sentences as key points
    # Priority: sentences with strong statements, rhetorical questions, or references
    
    # Score sentences by features that suggest importance
    scored_sentences = []
    for sentence in sentences:
        score = 0
        
        # Length (medium sentences often contain main points)
        words = len(sentence.split())
        if 10 <= words <= 25:
            score += 2
        
        # Contains strong indicator words
        indicators = ["must", "should", "crucial", "essential", "vital", "important",
                     "urge", "propose", "believe", "argue", "insist", "critical"]
        score += sum(2 for word in indicators if word.lower() in sentence.lower())
        
        # Contains a rhetorical question
        if "?" in sentence:
            score += 3
        
        # References to Rome or Republic
        if any(word in sentence.lower() for word in ["rome", "republic", "roman", "senate"]):
            score += 2
        
        # First or last sentence bonus (often contain key points)
        if sentence == sentences[0]:
            score += 3
        elif sentence == sentences[-1]:
            score += 3
        
        scored_sentences.append((sentence, score))
    
    # Sort by score and take the top 'count'
    scored_sentences.sort(key=lambda x: x[1], reverse=True)
    return [s[0] for s in scored_sentences[:count]]

def extract_mentioned_senators(speech_text: str, previous_speeches: Optional[List[Dict]] = None) -> List[int]:
    """
    Extract mentions of other senators from the speech.
    
    Args:
        speech_text: The speech text
        previous_speeches: Previous speeches in the debate
        
    Returns:
        List of senator IDs mentioned
    """
    mentioned_ids = []
    
    if not previous_speeches:
        return mentioned_ids
    
    for speech in previous_speeches:
        senator_name = speech.get("senator_name", "")
        senator_id = speech.get("senator_id", 0)
        
        # Check if this senator's name appears in the speech
        if senator_name and senator_name in speech_text:
            if senator_id not in mentioned_ids:
                mentioned_ids.append(senator_id)
    
    return mentioned_ids

def format_speech_output(senator: Dict, speech_data: Dict) -> Dict:
    """Format the speech output in a way compatible with the existing system."""
    # This function helps ensure compatibility with the existing display and processing code
    
    output = {
        "text": speech_data.get("text", ""),
        "senator_name": senator.get("name", "Unknown Senator"),
        "senator_id": senator.get("id", 0),
        "faction": senator.get("faction", ""),
        "topic": speech_data.get("topic", ""),
        "stance": speech_data.get("stance", "neutral"),
        "points": speech_data.get("points", []),
        "mentioned_senators": speech_data.get("mentioned_senators", []),
        "responding_to": speech_data.get("responding_to")
    }
    
    # Add extended metadata if available
    for key in ["archetype", "selected_devices", "evaluation", "speech_structure", "latin_version"]:
        if key in speech_data:
            output[key] = speech_data[key]
    
    return output