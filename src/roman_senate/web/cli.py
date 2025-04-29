"""
Roman Senate Web Server CLI

This module provides CLI commands for running the Roman Senate websocket server.
"""

import asyncio
import logging
import typer
from typing import Optional

from ..core.events.event_bus import EventBus
from .server import run_server
from .integration import setup_event_bridge

# Set up logging
logger = logging.getLogger(__name__)

# Create a Typer app
app = typer.Typer(help="Roman Senate Web Server CLI")


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
    from rich.console import Console
    console = Console()
    
    console.print("[bold cyan]Roman Senate Web Server[/]")
    console.print(f"[dim]Server running at http://{host}:{port}[/]")
    console.print(f"[dim]WebSocket endpoint at ws://{host}:{port}/ws[/]")
    
    # Create an event bus
    event_bus = EventBus()
    
    # Set up the event bridge
    setup_event_bridge(event_bus)
    
    # Auto-start a simulation if requested
    if auto_start:
        console.print("[bold green]Auto-starting simulation...[/]")
        
        # Import the simulation function
        from ..cli import run_framework_simulation
        
        # Create a background task to run the simulation
        async def start_simulation():
            # Wait a moment for the server to start
            await asyncio.sleep(2)
            
            console.print("[bold green]Starting simulation...[/]")
            
            # Run the simulation
            await run_framework_simulation(
                senators=senators,
                debate_rounds=debate_rounds,
                topics=topics,
                year=year,
                provider=provider,
                model=model
            )
            
        # Create and start the task
        loop = asyncio.get_event_loop()
        loop.create_task(start_simulation())
    
    # Run the server
    run_server(host=host, port=port, event_bus=event_bus)


if __name__ == "__main__":
    app()