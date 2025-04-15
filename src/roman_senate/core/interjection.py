"""
Roman Senate Game
Interjection Module

This module manages senator interjections during speeches, adding historical 
authenticity to debates with spontaneous reactions from senators.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, Any, List

class InterjectionType(Enum):
    """Types of interjections based on historical Roman Senate practices."""
    ACCLAMATION = "acclamation"  # Expressions of support (e.g., "Bene!")
    OBJECTION = "objection"      # Expressions of disagreement
    PROCEDURAL = "procedural"    # Points of order or procedure
    EMOTIONAL = "emotional"      # Personal reactions
    COLLECTIVE = "collective"    # Group reactions

class InterjectionTiming(Enum):
    """When during a speech the interjection occurs."""
    BEGINNING = "beginning"
    MIDDLE = "middle"
    END = "end"
    ANY = "any"

@dataclass
class Interjection:
    """
    Represents a senator's interjection during a speech.
    
    Attributes:
        senator_name: Name of the senator making the interjection
        type: Type of interjection (acclamation, objection, etc.)
        latin_content: Latin text of the interjection
        english_content: English translation of the interjection
        target_senator: Name of the senator being responded to
        timing: When during the speech the interjection occurs
        intensity: How forceful the interjection is (0.0-1.0)
        causes_disruption: Whether the interjection disrupts the flow of debate
    """
    senator_name: str
    type: InterjectionType
    latin_content: str
    english_content: str
    target_senator: str
    timing: InterjectionTiming = InterjectionTiming.ANY
    intensity: float = 0.5
    causes_disruption: bool = False
    
    def get_display_style(self) -> Dict[str, str]:
        """Get the display styling for this interjection type."""
        styles = {
            InterjectionType.ACCLAMATION: {
                "color": "green",
                "prefix": "[Acclaim]"
            },
            InterjectionType.OBJECTION: {
                "color": "red",
                "prefix": "[Object]"
            },
            InterjectionType.PROCEDURAL: {
                "color": "yellow",
                "prefix": "[Procedure]"
            },
            InterjectionType.EMOTIONAL: {
                "color": "magenta",
                "prefix": "[Emotion]"
            },
            InterjectionType.COLLECTIVE: {
                "color": "cyan",
                "prefix": "[Reaction]"
            }
        }
        
        return styles.get(self.type, {"color": "white", "prefix": "[Comment]"})
    
    def __str__(self) -> str:
        """Return a formatted string representation of the interjection."""
        style = self.get_display_style()
        return f"{style['prefix']} {self.senator_name}: {self.latin_content} ({self.english_content})"


def generate_fallback_interjection(
    senator_name: str, 
    target_senator: str, 
    interjection_type: InterjectionType
) -> Interjection:
    """
    Generate a fallback interjection when LLM generation fails.
    
    Args:
        senator_name: Name of the senator making the interjection
        target_senator: Name of the senator being responded to
        interjection_type: Type of interjection to generate
        
    Returns:
        A simple Interjection object with predetermined text
    """
    fallbacks = {
        InterjectionType.ACCLAMATION: {
            "latin": "Bene dictum!",
            "english": "Well said!"
        },
        InterjectionType.OBJECTION: {
            "latin": "Minime! Absurdum est!",
            "english": "No! That's absurd!"
        },
        InterjectionType.PROCEDURAL: {
            "latin": "Ad ordinem!",
            "english": "Point of order!"
        },
        InterjectionType.EMOTIONAL: {
            "latin": "Non possum silere!",
            "english": "I cannot remain silent!"
        },
        InterjectionType.COLLECTIVE: {
            "latin": "Murmura e senatu...",
            "english": "Murmurs from the senate..."
        }
    }
    
    fallback = fallbacks.get(interjection_type, {
        "latin": "Eheu!",
        "english": "Alas!"
    })
    
    return Interjection(
        senator_name=senator_name,
        type=interjection_type,
        latin_content=fallback["latin"],
        english_content=fallback["english"],
        target_senator=target_senator,
        intensity=0.5,
        causes_disruption=interjection_type in [InterjectionType.PROCEDURAL, InterjectionType.EMOTIONAL]
    )