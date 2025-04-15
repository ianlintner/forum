#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Roman Senate AI Game
Historical Context Module

This module provides historical context data for Roman speeches,
including appropriate historical figures, events, and values
based on the time period.
"""

import random
from typing import Dict, List, Optional, Any

# Historical periods of the Roman Republic
HISTORICAL_PERIODS = {
    "early_republic": (-509, -300),   # Early Republic
    "middle_republic": (-299, -150),  # Middle Republic
    "late_republic": (-149, -27)      # Late Republic (until Augustus)
}

# Notable historical figures by period
HISTORICAL_FIGURES = {
    "early_republic": [
        {"name": "Lucius Junius Brutus", "title": "Founder of the Republic", "years": (-509, -509)},
        {"name": "Cincinnatus", "title": "Dictator who relinquished power", "years": (-458, -438)},
        {"name": "Appius Claudius", "title": "Decemvir and legal reformer", "years": (-451, -449)},
        {"name": "Marcus Furius Camillus", "title": "Savior of Rome from the Gauls", "years": (-396, -365)},
        {"name": "Gaius Licinius Stolo", "title": "Tribune and reformer", "years": (-376, -367)}
    ],
    "middle_republic": [
        {"name": "Quintus Fabius Maximus", "title": "Cunctator (the Delayer)", "years": (-280, -203)},
        {"name": "Scipio Africanus", "title": "Conqueror of Hannibal", "years": (-236, -183)},
        {"name": "Cato the Elder", "title": "The Censor", "years": (-234, -149)},
        {"name": "Tiberius Gracchus", "title": "Land reformer", "years": (-168, -133)},
        {"name": "Scipio Aemilianus", "title": "Destroyer of Carthage", "years": (-185, -129)}
    ],
    "late_republic": [
        {"name": "Gaius Marius", "title": "Seven-time consul and military reformer", "years": (-157, -86)},
        {"name": "Lucius Cornelius Sulla", "title": "Dictator and constitutional reformer", "years": (-138, -78)},
        {"name": "Pompey the Great", "title": "Military commander and triumvir", "years": (-106, -48)},
        {"name": "Marcus Tullius Cicero", "title": "Consul and orator", "years": (-106, -43)},
        {"name": "Julius Caesar", "title": "General, consul, and dictator", "years": (-100, -44)},
        {"name": "Cato the Younger", "title": "Republican traditionalist", "years": (-95, -46)},
        {"name": "Marcus Junius Brutus", "title": "Liberator", "years": (-85, -42)}
    ]
}

# Notable historical events by period
HISTORICAL_EVENTS = {
    "early_republic": [
        {"name": "Founding of the Republic", "year": -509, "description": "Overthrow of the monarchy and establishment of the Republic"},
        {"name": "Secession of the Plebs", "year": -494, "description": "Plebeians seceded to the Sacred Mount to demand rights"},
        {"name": "Creation of the Twelve Tables", "year": -451, "description": "First written legal code of Rome"},
        {"name": "Gallic Sack of Rome", "year": -390, "description": "Rome was captured and sacked by Gallic tribes"}
    ],
    "middle_republic": [
        {"name": "Battle of Cannae", "year": -216, "description": "Devastating defeat by Hannibal"},
        {"name": "Battle of Zama", "year": -202, "description": "Defeat of Hannibal by Scipio Africanus"},
        {"name": "Third Punic War", "year": -149, "description": "Final conflict with Carthage"},
        {"name": "Destruction of Carthage", "year": -146, "description": "Complete destruction of Carthage and its territory"}
    ],
    "late_republic": [
        {"name": "Reforms of the Gracchi", "years": (-133, -121), "description": "Attempted land reforms leading to political violence"},
        {"name": "Sulla's March on Rome", "year": -88, "description": "First time a Roman general marched on Rome with his legions"},
        {"name": "First Triumvirate", "year": -60, "description": "Political alliance between Caesar, Pompey, and Crassus"},
        {"name": "Crossing the Rubicon", "year": -49, "description": "Caesar's fateful decision leading to civil war"},
        {"name": "Assassination of Caesar", "year": -44, "description": "Caesar's murder in the Senate on the Ides of March"}
    ]
}

# Roman values and virtues by period (with some evolution)
ROMAN_VALUES = {
    "early_republic": [
        {"name": "Virtus", "description": "Manliness, valor in war"},
        {"name": "Pietas", "description": "Duty to gods, homeland, and family"},
        {"name": "Fides", "description": "Trustworthiness and reliability"},
        {"name": "Mos Maiorum", "description": "Ways of the elders/ancestors"},
        {"name": "Disciplina", "description": "Military discipline"}
    ],
    "middle_republic": [
        {"name": "Virtus", "description": "Valor and excellence"},
        {"name": "Pietas", "description": "Religious and familial duty"},
        {"name": "Gravitas", "description": "Seriousness of character"},
        {"name": "Dignitas", "description": "Personal standing and honor"},
        {"name": "Constantia", "description": "Steadfastness"},
        {"name": "Frugalitas", "description": "Frugality and simplicity"}
    ],
    "late_republic": [
        {"name": "Dignitas", "description": "Personal dignity and political standing"},
        {"name": "Auctoritas", "description": "Prestige and influence"},
        {"name": "Clementia", "description": "Mercy toward opponents"},
        {"name": "Libertas", "description": "Political freedom"},
        {"name": "Gloria", "description": "Fame and prestige"},
        {"name": "Eloquentia", "description": "Persuasive oratory"}
    ]
}

# Common topics of debate with associated references
DEBATE_TOPICS = {
    "land_reform": {
        "figures": ["Tiberius Gracchus", "Gaius Gracchus", "Appius Claudius"],
        "events": ["Secession of the Plebs", "Reforms of the Gracchi"],
        "values": ["Iustitia", "Libertas", "Aequitas"]
    },
    "military_command": {
        "figures": ["Scipio Africanus", "Gaius Marius", "Pompey", "Julius Caesar"],
        "events": ["Battle of Zama", "Sulla's March on Rome", "Crossing the Rubicon"],
        "values": ["Virtus", "Imperium", "Gloria", "Disciplina"]
    },
    "taxation": {
        "figures": ["Cato the Elder", "Gaius Gracchus", "Crassus"],
        "events": ["Creation of the Twelve Tables", "Punic Wars"],
        "values": ["Frugalitas", "Iustitia", "Severitas"]
    },
    "foreign_policy": {
        "figures": ["Cato the Elder", "Scipio Africanus", "Pompey"],
        "events": ["Destruction of Carthage", "Third Punic War"],
        "values": ["Fides", "Dignitas", "Virtus"]
    },
    "citizenship": {
        "figures": ["Gaius Marius", "Lucius Cornelius Sulla", "Cicero"],
        "events": ["Social War", "Reforms of the Gracchi"],
        "values": ["Libertas", "Dignitas", "Civitas"]
    },
    "corruption": {
        "figures": ["Cato the Elder", "Cato the Younger", "Cicero"],
        "events": ["Jugurthine War", "First Triumvirate"],
        "values": ["Virtus", "Frugalitas", "Integritas"]
    }
}

def determine_period(year: int) -> str:
    """
    Determine the historical period based on a year.
    
    Args:
        year: The year (negative for BCE)
        
    Returns:
        String identifying the period
    """
    for period, (start, end) in HISTORICAL_PERIODS.items():
        if start <= year <= end:
            return period
    
    # Default to late republic if out of range
    return "late_republic"

def get_appropriate_historical_figures(year: int, count: int = 3) -> List[Dict]:
    """
    Get historically appropriate figures for references in speeches.
    
    Args:
        year: The year (negative for BCE)
        count: Number of figures to return
        
    Returns:
        List of figure dictionaries
    """
    period = determine_period(year)
    
    # Get figures from this period
    figures = HISTORICAL_FIGURES.get(period, [])
    
    # Filter figures by what would be historically known at this time
    known_figures = []
    for figure in figures:
        figure_end_year = figure.get("years", (0, 0))[1]
        if isinstance(figure_end_year, int) and figure_end_year < year:
            known_figures.append(figure)
    
    # Add some figures from earlier periods
    if period == "middle_republic":
        known_figures.extend(HISTORICAL_FIGURES.get("early_republic", []))
    elif period == "late_republic":
        known_figures.extend(HISTORICAL_FIGURES.get("middle_republic", [])[:3])  # Just some key figures
        known_figures.extend(HISTORICAL_FIGURES.get("early_republic", [])[:2])   # Just the most famous
    
    # If not enough figures, fill with available ones
    if len(known_figures) < count:
        return known_figures
    
    # Select random subset
    return random.sample(known_figures, count)

def get_appropriate_historical_events(year: int, count: int = 3) -> List[Dict]:
    """
    Get historically appropriate events for references in speeches.
    
    Args:
        year: The year (negative for BCE)
        count: Number of events to return
        
    Returns:
        List of event dictionaries
    """
    period = determine_period(year)
    
    # Get events from this period and before
    all_events = []
    
    # Add events from current and previous periods
    if period == "early_republic":
        all_events.extend(HISTORICAL_EVENTS.get("early_republic", []))
    elif period == "middle_republic":
        all_events.extend(HISTORICAL_EVENTS.get("middle_republic", []))
        all_events.extend(HISTORICAL_EVENTS.get("early_republic", []))
    elif period == "late_republic":
        all_events.extend(HISTORICAL_EVENTS.get("late_republic", []))
        all_events.extend(HISTORICAL_EVENTS.get("middle_republic", []))
        all_events.extend(HISTORICAL_EVENTS.get("early_republic", []))
    
    # Filter events by what would be historically known at this time
    known_events = []
    for event in all_events:
        event_year = event.get("year", 0)
        event_years = event.get("years", (0, 0))
        
        # Check if event is before the current year
        if isinstance(event_year, int) and event_year < year:
            known_events.append(event)
        elif isinstance(event_years, tuple) and event_years[1] < year:
            known_events.append(event)
    
    # If not enough events, fill with available ones
    if len(known_events) < count:
        return known_events
    
    # Select random subset
    return random.sample(known_events, count)

def get_appropriate_values(year: int, count: int = 3) -> List[Dict]:
    """
    Get historically appropriate values for references in speeches.
    
    Args:
        year: The year (negative for BCE)
        count: Number of values to return
        
    Returns:
        List of value dictionaries
    """
    period = determine_period(year)
    
    # Get values for this period
    values = ROMAN_VALUES.get(period, [])
    
    # If not enough values, fill with available ones
    if len(values) < count:
        return values
    
    # Select random subset
    return random.sample(values, count)

def get_topic_specific_references(topic: str, year: int) -> Dict:
    """
    Get references specific to a debate topic.
    
    Args:
        topic: The debate topic
        year: The year (negative for BCE)
        
    Returns:
        Dictionary of topic-relevant references
    """
    # Normalize topic by finding the closest match
    normalized_topic = "foreign_policy"  # Default
    
    for topic_key in DEBATE_TOPICS.keys():
        if topic_key in topic.lower():
            normalized_topic = topic_key
            break
    
    # Get topic-specific references
    topic_refs = DEBATE_TOPICS.get(normalized_topic, {})
    
    # Get general references relevant to the period
    figures = get_appropriate_historical_figures(year, 2)
    events = get_appropriate_historical_events(year, 2)
    values = get_appropriate_values(year, 2)
    
    # Try to add topic-specific figures if they're historically appropriate
    topic_figures = []
    if "figures" in topic_refs:
        for figure_name in topic_refs["figures"]:
            for period, figures_list in HISTORICAL_FIGURES.items():
                for figure in figures_list:
                    if figure["name"] == figure_name and figure.get("years", (0, 0))[1] < year:
                        topic_figures.append(figure)
    
    # Combine topic-specific and general references
    combined_refs = {
        "figures": topic_figures + figures,
        "events": events,  # Just use general events
        "values": values   # Just use general values
    }
    
    return combined_refs

def get_historical_context_for_speech(year: int, topic: str) -> Dict:
    """
    Generate complete historical context for a speech.
    
    Args:
        year: The year in Roman history (negative for BCE)
        topic: The topic of debate
        
    Returns:
        Dictionary with all needed historical context
    """
    # Get topic-specific references
    topic_refs = get_topic_specific_references(topic, year)
    
    # Add general context
    context = {
        "year": year,
        "period": determine_period(year),
        "topic": topic,
        "figures": topic_refs.get("figures", []),
        "events": topic_refs.get("events", []),
        "values": topic_refs.get("values", [])
    }
    
    return context