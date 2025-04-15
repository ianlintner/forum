#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Roman Senate Game
Senate Session Module

This module orchestrates a complete Roman Senate session with historically accurate phases
including attendance, agenda introduction, debate, voting, and adjournment.
"""

import random
import asyncio
import time
from typing import List, Dict, Optional, Tuple, Any
from rich.panel import Panel
from rich.console import Console
from rich.text import Text
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm

from . import senators, debate, vote, topic_generator
from .game_state import game_state

# Initialize console
console = Console()


class SenateSession:
    """
    Orchestrates a complete Roman Senate session with all historical phases.
    
    Includes:
    - Attendance and seating by rank
    - Introduction of agenda (relatio)
    - Debate on topics
    - Voting and decisions
    - Session adjournment
    """
    
    def __init__(self, senators_list: List[Dict], year: int, game_state: Any):
        """
        Initialize a new Senate session.
        
        Args:
            senators_list: List of senator dictionaries with their attributes
            year: Current year in the game (negative for BCE)
            game_state: The global game state object
        """
        self.senators = senators_list
        self.year = year
        self.game_state = game_state
        self.year_display = f"{abs(year)} BCE"
        self.presiding_magistrate = self._select_presiding_magistrate()
        self.attending_senators = []
        self.session_log = []
        self.topics = []
        
        # Determine the meeting location based on year
        if self.year < -100:  # Before 100 BCE
            self.meeting_location = "Curia Hostilia"
        else:
            self.meeting_location = "Curia Cornelia"
            
        # Random session details
        self.auspices_favorable = random.random() > 0.1  # Usually favorable
        
    def _select_presiding_magistrate(self) -> Dict:
        """Select the presiding magistrate for the session based on historical protocols."""
        # In the Roman Republic, sessions were typically presided over by Consuls or Praetors
        
        # Get the most influential senator to be the consul
        consul = max(self.senators, key=lambda s: s.get("influence", 0))
        
        # Create the presiding magistrate record
        magistrate = {
            "name": consul["name"],
            "title": "Consul" if random.random() < 0.7 else "Praetor",
            "faction": consul["faction"],
            "senator_id": consul.get("id", 0)
        }
        
        # Remove them from regular senators to avoid duplication
        self.senators = [s for s in self.senators if s.get("id") != magistrate["senator_id"]]
        
        return magistrate
    
    def _log_event(self, event_type: str, details: str) -> None:
        """Log a session event for record-keeping."""
        self.session_log.append({
            "type": event_type,
            "details": details,
            "timestamp": time.time()
        })
    
    def conduct_attendance_and_seating(self) -> None:
        """
        Conduct attendance and seating arrangements according to Roman tradition.
        
        In the Roman Senate, seating was arranged according to rank and status,
        with former magistrates (especially former consuls) seated in the front rows.
        """
        console.print("\n[bold yellow]ATTENDANCE AND SEATING ARRANGEMENTS[/]")
        
        # Create a copy of senators for attendance
        all_senators = [self.presiding_magistrate] + self.senators
        
        # Sort senators by influence (proxy for rank)
        sorted_senators = sorted(all_senators, key=lambda s: s.get("influence", 0), reverse=True)
        
        # Determine attendance
        # Historically, attendance could be spotty depending on the time of year and topics
        attendance_rate = random.uniform(0.75, 0.95)  # 75-95% attendance
        
        # Determine which senators are present
        for senator in sorted_senators:
            # Higher influence (rank) senators more likely to attend
            attendance_chance = min(0.95, attendance_rate + (senator.get("influence", 5) / 20))
            
            if random.random() < attendance_chance:
                # Senator is present
                self.attending_senators.append(senator)
        
        # Display attendance information
        console.print(f"[bold cyan]Total Senators:[/] {len(all_senators)}")
        console.print(f"[bold cyan]Senators Present:[/] {len(self.attending_senators)} ({int(len(self.attending_senators)/len(all_senators)*100)}% attendance)")
        
        # Create seating chart table
        seating_table = Table(title=f"Senate Seating Arrangement - {self.meeting_location}")
        seating_table.add_column("Rank", style="yellow")
        seating_table.add_column("Name", style="cyan")
        seating_table.add_column("Faction", style="magenta")
        seating_table.add_column("Status", style="green")
        
        # Add seating rows by rank
        rank_names = ["Consul/Presiding Officer", "Former Consuls", "Praetors", "Aediles", "Tribunes", "Quaestors", "Regular Senators"]
        
        # Track which senators have been listed
        listed_senators = set()
        
        # Generate seating assignments
        for rank in rank_names:
            # For presiding officer
            if rank == "Consul/Presiding Officer":
                seating_table.add_row(
                    rank,
                    f"{self.presiding_magistrate['title']} {self.presiding_magistrate['name']}",
                    self.presiding_magistrate['faction'],
                    "[bold green]PRESENT - PRESIDING[/]"
                )
                listed_senators.add(self.presiding_magistrate.get("senator_id", 0))
                continue
            
            # For other ranks, select based on influence ranges
            if rank == "Former Consuls":
                influence_min = 8
            elif rank == "Praetors":
                influence_min = 7
            elif rank == "Aediles":
                influence_min = 6
            elif rank == "Tribunes":
                influence_min = 5
            elif rank == "Quaestors":
                influence_min = 4
            else:  # Regular Senators
                influence_min = 0
            
            # Get senators of this rank who are attending
            rank_senators = [s for s in self.attending_senators 
                              if s.get("influence", 0) >= influence_min 
                              and s.get("senator_id", 0) not in listed_senators]
            
            # If no senators of this rank, skip
            if not rank_senators:
                continue
                
            # Add the senators of this rank
            for i, senator in enumerate(rank_senators):
                status = "[bold green]PRESENT[/]"
                
                seating_table.add_row(
                    rank if i == 0 else "",  # Only show rank on first row
                    senator["name"],
                    senator["faction"],
                    status
                )
                listed_senators.add(senator.get("senator_id", 0))
        
        # Display the seating arrangement
        console.print(seating_table)
        
        # Log the attendance
        self._log_event("Attendance", f"{len(self.attending_senators)} senators present out of {len(all_senators)}")
        
        console.print("\n[bold green]✓[/] Attendance has been taken and senators have been seated according to rank.")
    
    def introduce_agenda(self, topics: List[Tuple[str, str]]) -> None:
        """
        Formally introduce the day's agenda (relatio) to the Senate.
        
        Args:
            topics: List of (topic, category) tuples to be discussed
        """
        self.topics = topics
        
        console.print("\n[bold yellow]INTRODUCTION OF AGENDA (RELATIO)[/]")
        
        # Create agenda table
        agenda_table = Table(title=f"Senate Agenda - {self.year_display}")
        agenda_table.add_column("#", style="dim")
        agenda_table.add_column("Category", style="yellow")
        agenda_table.add_column("Issue", style="cyan")
        
        for i, (topic, category) in enumerate(topics, 1):
            agenda_table.add_row(str(i), category, topic)
        
        # Display the agenda
        console.print(agenda_table)
        
        # Presiding magistrate introduces the agenda
        magistrate = self.presiding_magistrate
        
        intro_text = f"""
        [bold]{magistrate['title']} {magistrate['name']}[/] addresses the Senate:
        
        [italic]"Patres conscripti, I have summoned you on this day to deliberate on matters 
        of great importance to the Republic. The auspices have been taken and the gods favor 
        our assembly{" despite concerning signs" if not self.auspices_favorable else ""}. 
        
        Today we shall address {len(topics)} matter{"s" if len(topics) > 1 else ""} of state. 
        Let us proceed with wisdom and in accordance with the mos maiorum."[/]
        """
        
        console.print(Panel(intro_text, border_style="blue", width=100))
        
        # Log agenda introduction
        self._log_event("Agenda Introduction", f"Introduced {len(topics)} topics for deliberation")
        
        console.print("\n[bold green]✓[/] The agenda has been formally introduced to the Senate.")
    
    async def run_full_session(self, topics: List[Tuple[str, str]], debate_rounds: int = 3) -> List[Dict]:
        """
        Run a complete Senate session through all phases in sequence.
        
        Args:
            topics: List of (topic, category) tuples to be discussed
            debate_rounds: Number of rounds for each debate topic
            
        Returns:
            List of results for each topic
        """
        console.print(Panel(
            "[bold yellow]SENATE SESSION BEGINS[/]",
            border_style="yellow",
            width=100
        ))
        
        # Take attendance and arrange seating
        self.conduct_attendance_and_seating()
        
        # Introduce the agenda
        self.introduce_agenda(topics)
        
        # Process each topic in sequence
        results = []
        for i, (topic, category) in enumerate(topics, 1):
            console.print(f"\n[bold yellow]TOPIC {i} OF {len(topics)}[/]")
            
            # Conduct debate on this topic
            debate_summary = await debate.conduct_debate(
                topic,
                self.attending_senators,
                rounds=debate_rounds,
                topic_category=category,
                year=self.year
            )
            
            # Conduct vote on this topic
            vote_result = await vote.conduct_vote(topic, self.attending_senators, debate_summary, topic_category=category)
            
            # Store the result
            result = {
                "topic": topic,
                "category": category,
                "debate_summary": debate_summary,
                "vote_result": vote_result
            }
            results.append(result)
            
            # Log the result
            self._log_event("Topic Completed", f"Topic: {topic}, Result: {vote_result['outcome']}")
            
            # If not the last topic, ask to continue
            if i < len(topics):
                console.print()
                continue_session = Confirm.ask("Continue to the next topic?", default=True)
                if not continue_session:
                    # End the session early
                    console.print("[yellow]The Senate adjourns early at the discretion of the presiding magistrate.[/]")
                    break
        
        # Conclude the session formally
        self.conclude_session(results)
        
        return results
    
    def conclude_session(self, results: List[Dict]) -> None:
        """
        Conduct the formal adjournment of the Senate session.
        
        Args:
            results: Results of the deliberations
        """
        console.print("\n[bold yellow]SENATE SESSION CONCLUSION[/]")
        
        # Create summary table of results
        summary_table = Table(title=f"Senate Session Summary - {self.year_display}")
        summary_table.add_column("Topic", style="cyan")
        summary_table.add_column("Category", style="yellow")
        summary_table.add_column("Result", style="green")
        
        for result in results:
            topic = result["topic"]
            category = result["category"]
            outcome = result["vote_result"]["outcome"]
            
            # Determine result style
            result_style = "green" if outcome == "PASSED" else "red"
            
            summary_table.add_row(
                topic,
                category,
                f"[bold {result_style}]{outcome}[/]"
            )
        
        # Display the summary
        console.print(summary_table)
        
        # Formal adjournment speech
        adjournment_text = f"""
        [bold]{self.presiding_magistrate['title']} {self.presiding_magistrate['name']}[/] rises to conclude the session:
        
        [italic]"Patres conscripti, we have completed our deliberations for this day. The Senate has
        expressed its will on {len(results)} matter{"s" if len(results) > 1 else ""} of state. The scribes have
        recorded our decisions, which shall be published in the acta diurna.
        
        If there is no other business, I declare this session of the Senate adjourned.
        
        May the gods continue to favor Rome."[/]
        """
        
        console.print(Panel(adjournment_text, border_style="blue", width=100))
        
        # Calculate session duration
        if self.session_log:
            start_time = self.session_log[0]["timestamp"]
            end_time = time.time()
            duration_mins = (end_time - start_time) / 60
            console.print(f"\n[bold cyan]Session Duration:[/] {duration_mins:.1f} minutes")
        
        # Log session conclusion
        self._log_event("Session Concluded", f"Completed with {len(results)} topics decided")
        
        console.print(Panel(
            "[bold yellow]SENATE SESSION CONCLUDED[/]",
            border_style="yellow",
            width=100
        ))


async def run_session(senators_count: int = 10, debate_rounds: int = 3, topics_count: int = 3, year: int = None) -> List[Dict]:
    """
    Run a complete senate session with the specified parameters.
    
    Args:
        senators_count: Number of senators to create
        debate_rounds: Number of debate rounds per topic
        topics_count: Number of topics to debate
        year: Year to set for the session (negative for BCE)
        
    Returns:
        List of results for all topics
    """
    # Reset game state
    game_state.reset()
    
    # Set default year if not provided (100 BCE)
    if year is None:
        year = -100
    
    game_state.year = year
    
    # Initialize senators
    senate_members = senators.initialize_senate(senators_count)
    game_state.senators = senate_members
    
    console.print(f"\n[bold cyan]Senate Session for Year: {abs(year)} BCE[/]")
    
    # Get historical context for the selected year
    historical_context = debate.get_historical_context(year)
    console.print(Panel(historical_context, title=f"Historical Context for {abs(year)} BCE", border_style="blue", width=100))
    
    # Generate topics for the session
    topics_by_category = await topic_generator.get_topics_for_year(year, topics_count + 2)  # Get a few extra for choice
    flattened_topics = topic_generator.flatten_topics_by_category(topics_by_category)
    
    # Select topics
    selected_topics = []
    for i in range(min(topics_count, len(flattened_topics))):
        if i < len(flattened_topics):
            topic_obj = flattened_topics[i]
            selected_topics.append((topic_obj['text'], topic_obj['category']))
    
    # Create and run session
    session = SenateSession(senate_members, year, game_state)
    results = await session.run_full_session(selected_topics, debate_rounds)
    
    # Add results to game state
    for result in results:
        game_state.add_topic_result(result['topic'], result['vote_result'])
    
    # Display summary
    display_session_summary(results)
    
    return results


def display_session_summary(results: List[Dict]):
    """Display a summary of the entire senate session."""
    if not results:
        console.print("\n[bold yellow]No topics were debated in this session.[/]")
        return
    
    table = Table(title="Session Summary", show_header=True)
    table.add_column("Topic", style="cyan")
    table.add_column("For", justify="right")
    table.add_column("Against", justify="right")
    table.add_column("Abstain", justify="right")
    table.add_column("Result", style="green")
    
    for result in results:
        votes = result['vote_result']['votes']
        outcome = result['vote_result']['outcome']
        outcome_style = "green" if outcome == "PASSED" else "red"
        
        table.add_row(
            result['topic'],
            str(votes.get('for', 0)),
            str(votes.get('against', 0)),
            str(votes.get('abstain', 0)),
            f"[bold {outcome_style}]{outcome}[/]"
        )
    
    console.print("\n")
    console.print(Panel("SENATE SESSION CONCLUDED", style="bold cyan"))
    console.print(table)
    console.print("\nGame session complete!\n")