#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Roman Senate AI Game
Speech Options Generator Module

This module generates multiple speech alternatives for players to choose from,
providing meaningful variations in stance, rhetorical style, and content.
"""

import random
from typing import Dict, List, Optional, Any, Tuple

# Import from the existing speech generation framework
from . import speech_generator
from . import archetype_system
from . import rhetorical_devices
from . import classical_structure
from . import latin_flourishes
from . import historical_context

def generate_speech_options(
    senator: Dict,
    topic: str,
    context: Dict = None,
    previous_speeches: Optional[List[Dict]] = None,
    count: int = 3
) -> List[Dict]:
    """
    Generate multiple speech options for the player to choose from, with meaningful
    variations in stance, rhetorical style, and content.
    
    Args:
        senator: Dictionary containing senator information
        topic: The debate topic
        context: Optional additional context (year, faction stances, etc.)
        previous_speeches: Optional list of previous speeches in the debate
        count: Number of options to generate (default 3)
        
    Returns:
        List of speech option dictionaries, each containing:
        - summary: Brief preview shown to player
        - stance: "support", "oppose", "neutral"
        - latin_text: Latin version of speech
        - english_text: English version of speech
        - full_text: Complete speech text with Latin phrases
        - devices_used: List of rhetorical devices used
        - key_points: Key points extracted from the speech
    """
    # Extract context variables or set defaults
    year = context.get("year") if context else None
    faction_stance = context.get("faction_stance") if context else None
    responding_to = context.get("responding_to") if context else None
    
    # Generate varied stances 
    stances = create_varied_stances(senator, topic, count)
    
    # Generate rhetorical approaches
    rhetorical_approaches = create_varied_rhetorical_approaches(senator, count)
    
    # Generate options
    options = []
    for i in range(count):
        # Create a customized set of parameters for this option
        option_params = {
            "stance": stances[i % len(stances)],
            "rhetorical_approach": rhetorical_approaches[i % len(rhetorical_approaches)],
            "structure_variation": generate_structure_variation(),
            "historical_focus": choose_historical_focus(year)
        }
        
        # Generate a speech with these parameters
        speech = generate_option_speech(
            senator, 
            topic, 
            option_params,
            faction_stance, 
            year, 
            responding_to, 
            previous_speeches
        )
        
        # Add a summary for player selection
        summary = generate_option_summary(speech)
        
        # Format the speech option
        speech_option = {
            "summary": summary,
            "stance": speech["stance"],
            "latin_text": speech.get("latin_version", ""),
            "english_text": speech.get("text", "").replace("(", "").replace(")", ""),  # Remove Latin parentheticals
            "full_text": speech.get("text", ""),
            "devices_used": speech.get("selected_devices", []),
            "key_points": speech.get("points", [])
        }
        
        options.append(speech_option)
    
    return options

def generate_option_speech(
    senator: Dict,
    topic: str,
    option_params: Dict,
    faction_stance: Dict = None,
    year: int = None,
    responding_to: Optional[Dict] = None,
    previous_speeches: Optional[List[Dict]] = None
) -> Dict:
    """
    Generate a single speech option using the existing speech generation framework
    but with customized parameters for variation.
    
    Args:
        senator: Dictionary containing senator information
        topic: The debate topic
        option_params: Parameters specific to this option
        faction_stance: Optional faction stances
        year: Optional year in Roman history
        responding_to: Optional senator/speech being responded to
        previous_speeches: Optional previous speeches
        
    Returns:
        Dictionary containing the generated speech and metadata
    """
    # Clone the senator to avoid modifying the original
    modified_senator = senator.copy()
    
    # Temporary trait modifications to influence archetype selection
    # (will be determined by the rhetorical approach)
    if "traits" in modified_senator:
        traits = modified_senator["traits"].copy()
    else:
        traits = {}
    
    # Modify traits based on rhetorical approach to influence archetype
    rhetorical_approach = option_params["rhetorical_approach"]
    if rhetorical_approach == "traditional":
        traits["eloquence"] = min(1.0, (traits.get("eloquence", 0.5) + 0.2))
        traits["loyalty"] = min(1.0, (traits.get("loyalty", 0.5) + 0.3))
    elif rhetorical_approach == "passionate":
        traits["eloquence"] = min(1.0, (traits.get("eloquence", 0.5) + 0.3))
        traits["corruption"] = min(1.0, (traits.get("corruption", 0.2) + 0.2))
    elif rhetorical_approach == "logical":
        traits["eloquence"] = min(1.0, (traits.get("eloquence", 0.5) + 0.2))
        traits["corruption"] = max(0.0, (traits.get("corruption", 0.2) - 0.1))
    elif rhetorical_approach == "combative":
        traits["corruption"] = min(1.0, (traits.get("corruption", 0.2) + 0.3))
        traits["loyalty"] = max(0.0, (traits.get("loyalty", 0.7) - 0.2))
    elif rhetorical_approach == "diplomatic":
        traits["eloquence"] = min(1.0, (traits.get("eloquence", 0.5) + 0.1))
        traits["loyalty"] = min(1.0, (traits.get("loyalty", 0.7) + 0.1))
    
    modified_senator["traits"] = traits
    
    # Override faction stance to match the desired stance for this option
    custom_faction_stance = None
    if faction_stance:
        custom_faction_stance = faction_stance.copy()
    else:
        custom_faction_stance = {}
    
    faction = modified_senator.get("faction", "")
    if faction:
        custom_faction_stance[faction] = option_params["stance"]
    
    # Use the existing speech generator with our modifications
    speech = speech_generator.generate_speech(
        senator=modified_senator,
        topic=topic,
        faction_stance=custom_faction_stance,
        year=year,
        responding_to=responding_to,
        previous_speeches=previous_speeches
    )
    
    # Apply structural variation based on the option parameters
    structure_variation = option_params["structure_variation"]
    speech = apply_structure_variation(speech, structure_variation)
    
    return speech

def apply_structure_variation(speech: Dict, variation: str) -> Dict:
    """
    Modify a speech to apply structural variations without completely regenerating it.
    
    Args:
        speech: The original speech dictionary
        variation: The type of structural variation to apply
        
    Returns:
        Modified speech dictionary
    """
    # Get the original text
    original_text = speech.get("text", "")
    
    if variation == "formal":
        # For formal variation, we'd ideally regenerate with more formal parameters
        # But for a simple implementation, we'll just note this in the speech metadata
        speech["structure_style"] = "formal"
    
    elif variation == "emotionally_charged":
        # Add emotional emphasis markers and exclamations
        modified_text = original_text
        sentences = modified_text.split(". ")
        for i in range(len(sentences)):
            if random.random() < 0.3 and not sentences[i].endswith("!"):
                sentences[i] = sentences[i] + "!"
        
        speech["text"] = ". ".join(sentences)
        speech["structure_style"] = "emotionally_charged"
    
    elif variation == "concise":
        # A more concise speech would be shorter, but for now we'll just note it
        speech["structure_style"] = "concise"
    
    elif variation == "elaborate":
        # An elaborate speech would be longer, but for now we'll just note it
        speech["structure_style"] = "elaborate"
    
    return speech

def create_varied_stances(senator: Dict, topic: str, count: int = 3) -> List[str]:
    """
    Generate different stance options (support/oppose/neutral) for a speech.
    Ensures variety while still being plausible for the senator.
    
    Args:
        senator: Dictionary containing senator information
        topic: The debate topic
        count: Number of stances to generate
        
    Returns:
        List of stance strings ("support", "oppose", "neutral")
    """
    # Always include all three stances for maximum player choice
    stances = ["support", "oppose", "neutral"]
    
    # If we need fewer than 3, prioritize the most likely stances for this senator
    if count < 3:
        faction = senator.get("faction", "")
        traits = senator.get("traits", {})
        
        # Determine which stance is most likely for this senator (simplified logic)
        if faction == "Optimates":
            # Optimates tend to be conservative
            stances = ["oppose", "neutral", "support"]
        elif faction == "Populares":
            # Populares tend to support popular measures
            stances = ["support", "neutral", "oppose"]
        elif faction == "Military":
            # Military faction might favor security/strength
            stances = ["support", "oppose", "neutral"]
        elif faction == "Merchant":
            # Merchants might be pragmatic
            stances = ["neutral", "support", "oppose"]
        else:
            # Randomize for other factions
            random.shuffle(stances)
            
        # Take only the number requested
        stances = stances[:count]
    
    # Shuffle to avoid predictable ordering
    random.shuffle(stances)
    
    return stances

def create_varied_rhetorical_approaches(senator: Dict, count: int = 3) -> List[str]:
    """
    Generate different rhetorical approaches for speeches.
    
    Args:
        senator: Dictionary containing senator information
        count: Number of approaches to generate
        
    Returns:
        List of rhetorical approach strings
    """
    # Define all possible approaches
    all_approaches = [
        "traditional",    # Appeals to tradition, precedent, ancestral wisdom
        "passionate",     # Emotional appeals, dramatic language
        "logical",        # Structured reasoning, evidence-based
        "combative",      # Aggressive, directly challenging opponents
        "diplomatic"      # Balanced, seeking consensus, moderate
    ]
    
    # Consider senator traits to determine which approaches are most plausible
    traits = senator.get("traits", {})
    faction = senator.get("faction", "")
    
    # Scoring approaches based on senator characteristics (simplified)
    scores = {}
    eloquence = traits.get("eloquence", 0.5)
    corruption = traits.get("corruption", 0.2)
    loyalty = traits.get("loyalty", 0.7)
    
    scores["traditional"] = loyalty * 0.7 + (1 - corruption) * 0.3
    scores["passionate"] = (1 - loyalty) * 0.4 + corruption * 0.3 + eloquence * 0.3
    scores["logical"] = eloquence * 0.6 + (1 - corruption) * 0.4
    scores["combative"] = corruption * 0.5 + (1 - loyalty) * 0.3 + eloquence * 0.2
    scores["diplomatic"] = (1 - corruption) * 0.4 + loyalty * 0.3 + eloquence * 0.3
    
    # Faction influences
    if faction == "Optimates":
        scores["traditional"] += 0.2
    elif faction == "Populares":
        scores["passionate"] += 0.2
    elif faction == "Military":
        scores["combative"] += 0.2
    elif faction == "Merchant":
        scores["diplomatic"] += 0.1
        scores["logical"] += 0.1
    
    # Sort approaches by score
    sorted_approaches = sorted(all_approaches, key=lambda a: scores[a], reverse=True)
    
    # Take the top N approaches, but always include some variety
    selected_approaches = sorted_approaches[:count]
    
    # Ensure we have the requested number
    while len(selected_approaches) < count:
        remaining = [a for a in all_approaches if a not in selected_approaches]
        if not remaining:
            break
        selected_approaches.append(random.choice(remaining))
    
    # Shuffle to avoid predictable ordering
    random.shuffle(selected_approaches)
    
    return selected_approaches

def generate_structure_variation() -> str:
    """
    Generate a structural variation type for a speech.
    
    Returns:
        String representing a structure variation
    """
    variations = [
        "formal",              # Strict adherence to classical form
        "emotionally_charged", # More emotional appeals, exclamations
        "concise",             # Shorter, more direct
        "elaborate"            # More detailed, longer
    ]
    
    return random.choice(variations)

def choose_historical_focus(year: Optional[int] = None) -> str:
    """
    Choose a historical focus for a speech.
    
    Args:
        year: Optional year in Roman history
        
    Returns:
        String representing a historical focus
    """
    focuses = [
        "recent_events",    # Focus on recent history
        "ancient_wisdom",   # Focus on early Republic/kings
        "greek_influence",  # Focus on Greek philosophical parallels
        "family_legacy",    # Focus on speaker's family history
        "military_history"  # Focus on military campaigns and leaders
    ]
    
    return random.choice(focuses)

def generate_option_summaries(options: List[Dict]) -> List[str]:
    """
    Generate brief summaries for each speech option.
    
    Args:
        options: List of speech option dictionaries
        
    Returns:
        List of summary strings
    """
    summaries = []
    
    for option in options:
        # Extract relevant information
        stance = option["stance"]
        devices = option["devices_used"]
        structure_style = option.get("structure_style", "balanced")
        
        # Create a stance description
        stance_desc = ""
        if stance == "support":
            stance_desc = "strongly support the proposal"
        elif stance == "oppose":
            stance_desc = "firmly oppose the measure"
        else:
            stance_desc = "take a nuanced position"
        
        # Create a style description
        style_desc = ""
        if "anaphora" in devices or "tricolon" in devices:
            style_desc = "rhetorical flourishes"
        elif "ratiocinatio" in devices or "distributio" in devices:
            style_desc = "logical reasoning"
        elif "exemplum" in devices or "sententia" in devices:
            style_desc = "historical examples"
        elif "pathos" in devices or "exclamatio" in devices:
            style_desc = "emotional appeals"
        else:
            style_desc = "balanced arguments"
        
        # Combine into a summary
        summary = f"A speech that would {stance_desc} using {style_desc}"
        
        # Add structure style if relevant
        if structure_style == "formal":
            summary += " in a formal, traditional manner"
        elif structure_style == "emotionally_charged":
            summary += " with passionate intensity"
        elif structure_style == "concise":
            summary += " in a direct, concise way"
        elif structure_style == "elaborate":
            summary += " with elaborate detail"
        
        summaries.append(summary)
        
        # Also set this as the option's summary
        option["summary"] = summary
    
    return summaries