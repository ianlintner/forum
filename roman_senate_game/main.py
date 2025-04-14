#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Roman Senate AI Game
Main application entry point

This module serves as the main entry point for the Roman Senate AI Game.
It orchestrates the simulation of senate debates and voting procedures.
"""

import os
import sys
import time
import random
import asyncio
import typer
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm
from rich.console import Console
from typing import List, Dict, Coroutine, Any

# Project imports
import utils
import senators
import debate
import vote
import topic_generator
import senate_session
import officials
import interjections
import political_maneuvering
from config import OPENAI_API_KEY
from logging_utils import get_logger

def ensure_correct_path():
    """Ensure the script runs from the correct directory."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if os.getcwd() != script_dir:
        os.chdir(script_dir)
        print(f"Changed working directory to: {script_dir}")

    # Add the script directory to Python path
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)
        print(f"Added {script_dir} to Python path")

app = typer.Typer(help="Roman Senate AI Simulation Game")
console = utils.console
logger = get_logger()  # Initialize logger at module level


# Game state management
class GameState:
    def __init__(self):
        self.game_history = []
        self.senators = []
        self.current_topic = None
        self.year = None
        self.voting_results = []
        
    def add_topic_result(self, topic, votes):
        self.game_history.append({
            'topic': topic,
            'votes': votes,
            'year': self.year,
            'year_display': f"{abs(self.year)} BCE" if self.year else "Unknown"
        })
        
    def reset(self):
        """Reset the game state for a new session."""
        self.__init__()

# Global game state
game_state = GameState()

# Topic categories (for reference)
TOPIC_CATEGORIES = topic_generator.TOPIC_CATEGORIES

# Sample senator factions
FACTIONS = ["Optimates", "Populares", "Military", "Religious", "Merchant"]



def initialize_senate(senator_count: int = 10):
    """Initialize the senate with AI senators."""
    console.print("\n[bold cyan]Initializing the Roman Senate...[/]")

    game_state.senators = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[bold green]Creating senator profiles...[/]"),
        console=console,
    ) as progress:
        task = progress.add_task("Working...", total=senator_count)

        for i in range(senator_count):
            senator = {
                "id": i + 1,
                "name": f"Senator {random.choice(['Marcus', 'Gaius', 'Lucius', 'Publius', 'Quintus'])} {random.choice(['Aurelius', 'Julius', 'Claudius', 'Cornelius', 'Flavius'])}",
                "faction": random.choice(FACTIONS),
                "influence": random.randint(1, 10),
                "traits": {
                    "eloquence": random.uniform(0.5, 1.0),
                    "loyalty": random.uniform(0.5, 1.0),
                    "corruption": random.uniform(0.0, 0.5),
                },
            }
            game_state.senators.append(senator)
            progress.update(task, advance=1)
            time.sleep(0.2)  # Simulated delay for effect

    console.print(
        "[bold green]✓[/] Senate initialized with [bold cyan]{}[/] senators.\n".format(
            len(game_state.senators)
        )
    )
    return game_state.senators

def select_debate_topic() -> tuple:
    """
    Select a debate topic based on the current year, either randomly or user-selected.
    Uses GPT to generate historically accurate topics for the selected year.
    
    Returns:
        tuple: (topic_text, topic_category) - The selected topic and its category
    """
    console.print("\n[bold yellow]Debate Topic Selection[/]")
    
    # Initialize topic with a default value
    selected_topic = None
    
    # Get topics for the current year
    if game_state.year is None:
        console.print("[bold red]Error:[/] Year not set. Defaulting to 100 BCE.")
        year = -100  # Default to 100 BCE if year not set
    else:
        year = game_state.year
    
    # Get the absolute year for display
    display_year = abs(year)
    console.print(f"[dim]Generating topics relevant to {display_year} BCE...[/]")
    
    try:
        # Get topics by category using the topic generator
        topics_by_category = topic_generator.get_topics_for_year(year)
        
        # Flatten the topics to a list with category information
        available_topics = topic_generator.flatten_topics_by_category(topics_by_category)
        
        if not available_topics:
            raise ValueError("No topics available")
            
        # Display topics by category
        console.print("\n[bold cyan]Available Debate Topics By Category:[/]")
        
        # First display a summary of categories
        category_table = Table(title=f"Topic Categories for {display_year} BCE")
        category_table.add_column("Category", style="yellow")
        category_table.add_column("Count", justify="right")
        
        # Count topics per category
        category_counts = {}
        for topic in available_topics:
            category = topic['category']
            if category not in category_counts:
                category_counts[category] = 0
            category_counts[category] += 1
        
        # Add rows to the table
        for category, count in category_counts.items():
            category_table.add_row(category, str(count))
            
        console.print(category_table)
        
        # Then display all topics with numbers for selection
        table = Table(title=f"All Available Topics ({display_year} BCE)")
        table.add_column("#", style="dim", width=4)
        table.add_column("Topic", style="cyan")
        table.add_column("Category", style="yellow")
        
        for i, topic in enumerate(available_topics):
            table.add_row(
                str(i + 1),
                topic['text'],
                topic['category']
            )
        
        console.print(table)
        
        # Let user choose or select random with Rich
        choice = Prompt.ask(
            "Select a topic number or press [R] for random selection", default="R"
        )
        
        selected_topic_category = None
        
        if choice.upper() == "R":
            selected_topic_obj = random.choice(available_topics)
            selected_topic = selected_topic_obj['text']
            selected_topic_category = selected_topic_obj['category']
            console.print(f"[bold green]Randomly selected:[/] {selected_topic} [dim]({selected_topic_category})[/]\n")
        else:
            try:
                index = int(choice) - 1
                if 0 <= index < len(available_topics):
                    selected_topic_obj = available_topics[index]
                    selected_topic = selected_topic_obj['text']
                    selected_topic_category = selected_topic_obj['category']
                    console.print(f"[bold green]Selected:[/] {selected_topic} [dim]({selected_topic_category})[/]\n")
                else:
                    selected_topic_obj = random.choice(available_topics)
                    selected_topic = selected_topic_obj['text']
                    selected_topic_category = selected_topic_obj['category']
                    console.print(
                        f"[bold yellow]Invalid selection. Randomly selected:[/] {selected_topic} [dim]({selected_topic_category})[/]\n"
                    )
            except ValueError:
                selected_topic_obj = random.choice(available_topics)
                selected_topic = selected_topic_obj['text']
                selected_topic_category = selected_topic_obj['category']
                console.print(
                    f"[bold yellow]Invalid input. Randomly selected:[/] {selected_topic} [dim]({selected_topic_category})[/]\n"
                )
    
    except Exception as e:
        # Fallback to a basic list if the topic generator fails
        console.print(f"[bold red]Error generating topics: {e}[/]")
        console.print("[dim]Falling back to basic topics...[/]")
        
        # Get fallback topics
        fallback_topics = topic_generator.get_fallback_topics()
        available_topics = topic_generator.flatten_topics_by_category(fallback_topics)
        
        # Select a random fallback topic
        selected_topic_obj = random.choice(available_topics)
        selected_topic = selected_topic_obj['text']
        selected_topic_category = selected_topic_obj['category']
        
        console.print(f"[bold yellow]Using fallback topic:[/] {selected_topic} [dim]({selected_topic_category})[/]\n")
    
    # Store the selected topic in game state
    game_state.current_topic = selected_topic
    return selected_topic, selected_topic_category

def select_senate_year():
    """
    Select a year for the Roman Senate session.
    
    The Roman Republic period spanned from 509 BCE to 27 BCE,
    when it transitioned to the Roman Empire under Augustus.
    
    Returns:
        int: The selected year (negative for BCE)
    """
    console.print("\n[bold yellow]Senate Year Selection[/]")
    
    # Range of years for the Roman Republic
    min_year = -509  # 509 BCE
    max_year = -27   # 27 BCE
    
    console.print(Panel(
        f"The Roman Republic existed from [bold]509 BCE[/] to [bold]27 BCE[/].\n"
        f"Choose a year for your Senate session.",
        title="Historical Period",
        border_style="blue"
    ))
    
    # Expanded notable years with rich historical context
    notable_years = {
        -509: {"event": "Founding of the Republic",
               "context": "The monarchy has just been overthrown. The patrician class holds most power. The Senate consists primarily of patrician landowners who advise the newly established consuls."},
        -451: {"event": "Law of the Twelve Tables",
               "context": "First formal Roman legal code created to address the conflict between patricians and plebeians. Plebeians are gaining more political representation but still face significant restrictions."},
        -390: {"event": "Gallic invasion of Rome",
               "context": "Rome has just been sacked by Gallic tribes led by Brennus. The city is rebuilding and strengthening its defenses. Military reforms are being considered to prevent future invasions."},
        -287: {"event": "Lex Hortensia passed",
               "context": "A significant political reform giving plebiscites the full force of law, benefiting the plebeian class. Rome is now the dominant power in central Italy."},
        -264: {"event": "First Punic War begins",
               "context": "Rome and Carthage come into conflict over control of Sicily. This marks Rome's first major overseas military campaign and the beginning of Roman expansion beyond Italy."},
        -218: {"event": "Second Punic War begins",
               "context": "Hannibal crosses the Alps and invades Italy, threatening Rome's existence. This conflict will determine Mediterranean dominance for generations to come."},
        -146: {"event": "Destruction of Carthage",
               "context": "Rome utterly destroys its long-time rival, becoming the undisputed Mediterranean power. Greek cultural influence is strong, and enormous wealth is flowing into Rome from conquered provinces."},
        -133: {"event": "Tiberius Gracchus' reforms",
               "context": "Land reform attempts by Tribune Tiberius Gracchus mark the beginning of the Republic's crisis period. Social inequality and the consequences of imperial expansion are causing political tensions."},
        -107: {"event": "Marius' military reforms",
               "context": "Consul Marius reforms the army to include landless citizens, professionalizing the military but creating soldiers loyal to their generals rather than the Republic."},
        -91: {"event": "Social War begins",
               "context": "Rome's Italian allies revolt demanding citizenship rights. This internal conflict highlights structural problems in how Rome manages its growing influence."},
        -60: {"event": "First Triumvirate formed",
               "context": "Pompey, Caesar, and Crassus form an unofficial political alliance dominating Roman politics. Constitutional norms are being undermined by powerful individuals."},
        -49: {"event": "Caesar crosses the Rubicon",
               "context": "Caesar leads his army into Italy, beginning civil war with Pompey. The traditional republican system is breaking down due to factional violence and personal ambition."},
        -44: {"event": "Assassination of Julius Caesar",
               "context": "Caesar is killed by senatorial conspirators after being made dictator perpetuo. The Republic is in crisis with multiple factions vying for power."},
        -31: {"event": "Battle of Actium",
               "context": "Octavian defeats Antony and Cleopatra in the decisive naval battle of the final civil war. The republican system has effectively collapsed."},
        -27: {"event": "Establishment of the Principate",
               "context": "Octavian becomes Augustus, transforming Rome into an empire while maintaining the facade of republican institutions. The Senate continues to function but with diminished authority."}
    }
    
    # Create a table with more detailed information
    table = Table(title="Notable Years in Roman History")
    table.add_column("Year", style="cyan", width=10)
    table.add_column("Event", style="yellow", width=30)
    table.add_column("Historical Context", style="green")
    
    for year, data in notable_years.items():
        year_str = f"{abs(year)} BCE"
        table.add_row(year_str, data["event"], data["context"])
    
    console.print(table)
    
    # Display options for year selection
    console.print("\n[cyan]Options:[/]")
    console.print("1. Enter a custom year")
    console.print("2. Select from notable years")
    console.print("3. Use default year (100 BCE)")
    
    option = Prompt.ask("Select an option", choices=["1", "2", "3"], default="1")
    
    if option == "2":
        # Allow selection from notable years
        notable_year_list = sorted([(abs(year), year, data) for year, data in notable_years.items()], key=lambda x: x[0])
        
        choices = [str(i) for i in range(1, len(notable_year_list) + 1)]
        console.print("\n[bold cyan]Select a notable year:[/]")
        
        for i, (year_bce, year, data) in enumerate(notable_year_list, 1):
            console.print(f"[cyan]{i}.[/] [yellow]{year_bce} BCE[/] - {data['event']}")
        
        year_choice = Prompt.ask("Enter your choice", choices=choices)
        year_index = int(year_choice) - 1
        selected_year = notable_year_list[year_index][1]  # Get the actual year value
        
        # Display context for selected year
        year_bce = abs(selected_year)
        event = notable_years[selected_year]['event']
        
        # Get enhanced context from topic_generator
        from topic_generator import get_historical_period_context
        detailed_context = get_historical_period_context(selected_year)
        
        console.print(Panel(
            f"[bold yellow]{year_bce} BCE[/] - {event}\n\n"
            f"[green]{detailed_context}[/]",
            title="Detailed Historical Context",
            border_style="cyan"
        ))
        
        # Confirm selection
        confirm = Prompt.ask("Confirm this year selection?", choices=["y", "n"], default="y")
        if confirm.lower() == "y":
            console.print(f"[bold green]Selected:[/] {year_bce} BCE\n")
            game_state.year = selected_year
            return selected_year
        else:
            # Start over if not confirmed
            return select_senate_year()
    
    elif option == "3":
        # Default to 100 BCE
        year = -100
        from topic_generator import get_historical_period_context
        detailed_context = get_historical_period_context(year)
        
        console.print(Panel(
            f"[bold yellow]100 BCE[/] (Default)\n\n"
            f"[green]{detailed_context}[/]",
            title="Detailed Historical Context",
            border_style="cyan"
        ))
        
        console.print(f"[bold green]Selected:[/] 100 BCE\n")
        game_state.year = year
        return year
    
    else:
        # Custom year entry (original behavior)
        while True:
            choice = Prompt.ask(
                "Enter a year (509-27 BCE)",
                default="100"
            )
            
            try:
                # Convert input to negative integer (BCE)
                year_input = int(choice)
                if year_input > 0:
                    year = -year_input  # Convert to BCE format (negative)
                else:
                    year = year_input
                    
                # Validate range
                if min_year <= year <= max_year:
                    display_year = abs(year)
                    
                    # Get enhanced context from topic_generator
                    from topic_generator import get_historical_period_context
                    detailed_context = get_historical_period_context(year)
                    
                    console.print(Panel(
                        f"[green]{detailed_context}[/]",
                        title=f"Historical Context for {display_year} BCE",
                        border_style="cyan"
                    ))
                    
                    # Confirm selection
                    confirm = Prompt.ask("Confirm this year selection?", choices=["y", "n"], default="y")
                    if confirm.lower() == "y":
                        console.print(f"[bold green]Selected:[/] {display_year} BCE\n")
                        game_state.year = year
                        return year
                else:
                    console.print(f"[bold red]Error:[/] Please enter a year between 509 and 27 BCE.\n")
            except ValueError:
                console.print(f"[bold red]Error:[/] Please enter a valid number.\n")


async def conduct_debate(topic: str, senators_list: List[Dict], rounds: int = 3, topic_category: str = None):
    """
    Conduct a debate on the given topic with interactive responses between senators.
    Uses async/await to parallelize speech generation for better performance.
    
    Args:
        topic (str): The topic to debate
        senators_list (List[Dict]): List of senators participating
        rounds (int): Number of debate rounds
        topic_category (str, optional): Category of the topic (e.g., Military funding)
    """
    # Reset debate state for a new debate
    debate.reset_debate_state()
    
    # Handle case where topic might be None
    topic_display = topic if topic else "Unknown Topic"
    
    # Create a more informative debate introduction
    if topic_category:
        introduction = f"The Senate will now debate on a matter of [bold yellow]{topic_category}[/]:\n[italic]{topic_display}[/]"
    else:
        introduction = f"The Senate will now debate:\n[italic]{topic_display}[/]"
    
    # Display the debate panel with category context
    console.print(Panel(introduction, title="[bold cyan]SENATE DEBATE BEGINS[/]", border_style="cyan", width=100))

    debate_summary = []
    
    # Track which senators have already responded to which others to prevent loops
    responded_pairs = set()  # (responder_id, target_id) pairs
    
    # Generate faction stances for consistency
    faction_stances = {
        "Optimates": random.choice(["oppose", "oppose", "neutral"]),
        "Populares": random.choice(["support", "support", "neutral"]),
        "Military": random.choice(["support", "oppose", "neutral"]),
        "Religious": random.choice(["oppose", "neutral", "support"]),
        "Merchant": random.choice(["support", "neutral", "oppose"])
    }

    # Keep track of all previous speeches for context
    previous_speeches = []
    
    for round_num in range(1, rounds + 1):
        console.print(f"\n[bold blue]Round {round_num} of Debate[/]")

        # Select speakers for this round
        speakers = random.sample(senators_list, min(3, len(senators_list)))

        # Create speech generation tasks for all speakers in this round
        async def generate_senator_speech(senator, responding_to=None):
            """
            Helper function to generate a speech for a senator, handling response logic.
            Returns the speech and the responding_to information.
            """
            # Determine if this senator should respond to a previous speaker
            if not responding_to and previous_speeches and (round_num > 1 or len(previous_speeches) >= 2):
                # Check for each previous speech if this senator might respond
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
                        # More likely to respond to same faction
                        response_chance += 0.1
                    
                    # Strongly agree/disagree increases chance to respond
                    if prev_speech.get("stance") == senator.get("faction"):
                        # Same stance, more likely to support
                        response_chance += 0.2
                    elif prev_speech.get("stance") != senator.get("faction") and prev_speech.get("stance") != "neutral":
                        # Opposing stance, more likely to rebut
                        response_chance += 0.3
                    
                    # Check if random chance triggers a response
                    if random.random() < response_chance:
                        responding_to = prev_speech
                        
                        # Record that this senator has responded to prevent loops
                        if prev_senator_id and current_senator_id:
                            responded_pairs.add((current_senator_id, prev_senator_id))
                        
                        # Break out of the loop, we found someone to respond to
                        break

            # Generate senator's AI speech with historical context from the game year
            speech = debate.generate_speech(
                senator,
                topic,
                faction_stances,
                game_state.year,
                responding_to=responding_to,
                previous_speeches=previous_speeches
            )
            
            return speech, responding_to

        # Create tasks for parallel speech generation
        speech_tasks = []
        
        # Show which senators are preparing their speeches
        for senator in speakers:
            thought_text = f"[bold]{senator['name']} ({senator['faction']}) is preparing to speak...[/]"
            console.print(thought_text)
            
            # Create a task for each senator's speech generation
            speech_tasks.append(generate_senator_speech(senator))
        
        # Process all speakers in parallel
        speech_results = await asyncio.gather(*speech_tasks)
        
        # Display speeches in order
        for i, (speech, responding_to) in enumerate(speech_results):
            senator = speakers[i]
            
            # Display the speech in an immersive format with position summary
            debate.display_speech(senator, speech, topic)
            
            # Extract argument from speech for scoring
            argument = speech["full_text"]

            # Score the speech
            score = utils.score_argument(argument, topic)

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

            # Check for emotional reactions based on mentions
            mentions = speech.get("mentioned_senators", [])
            for mention in mentions:
                mentioned_id = mention.get("senator_id")
                sentiment = mention.get("sentiment", "neutral")
                interaction_type = mention.get("interaction_type", "mention")
                
                # Find the mentioned senator in the list
                for other_senator in senators_list:
                    if other_senator.get("id") == mentioned_id:
                        # Add emotional reactions based on sentiment
                        if sentiment == "negative":
                            # Negative mention creates anger or insult
                            if interaction_type == "direct_response" or interaction_type == "criticism":
                                debate.add_emotion(
                                    mentioned_id,
                                    "angry",
                                    0.7,  # Medium-high intensity
                                    senator["name"],
                                    duration=1  # Lasts one round
                                )
                                # Inform the user
                                console.print(f"[bold red]{other_senator['name']} becomes angry at {senator['name']}![/]")
                                
                                # Update relationship negatively
                                debate.update_relationship(mentioned_id, senator.get("id", 0), -0.2)
                        
                        elif sentiment == "positive":
                            # Positive mention creates gratitude
                            debate.add_emotion(
                                mentioned_id,
                                "grateful",
                                0.6,  # Medium intensity
                                senator["name"],
                                duration=1
                            )
                            # Inform the user
                            console.print(f"[bold green]{other_senator['name']} appreciates {senator['name']}'s support.[/]")
                            
                            # Update relationship positively
                            debate.update_relationship(mentioned_id, senator.get("id", 0), 0.15)
            
            # Create enriched speech summary
            speech_summary = {
                "round": round_num,
                "senator_id": senator.get("id", 0),
                "senator_name": senator["name"],
                "faction": senator["faction"],
                "speech": speech["full_text"],
                "latin_speech": speech["latin_text"],
                "english_speech": speech["english_text"],
                "stance": speech["stance"],
                "score": score["total"],
                "is_response": speech.get("is_response", False),
                "responding_to": speech.get("responding_to"),
                "mentioned_senators": speech.get("mentioned_senators", [])
            }
            
            # Add to both the overall debate summary and the running list of speeches
            debate_summary.append(speech_summary)
            previous_speeches.append(speech_summary)

            # Pause for readability
            time.sleep(1)

    console.print("\n[bold green]✓[/] Debate concluded.\n")
    return debate_summary


async def conduct_vote(topic: str, senators_list: List[Dict], debate_summary=None, topic_category: str = None):
    """
    Conduct an asynchronous vote on the given topic after debate.
    
    Args:
        topic (str): The topic to vote on
        senators_list (List[Dict]): List of senators participating
        debate_summary: Summary of the debate results
        topic_category (str, optional): Category of the topic (e.g., Military funding)
    """
    # Handle case where topic might be None
    topic_display = topic if topic else "Unknown Topic"
    
    # Create a more informative vote introduction
    if topic_category:
        introduction = f"The Senate will now vote on a matter of [bold yellow]{topic_category}[/]:\n[italic]{topic_display}[/]"
    else:
        introduction = f"The Senate will now vote on:\n[italic]{topic_display}[/]"
    
    # Display the vote panel with category context
    console.print(Panel(introduction, title="[bold magenta]SENATE VOTE BEGINS[/]", border_style="magenta", width=100))

    votes = {"for": 0, "against": 0, "abstain": 0}
    voting_record = []
    
    # Create a map of senator names to their debate stance
    debate_stances = {}
    if debate_summary:
        # Group by senator name and take the last stance (most recent)
        senator_speeches = {}
        logger = get_logger()
        
        for speech in debate_summary:
            try:
                senator_name = speech.get("senator_name")
                if senator_name:
                    senator_speeches[senator_name] = speech
                    logger.log_response(f"Processed speech for {senator_name}")
                else:
                    logger.log_error(f"Missing senator_name in speech: {speech}")
            except Exception as e:
                logger.log_error(f"Error processing speech: {e}")
                continue
        
        for senator_name, speech in senator_speeches.items():
            try:
                debate_stances[senator_name] = speech.get("stance", "neutral")
                logger.log_response(f"Recorded stance for {senator_name}: {debate_stances[senator_name]}")
            except Exception as e:
                logger.log_error(f"Error recording stance for {senator_name}: {e}")
                debate_stances[senator_name] = "neutral"  # Fallback to neutral
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold]Senators are casting their votes...[/]"),
        console=console,
    ) as progress:
        task = progress.add_task("Voting...", total=len(senators_list))

        # Create tasks for parallel vote processing
        vote_tasks = []
        for senator in senators_list:
            # Pass the senator's debate stance if available
            stance = debate_stances.get(senator["name"], None)
            # Create coroutine for each senator's vote
            vote_tasks.append(asyncio.create_task(process_senator_vote_async(senator, votes, voting_record, stance)))
            progress.update(task, advance=1)
            await asyncio.sleep(0.1)  # Small delay for visual effect

        # Wait for all votes to be processed
        await asyncio.gather(*vote_tasks)

    # Display voting results summary
    console.print("\n[bold yellow]Voting Results Summary:[/]")

    results_table = Table()
    results_table.add_column("Option", style="cyan")
    results_table.add_column("Votes", justify="right")
    results_table.add_column("Percentage", justify="right")

    total_votes = sum(votes.values())

    for option, count in votes.items():
        percentage = (count / total_votes) * 100 if total_votes > 0 else 0
        results_table.add_row(option.title(), str(count), f"{percentage:.1f}%")

    console.print(results_table)

    # Display detailed voting breakdown
    console.print("\n[bold yellow]Detailed Voting Breakdown:[/]")
    
    detailed_table = Table(title=f"Vote on: {topic}")
    detailed_table.add_column("Senator", style="cyan")
    detailed_table.add_column("Faction", style="magenta")
    detailed_table.add_column("Debate Stance", justify="center")
    detailed_table.add_column("Final Vote", justify="center")
    detailed_table.add_column("Swayed", justify="center")
    
    # Map stances to votes for comparison
    stance_to_vote = {
        "support": "for",
        "oppose": "against",
        "neutral": None  # Neutral could be any vote
    }
    
    # Sort voting record by faction then senator name
    sorted_record = sorted(voting_record, key=lambda x: (x["faction"], x["senator"]))
    
    for record in sorted_record:
        senator_name = record["senator"]
        stance = debate_stances.get(senator_name, "unknown")
        vote = record["vote"]
        
        # Determine if senator was swayed
        expected_vote = stance_to_vote.get(stance, None)
        swayed = ""
        
        if expected_vote and vote != expected_vote:
            swayed = "[bold yellow]*[/]"
        elif stance == "neutral" and vote != "abstain":
            swayed = "[bold blue]†[/]"
            
        # Format the stance and vote with colors
        stance_format = {
            "support": "[green]Support[/]",
            "oppose": "[red]Oppose[/]",
            "neutral": "[yellow]Neutral[/]",
            "unknown": "[dim]Unknown[/]"
        }
        
        vote_format = {
            "for": "[green]For[/]",
            "against": "[red]Against[/]",
            "abstain": "[yellow]Abstain[/]"
        }
        
        detailed_table.add_row(
            record["senator"],
            record["faction"],
            stance_format.get(stance, f"[dim]{stance}[/]"),
            vote_format.get(vote, f"[dim]{vote}[/]"),
            swayed
        )
    
    console.print(detailed_table)
    console.print("[bold yellow]*[/] Senator voted differently than their debate stance")
    console.print("[bold blue]†[/] Senator with neutral stance made a definitive vote")

    # Determine outcome
    if votes["for"] > votes["against"]:
        outcome = "PASSED"
        style = "bold green"
    elif votes["for"] < votes["against"]:
        outcome = "REJECTED"
        style = "bold red"
    else:
        outcome = "TIE - CONSUL DECIDES"
        style = "bold yellow"
        outcome = random.choice(["PASSED", "REJECTED"])
        style = "bold green" if outcome == "PASSED" else "bold red"

    console.print(f"\nThe motion has been [bold {style}]{outcome}[/].\n")

    # Record result in game state
    result = {
        "topic": topic,
        "votes": votes,
        "outcome": outcome,
        "voting_record": voting_record,
        "debate_stances": debate_stances
    }
    game_state.voting_results.append(result)

    return result
async def process_senator_vote_async(senator, votes, voting_record, debate_stance=None):
    """
    Asynchronous helper function to process a senator's vote.
    
    Args:
        senator: Senator information
        votes: Counter to update with vote
        voting_record: List to append vote details
        debate_stance: Optional stance from debate ("support", "oppose", "neutral")
    """
    vote_options = ["for", "against", "abstain"]
    weights = [0.5, 0.4, 0.1]  # Default weights
    
    # Modify weights based on faction
    if senator["faction"] == "Optimates":
        weights = [0.4, 0.5, 0.1]  # More conservative
    elif senator["faction"] == "Populares":
        weights = [0.6, 0.3, 0.1]  # More progressive
    
    # Factor in debate stance if available
    if debate_stance:
        # Strongly influence vote by debate stance (80% correlation)
        if debate_stance == "support":
            weights = [0.8, 0.15, 0.05]  # Heavily favor "for" vote
        elif debate_stance == "oppose":
            weights = [0.15, 0.8, 0.05]  # Heavily favor "against" vote
        elif debate_stance == "neutral":
            weights = [0.45, 0.45, 0.1]  # More balanced between for/against
            
        # Modify a bit based on faction and loyalty
        loyalty = senator["traits"]["loyalty"]
        if debate_stance == "support" and senator["faction"] == "Optimates":
            # Optimates slightly more likely to deviate from support
            weights[0] -= (1 - loyalty) * 0.2
            weights[1] += (1 - loyalty) * 0.2
        elif debate_stance == "oppose" and senator["faction"] == "Populares":
            # Populares slightly more likely to deviate from opposition
            weights[0] += (1 - loyalty) * 0.2
            weights[1] -= (1 - loyalty) * 0.2
    
    # Simulate vote deliberation time
    await asyncio.sleep(random.uniform(0.1, 0.3))
    
    vote = random.choices(vote_options, weights=weights)[0]
    votes[vote] += 1
    
    voting_record.append(
        {
            "senator": senator["name"],
            "faction": senator["faction"],
            "vote": vote,
            "influence": senator["influence"],
            "debate_stance": debate_stance
        }
    )
    
    return vote


def display_session_summary(game_history):
    """Display a summary of the entire senate session."""
    console = Console()
    
    table = Table(title="Session Summary", show_header=True)
    table.add_column("Topic", style="cyan")
    table.add_column("For", justify="right")
    table.add_column("Against", justify="right")
    table.add_column("Abstain", justify="right")
    table.add_column("Result", style="green")
    
    for topic_data in game_history:
        votes = topic_data.get('vote_result', {}).get('votes', {})
        table.add_row(
            topic_data.get('topic', ''),
            str(votes.get('for', 0)),
            str(votes.get('against', 0)),
            str(votes.get('abstain', 0)),
            'PASSED' if votes.get('for', 0) > votes.get('against', 0) else 'FAILED'
        )
    
    console.print("\n")
    console.print(Panel("SENATE SESSION CONCLUDED", style="bold cyan"))
    console.print(table)
    console.print("\nGame session complete! Type 'senate play' to start a new session.\n")

def display_senators_info(senators_list: List[Dict]):
    """Display information about all senators."""
    console.print("\n[bold cyan]Roman Senate Membership[/]")

    # Group senators by faction
    factions = {}
    for senator in senators_list:
        faction = senator["faction"]
        if faction not in factions:
            factions[faction] = []
        factions[faction].append(senator)

    # Display senators by faction
    for faction, members in factions.items():
        console.print(f"\n[bold]{faction} Faction[/] ({len(members)} members)")

        table = Table(show_header=True)
        table.add_column("Name", style="cyan")
        table.add_column("Influence", justify="center")
        table.add_column("Traits")

        for senator in members:
            traits_str = ", ".join(
                [f"{k}: {v:.1f}" for k, v in senator["traits"].items()]
            )
            table.add_row(senator["name"], str(senator["influence"]), traits_str)

        console.print(table)


def display_game_rules():
    """Display the rules and background of the game."""
    rules_text = """
    [bold underline]ROMAN SENATE AI GAME[/]
    
    [bold]Background:[/]
    You are participating in a simulation of the Roman Senate during the late Republic era.
    AI senators with unique personalities, backgrounds, and political alignments debate and
    vote on important matters facing Rome.
    
    [bold]Game Flow:[/]
    1. Select a year for your Senate session (509 BCE to 27 BCE)
    2. Initialize the Senate with AI senators from different factions
    3. Select a debate topic for the Senate to consider
    4. Conduct debates where senators present arguments
    5. Hold a vote on the proposed motion
    6. See the results and their implications
    7. Continue with new topics or end the session
    
    [bold]Senate Factions:[/]
    • [cyan]Optimates[/]: Conservative aristocrats who seek to preserve traditional power structures
    • [cyan]Populares[/]: Reform-minded politicians who appeal to common citizens
    • [cyan]Military[/]: Generals and veterans focused on military matters and expansion
    • [cyan]Religious[/]: Priests and religious conservatives concerned with tradition and piety
    • [cyan]Merchant[/]: Business interests focused on trade and economic policy
    
    [bold]Debate System:[/]
    Senators take turns presenting arguments. Each argument is scored based on:
    • Persuasiveness
    • Historical accuracy
    • Logical coherence
    • Eloquence
    
    [bold]Voting System:[/]
    After debate, senators vote based on their faction, personal traits, and the arguments made.
    Senators have varying levels of influence that can sway others.
    """

    utils.format_text(rules_text, as_panel=True, title="Game Rules and Information")


# CLI Commands
@app.command()
def play(senators=10, debate_rounds=3, topics=3):
    """Start a new game session of the Roman Senate simulation."""
    try:
        # Run the async play function with asyncio.run
        # Convert parameters to integers
        senators_int = int(senators)
        debate_rounds_int = int(debate_rounds)
        topics_int = int(topics)
        
        import asyncio
        asyncio.run(play_async(senators_int, debate_rounds_int, topics_int))
    except Exception as e:
        # Use console.print for error logging instead of logger.error
        console = Console()
        console.print(f"\n[bold red]Fatal game error:[/bold red] {str(e)}")
        
        # Add detailed traceback for debugging
        import traceback
        console.print("\n[bold yellow]Detailed Error Information:[/bold yellow]")
        console.print(traceback.format_exc())
        console.print(f"\n[bold cyan]Error Type:[/bold cyan] {type(e).__name__}")
        console.print(f"[bold cyan]Error Location:[/bold cyan] Look for 'File' and line number in traceback above")
        
        console.print("\nGame session terminated. Type 'senate play' to try again.\n")

async def play_async(senators: int = 10, debate_rounds: int = 3, topics: int = 3):
    """Async version of the main game loop."""
    # Clear game state for new session
    game_state.reset()

    # Display welcome banner with historical feature highlight
    console.print(
        Panel(
            "[bold yellow]ROMAN SENATE AI GAME[/]\n"
            "Step into the sandals of a Consul presiding over the Senate of Rome\n\n"
            "[bold cyan]NEW FEATURE: Historical Accuracy[/]\n"
            "Experience a complete Roman Senate with opening ceremonies, officials,\n"
            "political maneuvering, interjections, and historically accurate procedures",
            title="SALVETE SENATORES!",
            border_style="yellow",
            width=100
        )
    )
    
    # Select the year for the senate session
    year = select_senate_year()
    display_year = abs(year)
    
    # Get historical context for the selected year
    historical_context = debate.get_historical_context(year)
    
    # Display senate year banner with historical context
    console.print(
        Panel(
            f"[bold cyan]The Senate of Rome, [bold yellow]{display_year} BCE[/][/]\n"
            f"The Republic stands strong in its {'early' if year <= -300 else 'middle' if year <= -100 else 'late'} period\n\n"
            f"[bold yellow]Historical Context:[/]\n{historical_context}",
            title="SENATUS POPULUSQUE ROMANUS",
            border_style="blue",
            width=100
        )
    )
    
    # Add a brief pause to let users read the historical context
    console.print("\n[dim]Press Enter to continue...[/]")
    input()

    # Initialize senate with AI senators
    senate_members = initialize_senate(senators)
    # Create presiding officials
    presiding_officials = officials.PresidingOfficials(year, senate_members, game_state)

    # Create political maneuvering system
    politics = political_maneuvering.PoliticalManeuvering(senate_members, year, game_state)
    
    # Create a Senate Session object
    senate_session_obj = senate_session.SenateSession(senate_members, year, game_state)
    
    # Prepare topics list
    topics_list = []
    for topic_num in range(1, topics + 1):
        # Select debate topic
        topic, topic_category = select_debate_topic()
        topics_list.append((topic, topic_category))
    
    # Run the full senate session with all topics
    results = await senate_session_obj.run_full_session(topics_list, debate_rounds)
    
    # Record to game history
    for i, result in enumerate(results):
        game_state.game_history.append({
            "year": game_state.year,
            "year_display": f"{abs(game_state.year)} BCE",
            "topic_number": i + 1,
            "topic": result["topic"],
            "topic_category": result["category"],
            "debate_summary": result["debate_summary"],
            "vote_result": result["vote_result"],
        })

    # End of game summary
    console.print(Panel("[bold cyan]SENATE SESSION CONCLUDED[/]", border_style="cyan"))

    # Display summary of all votes
    console.print("\n[bold]Session Summary:[/]")

    summary_table = Table(title="Senate Session Summary")
    summary_table.add_column("Year", style="yellow")
    summary_table.add_column("Category", style="magenta")
    summary_table.add_column("Topic", style="cyan")
    summary_table.add_column("For", justify="right")
    summary_table.add_column("Against", justify="right")
    summary_table.add_column("Abstain", justify="right")
    summary_table.add_column("Result", justify="center")

    for entry in game_state.game_history:
        result = entry["vote_result"]
        outcome_style = "green" if result["outcome"] == "PASSED" else "red"

        # Handle case where topic might be None
        topic_display = "Unknown Topic"
        if entry["topic"]:
            topic_display = entry["topic"][:30] + "..." if len(entry["topic"]) > 30 else entry["topic"]
            
        # Get topic category or default if not available (for backward compatibility)
        topic_category = entry.get("topic_category", "Unknown")
        
        summary_table.add_row(
            entry["year_display"],
            topic_category,  # Add the topic category
            topic_display,
            str(result["votes"]["for"]),
            str(result["votes"]["against"]),
            str(result["votes"]["abstain"]),
            f"[bold {outcome_style}]{result['outcome']}[/]",
        )

    console.print(summary_table)
    console.print(
        "\n[bold green]Game session complete![/] Type 'senate play' to start a new session.\n"
    )


@app.command()
def info():
    """Display information about the senators and game rules."""
    # Ensure correct working directory
    ensure_correct_path()

    if not game_state.senators:
        # No active game session, display general information
        display_game_rules()
        console.print(
            "\n[yellow]No active senate session.[/] Start a game with 'senate play' to view senator information.\n"
        )
    else:
        # Display both rules and senator information
        display_game_rules()
        display_senators_info(game_state.senators)


@app.callback()
def main():
    """Roman Senate AI Game - Experience politics in Ancient Rome."""
    # Ensure correct working directory
    ensure_correct_path()


if __name__ == "__main__":
    ensure_correct_path()
    app()
