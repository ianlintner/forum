#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Roman Senate AI Game
Latin Flourishes Module

This module handles the integration of Latin phrases, terminology, and
flourishes into speeches to enhance historical authenticity.
"""

import random
import re
from typing import Dict, List, Optional, Any, Tuple

# Common Latin phrases by category for use in speeches
LATIN_PHRASES = {
    "opening_phrases": [
        {"latin": "Patres conscripti", "english": "Conscript fathers", "usage": "formal address to Senate"},
        {"latin": "Quirites", "english": "Citizens", "usage": "formal address to Roman people"},
        {"latin": "Senatus populusque Romanus", "english": "The Senate and People of Rome", "usage": "formal reference to state"},
        {"latin": "Pro bono publico", "english": "For the public good", "usage": "stating purpose of proposal"}
    ],
    
    "transitional_phrases": [
        {"latin": "Ad rem", "english": "To the point", "usage": "transition to main argument"},
        {"latin": "Ex illo tempore", "english": "From that time", "usage": "historical transition"},
        {"latin": "Primo... deinde... postremo", "english": "First... then... finally", "usage": "structuring arguments"},
        {"latin": "Quid plura?", "english": "What more?", "usage": "rhetorical transition"}
    ],
    
    "rhetorical_phrases": [
        {"latin": "Quo usque tandem?", "english": "How long still?", "usage": "expressing exasperation"},
        {"latin": "O tempora! O mores!", "english": "Oh the times! Oh the customs!", "usage": "expressing outrage"},
        {"latin": "Cui bono?", "english": "To whose benefit?", "usage": "questioning motives"},
        {"latin": "Quid pro quo", "english": "Something for something", "usage": "proposing exchange"}
    ],
    
    "logical_phrases": [
        {"latin": "Quod erat demonstrandum", "english": "Which was to be demonstrated", "usage": "concluding argument"},
        {"latin": "A fortiori", "english": "From the stronger", "usage": "stronger logical case"},
        {"latin": "Prima facie", "english": "At first sight", "usage": "initial impression"},
        {"latin": "Reductio ad absurdum", "english": "Reduction to absurdity", "usage": "showing absurd conclusion"}
    ],
    
    "value_phrases": [
        {"latin": "Virtus", "english": "Valor, excellence", "usage": "appealing to virtue"},
        {"latin": "Dignitas", "english": "Dignity, prestige", "usage": "appealing to honor"},
        {"latin": "Pietas", "english": "Duty, loyalty", "usage": "appealing to duty"},
        {"latin": "Gravitas", "english": "Seriousness", "usage": "appealing to solemnity"}
    ],
    
    "legal_phrases": [
        {"latin": "De jure", "english": "By law", "usage": "legal argument"},
        {"latin": "De facto", "english": "In fact", "usage": "practical reality"},
        {"latin": "Ultra vires", "english": "Beyond the powers", "usage": "exceeding authority"},
        {"latin": "Lex non scripta", "english": "Unwritten law", "usage": "customary law"}
    ],
    
    "conclusive_phrases": [
        {"latin": "Sic semper tyrannis", "english": "Thus always to tyrants", "usage": "opposing tyranny"},
        {"latin": "Vox populi, vox Dei", "english": "Voice of the people, voice of God", "usage": "populist appeal"},
        {"latin": "Carthago delenda est", "english": "Carthage must be destroyed", "usage": "forceful conclusion"},
        {"latin": "Res ipsa loquitur", "english": "The thing speaks for itself", "usage": "self-evident conclusion"}
    ]
}

# Latin terms related to Roman politics
POLITICAL_TERMS = {
    "institutions": [
        {"latin": "Senatus", "english": "Senate", "usage": "Roman Senate"},
        {"latin": "Comitia centuriata", "english": "Centuriate Assembly", "usage": "voting assembly"},
        {"latin": "Comitia tributa", "english": "Tribal Assembly", "usage": "plebeian assembly"},
        {"latin": "Curia", "english": "Senate House", "usage": "meeting place"}
    ],
    
    "officials": [
        {"latin": "Consul", "english": "Consul", "usage": "chief magistrate"},
        {"latin": "Praetor", "english": "Praetor", "usage": "judicial magistrate"},
        {"latin": "Tribunus plebis", "english": "Tribune of the Plebs", "usage": "plebeian representative"},
        {"latin": "Censor", "english": "Censor", "usage": "moral regulator/census taker"}
    ],
    
    "legal_concepts": [
        {"latin": "Mos maiorum", "english": "Way of the ancestors", "usage": "traditional customs"},
        {"latin": "Imperium", "english": "Command power", "usage": "official authority"},
        {"latin": "Auctoritas", "english": "Authority", "usage": "moral influence"},
        {"latin": "Provocatio", "english": "Appeal", "usage": "right to appeal"}
    ],
    
    "political_factions": [
        {"latin": "Optimates", "english": "Best men", "usage": "conservative faction"},
        {"latin": "Populares", "english": "Popular ones", "usage": "reform faction"},
        {"latin": "Equites", "english": "Knights", "usage": "wealthy business class"},
        {"latin": "Nobiles", "english": "Nobles", "usage": "aristocratic elites"}
    ]
}

# Roman virtues relevant to political discourse
ROMAN_VIRTUES = [
    {"latin": "Virtus", "english": "Valor", "explanation": "Courage and excellence in military matters"},
    {"latin": "Clementia", "english": "Mercy", "explanation": "Mildness and gentleness toward others"},
    {"latin": "Iustitia", "english": "Justice", "explanation": "Fair dealing according to law and custom"},
    {"latin": "Pietas", "english": "Piety", "explanation": "Dutiful respect to gods, homeland, and family"},
    {"latin": "Gravitas", "english": "Dignity", "explanation": "Serious conduct and self-control"},
    {"latin": "Dignitas", "english": "Dignity", "explanation": "Personal standing and honor"},
    {"latin": "Severitas", "english": "Severity", "explanation": "Strictness, especially in discipline"},
    {"latin": "Constantia", "english": "Perseverance", "explanation": "Steadfastness and persistence"},
    {"latin": "Frugalitas", "english": "Frugality", "explanation": "Economy and simplicity of lifestyle"},
    {"latin": "Fides", "english": "Faithfulness", "explanation": "Reliability and trustworthiness"}
]

def add_latin_flourish(text: str, flourish_level: float = 0.5, 
                      archetype: str = None, format_style: str = "parentheses") -> str:
    """
    Add Latin phrases and terms to an English text to create appropriate flourishes.
    
    Args:
        text: The English text to enhance
        flourish_level: How much Latin to include (0.0-1.0)
        archetype: Optional senator archetype to tailor Latin usage
        format_style: How to format Latin phrases ("parentheses", "italic", "follow")
        
    Returns:
        Text with added Latin flourishes
    """
    if not text:
        return text
        
    # Skip if flourish level is too low
    if flourish_level < 0.1:
        return text
    
    # Adjust flourish level based on archetype
    if archetype:
        modifiers = {
            "traditionalist": 1.3,  # Uses more Latin
            "philosopher": 1.2,
            "pragmatist": 0.8,
            "militarist": 0.9,
            "populist": 0.6  # Uses less Latin
        }
        flourish_level *= modifiers.get(archetype, 1.0)
    
    # Determine number of phrases to add based on text length and flourish level
    sentences = re.split(r'[.!?]\s*', text)
    sentences = [s for s in sentences if s]  # Remove empty sentences
    
    # Number of phrases to add based on text length and flourish level
    num_phrases = max(1, int(flourish_level * len(sentences) * 0.4))
    
    # Avoid overdoing it
    num_phrases = min(num_phrases, 5)  
    
    # Select positions for insertion (prefer beginning, transitions, and end)
    potential_positions = []
    
    # Beginning
    if len(sentences) > 0:
        potential_positions.append(0)
    
    # Transitions (after commas or key transitional words)
    for i, sentence in enumerate(sentences):
        if i > 0 and i < len(sentences) - 1:
            if ',' in sentence or any(word in sentence.lower() for word in 
                                     ['however', 'therefore', 'thus', 'moreover']):
                potential_positions.append(i)
    
    # End
    if len(sentences) > 1:
        potential_positions.append(len(sentences) - 1)
    
    # Ensure we have enough positions (fall back to random if needed)
    while len(potential_positions) < num_phrases and len(sentences) > 1:
        pos = random.randint(0, len(sentences) - 1)
        if pos not in potential_positions:
            potential_positions.append(pos)
    
    # Sort positions to process in order
    potential_positions.sort()
    
    # Select random positions from potential positions
    if len(potential_positions) > num_phrases:
        selected_positions = random.sample(potential_positions, num_phrases)
        selected_positions.sort()
    else:
        selected_positions = potential_positions
    
    # Determine phrase categories to use
    categories = []
    
    # For beginning of text, use opening phrases
    if len(selected_positions) > 0 and 0 in selected_positions:
        categories.append("opening_phrases")
        selected_positions.remove(0)
    
    # For middle and end positions
    for _ in range(len(selected_positions)):
        available_categories = ["transitional_phrases", "rhetorical_phrases", 
                               "logical_phrases", "value_phrases", "legal_phrases"]
        categories.append(random.choice(available_categories))
    
    # Select phrases for each position
    selected_phrases = []
    for category in categories:
        phrases = LATIN_PHRASES.get(category, LATIN_PHRASES["transitional_phrases"])
        selected_phrases.append(random.choice(phrases))
    
    # Also include some virtues
    if random.random() < flourish_level and len(sentences) > 3:
        selected_phrases.append(random.choice(ROMAN_VIRTUES))
    
    # Insert phrases into text at selected positions
    modified_sentences = sentences.copy()
    
    # Insert phrases at selected positions
    i = 0
    for position in potential_positions[:num_phrases]:
        if i < len(selected_phrases):
            phrase = selected_phrases[i]
            
            # Format based on style preference
            if format_style == "parentheses":
                latin_insertion = f"{phrase['latin']} ({phrase['english']})"
            elif format_style == "italic":
                latin_insertion = f"*{phrase['latin']}*"
            else:  # "follow"
                latin_insertion = f"{phrase['latin']}, which means {phrase['english']},"
            
            # Insert at beginning of sentence if this is the selected position
            if position == 0:
                modified_sentences[position] = f"{latin_insertion}! {modified_sentences[position]}"
            else:
                # Check if sentence has a comma for natural insertion point
                sentence = modified_sentences[position]
                
                if ',' in sentence:
                    # Insert after the first comma
                    comma_pos = sentence.find(',')
                    modified_sentences[position] = f"{sentence[:comma_pos+1]} {latin_insertion}, {sentence[comma_pos+1:].lstrip()}"
                else:
                    # Insert at beginning with appropriate connection
                    modified_sentences[position] = f"{latin_insertion}. {sentence}"
            
            i += 1
    
    # Reconstruct the text
    modified_text = ". ".join(modified_sentences)
    if not modified_text.endswith('.'):
        modified_text += '.'
    
    return modified_text

def add_latin_opening(speech_text: str, year: int = -100) -> str:
    """
    Add a formal Latin opening to a speech based on historical period.
    
    Args:
        speech_text: The speech text
        year: The year in Roman history
        
    Returns:
        Speech with formal Latin opening
    """
    # Select an appropriate opening based on time period
    early_republic = (-509, -300)
    middle_republic = (-299, -150)
    late_republic = (-149, -27)
    
    if early_republic[0] <= year <= early_republic[1]:
        openings = [
            "Patres conscripti!",
            "Quirites!",
            "Patres et cives!"
        ]
    elif middle_republic[0] <= year <= middle_republic[1]:
        openings = [
            "Patres conscripti!",
            "Senatus populusque Romanus!",
            "Patres et equites!"
        ]
    else:  # Late republic
        openings = [
            "Patres conscripti!",
            "Senatus amplissimus!",
            "Optimi et nobilissimi viri!"
        ]
    
    opening = random.choice(openings)
    
    # Add translation
    translations = {
        "Patres conscripti!": "Conscript Fathers!",
        "Quirites!": "Citizens!",
        "Patres et cives!": "Senators and citizens!",
        "Senatus populusque Romanus!": "Senate and People of Rome!",
        "Patres et equites!": "Senators and knights!",
        "Senatus amplissimus!": "Most distinguished Senate!",
        "Optimi et nobilissimi viri!": "Best and most noble men!"
    }
    
    translation = translations.get(opening, "")
    
    # Add the opening to the speech
    if speech_text.startswith(opening) or speech_text.startswith(translation):
        # Already has an appropriate opening
        return speech_text
    else:
        # Add opening and translation
        return f"{opening} ({translation}) {speech_text}"

def generate_latin_speech_version(speech_text: str, senator_archetype: str, 
                                 flourish_level: float = 0.7) -> str:
    """
    Generate a version of the speech with Latin terms replacing key English phrases.
    
    Args:
        speech_text: The English speech text
        senator_archetype: The senator's archetype
        flourish_level: Level of Latin integration (0.0-1.0)
        
    Returns:
        A partially Latinized version of the speech
    """
    # This is a simplified implementation - just add Latin flourishes to the English text
    latinized_text = add_latin_flourish(
        speech_text, 
        flourish_level=flourish_level,
        archetype=senator_archetype, 
        format_style="follow"
    )
    
    return latinized_text

def score_latin_usage(speech_text: str) -> Dict[str, float]:
    """
    Score the Latin usage in a speech for evaluation purposes.
    
    Args:
        speech_text: The speech text
        
    Returns:
        Dictionary with scores for various aspects of Latin usage
    """
    # Count Latin phrases
    latin_count = 0
    for category in LATIN_PHRASES:
        for phrase in LATIN_PHRASES[category]:
            latin = phrase["latin"]
            if latin in speech_text:
                latin_count += 1
    
    # Count political terms
    term_count = 0
    for category in POLITICAL_TERMS:
        for term in POLITICAL_TERMS[category]:
            latin = term["latin"]
            if latin in speech_text:
                term_count += 1
    
    # Count virtues
    virtue_count = 0
    for virtue in ROMAN_VIRTUES:
        latin = virtue["latin"]
        if latin in speech_text:
            virtue_count += 1
    
    # Calculate overall score (scale 0-1)
    total_count = latin_count + term_count + virtue_count
    max_expected = 8  # Reasonable maximum for a good speech
    
    return {
        "latin_phrases": latin_count,
        "political_terms": term_count,
        "virtues": virtue_count,
        "total_count": total_count,
        "authenticity_score": min(1.0, total_count / max_expected)
    }