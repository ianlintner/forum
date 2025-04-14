#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Roman Senate AI Game
Historical Context Module

This module provides historically accurate references, figures, and events
for speech generation based on the selected year in Roman history.
"""

import random
from typing import Dict, List, Tuple, Optional, Any
import sys
import os

# Add a fallback implementation instead of importing from debate to avoid circular imports
def get_original_historical_context(year: int) -> str:
    """
    Basic fallback implementation of the historical context function.
    This prevents circular imports with debate.py.
    
    Args:
        year (int): The year in Roman history (negative for BCE)
        
    Returns:
        str: Historical context description
    """
    year_bce = abs(year)
    
    # Early Republic
    if -509 <= year <= -287:
        return f"Year {year_bce} BCE. Early Republic period. Rome is establishing its republican institutions after the expulsion of the kings. The conflict between patricians and plebeians is central to politics."
    
    # Middle Republic
    elif -286 <= year <= -134:
        return f"Year {year_bce} BCE. Middle Republic period. Rome is expanding its influence throughout Italy and the Mediterranean. The Punic Wars against Carthage define this era."
    
    # Late Republic
    elif -133 <= year <= -27:
        return f"Year {year_bce} BCE. Late Republic period. Internal political strife is increasing. Powerful generals and politicians vie for control as traditional republican institutions are strained."
    
    # Default/fallback
    else:
        return f"Year {year_bce} BCE. This period in Roman history."

# Try to import topic_generator's historical context function if available
try:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from topic_generator import get_historical_period_context
    original_get_historical_context = get_historical_period_context
except ImportError:
    # Use our fallback implementation if import fails
    original_get_historical_context = get_original_historical_context

# Historical figures by time period
HISTORICAL_FIGURES = {
    # Early Republic (509-287 BCE)
    (-509, -450): [
        {"name": "Lucius Junius Brutus", "title": "founder of the Republic", "achievement": "expelled the kings"},
        {"name": "Publius Valerius Publicola", "title": "consul", "achievement": "established republican laws"},
        {"name": "Coriolanus", "title": "general", "achievement": "defected to the Volsci"},
        {"name": "Appius Claudius", "title": "decemvir", "achievement": "created the Twelve Tables"},
        {"name": "Lucius Quinctius Cincinnatus", "title": "dictator", "achievement": "saved Rome and returned to his farm"}
    ],
    
    (-449, -400): [
        {"name": "Marcus Furius Camillus", "title": "general", "achievement": "defeated the Gauls"},
        {"name": "Gaius Licinius Stolo", "title": "tribune", "achievement": "passed the Licinian-Sextian laws"},
        {"name": "Lucius Sextius", "title": "tribune", "achievement": "first plebeian consul"},
        {"name": "Appius Claudius Caecus", "title": "censor", "achievement": "built the Appian Way"}
    ],
    
    # Middle Republic (399-134 BCE)
    (-399, -300): [
        {"name": "Marcus Manlius Capitolinus", "title": "consul", "achievement": "defended the Capitol from the Gauls"},
        {"name": "Lucius Papirius Cursor", "title": "dictator", "achievement": "victories against the Samnites"},
        {"name": "Quintus Fabius Maximus Rullianus", "title": "consul", "achievement": "reformed the equestrian order"}
    ],
    
    (-299, -200): [
        {"name": "Manius Curius Dentatus", "title": "consul", "achievement": "defeated Pyrrhus"},
        {"name": "Appius Claudius Caudex", "title": "consul", "achievement": "began First Punic War"},
        {"name": "Gaius Duilius", "title": "consul", "achievement": "first Roman naval victory"},
        {"name": "Quintus Fabius Maximus Cunctator", "title": "dictator", "achievement": "delayed Hannibal through attrition"},
        {"name": "Publius Cornelius Scipio Africanus", "title": "general", "achievement": "defeated Hannibal at Zama"}
    ],
    
    (-199, -134): [
        {"name": "Titus Quinctius Flamininus", "title": "general", "achievement": "proclaimed freedom of Greece"},
        {"name": "Marcus Porcius Cato", "title": "censor", "achievement": "champion of traditional Roman values"},
        {"name": "Lucius Aemilius Paullus", "title": "general", "achievement": "conquered Macedonia"},
        {"name": "Publius Cornelius Scipio Aemilianus", "title": "general", "achievement": "destroyed Carthage"}
    ],
    
    # Late Republic (133-27 BCE)
    (-133, -100): [
        {"name": "Tiberius Sempronius Gracchus", "title": "tribune", "achievement": "land reform attempts"},
        {"name": "Gaius Sempronius Gracchus", "title": "tribune", "achievement": "expanded reforms"},
        {"name": "Gaius Marius", "title": "consul", "achievement": "military reforms and defeating the Germans"},
        {"name": "Lucius Cornelius Sulla", "title": "dictator", "achievement": "constitutional reforms and proscriptions"}
    ],
    
    (-99, -50): [
        {"name": "Gnaeus Pompeius Magnus", "title": "general", "achievement": "conquered the East"},
        {"name": "Marcus Licinius Crassus", "title": "triumvir", "achievement": "defeated Spartacus"},
        {"name": "Marcus Tullius Cicero", "title": "consul", "achievement": "exposed the Catilinarian conspiracy"},
        {"name": "Gaius Julius Caesar", "title": "general", "achievement": "conquered Gaul"}
    ],
    
    (-49, -27): [
        {"name": "Marcus Junius Brutus", "title": "liberator", "achievement": "assassinated Caesar"},
        {"name": "Gaius Cassius Longinus", "title": "liberator", "achievement": "planned Caesar's assassination"},
        {"name": "Marcus Antonius", "title": "triumvir", "achievement": "ruled the East with Cleopatra"},
        {"name": "Gaius Octavius", "title": "Augustus", "achievement": "first Roman Emperor"}
    ]
}

# Important events by time period
HISTORICAL_EVENTS = {
    # Early Republic (509-287 BCE)
    (-509, -450): [
        {"name": "Founding of the Republic", "year": -509, "significance": "established republican government"},
        {"name": "Battle of Lake Regillus", "year": -496, "significance": "defeated Latin allies of Tarquins"},
        {"name": "First Secession of the Plebs", "year": -494, "significance": "creation of Tribune of the Plebs"},
        {"name": "Battle of Veii", "year": -477, "significance": "war with neighboring Etruscan city"},
        {"name": "Law of the Twelve Tables", "year": -451, "significance": "first written Roman law code"}
    ],
    
    (-449, -400): [
        {"name": "Creation of military tribunes with consular power", "year": -445, "significance": "allowed plebeians in executive office"},
        {"name": "Siege of Veii", "year": -396, "significance": "Rome's first major territorial expansion"},
        {"name": "Gallic sack of Rome", "year": -390, "significance": "destruction of early records and city rebuilding"}
    ],
    
    # Middle Republic (399-134 BCE)
    (-399, -300): [
        {"name": "Licinian-Sextian Laws", "year": -367, "significance": "economic reforms and plebeian consul access"},
        {"name": "Latin War", "year": -340, "significance": "Rome secured dominance over Latium"},
        {"name": "Samnite Wars", "year": -343, "significance": "extended Roman influence in central Italy"}
    ],
    
    (-299, -200): [
        {"name": "Third Samnite War", "year": -298, "significance": "Rome secured central Italy"},
        {"name": "Pyrrhic War", "year": -280, "significance": "victory over Greek armies in Italy"},
        {"name": "First Punic War", "year": -264, "significance": "began Rome's overseas expansion"},
        {"name": "Second Punic War", "year": -218, "significance": "existential threat from Hannibal"},
        {"name": "Battle of Zama", "year": -202, "significance": "decided mastery of western Mediterranean"}
    ],
    
    (-199, -134): [
        {"name": "Second Macedonian War", "year": -200, "significance": "expanded influence in Greece"},
        {"name": "War with Antiochus", "year": -192, "significance": "defeated Seleucid Empire"},
        {"name": "Third Macedonian War", "year": -171, "significance": "ended Macedonian kingdom"},
        {"name": "Third Punic War", "year": -149, "significance": "destroyed Carthage"}
    ],
    
    # Late Republic (133-27 BCE)
    (-133, -100): [
        {"name": "Tiberius Gracchus's tribunate", "year": -133, "significance": "began period of reform and violence"},
        {"name": "Gaius Gracchus's tribunate", "year": -123, "significance": "expanded reforms and heightened tensions"},
        {"name": "Jugurthine War", "year": -112, "significance": "exposed corruption in Senate"},
        {"name": "Cimbrian War", "year": -113, "significance": "Germanic invasion threat"},
        {"name": "Social War", "year": -91, "significance": "Italian allies fought for citizenship"}
    ],
    
    (-99, -50): [
        {"name": "Sulla's dictatorship", "year": -82, "significance": "constitutional reforms strengthening Senate"},
        {"name": "Spartacus Revolt", "year": -73, "significance": "largest slave uprising"},
        {"name": "Catilinarian Conspiracy", "year": -63, "significance": "plot to overthrow government"},
        {"name": "First Triumvirate", "year": -60, "significance": "alliance of Caesar, Pompey, Crassus"},
        {"name": "Conquest of Gaul", "year": -58, "significance": "Caesar's military campaigns"}
    ],
    
    (-49, -27): [
        {"name": "Crossing the Rubicon", "year": -49, "significance": "Caesar began civil war"},
        {"name": "Battle of Pharsalus", "year": -48, "significance": "Caesar defeated Pompey"},
        {"name": "Caesar's Dictatorship", "year": -46, "significance": "reforms and centralization of power"},
        {"name": "Assassination of Caesar", "year": -44, "significance": "attempted restoration of Republic"},
        {"name": "Second Triumvirate", "year": -43, "significance": "alliance of Octavian, Antony, Lepidus"},
        {"name": "Battle of Actium", "year": -31, "significance": "Octavian defeated Antony and Cleopatra"}
    ]
}

# Roman values and virtues with time period relevance
ROMAN_VALUES = {
    # Early-Mid Republic (most traditional)
    (-509, -200): [
        {"name": "virtus", "translation": "virtue, courage", "significance": "martial valor, excellence as a soldier"},
        {"name": "pietas", "translation": "piety, duty", "significance": "duty to gods, family, and state"},
        {"name": "dignitas", "translation": "dignity, prestige", "significance": "personal standing and honor"},
        {"name": "gravitas", "translation": "seriousness", "significance": "sobriety and moral rigor"},
        {"name": "disciplina", "translation": "discipline", "significance": "military and personal self-control"},
        {"name": "frugalitas", "translation": "frugality", "significance": "simple living, avoiding luxury"}
    ],
    
    # Late Republic (evolving values)
    (-199, -27): [
        {"name": "virtus", "translation": "virtue, courage", "significance": "broader concept of excellence"},
        {"name": "pietas", "translation": "piety, duty", "significance": "increasingly political meaning"},
        {"name": "dignitas", "translation": "dignity, prestige", "significance": "political standing and influence"},
        {"name": "gravitas", "translation": "seriousness", "significance": "authority in public speaking"},
        {"name": "humanitas", "translation": "humanity, refinement", "significance": "education and culture"},
        {"name": "clementia", "translation": "mercy", "significance": "political tool for winning loyalty"}
    ]
}

# Political terms and concepts by period
POLITICAL_TERMS = {
    # Early Republic
    (-509, -350): [
        {"term": "mos maiorum", "translation": "way of the ancestors", "usage": "appealing to tradition"},
        {"term": "patres", "translation": "fathers, senators", "usage": "reference to Senate as institution"},
        {"term": "plebs", "translation": "common people", "usage": "reference to non-patrician citizens"},
        {"term": "auctoritas", "translation": "authority", "usage": "Senate's advisory power"}
    ],
    
    # Middle Republic
    (-349, -150): [
        {"term": "novus homo", "translation": "new man", "usage": "first in family to reach high office"},
        {"term": "cursus honorum", "translation": "course of offices", "usage": "political career path"},
        {"term": "lex", "translation": "law", "usage": "legislation passed by assemblies"},
        {"term": "provincia", "translation": "province", "usage": "area of military command"}
    ],
    
    # Late Republic
    (-149, -27): [
        {"term": "optimates", "translation": "best men", "usage": "conservative faction label"},
        {"term": "populares", "translation": "populists", "usage": "reform-minded faction label"},
        {"term": "dignitas", "translation": "dignity, rank", "usage": "political standing"},
        {"term": "res publica", "translation": "public affair, commonwealth", "usage": "state interests"}
    ]
}

# Latin phrases appropriate to different time periods
LATIN_PHRASES = {
    # Early Republic (simpler expressions)
    (-509, -300): [
        {"phrase": "Senatus Populusque Romanus", "translation": "The Senate and People of Rome", "usage": "formal address"},
        {"phrase": "pro patria", "translation": "for the fatherland", "usage": "patriotic appeal"},
        {"phrase": "more maiorum", "translation": "according to ancestral custom", "usage": "traditional argument"},
        {"phrase": "di immortales", "translation": "immortal gods", "usage": "religious invocation"}
    ],
    
    # Middle Republic (expanding political vocabulary)
    (-299, -150): [
        {"phrase": "cum dignitate otium", "translation": "peace with dignity", "usage": "political ideal"},
        {"phrase": "gloria militaris", "translation": "military glory", "usage": "appeal to martial values"},
        {"phrase": "civium consensu", "translation": "by consent of the citizens", "usage": "popular legitimacy"},
        {"phrase": "salus populi suprema lex", "translation": "people's welfare is the highest law", "usage": "civic duty"}
    ],
    
    # Late Republic (sophisticated political rhetoric)
    (-149, -27): [
        {"phrase": "concordia ordinum", "translation": "harmony between social orders", "usage": "social unity appeal"},
        {"phrase": "optimo iure", "translation": "by the best law", "usage": "legal argument"},
        {"phrase": "summum bonum", "translation": "highest good", "usage": "philosophical reference"},
        {"phrase": "exempli gratia", "translation": "for the sake of example", "usage": "rhetorical device"}
    ]
}

def get_historical_context_for_speech(year: int, topic: str = None) -> Dict[str, Any]:
    """
    Get a rich collection of historical references for a specific year,
    tailored for speech generation.
    
    Args:
        year: The year in Roman history (negative for BCE)
        topic: Optional topic to guide reference selection
        
    Returns:
        Dictionary containing historical figures, events, values, terms and phrases
        appropriate for the specified time period
    """
    # Get the basic historical context first
    base_context = original_get_historical_context(year)
    
    # Convert year to positive BCE for readability
    year_bce = abs(year)
    
    # Determine the relevant time periods for selection
    figures_period = None
    events_period = None
    values_period = None
    terms_period = None
    phrases_period = None
    
    # Find the appropriate time periods for each category
    for period in HISTORICAL_FIGURES:
        if period[0] <= year <= period[1]:
            figures_period = period
            break
    
    for period in HISTORICAL_EVENTS:
        if period[0] <= year <= period[1]:
            events_period = period
            break
    
    for period in ROMAN_VALUES:
        if period[0] <= year <= period[1]:
            values_period = period
            break
    
    for period in POLITICAL_TERMS:
        if period[0] <= year <= period[1]:
            terms_period = period
            break
    
    for period in LATIN_PHRASES:
        if period[0] <= year <= period[1]:
            phrases_period = period
            break
    
    # Select figures appropriate for the time period
    selected_figures = []
    if figures_period:
        # Figures who lived before or during this year (not future figures)
        available_figures = [f for f in HISTORICAL_FIGURES[figures_period] 
                            if not f.get("year") or f.get("year", year+100) <= year]
        
        # Select 2-3 prominent figures
        if available_figures:
            count = min(random.randint(2, 3), len(available_figures))
            selected_figures = random.sample(available_figures, count)
    
    # Select events appropriate for the time period
    selected_events = []
    if events_period:
        # Events that occurred before this year (not future events)
        available_events = [e for e in HISTORICAL_EVENTS[events_period] 
                           if e.get("year", year+100) <= year]
        
        # Select 2-3 significant events
        if available_events:
            count = min(random.randint(2, 3), len(available_events))
            selected_events = random.sample(available_events, count)
    
    # Select Roman values
    selected_values = []
    if values_period:
        # Select 2-3 values
        if ROMAN_VALUES[values_period]:
            count = min(random.randint(2, 3), len(ROMAN_VALUES[values_period]))
            selected_values = random.sample(ROMAN_VALUES[values_period], count)
    
    # Select political terms
    selected_terms = []
    if terms_period:
        # Select 2-3 terms
        if POLITICAL_TERMS[terms_period]:
            count = min(random.randint(2, 3), len(POLITICAL_TERMS[terms_period]))
            selected_terms = random.sample(POLITICAL_TERMS[terms_period], count)
    
    # Select Latin phrases
    selected_phrases = []
    if phrases_period:
        # Select 2-3 phrases
        if LATIN_PHRASES[phrases_period]:
            count = min(random.randint(2, 3), len(LATIN_PHRASES[phrases_period]))
            selected_phrases = random.sample(LATIN_PHRASES[phrases_period], count)
    
    # Combine all selections into a structured context object
    return {
        "year": year,
        "year_display": f"{year_bce} BCE",
        "base_context": base_context,
        "figures": selected_figures,
        "events": selected_events,
        "values": selected_values,
        "political_terms": selected_terms,
        "latin_phrases": selected_phrases
    }

def get_historically_appropriate_address(year: int, audience: str = "senate") -> str:
    """
    Get a historically appropriate formal address for the beginning of a speech.
    
    Args:
        year: The year in Roman history (negative for BCE)
        audience: The audience being addressed (default: "senate")
        
    Returns:
        A string containing an appropriate formal address
    """
    # Early Republic (more simple)
    if -509 <= year <= -300:
        if audience == "senate":
            return random.choice([
                "Patres conscripti",  # Conscript fathers
                "Senatores",          # Senators
                "Quirites"            # Citizens (formal address)
            ])
        else:
            return "Quirites"  # Default address to citizens
    
    # Middle Republic (more formal)
    elif -299 <= year <= -150:
        if audience == "senate":
            return random.choice([
                "Patres conscripti",                  # Conscript fathers
                "Patres et conscripti",               # Fathers and conscripts
                "Senatus populusque Romanus"          # Senate and People of Rome
            ])
        else:
            return random.choice([
                "Quirites",                           # Citizens
                "Cives Romani"                        # Roman citizens
            ])
    
    # Late Republic (most elaborate)
    else:
        if audience == "senate":
            return random.choice([
                "Patres conscripti",                  # Conscript fathers
                "Patres et iudices",                  # Fathers and judges
                "Senatus amplissimus",                # Most distinguished Senate
                "Patres conscripti et cives optimi"   # Conscript fathers and best citizens
            ])
        else:
            return random.choice([
                "Quirites",                           # Citizens
                "Populus Romanus",                    # Roman People
                "Cives et socii"                      # Citizens and allies
            ])

def generate_historical_reference(context: Dict[str, Any], reference_type: str = None) -> str:
    """
    Generate a historical reference based on the context.
    
    Args:
        context: Historical context from get_historical_context_for_speech()
        reference_type: Optional type of reference to generate (figure, event, value)
        
    Returns:
        String containing the historical reference
    """
    if not reference_type:
        reference_type = random.choice(["figure", "event", "value", "phrase"])
    
    if reference_type == "figure" and context.get("figures"):
        figure = random.choice(context["figures"])
        templates = [
            f"As {figure['name']}, {figure['title']}, demonstrated when he {figure['achievement']}",
            f"We should remember the example of {figure['name']}, who {figure['achievement']}",
            f"Following in the footsteps of {figure['name']}, the {figure['title']} who {figure['achievement']}"
        ]
        return random.choice(templates)
    
    elif reference_type == "event" and context.get("events"):
        event = random.choice(context["events"])
        year_display = abs(event["year"])
        templates = [
            f"In {year_display} BCE, the {event['name']} {event['significance']}",
            f"We learned from the {event['name']} of {year_display} BCE that {event['significance']}",
            f"The {event['name']} taught us the importance of {event['significance']}"
        ]
        return random.choice(templates)
    
    elif reference_type == "value" and context.get("values"):
        value = random.choice(context["values"])
        templates = [
            f"Our ancestors valued {value['name']} ({value['translation']}), which means {value['significance']}",
            f"The virtue of {value['name']} reminds us of {value['significance']}",
            f"As Romans, we must uphold {value['name']} – {value['significance']}"
        ]
        return random.choice(templates)
    
    elif reference_type == "phrase" and context.get("latin_phrases"):
        phrase = random.choice(context["latin_phrases"])
        templates = [
            f"{phrase['phrase']} – {phrase['translation']}",
            f"As we say, {phrase['phrase']}, meaning {phrase['translation']}",
            f"{phrase['phrase']}! {phrase['translation']}!"
        ]
        return random.choice(templates)
    
    else:
        # Fallback if no reference of the requested type is available
        return f"As our ancestors have shown us"