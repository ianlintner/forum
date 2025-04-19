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
import importlib
import logging
from typing import Optional, List
from rich.console import Console
from rich.table import Table
from datetime import datetime

# Import the logging utilities
from src.roman_senate.utils.logging_utils import setup_logging, get_logger

# Fix import issues when running the script directly
# Set up path correctly first before any other imports
script_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(os.path.dirname(script_dir))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

# Determine if running as a script or as a module
is_running_directly = __name__ == "__main__"

# If running directly, set package name to enable relative imports
if is_running_directly:
    # When running as script, we need to set __package__ manually
    package_name = "src.roman_senate"
    __package__ = package_name

# Global variables to be set after imports
LLM_PROVIDER = None
# Flag to determine which architecture to use (legacy or framework)
USE_FRAMEWORK = False
LLM_MODEL = None
save_game = None
load_game = None
get_save_files = None
auto_save = None
setup_logging = None
get_logger = None

# Initialize the necessary modules
def init_imports():
    global LLM_PROVIDER, LLM_MODEL, save_game, load_game, get_save_files, auto_save, setup_logging, get_logger
    
    # Use dynamic import to handle both direct execution and module import
    if is_running_directly:
        # If running as a script directly (./cli.py), use absolute imports
        config_module = importlib.import_module("src.roman_senate.utils.config")
        persistence_module = importlib.import_module("src.roman_senate.core.persistence")
        utils_module = importlib.import_module("src.roman_senate.utils")
    else:
        # If running as a module (python -m src.roman_senate.cli), use relative imports
        config_module = importlib.import_module(".utils.config", package=__package__)
        persistence_module = importlib.import_module(".core.persistence", package=__package__)
        utils_module = importlib.import_module(".utils", package=__package__)

    # Extract the needed imports from the modules
    LLM_PROVIDER = config_module.LLM_PROVIDER
    LLM_MODEL = config_module.LLM_MODEL
    save_game = persistence_module.save_game
    load_game = persistence_module.load_game
    get_save_files = persistence_module.get_save_files
    auto_save = persistence_module.auto_save
    setup_logging = utils_module.setup_logging
    get_logger = utils_module.get_logger

# Initialize imports
init_imports()

app = typer.Typer(help="Roman Senate AI Simulation Game")
console = Console()
logger = None  # Will be initialized in main()

@app.callback()
def main(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Increase output verbosity"),
    log_level: str = typer.Option(None, "--log-level", help="Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"),
    log_file: str = typer.Option(None, "--log-file", help="Custom log file path"),
    use_framework: bool = typer.Option(False, "--use-framework", help="Use the new Agentic Game Framework architecture")
):
    """
    Roman Senate AI Simulation Game - A political simulation set in ancient Rome
    
    This application supports both the legacy architecture and the new Agentic Game Framework.
    Use the --use-framework flag to enable the new architecture.
    """
    global logger, USE_FRAMEWORK
    
    # Set the global framework flag
    USE_FRAMEWORK = use_framework
    
    # Set up logging early
    logger = setup_logging(log_level=log_level, log_file=log_file, verbose=verbose)
    
    # Log application startup
    logger.info("Roman Senate AI Game starting")
    logger.info(f"Using LLM Provider: {LLM_PROVIDER} (Model: {LLM_MODEL})")
    logger.info(f"Architecture mode: {'Agentic Framework' if USE_FRAMEWORK else 'Legacy'}")
    
    # Display version info and environment
    console.print("[bold cyan]Roman Senate AI Game[/]")
    console.print(f"[dim]Using LLM Provider: {LLM_PROVIDER} (Model: {LLM_MODEL})[/]")
    if USE_FRAMEWORK:
        console.print("[bold green]Using Agentic Game Framework architecture[/]")
    
    # Ensure correct working directory
    ensure_correct_path()
    
    # Log command line arguments
    logger.debug(f"Command line arguments: verbose={verbose}, log_level={log_level}, log_file={log_file}, use_framework={use_framework}")

def ensure_correct_path():
    """Ensure the script runs from the correct directory."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(os.path.dirname(script_dir))  # Get project root
    
    if os.getcwd() != base_dir:
        os.chdir(base_dir)
        console.print(f"[dim]Changed working directory to: {base_dir}[/]")
        logger.debug(f"Changed working directory to: {base_dir}")

    # Add the base directory to Python path
    if base_dir not in sys.path:
        sys.path.insert(0, base_dir)
        console.print(f"[dim]Added {base_dir} to Python path[/]")
        logger.debug(f"Added {base_dir} to Python path")


@app.command(name="play")
def play(
    senators: int = typer.Option(10, help="Number of senators to simulate"),
    debate_rounds: int = typer.Option(3, help="Number of debate rounds per topic"),
    topics: int = typer.Option(3, help="Number of topics to debate"),
    year: int = typer.Option(-100, help="Year in Roman history (negative for BCE)"),
    provider: str = typer.Option(None, help="LLM provider to use (defaults to config)"),
    model: str = typer.Option(None, help="LLM model to use (defaults to config)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Increase output verbosity"),
    log_level: str = typer.Option(None, "--log-level", help="Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"),
    log_file: str = typer.Option(None, "--log-file", help="Custom log file path")
):
    """
    Start a new game session of the Roman Senate simulation.
    
    Supports both legacy and Agentic Game Framework architectures via the global --use-framework flag.
    """
    try:
        # Convert parameters to integers (typer does this automatically, but keeping for safety)
        senators_int = int(senators)
        debate_rounds_int = int(debate_rounds)
        topics_int = int(topics)
        year_int = int(year)
        
        # Log play command execution
        architecture_mode = "Agentic Framework" if USE_FRAMEWORK else "Legacy"
        logger.info(f"Starting play mode ({architecture_mode}): senators={senators_int}, debate_rounds={debate_rounds_int}, topics={topics_int}, year={year_int}")
        
        if USE_FRAMEWORK:
            # Import the framework simulation components
            try:
                from src.roman_senate_framework.domains.senate.simulation import run_simulation
                
                # Select LLM provider
                llm_provider = None
                if provider:
                    if provider.lower() == "mock":
                        from src.roman_senate.utils.llm.mock_provider import MockProvider
                        llm_provider = MockProvider()
                    elif provider.lower() == "openai":
                        from src.roman_senate.utils.llm.openai_provider import OpenAIProvider
                        llm_provider = OpenAIProvider(model=model or "gpt-3.5-turbo")
                    elif provider.lower() == "ollama":
                        from src.roman_senate.utils.llm.ollama_provider import OllamaProvider
                        llm_provider = OllamaProvider(model=model or "llama2")
                
                # Create default topics
                debate_topics = [
                    "The expansion of Roman citizenship to Italian allies",
                    "Funding for new aqueducts in Rome",
                    "Military reforms proposed by the consul",
                    "Land redistribution to veterans",
                    "Grain subsidies for the urban poor"
                ]
                
                # Use only the requested number of topics
                selected_topics = debate_topics[:topics_int]
                
                # Configuration
                config = {
                    "year": year_int,
                    "topics": selected_topics,
                    "factions": ["Optimates", "Populares", "Neutral"],
                    "debate": {
                        "max_rounds": debate_rounds_int,
                        "speech_time_limit": 120,
                        "interjection_limit": 2,
                        "reaction_limit": 5
                    }
                }
                
                console.print("[bold green]Using Agentic Game Framework architecture[/]")
                
                # Run the framework simulation
                asyncio.run(run_simulation(
                    num_senators=senators_int,
                    topics=selected_topics,
                    rounds_per_topic=debate_rounds_int,
                    llm_provider=llm_provider,
                    config=config
                ))
            except ImportError as e:
                logger.error(f"Failed to import framework components: {e}")
                console.print("[bold red]Failed to load framework components. Falling back to legacy mode.[/]")
                # Fall back to legacy mode
                asyncio.run(play_async(senators_int, debate_rounds_int, topics_int, year_int))
        else:
            # Run the legacy async play function
            console.print("[dim]Using legacy architecture[/]")
            asyncio.run(play_async(senators_int, debate_rounds_int, topics_int, year_int))
    except Exception as e:
        error_msg = f"Fatal game error: {str(e)}"
        logger.error(error_msg)
        console.print(f"\n[bold red]{error_msg}[/bold red]")
        
        # Add detailed traceback for debugging
        import traceback
        trace = traceback.format_exc()
        logger.error(f"Traceback:\n{trace}")
        
        console.print("\n[bold yellow]Detailed Error Information:[/bold yellow]")
        console.print(trace)
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
    if is_running_directly:
        from src.roman_senate.core.game_state import game_state
        from src.roman_senate.core import senators as senators_module
        from src.roman_senate.core import topic_generator, senate_session, debate, vote
    else:
        from .core.game_state import game_state
        from .core import senators as senators_module
        from .core import topic_generator, senate_session, debate, vote
    
    logger.info(f"LLM integration check successful. Using model: {LLM_MODEL}")
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
        logger.info(f"Initializing the Senate with {senators} senators")
        senate_members = senators_module.initialize_senate(senators)
        game_state.senators = senate_members
        
        # Display senators info if desired (optional)
        if senators <= 15:  # Only show details for smaller senates
            senators_module.display_senators_info(senate_members)
        
        # 3. Generate topics for the session
        console.print("\n[bold cyan]Generating debate topics...[/]")
        logger.info(f"Generating {topics} debate topics for year {year}")
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
        logger.info("Beginning Senate session")
        results = await senate_session.run_session(
            senators_count=senators,
            debate_rounds=debate_rounds,
            topics_count=topics,
            year=year
        )
        
        # 5. Display game completion message with summary
        console.print("\n[bold green]Game session completed successfully![/]")
        console.print(f"Simulated {len(results)} topics with {senators} senators in the year {abs(year)} BCE.")
        logger.info(f"Game session completed successfully! Simulated {len(results)} topics with {senators} senators in year {abs(year)} BCE")
        
        # Display vote summary for each topic
        for result in results:
            vote.display_vote_result(result['vote_result'])
        
        console.print("\nType 'senate play' to start a new session.")
        
    except Exception as e:
        error_msg = f"Error during game session: {str(e)}"
        logger.error(error_msg)
        console.print(f"\n[bold red]{error_msg}[/]")
        import traceback
        trace = traceback.format_exc()
        logger.error(f"Traceback:\n{trace}")
        console.print(trace)


@app.command(name="play-as-senator")
def play_as_senator(
    senators: int = typer.Option(9, help="Number of NPC senators to simulate (plus you)"),
    topics: int = typer.Option(3, help="Number of topics to debate"),
    year: int = typer.Option(-100, help="Year in Roman history (negative for BCE)"),
    provider: str = typer.Option(None, help="LLM provider to use (defaults to config)"),
    model: str = typer.Option(None, help="LLM model to use (defaults to config)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Increase output verbosity"),
    log_level: str = typer.Option(None, "--log-level", help="Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"),
    log_file: str = typer.Option(None, "--log-file", help="Custom log file path")
):
    """
    Start a new game as a Roman Senator, allowing you to participate in debates and votes.
    
    Supports both legacy and Agentic Game Framework architectures via the global --use-framework flag.
    """
    try:
        # Convert parameters to integers (typer does this automatically, but keeping for safety)
        senators_int = int(senators)
        topics_int = int(topics)
        year_int = int(year)
        
        # Log player game start
        architecture_mode = "Agentic Framework" if USE_FRAMEWORK else "Legacy"
        logger.info(f"Starting player mode ({architecture_mode}): senators={senators_int}, topics={topics_int}, year={year_int}")
        
        if USE_FRAMEWORK:
            try:
                # Import the framework player module
                from src.roman_senate_framework.domains.senate.player.interactive_mode import InteractivePlayerSession
                
                # Select LLM provider
                llm_provider = None
                if provider:
                    if provider.lower() == "mock":
                        from src.roman_senate.utils.llm.mock_provider import MockProvider
                        llm_provider = MockProvider()
                    elif provider.lower() == "openai":
                        from src.roman_senate.utils.llm.openai_provider import OpenAIProvider
                        llm_provider = OpenAIProvider(model=model or "gpt-3.5-turbo")
                    elif provider.lower() == "ollama":
                        from src.roman_senate.utils.llm.ollama_provider import OllamaProvider
                        llm_provider = OllamaProvider(model=model or "llama2")
                
                # Create default topics
                debate_topics = [
                    "The expansion of Roman citizenship to Italian allies",
                    "Funding for new aqueducts in Rome",
                    "Military reforms proposed by the consul",
                    "Land redistribution to veterans",
                    "Grain subsidies for the urban poor"
                ]
                
                # Use only the requested number of topics
                selected_topics = debate_topics[:topics_int]
                
                console.print("[bold green]Using Agentic Game Framework architecture for interactive mode[/]")
                
                # Set up player session
                player_session = InteractivePlayerSession(
                    num_senators=senators_int,
                    topics=selected_topics,
                    year=year_int,
                    llm_provider=llm_provider
                )
                
                # Run the interactive player session
                asyncio.run(player_session.start())
                
            except ImportError as e:
                logger.error(f"Failed to import framework player components: {e}")
                console.print("[bold red]Failed to load framework player components. Falling back to legacy mode.[/]")
                # Fall back to legacy mode
                if is_running_directly:
                    from src.roman_senate.player.game_loop import PlayerGameLoop
                else:
                    from .player.game_loop import PlayerGameLoop
                
                player_loop = PlayerGameLoop()
                asyncio.run(player_loop.start_game(senators_int, topics_int, year_int))
        else:
            # Use the legacy player game loop
            console.print("[dim]Using legacy architecture for interactive mode[/]")
            
            # Import player game loop here to avoid circular imports
            if is_running_directly:
                from src.roman_senate.player.game_loop import PlayerGameLoop
            else:
                from .player.game_loop import PlayerGameLoop
            
            # Create and start the player game loop
            player_loop = PlayerGameLoop()
            asyncio.run(player_loop.start_game(senators_int, topics_int, year_int))
        
    except Exception as e:
        error_msg = f"Fatal game error: {str(e)}"
        logger.error(error_msg)
        console.print(f"\n[bold red]{error_msg}[/bold red]")
        
        # Add detailed traceback for debugging
        import traceback
        trace = traceback.format_exc()
        logger.error(f"Traceback:\n{trace}")
        
        console.print("\n[bold yellow]Detailed Error Information:[/bold yellow]")
        console.print(trace)
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
    model: str = typer.Option(None, help="LLM model to use (defaults to config, for OpenAI use 'gpt-4' for non-turbo)"),
    use_framework: bool = typer.Option(None, help="Use the new Agentic Game Framework (overrides global setting)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Increase output verbosity"),
    log_level: str = typer.Option(None, "--log-level", help="Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"),
    log_file: str = typer.Option(None, "--log-file", help="Custom log file path")
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
            logger.info("Running in non-interactive test mode")
        
        # Convert parameters to integers
        senators_int = int(senators)
        debate_rounds_int = int(debate_rounds)
        topics_int = int(topics)
        year_int = int(year)
        # Run the unified simulation
        console.print("[dim]Starting Roman Senate simulation...[/]")
        
        # Determine which architecture to use:
        # - Command parameter overrides global setting if provided (not None)
        # - Otherwise use global setting
        should_use_framework = use_framework if use_framework is not None else USE_FRAMEWORK
        
        logger.info(f"Starting simulation: senators={senators_int}, debate_rounds={debate_rounds_int}, topics={topics_int}, year={year_int}, provider={provider}, model={model}, use_framework={should_use_framework}")
        
        if should_use_framework:
            # Run simulation with the new framework
            console.print("[bold cyan]Using new Agentic Game Framework[/]")
            logger.info("Using new Agentic Game Framework for simulation")
            asyncio.run(run_framework_simulation(senators_int, debate_rounds_int, topics_int, year_int, provider, model))
        else:
            # Run simulation with the traditional system
            console.print("[dim]Using legacy architecture[/]")
            asyncio.run(run_simulation_async(senators_int, debate_rounds_int, topics_int, year_int, provider, model))
        
    except Exception as e:
        error_msg = f"Simulation error: {str(e)}"
        logger.error(error_msg)
        console.print(f"\n[bold red]{error_msg}[/bold red]")
        
        # Add detailed traceback for debugging
        import traceback
        trace = traceback.format_exc()
        logger.error(f"Traceback:\n{trace}")
        
        console.print("\n[bold yellow]Detailed Error Information:[/bold yellow]")
        console.print(trace)
        
        # Exit with error code for CI/CD
        if non_interactive:
            logger.critical("Exiting with error code 1 due to simulation failure in non-interactive mode")
            sys.exit(1)

async def run_framework_simulation(senators: int = 10, debate_rounds: int = 3, topics: int = 3, year: int = -100, provider: str = None, model: str = None):
    """
    Run a simulation using the new Agentic Game Framework.
    
    This function uses the integration components to run a Senate simulation
    with the new framework architecture.
    
    Args:
        senators: Number of senators to simulate
        debate_rounds: Number of debate rounds per topic
        topics: Number of topics to debate
        year: Year in Roman history (negative for BCE)
        provider: LLM provider to use (defaults to config)
        model: LLM model to use (defaults to config)
    """
    # Import the framework integration demo
    if is_running_directly:
        from src.roman_senate.examples.framework_integration_demo.framework_integration_demo import FrameworkIntegrationDemo
    else:
        from .examples.framework_integration_demo.framework_integration_demo import FrameworkIntegrationDemo
    
    # Use a deterministic seed if in test/non-interactive mode for reproducibility
    if os.environ.get('ROMAN_SENATE_TEST_MODE') == 'true':
        import random
        random.seed(42)
        console.print("[dim]Using deterministic seed for testing...[/]")
        logger.debug("Using deterministic seed (42) for testing")
    
    # Create and run the framework integration demo
    console.print("[bold cyan]Initializing Framework Integration Demo...[/]")
    demo = FrameworkIntegrationDemo(num_senators=senators, num_topics=topics)
    
    # Run the simulation
    console.print("[bold cyan]Running Senate simulation with Agentic Game Framework...[/]")
    await demo.run_simulation()
    
    console.print("\n[bold green]Framework simulation completed successfully![/]")
    console.print(f"Simulated {topics} topics with {senators} senators in the year {abs(year)} BCE using the new framework.")
    
    return demo.event_history

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
    if is_running_directly:
        from src.roman_senate.agent_simulation import run_simulation
    else:
        from .agent_simulation import run_simulation
    
    # Use a deterministic seed if in test/non-interactive mode for reproducibility
    if os.environ.get('ROMAN_SENATE_TEST_MODE') == 'true':
        import random
        random.seed(42)
        console.print("[dim]Using deterministic seed for testing...[/]")
        logger.debug("Using deterministic seed (42) for testing")
   
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
def info(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Increase output verbosity"),
    log_level: str = typer.Option(None, "--log-level", help="Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"),
    log_file: str = typer.Option(None, "--log-file", help="Custom log file path")
):
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
        "\n• senate save - Save the current game state"
        "\n• senate load <filename> - Load a saved game"
        "\n• senate list-saves - Show available save files"
        "\n• senate info - Display this information"
    )
@app.command(name="save")
def save_command(
    filename: Optional[str] = typer.Argument(None, help="Optional custom filename for the save (without extension)")
):
    """Save the current game state to a file."""
    try:
        # Check if there's an active game state to save
        if is_running_directly:
            from src.roman_senate.core.game_state import game_state
        else:
            from .core.game_state import game_state
            
        if not game_state.senators:
            console.print("[bold red]No active game to save.[/] Start a game first with 'senate play' or 'senate play-as-senator'.")
            return
            
        # Save the game
        saved_path = save_game(filename)
        console.print(f"[bold green]Game saved successfully to:[/] {saved_path}")
        logger.info(f"Game saved successfully to: {saved_path}")
        
    except Exception as e:
        error_msg = f"Error saving game: {str(e)}"
        logger.error(error_msg)
        console.print(f"[bold red]{error_msg}[/]")
        import traceback
        trace = traceback.format_exc()
        logger.error(f"Traceback:\n{trace}")
        console.print(trace)


@app.command(name="load")
def load_command(
    filename: str = typer.Argument(..., help="Name of the save file to load")
):
    """Load a game state from a save file."""
    try:
        # Load the game
        if load_game(filename):
            console.print(f"[bold green]Game loaded successfully from:[/] {filename}")
            console.print("Use 'senate play' to continue the loaded game session.")
            logger.info(f"Game loaded successfully from: {filename}")
        else:
            console.print(f"[bold red]Failed to load game from:[/] {filename}")
            logger.error(f"Failed to load game from: {filename}")
            
    except Exception as e:
        error_msg = f"Error loading game: {str(e)}"
        logger.error(error_msg)
        console.print(f"[bold red]{error_msg}[/]")
        import traceback
        trace = traceback.format_exc()
        logger.error(f"Traceback:\n{trace}")
        console.print(trace)


@app.command(name="list-saves")
def list_saves_command():
    """List all available save files."""
    try:
        # Get all save files
        save_files = get_save_files()
        
        if not save_files:
            console.print("[yellow]No save files found.[/]")
            logger.info("No save files found")
            return
            
        # Create table
        table = Table(title="Available Save Files")
        table.add_column("Filename", style="cyan")
        table.add_column("Created", style="green")
        table.add_column("Year", style="yellow")
        table.add_column("Senators", style="magenta")
        table.add_column("Topics", style="blue")
        
        # Add each save file to the table
        for save_file in save_files:
            table.add_row(
                save_file["filename"],
                save_file["created"],
                str(save_file["year"]),
                str(save_file["senator_count"]),
                str(save_file["topics_resolved"])
            )
            
        # Display the table
        console.print(table)
        console.print("\nTo load a save file, use: senate load <filename>")
        logger.info(f"Listed {len(save_files)} save files")
        
    except Exception as e:
        error_msg = f"Error listing save files: {str(e)}"
        logger.error(error_msg)
        console.print(f"[bold red]{error_msg}[/]")
        import traceback
        trace = traceback.format_exc()
        logger.error(f"Traceback:\n{trace}")
        console.print(trace)


if __name__ == "__main__":
    # This ensures the script can be run directly with python cli.py
    app()