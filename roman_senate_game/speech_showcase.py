#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Roman Senate Speech Generator Showcase

This script demonstrates the capabilities of the Roman Senate speech generation framework
by generating example speeches from different senator archetypes on various topics.
It showcases how speeches incorporate different rhetorical devices, Latin flourishes,
and classical structure, as well as how they vary based on senator personality traits.

Run as: python roman_senate_game/speech_showcase.py
"""

import random
import sys
import os
from pprint import pprint
from typing import Dict, List, Any

# Add parent directory to path to ensure imports work
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import speech generation modules
from roman_senate_game.speech_generation import speech_generator
from roman_senate_game.speech_generation import archetype_system
from roman_senate_game.speech_generation import rhetorical_devices
from roman_senate_game.speech_generation import classical_structure
from roman_senate_game.speech_generation import latin_flourishes
from roman_senate_game.speech_generation import historical_context

# Define text formatting for better readability
class TextFormat:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

# Check if terminal supports color
def supports_color():
    """Return True if the running terminal supports color, False otherwise."""
    supported_platform = sys.platform != 'win32' or 'ANSICON' in os.environ
    is_a_tty = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
    return supported_platform and is_a_tty

# Use colors only if supported
USE_COLOR = supports_color()

def format_text(text, format_code):
    """Apply formatting if supported, otherwise return plain text."""
    if USE_COLOR:
        return f"{format_code}{text}{TextFormat.END}"
    return text

def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 80)
    print(format_text(text, TextFormat.HEADER + TextFormat.BOLD))
    print("=" * 80)

def print_section(text):
    """Print a formatted section header."""
    print("\n" + "-" * 40)
    print(format_text(text, TextFormat.BOLD + TextFormat.YELLOW))
    print("-" * 40)

def print_annotation(text):
    """Print an annotation explaining a showcase feature."""
    print(format_text(f"\n[ANNOTATION] {text}", TextFormat.CYAN))

def print_structure_analysis(speech_data):
    """Print an analysis of the speech structure."""
    if 'speech_structure' in speech_data:
        print_section("Classical Structure Analysis")
        
        for part, content in speech_data['speech_structure'].items():
            if content and len(content) > 0:
                # Get description of this part from classical_structure module
                part_desc = classical_structure.SPEECH_PARTS.get(part, {}).get('description', 'Part of speech')
                print(format_text(f"\n{part.upper()}: {part_desc}", TextFormat.BOLD + TextFormat.GREEN))
                print(content)

def print_rhetorical_devices(speech_data):
    """Print the rhetorical devices used in the speech."""
    if 'selected_devices' in speech_data and 'device_descriptions' in speech_data:
        print_section("Rhetorical Devices Used")
        
        for device, description in zip(speech_data['selected_devices'], speech_data['device_descriptions']):
            device_info = rhetorical_devices.RHETORICAL_DEVICES.get(device, {})
            print(format_text(f"{device}: ", TextFormat.BOLD), end='')
            print(device_info.get('description', description))
            if 'example_latin' in device_info and 'example_english' in device_info:
                print(f"  Example: {device_info['example_latin']} ({device_info['example_english']})")

def print_latin_analysis(speech_data):
    """Print analysis of Latin usage in the speech."""
    print_section("Latin Flourishes")
    
    # Extract Latin phrases from the text
    text = speech_data['text']
    
    # Simple detection of Latin phrases by looking for phrases from latin_flourishes module
    found_phrases = []
    
    for category in latin_flourishes.LATIN_PHRASES:
        for phrase in latin_flourishes.LATIN_PHRASES[category]:
            latin = phrase['latin']
            if latin in text:
                found_phrases.append({
                    'latin': latin,
                    'english': phrase['english'],
                    'usage': phrase['usage'],
                    'category': category
                })
    
    if found_phrases:
        for phrase in found_phrases:
            print(format_text(f"{phrase['latin']}", TextFormat.BOLD), end='')
            print(f" ({phrase['english']}) - {phrase['usage']} [{phrase['category']}]")
    else:
        print("No specific Latin phrases detected in output.")
    
    # Show Latin version if available
    if 'latin_version' in speech_data and speech_data['latin_version']:
        print("\n" + format_text("Partial Latin version:", TextFormat.BOLD))
        print(speech_data['latin_version'])

def create_senator(name, faction, archetype=None, traits=None):
    """Create a senator with specific traits to showcase personality effects."""
    if traits is None:
        traits = {}
    
    # Default traits
    default_traits = {
        "eloquence": 0.5,
        "corruption": 0.2,
        "loyalty": 0.7,
    }
    
    # Update defaults with provided traits
    for trait, value in traits.items():
        default_traits[trait] = value
    
    senator = {
        "id": random.randint(1, 1000),
        "name": name,
        "faction": faction,
        "traits": default_traits
    }
    
    # If archetype is specified, adjust traits to ensure that archetype is selected
    if archetype:
        if archetype == "traditionalist":
            senator["traits"]["loyalty"] = 0.9
            senator["traits"]["corruption"] = 0.1
            senator["faction"] = "Optimates"
        elif archetype == "populist":
            senator["traits"]["loyalty"] = 0.3
            senator["traits"]["corruption"] = 0.6
            senator["faction"] = "Populares"
        elif archetype == "philosopher":
            senator["traits"]["eloquence"] = 0.9
            senator["traits"]["corruption"] = 0.1
        elif archetype == "pragmatist":
            senator["traits"]["loyalty"] = 0.4
            senator["traits"]["corruption"] = 0.3
        elif archetype == "militarist":
            senator["traits"]["loyalty"] = 0.8
            senator["traits"]["corruption"] = 0.4
            senator["faction"] = "Military"
    
    return senator

def showcase_speech(senator, topic, year=-80, annotation=None):
    """Generate and display a showcase speech with analysis."""
    # Print header with senator and topic information
    print_header(f"Speech by {senator['name']} ({senator['faction']}) on {topic}")
    
    # Add annotation if provided
    if annotation:
        print_annotation(annotation)
    
    # Generate the speech
    speech_data = speech_generator.generate_speech(
        senator=senator,
        topic=topic,
        year=year
    )
    
    # Print senator archetype information
    archetype_info = speech_data.get('archetype', {})
    primary = archetype_info.get('primary', 'unknown')
    secondary = archetype_info.get('secondary', 'unknown')
    
    print_section("Senator Archetype")
    print(f"Primary: {format_text(primary, TextFormat.BOLD)} ({archetype_info.get('primary_score', 0):.2f})")
    print(f"Secondary: {format_text(secondary, TextFormat.BOLD)} ({archetype_info.get('secondary_score', 0):.2f})")
    print(f"Faction: {senator['faction']}")
    
    print_section("Personality Traits")
    for trait, value in senator['traits'].items():
        print(f"{trait}: {value:.2f}")
    
    # Print the speech
    print_section("Complete Speech")
    print(speech_data['text'])
    
    # Print structural analysis
    print_structure_analysis(speech_data)
    
    # Print rhetorical devices
    print_rhetorical_devices(speech_data)
    
    # Print Latin analysis
    print_latin_analysis(speech_data)
    
    # Print stance on topic
    print_section("Political Position")
    print(f"Stance on {topic}: {format_text(speech_data.get('stance', 'neutral'), TextFormat.BOLD)}")
    
    # Return the speech data for potential further analysis
    return speech_data

def main():
    """Run the speech showcase demonstrations."""
    print_header("ROMAN SENATE SPEECH GENERATION FRAMEWORK SHOWCASE")
    print("This script demonstrates the capabilities of the speech generation framework.")
    print("It generates example speeches from different senator archetypes on various topics,")
    print("showcasing rhetorical devices, Latin flourishes, classical structure, and personality effects.")
    
    # SHOWCASE 1: Optimates Senator on Military Topic (Traditionalist)
    optimates_senator = create_senator(
        name="Marcus Calpurnius Bibulus",
        faction="Optimates",
        archetype="traditionalist",
        traits={"eloquence": 0.7, "corruption": 0.1, "loyalty": 0.9}
    )
    
    showcase_speech(
        optimates_senator,
        topic="Funding for the legions in Gaul",
        annotation="This speech demonstrates the TRADITIONALIST archetype, characterized by formal language, "
                  "appeals to tradition and ancestral customs (mos maiorum), and extensive use of historical "
                  "precedent. Note the formal structure and heavier Latin usage typical of Optimates senators."
    )
    
    # SHOWCASE 2: Populares Senator on Public Works (Populist)
    populares_senator = create_senator(
        name="Gaius Scribonius Curio",
        faction="Populares",
        archetype="populist",
        traits={"eloquence": 0.6, "corruption": 0.5, "loyalty": 0.3}
    )
    
    showcase_speech(
        populares_senator,
        topic="Grain distribution to the urban poor",
        annotation="This speech demonstrates the POPULIST archetype, characterized by emotional appeals, "
                  "references to the common people's struggles, and simpler language. Populares senators "
                  "typically use more direct rhetorical questions and exclamations while employing fewer "
                  "Latin flourishes to ensure their message reaches the common people."
    )
    
    # SHOWCASE 3: Military Senator on Defense (Militarist)
    military_senator = create_senator(
        name="Titus Labienus",
        faction="Military",
        archetype="militarist",
        traits={"eloquence": 0.5, "corruption": 0.3, "loyalty": 0.8}
    )
    
    showcase_speech(
        military_senator,
        topic="Border defenses against Germanic tribes",
        annotation="This speech demonstrates the MILITARIST archetype, characterized by direct, assertive language, "
                  "threat assessments, and security-focused arguments. Note the shorter sentences, command-oriented "
                  "phrasing, and focus on action rather than philosophical considerations."
    )
    
    # SHOWCASE 4: Intellectual Senator on Taxation (Philosopher)
    philosopher_senator = create_senator(
        name="Publius Nigidius Figulus",
        faction="Independent",
        archetype="philosopher",
        traits={"eloquence": 0.9, "corruption": 0.1, "loyalty": 0.6}
    )
    
    showcase_speech(
        philosopher_senator,
        topic="Tax reform for the equestrian class",
        annotation="This speech demonstrates the PHILOSOPHER archetype, characterized by abstract reasoning, "
                  "complex sentence structures, and principled arguments. Note the sophisticated rhetorical devices, "
                  "Greek-influenced philosophical references, and logical structure of arguments."
    )
    
    # SHOWCASE 5: Pragmatic Senator on Agricultural Policy (Pragmatist)
    pragmatist_senator = create_senator(
        name="Lucius Munatius Plancus",
        faction="Merchant",
        archetype="pragmatist",
        traits={"eloquence": 0.6, "corruption": 0.3, "loyalty": 0.4}
    )
    
    showcase_speech(
        pragmatist_senator,
        topic="Land distribution to veteran soldiers",
        annotation="This speech demonstrates the PRAGMATIST archetype, characterized by practical considerations, "
                  "cost-benefit analysis, and results-oriented thinking. Note the focus on implementation details, "
                  "resource management, and practical outcomes rather than emotional or traditional appeals."
    )
    
    # SHOWCASE 6: Eloquence Comparison (Same archetype, different eloquence)
    print_header("SHOWCASE: IMPACT OF ELOQUENCE ON SPEECH GENERATION")
    print_annotation("The following two speeches are from senators with the same archetype and faction, "
                    "but with different eloquence traits. This demonstrates how personality traits affect "
                    "speech quality, complexity, and rhetorical device usage within the same archetype.")
    
    # Low eloquence traditionalist
    low_eloquence = create_senator(
        name="Appius Claudius Pulcher",
        faction="Optimates",
        archetype="traditionalist",
        traits={"eloquence": 0.2, "corruption": 0.2, "loyalty": 0.8}
    )
    
    showcase_speech(
        low_eloquence,
        topic="Religious observances for public festivals",
        annotation="LOW ELOQUENCE (0.2): Notice the simpler sentence structures, fewer rhetorical devices, "
                  "and less sophisticated arguments. The speech maintains traditionalist values but expresses "
                  "them with less oratorical flair."
    )
    
    # High eloquence traditionalist
    high_eloquence = create_senator(
        name="Quintus Hortensius Hortalus",
        faction="Optimates", 
        archetype="traditionalist",
        traits={"eloquence": 0.9, "corruption": 0.2, "loyalty": 0.8}
    )
    
    showcase_speech(
        high_eloquence,
        topic="Religious observances for public festivals",
        annotation="HIGH ELOQUENCE (0.9): Compare with the previous speech on the same topic. "
                  "Note the more sophisticated sentence structures, greater variety of rhetorical devices, "
                  "and more nuanced arguments while maintaining the same traditionalist values."
    )
    
    # Final summary
    print_header("SHOWCASE SUMMARY")
    print("This showcase has demonstrated:")
    print("1. Different senator archetypes (Traditionalist, Populist, Militarist, Philosopher, Pragmatist)")
    print("2. Speeches on various topics (military, public works, defense, taxation, agriculture)")
    print("3. How speeches incorporate rhetorical devices, Latin flourishes, and classical structure")
    print("4. How speeches vary based on senator personality traits, particularly eloquence")
    print()
    print("The Roman Senate speech generation framework successfully produces historically authentic")
    print("and characterful speeches that reflect the political divisions, rhetorical styles, and")
    print("cultural context of the late Roman Republic.")

if __name__ == "__main__":
    main()