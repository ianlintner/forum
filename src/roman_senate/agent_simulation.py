"""
Roman Senate AI Game
Agent-Driven Simulation

This module serves as the main entry point for running agent-based simulations
of the Roman Senate, where senators behave as autonomous agents.
"""

import asyncio
from typing import Dict, List, Optional
from rich.console import Console

from .core.game_state import game_state
from .core import senators as senators_module
from .core import topic_generator
from .utils.llm.factory import get_llm_provider
from .agents.environment import SenateEnvironment

console = Console()

async def run_agent_simulation(
    senators_count: int = 10,
    debate_rounds: int = 3,
    topics_count: int = 3,
    year: int = -100,
    provider: str = None,
    model: str = None
) -> List[Dict]:
    """
    Run an agent-driven simulation of the Roman Senate.
    
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
        console.print(f"\n[bold green]✓[/] LLM integration is working. Using provider: [bold cyan]{llm_provider.provider_name}[/]")
        
        # 3. Display welcome banner
        console.print(
            "\n[bold cyan]ROMAN SENATE AGENT SIMULATION[/]\n"
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
        
        # 5. Generate topics for the session
        console.print("\n[bold cyan]Generating debate topics...[/]")
        topics_by_category = await topic_generator.get_topics_for_year(year, topics_count)
        flattened_topics = topic_generator.flatten_topics_by_category(topics_by_category)
        
        # Select topics for this session
        selected_topics = []
        for i in range(min(topics_count, len(flattened_topics))):
            if i < len(flattened_topics):
                selected_topics.append(flattened_topics[i])
        
        # 6. Create and run the senate environment simulation
        console.print("\n[bold cyan]Initializing agent-driven simulation...[/]")
        environment = SenateEnvironment(llm_provider)
        results = await environment.run_simulation(
            senators=senate_members,
            topics=selected_topics,
            debate_rounds=debate_rounds,
            year=year
        )
        
        # 7. Display completion message
        console.print("\n[bold green]Agent simulation completed successfully![/]")
        console.print(f"Simulated {len(results)} topics with {senators_count} senator agents in the year {abs(year)} BCE.")
        
        return results
        
    except Exception as e:
        console.print(f"\n[bold red]Error during agent simulation:[/] {str(e)}")
        import traceback
        console.print(traceback.format_exc())
        raise