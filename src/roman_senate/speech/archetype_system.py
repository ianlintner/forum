#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Roman Senate AI Game
Archetype System Module

This module handles the determination of senator archetypes (personality types)
and their influence on speech generation.
"""

import random
from typing import Dict, Any, Tuple, List

# Define the available archetypes
ARCHETYPES = [
    "traditionalist",
    "pragmatist", 
    "philosopher",
    "populist",
    "militarist"
]

# Archetype parameters for speech generation
ARCHETYPE_PARAMETERS = {
    "traditionalist": {
        "exordium_style": "formal_ancestral",
        "narratio_focus": "historical_precedent",
        "argument_style": "tradition_based",
        "peroratio_style": "duty_honor_focus",
        "preferred_devices": ["exemplum", "sententia", "anaphora", "tricolon"],
        "latin_usage": "heavy",
        "formality_level": 0.9,
        "sentence_complexity": 0.8,
        "historical_references": 0.9,
        "moral_appeals": 0.7,
        "emotional_appeals": 0.3,
        "logical_appeals": 0.6
    },
    "pragmatist": {
        "exordium_style": "direct_purposeful",
        "narratio_focus": "practical_context",
        "argument_style": "results_oriented",
        "peroratio_style": "benefit_summary",
        "preferred_devices": ["ratiocinatio", "distributio", "antithesis", "asyndeton"],
        "latin_usage": "moderate",
        "formality_level": 0.6,
        "sentence_complexity": 0.5,
        "historical_references": 0.4,
        "moral_appeals": 0.3,
        "emotional_appeals": 0.2,
        "logical_appeals": 0.9
    },
    "philosopher": {
        "exordium_style": "abstract_principle",
        "narratio_focus": "philosophical_context",
        "argument_style": "abstract_reasoning",
        "peroratio_style": "principle_restatement",
        "preferred_devices": ["syllogismus", "definitio", "analogia", "rhetorical_question"],
        "latin_usage": "sophisticated",
        "formality_level": 0.8,
        "sentence_complexity": 0.9,
        "historical_references": 0.6,
        "moral_appeals": 0.6,
        "emotional_appeals": 0.2,
        "logical_appeals": 0.9
    },
    "populist": {
        "exordium_style": "direct_emotional_appeal",
        "narratio_focus": "common_experience",
        "argument_style": "moralistic_emotional",
        "peroratio_style": "emotional_call_to_action",
        "preferred_devices": ["pathos", "interrogatio", "exclamatio", "anaphora"],
        "latin_usage": "simple",
        "formality_level": 0.3,
        "sentence_complexity": 0.4,
        "historical_references": 0.3,
        "moral_appeals": 0.8,
        "emotional_appeals": 0.9,
        "logical_appeals": 0.4
    },
    "militarist": {
        "exordium_style": "direct_assertive",
        "narratio_focus": "threat_assessment",
        "argument_style": "security_focused",
        "peroratio_style": "call_to_strength",
        "preferred_devices": ["asyndeton", "hyperbole", "enumeratio", "anaphora"],
        "latin_usage": "command_oriented",
        "formality_level": 0.5,
        "sentence_complexity": 0.4,
        "historical_references": 0.6,
        "moral_appeals": 0.5,
        "emotional_appeals": 0.6,
        "logical_appeals": 0.5
    }
}

# Archetype rhetoric weights for device selection
ARCHETYPE_RHETORIC_WEIGHTS = {
    "traditionalist": {
        "anaphora": 0.5,       # Repetition at beginning of clauses
        "tricolon": 0.7,       # Series of three elements
        "antithesis": 0.6,     # Contrasting ideas in parallel structure
        "chiasmus": 0.3,       # Reversed grammatical structure
        "alliteration": 0.4,   # Repetition of consonant sounds
        "asyndeton": 0.3,      # Omission of conjunctions
        "polysyndeton": 0.5,   # Multiple conjunctions
        "praeteritio": 0.7,    # Pretending to pass over something
        "rhetorical_question": 0.4,  # Question for effect
        "exemplum": 0.9,       # Historical examples
        "sententia": 0.8       # Aphoristic statements
    },
    "pragmatist": {
        "anaphora": 0.3,
        "tricolon": 0.5,
        "antithesis": 0.7,
        "chiasmus": 0.2,
        "alliteration": 0.1,
        "asyndeton": 0.6,
        "polysyndeton": 0.3,
        "praeteritio": 0.4,
        "rhetorical_question": 0.3,
        "exemplum": 0.5,
        "sententia": 0.4,
        "ratiocinatio": 0.9,    # Logical reasoning
        "distributio": 0.8      # Systematic division of arguments
    },
    "philosopher": {
        "anaphora": 0.4,
        "tricolon": 0.6,
        "antithesis": 0.8,
        "chiasmus": 0.7,
        "alliteration": 0.2,
        "asyndeton": 0.4,
        "polysyndeton": 0.4,
        "praeteritio": 0.3,
        "rhetorical_question": 0.8,
        "exemplum": 0.5,
        "sententia": 0.6,
        "syllogismus": 0.9,     # Formal logical arguments
        "definitio": 0.8,       # Careful definition of terms
        "analogia": 0.7         # Analogical reasoning
    },
    "populist": {
        "anaphora": 0.8,
        "tricolon": 0.6,
        "antithesis": 0.5,
        "chiasmus": 0.2,
        "alliteration": 0.6,
        "asyndeton": 0.5,
        "polysyndeton": 0.6,
        "praeteritio": 0.4,
        "rhetorical_question": 0.9,
        "exemplum": 0.7,
        "sententia": 0.5,
        "exclamatio": 0.8,      # Exclamation for emphasis
        "pathos": 0.9           # Emotional appeals
    },
    "militarist": {
        "anaphora": 0.6,
        "tricolon": 0.5,
        "antithesis": 0.5,
        "chiasmus": 0.2,
        "alliteration": 0.5,
        "asyndeton": 0.8,
        "polysyndeton": 0.3,
        "praeteritio": 0.5,
        "rhetorical_question": 0.5,
        "exemplum": 0.6,
        "sententia": 0.4,
        "hyperbole": 0.7,       # Exaggeration for effect
        "enumeratio": 0.8       # Detailed listing of points
    }
}

def determine_archetype(senator: Dict[str, Any]) -> Dict[str, Any]:
    """
    Determine a senator's primary and secondary archetypes based on traits and faction.
    
    Args:
        senator: Dictionary containing senator information including traits and faction
    
    Returns:
        Dictionary with primary and secondary archetypes and their scores
    """
    # Extract traits with defaults if missing
    traits = senator.get("traits", {}) or {}
    eloquence = traits.get("eloquence", 0.5)
    corruption = traits.get("corruption", 0.2)
    loyalty = traits.get("loyalty", 0.7)
    
    # Add randomness for variety
    rand_factor = random.uniform(-0.1, 0.1)
    
    # Calculate archetype affinities
    traditionalist_score = (loyalty * 0.6) + (0.3 * (1 - corruption)) + rand_factor
    pragmatist_score = ((1 - loyalty) * 0.4) + (0.4 * (1 - corruption)) + rand_factor
    philosopher_score = (eloquence * 0.7) + (0.2 * (1 - corruption)) + rand_factor
    populist_score = ((1 - eloquence) * 0.3) + (corruption * 0.4) + rand_factor
    militarist_score = (loyalty * 0.4) + (0.3 * corruption) + rand_factor
    
    # Adjust based on faction (provides bias but doesn't guarantee)
    if senator.get("faction") == "Optimates":
        traditionalist_score += 0.2
        philosopher_score += 0.1
    elif senator.get("faction") == "Populares":
        populist_score += 0.2
        pragmatist_score += 0.1
    elif senator.get("faction") == "Military":
        militarist_score += 0.3
    elif senator.get("faction") == "Religious":
        traditionalist_score += 0.2
    elif senator.get("faction") == "Merchant":
        pragmatist_score += 0.2
        
    # Compile all scores
    scores = {
        "traditionalist": min(1.0, max(0.0, traditionalist_score)),
        "pragmatist": min(1.0, max(0.0, pragmatist_score)),
        "philosopher": min(1.0, max(0.0, philosopher_score)),
        "populist": min(1.0, max(0.0, populist_score)),
        "militarist": min(1.0, max(0.0, militarist_score))
    }
    
    # Determine primary archetype
    primary_archetype = max(scores, key=scores.get)
    primary_score = scores[primary_archetype]
    
    # Get secondary archetype
    scores_copy = scores.copy()
    scores_copy.pop(primary_archetype)
    secondary_archetype = max(scores_copy, key=scores_copy.get)
    secondary_score = scores_copy[secondary_archetype]
    
    return {
        "primary": primary_archetype,
        "secondary": secondary_archetype,
        "primary_score": primary_score,
        "secondary_score": secondary_score,
        "all_scores": scores
    }

def generate_archetype_parameters(senator: Dict[str, Any], archetype_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate speech parameters based on a senator's archetype information.
    
    Args:
        senator: Dictionary containing senator information
        archetype_info: Archetype information from determine_archetype()
    
    Returns:
        Dictionary of parameters for speech generation
    """
    primary = archetype_info["primary"]
    secondary = archetype_info["secondary"]
    primary_score = archetype_info["primary_score"]
    secondary_score = archetype_info["secondary_score"]
    
    # Normalize influence weights
    total_weight = primary_score + secondary_score
    primary_weight = primary_score / total_weight
    secondary_weight = secondary_score / total_weight
    
    # Get base parameters for both archetypes
    primary_params = ARCHETYPE_PARAMETERS[primary].copy()
    secondary_params = ARCHETYPE_PARAMETERS[secondary].copy()
    
    # Merge parameter dictionaries with weighted influence
    merged_params = {}
    for key in primary_params:
        if isinstance(primary_params[key], (int, float)) and isinstance(secondary_params.get(key, 0), (int, float)):
            # Numeric values are weighted averages
            merged_params[key] = (primary_params[key] * primary_weight) + (secondary_params.get(key, 0) * secondary_weight)
        elif isinstance(primary_params[key], list) and isinstance(secondary_params.get(key, []), list):
            # Lists (like preferred devices) are merged with more items from primary
            primary_items = primary_params[key]
            secondary_items = secondary_params.get(key, [])
            # Take all primary items and some secondary items based on weight
            num_secondary = max(1, int(len(secondary_items) * secondary_weight))
            merged_params[key] = primary_items + random.sample(secondary_items, min(num_secondary, len(secondary_items)))
        else:
            # Non-numeric, non-list values default to primary
            merged_params[key] = primary_params[key]
    
    # Add faction influence
    faction = senator.get("faction", "")
    merged_params["faction"] = faction
    
    # Adjust based on senator's traits
    traits = senator.get("traits", {}) or {}
    eloquence = traits.get("eloquence", 0.5)
    corruption = traits.get("corruption", 0.2)
    loyalty = traits.get("loyalty", 0.7)
    
    # Apply trait modifications
    merged_params["sentence_complexity"] = min(1.0, merged_params.get("sentence_complexity", 0.5) * (1.0 + (eloquence - 0.5)))
    merged_params["moral_appeals"] = max(0.1, merged_params.get("moral_appeals", 0.5) * (1.0 - corruption))
    
    # Add rhetoric weights
    merged_params["rhetoric_weights"] = merge_rhetoric_weights(
        ARCHETYPE_RHETORIC_WEIGHTS[primary],
        ARCHETYPE_RHETORIC_WEIGHTS[secondary],
        primary_weight,
        secondary_weight
    )
    
    return merged_params

def merge_rhetoric_weights(primary_weights: Dict[str, float], secondary_weights: Dict[str, float], 
                           primary_weight: float, secondary_weight: float) -> Dict[str, float]:
    """Merge rhetorical device weights from two archetypes."""
    merged = {}
    
    # Add all primary weights
    for device, weight in primary_weights.items():
        merged[device] = weight * primary_weight
    
    # Add or update with secondary weights
    for device, weight in secondary_weights.items():
        if device in merged:
            merged[device] += weight * secondary_weight
        else:
            merged[device] = weight * secondary_weight
    
    # Normalize to ensure some weights are still close to 1.0
    max_value = max(merged.values())
    if max_value > 0:
        scaling_factor = 1.0 / max_value
        for device in merged:
            merged[device] *= scaling_factor
    
    return merged

def select_rhetorical_devices(archetype_params: Dict[str, Any], eloquence: float, 
                             count: int = 3) -> List[str]:
    """
    Select rhetorical devices appropriate for a given archetype and eloquence level.
    
    Args:
        archetype_params: Parameters from generate_archetype_parameters()
        eloquence: Senator's eloquence trait (0.0-1.0)
        count: Number of devices to select
    
    Returns:
        List of selected rhetorical device names
    """
    rhetoric_weights = archetype_params.get("rhetoric_weights", {})
    
    # Adjust weights based on eloquence
    adjusted_weights = {}
    for device, weight in rhetoric_weights.items():
        # More eloquent senators can use more complex devices
        complexity_modifier = 1.0
        if device in ["chiasmus", "syllogismus", "analogia"]:
            complexity_modifier = 0.5 + eloquence
        elif device in ["anaphora", "tricolon", "alliteration"]:
            complexity_modifier = 0.8 + (0.4 * eloquence)
        
        adjusted_weights[device] = weight * complexity_modifier
    
    # Select devices based on weights
    devices = list(adjusted_weights.keys())
    weights = [adjusted_weights[d] for d in devices]
    
    # Normalize weights to sum to 1.0
    weight_sum = sum(weights)
    if weight_sum > 0:
        normalized_weights = [w/weight_sum for w in weights]
        
        # Select devices without replacement
        selected = []
        remaining_devices = devices.copy()
        remaining_weights = normalized_weights.copy()
        
        for _ in range(min(count, len(devices))):
            if not remaining_devices:
                break
                
            # Convert to probability distribution and select
            weight_sum = sum(remaining_weights)
            if weight_sum <= 0:
                # If all weights are zero, select randomly
                idx = random.randrange(len(remaining_devices))
            else:
                # Normalize and select based on weights
                probs = [w/weight_sum for w in remaining_weights]
                idx = random.choices(range(len(remaining_devices)), probs, k=1)[0]
                
            selected.append(remaining_devices.pop(idx))
            remaining_weights.pop(idx)
            
        return selected
    else:
        # Fallback to random selection if all weights are zero
        return random.sample(devices, min(count, len(devices)))