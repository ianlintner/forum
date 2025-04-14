"""Utility functions for the Roman Senate game."""

from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn, TextColumn
from typing import Optional

# Initialize console
console = Console()

def score_argument(argument: str, topic: str) -> dict:
    """
    Score a senator's argument based on various criteria.
    Returns a dictionary with individual scores and total.
    """
    # Basic scoring implementation
    scores = {
        "relevance": 0.8,
        "persuasiveness": 0.7,
        "historical_accuracy": 0.9,
        "eloquence": 0.75,
        "total": 0.0
    }
    
    # Calculate total (average of individual scores)
    scores["total"] = sum(v for k, v in scores.items() if k != "total") / 4
    return scores

def format_text(text: str, as_panel: bool = False, title: str = None) -> None:
    """Format and display text, optionally as a panel."""
    if as_panel:
        console.print(Panel(text, title=title))
    else:
        console.print(text)

def display_message(message: str, elapsed: Optional[float] = None):
    """Display a message with optional elapsed time."""
    if elapsed is not None:
        console.print(f"[cyan]{message} ({elapsed:.2f}s)[/cyan]")
    else:
        console.print(f"[cyan]{message}[/cyan]")

def display_error(message: str):
    """Display an error message in a panel."""
    console.print(Panel(f"[red]Error: {message}[/red]", border_style="red"))

def display_progress(message: str, elapsed: Optional[float] = None):
    """Display progress message with optional elapsed time."""
    if elapsed is not None:
        console.print(f"[cyan]{message} ({elapsed:.2f}s)[/cyan]")
    else:
        console.print(f"[cyan]{message}[/cyan]")
