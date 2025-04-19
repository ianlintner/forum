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
from src.roman_senate.cli import app as legacy_app
from src.roman_senate.utils.logging_utils import setup_logging

# Create a new Typer app for the framework-based implementation
app = typer.Typer(help="Roman Senate AI Simulation Game (Framework Edition)")

# Set up logging
logger = None

@app.callback()
def main(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Increase output verbosity"),
    log_level: str = typer.Option(None, "--log-level", help="Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"),
    log_file: str = typer.Option(None, "--log-file", help="Custom log file path")
):
    """
    Roman Senate AI Simulation Game - A political simulation set in ancient Rome
    
    This version uses the new Agentic Game Framework for enhanced simulation capabilities.
    """
    global logger
    
    # Set up logging early
    logger = setup_logging(log_level=log_level, log_file=log_file, verbose=verbose)
    
    # Log application startup
    logger.info("Roman Senate AI Game (Framework Edition) starting")
    
    # Display version info and environment
    typer.echo(typer.style("Roman Senate AI Game (Framework Edition)", fg="cyan", bold=True))
    
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
    model: str = typer.Option(None, help="LLM model name")
):
    """Run a simulation of the Roman Senate using the new framework."""
    try:
        # Convert parameters to integers (typer does this automatically, but keeping for safety)
        senators_int = int(senators)
        debate_rounds_int = int(debate_rounds)
        topics_int = int(topics)
        year_int = int(year)
        
        # Log simulation command execution
        logger.info(f"Starting framework simulation: senators={senators_int}, debate_rounds={debate_rounds_int}, topics={topics_int}, year={year_int}")
        
        # Run the async simulation function with asyncio.run
        asyncio.run(run_framework_simulation(senators_int, debate_rounds_int, topics_int, year_int, provider, model))
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

async def run_framework_simulation(
    senators: int = 10,
    debate_rounds: int = 3,
    topics: int = 3,
    year: int = -100,
    provider: str = None,
    model: str = None
):
    """
    Run a simulation using the new framework.
    
    Args:
        senators: Number of senators to simulate
        debate_rounds: Number of debate rounds per topic
        topics: Number of topics to debate
        year: Year in Roman history (negative for BCE)
        provider: LLM provider name
        model: LLM model name
    """
    # Import the framework simulation
    from src.roman_senate_framework.domains.senate.simulation import run_simulation
    
    # Import LLM provider
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
    
    # Generate topics
    # In a real implementation, we would use a topic generator
    # For now, we'll use some hardcoded topics
    debate_topics = [
        "The expansion of Roman citizenship to Italian allies",
        "Funding for new aqueducts in Rome",
        "Military reforms proposed by the consul",
        "Land redistribution to veterans",
        "Grain subsidies for the urban poor"
    ]
    
    # Use only the requested number of topics
    selected_topics = debate_topics[:topics]
    
    # Configuration
    config = {
        "year": year,
        "topics": selected_topics,
        "factions": ["Optimates", "Populares", "Neutral"],
        "debate": {
            "max_rounds": debate_rounds,
            "speech_time_limit": 120,
            "interjection_limit": 2,
            "reaction_limit": 5
        }
    }
    
    typer.echo(typer.style("\nStarting Roman Senate Simulation", fg="cyan", bold=True))
    typer.echo(f"Year: {abs(year)} BCE")
    typer.echo(f"Senators: {senators}")
    typer.echo(f"Topics: {len(selected_topics)}")
    typer.echo(f"Debate Rounds: {debate_rounds} per topic\n")
    
    # Run the simulation
    results = await run_simulation(
        num_senators=senators,
        topics=selected_topics,
        rounds_per_topic=debate_rounds,
        llm_provider=llm_provider,
        config=config
    )
    
    # Display results
    typer.echo(typer.style("\nSimulation Results:", fg="green", bold=True))
    for result in results:
        topic = result["topic"]
        speeches = result["speeches"]
        reactions = result["reactions"]
        interjections = result["interjections"]
        
        typer.echo(typer.style(f"\nTopic: {topic}", fg="yellow"))
        typer.echo(f"Speeches: {speeches}")
        typer.echo(f"Reactions: {reactions}")
        typer.echo(f"Interjections: {interjections}")
        
        # Display stance distribution
        stances = result.get("stances", {})
        support_count = sum(1 for stance in stances.values() if stance == "support")
        oppose_count = sum(1 for stance in stances.values() if stance == "oppose")
        neutral_count = sum(1 for stance in stances.values() if stance == "neutral")
        
        typer.echo(f"Stance Distribution: {support_count} support, {oppose_count} oppose, {neutral_count} neutral")
    
    typer.echo(typer.style("\nSimulation completed successfully!", fg="green", bold=True))

@app.command(name="legacy")
def legacy():
    """Run the legacy version of the Roman Senate simulation."""
    # Just pass through to the legacy CLI
    legacy_app()

# Run the typer CLI app
if __name__ == "__main__":
    # If no arguments provided, show help
    if len(sys.argv) == 1:
        sys.argv.append("--help")
    app()