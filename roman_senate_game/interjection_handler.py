"""
Interjection Handler Module for the Roman Senate Game

This module handles the generation, tracking, and processing of player interjections
during senate debates. It provides functionality to create contextually appropriate
interjection options for players and processes their effects on relationships and
the debate.
"""

import random
from typing import Dict, List, Any, Optional

from interjections import InterjectionType
import logging_utils

# Define the missing utility function
def get_value_with_variance(base_value, variance_factor):
    """
    Get a value with random variance applied.
    
    Args:
        base_value: The base value
        variance_factor: How much variance to apply (0.0-1.0)
        
    Returns:
        Value with random variance
    """
    variance = base_value * variance_factor
    return base_value + random.uniform(-variance, variance)

logger = logging_utils.get_logger()

# Default number of interjections a player has per senate session
DEFAULT_INTERJECTIONS_PER_SESSION = 3

# Base probability adjustments for different interjection types
INTERJECTION_PROBABILITY_ADJUSTMENTS = {
    InterjectionType.ACCLAMATION: 0.3,  # Positive response
    InterjectionType.OBJECTION: 0.3,    # Negative response
    InterjectionType.PROCEDURAL: 0.2,   # Procedural point
    InterjectionType.EMOTIONAL: 0.1,    # Emotional outburst
    InterjectionType.COLLECTIVE: 0.1,   # Collective reaction (rare for player)
}

# Intensity levels and their effect multipliers
INTENSITY_LEVELS = {
    "mild": 0.5,        # Subtle effect
    "moderate": 1.0,    # Standard effect
    "strong": 1.5       # Powerful effect
}


def generate_interjection_options(player_senator: Dict, target_senator: Dict, 
                                 speech_content: Dict, count: int = 3) -> List[Dict]:
    """
    Generate a list of possible interjection options for the player 
    based on the current speech content and speakers.
    
    Args:
        player_senator: The player's senator data
        target_senator: The senator currently speaking
        speech_content: Content and metadata of the current speech
        count: Number of interjection options to generate (default: 3)
        
    Returns:
        List of interjection option dictionaries
    """
    logger.info(f"Generating {count} interjection options for {player_senator['name']}")
    
    # First check if interjection is appropriate
    if not is_interjection_appropriate(player_senator, target_senator, speech_content):
        logger.info("Interjection not appropriate in current context")
        return []
    
    # Filter out interjection types that aren't appropriate for the current context
    available_types = _get_appropriate_interjection_types(
        player_senator, target_senator, speech_content
    )
    
    if not available_types:
        logger.warning("No appropriate interjection types found")
        return []
        
    # Generate the requested number of interjection options
    options = []
    for _ in range(count):
        # Select interjection type based on weighted probabilities
        interjection_type = _select_weighted_interjection_type(available_types)
        
        # Create a unique interjection for this type
        option = _create_interjection_option(
            interjection_type, player_senator, target_senator, speech_content
        )
        
        options.append(option)
        
    # Ensure we have variety in the options
    options = _ensure_option_variety(options)
    
    logger.info(f"Generated {len(options)} interjection options")
    return options


def can_player_interject(player_senator: Dict) -> bool:
    """
    Check if the player has interjections available to use.
    
    Args:
        player_senator: The player's senator data
        
    Returns:
        True if player can interject, False otherwise
    """
    # Check if player has the interjections_remaining field and it's > 0
    return player_senator.get('interjections_remaining', 0) > 0


def is_interjection_appropriate(player_senator: Dict, target_senator: Dict, 
                               speech_content: Dict) -> bool:
    """
    Determine if an interjection is appropriate based on the current context.
    
    Args:
        player_senator: The player's senator data
        target_senator: The senator currently speaking
        speech_content: Content and metadata of the current speech
        
    Returns:
        True if interjection is appropriate, False otherwise
    """
    # Check if player can interject
    if not can_player_interject(player_senator):
        return False
        
    # Don't allow interjecting during your own speech
    if player_senator['id'] == target_senator['id']:
        return False
        
    # Check if presiding official allows interjections
    # This could be extended based on senate rules or presiding official's mood
    if speech_content.get('no_interruptions', False):
        return False
        
    # Check if the speech is at an appropriate point for interjection
    # Some speeches might have sections where interjections are more or less appropriate
    speech_phase = speech_content.get('phase', 'middle')
    if speech_phase == 'conclusion' and speech_content.get('is_final_statement', False):
        # Less appropriate to interject during final statements
        return random.random() > 0.7  # 30% chance to allow anyway
        
    # Could add more context-specific checks here
    
    return True


def process_interjection_effects(player_senator: Dict, target_senator: Dict, 
                                interjection: Dict) -> Dict:
    """
    Process the effects of a player's interjection on relationships and the debate.
    
    Args:
        player_senator: The player's senator data
        target_senator: The senator receiving the interjection
        interjection: The interjection option used
        
    Returns:
        Dictionary containing the effects of the interjection
    """
    # Track that player used an interjection
    player_senator['interjections_remaining'] = player_senator.get('interjections_remaining', 0) - 1
    
    # Calculate base effect magnitude based on intensity
    intensity = interjection.get('intensity', 1.0)
    
    # Apply effects based on interjection type
    effects = {
        'relationship_change': 0,
        'speech_impact': 0,
        'audience_reaction': 0,
        'prestige_change': 0,
        'influence_change': 0,
        'description': ""
    }
    
    interjection_type = interjection.get('type', InterjectionType.OBJECTION)
    
    # Apply relationship effects
    if interjection_type == InterjectionType.ACCLAMATION:
        effects['relationship_change'] = get_value_with_variance(2 * intensity, 0.2)
        effects['prestige_change'] = get_value_with_variance(1 * intensity, 0.2)
        effects['description'] = "Your acclamation was well received."
        
    elif interjection_type == InterjectionType.OBJECTION:
        effects['relationship_change'] = get_value_with_variance(-3 * intensity, 0.2)
        effects['speech_impact'] = get_value_with_variance(-2 * intensity, 0.3)
        effects['description'] = "Your objection created tension in the Senate."
        
    elif interjection_type == InterjectionType.PROCEDURAL:
        effects['prestige_change'] = get_value_with_variance(1.5 * intensity, 0.2)
        effects['influence_change'] = get_value_with_variance(1 * intensity, 0.2)
        effects['description'] = "Your procedural point demonstrated your knowledge of Senate rules."
        
    elif interjection_type == InterjectionType.EMOTIONAL:
        # Emotional effects depend on current relationship
        relationship = player_senator.get('relationships', {}).get(target_senator['id'], 0)
        
        if relationship > 0:  # Positive relationship
            effects['relationship_change'] = get_value_with_variance(1.5 * intensity, 0.3)
            effects['description'] = "Your emotional support strengthened your alliance."
        else:  # Negative relationship
            effects['relationship_change'] = get_value_with_variance(-2 * intensity, 0.3)
            effects['speech_impact'] = get_value_with_variance(-1 * intensity, 0.3)
            effects['description'] = "Your emotional outburst highlighted your opposition."
            
    elif interjection_type == InterjectionType.COLLECTIVE:
        # Collective interjections have more subtle individual effects but larger audience impact
        effects['audience_reaction'] = get_value_with_variance(3 * intensity, 0.3)
        effects['influence_change'] = get_value_with_variance(0.5 * intensity, 0.2)
        effects['description'] = "You successfully swayed the mood of the Senate."
        
    # Log the effects
    logger.info(f"Interjection effects: {effects}")
    
    return effects


def reset_player_interjections(player_senator: Dict, 
                              count: int = DEFAULT_INTERJECTIONS_PER_SESSION) -> None:
    """
    Reset the player's available interjections for a new session.
    
    Args:
        player_senator: The player's senator data
        count: Number of interjections to reset to (default: 3)
    """
    player_senator['interjections_remaining'] = count
    logger.info(f"Reset interjections for {player_senator['name']} to {count}")


# Helper functions

def _get_appropriate_interjection_types(player_senator: Dict, target_senator: Dict, 
                                      speech_content: Dict) -> List[InterjectionType]:
    """
    Determine which interjection types are appropriate given the context.
    
    Args:
        player_senator: The player's senator data
        target_senator: The senator currently speaking
        speech_content: Content and metadata of the current speech
        
    Returns:
        List of appropriate InterjectionType values
    """
    # Start with all types
    available_types = list(InterjectionType)
    
    # Filter based on speech content and senator relationships
    relationship = player_senator.get('relationships', {}).get(target_senator['id'], 0)
    
    # Mood/tone of speech affects available types
    tone = speech_content.get('tone', 'neutral')
    
    # For hostile speeches, reduce likelihood of acclamation
    if tone in ['aggressive', 'hostile'] and relationship < 0:
        if InterjectionType.ACCLAMATION in available_types and random.random() < 0.7:
            available_types.remove(InterjectionType.ACCLAMATION)
            
    # For formal speeches, reduce likelihood of emotional outbursts
    if tone in ['formal', 'serious']:
        if InterjectionType.EMOTIONAL in available_types and random.random() < 0.7:
            available_types.remove(InterjectionType.EMOTIONAL)
            
    # If relationship is very positive, reduce likelihood of objections
    if relationship > 50 and InterjectionType.OBJECTION in available_types:
        if random.random() < 0.7:
            available_types.remove(InterjectionType.OBJECTION)
            
    # Collective type is rare for player interjections as it represents group actions
    if InterjectionType.COLLECTIVE in available_types and random.random() < 0.9:
        available_types.remove(InterjectionType.COLLECTIVE)
            
    # Could add more context-specific filters here
            
    return available_types


def _select_weighted_interjection_type(available_types: List[InterjectionType]) -> InterjectionType:
    """
    Select an interjection type based on weighted probabilities.
    
    Args:
        available_types: List of available InterjectionType values
        
    Returns:
        Selected InterjectionType
    """
    # Create probabilities dictionary for available types
    probabilities = {}
    total_prob = 0
    
    for interjection_type in available_types:
        prob = INTERJECTION_PROBABILITY_ADJUSTMENTS.get(interjection_type, 0.1)
        probabilities[interjection_type] = prob
        total_prob += prob
        
    # Normalize probabilities
    for interjection_type in probabilities:
        probabilities[interjection_type] /= total_prob
        
    # Select based on weighted random choice
    rand_val = random.random()
    cumulative_prob = 0
    
    for interjection_type, prob in probabilities.items():
        cumulative_prob += prob
        if rand_val <= cumulative_prob:
            return interjection_type
            
    # Fallback - should not reach here
    return random.choice(available_types)


def _create_interjection_option(interjection_type: InterjectionType, player_senator: Dict, 
                               target_senator: Dict, speech_content: Dict) -> Dict:
    """
    Create a specific interjection option based on the selected type.
    
    Args:
        interjection_type: The type of interjection to create
        player_senator: The player's senator data
        target_senator: The senator currently speaking
        speech_content: Content and metadata of the current speech
        
    Returns:
        Interjection option dictionary
    """
    # Select intensity level
    intensity_key = random.choice(list(INTENSITY_LEVELS.keys()))
    intensity = INTENSITY_LEVELS[intensity_key]
    
    # Get content based on speech content and interjection type
    content, latin_content = _generate_interjection_content(
        interjection_type, intensity_key, target_senator, speech_content
    )
    
    # Create the option dictionary
    option = {
        "type": interjection_type,
        "content": content,
        "latin_content": latin_content,
        "intensity": intensity,
        "target": target_senator
    }
    
    return option


def _generate_interjection_content(interjection_type: InterjectionType, intensity: str, 
                                  target_senator: Dict, speech_content: Dict) -> tuple:
    """
    Generate the content for an interjection based on type and context.
    
    Args:
        interjection_type: The type of interjection
        intensity: The intensity level ("mild", "moderate", "strong")
        target_senator: The senator currently speaking
        speech_content: Content and metadata of the current speech
        
    Returns:
        Tuple of (content, latin_content)
    """
    # Extract useful information from speech content
    topic = speech_content.get('topic', 'the matter at hand')
    stance = speech_content.get('stance', 'neutral')
    key_points = speech_content.get('key_points', [])
    
    # Base templates for different interjection types
    templates = {
        InterjectionType.ACCLAMATION: {
            "mild": [
                "I support this point.",
                "A fair assessment.",
                "Well observed, {name}."
            ],
            "moderate": [
                "I strongly agree with {name}!",
                "An excellent point about {topic}!",
                "This wisdom must be heeded!"
            ],
            "strong": [
                "Remarkable insight, Senator {name}! The gods themselves would approve!",
                "None could argue against such wisdom on {topic}!",
                "By Jupiter, this is precisely what Rome needs to hear!"
            ]
        },
        InterjectionType.OBJECTION: {
            "mild": [
                "I must respectfully disagree.",
                "That point seems questionable.",
                "I'm not convinced, {name}."
            ],
            "moderate": [
                "That is simply not accurate!",
                "I must object to this characterization of {topic}!",
                "The honorable senator is mistaken!"
            ],
            "strong": [
                "Absolute nonsense! {name} clearly doesn't understand {topic}!",
                "I cannot allow such falsehoods to stand unchallenged!",
                "This is an outrage to the dignity of the Senate!"
            ]
        },
        InterjectionType.PROCEDURAL: {
            "mild": [
                "A point of order, please.",
                "May I make a procedural observation?",
                "On procedural grounds..."
            ],
            "moderate": [
                "The rules of the Senate require us to address {topic} differently.",
                "I call for proper procedure to be followed!",
                "Point of order! This matter requires proper consideration."
            ],
            "strong": [
                "I demand the presiding official enforce the rules of this chamber!",
                "This entire proceeding violates Senate tradition!",
                "We must adhere to proper procedure or our decisions on {topic} are meaningless!"
            ]
        },
        InterjectionType.EMOTIONAL: {
            "mild": [
                "This matter affects me deeply.",
                "I feel strongly about this issue.",
                "My family's honor is touched by this debate."
            ],
            "moderate": [
                "I cannot remain silent when Rome's future is at stake!",
                "As a true Roman, I am moved to speak on {topic}!",
                "My conscience compels me to address the Senate!"
            ],
            "strong": [
                "By the memory of my ancestors, I cannot let this stand!",
                "My blood boils at these words on {topic}!",
                "For the glory of Rome and all we hold sacred!"
            ]
        },
        InterjectionType.COLLECTIVE: {
            "mild": [
                "Many senators share this concern.",
                "I speak for several of my colleagues when I say...",
                "There is broad agreement on this point."
            ],
            "moderate": [
                "The mood of the Senate clearly favors a different approach to {topic}!",
                "My faction stands united on this matter!",
                "Look around you - many share this view!"
            ],
            "strong": [
                "The will of the Senate cannot be ignored! We demand to be heard on {topic}!",
                "A majority of senators reject these assertions!",
                "Rome speaks with one voice on this matter, and it is not yours, {name}!"
            ]
        }
    }
    
    # Latin version templates (simplified for each type and intensity)
    latin_templates = {
        InterjectionType.ACCLAMATION: {
            "mild": "Assentior!",  # I agree
            "moderate": "Optime dictum!",  # Well said
            "strong": "Magnifice! Per Jovem!"  # Magnificent! By Jupiter!
        },
        InterjectionType.OBJECTION: {
            "mild": "Dissentio.",  # I disagree
            "moderate": "Falsum est!",  # That is false
            "strong": "Absurdum! Mendacium!"  # Absurd! A lie!
        },
        InterjectionType.PROCEDURAL: {
            "mild": "Ad ordinem.",  # To order
            "moderate": "Contra morem!",  # Against custom
            "strong": "Leges senatus servandae sunt!"  # The laws of the senate must be observed!
        },
        InterjectionType.EMOTIONAL: {
            "mild": "Moveor...",  # I am moved
            "moderate": "Non possum silere!",  # I cannot be silent
            "strong": "Per manes maiorum!"  # By the spirits of my ancestors!
        },
        InterjectionType.COLLECTIVE: {
            "mild": "Multi senatores consentiunt.",  # Many senators agree
            "moderate": "Factio mea stat unita!",  # My faction stands united
            "strong": "Vox populi, vox Dei!"  # The voice of the people is the voice of God
        }
    }
    
    # Select a random template for the chosen type and intensity
    template_options = templates[interjection_type][intensity]
    chosen_template = random.choice(template_options)
    
    # Fill in template variables
    content = chosen_template.format(
        name=target_senator.get('name', 'Senator'),
        topic=topic
    )
    
    # Get matching Latin content
    latin_content = latin_templates[interjection_type][intensity]
    
    return content, latin_content


def _ensure_option_variety(options: List[Dict]) -> List[Dict]:
    """
    Ensure that the generated options have variety in types and intensity.
    
    Args:
        options: List of interjection options
        
    Returns:
        List of options with improved variety
    """
    # If we have fewer than 2 options, no need to check variety
    if len(options) < 2:
        return options
        
    # Check for duplicate types
    seen_types = []
    for option in options:
        option_type = option.get('type')
        seen_types.append(option_type)
            
    # If all options are the same type, try to replace one
    if len(set(seen_types)) == 1 and len(options) > 1:
        # Get all possible types minus the one we already have
        current_type = seen_types[0]
        all_types = list(InterjectionType)
        available_types = [t for t in all_types if t != current_type]
        
        if available_types:
            # Replace the last option with a different type
            new_type = random.choice(available_types)
            
            # Get the target and speech content from existing option
            target = options[-1].get('target', {})
            speech_content = {'topic': 'the current matter'}  # Fallback
            
            # Create new option of different type
            options[-1] = _create_interjection_option(
                new_type, 
                {},  # Empty player data is okay for content generation
                target,
                speech_content
            )
    
    # Check for all same intensity
    intensities = [option.get('intensity') for option in options]
    if len(set(intensities)) == 1 and len(options) > 1:
        # Change intensity of one option
        current_intensity = intensities[0]
        
        # Get a different intensity
        all_intensities = list(INTENSITY_LEVELS.values())
        available_intensities = [i for i in all_intensities if i != current_intensity]
        
        if available_intensities:
            # Apply new intensity to first option
            options[0]['intensity'] = random.choice(available_intensities)
    
    return options