#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Roman Senate AI Game
Rhetorical Devices Module

This module implements classical rhetorical devices used in Roman oratory.
"""

import random
import re
from typing import Dict, List, Callable, Any, Tuple, Optional

# Dictionary of rhetorical devices with descriptions and implementations
RHETORICAL_DEVICES = {
    # Repetition-based devices
    "anaphora": {
        "description": "Repetition of words at the beginning of successive clauses",
        "example_latin": "Vivamus Romae, vivamus pro patria, vivamus pro futuro.",
        "example_english": "We live for Rome, we live for our homeland, we live for the future."
    },
    "tricolon": {
        "description": "Series of three parallel elements, often increasing in length",
        "example_latin": "Veni, vidi, vici.",
        "example_english": "I came, I saw, I conquered."
    },
    "polysyndeton": {
        "description": "Use of multiple conjunctions",
        "example_latin": "Et senatus et populus et exercitus Romam defendit.",
        "example_english": "Both the Senate and the people and the army defend Rome."
    },
    "asyndeton": {
        "description": "Omission of conjunctions",
        "example_latin": "Senatus decrevit, populus approbavit, hostes fugerunt.",
        "example_english": "The Senate decreed, the people approved, the enemies fled."
    },
    
    # Contrast-based devices
    "antithesis": {
        "description": "Juxtaposition of contrasting ideas in parallel structure",
        "example_latin": "Non ut vivamus edimus, sed ut edamus vivimus.",
        "example_english": "We do not eat to live, but we live to eat."
    },
    "chiasmus": {
        "description": "Reversed grammatical structure in successive phrases",
        "example_latin": "Non ut vivamus edimus, sed ut edamus vivimus.",
        "example_english": "Not to live we eat, but to eat we live."
    },
    
    # Reference-based devices
    "exemplum": {
        "description": "Historical example used to support an argument",
        "example_latin": "Recordamini quod fecit Brutus contra tyrannum.",
        "example_english": "Remember what Brutus did against the tyrant."
    },
    "sententia": {
        "description": "Aphoristic statement embodying a general truth",
        "example_latin": "Historia est magistra vitae.",
        "example_english": "History is the teacher of life."
    },
    
    # Question-based devices
    "rhetorical_question": {
        "description": "Question asked for effect without answer expected",
        "example_latin": "Quo usque tandem abutere, Catilina, patientia nostra?",
        "example_english": "How long, Catiline, will you abuse our patience?"
    },
    "interrogatio": {
        "description": "Series of questions to emphasize a point",
        "example_latin": "Quis hoc fecit? Quis patriam prodidit? Quis nos decepit?",
        "example_english": "Who did this? Who betrayed the homeland? Who deceived us?"
    },
    
    # Argumentation devices
    "ratiocinatio": {
        "description": "Logical reasoning step by step",
        "example_latin": "Si bellum necessarium est et si victoria utilis, tunc pugnare debemus.",
        "example_english": "If war is necessary and if victory is useful, then we must fight."
    },
    "distributio": {
        "description": "Systematic division of argument into parts",
        "example_latin": "Primum de moribus, deinde de legibus, postremo de utilitate dicam.",
        "example_english": "First I will speak about customs, then about laws, and finally about utility."
    },
    
    # Emphasis devices
    "hyperbole": {
        "description": "Exaggeration for effect",
        "example_latin": "Montes auri pollicetur.",
        "example_english": "He promises mountains of gold."
    },
    "exclamatio": {
        "description": "Exclamation for emphasis",
        "example_latin": "O tempora! O mores!",
        "example_english": "Oh the times! Oh the customs!"
    },
    
    # Sophisticated devices
    "praeteritio": {
        "description": "Drawing attention by pretending to pass over",
        "example_latin": "Non dicam Antonium esse ebriosum.",
        "example_english": "I will not mention that Antonius is a drunkard."
    },
    "definitio": {
        "description": "Careful definition of terms",
        "example_latin": "Virtus est constans et perpetua voluntas ius suum cuique tribuendi.",
        "example_english": "Virtue is the constant and perpetual wish to give everyone their due."
    },
    "analogia": {
        "description": "Analogical reasoning",
        "example_latin": "Sicut corpus sine spiritu, ita res publica sine legibus.",
        "example_english": "As a body without spirit, so is a republic without laws."
    },
    
    # Emotional appeals
    "pathos": {
        "description": "Appeal to emotions",
        "example_latin": "Flete, cives, flete pro patria vestra!",
        "example_english": "Weep, citizens, weep for your homeland!"
    }
}

# Implementation functions for rhetorical devices
def apply_anaphora(text: str, repetition: str = None) -> str:
    """Apply anaphora (repetition at beginning of clauses) to text."""
    if not text:
        return text
        
    sentences = re.split(r'[.!?]\s*', text)
    sentences = [s for s in sentences if s]  # Remove empty sentences
    
    if len(sentences) < 3:
        return text  # Need at least 3 sentences for anaphora
    
    # Choose which sentences to modify (at least 2 consecutive ones)
    start_idx = random.randint(0, len(sentences) - 3)
    count = random.randint(2, min(3, len(sentences) - start_idx))
    
    # If no repetition phrase provided, extract one from the first sentence
    if not repetition:
        first_sentence = sentences[start_idx]
        words = first_sentence.split()
        
        # Use first 2-3 words or generate a new phrase
        if len(words) >= 3:
            word_count = random.randint(1, min(3, len(words)))
            repetition = " ".join(words[:word_count])
        else:
            # Fallback repetition phrases
            repetition_options = [
                "Fellow senators,", 
                "I declare that", 
                "Remember that", 
                "Consider how"
            ]
            repetition = random.choice(repetition_options)
    
    # Apply anaphora to selected sentences
    modified_sentences = sentences.copy()
    for i in range(start_idx, start_idx + count):
        # Skip if sentence already starts with the repetition
        if not modified_sentences[i].startswith(repetition):
            # Ensure proper capitalization
            sentence = modified_sentences[i]
            # Remove the first word if it would make the sentence awkward
            if len(sentence.split()) > 3:  # Only if sentence is long enough
                # Remove first word or two to avoid awkward phrasing
                words_to_remove = random.randint(1, 2)
                sentence_words = sentence.split()
                if len(sentence_words) > words_to_remove:
                    sentence = " ".join(sentence_words[words_to_remove:])
            
            # Apply the repetition
            modified_sentences[i] = f"{repetition} {sentence[0].lower()}{sentence[1:]}"
    
    # Reconstruct the text
    return ". ".join(modified_sentences) + "."

def apply_tricolon(text: str, elements: List[str] = None) -> str:
    """Apply tricolon (series of three parallel elements) to text."""
    if not text:
        return text
        
    sentences = re.split(r'[.!?]\s*', text)
    sentences = [s for s in sentences if s]  # Remove empty sentences
    
    if not sentences:
        return text
    
    # Choose a sentence to modify or create a new one
    if len(sentences) > 1:
        target_idx = random.randint(0, len(sentences) - 1)
        insert_position = target_idx
    else:
        target_idx = 0
        insert_position = 0
    
    # If elements not provided, generate them based on the context
    if not elements:
        # Use verbs, nouns, or adjectives that fit the context
        context_words = {
            "values": ["honor", "duty", "virtue", "glory", "courage", "wisdom", "piety"],
            "actions": ["defend", "protect", "serve", "honor", "uphold", "preserve", "build"],
            "entities": ["Rome", "the Republic", "the Senate", "our ancestors", "our laws", 
                        "our traditions", "our citizens", "our future"]
        }
        
        # Choose a pattern for the tricolon
        patterns = [
            # {verb} for {entity}
            lambda: f"{random.choice(context_words['actions'])} for {random.choice(context_words['entities'])}, " + 
                    f"{random.choice(context_words['actions'])} for {random.choice(context_words['entities'])}, " +
                    f"{random.choice(context_words['actions'])} for {random.choice(context_words['entities'])}",
            
            # {entity}, {entity}, and {entity}
            lambda: f"{random.choice(context_words['entities'])}, " +
                    f"{random.choice(context_words['entities'])}, and " +
                    f"{random.choice(context_words['entities'])}",
            
            # with {value}, with {value}, with {value}
            lambda: f"with {random.choice(context_words['values'])}, " +
                    f"with {random.choice(context_words['values'])}, " +
                    f"with {random.choice(context_words['values'])}"
        ]
        
        tricolon = random.choice(patterns)()
    else:
        tricolon = ", ".join(elements[:-1]) + ", and " + elements[-1]
    
    # Create a new sentence with the tricolon or modify existing one
    if random.random() < 0.5 and len(sentences) > 2:
        # Insert as a standalone sentence
        new_sentence = f"We must act for {tricolon}."
        sentences.insert(insert_position, new_sentence)
    else:
        # Modify existing sentence to include the tricolon
        original = sentences[target_idx]
        
        # Place the tricolon in a natural position in the sentence
        if len(original.split()) > 5:
            # For longer sentences, try to insert the tricolon after a comma or appropriate point
            comma_positions = [m.start() for m in re.finditer(r',\s*', original)]
            if comma_positions and random.random() < 0.7:
                pos = random.choice(comma_positions)
                sentences[target_idx] = f"{original[:pos+1]} {tricolon}, {original[pos+2:]}"
            else:
                # Insert near the end
                words = original.split()
                insert_point = max(len(words) - 3, len(words) // 2)
                sentences[target_idx] = " ".join(words[:insert_point]) + f" {tricolon} " + " ".join(words[insert_point:])
        else:
            # For shorter sentences, append the tricolon
            sentences[target_idx] = f"{original} for {tricolon}"
    
    # Reconstruct the text
    return ". ".join(sentences) + "."

def apply_rhetorical_device(text: str, device_name: str) -> Tuple[str, str]:
    """
    Apply a rhetorical device to the text.
    
    Args:
        text: The text to modify
        device_name: Name of the rhetorical device to apply
        
    Returns:
        Tuple of (modified_text, description_of_change)
    """
    device_info = RHETORICAL_DEVICES.get(device_name)
    if not device_info:
        return text, f"No device named '{device_name}' found"
    
    # Each device has a specific implementation
    if device_name == "anaphora":
        modified = apply_anaphora(text)
        return modified, "Applied anaphora (repetition at the beginning of clauses)"
    
    elif device_name == "tricolon":
        modified = apply_tricolon(text)
        return modified, "Applied tricolon (series of three parallel elements)"
    
    # Add implementations for other devices here
    # For now, we'll just add placeholder implementations
    
    elif device_name == "rhetorical_question":
        sentences = re.split(r'[.!?]\s*', text)
        sentences = [s for s in sentences if s]
        if sentences:
            idx = random.randint(0, len(sentences) - 1)
            question_templates = [
                "Is this not what our ancestors would have wanted?",
                "How can we ignore the lessons of history?",
                "Who among us would deny this truth?",
                "What greater cause exists than the defense of our Republic?",
                "Have we forgotten the wisdom of our forefathers?"
            ]
            sentences.insert(idx, random.choice(question_templates))
            return ". ".join(sentences) + ".", "Applied rhetorical question"
    
    # Default: return original text with note that implementation is pending
    return text, f"Device '{device_name}' implementation pending"

# Function to apply multiple rhetorical devices to a text
def apply_multiple_devices(text: str, devices: List[str]) -> Tuple[str, List[str]]:
    """
    Apply multiple rhetorical devices to a text.
    
    Args:
        text: The text to modify
        devices: List of device names to apply
    
    Returns:
        Tuple of (modified_text, list_of_descriptions)
    """
    modified_text = text
    descriptions = []
    
    for device in devices:
        modified_text, desc = apply_rhetorical_device(modified_text, device)
        descriptions.append(desc)
    
    return modified_text, descriptions

# Function to suggest appropriate devices based on text content
def suggest_devices(text: str, count: int = 3) -> List[str]:
    """Suggest appropriate rhetorical devices based on text content."""
    # TODO: Implement more sophisticated suggestion logic
    return random.sample(list(RHETORICAL_DEVICES.keys()), min(count, len(RHETORICAL_DEVICES)))

# Function to analyze text for existing rhetorical devices
def analyze_rhetoric(text: str) -> Dict[str, float]:
    """
    Analyze text for existing rhetorical devices.
    
    Returns:
        Dictionary mapping device names to confidence scores (0.0-1.0)
    """
    # TODO: Implement rhetoric analysis
    return {}