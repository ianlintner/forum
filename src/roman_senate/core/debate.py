#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Roman Senate Game
Debate Module

This module handles the debate mechanics of the Roman Senate simulation.
It manages the flow of arguments, rebuttals, and procedural rules
during senate deliberations.
"""

import random
import asyncio
import time
from typing import Dict, List, Optional, Any
from collections import defaultdict
from rich.panel import Panel
from rich.text import Text
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from ..utils.llm import factory as llm_factory
from ..utils.config import LLM_PROVIDER, LLM_MODEL

console = Console()

# Relationship tracking between senators
# Format: {senator_id: {other_senator_id: relationship_score}}
# Scores range from -1.0 (hostile) to 1.0 (friendly)
senator_relationships = defaultdict(lambda: defaultdict(float))

# Emotion and status effects for senators
# Format: {senator_id: {"emotions": [{"type": str, "intensity": float, "source": str, "duration": int}],
#                      "status_effects": [{"type": str, "source": str, "duration": int}]}}
senator_states = defaultdict(lambda: {"emotions": [], "status_effects": []})

# Debate history to track who said what
debate_history = []


def reset_debate_state():
    """Reset debate state for a new debate session."""
    global debate_history
    debate_history = []

    # Clear temporary emotions and status effects
    for senator_id in senator_states:
        # Filter out expired emotions and status effects
        senator_states[senator_id]["emotions"] = [
            e
            for e in senator_states[senator_id]["emotions"]
            if e.get("duration", 0) > 1
        ]
        senator_states[senator_id]["status_effects"] = [
            s
            for s in senator_states[senator_id]["status_effects"]
            if s.get("duration", 0) > 1
        ]

        # Reduce duration of remaining effects
        for e in senator_states[senator_id]["emotions"]:
            if "duration" in e:
                e["duration"] -= 1

        for s in senator_states[senator_id]["status_effects"]:
            if "duration" in s:
                s["duration"] -= 1


def update_relationship(senator1_id: int, senator2_id: int, change: float):
    """
    Update the relationship between two senators.

    Args:
        senator1_id: ID of first senator
        senator2_id: ID of second senator
        change: Amount to change relationship (-1.0 to 1.0)
        
    Returns:
        float: The new relationship value
    """
    # Get current relationship
    current = senator_relationships[senator1_id][senator2_id]

    # Update with boundaries
    new_value = max(-1.0, min(1.0, current + change))

    # Store in both directions
    senator_relationships[senator1_id][senator2_id] = new_value
    senator_relationships[senator2_id][senator1_id] = new_value

    return new_value


def add_emotion(
    senator_id: int, emotion_type: str, intensity: float, source: str, duration: int = 1
):
    """
    Add an emotion to a senator.

    Args:
        senator_id: ID of the senator
        emotion_type: Type of emotion (e.g., "angry", "pleased")
        intensity: Intensity of emotion (0.0 to 1.0)
        source: Source of the emotion (e.g., senator name)
        duration: How many debate rounds the emotion lasts
        
    Returns:
        Dict: The emotion that was added
    """
    emotion = {
        "type": emotion_type,
        "intensity": max(0.0, min(1.0, intensity)),
        "source": source,
        "duration": duration,
    }

    # Add new emotion, replacing existing one of same type if present
    existing_emotions = [
        e for e in senator_states[senator_id]["emotions"] if e["type"] != emotion_type
    ]
    existing_emotions.append(emotion)
    senator_states[senator_id]["emotions"] = existing_emotions

    return emotion


def add_status_effect(
    senator_id: int, effect_type: str, source: str, duration: int = 1
):
    """
    Add a status effect to a senator.

    Args:
        senator_id: ID of the senator
        effect_type: Type of effect (e.g., "agitated", "supported")
        source: Source of the effect
        duration: How many debate rounds the effect lasts
        
    Returns:
        Dict: The status effect that was added
    """
    effect = {"type": effect_type, "source": source, "duration": duration}

    # Add new effect, replacing existing one of same type if present
    existing_effects = [
        e
        for e in senator_states[senator_id]["status_effects"]
        if e["type"] != effect_type
    ]
    existing_effects.append(effect)
    senator_states[senator_id]["status_effects"] = existing_effects

    return effect


def get_emotions(senator_id: int) -> List[Dict]:
    """Get all active emotions for a senator."""
    return senator_states[senator_id]["emotions"]


def get_status_effects(senator_id: int) -> List[Dict]:
    """Get all active status effects for a senator."""
    return senator_states[senator_id]["status_effects"]


def summarize_speech(speech: Dict) -> Dict:
    """
    Create a summary of a speech for use in debate context.

    Args:
        speech: Full speech data

    Returns:
        Dict: Summarized speech data
    """
    return {
        "senator_id": speech.get("senator_id"),
        "senator_name": speech.get("senator_name"),
        "faction": speech.get("faction"),
        "stance": speech.get("stance"),
        "key_points": speech.get("key_points", []),
        "mentioned_senators": speech.get("mentioned_senators", []),
    }


def add_to_debate_history(speech_data: Dict):
    """
    Add a speech to the debate history.

    Args:
        speech_data: Speech data including senator information
    """
    global debate_history
    debate_history.append(summarize_speech(speech_data))


async def generate_speech(
    senator: Dict,
    topic: str,
    faction_stance: Dict = None,
    year: int = None,
    responding_to: Optional[Dict] = None,
    previous_speeches: Optional[List[Dict]] = None,
) -> Dict:
    """
    Generate an AI-powered speech for a senator based on their identity, the debate topic,
    and the historical context of the specified year.
    
    Args:
        senator (Dict): The senator data including name, faction, and traits
        topic (str): The current debate topic
        faction_stance (Dict, optional): Faction stances on the topic for consistency
        year (int, optional): The year in Roman history (negative for BCE)
        responding_to (Dict, optional): Senator/speech being directly responded to
        previous_speeches (List[Dict], optional): Previous speeches in this debate
        
    Returns:
        Dict: Speech data including the full text, key points, stance, and other metadata
    """
    # Determine the senator's likely stance based on faction and personality
    # Default stances if none provided
    if not faction_stance:
        faction_stance = {
            "Optimates": random.choice(["oppose", "oppose", "neutral"]),
            "Populares": random.choice(["support", "support", "neutral"]),
            "Military": random.choice(["support", "oppose", "neutral"]),
            "Religious": random.choice(["oppose", "neutral", "support"]),
            "Merchant": random.choice(["support", "neutral", "oppose"]),
        }

    stance = faction_stance.get(
        senator["faction"], random.choice(["support", "oppose", "neutral"])
    )

    # Senator personality factors
    traits = senator.get("traits", {})
    eloquence = traits.get("eloquence", 0.5)
    corruption = traits.get("corruption", 0.2)
    loyalty = traits.get("loyalty", 0.7)
    
    # Calculate variable speech characteristics based on senator personality and random rolls
    # Speech length varies based on eloquence and random chance
    random_length_factor = random.uniform(0.7, 1.3)  # Random variation of ±30%
    speech_length_factor = eloquence * random_length_factor
    
    # Determine number of sentences based on speech length factor
    if speech_length_factor < 0.6:  # Brief speakers
        sentences = "2-3"
    elif speech_length_factor < 0.9:  # Average speakers
        sentences = "3-4"
    else:  # Long-winded speakers
        sentences = "5-7"
    
    # Speech quality is influenced by eloquence, corruption, and loyalty
    quality_factor = eloquence * 0.6 - corruption * 0.3 + loyalty * 0.1
    quality_factor = max(0.1, min(1.0, quality_factor))
    
    # Determine argument quality level
    if quality_factor < 0.4:
        argument_quality = "basic and somewhat flawed"
    elif quality_factor < 0.7:
        argument_quality = "sound and reasonable"
    else:
        argument_quality = "sophisticated and compelling"
    
    # Rhetorical flourish level varies based on eloquence and random chance
    random_flourish_factor = random.uniform(0.8, 1.2)  # Random variation of ±20%
    flourish_factor = eloquence * random_flourish_factor
    
    # Determine number of rhetorical flourishes
    if flourish_factor < 0.6:  # Basic speakers
        flourishes = "1"
    elif flourish_factor < 0.9:  # Capable orators
        flourishes = "2-3"
    else:  # Master orators
        flourishes = "3-4"
    
    # Set default year if not provided (middle Republic)
    if year is None:
        year = -200  # Default to 200 BCE
    
    # Convert to display format (positive number for BCE)
    year_display = abs(year)
    
    # Determine period of Roman Republic based on year
    if year <= -400:
        period = "early Republic"
    elif year <= -150:
        period = "middle Republic"
    else:
        period = "late Republic"
    
    # Historical context based on time period
    from .topic_generator import get_historical_period_context
    historical_events = get_historical_period_context(year)
    
    # Check for active emotions and status effects
    active_emotions = get_emotions(senator.get("id", 0))
    active_status = get_status_effects(senator.get("id", 0))
    
    # Create debate context section
    debate_context = ""
    responding_to_info = ""
    previous_speech_info = ""
    
    # If responding to another senator directly
    if responding_to:
        responding_senator = responding_to.get("senator_name", "Unknown Senator")
        responding_faction = responding_to.get("faction", "Unknown Faction")
        responding_stance = responding_to.get("stance", "neutral")
        responding_key_points = responding_to.get("key_points", [])
        
        # Format the key points as a bullet list
        key_points_text = "\n".join(
            [f"  • {point}" for point in responding_key_points if point]
        )
        
        responding_to_info = f"""
    IMPORTANT: You are DIRECTLY RESPONDING to {responding_senator} of the {responding_faction} faction.
    Their stance: They {responding_stance} the proposal.
    Their key points:
    {key_points_text}
    
    Your response should:
    - Acknowledge their arguments by name
    - Address their key points specifically
    - {"Support their position with additional arguments" if stance == responding_stance else "Rebut their points with counterarguments"}
    - Maintain a respectful tone appropriate for the Senate
    """
    
    # If there are previous speeches but not directly responding to anyone
    elif previous_speeches and len(previous_speeches) > 0:
        # Get summaries of recent speeches (up to 3 most recent)
        recent_speeches = (
            previous_speeches[-3:] if len(previous_speeches) > 3 else previous_speeches
        )
        
        summaries = []
        for i, speech in enumerate(recent_speeches):
            speaker = speech.get("senator_name", "Unknown Senator")
            faction = speech.get("faction", "Unknown Faction")
            prev_stance = speech.get("stance", "neutral")
            key_points = speech.get("key_points", [])
            
            stance_text = {
                "support": "supported",
                "oppose": "opposed",
                "neutral": "was undecided about",
            }.get(prev_stance, "discussed")
            
            # Create a brief summary
            point_summary = "; ".join([p for p in key_points if p])[:100] + "..."
            summaries.append(
                f"• {speaker} ({faction}) {stance_text} the proposal, arguing: {point_summary}"
            )
        
        previous_speech_info = f"""
    Previous speakers in this debate:
    {"".join(summaries)}
    
    You may reference previous arguments if relevant to your position.
    """
    
    # Add emotion and status context if applicable
    emotion_context = ""
    if active_emotions:
        emotion_descriptions = []
        for emotion in active_emotions:
            emotion_type = emotion.get("type", "")
            source = emotion.get("source", "")
            intensity = emotion.get("intensity", 0.5)
            
            if emotion_type == "angry":
                emotion_descriptions.append(
                    f"You are {'very ' if intensity > 0.7 else ''}angry at {source}"
                )
            elif emotion_type == "grateful":
                emotion_descriptions.append(
                    f"You feel {'deeply ' if intensity > 0.7 else ''}grateful to {source}"
                )
            elif emotion_type == "insulted":
                emotion_descriptions.append(
                    f"You feel {'gravely ' if intensity > 0.7 else ''}insulted by {source}"
                )
        
        if emotion_descriptions:
            emotion_context = "Current emotional state:\n" + "\n".join(
                emotion_descriptions
            )
    
    # Combine all context elements
    if responding_to_info or previous_speech_info or emotion_context:
        debate_context = f"""
    DEBATE CONTEXT:
    {responding_to_info}
    {previous_speech_info}
    {emotion_context}
    """
    
    # Create a prompt for the AI based on senator details, personality traits, and calculated variables
    prompt = f"""
    You are {senator['name']}, a Roman Senator of the {senator['faction']} faction during the {period} ({year_display} BCE).
    
    Your traits:
    - Eloquence: {eloquence:.1f}/1.0 (how effectively you speak)
    - Corruption: {corruption:.1f}/1.0 (how much personal gain influences you)
    - Loyalty: {loyalty:.1f}/1.0 (how loyal you are to your faction)
    
    Speech characteristics (follow these precisely):
    - Speech length: {sentences} sentences (determined by your eloquence)
    - Argument quality: {argument_quality} (determined by your traits)
    - Rhetorical flourishes: Include {flourishes} rhetorical device(s) (like metaphor, repetition, tricolon, etc.)
    
    Historical context for {year_display} BCE:
    {historical_events}
    {debate_context}
    Write a speech addressing the Senate on this topic:
    "{topic}"
    
    Your stance is to {stance} the proposal.
    
    Provide the speech in TWO languages:
    1. LATIN version: Authentic Classical Latin using appropriate vocabulary and syntax
    2. ENGLISH version: Same speech translated to English
    
    Both versions should:
    - Reference appropriate historical events, figures, or context from {year_display} BCE
    - Use historically accurate Roman terminology and political references for {year_display} BCE
    - Reflect your faction's interests in the context of {year_display} BCE
    - Be in first person
    - Begin with a formal address appropriate to {year_display} BCE
    - End with a clear statement of your position
    - Include at least one reference to the current political or military situation in {year_display} BCE
    - Match the speech length, quality level, and rhetorical flourish count specified above
    
    Format your response exactly like this:
    ---LATIN---
    [Latin version of the speech here]
    ---ENGLISH---
    [English version of the speech here]
    """
    
    # Start time for progress tracking
    start_time = time.time()
    
    try:
        # Get the LLM provider
        llm = llm_factory.get_provider()
        
        # Display progress message
        console.print(f"[cyan]Senator {senator['name']} is formulating an argument...[/]")
        
        # Generate speech using the configured LLM provider
        response_text = await llm.generate_text(prompt)
        
        # Display generation time
        generation_time = time.time() - start_time
        console.print(f"[dim]Speech generated in {generation_time:.1f} seconds[/]")
        
        # Extract Latin and English versions from formatted response
        latin_text = ""
        english_text = ""
        
        # Parse the response to extract Latin and English sections
        if (
            response_text
            and "---LATIN---" in response_text
            and "---ENGLISH---" in response_text
        ):
            sections = response_text.split("---LATIN---")
            if len(sections) > 1:
                latin_english = sections[1].split("---ENGLISH---")
                if len(latin_english) > 1:
                    latin_text = latin_english[0].strip()
                    english_text = latin_english[1].strip()
        
        # Fallback for cases where formatting is incorrect
        if not latin_text or not english_text:
            if "---LATIN---" not in response_text and "---ENGLISH---" not in response_text:
                # No formatting at all - assume everything is English
                english_text = response_text.strip()
                latin_text = "Lorem ipsum dolor sit amet..."  # Placeholder Latin
            elif "---LATIN---" in response_text and "---ENGLISH---" not in response_text:
                # Only Latin marker - split at that
                parts = response_text.split("---LATIN---", 1)
                if len(parts) > 1:
                    latin_text = parts[1].strip()
                    english_text = latin_text  # Use same content for both
            elif "---LATIN---" not in response_text and "---ENGLISH---" in response_text:
                # Only English marker - split at that
                parts = response_text.split("---ENGLISH---", 1)
                if len(parts) > 1:
                    english_text = parts[1].strip()
                    latin_text = "Lorem ipsum dolor sit amet..."  # Placeholder Latin
    
    except Exception as e:
        console.print(f"[bold red]Error generating speech: {e}[/]")
        # Create fallback speech if the LLM request fails
        latin_text = "Lorem ipsum dolor sit amet, consul senatum vocat."
        english_text = f"Senators of Rome, regarding {topic}, I {'support' if stance == 'support' else 'oppose' if stance == 'oppose' else 'need more information about'} this matter based on the interests of Rome."

    # Use fallback speech if still empty
    if not latin_text or not english_text:
        # Generate fallback speech
        stance_phrases = {
            "support": [
                f"Fellow senators, I strongly support this measure on {topic}.",
                f"Rome's glory depends on our approval of this matter.",
            ],
            "oppose": [
                f"I must oppose this proposal regarding {topic}.",
                f"For the good of Rome, we must reject this measure.",
            ],
            "neutral": [
                f"This matter requires careful deliberation before we decide.",
                f"I call for more discussion on the implications of this proposal.",
            ],
        }

        opening = random.choice(
            [
                "Senators of Rome,",
                "Fellow patricians,",
                "Esteemed colleagues,",
                "Noble representatives of our Republic,",
            ]
        )

        faction_interest = {
            "Optimates": "the traditions of our ancestors",
            "Populares": "the welfare of the common people",
            "Military": "the strength of our legions",
            "Religious": "the will of the gods",
            "Merchant": "Rome's commercial interests",
        }

        main_point = random.choice(stance_phrases[stance])

        # Get faction interest or default
        default_interest = "Rome's future"
        interest_phrase = faction_interest.get(senator["faction"], default_interest)
        interest = f"As we consider {interest_phrase}, we must act wisely."

        english_text = (
            f"{opening} {main_point} {interest} {random.choice(stance_phrases[stance])}"
        )

        # Latin fallback version - simple translations of common phrases
        latin_openings = {
            "Senators of Rome,": "Senatores Romani,",
            "Fellow patricians,": "Patricii,",
            "Esteemed colleagues,": "Collegae aestimati,",
            "Noble representatives of our Republic,": "Nobiles rei publicae nostrae legati,",
        }

        latin_stance = {
            "support": [
                f"Hanc causam de {topic} vehementer sustineo.",
                f"Gloria Romae ex approbatione huius rei pendet.",
            ],
            "oppose": [
                f"Hanc propositionem de {topic} repudiare debeo.",
                f"Pro bono Romae, hoc consilium reiciendum est.",
            ],
            "neutral": [
                f"Haec res deliberationem attentam requirit antequam decernamus.",
                f"Ad discussionem ampliorem de implicationibus huius propositionis voco.",
            ],
        }

        latin_interests = {
            "Optimates": "mores maiorum",
            "Populares": "salutem plebis",
            "Military": "virtutem legionum nostrarum",
            "Religious": "voluntatem deorum",
            "Merchant": "commercium Romanum",
        }

        latin_opening = latin_openings.get(opening, "Senatores,")
        latin_main = random.choice(latin_stance[stance])
        latin_interest_phrase = latin_interests.get(senator["faction"], "futurum Romae")
        latin_interest = (
            f"Dum {latin_interest_phrase} consideramus, sapienter agere debemus."
        )
        latin_text = f"{latin_opening} {latin_main} {latin_interest} {random.choice(latin_stance[stance])}"

    # Analyze the speech to find mentioned senators
    mentioned_senators = []
    if responding_to:
        mentioned_senators.append(
            {
                "senator_id": responding_to.get("senator_id"),
                "senator_name": responding_to.get("senator_name"),
                "faction": responding_to.get("faction"),
                "sentiment": (
                    "positive" if stance == responding_to.get("stance") else "negative"
                ),
                "interaction_type": "direct_response",
            }
        )

    # Return the speech data with both language versions, historical context, and speech characteristics
    speech_data = {
        "senator_id": senator.get("id", 0),
        "senator_name": senator["name"],
        "faction": senator["faction"],
        "latin_text": latin_text.strip(),
        "english_text": english_text.strip(),
        "full_text": english_text.strip(),  # For backward compatibility
        "stance": stance,
        "key_points": english_text.split(". ")[:2],  # First two sentences as key points
        "year": year,
        "year_display": f"{year_display} BCE",
        "historical_context": historical_events.strip(),
        # Speech characteristics
        "speech_length": sentences,
        "argument_quality": argument_quality,
        "rhetorical_flourishes": flourishes,
        "quality_factor": quality_factor,
        "eloquence": eloquence,
        "corruption": corruption,
        "loyalty": loyalty,
        # Interaction data
        "responding_to": responding_to.get("senator_name") if responding_to else None,
        "mentioned_senators": mentioned_senators,
        "is_response": responding_to is not None,
    }

    # Store speech in debate history
    add_to_debate_history(speech_data)

    # Update relationships if responding to someone
    if responding_to and "id" in senator and responding_to.get("senator_id"):
        # Agree with the senator being responded to
        if speech_data["stance"] == responding_to.get("stance"):
            update_relationship(
                senator["id"], responding_to["senator_id"], 0.1  # Small positive change
            )
        # Disagree with the senator being responded to
        else:
            update_relationship(
                senator["id"],
                responding_to["senator_id"],
                -0.1,  # Small negative change
            )

    return speech_data


async def conduct_debate(
    topic: str, senators_list: List[Dict], rounds: int = 3, topic_category: str = None,
    year: int = None
):
    """
    Conduct a debate on the given topic with interactive responses between senators.

    Args:
        topic (str): The topic to debate
        senators_list (List[Dict]): List of senators participating
        rounds (int): Number of debate rounds
        topic_category (str, optional): Category of the topic (e.g., Military funding)
        year (int, optional): The year in Roman history
        
    Returns:
        List[Dict]: Summary of the debate including all speeches
    """
    # Reset debate state for a new debate
    reset_debate_state()

    # Handle case where topic might be None
    topic_display = topic if topic else "Unknown Topic"
    
    # Create a more informative debate introduction
    if topic_category:
        introduction = f"The Senate will now debate on a matter of [bold yellow]{topic_category}[/]:\n[italic]{topic_display}[/]"
    else:
        introduction = f"The Senate will now debate:\n[italic]{topic_display}[/]"

    # Display the debate panel with category context
    console.print(
        Panel(
            introduction,
            title="[bold cyan]SENATE DEBATE BEGINS[/]",
            border_style="cyan",
            width=100,
        )
    )

    debate_summary = []

    # Track which senators have already responded to which others to prevent loops
    responded_pairs = set()  # (responder_id, target_id) pairs

    # Generate faction stances for consistency
    faction_stances = {
        "Optimates": random.choice(["oppose", "oppose", "neutral"]),
        "Populares": random.choice(["support", "support", "neutral"]),
        "Military": random.choice(["support", "oppose", "neutral"]),
        "Religious": random.choice(["oppose", "neutral", "support"]),
        "Merchant": random.choice(["support", "neutral", "oppose"]),
    }

    # Keep track of all previous speeches for context
    previous_speeches = []

    for round_num in range(1, rounds + 1):
        console.print(f"\n[bold blue]Round {round_num} of Debate[/]")

        # Select speakers for this round
        speakers = random.sample(senators_list, min(3, len(senators_list)))

        # Create speech generation tasks for all speakers in this round
        speech_tasks = []
        
        # Show which senators are preparing their speeches
        for senator in speakers:
            thought_text = f"[bold]{senator['name']} ({senator['faction']}) is preparing to speak...[/]"
            console.print(thought_text)
            
            # Determine if this senator should respond to a previous speaker
            responding_to = None
            if previous_speeches and (round_num > 1 or len(previous_speeches) >= 2):
                for prev_speech in reversed(previous_speeches):  # Check most recent first
                    prev_senator_id = prev_speech.get("senator_id")
                    current_senator_id = senator.get("id")
                    
                    # Skip if they've already responded to each other
                    if prev_senator_id and current_senator_id:
                        pair = (current_senator_id, prev_senator_id)
                        if pair in responded_pairs:
                            continue
                    
                    # Calculate response probability based on stance agreement/disagreement
                    response_chance = 0.2  # Base chance
                    
                    if prev_speech.get("faction") == senator.get("faction"):
                        response_chance += 0.1  # More likely to respond to same faction
                    
                    # Strongly agree/disagree increases chance to respond
                    if prev_speech.get("stance") == faction_stances.get(senator.get("faction")):
                        response_chance += 0.2  # Same stance, more likely to support
                    elif (prev_speech.get("stance") != faction_stances.get(senator.get("faction"))
                          and prev_speech.get("stance") != "neutral"):
                        response_chance += 0.3  # Opposing stance, more likely to rebut
                    
                    # Check if random chance triggers a response
                    if random.random() < response_chance:
                        responding_to = prev_speech
                        
                        # Record that this senator has responded to prevent loops
                        if prev_senator_id and current_senator_id:
                            responded_pairs.add((current_senator_id, prev_senator_id))
                        break
            
            # Create a task for each senator's speech generation
            speech_tasks.append(generate_speech(
                senator,
                topic,
                faction_stance=faction_stances,
                year=year,
                responding_to=responding_to,
                previous_speeches=previous_speeches
            ))
        
        # Process all speakers in parallel
        speech_results = await asyncio.gather(*speech_tasks)
        
        # Display speeches in order
        for i, speech in enumerate(speech_results):
            senator = speakers[i]
            
            # Display the speech in an immersive format
            display_speech(senator, speech, topic)
            
            # Score the speech
            score = score_argument(speech["english_text"], topic)
            
            # Show the score
            score_table = Table(title="Speech Assessment")
            score_table.add_column("Criterion", style="cyan")
            score_table.add_column("Score", justify="right")
            
            for criterion, value in score.items():
                if criterion != "total":
                    score_table.add_row(
                        criterion.replace("_", " ").title(), f"{value:.2f}"
                    )
            
            score_table.add_row("Overall", f"[bold]{score['total']:.2f}[/]")
            console.print(score_table)
            
            # Add to debate summary and previous speeches
            speech["score"] = score["total"]
            debate_summary.append(speech)
            previous_speeches.append(speech)
            
            # Pause for readability
            time.sleep(1)

    console.print("\n[bold green]✓[/] Debate concluded.\n")
    return debate_summary


def display_speech(senator: Dict, speech: Dict, topic: str = ""):
    """
    Display a senator's speech with Latin and English versions.
    
    Args:
        senator: Senator data
        speech: Speech data including latin_text and english_text
        topic: The debate topic (optional)
    """
    # Get the speech text in both languages
    latin = speech.get("latin_text", "")
    english = speech.get("english_text", "")
    
    # Handle the possibility of missing data
    if not latin and not english:
        console.print(f"[bold red]Error: No speech content for {senator['name']}[/]")
        return
    
    # Create a header with senator information
    header = f"[bold]{senator['name']}[/] ([italic]{senator['faction']}[/]) addresses the Senate:"
    
    latin_panel = Panel(
        f"[italic yellow]{latin}[/]",
        title="Latin",
        border_style="blue"
    )
    
    english_panel = Panel(
        f"[italic white]{english}[/]",
        title="English",
        border_style="blue"
    )
    
    # Get the stance from speech data, with fallback
    stance = speech.get("stance", "neutral")
    
    # Show stance with appropriate color
    stance_tag = {
        "support": "[green]SUPPORTS[/]",
        "oppose": "[red]OPPOSES[/]",
        "neutral": "[yellow]UNDECIDED[/]"
    }.get(stance, "[dim]UNKNOWN[/]")
    
    stance_text = f"{senator['name']} {stance_tag} the proposal."
    
    # Display the full speech
    console.print("\n" + header)
    console.print(latin_panel)
    console.print(english_panel)
    console.print(f"\n[bold]Position:[/] {stance_text}")


def score_argument(argument: str, topic: str) -> Dict[str, float]:
    """
    Score a speech based on various criteria.
    
    Args:
        argument: The speech text
        topic: The debate topic
        
    Returns:
        Dict: Dictionary of scores for different criteria and a total score
    """
    # This is a simple scoring mechanism - in a full implementation, 
    # you might use the LLM to perform a more sophisticated analysis
    
    # Basic metrics
    length_score = min(1.0, len(argument) / 500)  # Reward reasonable length
    
    # Topic relevance (simple keyword matching)
    topic_words = set(topic.lower().split())
    argument_words = set(argument.lower().split())
    topic_overlap = len(topic_words.intersection(argument_words)) / max(1, len(topic_words))
    relevance_score = min(1.0, topic_overlap * 2)  # Weight topic relevance
    
    # Simple structure analysis
    has_introduction = any(phrase in argument.lower() for phrase in 
                          ["senators", "colleagues", "romans", "citizens", "patres", "conscripti"])
    has_conclusion = any(phrase in argument.lower() for phrase in 
                        ["therefore", "thus", "conclude", "support", "oppose", "vote"])
    
    structure_score = (0.6 if has_introduction else 0) + (0.4 if has_conclusion else 0)
    
    # Calculate weighted total
    total_score = (length_score * 0.2 + 
                  relevance_score * 0.5 + 
                  structure_score * 0.3)
    
    return {
        "length": length_score,
        "relevance": relevance_score,
        "structure": structure_score,
        "total": total_score
    }


def get_historical_context(year: int) -> str:
    """
    Get historical context for a specific year in Roman history.
    
    Args:
        year (int): The year (negative for BCE)
        
    Returns:
        str: Historical context description
    """
    # Use the function from topic_generator.py
    from .topic_generator import get_historical_period_context
    return get_historical_period_context(year)