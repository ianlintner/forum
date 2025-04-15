#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Roman Senate AI Game
Player Game Loop Module

This module handles the main game loop for player interactions in the Senate game.
"""

import asyncio
import random
from typing import Dict, List, Optional, Tuple, Any
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

from ..core.game_state import game_state
from ..core import senators as senators_module
from ..core import topic_generator, senate_session, debate, vote
from ..core.roman_calendar import DateFormat
from .player import Player
from .player_manager import PlayerManager
from .player_ui import PlayerUI
from .player_actions import PlayerActions

console = Console()

class PlayerGameLoop:
    """Manages the game loop for player mode of the Senate game."""
    
    def __init__(self):
        """Initialize the player game loop."""
        self.player_manager = PlayerManager()
        self.player_ui = PlayerUI()
        self.player_actions = None
        self.senate_members = []
        self.topics = []
        self.year = -100  # Default to 100 BCE
        
    async def start_game(self, senators_count: int = 10, topics_count: int = 3, year: int = -100):
        """
        Start a new player game session.
        
        Args:
            senators_count: Number of NPC senators to create
            topics_count: Number of topics to debate
            year: Year to set for the session (negative for BCE)
        """
        # Display welcome screen
        self.player_ui.display_welcome()
        
        # Initialize game state
        game_state.reset()
        game_state.year = year
        self.year = year
        
        # Initialize Roman calendar
        game_state.initialize_calendar(year)
        
        # Character creation
        player = self.create_character()
        self.player_ui.set_player(player)
        self.player_actions = PlayerActions(player, self.player_ui)
        
        # Initialize senators (NPCs)
        console.print("\n[bold cyan]Initializing the Senate...[/]")
        self.senate_members = senators_module.initialize_senate(senators_count)
        game_state.senators = self.senate_members
        
        # Display senators info
        if senators_count <= 15:  # Only show details for smaller senates
            senators_module.display_senators_info(self.senate_members)
        
        # Generate topics for the session
        console.print("\n[bold cyan]Generating debate topics...[/]")
        topics_by_category = await topic_generator.get_topics_for_year(year, topics_count + 2)  # Get a few extra for choice
        flattened_topics = topic_generator.flatten_topics_by_category(topics_by_category)
        
        # Select topics
        selected_topics = []
        for i in range(min(topics_count, len(flattened_topics))):
            if i < len(flattened_topics):
                topic_obj = flattened_topics[i]
                selected_topics.append((topic_obj['text'], topic_obj['category']))
        
        self.topics = selected_topics
        
        # Display current calendar date
        current_date = game_state.get_formatted_date(DateFormat.ROMAN_FULL)
        modern_date = game_state.get_formatted_date(DateFormat.MODERN)
        console.print(f"\n[bold cyan]Current Date: {current_date}[/]")
        console.print(f"[italic]({modern_date})[/]")
        
        # Check for any special events for today
        special_events = game_state.calendar.get_special_events_for_current_day()
        if special_events:
            console.print("\n[bold yellow]Today's Events:[/]")
            for event in special_events:
                console.print(f"[bold]{event['name']}[/]: {event['description']}")
                
        # Check if senate can meet today
        can_meet, reason = game_state.can_hold_senate_session()
        if not can_meet:
            console.print(f"\n[bold red]WARNING:[/] {reason}")
            console.print("The Senate is convening despite traditional restrictions.")
        
        # Start the modified senate session with player participation
        console.print("\n[bold cyan]Beginning Senate session...[/]")
        await self.run_player_senate_session(player)

    def create_character(self) -> Player:
        """
        Guide the player through character creation.
        
        Returns:
            The created Player instance
        """
        # Get player name
        name = self.player_ui.prompt_for_name()
        
        # Choose faction
        faction = self.player_ui.prompt_for_faction()
        
        # Choose background
        ancestry, background = self.player_ui.prompt_for_background()
        
        # Determine starting attributes based on choices
        if ancestry == "Patrician":
            wealth = 150
            influence = 40
            reputation = 30
        else:  # Plebeian
            wealth = 80
            influence = 20
            reputation = 60
        
        # Military background adjustments
        if "Military" in background:
            influence += 5
            reputation += 5
            
        # Merchant background adjustments
        if "Merchant" in background:
            wealth += 20
            
        # Create character data for confirmation
        character_data = {
            "name": name,
            "faction": faction,
            "ancestry": ancestry,
            "background": background,
            "wealth": wealth,
            "influence": influence,
            "reputation": reputation
        }
        
        # Confirm character
        confirmed = self.player_ui.confirm_character(character_data)
        
        if not confirmed:
            # If not confirmed, restart character creation
            console.print("[yellow]Let's try again then...[/]")
            return self.create_character()
        
        # Create the player
        return self.player_manager.create_player(
            name=name,
            faction=faction,
            wealth=wealth,
            influence=influence,
            reputation=reputation,
            ancestry=ancestry,
            background=background
        )

    async def run_player_senate_session(self, player: Player):
        """
        Run a modified senate session with player participation.
        
        Args:
            player: The player character
        """
        # Create a modified senate session instance
        session = PlayerSenateSession(
            self.senate_members, 
            self.year, 
            game_state, 
            player,
            self.player_actions
        )
        
        # Run the session with player interaction
        results = await session.run_full_session(self.topics)
        
        # Add results to game state and auto-save after session
        from ..core.persistence import auto_save
        import os
        
        # Add each topic result to game state
        for result in results:
            game_state.add_topic_result(result['topic'], result['vote_result'])
            
            # Auto-save after each topic is processed
            if os.environ.get('ROMAN_SENATE_NO_AUTOSAVE') != 'true':
                try:
                    save_path = auto_save()
                    console.print(f"[dim]Game auto-saved to: {save_path}[/]")
                except Exception as e:
                    console.print(f"[dim]Auto-save failed: {str(e)}[/]")
        
        # Advance the calendar day after the session
        game_state.advance_day()
        new_date = game_state.get_formatted_date(DateFormat.ROMAN_FULL)
        new_modern_date = game_state.get_formatted_date(DateFormat.MODERN)
        console.print(f"\n[bold cyan]A new day begins: {new_date}[/]")
        console.print(f"[italic]({new_modern_date})[/]")
        
        # Check for any special events on the new day
        new_special_events = game_state.calendar.get_special_events_for_current_day()
        if new_special_events:
            console.print("\n[bold yellow]Upcoming Events:[/]")
            for event in new_special_events:
                console.print(f"[bold]{event['name']}[/]: {event['description']}")
        
        # Save the player state after the session
        self.player_manager.save_player()
        
        # Display session summary
        senate_session.display_session_summary(results)
        
        # Display player status
        self.player_ui.display_player_status()
        
        # Convert senator_id to full senator objects for relationship display
        senator_dict = {s.get("id", ""): s for s in self.senate_members}
        self.player_ui.display_relationship_status(senator_dict)
        
        console.print("\n[bold green]Senate session completed![/]")


class PlayerSenateSession(senate_session.SenateSession):
    """
    Extended senate session with player participation.
    """
    
    def __init__(
        self, 
        senators_list: List[Dict], 
        year: int, 
        game_state: Any, 
        player: Player,
        player_actions: PlayerActions
    ):
        """
        Initialize a player-enabled senate session.
        
        Args:
            senators_list: List of senator dictionaries with their attributes
            year: Current year in the game (negative for BCE)
            game_state: The global game state object
            player: The player character
            player_actions: The player actions handler
        """
        super().__init__(senators_list, year, game_state)
        self.player = player
        self.player_actions = player_actions
        
        # Add player to attending senators
        self.player_data = {
            "id": self.player.id,
            "name": self.player.name,
            "faction": self.player.faction,
            "influence": self.player.influence,
            "traits": {
                "eloquence": self.player.skills.get("oratory", 3) / 10,
                "corruption": 0.1,  # Low default corruption for player
                "loyalty": 0.8      # High default loyalty for player
            }
        }
        
    def conduct_attendance_and_seating(self) -> None:
        """
        Override to ensure player is always included in attendance.
        """
        console.print("\n[bold yellow]ATTENDANCE AND SEATING ARRANGEMENTS[/]")
        
        # Display current date in Roman style
        if hasattr(self.game_state, 'calendar') and self.game_state.calendar:
            roman_date = self.game_state.calendar.format_current_date(DateFormat.ROMAN_FULL)
            modern_date = self.game_state.calendar.format_current_date(DateFormat.MODERN)
            console.print(f"\n[bold cyan]Current Date: {roman_date}[/]")
            console.print(f"[italic]({modern_date})[/]")
            
            # Display any special events for today
            special_events = self.game_state.calendar.get_special_events_for_current_day()
            if special_events:
                for event in special_events:
                    console.print(f"[bold yellow]Today is {event['name']}[/]")
                    console.print(f"[italic]{event['description']}[/]")
                    
                    # Apply special event effects to attendance if needed
                    if "increased_attendance" in event.get("effects", []):
                        console.print("[green]The significance of this day has increased Senate attendance.[/]")
                    elif "decreased_attendance" in event.get("effects", []):
                        console.print("[yellow]Many senators are absent attending religious ceremonies.[/]")
        
        # Create a copy of senators for attendance
        all_senators = [self.presiding_magistrate] + self.senators
        
        # Sort senators by influence (proxy for rank)
        sorted_senators = sorted(all_senators, key=lambda s: s.get("influence", 0), reverse=True)
        
        # Determine attendance
        for senator in sorted_senators:
            # Higher influence (rank) senators more likely to attend
            attendance_chance = min(0.95, 0.75 + (senator.get("influence", 5) / 20))
            
            if random.random() < attendance_chance:
                # Senator is present
                self.attending_senators.append(senator)
        
        # Add player to attending senators (player is always present)
        # Find where to insert player based on influence
        player_inserted = False
        for i, senator in enumerate(self.attending_senators):
            if self.player.influence > senator.get("influence", 0):
                self.attending_senators.insert(i, self.player_data)
                player_inserted = True
                break
        
        if not player_inserted:
            self.attending_senators.append(self.player_data)
        
        # Display attendance information
        console.print(f"[bold cyan]Total Senators:[/] {len(all_senators) + 1}")  # +1 for player
        console.print(f"[bold cyan]Senators Present:[/] {len(self.attending_senators)} (including you)")
        
        # Create seating chart table
        seating_table = self._create_seating_chart()
        
        # Display the seating arrangement
        console.print(seating_table)
        
        # Log the attendance
        self._log_event("Attendance", f"{len(self.attending_senators)} senators present (including player)")
        
        console.print("\n[bold green]✓[/] Attendance has been taken and senators have been seated according to rank.")
    
    def _create_seating_chart(self):
        """Create and return the seating chart table."""
        from rich.table import Table
        
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
            
            # Set influence requirements for different ranks
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
            rank_senators = []
            
            # Check if player belongs to this rank
            if self.player_data["id"] not in listed_senators and self.player_data.get("influence", 0) >= influence_min:
                rank_senators.append(self.player_data)
            
            # Add other senators of this rank
            rank_senators.extend([
                s for s in self.attending_senators 
                if s.get("influence", 0) >= influence_min 
                and s.get("id", 0) not in listed_senators
                and s.get("id", 0) != self.player_data["id"]  # Don't include player twice
            ])
            
            # If no senators of this rank, skip
            if not rank_senators:
                continue
                
            # Add the senators of this rank
            for i, senator in enumerate(rank_senators):
                status = "[bold green]PRESENT[/]"
                
                # Highlight the player
                name_display = senator["name"]
                if senator.get("id") == self.player_data["id"]:
                    name_display = f"[bold white on blue]{name_display} (YOU)[/]"
                    status = "[bold cyan]PRESENT[/]"
                
                seating_table.add_row(
                    rank if i == 0 else "",  # Only show rank on first row
                    name_display,
                    senator["faction"],
                    status
                )
                listed_senators.add(senator.get("id", 0))
        
        return seating_table
    
    async def run_full_session(self, topics: List[Tuple[str, str]], debate_rounds: int = 3) -> List[Dict]:
        """
        Run a complete Senate session with player participation.
        
        Args:
            topics: List of (topic, category) tuples to be discussed
            debate_rounds: Number of rounds for each debate topic
            
        Returns:
            List of results for each topic
        """
        # Check if senate can meet today
        can_meet, reason = self.game_state.calendar.can_hold_senate_session()
        if not can_meet:
            console.print(f"\n[bold red]WARNING:[/] {reason}")
            console.print("The Senate is convening despite traditional restrictions.")
            
            # Add special magistrate justification
            console.print(f"[italic]{self.presiding_magistrate['title']} {self.presiding_magistrate['name']} has declared this an exceptional circumstance.[/]")
            
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
            
            # Display topic information
            console.print(Panel(
                f"[bold]{topic}[/]",
                title=f"[bold cyan]Current Topic: {category}[/]",
                border_style="cyan",
                width=100
            ))
            
            # Conduct debate on this topic with player participation
            debate_summary = await self.conduct_player_debate(
                topic,
                category=category,
                rounds=debate_rounds
            )
            
            # Conduct vote on this topic with player participation
            vote_result = await self.conduct_player_vote(topic, debate_summary, category)
            
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
    
    async def conduct_player_debate(
        self, 
        topic: str, 
        category: str = None,
        rounds: int = 3
    ) -> List[Dict]:
        """
        Conduct a debate with player participation.
        
        Args:
            topic: The topic being debated
            category: The category of the topic
            rounds: Number of debate rounds
            
        Returns:
            List of speech records from the debate
        """
        console.print(f"\n[bold cyan]Beginning debate on: [/][italic]{topic}[/]")
        
        # Reset debate state
        debate.reset_debate_state()
        
        # Create context for the debate
        context = {
            "topic_category": category,
            "year": self.year,
            "player_name": self.player.name,
            "player_faction": self.player.faction
        }
        
        # Keep track of all speeches
        all_speeches = []
        
        # For each round
        for round_num in range(1, rounds + 1):
            console.print(f"\n[bold blue]Round {round_num} of Debate[/]")
            
            # Select NPC speakers for this round (excluding player)
            npc_senators = [s for s in self.attending_senators if s.get("id") != self.player_data["id"]]
            num_speakers = min(2, len(npc_senators))  # Allow for 2 NPCs plus player per round
            speakers = random.sample(npc_senators, num_speakers)
            
            # Determine if player speaks in this round
            player_speaks = True if round_num == 1 else Confirm.ask(
                "Would you like to address the Senate in this round?", 
                default=True
            )
            
            # Process NPC speeches
            npc_speech_tasks = []
            for senator in speakers:
                # Determine if this senator should respond to a previous speaker
                responding_to = None
                if all_speeches:
                    # 30% chance to respond to a previous speech
                    if random.random() < 0.3:
                        responding_to = random.choice(all_speeches)
                
                # Create task for speech generation
                npc_speech_tasks.append(debate.generate_speech(
                    senator,
                    topic,
                    year=self.year,
                    responding_to=responding_to,
                    previous_speeches=all_speeches
                ))
            
            # Process all NPC speakers in parallel
            npc_speech_results = await asyncio.gather(*npc_speech_tasks)
            
            # Iterate through speeches and allow player to interject
            for speech in npc_speech_results:
                # Display the speech
                debate.display_speech(
                    {"name": speech["senator_name"], "faction": speech["faction"]}, 
                    speech, 
                    topic
                )
                
                # Record the speech
                all_speeches.append(speech)
                
                # Ask if player wants to interject
                interject = Confirm.ask(
                    "Would you like to interject during this speech?", 
                    default=False
                )
                
                if interject:
                    # Extract a segment from the speech for the player to interject on
                    sentences = speech["english_text"].split(". ")
                    if len(sentences) > 2:
                        speech_segment = ". ".join(sentences[1:3])  # Use middle portion of speech
                    else:
                        speech_segment = speech["english_text"]  # Use whole speech if short
                    
                    # Allow player to make interjection
                    interjection_result = await self.player_actions.make_interjection(
                        speech["senator_name"],
                        speech_segment,
                        topic,
                        context
                    )
                    
                    # If interjection was made, record it
                    if interjection_result.get("interjected", False):
                        # Record interjection in debate history
                        all_speeches.append({
                            "senator_id": self.player.id,
                            "senator_name": self.player.name,
                            "faction": self.player.faction,
                            "stance": "support" if "support" in interjection_result["interjection"]["content"].lower() else 
                                      "oppose" if "oppose" in interjection_result["interjection"]["content"].lower() else "neutral",
                            "key_points": [interjection_result["interjection"]["content"]],
                            "full_text": interjection_result["interjection"]["content"],
                            "english_text": interjection_result["interjection"]["content"],
                            "is_interjection": True,
                            "target_speaker": speech["senator_name"]
                        })
            
            # Player's turn to speak if they chose to
            if player_speaks:
                console.print("\n[bold cyan]Your turn to address the Senate[/]")
                
                # Determine stance options based on faction
                if self.player.faction == "Optimates":
                    default_stance = "oppose"
                elif self.player.faction == "Populares":
                    default_stance = "support"
                else:
                    default_stance = "neutral"
                
                # Allow player to choose stance
                stance_options = ["support", "oppose", "neutral"]
                stance = Prompt.ask(
                    "What is your position on this topic?",
                    choices=stance_options,
                    default=default_stance
                )
                
                # Let player make a speech
                speech_result = await self.player_actions.make_speech(
                    topic,
                    stance,
                    context
                )
                
                # Record the player's speech
                all_speeches.append(speech_result["speech"])
            
        return all_speeches
    
    async def conduct_player_vote(self, topic: str, debate_summary: List[Dict], category: str = None) -> Dict:
        """
        Conduct a vote on a topic with player participation.
        
        Args:
            topic: The topic being voted on
            debate_summary: Summary of the debate speeches
            category: The category of the topic
            
        Returns:
            Vote result information
        """
        console.print(f"\n[bold yellow]VOTING ON:[/] {topic}")
        
        # Create vote context
        context = {
            "description": f"The Senate will now vote on this {category} matter.",
            "debate_summary": debate_summary
        }
        
        # Get player's vote
        player_vote = self.player_actions.cast_vote(topic, context)
        
        # Process NPC votes
        vote_counts = {"for": 0, "against": 0, "abstain": 0}
        
        # Count player vote
        if player_vote["vote"] == "aye":
            vote_counts["for"] += 1
        elif player_vote["vote"] == "nay":
            vote_counts["against"] += 1
        else:
            vote_counts["abstain"] += 1
        
        # Count NPC votes with some influence from player
        for senator in self.attending_senators:
            # Skip player
            if senator.get("id") == self.player_data["id"]:
                continue
            
            # Calculate base voting tendencies from debate stances
            senator_speeches = [s for s in debate_summary if s.get("senator_id") == senator.get("id")]
            if senator_speeches:
                # Use the senator's stated stance in the debate
                stance = senator_speeches[-1].get("stance", "neutral")  # Use most recent speech
                if stance == "support":
                    vote_chance = {"for": 0.8, "against": 0.1, "abstain": 0.1}
                elif stance == "oppose":
                    vote_chance = {"for": 0.1, "against": 0.8, "abstain": 0.1}
                else:  # neutral
                    vote_chance = {"for": 0.3, "against": 0.3, "abstain": 0.4}
            else:
                # Senator didn't speak, use faction tendency
                faction = senator.get("faction", "")
                if faction == "Optimates":
                    vote_chance = {"for": 0.3, "against": 0.6, "abstain": 0.1}
                elif faction == "Populares":
                    vote_chance = {"for": 0.6, "against": 0.3, "abstain": 0.1}
                else:
                    vote_chance = {"for": 0.4, "against": 0.4, "abstain": 0.2}
            
            # Check if player has relationship with this senator
            relationship = self.player.relationships.get(str(senator.get("id", "")), 50)
            relationship_factor = relationship / 100.0  # 0 to 1
            
            # Adjust vote chance based on relationship and player's vote
            if relationship > 60:  # Friendly to player
                if player_vote["vote"] == "aye":
                    vote_chance["for"] += 0.2 * relationship_factor
                    vote_chance["against"] -= 0.2 * relationship_factor
                elif player_vote["vote"] == "nay":
                    vote_chance["for"] -= 0.2 * relationship_factor
                    vote_chance["against"] += 0.2 * relationship_factor
            
            # Normalize probabilities
            total = sum(vote_chance.values())
            vote_chance = {k: v/total for k, v in vote_chance.items()}
            
            # Determine vote
            vote_value = random.random()
            if vote_value < vote_chance["for"]:
                vote_counts["for"] += 1
            elif vote_value < vote_chance["for"] + vote_chance["against"]:
                vote_counts["against"] += 1
            else:
                vote_counts["abstain"] += 1
        
        # Determine outcome
        total_votes = vote_counts["for"] + vote_counts["against"]
        if total_votes > 0 and vote_counts["for"] / total_votes > 0.5:
            outcome = "PASSED"
        else:
            outcome = "FAILED"
        
        # Display vote results
        vote.display_vote_result({
            "topic": topic,
            "votes": vote_counts,
            "outcome": outcome,
            "player_vote": player_vote["vote"]
        })
        
        # Update player influence based on vote outcome
        if player_vote["vote"] == "aye" and outcome == "PASSED":
            self.player.change_influence(3)
            console.print("[green]You successfully supported the winning position. +3 Influence[/]")
        elif player_vote["vote"] == "nay" and outcome == "FAILED":
            self.player.change_influence(3)
            console.print("[green]You successfully opposed the defeated measure. +3 Influence[/]")
        
        return {
            "topic": topic,
            "votes": vote_counts,
            "outcome": outcome,
            "player_vote": player_vote["vote"]
        }