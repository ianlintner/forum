#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Roman Senate AI Game
Interjections Module

This module implements interjections and interruptions that occurred during
Roman Senate debates, including acclamations, objections, heckling, and
procedural interruptions. It adds realism and dynamism to Senate proceedings
based on historical practices circa 100 BCE.
"""

import random
import time
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum

from rich.panel import Panel
from rich.text import Text
from rich.console import Console
from rich.style import Style

import utils
from logging_utils import get_logger

# Initialize console and logger
console = utils.console
logger = get_logger()

class InterjectionType(Enum):
    """Enumeration of possible interjection types in Roman Senate debates."""
    ACCLAMATION = "acclamation"      # Vocal approval/support
    OBJECTION = "objection"          # Disagreement, challenge, or heckling
    PROCEDURAL = "procedural"        # Point of order, procedural challenge
    EMOTIONAL = "emotional"          # Emotional outburst based on relationships
    COLLECTIVE = "collective"        # Group reaction from multiple senators

class InterjectionTiming(Enum):
    """When during a speech an interjection might occur."""
    BEGINNING = "beginning"          # At the introduction of a speech
    MIDDLE = "middle"                # During the main arguments
    END = "end"                      # After a key point or conclusion
    ANY = "any"                      # Can occur at any point


class Interjection:
    """
    Represents a spontaneous reaction or interruption during Senate debate.
    
    Interjections reflect the lively nature of Roman Senate discussions, where
    senators would frequently interrupt, acclaim, or object during speeches.
    Different types of interjections have different impacts on the debate
    and the relationships between senators.
    """
    
    def __init__(
        self,
        interjection_type: InterjectionType,
        content: str,
        latin_content: str,
        source_senator: Dict,
        target_senator: Optional[Dict] = None,
        timing: InterjectionTiming = InterjectionTiming.ANY,
        intensity: float = 0.5,
        causes_disruption: bool = False
    ):
        """
        Initialize an interjection with its properties.
        
        Args:
            interjection_type: The category of interjection
            content: English text of the interjection
            latin_content: Latin text of the interjection (for historical authenticity)
            source_senator: Senator making the interjection
            target_senator: Senator being addressed (if applicable)
            timing: When during the speech this occurs
            intensity: How forceful the interjection is (0.0-1.0)
            causes_disruption: Whether this interrupts the normal flow of debate
        """
        self.type = interjection_type
        self.content = content
        self.latin_content = latin_content
        self.source_senator = source_senator
        self.target_senator = target_senator
        self.timing = timing
        self.intensity = max(0.0, min(1.0, intensity))  # Constrain to 0.0-1.0
        self.causes_disruption = causes_disruption
        self.timestamp = time.time()
        
        # Determine display characteristics based on type
        if self.type == InterjectionType.ACCLAMATION:
            self.border_style = "green"
            self.prefix = "ACCLAIM"
        elif self.type == InterjectionType.OBJECTION:
            self.border_style = "red"
            self.prefix = "OBJECT"
        elif self.type == InterjectionType.PROCEDURAL:
            self.border_style = "yellow"
            self.prefix = "POINT OF ORDER"
        elif self.type == InterjectionType.EMOTIONAL:
            self.border_style = "magenta"
            self.prefix = "OUTBURST"
        elif self.type == InterjectionType.COLLECTIVE:
            self.border_style = "cyan"
            self.prefix = "SENATE FLOOR"
        else:
            self.border_style = "blue"
            self.prefix = "INTERJECT"

def generate_interjection(
    senator: Dict,
    speech: Dict,
    context: Dict,
    previous_interjections: List[Interjection] = None
) -> Optional[Interjection]:
    """
    Generate an appropriate interjection based on a senator's reaction to a speech.
    
    Considers the senator's personality, faction, relationship with the speaker,
    and the content of the speech to determine if and how they might interject.
    
    Args:
        senator: The senator who might interject
        speech: The current speech being given
        context: Additional context (topic, historical context, etc.)
        previous_interjections: Any interjections already made in this debate
        
    Returns:
        An Interjection object if generated, None otherwise
    """
    # Skip if this is the speaking senator
    if senator.get("id") == speech.get("senator_id"):
        return None
    
    # Probability of interjection based on senator traits
    base_probability = 0.15  # Base chance for any interjection
    
    # Adjust probability based on senator's personality traits
    if "traits" in senator and senator["traits"] is not None:
        traits = senator["traits"]
        # Impulsive or less restrained senators interject more
        if "eloquence" in traits and traits["eloquence"] is not None:
            # More eloquent senators are more likely to speak up
            base_probability += traits["eloquence"] * 0.1
        if "corruption" in traits and traits["corruption"] is not None:
            # More corrupt senators are more likely to interrupt
            base_probability += traits["corruption"] * 0.05
        if "loyalty" in traits and traits["loyalty"] is not None and speech.get("faction") == senator.get("faction"):
            # More loyal senators are more likely to support same-faction speakers
            base_probability += traits["loyalty"] * 0.1
    
    # Adjust probability based on relationships
    from debate import senator_relationships
    source_id = senator.get("id", 0)
    target_id = speech.get("senator_id", 0)
    relationship = senator_relationships[source_id][target_id]
    
    # Strong feelings (positive or negative) increase chance of interjection
    relationship_factor = abs(relationship) * 0.2
    base_probability += relationship_factor
    
    # Limit maximum probability
    interjection_chance = min(0.6, base_probability)
    
    # Check if interjection occurs
    if random.random() > interjection_chance:
        return None
    
    # Determine type of interjection
    if speech.get("faction") == senator.get("faction") and relationship >= 0:
        # More likely to acclaim those from same faction with positive relationship
        type_weights = {
            InterjectionType.ACCLAMATION: 0.7,
            InterjectionType.OBJECTION: 0.1,
            InterjectionType.PROCEDURAL: 0.1,
            InterjectionType.EMOTIONAL: 0.1
        }
    elif relationship < -0.3:
        # More likely to object to those they dislike
        type_weights = {
            InterjectionType.ACCLAMATION: 0.05,
            InterjectionType.OBJECTION: 0.7,
            InterjectionType.PROCEDURAL: 0.15,
            InterjectionType.EMOTIONAL: 0.1
        }
    else:
        # Neutral default
        type_weights = {
            InterjectionType.ACCLAMATION: 0.25,
            InterjectionType.OBJECTION: 0.25,
            InterjectionType.PROCEDURAL: 0.3,
            InterjectionType.EMOTIONAL: 0.2
        }
    
    # Select interjection type based on weights
    interjection_types = list(type_weights.keys())
    interjection_probabilities = list(type_weights.values())
    interjection_type = random.choices(interjection_types, interjection_probabilities, k=1)[0]
    
    # Determine timing
    timing_options = [
        InterjectionTiming.BEGINNING,
        InterjectionTiming.MIDDLE,
        InterjectionTiming.END
    ]
    timing = random.choice(timing_options)
    
    # Generate content based on type
    content, latin_content = _generate_interjection_content(
        interjection_type,
        senator,
        speech,
        context,
        relationship
    )
    
    # Determine intensity - stronger relationships (positive or negative) create stronger interjections
    intensity = min(1.0, 0.3 + abs(relationship) * 0.7)
    
    # Determine if this causes a disruption
    # Procedural points and high-intensity objections are more disruptive
    causes_disruption = (
        interjection_type == InterjectionType.PROCEDURAL or
        (interjection_type == InterjectionType.OBJECTION and intensity > 0.7) or
        (interjection_type == InterjectionType.EMOTIONAL and intensity > 0.8)
    )
    
    # Create the interjection
    interjection = Interjection(
        interjection_type=interjection_type,
        content=content,
        latin_content=latin_content,
        source_senator=senator,
        target_senator={"name": speech.get("senator_name"), "id": speech.get("senator_id")},
        timing=timing,
        intensity=intensity,
        causes_disruption=causes_disruption
    )
    
    # If this causes disruption, potentially update relationship
    if causes_disruption and source_id != 0 and target_id != 0:
        from debate import update_relationship
        # Disruptions generally worsen relationships
        update_relationship(source_id, target_id, -0.05)
        
        # Add emotion to target
        from debate import add_emotion
        if interjection_type == InterjectionType.OBJECTION:
            add_emotion(
                target_id,
                "insulted" if intensity > 0.7 else "annoyed",
                min(1.0, intensity + 0.2),
                senator.get("name", "Unknown Senator"),
                1  # Duration of 1 debate round
            )
    
    return interjection

def process_crowd_reaction(
    speech: Dict,
    senators: List[Dict],
    context: Dict = None
) -> Optional[Interjection]:
    """
    Generates collective reactions from the Senate body to a speech.
    
    Crowd reactions represent multiple senators reacting at once, such as
    murmuring, applause, or collective outrage.
    
    Args:
        speech: The speech being reacted to
        senators: List of senators present
        context: Additional context about the debate
        
    Returns:
        An Interjection object representing the collective reaction, or None
    """
    # Base probability of crowd reaction
    reaction_chance = 0.2
    
    # Adjust based on speech qualities
    if speech.get("quality_factor", 0) > 0.8:
        # High quality speeches get more reactions
        reaction_chance += 0.2
    
    # Check if a reaction occurs
    if random.random() > reaction_chance:
        return None
    
    # Determine general sentiment of senators toward this speech
    stance = speech.get("stance", "neutral")
    faction = speech.get("faction", "Unknown")
    
    # Count senators by faction to gauge potential reaction
    faction_counts = {}
    for senator in senators:
        sen_faction = senator.get("faction", "Unknown")
        faction_counts[sen_faction] = faction_counts.get(sen_faction, 0) + 1
    
    # Determine if speech would generally be supported or opposed
    supporting_factions = []
    opposing_factions = []
    
    for sen_faction, count in faction_counts.items():
        # Same faction is likely supportive
        if sen_faction == faction:
            supporting_factions.append(sen_faction)
        # Factions with opposite stance are opposing
        elif (stance == "support" and sen_faction in ["Optimates", "Religious"]) or \
             (stance == "oppose" and sen_faction in ["Populares", "Merchant"]):
            opposing_factions.append(sen_faction)
        elif random.random() < 0.5:  # Random assignment for other factions
            supporting_factions.append(sen_faction)
        else:
            opposing_factions.append(sen_faction)
    
    # Determine type of crowd reaction based on support/opposition
    if len(supporting_factions) > len(opposing_factions):
        reaction_type = InterjectionType.ACCLAMATION
        intensity = min(1.0, 0.5 + (len(supporting_factions) / len(faction_counts)) * 0.5)
    elif len(opposing_factions) > len(supporting_factions):
        reaction_type = InterjectionType.OBJECTION
        intensity = min(1.0, 0.5 + (len(opposing_factions) / len(faction_counts)) * 0.5)
    else:
        # Mixed reaction
        reaction_type = random.choice([InterjectionType.ACCLAMATION, InterjectionType.OBJECTION])
        intensity = 0.5
    
    # Generate content based on reaction type
    content, latin_content = _generate_crowd_reaction_content(
        reaction_type,
        supporting_factions if reaction_type == InterjectionType.ACCLAMATION else opposing_factions,
        speech,
        intensity
    )
    
    # Determine if this causes disruption
    causes_disruption = intensity > 0.7
    
    # Create the interjection
    return Interjection(
        interjection_type=InterjectionType.COLLECTIVE,
        content=content,
        latin_content=latin_content,
        source_senator={"name": "Senate Floor", "id": 0},  # Collective source
        target_senator={"name": speech.get("senator_name"), "id": speech.get("senator_id")},
        timing=InterjectionTiming.ANY,  # Crowd reactions can occur at any time
        intensity=intensity,
        causes_disruption=causes_disruption
    )

def handle_procedural_objection(
    senator: Dict,
    speech: Dict,
    officials: Any
) -> Tuple[Interjection, Dict]:
    """
    Creates and resolves a procedural objection or point of order.
    
    Procedural objections are formal challenges to the way debate is being conducted.
    These require rulings from the presiding official.
    
    Args:
        senator: Senator raising the objection
        speech: Current speech being challenged
        officials: Presiding officials object to make rulings
        
    Returns:
        Tuple of (interjection, ruling) where ruling is the official's response
    """
    # Generate a procedural objection
    procedural_reasons = [
        "speaking time limit violation",
        "irrelevance to the topic",
        "improper reference to absent senators",
        "violation of speaking order",
        "excessive personal attacks",
        "reference to prohibited religious matters",
        "improper invocation of foreign powers"
    ]
    
    reason = random.choice(procedural_reasons)
    
    # Generate content
    content = f"Point of order! The honorable senator has violated decorum through {reason}."
    latin_content = f"Moneo ordinem! Senator violavit decorum per {_translate_to_latin(reason)}."
    
    # Create the interjection
    interjection = Interjection(
        interjection_type=InterjectionType.PROCEDURAL,
        content=content,
        latin_content=latin_content,
        source_senator=senator,
        target_senator={"name": speech.get("senator_name"), "id": speech.get("senator_id")},
        timing=InterjectionTiming.ANY,
        intensity=0.7,
        causes_disruption=True
    )
    
    # Get ruling from officials
    if hasattr(officials, 'current_presiding_official') and officials.current_presiding_official:
        presiding_official = officials.current_presiding_official
    else:
        # Default fallback if no presiding official
        presiding_official = {"name": "Consul", "title": "Acting Consul"}
    
    # Generate official ruling (if officials module available)
    if officials and hasattr(officials, 'make_ruling'):
        ruling_type, ruling_text = officials.make_ruling(
            official=presiding_official,
            context=f"procedural objection regarding {reason}",
            topic=speech.get("topic", "")
        )
    else:
        # Fallback if officials module not fully available
        ruling_type = "procedure_clarification"
        ruling_text = (
            f"The {presiding_official.get('title', 'Consul')} rules on the objection. "
            f"The point is {'well-taken' if random.random() < 0.5 else 'overruled'}. "
            f"The debate shall {'proceed with adjustments' if random.random() < 0.5 else 'continue as before'}."
        )
    
    # Create ruling response
    ruling = {
        "official": presiding_official,
        "ruling_type": ruling_type,
        "ruling_text": ruling_text,
        "in_favor": random.random() < 0.5,  # Random ruling
        "timestamp": time.time()
    }
    
    # Update relationships based on ruling
    from debate import update_relationship, add_emotion
    source_id = senator.get("id", 0)
    target_id = speech.get("senator_id", 0)
    
    if source_id != 0 and target_id != 0:
        # Procedural objections affect relationships
        if ruling["in_favor"]:
            # Successful objection harms relationship
            update_relationship(source_id, target_id, -0.1)
            # Target feels insulted by successful objection
            add_emotion(target_id, "insulted", 0.7, senator.get("name", "Unknown Senator"), 1)
        else:
            # Failed objection makes objector look bad
            update_relationship(source_id, target_id, -0.05)
    
    return interjection, ruling

def display_interjection(interjection: Interjection, timing: str = None) -> None:
    """
    Displays an interjection in a visually distinct way in the console.
    
    Args:
        interjection: The interjection to display
        timing: Optional override for when the interjection occurs
    """
    # Determine formatting based on type and intensity
    intensity_marker = "!" * (1 + int(interjection.intensity * 3))
    
    # Set border width and style based on interjection properties
    border_style = interjection.border_style
    width = 80  # Default width
    
    # Build title based on type
    title = f"[bold]{interjection.prefix}{intensity_marker}[/]"
    
    # Build content with Latin and English
    source_name = interjection.source_senator.get("name", "Unknown Senator")
    source_faction = interjection.source_senator.get("faction", "")
    
    # Format the source information
    if interjection.type == InterjectionType.COLLECTIVE:
        source_text = "[bold]SENATE FLOOR[/]"
    elif source_faction:
        source_text = f"[bold]{source_name}[/] ({source_faction})"
    else:
        source_text = f"[bold]{source_name}[/]"
    
    # Create the formatted content
    content_text = Text()
    
    # Add Latin with styling
    content_text.append(f"{source_text} interjects:\n\n")
    content_text.append(f"[italic yellow]{interjection.latin_content}[/]\n\n")
    
    # Add English translation
    content_text.append(f"[italic]{interjection.content}[/]")
    
    # Create and display the panel
    panel = Panel(
        content_text,
        title=title,
        border_style=border_style,
        width=width
    )
    
    console.print(panel)
    
    # If this causes disruption, add a pause and disruption notification
    if interjection.causes_disruption:
        time.sleep(0.5)  # Pause for dramatic effect
        console.print(f"[bold red]The Senate floor briefly erupts in {'disorder' if interjection.intensity > 0.7 else 'murmurs'}![/]")
        time.sleep(0.5)  # Additional pause after disruption

# ------ Helper functions ------

def _generate_interjection_content(
    interjection_type: InterjectionType,
    senator: Dict,
    speech: Dict,
    context: Dict,
    relationship: float
) -> Tuple[str, str]:
    """
    Generate appropriate content for an interjection based on its type.
    
    Returns both English and Latin versions for historical authenticity.
    
    Args:
        interjection_type: Type of interjection
        senator: Senator making the interjection
        speech: The speech being interrupted
        context: Additional context
        relationship: Relationship between senators
        
    Returns:
        Tuple of (english_content, latin_content)
    """
    speaker_name = speech.get("senator_name", "the speaker")
    
    # Acclamations - expressions of support or agreement
    if interjection_type == InterjectionType.ACCLAMATION:
        acclamations = [
            f"Well said, {speaker_name}! You speak with wisdom.",
            f"I fully support the position of {speaker_name}!",
            f"This reasoning is sound and benefits Rome.",
            f"The senator speaks truly in this matter!",
            f"{speaker_name} honors the traditions of our ancestors with these words.",
        ]
        
        latin_acclamations = [
            f"Bene dictum, {speaker_name}! Sapienter loqueris.",
            f"Sententiam {speaker_name} omnino probo!",
            f"Haec ratio proba est et Romae prodest.",
            f"Senator vere loquitur in hac re!",
            f"{speaker_name} mores maiorum his verbis honorat.",
        ]
        
        english = random.choice(acclamations)
        latin = latin_acclamations[acclamations.index(english)]  # Matching pairs
    
    # Objections - disagreements or challenges
    elif interjection_type == InterjectionType.OBJECTION:
        objections = [
            f"I must strongly disagree with {speaker_name}!",
            f"This argument betrays ignorance of the facts!",
            f"The Senate should reject this flawed reasoning!",
            f"Your words twist the truth, {speaker_name}!",
            f"This proposal would bring disaster upon Rome!",
        ]
        
        latin_objections = [
            f"Vehementer dissentio a {speaker_name}!",
            f"Hoc argumentum ignorantiam factorum prodit!",
            f"Senatus hanc rationem vitiosam repudiare debet!",
            f"Verba tua veritatem torquent, {speaker_name}!",
            f"Haec propositio cladem Romae afferet!",
        ]
        
        english = random.choice(objections)
        latin = latin_objections[objections.index(english)]
    
    # Procedural points - challenges to the process
    elif interjection_type == InterjectionType.PROCEDURAL:
        procedurals = [
            "Point of order! The senator exceeds the allotted time.",
            "I challenge the relevance of these remarks to our current debate.",
            "The senator violates protocol by addressing absent members.",
            "This matter falls outside the authorized agenda of this session.",
            "I remind the Senate that this issue was previously decided.",
        ]
        
        latin_procedurals = [
            "Ad ordinem! Senator tempus concessum excedit.",
            "Contestor pertinentiam horum verborum ad disputationem nostram.",
            "Senator protocollum violat appellando membra absentia.",
            "Haec res extra agenda huius sessionis cadit.",
            "Senatui in memoriam revoco hanc rem antea decisam esse.",
        ]
        
        english = random.choice(procedurals)
        latin = latin_procedurals[procedurals.index(english)]
    
    # Emotional outbursts - based on relationships
    elif interjection_type == InterjectionType.EMOTIONAL:
        if relationship > 0.3:  # Positive relationship
            emotionals = [
                f"I stand with my honorable friend {speaker_name}!",
                f"The wisdom of {speaker_name} is beyond question!",
                f"No one understands this matter better than {speaker_name}!",
                f"Rome is blessed to have {speaker_name}'s counsel!",
            ]
            
            latin_emotionals = [
                f"Sto cum amico meo honorabili {speaker_name}!",
                f"Sapientia {speaker_name} ultra quaestionem est!",
                f"Nemo hanc rem melius quam {speaker_name} intellegit!",
                f"Roma consilio {speaker_name} beata est!",
            ]
        else:  # Negative relationship
            emotionals = [
                f"Once again {speaker_name} misleads this body!",
                f"I cannot remain silent as {speaker_name} spreads falsehoods!",
                f"The people would weep to hear such arguments!",
                f"Your faction's agenda blinds you to reason, {speaker_name}!",
            ]
            
            latin_emotionals = [
                f"Iterum {speaker_name} hoc corpus decipit!",
                f"Non possum silere dum {speaker_name} falsa disseminat!",
                f"Populus fleret talia argumenta audiens!",
                f"Factio tua te rationi caecum facit, {speaker_name}!",
            ]
        
        english = random.choice(emotionals)
        latin = latin_emotionals[emotionals.index(english)]
    
    else:  # Default fallback
        english = f"I wish to address the points made by {speaker_name}."
        latin = f"Volo capita a {speaker_name} facta tractare."
    
    return english, latin

def _generate_crowd_reaction_content(
    reaction_type: InterjectionType,
    factions: List[str],
    speech: Dict,
    intensity: float
) -> Tuple[str, str]:
    """
    Generate content for a collective Senate reaction.
    
    Args:
        reaction_type: Type of reaction (acclaim or object)
        factions: List of factions involved in reaction
        speech: The speech being reacted to
        intensity: How strong the reaction is
        
    Returns:
        Tuple of (english_content, latin_content)
    """
    # Format faction text for inclusion
    faction_text = ""
    if factions:
        if len(factions) == 1:
            faction_text = f"from the {factions[0]} faction"
        elif len(factions) == 2:
            faction_text = f"from the {factions[0]} and {factions[1]} factions"
        else:
            faction_text = f"from multiple factions"
    
    # Reaction descriptions based on intensity
    if intensity < 0.4:
        intensity_level = "low"
    elif intensity < 0.7:
        intensity_level = "medium"
    else:
        intensity_level = "high"
    
    # Generate content based on type and intensity
    if reaction_type == InterjectionType.ACCLAMATION:
        if intensity_level == "low":
            english = f"Murmurs of approval {faction_text} ripple through the Senate chamber."
            latin = f"Murmura approbationis {_translate_factions_to_latin(faction_text)} per Senatum fluunt."
        elif intensity_level == "medium":
            english = f"Senators {faction_text} voice their support with 'Recte!' and 'Bene!'"
            latin = f"Senatores {_translate_factions_to_latin(faction_text)} 'Recte!' et 'Bene!' clamant."
        else:
            english = f"The chamber erupts with cries of 'Ita vero!' and loud approval {faction_text}."
            latin = f"Curia clamoribus 'Ita vero!' et magna approbatione {_translate_factions_to_latin(faction_text)} erumpit."
    else:  # OBJECTION
        if intensity_level == "low":
            english = f"Disapproving murmurs {faction_text} can be heard in the chamber."
            latin = f"Murmura improbationis {_translate_factions_to_latin(faction_text)} in curia audiuntur."
        elif intensity_level == "medium":
            english = f"Senators {faction_text} voice objections with calls of 'Absurdum!' and shaking heads."
            latin = f"Senatores {_translate_factions_to_latin(faction_text)} 'Absurdum!' vociferantur et capita quassant."
        else:
            english = f"Loud objections and cries of 'Numquam!' echo through the chamber {faction_text}."
            latin = f"Obiectiones magnae et clamores 'Numquam!' per curiam {_translate_factions_to_latin(faction_text)} resonant."
    
    return english, latin

def _translate_to_latin(phrase: str) -> str:
    """Simple translation helper for common procedural terms."""
    translations = {
        "speaking time limit violation": "violationem limitis temporis loquendi",
        "irrelevance to the topic": "irrelevantiam ad argumentum",
        "improper reference to absent senators": "mentionem improprium senatorum absentium",
        "violation of speaking order": "violationem ordinis loquendi",
        "excessive personal attacks": "excessum in impetibus personalibus",
        "reference to prohibited religious matters": "mentionem rerum religiosarum prohibitarum",
        "improper invocation of foreign powers": "invocationem improprium potestatum externarum"
    }
    
    return translations.get(phrase.lower(), "rem improprium")

def _translate_factions_to_latin(faction_text: str) -> str:
    """Translate faction references to Latin."""
    if "Optimates" in faction_text:
        faction_text = faction_text.replace("Optimates", "Optimatium")
    if "Populares" in faction_text:
        faction_text = faction_text.replace("Populares", "Popularium")
    if "Military" in faction_text:
        faction_text = faction_text.replace("Military", "Militaris")
    if "Religious" in faction_text:
        faction_text = faction_text.replace("Religious", "Religiosi")
    if "Merchant" in faction_text:
        faction_text = faction_text.replace("Merchant", "Mercatorum")
    if "multiple factions" in faction_text:
        faction_text = faction_text.replace("multiple factions", "multis factionibus")
    if "from the" in faction_text:
        faction_text = faction_text.replace("from the", "ex")
    if "and" in faction_text:
        faction_text = faction_text.replace("and", "et")
        
    return faction_text

def integrate_with_debate(
    speech: Dict,
    speaking_senator: Dict,
    all_senators: List[Dict],
    officials: Any = None,
    context: Dict = None
) -> List[Dict]:
    """
    Main integration point with the debate module to generate and process interjections.
    
    This function handles generating appropriate interjections during a speech,
    displaying them, and returning information about them for debate impact.
    
    Args:
        speech: The current speech being given
        speaking_senator: The senator giving the speech
        all_senators: All senators present in the session
        officials: Presiding officials object (optional)
        context: Additional context about the topic/debate
        
    Returns:
        List of interjection results with their impacts
    """
    # Skip interjections if no other senators present
    if len(all_senators) <= 1:
        return []
    
    # Track all interjections and their results
    interjection_results = []
    
    # Identify non-speaking senators who might interject
    other_senators = [s for s in all_senators if s.get("id") != speaking_senator.get("id")]
    
    # Random number of potential interjections based on speech length/quality
    speech_quality = speech.get("quality_factor", 0.5)
    speech_length = 1
    if speech.get("speech_length") == "2-3":
        speech_length = 2
    elif speech.get("speech_length") == "3-4":
        speech_length = 3
    elif speech.get("speech_length") == "5-7":
        speech_length = 5
    
    # More controversial speeches get more interjections
    base_interjections = int(speech_length * (0.5 + speech_quality * 0.5))
    max_interjections = min(len(other_senators), base_interjections)
    
    # Randomly select some senators who might interject
    potential_interjectors = random.sample(
        other_senators,
        min(max_interjections, len(other_senators))
    )
    
    # Process individual interjections
    for senator in potential_interjectors:
        interjection = generate_interjection(
            senator=senator,
            speech=speech,
            context=context or {},
            previous_interjections=[r.get("interjection") for r in interjection_results if "interjection" in r]
        )
        
        if interjection:
            # Display the interjection
            display_interjection(interjection)
            
            # For procedural objections, get ruling if officials provided
            ruling = None
            if interjection.type == InterjectionType.PROCEDURAL and officials:
                interjection, ruling = handle_procedural_objection(
                    senator=senator,
                    speech=speech,
                    officials=officials
                )
                
                # Display the ruling if available
                if ruling:
                    console.print(Panel(
                        f"[bold]{ruling['official'].get('title', 'Consul')} {ruling['official'].get('name', 'Unknown')}[/] rules:\n\n"
                        f"{ruling['ruling_text']}",
                        title="[bold yellow]RULING[/]",
                        border_style="yellow",
                        width=80
                    ))
            
            # Add to results
            result = {
                "interjection": interjection,
                "ruling": ruling,
                "impact": {
                    "disruption": interjection.causes_disruption,
                    "intensity": interjection.intensity,
                    "affects_relationships": interjection.causes_disruption,
                    "source_id": interjection.source_senator.get("id", 0),
                    "target_id": speech.get("senator_id", 0)
                }
            }
            interjection_results.append(result)
            
            # Add a small pause after each interjection for readability
            time.sleep(0.5)
    
    # Potentially add a crowd reaction
    if random.random() < 0.3 and interjection_results:  # 30% chance if there were already interjections
        crowd_reaction = process_crowd_reaction(
            speech=speech,
            senators=all_senators,
            context=context
        )
        
        if crowd_reaction:
            # Display the crowd reaction
            display_interjection(crowd_reaction)
            
            # Add to results
            result = {
                "interjection": crowd_reaction,
                "ruling": None,
                "impact": {
                    "disruption": crowd_reaction.causes_disruption,
                    "intensity": crowd_reaction.intensity,
                    "affects_relationships": False,  # Crowd reactions don't directly affect relationships
                    "collective": True
                }
            }
            interjection_results.append(result)
    
    return interjection_results