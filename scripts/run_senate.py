#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Roman Senate AI Game
CLI Runner

This script provides a convenient entry point to run the Roman Senate simulation
without having to worry about Python's module/import system.
Simply run: python run_senate.py [commands...]
"""

import os
import sys
import typer
import asyncio
import logging
from typing import Optional, List

# Add the project directory to the Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

# Import the CLI app after setting the correct path
from src.roman_senate.cli import app as senate_app, USE_FRAMEWORK
from src.roman_senate.utils.logging_utils import setup_logging

# Create a unified Typer app
app = typer.Typer(help="Roman Senate AI Simulation Game - Unified CLI")

# Set up logging
logger = None

@app.callback()
def main(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Increase output verbosity"),
    log_level: str = typer.Option(None, "--log-level", help="Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"),
    log_file: str = typer.Option(None, "--log-file", help="Custom log file path"),
    use_framework: bool = typer.Option(True, "--use-framework/--use-legacy", help="Use the new Agentic Game Framework architecture")
):
    """
    Roman Senate AI Simulation Game - A political simulation set in ancient Rome
    
    This script supports both the legacy architecture and the new Agentic Game Framework.
    By default, it uses the new framework, but you can switch to legacy mode with --use-legacy.
    """
    global logger
    
    # Set up logging early
    logger = setup_logging(log_level=log_level, log_file=log_file, verbose=verbose)
    
    # Set the framework flag in the imported CLI module
    # This will affect all commands that use it
    import src.roman_senate.cli
    src.roman_senate.cli.USE_FRAMEWORK = use_framework
    
    # Log application startup
    architecture = "Agentic Framework" if use_framework else "Legacy"
    logger.info(f"Roman Senate AI Game ({architecture} architecture) starting")
    
    # Display version info and environment
    typer.echo(typer.style("Roman Senate AI Game", fg="cyan", bold=True))
    typer.echo(typer.style(f"Architecture: {architecture}", fg="green", bold=use_framework))
    
    # Ensure correct working directory
    ensure_correct_path()

def ensure_correct_path():
    """Ensure the script runs from the correct directory."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    if os.getcwd() != script_dir:
        os.chdir(script_dir)
        logger.debug(f"Changed working directory to: {script_dir}")
    
    # Add the base directory to Python path
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)
        logger.debug(f"Added {script_dir} to Python path")

@app.command(name="simulate")
def simulate(
    senators: int = typer.Option(10, help="Number of senators to simulate"),
    debate_rounds: int = typer.Option(3, help="Number of debate rounds per topic"),
    topics: int = typer.Option(3, help="Number of topics to debate"),
    year: int = typer.Option(-100, help="Year in Roman history (negative for BCE)"),
    provider: str = typer.Option("mock", help="LLM provider (mock, openai, ollama)"),
    model: str = typer.Option(None, help="LLM model name"),
    non_interactive: bool = typer.Option(False, help="Run in non-interactive mode (for CI/CD testing)")
):
    """
    Run a simulation of the Roman Senate.
    
    This command will use either the legacy or framework architecture based on
    the --use-framework/--use-legacy global flag.
    """
    try:
        # Convert parameters to integers (typer does this automatically, but keeping for safety)
        senators_int = int(senators)
        debate_rounds_int = int(debate_rounds)
        topics_int = int(topics)
        year_int = int(year)
        
        # Get the current architecture mode from the CLI module
        import src.roman_senate.cli
        using_framework = src.roman_senate.cli.USE_FRAMEWORK
        
        # Log simulation command execution
        architecture = "Agentic Framework" if using_framework else "Legacy"
        logger.info(f"Starting {architecture} simulation: senators={senators_int}, debate_rounds={debate_rounds_int}, topics={topics_int}, year={year_int}")
        
        # Use the unified CLI to run the simulation with the current framework setting
        # This avoids duplicating code between the scripts and CLI
        from src.roman_senate.cli import simulate as cli_simulate
        cli_simulate(
            senators=senators_int,
            debate_rounds=debate_rounds_int,
            topics=topics_int,
            year=year_int,
            non_interactive=non_interactive,
            provider=provider,
            model=model,
            use_framework=using_framework,
            verbose=False
        )
    except Exception as e:
        error_msg = f"Fatal simulation error: {str(e)}"
        logger.error(error_msg)
        typer.echo(typer.style(f"\n{error_msg}", fg="red", bold=True))
        
        # Add detailed traceback for debugging
        import traceback
        trace = traceback.format_exc()
        logger.error(f"Traceback:\n{trace}")
        
        typer.echo(typer.style("\nDetailed Error Information:", fg="yellow", bold=True))
        typer.echo(trace)
        typer.echo(typer.style(f"\nError Type:", fg="cyan", bold=True) + f" {type(e).__name__}")
        typer.echo(typer.style(f"Error Location:", fg="cyan", bold=True) + f" Look for 'File' and line number in traceback above")
        
        typer.echo("\nSimulation terminated. Type 'python run_senate.py simulate' to try again.\n")

@app.command(name="play")
def play(
    senators: int = typer.Option(10, help="Number of senators to simulate"),
    debate_rounds: int = typer.Option(3, help="Number of debate rounds per topic"),
    topics: int = typer.Option(3, help="Number of topics to debate"),
    year: int = typer.Option(-100, help="Year in Roman history (negative for BCE)"),
    provider: str = typer.Option(None, help="LLM provider to use (defaults to config)"),
    model: str = typer.Option(None, help="LLM model to use (defaults to config)")
):
    """
    Start a new game session of the Roman Senate simulation.
    
    This command will use either the legacy or framework architecture based on
    the --use-framework/--use-legacy global flag.
    """
    try:
        # Convert parameters to integers
        senators_int = int(senators)
        debate_rounds_int = int(debate_rounds)
        topics_int = int(topics)
        year_int = int(year)
        
        # Get the current architecture mode from the CLI module
        import src.roman_senate.cli
        using_framework = src.roman_senate.cli.USE_FRAMEWORK
        
        # Log game command execution
        architecture = "Agentic Framework" if using_framework else "Legacy"
        logger.info(f"Starting play mode ({architecture}): senators={senators_int}, debate_rounds={debate_rounds_int}, topics={topics_int}, year={year_int}")
        
        # Use the unified CLI to run the game with the current framework setting
        from src.roman_senate.cli import play as cli_play
        cli_play(
            senators=senators_int,
            debate_rounds=debate_rounds_int,
            topics=topics_int,
            year=year_int,
            provider=provider,
            model=model,
            verbose=False
        )
    except Exception as e:
        error_msg = f"Fatal game error: {str(e)}"
        logger.error(error_msg)
        typer.echo(typer.style(f"\n{error_msg}", fg="red", bold=True))
        
        # Add detailed traceback for debugging
        import traceback
        trace = traceback.format_exc()
        logger.error(f"Traceback:\n{trace}")
        
        typer.echo(typer.style("\nDetailed Error Information:", fg="yellow", bold=True))
        typer.echo(trace)
        typer.echo(typer.style(f"\nError Type:", fg="cyan", bold=True) + f" {type(e).__name__}")
        typer.echo(typer.style(f"Error Location:", fg="cyan", bold=True) + f" Look for 'File' and line number in traceback above")
        
        typer.echo("\nGame session terminated. Type 'python run_senate.py play' to try again.\n")

@app.command(name="play-as-senator")
def play_as_senator(
    senators: int = typer.Option(9, help="Number of NPC senators to simulate (plus you)"),
    topics: int = typer.Option(3, help="Number of topics to debate"),
    year: int = typer.Option(-100, help="Year in Roman history (negative for BCE)"),
    provider: str = typer.Option(None, help="LLM provider to use (defaults to config)"),
    model: str = typer.Option(None, help="LLM model to use (defaults to config)")
):
    """
    Start a new game as a Roman Senator, allowing you to participate in debates and votes.
    
    This command will use either the legacy or framework architecture based on
    the --use-framework/--use-legacy global flag.
    """
    try:
        # Convert parameters to integers
        senators_int = int(senators)
        topics_int = int(topics)
        year_int = int(year)
        
        # Get the current architecture mode from the CLI module
        import src.roman_senate.cli
        using_framework = src.roman_senate.cli.USE_FRAMEWORK
        
        # Log player game command execution
        architecture = "Agentic Framework" if using_framework else "Legacy"
        logger.info(f"Starting player mode ({architecture}): senators={senators_int}, topics={topics_int}, year={year_int}")
        
        # Use the unified CLI to run the player game with the current framework setting
        from src.roman_senate.cli import play_as_senator as cli_play_as_senator
        cli_play_as_senator(
            senators=senators_int,
            topics=topics_int,
            year=year_int,
            provider=provider,
            model=model,
            verbose=False
        )
    except Exception as e:
        error_msg = f"Fatal game error: {str(e)}"
        logger.error(error_msg)
        typer.echo(typer.style(f"\n{error_msg}", fg="red", bold=True))
        
        # Add detailed traceback for debugging
        import traceback
        trace = traceback.format_exc()
        logger.error(f"Traceback:\n{trace}")
        
        typer.echo(typer.style("\nDetailed Error Information:", fg="yellow", bold=True))
        typer.echo(trace)
        typer.echo(typer.style(f"\nError Type:", fg="cyan", bold=True) + f" {type(e).__name__}")
        typer.echo(typer.style(f"Error Location:", fg="cyan", bold=True) + f" Look for 'File' and line number in traceback above")
        
        typer.echo("\nGame session terminated. Type 'python run_senate.py play-as-senator' to try again.\n")

@app.command(name="info")
def info():
    """Display information about the game and available commands."""
    # Call the info command from the main CLI
    from src.roman_senate.cli import info as cli_info
    cli_info()
    
    # Add script-specific information
    typer.echo("\n" + typer.style("Additional Script Information:", fg="cyan", bold=True))
    typer.echo("This unified script allows you to use both architectures via the --use-framework/--use-legacy flags.")
    typer.echo("By default, the new Agentic Game Framework architecture is used.")

# Run the typer CLI app
if __name__ == "__main__":
    # If no arguments provided, show help
    if len(sys.argv) == 1:
        sys.argv.append("--help")
    app()