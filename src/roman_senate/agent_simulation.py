"""
Roman Senate AI Game
Unified Simulation

This module serves as the main entry point for running simulations
of the Roman Senate, combining agent-driven logic with rich traditional display.
"""

import asyncio
from typing import Dict, List, Optional
from rich.console import Console
from rich.panel import Panel

from .core.game_state import game_state
from .core import senators as senators_module
from .core import topic_generator, vote
from .utils.llm.factory import get_llm_provider
from .agents.environment import SenateEnvironment
from .core.senate_session import SenateSession

console = Console()

async def run_simulation(
    senators_count: int = 10,
    debate_rounds: int = 3,
    topics_count: int = 3,
    year: int = -100,
    provider: str = None,
    model: str = None
) -> List[Dict]:
    """
    Run a simulation of the Roman Senate with agent-driven logic and traditional display.
    
    Args:
        senators_count: Number of senators to simulate
        debate_rounds: Number of debate rounds per topic
        topics_count: Number of topics to debate
        year: Year in Roman history (negative for BCE)
        provider: LLM provider to use (defaults to config)
        model: LLM model to use (defaults to config)
        
    Returns:
        List of results for each topic, including debates and votes
    """
    try:
        # 1. Reset game state
        game_state.reset()
        game_state.year = year
        
        # 2. Get LLM provider
        # Handle None provider by not passing it to avoid NoneType error
        if provider is None:
            llm_provider = get_llm_provider(model_name=model)
        else:
            llm_provider = get_llm_provider(provider_type=provider, model_name=model)
        
        # Display provider info (get provider type from class name to avoid attribute errors)
        provider_type = llm_provider.__class__.__name__.replace('Provider', '')
        model_info = getattr(llm_provider, 'model_name', 'default model')
        console.print(f"\n[bold green]✓[/] LLM integration is working. Using provider: [bold cyan]{provider_type}[/] with model: [bold cyan]{model_info}[/]")
        
        # 3. Display welcome banner
        console.print(
            "\n[bold cyan]ROMAN SENATE SIMULATION[/]\n"
            f"[bold]Year:[/] {abs(year)} BCE\n"
            f"[bold]Senators:[/] {senators_count}\n"
            f"[bold]Topics:[/] {topics_count}\n"
            f"[bold]Debate Rounds:[/] {debate_rounds} per topic\n"
        )
        
        # 4. Initialize senators
        console.print("\n[bold cyan]Initializing the Senate...[/]")
        senate_members = senators_module.initialize_senate(senators_count)
        game_state.senators = senate_members
        
        # Display senators info if desired (optional)
        if senators_count <= 15:  # Only show details for smaller senates
            senators_module.display_senators_info(senate_members)
        
        # Get historical context for the selected year
        historical_context = topic_generator.get_historical_period_context(year)
        console.print(Panel(historical_context, title=f"Historical Context for {abs(year)} BCE", border_style="blue", width=100))
        
        # 5. Generate topics for the session
        console.print("\n[bold cyan]Generating debate topics...[/]")
        topics_by_category = await topic_generator.get_topics_for_year(year, topics_count)
        flattened_topics = topic_generator.flatten_topics_by_category(topics_by_category)
        
        # Select topics for this session
        selected_topics = []
        for i in range(min(topics_count, len(flattened_topics))):
            if i < len(flattened_topics):
                topic_obj = flattened_topics[i]
                selected_topics.append((topic_obj['text'], topic_obj['category']))
        
        # Setup traditional senate session for formatting
        console.print("\n[bold cyan]Initializing Senate Session...[/]")
        session = SenateSession(senate_members, year, game_state, test_mode=False)
        
        # Take attendance (traditional feature)
        console.print("\n[bold cyan]Taking attendance...[/]")
        session.conduct_attendance_and_seating()
        
        # Introduce agenda (traditional feature)
        console.print("\n[bold cyan]Introducing agenda...[/]")
        session.introduce_agenda(selected_topics)
        
        # 6. Create and run the senate environment simulation with agent-driven logic
        console.print("\n[bold cyan]Beginning debates and votes...[/]")
        environment = SenateEnvironment(llm_provider)
        results = await environment.run_simulation(
            senators=session.attending_senators,  # Use the attending senators from the session
            topics=selected_topics,
            debate_rounds=debate_rounds,
            year=year
        )
        
        # 7. Display completion message and voting summary
        console.print("\n[bold green]Simulation completed successfully![/]")
        console.print(f"Simulated {len(results)} topics with {len(session.attending_senators)} senator agents in the year {abs(year)} BCE.")
        
        # Display vote summary for each topic (traditional formatting)
        for result in results:
            vote.display_vote_result(result['vote_result'])
        
        # Conclude the session (traditional feature)
        session.conclude_session(results)
        
        return results
        
    except Exception as e:
        console.print(f"\n[bold red]Error during simulation:[/] {str(e)}")
        import traceback
        console.print(traceback.format_exc())
        raise