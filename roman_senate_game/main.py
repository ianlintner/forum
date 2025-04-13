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
import typer
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm
from rich.console import Console
from typing import List, Dict

# Project imports
import utils
import senators
import debate
import vote
from config import OPENAI_API_KEY

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
console = utils.console


# Game state
class GameState:
    def __init__(self):
        self.senators = []
        self.current_topic = None
        self.debate_round = 0
        self.voting_results = []
        self.game_history = []

    def reset(self):
        """Reset the game state for a new session."""
        self.senators = []
        self.current_topic = None
        self.debate_round = 0
        self.voting_results = []
        self.game_history = []


# Initialize game state
game_state = GameState()

# Sample debate topics
DEBATE_TOPICS = [
    "Expansion of Roman citizenship to conquered territories",
    "Funding for a new aqueduct in Rome",
    "Land redistribution for veterans of the Gallic wars",
    "Trade agreements with Carthage",
    "Military campaign against Germanic tribes",
    "Tax reforms for the provinces",
    "Grain subsidies for the urban poor",
    "Construction of a new temple to Jupiter",
    "Reforms to the judiciary system",
    "Diplomatic relations with Egypt",
]

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

def select_debate_topic():
    """Select a debate topic, either randomly or user-selected."""
    console.print("\n[bold yellow]Debate Topic Selection[/]")

    table = Table(title="Available Debate Topics")
    table.add_column("#", style="dim")
    table.add_column("Topic", style="cyan")

    for i, topic in enumerate(DEBATE_TOPICS):
        table.add_row(str(i + 1), topic)

    console.print(table)

    # Let user choose or select random with Rich
    choice = Prompt.ask(
        "Select a topic number or press [R] for random selection", default="R"
    )

    if choice.upper() == "R":
        topic = random.choice(DEBATE_TOPICS)
        console.print(f"[bold green]Randomly selected:[/] {topic}\n")
    else:
        try:
            index = int(choice) - 1
            if 0 <= index < len(DEBATE_TOPICS):
                topic = DEBATE_TOPICS[index]
                console.print(f"[bold green]Selected:[/] {topic}\n")
            else:
                topic = random.choice(DEBATE_TOPICS)
                console.print(
                    f"[bold yellow]Invalid selection. Randomly selected:[/] {topic}\n"
                )
        except ValueError:
            topic = random.choice(DEBATE_TOPICS)
            console.print(
                f"[bold yellow]Invalid input. Randomly selected:[/] {topic}\n"
            )

    game_state.current_topic = topic
    return topic


def conduct_debate(topic: str, senators_list: List[Dict], rounds: int = 3):
    """Conduct a debate on the given topic."""
    console.print(Panel(f"[bold cyan]SENATE DEBATE: {topic}[/]", expand=False))

    debate_summary = []

    for round_num in range(1, rounds + 1):
        console.print(f"\n[bold blue]Round {round_num} of Debate[/]")

        # Select speakers for this round
        speakers = random.sample(senators_list, min(3, len(senators_list)))

        for senator in speakers:
            # Simulate thinking and speaking
            with Progress(
                SpinnerColumn(),
                TextColumn(
                    f"[bold]{senator['name']} ({senator['faction']}) is formulating an argument...[/]"
                ),
                console=console,
            ) as progress:
                task = progress.add_task("Thinking...", total=1)
                # Simulate delay for effect
                time.sleep(1 + random.random())
                progress.update(task, completed=1)

            # Generate senator's argument
            argument_types = ["proposes", "opposes", "questions", "amends"]
            argument_action = random.choice(argument_types)

            argument = f"{senator['name']} {argument_action} the motion regarding {topic}, citing {random.choice(['historical precedent', 'economic concerns', 'military necessity', 'public opinion', 'religious implications'])}."

            # Display the argument
            utils.format_text(
                f"{senator['name']} ({senator['faction']})", style="bold cyan"
            )
            utils.format_text(argument, as_panel=True)

            # Score the argument
            score = utils.score_argument(argument, topic)

            # Show the score
            score_table = Table(title="Argument Assessment")
            score_table.add_column("Criterion", style="cyan")
            score_table.add_column("Score", justify="right")

            for criterion, value in score.items():
                if criterion != "total":
                    score_table.add_row(
                        criterion.replace("_", " ").title(), f"{value:.2f}"
                    )

            score_table.add_row("Overall", f"[bold]{score['total']:.2f}[/]")
            console.print(score_table)

            # Record the argument
            debate_summary.append(
                {
                    "round": round_num,
                    "senator": senator["name"],
                    "faction": senator["faction"],
                    "argument": argument,
                    "score": score["total"],
                }
            )

            # Pause for readability
            time.sleep(1)

    console.print("\n[bold green]✓[/] Debate concluded.\n")
    return debate_summary


def conduct_vote(topic: str, senators_list: List[Dict], debate_summary=None):
    """Conduct a vote on the given topic after debate."""
    console.print(Panel(f"[bold magenta]SENATE VOTE: {topic}[/]", expand=False))

    votes = {"for": 0, "against": 0, "abstain": 0}
    voting_record = []
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold]Senators are casting their votes...[/]"),
        console=console,
    ) as progress:
        task = progress.add_task("Voting...", total=len(senators_list))

        for senator in senators_list:
            process_senator_vote(senator, votes, voting_record)
            progress.update(task, advance=1)
            time.sleep(0.3 + random.random() * 0.5)

    # Display voting results
    console.print("\n[bold yellow]Voting Results:[/]")

    results_table = Table()
    results_table.add_column("Option", style="cyan")
    results_table.add_column("Votes", justify="right")
    results_table.add_column("Percentage", justify="right")

    total_votes = sum(votes.values())

    for option, count in votes.items():
        percentage = (count / total_votes) * 100 if total_votes > 0 else 0
        results_table.add_row(option.title(), str(count), f"{percentage:.1f}%")

    console.print(results_table)

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
    }
    game_state.voting_results.append(result)

    return result
def process_senator_vote(senator, votes, voting_record):
    """Helper function to process a senator's vote."""
    vote_options = ["for", "against", "abstain"]
    weights = [0.5, 0.4, 0.1]  # Biased slightly toward approval

    # Modify weights based on faction
    if senator["faction"] == "Optimates":
        weights = [0.4, 0.5, 0.1]  # More conservative
    elif senator["faction"] == "Populares":
        weights = [0.6, 0.3, 0.1]  # More progressive

    vote = random.choices(vote_options, weights=weights)[0]
    votes[vote] += 1

    voting_record.append(
        {
            "senator": senator["name"],
            "faction": senator["faction"],
            "vote": vote,
            "influence": senator["influence"],
        }
    )


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
    1. Initialize the Senate with AI senators from different factions
    2. Select a debate topic for the Senate to consider
    3. Conduct debates where senators present arguments
    4. Hold a vote on the proposed motion
    5. See the results and their implications
    6. Continue with new topics or end the session
    
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
def play(senators: int = 10, debate_rounds: int = 3, topics: int = 3):
    """Start a new game session of the Roman Senate simulation."""
    # Ensure correct working directory
    ensure_correct_path()

    # Clear game state for new session
    game_state.reset()

    # Display welcome banner
    console.print(
        Panel(
            "[bold yellow]ROMAN SENATE AI GAME[/]\n"
            "Step into the sandals of a Consul presiding over the Senate of Rome",
            title="SALVETE SENATORES!",
            border_style="yellow",
        )
    )

    # Initialize senate with AI senators
    senate = initialize_senate(senators)

    # Main game loop
    for topic_num in range(1, topics + 1):
        console.print(f"\n[bold]TOPIC {topic_num} OF {topics}[/]")

        # Select debate topic
        topic = select_debate_topic()

        # Conduct debate
        debate_summary = conduct_debate(topic, senate, rounds=debate_rounds)

        # Conduct vote
        vote_result = conduct_vote(topic, senate, debate_summary)

        # Record to game history
        game_state.game_history.append(
            {
                "topic_number": topic_num,
                "topic": topic,
                "debate_summary": debate_summary,
                "vote_result": vote_result,
            }
        )

        # Ask to continue if not the last topic
        if topic_num < topics:
            console.print()
            continue_game = Confirm.ask("Continue to the next topic?", default=True)
            if not continue_game:
                break

    # End of game summary
    console.print(Panel("[bold cyan]SENATE SESSION CONCLUDED[/]", border_style="cyan"))

    # Display summary of all votes
    console.print("\n[bold]Session Summary:[/]")

    summary_table = Table(title="Voting Results")
    summary_table.add_column("Topic", style="cyan")
    summary_table.add_column("For", justify="right")
    summary_table.add_column("Against", justify="right")
    summary_table.add_column("Abstain", justify="right")
    summary_table.add_column("Result", justify="center")

    for entry in game_state.game_history:
        result = entry["vote_result"]
        outcome_style = "green" if result["outcome"] == "PASSED" else "red"

        summary_table.add_row(
            entry["topic"][:30] + "..." if len(entry["topic"]) > 30 else entry["topic"],
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
