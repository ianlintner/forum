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
import logging
from typing import Dict, List, Optional, Any, Tuple

# Import submodules from the speech framework
from . import archetype_system
from . import rhetorical_devices
from . import historical_context
from . import classical_structure
from . import latin_flourishes

# Import existing LLM integration capabilities
from ..utils.llm.factory import get_llm_provider
from ..utils.config import LLM_PROVIDER, LLM_MODEL

# Setup logging
logger = logging.getLogger(__name__)

# Initialize the LLM provider based on configuration
# We'll create providers on-demand based on task type
# Speech generation will use the high-quality speech tier
# Other operations will use appropriate tiers
def get_speech_llm_provider():
    """Get a speech-tier LLM provider"""
    try:
        return get_llm_provider(provider_type=LLM_PROVIDER, task_type="speech")
    except Exception as e:
        logger.warning(f"Could not initialize speech LLM provider: {e}")
        return None

def get_reasoning_llm_provider():
    """Get a reasoning-tier LLM provider"""
    try:
        return get_llm_provider(provider_type=LLM_PROVIDER, task_type="reasoning")
    except Exception as e:
        logger.warning(f"Could not initialize reasoning LLM provider: {e}")
        return None

def get_simple_llm_provider():
    """Get a simple-tier LLM provider for basic tasks"""
    try:
        return get_llm_provider(provider_type=LLM_PROVIDER, task_type="simple")
    except Exception as e:
        logger.warning(f"Could not initialize simple LLM provider: {e}")
        return None

def generate_speech(
    senator: Dict,
    topic: str,
    faction_stance: Dict = None,
    year: int = None,
    responding_to: Optional[Dict] = None,
    previous_speeches: Optional[List[Dict]] = None,
    use_llm: bool = False,
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
        use_llm: Whether to use LLM for enhancement (if available)
        
    Returns:
        Dict: Speech data including the full text, key points,
              rhetorical devices used, historical references included, and metadata.
    """
    # Use default year if not provided
    if year is None:
        year = -80  # Default to late Republic
    
    logger.info(f"Generating speech for {senator.get('name', 'Unknown Senator')} on topic: {topic}")
    
    # 1. Determine senator's archetype
    logger.debug("Determining senator archetype")
    archetype_info = archetype_system.determine_archetype(senator)
    
    # 2. Generate speech parameters based on archetype
    logger.debug(f"Generating speech parameters for {archetype_info['primary']} archetype")
    speech_params = archetype_system.generate_archetype_parameters(senator, archetype_info)
    
    # 3. Get historical context for the year
    logger.debug(f"Getting historical context for year {year}")
    hist_context = historical_context.get_historical_context_for_speech(year, topic)
    
    # 4. Generate a structured speech according to classical rhetoric
    logger.debug("Generating speech structure")
    speech_structure = classical_structure.generate_speech_structure(
        senator,
        topic,
        speech_params,
        hist_context,
        responding_to
    )
    
    # 5. Expand the structure into actual content
    logger.debug("Expanding speech structure into content")
    expanded_structure = classical_structure.expand_speech_structure(
        speech_structure,
        topic,
        speech_params,
        hist_context
    )
    
    # 6. Assemble the basic speech text
    logger.debug("Assembling basic speech")
    basic_speech_text = classical_structure.assemble_full_speech(expanded_structure)
    
    # 7. Select and apply rhetorical devices
    logger.debug("Applying rhetorical devices")
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
    logger.debug("Adding Latin flourishes")
    latin_usage_level = speech_params.get("formality_level", 0.5)
    english_with_latin = latin_flourishes.add_latin_flourish(
        enhanced_speech_text,
        flourish_level=latin_usage_level,
        archetype=archetype_info["primary"]
    )
    
    # 9. Add Latin opening
    final_speech_text = latin_flourishes.add_latin_opening(english_with_latin, year)
    
    # 10. Determine stance on topic based on faction and archetype
    stance = determine_stance(topic, senator, speech_params, faction_stance)
    
    # 11. Extract key points and build speech data
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
        "points": extract_key_points(final_speech_text, 3),
        "mentioned_senators": extract_mentioned_senators(final_speech_text, previous_speeches),
        "responding_to": responding_to.get("senator_id") if responding_to else None
    }
    
    # 12. Optionally enhance with LLM if available and requested
    if use_llm:
        logger.info("Enhancing speech with LLM")
        try:
            enhanced_text = enhance_speech_with_llm(
                speech_data["text"],
                senator,
                archetype_info["primary"],
                topic,
                stance
            )
            if enhanced_text:
                speech_data["text"] = enhanced_text
                # Re-extract key points with enhanced text
                speech_data["points"] = extract_key_points(enhanced_text, 3)
        except Exception as e:
            logger.error(f"Error enhancing speech with LLM: {e}")
    
    logger.info(f"Speech generation complete: {len(speech_data['text'])} characters")
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
        String indicating stance ("support", "oppose", or "neutral")
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

def enhance_speech_with_llm(speech_text: str, senator: Dict, archetype: str, topic: str, stance: str) -> Optional[str]:
    """
    Enhance a generated speech using the LLM provider.
    
    Args:
        speech_text: The generated speech text
        senator: Senator information
        archetype: Primary archetype
        topic: Debate topic
        stance: Senator's stance on the topic
        
    Returns:
        Enhanced speech text or None if enhancement failed
    """
    # Use our high-quality speech tier model
    speech_provider = get_speech_llm_provider()
    if not speech_provider:
        logger.warning("No speech LLM provider available for speech enhancement")
        return None
    
    prompt = f"""
You are assisting with generating Roman Senate speeches in a historical simulation.
Enhance the following speech while preserving its core arguments, structure, and Latin phrases.
The speech should maintain its {archetype} personality archetype and {stance} stance on the topic of {topic}.

Original speech:
{speech_text}

Please provide an enhanced version that:
1. Maintains all Latin phrases (marked with parentheses for translations)
2. Preserves the original stance and arguments
3. Adds natural flow between sections
4. Improves rhetorical quality while maintaining historical authenticity
5. Keeps approximately the same length
"""

    try:
        enhanced_text = speech_provider.generate_completion(
            prompt=prompt,
            temperature=0.7,
            max_tokens=len(speech_text.split()) + 100  # Allow some expansion
        )
        return enhanced_text
    except Exception as e:
        logger.error(f"Error in LLM enhancement: {e}")
        return None

def generate_response_speech(senator: Dict, topic: str, original_speech: Dict, 
                           year: int = None, previous_speeches: Optional[List[Dict]] = None,
                           use_llm: bool = False) -> Dict:
    """
    Generate a speech that directly responds to another speech.
    
    Args:
        senator: The responding senator
        topic: The debate topic
        original_speech: The speech being responded to
        year: Historical year
        previous_speeches: Previous speeches in the debate
        use_llm: Whether to use LLM enhancement
        
    Returns:
        Speech data for the response
    """
    # Generate a normal speech but with responding_to parameter set
    speech = generate_speech(
        senator=senator,
        topic=topic,
        year=year,
        responding_to=original_speech,
        previous_speeches=previous_speeches,
        use_llm=use_llm
    )
    
    # Add a reference to the original speaker in the speech text if not present
    original_speaker = original_speech.get("senator_name", "the previous speaker")
    if original_speaker not in speech["text"]:
        # Inject a reference at a suitable point (preferably in refutatio)
        structure = speech.get("speech_structure", {})
        if "refutatio" in structure:
            refutatio = structure["refutatio"]
            modified_refutatio = f"As {original_speaker} has stated, but I must disagree. {refutatio}"
            structure["refutatio"] = modified_refutatio
            
            # Reassemble the speech
            parts_order = ["exordium", "narratio", "partitio", "confirmatio", "refutatio", "peroratio"]
            speech_parts = []
            for part in parts_order:
                if part in structure:
                    speech_parts.append(structure[part])
            
            speech["text"] = " ".join(speech_parts)
    
    return speech