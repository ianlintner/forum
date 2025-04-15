
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Roman Senate AI Game
Command Line Interface

This module provides the command-line interface for the Roman Senate game.
It supports both simulation and player modes.
"""

import os
import sys
import typer
import asyncio
from typing import Optional
from rich.console import Console

from .utils.config import LLM_PROVIDER, LLM_MODEL

app = typer.Typer(help="Roman Senate AI Simulation Game")
console = Console()

@app.callback()
def main():
    """
    Roman Senate AI Simulation Game - A political simulation set in ancient Rome
    """
    # Display version info and environment
    console.print("[bold cyan]Roman Senate AI Game[/]")
    console.print(f"[dim]Using LLM Provider: {LLM_PROVIDER} (Model: {LLM_MODEL})[/]")
    
    # Ensure correct working directory
    ensure_correct_path()

def ensure_correct_path():
    """Ensure the script runs from the correct directory."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(os.path.dirname(script_dir))  # Get project root
    
    if os.getcwd() != base_dir:
        os.chdir(base_dir)
        console.print(f"[dim]Changed working directory to: {base_dir}[/]")

    # Add the base directory to Python path
    if base_dir not in sys.path:
        sys.path.insert(0, base_dir)
        console.print(f"[dim]Added {base_dir} to Python path[/]")


@app.command(name="play")
def play(
    senators: int = typer.Option(10, help="Number of senators to simulate"),
    debate_rounds: int = typer.Option(3, help="Number of debate rounds per topic"),
    topics: int = typer.Option(3, help="Number of topics to debate"),
    year: int = typer.Option(-100, help="Year in Roman history (negative for BCE)")
):
    """Start a new game session of the Roman Senate simulation."""
    try:
        # Convert parameters to integers (typer does this automatically, but keeping for safety)
        senators_int = int(senators)
        debate_rounds_int = int(debate_rounds)
        topics_int = int(topics)
        year_int = int(year)
        
        # Run the async play function with asyncio.run
        asyncio.run(play_async(senators_int, debate_rounds_int, topics_int, year_int))
    except Exception as e:
        console.print(f"\n[bold red]Fatal game error:[/bold red] {str(e)}")
        
        # Add detailed traceback for debugging
        import traceback
        console.print("\n[bold yellow]Detailed Error Information:[/bold yellow]")
        console.print(traceback.format_exc())
        console.print(f"\n[bold cyan]Error Type:[/bold cyan] {type(e).__name__}")
        console.print(f"[bold cyan]Error Location:[/bold cyan] Look for 'File' and line number in traceback above")
        
        console.print("\nGame session terminated. Type 'senate play' to try again.\n")

async def play_async(senators: int = 10, debate_rounds: int = 3, topics: int = 3, year: int = -100):
    """
    Async version of the main game loop.
    
    Args:
        senators: Number of senators to simulate
        debate_rounds: Number of debate rounds per topic
        topics: Number of topics to debate
        year: Year in Roman history (negative for BCE)
    """
    # We're importing these inside the function to avoid circular imports
    from .core.game_state import game_state
    from .core import senators as senators_module
    from .core import topic_generator, senate_session, debate, vote
    
    console.print(f"\n[bold green]✓[/] LLM integration is working. Using model: [bold cyan]{LLM_MODEL}[/]")
    
    # Display welcome banner
    console.print(
        "\n[bold cyan]ROMAN SENATE SIMULATION[/]\n"
        f"[bold]Year:[/] {abs(year)} BCE\n"
        f"[bold]Senators:[/] {senators}\n"
        f"[bold]Topics:[/] {topics}\n"
        f"[bold]Debate Rounds:[/] {debate_rounds} per topic\n"
    )
    
    # Integrated game loop
    try:
        # 1. Reset game state
        game_state.reset()
        game_state.year = year
        
        # 2. Initialize senators
        console.print("\n[bold cyan]Initializing the Senate...[/]")
        senate_members = senators_module.initialize_senate(senators)
        game_state.senators = senate_members
        
        # Display senators info if desired (optional)
        if senators <= 15:  # Only show details for smaller senates
            senators_module.display_senators_info(senate_members)
        
        # 3. Generate topics for the session
        console.print("\n[bold cyan]Generating debate topics...[/]")
        topics_by_category = await topic_generator.get_topics_for_year(year, topics)
        flattened_topics = topic_generator.flatten_topics_by_category(topics_by_category)
        
        # Select topics for this session
        selected_topics = []
        for i in range(min(topics, len(flattened_topics))):
            if i < len(flattened_topics):
                topic_obj = flattened_topics[i]
                selected_topics.append((topic_obj['text'], topic_obj['category']))
        
        # 4. Run the full senate session with debate and voting
        console.print("\n[bold cyan]Beginning Senate session...[/]")
        results = await senate_session.run_session(
            senators_count=senators,
            debate_rounds=debate_rounds,
            topics_count=topics,
            year=year
        )
        
        # 5. Display game completion message with summary
        console.print("\n[bold green]Game session completed successfully![/]")
        console.print(f"Simulated {len(results)} topics with {senators} senators in the year {abs(year)} BCE.")
        
        # Display vote summary for each topic
        for result in results:
            vote.display_vote_result(result['vote_result'])
        
        console.print("\nType 'senate play' to start a new session.")
        
    except Exception as e:
        console.print(f"\n[bold red]Error during game session:[/] {str(e)}")
        import traceback
        console.print(traceback.format_exc())
        console.print(traceback.format_exc())


@app.command(name="play-as-senator")
def play_as_senator(
    senators: int = typer.Option(9, help="Number of NPC senators to simulate (plus you)"),
    topics: int = typer.Option(3, help="Number of topics to debate"),
    year: int = typer.Option(-100, help="Year in Roman history (negative for BCE)")
):
    """Start a new game as a Roman Senator, allowing you to participate in debates and votes."""
    try:
        # Import player game loop here to avoid circular imports
        from .player.game_loop import PlayerGameLoop
        
        # Convert parameters to integers (typer does this automatically, but keeping for safety)
        senators_int = int(senators)
        topics_int = int(topics)
        year_int = int(year)
        
        # Create and start the player game loop
        player_loop = PlayerGameLoop()
        asyncio.run(player_loop.start_game(senators_int, topics_int, year_int))
        
    except Exception as e:
        console.print(f"\n[bold red]Fatal game error:[/bold red] {str(e)}")
        
        # Add detailed traceback for debugging
        import traceback
        console.print("\n[bold yellow]Detailed Error Information:[/bold yellow]")
        console.print(traceback.format_exc())
        console.print(f"\n[bold cyan]Error Type:[/bold cyan] {type(e).__name__}")
        console.print(f"[bold cyan]Error Location:[/bold cyan] Look for 'File' and line number in traceback above")
        
        console.print("\nGame session terminated. Type 'senate play-as-senator' to try again.\n")


@app.command(name="simulate", help="Run a simulation of the Roman Senate")
def simulate(
    senators: int = typer.Option(10, help="Number of senators to simulate"),
    debate_rounds: int = typer.Option(3, help="Number of debate rounds per topic"),
    topics: int = typer.Option(3, help="Number of topics to debate"),
    year: int = typer.Option(-100, help="Year in Roman history (negative for BCE)"),
    non_interactive: bool = typer.Option(False, help="Run in non-interactive mode (for CI/CD testing)"),
    provider: str = typer.Option(None, help="LLM provider to use (defaults to config)"),
    model: str = typer.Option(None, help="LLM model to use (defaults to config, for OpenAI use 'gpt-4' for non-turbo)")
):
    """
    Run a simulation of the Roman Senate with detailed speeches and voting displays.
    
    Uses agent-driven logic for intelligent decision-making combined with
    rich traditional formatting to display speeches, debates, and voting results.
    """
    try:
        # Set test mode environment variable if non_interactive
        if non_interactive:
            os.environ['ROMAN_SENATE_TEST_MODE'] = 'true'
            console.print("[bold yellow]Running in non-interactive test mode[/]")
        
        # Convert parameters to integers
        senators_int = int(senators)
        debate_rounds_int = int(debate_rounds)
        topics_int = int(topics)
        year_int = int(year)
        # Run the unified simulation
        console.print("[dim]Starting Roman Senate simulation...[/]")
        asyncio.run(run_simulation_async(senators_int, debate_rounds_int, topics_int, year_int, provider, model))
        
    except Exception as e:
        console.print(f"\n[bold red]Simulation error:[/bold red] {str(e)}")
        
        # Add detailed traceback for debugging
        import traceback
        console.print("\n[bold yellow]Detailed Error Information:[/bold yellow]")
        console.print(traceback.format_exc())
        
        # Exit with error code for CI/CD
        if non_interactive:
            sys.exit(1)
async def run_simulation_async(senators: int = 10, debate_rounds: int = 3, topics: int = 3, year: int = -100, provider: str = None, model: str = None):
    """
    Run a unified simulation of the Roman Senate using agent-driven logic with traditional display.
    
    Args:
        senators: Number of senators to simulate
        debate_rounds: Number of debate rounds per topic
        topics: Number of topics to debate
        year: Year in Roman history (negative for BCE)
        provider: LLM provider to use (defaults to config)
        model: LLM model to use (defaults to config)
    """
    # Import the unified simulation here to avoid circular imports
    from .agent_simulation import run_simulation
    
    # Use a deterministic seed if in test/non-interactive mode for reproducibility
    if os.environ.get('ROMAN_SENATE_TEST_MODE') == 'true':
        import random
        random.seed(42)
        console.print("[dim]Using deterministic seed for testing...[/]")
   
    # Run the unified simulation with rich display
    results = await run_simulation(
        senators_count=senators,
        debate_rounds=debate_rounds,
        topics_count=topics,
        year=year,
        provider=provider,
        model=model
    )
    
    # For CI/CD testing, output simplified results if in non-interactive mode
    if os.environ.get('ROMAN_SENATE_TEST_MODE') == 'true':
        # Output vote summary for test verification
        for i, result in enumerate(results):
            console.print(f"\n[bold]Topic {i+1} vote result:[/]")
            vote_result = result['vote_result']
            console.print(f"Outcome: {vote_result['outcome']}")
            
        console.print("[bold green]CI/CD test passed successfully[/]")
        
    return results

@app.command()
def info():
    """Display information about the game and its systems."""
    console.print(
        "\n[bold underline]ROMAN SENATE AI GAME[/]\n"
        "\n[bold]Game Description:[/]"
        "\nA political simulation set in the Roman Senate during the late Republic era."
        "\nAI senators with unique personalities, backgrounds, and political alignments"
        "\ndebate and vote on important matters facing Rome."
        
        "\n\n[bold]Technical Information:[/]"
        f"\nLLM Provider: [cyan]{LLM_PROVIDER}[/]"
        f"\nModel: [cyan]{LLM_MODEL}[/]"
        
        "\n\n[bold]Commands:[/]"
        "\n• senate play - Start a new simulation game session"
        "\n• senate play-as-senator - Play as a Roman Senator (interactive mode)"
        "\n• senate simulate - Run a simulation with detailed speeches and voting"
        "\n• senate info - Display this information"
    )

if __name__ == "__main__":
    app()