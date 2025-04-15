#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Roman Senate Game
Vote Module

This module handles the voting procedures of the Roman Senate simulation,
including vote collection, tallying, and results analysis.
"""

import random
import asyncio
import time
from typing import Dict, List, Optional, Any
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.panel import Panel


from .debate import get_historical_context

console = Console()


async def conduct_vote(topic: str, senators_list: List[Dict], debate_summary=None, topic_category: str = None):
    """
    Conduct a vote on the given topic after debate.
    
    Args:
        topic (str): The topic to vote on
        senators_list (List[Dict]): List of senators participating
        debate_summary: Summary of the debate results
        topic_category (str, optional): Category of the topic (e.g., Military funding)
        
    Returns:
        Dict: Vote results including counts, outcome, and voting record
    """
    # Handle case where topic might be None
    topic_display = topic if topic else "Unknown Topic"
    
    # Create a more informative vote introduction
    if topic_category:
        introduction = f"The Senate will now vote on a matter of [bold yellow]{topic_category}[/]:\n[italic]{topic_display}[/]"
    else:
        introduction = f"The Senate will now vote on:\n[italic]{topic_display}[/]"
    
    # Display the vote panel with category context
    console.print(Panel(introduction, title="[bold magenta]SENATE VOTE BEGINS[/]", border_style="magenta", width=100))

    votes = {"for": 0, "against": 0, "abstain": 0}
    voting_record = []
    
    # Create a map of senator names to their debate stance
    debate_stances = {}
    if debate_summary:
        # Group by senator name and take the last stance (most recent)
        senator_speeches = {}
        
        for speech in debate_summary:
            try:
                senator_name = speech.get("senator_name")
                if senator_name:
                    senator_speeches[senator_name] = speech
                else:
                    console.print(f"[bold yellow]Warning: Missing senator_name in speech[/]")
            except Exception as e:
                console.print(f"[bold yellow]Warning: Error processing speech: {e}[/]")
                continue
        
        for senator_name, speech in senator_speeches.items():
            try:
                debate_stances[senator_name] = speech.get("stance", "neutral")
            except Exception as e:
                console.print(f"[bold yellow]Warning: Error recording stance for {senator_name}: {e}[/]")
                debate_stances[senator_name] = "neutral"  # Fallback to neutral
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold]Senators are casting their votes...[/]"),
        console=console,
    ) as progress:
        task = progress.add_task("Voting...", total=len(senators_list))

        # Create tasks for parallel vote processing
        vote_tasks = []
        for senator in senators_list:
            # Pass the senator's debate stance if available
            stance = debate_stances.get(senator["name"], None)
            # Create coroutine for each senator's vote
            vote_tasks.append(asyncio.create_task(process_senator_vote_async(senator, votes, voting_record, stance)))
            progress.update(task, advance=1)
            await asyncio.sleep(0.1)  # Small delay for visual effect

        # Wait for all votes to be processed
        await asyncio.gather(*vote_tasks)

    # Display voting results summary
    console.print("\n[bold yellow]Voting Results Summary:[/]")

    results_table = Table()
    results_table.add_column("Option", style="cyan")
    results_table.add_column("Votes", justify="right")
    results_table.add_column("Percentage", justify="right")

    total_votes = sum(votes.values())

    for option, count in votes.items():
        percentage = (count / total_votes) * 100 if total_votes > 0 else 0
        results_table.add_row(option.title(), str(count), f"{percentage:.1f}%")

    console.print(results_table)

    # Display detailed voting breakdown
    console.print("\n[bold yellow]Detailed Voting Breakdown:[/]")
    
    detailed_table = Table(title=f"Vote on: {topic}")
    detailed_table.add_column("Senator", style="cyan")
    detailed_table.add_column("Faction", style="magenta")
    detailed_table.add_column("Debate Stance", justify="center")
    detailed_table.add_column("Final Vote", justify="center")
    detailed_table.add_column("Swayed", justify="center")
    
    # Map stances to votes for comparison
    stance_to_vote = {
        "support": "for",
        "oppose": "against",
        "neutral": None  # Neutral could be any vote
    }
    
    # Sort voting record by faction then senator name
    sorted_record = sorted(voting_record, key=lambda x: (x["faction"], x["senator"]))
    
    for record in sorted_record:
        senator_name = record["senator"]
        stance = debate_stances.get(senator_name, "unknown")
        vote = record["vote"]
        
        # Determine if senator was swayed
        expected_vote = stance_to_vote.get(stance, None)
        swayed = ""
        
        if expected_vote and vote != expected_vote:
            swayed = "[bold yellow]*[/]"
        elif stance == "neutral" and vote != "abstain":
            swayed = "[bold blue]†[/]"
            
        # Format the stance and vote with colors
        stance_format = {
            "support": "[green]Support[/]",
            "oppose": "[red]Oppose[/]",
            "neutral": "[yellow]Neutral[/]",
            "unknown": "[dim]Unknown[/]"
        }
        
        vote_format = {
            "for": "[green]For[/]",
            "against": "[red]Against[/]",
            "abstain": "[yellow]Abstain[/]"
        }
        
        detailed_table.add_row(
            record["senator"],
            record["faction"],
            stance_format.get(stance, f"[dim]{stance}[/]"),
            vote_format.get(vote, f"[dim]{vote}[/]"),
            swayed
        )
    
    console.print(detailed_table)
    console.print("[bold yellow]*[/] Senator voted differently than their debate stance")
    console.print("[bold blue]†[/] Senator with neutral stance made a definitive vote")

    # Determine outcome
    if votes["for"] > votes["against"]:
        outcome = "PASSED"
        style = "bold green"
    elif votes["for"] < votes["against"]:
        outcome = "REJECTED"
        style = "bold red"
    else:
        # In case of a tie, the consul decides (Presiding officer)
        outcome = "TIE - CONSUL DECIDES"
        console.print(f"\n[bold yellow]{outcome}[/]")
        time.sleep(1)  # Dramatic pause
        
        # Randomly decide for demonstration purposes 
        # In a real implementation this could involve the presiding official
        outcome = random.choice(["PASSED", "REJECTED"])
        style = "bold green" if outcome == "PASSED" else "bold red"

    console.print(f"\nThe motion has been [bold {style}]{outcome}[/].\n")

    # Return result
    result = {
        "topic": topic,
        "category": topic_category,
        "votes": votes,
        "outcome": outcome,
        "voting_record": voting_record,
        "debate_stances": debate_stances
    }
    
    return result


async def process_senator_vote_async(senator, votes, voting_record, debate_stance=None):
    """
    Asynchronous helper function to process a senator's vote.
    
    Args:
        senator: Senator information
        votes: Counter to update with vote
        voting_record: List to append vote details
        debate_stance: Optional stance from debate ("support", "oppose", "neutral")
    """
    vote_options = ["for", "against", "abstain"]
    weights = [0.5, 0.4, 0.1]  # Default weights
    
    # Modify weights based on faction
    if senator["faction"] == "Optimates":
        weights = [0.4, 0.5, 0.1]  # More conservative
    elif senator["faction"] == "Populares":
        weights = [0.6, 0.3, 0.1]  # More progressive
    elif senator["faction"] == "Military":
        weights = [0.5, 0.4, 0.1]  # Balanced
    elif senator["faction"] == "Religious":
        weights = [0.4, 0.4, 0.2]  # More likely to abstain
    elif senator["faction"] == "Merchant":
        weights = [0.6, 0.3, 0.1]  # Pro-commercial interests
    
    # Factor in debate stance if available
    if debate_stance:
        # Strongly influence vote by debate stance (80% correlation)
        if debate_stance == "support":
            weights = [0.8, 0.15, 0.05]  # Heavily favor "for" vote
        elif debate_stance == "oppose":
            weights = [0.15, 0.8, 0.05]  # Heavily favor "against" vote
        elif debate_stance == "neutral":
            weights = [0.45, 0.45, 0.1]  # More balanced between for/against
            
        # Modify a bit based on faction and loyalty
        # Handle potential None values for traits
        traits = senator.get("traits", {}) or {}
        loyalty = traits.get("loyalty", 0.7)
        
        if debate_stance == "support" and senator["faction"] == "Optimates":
            # Optimates slightly more likely to deviate from support
            weights[0] -= (1 - loyalty) * 0.2
            weights[1] += (1 - loyalty) * 0.2
        elif debate_stance == "oppose" and senator["faction"] == "Populares":
            # Populares slightly more likely to deviate from opposition
            weights[0] += (1 - loyalty) * 0.2
            weights[1] -= (1 - loyalty) * 0.2
    
    # Simulate vote deliberation time
    await asyncio.sleep(random.uniform(0.1, 0.3))
    
    # Ensure weights are positive
    weights = [max(0.01, weight) for weight in weights]
    
    # Use random.choices for weighted random selection
    vote = random.choices(vote_options, weights=weights)[0]
    votes[vote] += 1
    
    # Add to voting record with safe access to influence (default to median if missing)
    voting_record.append(
        {
            "senator": senator["name"],
            "faction": senator["faction"],
            "vote": vote,
            "influence": senator.get("influence", 5),  # Default to median influence
            "debate_stance": debate_stance
        }
    )
    
    return vote


def analyze_vote_patterns(vote_results: Dict) -> Dict:
    """
    Analyze voting patterns based on faction, influence, etc.
    
    Args:
        vote_results: Vote results from conduct_vote
        
    Returns:
        Dict: Analysis of voting patterns
    """
    voting_record = vote_results.get("voting_record", [])
    
    # Skip analysis if no voting record
    if not voting_record:
        return {"analysis": "No voting records to analyze"}
    
    # Faction analysis
    faction_votes = {}
    
    for record in voting_record:
        faction = record["faction"]
        vote = record["vote"]
        
        if faction not in faction_votes:
            faction_votes[faction] = {"for": 0, "against": 0, "abstain": 0, "total": 0}
        
        faction_votes[faction][vote] += 1
        faction_votes[faction]["total"] += 1
    
    # Calculate faction cohesion (what percentage voted the same way)
    faction_cohesion = {}
    for faction, votes in faction_votes.items():
        if votes["total"] > 0:
            max_vote = max(votes["for"], votes["against"], votes["abstain"])
            cohesion = max_vote / votes["total"]
            faction_cohesion[faction] = cohesion
    
    # Influence analysis - do high influence senators sway the vote?
    influence_votes = {"high": {"for": 0, "against": 0}, "low": {"for": 0, "against": 0}}
    
    for record in voting_record:
        influence = record.get("influence", 5)
        vote = record["vote"]
        
        if vote == "abstain":
            continue
            
        if influence >= 7:  # High influence threshold
            influence_votes["high"][vote] += 1
        elif influence <= 4:  # Low influence threshold
            influence_votes["low"][vote] += 1
    
    # Match between debate stance and vote
    debate_match = {"matched": 0, "changed": 0, "neutral_decided": 0}
    
    for record in voting_record:
        stance = record.get("debate_stance")
        vote = record["vote"]
        
        if not stance:
            continue
            
        if stance == "support" and vote == "for":
            debate_match["matched"] += 1
        elif stance == "oppose" and vote == "against":
            debate_match["matched"] += 1
        elif stance == "neutral" and vote != "abstain":
            debate_match["neutral_decided"] += 1
        elif (stance == "support" and vote == "against") or (stance == "oppose" and vote == "for"):
            debate_match["changed"] += 1
    
    # Return the analysis
    return {
        "faction_votes": faction_votes,
        "faction_cohesion": faction_cohesion,
        "influence_analysis": influence_votes,
        "debate_to_vote": debate_match
    }


def display_vote_result(vote_result: Dict):
    """
    Display a formatted version of vote results.
    
    Args:
        vote_result: Vote results dictionary
    """
    topic = vote_result.get("topic", "Unknown Topic")
    category = vote_result.get("category", "")
    votes = vote_result.get("votes", {})
    outcome = vote_result.get("outcome", "UNKNOWN")
    
    # Title with category if available
    title = f"Vote on: {topic}"
    if category:
        title = f"Vote on {category}: {topic}"
        
    # Create results table
    table = Table(title=title)
    table.add_column("Option", style="cyan")
    table.add_column("Votes", justify="right")
    table.add_column("Percentage", justify="right")
    
    total_votes = sum(votes.values())
    
    for option, count in votes.items():
        percentage = (count / total_votes) * 100 if total_votes > 0 else 0
        table.add_row(option.title(), str(count), f"{percentage:.1f}%")
    
    # Add outcome row with appropriate styling
    outcome_style = "green" if outcome == "PASSED" else "red"
    
    console.print(table)
    console.print(f"\nResult: [bold {outcome_style}]{outcome}[/]")