#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Roman Senate Websocket Server Runner

This script provides a convenient entry point to run the Roman Senate websocket server
without having to worry about Python's module/import system.
Simply run: python run_websocket_server.py [commands...]
"""

import os
import sys
import typer
import logging
from typing import Optional

# Add the project root directory to the Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)  # Go up one level to the project root
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import the CLI app after setting the correct path
from src.roman_senate.web.cli import app as websocket_app
from src.roman_senate.utils.logging_utils import setup_logging

# Set up logging
logger = None

@typer.callback()
def main(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Increase output verbosity"),
    log_level: str = typer.Option(None, "--log-level", help="Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"),
    log_file: str = typer.Option(None, "--log-file", help="Custom log file path")
):
    """
    Roman Senate Websocket Server - Stream simulation events via websockets
    """
    global logger
    
    # Set up logging early
    logger = setup_logging(log_level=log_level, log_file=log_file, verbose=verbose)
    
    # Log application startup
    logger.info("Roman Senate Websocket Server starting")
    
    # Display version info and environment
    typer.echo(typer.style("Roman Senate Websocket Server", fg="cyan", bold=True))
    
    # Ensure correct working directory
    ensure_correct_path()

def ensure_correct_path():
    """Ensure the script runs from the correct directory."""
    # Ensure logger is initialized
    global logger
    if logger is None:
        from src.roman_senate.utils.logging_utils import setup_logging
        logger = setup_logging()
        
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    if os.getcwd() != script_dir:
        os.chdir(script_dir)
        logger.debug(f"Changed working directory to: {script_dir}")
    
    # Add the project root directory to Python path
    project_root = os.path.dirname(script_dir)  # Go up one level to the project root
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
        logger.debug(f"Added {project_root} to Python path")

# Add the websocket app commands to this app
app = typer.Typer()
app.add_typer(websocket_app, name="server")

@app.command()
def run(
    host: str = typer.Option("0.0.0.0", help="Host to bind the server to"),
    port: int = typer.Option(8000, help="Port to bind the server to"),
    senators: int = typer.Option(10, help="Number of senators to simulate"),
    debate_rounds: int = typer.Option(3, help="Number of debate rounds per topic"),
    topics: int = typer.Option(3, help="Number of topics to debate"),
    year: int = typer.Option(-100, help="Year in Roman history (negative for BCE)"),
    provider: str = typer.Option("mock", help="LLM provider (mock, openai, ollama)"),
    model: Optional[str] = typer.Option(None, help="LLM model name"),
    auto_start: bool = typer.Option(False, help="Automatically start a simulation when the server starts")
):
    """
    Run the Roman Senate websocket server.
    
    This command starts a FastAPI server with websocket endpoints for streaming
    Roman Senate simulation events.
    """
    try:
        # Import the run function from the web CLI
        from src.roman_senate.web.cli import run as run_server
        
        # Run the server
        run_server(
            host=host,
            port=port,
            senators=senators,
            debate_rounds=debate_rounds,
            topics=topics,
            year=year,
            provider=provider,
            model=model,
            auto_start=auto_start
        )
    except Exception as e:
        error_msg = f"Fatal server error: {str(e)}"
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
        
        typer.echo("\nServer terminated. Type 'python run_websocket_server.py run' to try again.\n")

if __name__ == "__main__":
    app()