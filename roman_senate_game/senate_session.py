#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Roman Senate Game
Senate Session Module

This module orchestrates a complete Roman Senate session with historically accurate phases
including opening ceremonies, attendance, agenda introduction, debate, voting, and adjournment.
It creates a structured, immersive session flow based on the practices of the Roman Republic circa 100 BCE.
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

import debate
import vote
import utils
import officials
import political_maneuvering
import interjections
from logging_utils import get_logger

# Initialize console and logger
console = utils.console
logger = get_logger()

class SenateSession:
    """
    Orchestrates a complete Roman Senate session with all historical phases.
    
    Includes:
    - Opening ceremonies and religious observances
    - Attendance and seating by rank
    - Introduction of agenda (relatio)
    - Debate on topics
    - Voting and decisions
    - Session adjournment
    
    Designed to provide a historically accurate recreation of Senate proceedings
    from the Roman Republic period.
    """
    
    def __init__(self, senators: List[Dict], year: int, game_state: Any):
        """
        Initialize a new Senate session.
        
        Args:
            senators: List of senator dictionaries with their attributes
            year: Current year in the game (negative for BCE)
            game_state: The global game state object
        """
        self.senators = senators
        self.year = year
        self.game_state = game_state
        self.year_display = f"{abs(year)} BCE"
        self.presiding_magistrate = self._select_presiding_magistrate()
        self.attending_senators = []
        self.lictors = random.randint(6, 12)  # Number of lictors present
        self.session_log = []
        self.topics = []
        
        # Determine the meeting location based on year
        if self.year < -100:  # Before 100 BCE
            self.meeting_location = "Curia Hostilia"
        else:
            self.meeting_location = "Curia Cornelia"
            
        # Roman calendar date generation
        self.roman_date = self._generate_roman_date()
        
        # Import modules here to avoid circular imports
        import political_maneuvering
        import officials
        import interjections
        
        # Random session details
        self.auspices_favorable = random.random() > 0.1  # Usually favorable
        
        # Divine omens that might affect the session
        self.omens = []
        if random.random() < 0.3:  # 30% chance of omens
            possible_omens = [
                "A thunder was heard from the left during morning observations.",
                "Birds were seen flying in favorable patterns.",
                "The sacred chickens ate eagerly during morning rituals.",
                "Lightning was observed in the eastern sky.",
                "A snake was found in the Forum, considered a sign from the gods."
            ]
            self.omens.append(random.choice(possible_omens))
        
        # Log session initialization
        self._log_event("Session initialized", f"Year: {self.year_display}, Location: {self.meeting_location}")
    
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
    
    def _generate_roman_date(self) -> str:
        """Generate a historically accurate Roman calendar date."""
        # Roman months
        months = ["Ianuarius", "Februarius", "Martius", "Aprilis", "Maius", "Iunius", 
                 "Quintilis", "Sextilis", "September", "October", "November", "December"]
        
        # Roman date markers
        date_markers = ["Kalendae", "Nonae", "Idus"]
        
        month = random.choice(months)
        date_type = random.choice(date_markers)
        
        if date_type == "Kalendae":
            return f"Kalendae {month}"
        elif date_type == "Nonae":
            return f"{random.randint(2, 5)} Nonae {month}"
        else:  # Idus
            return f"{random.randint(2, 7)} Idus {month}"
    
    def _log_event(self, event_type: str, details: str) -> None:
        """Log a session event for record-keeping."""
        self.session_log.append({
            "type": event_type,
            "details": details,
            "timestamp": time.time()
        })
    
    def conduct_opening_ceremonies(self) -> None:
        """
        Conduct the opening religious ceremonies of the Senate session.
        
        In Roman tradition, Senate sessions began with religious rituals,
        including taking the auspices, making offerings, and invoking the gods.
        """
        console.print("\n")
        
        # Create opening ceremony title
        title = f"[bold yellow]SENATE SESSION OPENING CEREMONIES[/]"
        subtitle = f"{self.roman_date} • {self.year_display} • {self.meeting_location}"
        
        # Display the ceremony banner
        ceremony_text = f"[bold cyan]{title}[/]\n[italic]{subtitle}[/]\n\n"
        ceremony_text += f"The Senate of Rome convenes on the {self.roman_date} in the year [bold]{self.year_display}[/].\n"
        ceremony_text += f"Location: The {self.meeting_location}\n"
        ceremony_text += f"Presiding: [bold]{self.presiding_magistrate['title']} {self.presiding_magistrate['name']}[/] of the {self.presiding_magistrate['faction']} faction\n"
        ceremony_text += f"Lictors present: {self.lictors}\n"
        
        console.print(Panel(ceremony_text, border_style="yellow", width=100, title="SENATUS ROMANUS"))
        
        # Religious observances
        console.print("[bold cyan]Religious Observances[/]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            progress.add_task("[cyan]Taking the auspices...[/]", total=None)
            # Simulate time for religious ritual
            time.sleep(1.5)
        
        # Report on auspices
        if self.auspices_favorable:
            console.print("[bold green]✓[/] The auspices are favorable. The gods smile upon this session.")
        else:
            console.print("[bold red]![/] The auspices show concerning signs. The session may proceed, but with caution.")
        
        # Report any omens
        if self.omens:
            console.print("\n[bold magenta]Omens and Signs[/]")
            for omen in self.omens:
                console.print(f"• [italic]{omen}[/]")
        
        # Ritual opening
        console.print("\n[bold cyan]Opening Invocation[/]")
        
        # Latin invocation followed by English translation
        latin_invocation = "Di immortales, qui Romam aeternam fecistis, adeste. Iuppiter Optimus Maximus, Mars Pater, Quirine, Vesta, ceterique di deaeque, favete huic consilio. Auspicia capta sunt; rite precati sumus. Nunc de re publica consulere possumus."
        
        english_translation = "Immortal gods, who made Rome eternal, be present. Jupiter Best and Greatest, Father Mars, Quirinus, Vesta, and all other gods and goddesses, favor this assembly. The auspices have been taken; we have prayed according to ritual. Now we may deliberate on matters of state."
        
        invocation_panel = Panel(
            f"[italic yellow]{latin_invocation}[/]\n\n[italic white]{english_translation}[/]",
            border_style="blue",
            width=100,
            title="Invocatio"
        )
        console.print(invocation_panel)
        
        # Ritual sacrifice description
        console.print("[bold cyan]Ritual Sacrifice[/]")
        console.print("A white bull is sacrificed on the altar by the appointed priests.")
        console.print("The entrails are examined and declared favorable for Senate business.")
        
        # Log opening ceremonies completion
        self._log_event("Opening Ceremonies", "Completed with " + ("favorable" if self.auspices_favorable else "unfavorable") + " auspices")
        
        # Pause for effect
        time.sleep(1)
        
        console.print("\n[bold green]✓[/] The opening ceremonies are complete. The session may begin.")
    
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
        
        # Late arrivals
        if random.random() < 0.3:  # 30% chance of late arrivals
            num_late = random.randint(1, 3)
            console.print(f"\n[bold yellow]Late Arrivals:[/] {num_late} senator(s) arrive after the roll call.")
        
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
        agenda_table = Table(title=f"Senate Agenda - {self.roman_date}, {self.year_display}")
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
        
        [italic]"Patres conscripti, I have summoned you on this {self.roman_date} to deliberate on matters 
        of great importance to the Republic. The auspices have been taken and the gods favor 
        our assembly{" despite concerning signs" if not self.auspices_favorable else ""}. 
        
        Today we shall address {len(topics)} matter{"s" if len(topics) > 1 else ""} of state. 
        Let us proceed with wisdom and in accordance with the mos maiorum."[/]
        """
        
        console.print(Panel(intro_text, border_style="blue", width=100))
        
        # Objections or procedural notes
        if random.random() < 0.2:  # 20% chance of procedural objection
            # Find a senator likely to object (lower loyalty)
            objectors = [s for s in self.attending_senators if s.get("traits", {}).get("loyalty", 1.0) < 0.7]
            if objectors:
                objector = random.choice(objectors)
                
                objection_text = f"""
                [bold]{objector['name']}[/] ([italic]{objector['faction']}[/]) rises to speak:
                
                [italic]"I note for the record that proper notice for this assembly was not given according 
                to tradition. However, given the importance of these matters, I will not formally 
                object to proceeding, but request that it be recorded in the Senate's minutes."[/]
                """
                
                console.print(Panel(objection_text, border_style="red", width=100))
                
                response_text = f"""
                [bold]{magistrate['title']} {magistrate['name']}[/] responds:
                
                [italic]"Your objection is noted, Senator {objector['name']}. The Senate's scribes will 
                record your statement. With that matter addressed, let us proceed to the first item."[/]
                """
                
                console.print(Panel(response_text, border_style="blue", width=100))
                
                # Log the objection
                self._log_event("Procedural Objection", f"Senator {objector['name']} objected to notice procedure")
        
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
        
        # Create political maneuvering system
        politics = political_maneuvering.PoliticalManeuvering(self.senators, self.year, self.game_state)
        
        # Create presiding officials manager
        presiding_officials = officials.PresidingOfficials(self.year, self.senators, self.game_state)
        
        # Select the presiding official
        official = presiding_officials.select_presiding_official()
        
        # Conduct the opening ceremonies
        self.conduct_opening_ceremonies()
        
        # Take attendance and arrange seating
        self.conduct_attendance_and_seating()
        
        # Introduce the agenda
        self.introduce_agenda(topics)
        
        # Process each topic in sequence
        results = []
        for i, (topic, category) in enumerate(topics, 1):
            console.print(f"\n[bold yellow]TOPIC {i} OF {len(topics)}[/]")
            
            # Simulate backroom political dealings before the formal debate
            politics.simulate_backroom_dealings(self.attending_senators, topic, category)
            
            # Announce the current topic with the presiding official
            topic_intro = presiding_officials.introduce_topic(topic, category)
            console.print(Panel(topic_intro, border_style="cyan", width=100))
            
            # Conduct debate on this topic with interjections
            # We'll modify the debate call to integrate interjections
            debate_summary = await self._conduct_debate_with_interjections(
                topic,
                self.attending_senators,
                rounds=debate_rounds,
                topic_category=category,
                officials=presiding_officials
            )
            
            # Generate amendments based on political maneuvering
            amendments = []
            # Select a few senators to propose amendments
            potential_amenders = random.sample(
                self.attending_senators,
                min(3, len(self.attending_senators))
            )
            
            # Generate faction stances for consistency
            faction_stances = {
                "Optimates": random.choice(["oppose", "oppose", "neutral"]),
                "Populares": random.choice(["support", "support", "neutral"]),
                "Military": random.choice(["support", "oppose", "neutral"]),
                "Religious": random.choice(["oppose", "neutral", "support"]),
                "Merchant": random.choice(["support", "neutral", "oppose"])
            }
            
            for senator in potential_amenders:
                amendment = politics.generate_amendment(senator, topic, faction_stances)
                amendments.append(amendment)
            
            # Display political outcomes before voting
            if amendments:
                politics.display_political_outcome(politics.backroom_outcomes, amendments)
                
                # Get voting modifiers based on amendments
                voting_modifiers = politics.get_amendment_effects_on_voting(
                    amendments, self.attending_senators
                )
                # These modifiers would be passed to the vote function
            
            # Conduct vote on this topic
            vote_result = await self.conduct_vote_session(topic, debate_summary, topic_category=category)
            
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
        summary_table = Table(title=f"Senate Session Summary - {self.roman_date}, {self.year_display}")
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
        
        # Closing rituals
        console.print("[bold cyan]Closing Rituals[/]")
        console.print("The augurs perform the final observations and declare the session properly concluded.")
        
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

    async def _process_senator_vote_async(self, senator, votes, voting_record, debate_stance=None):
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
            # Handle potential None values for traits and loyalty
            traits = senator.get("traits", {}) or {}
            loyalty = traits.get("loyalty")
            
            # Only apply modifications if loyalty is not None
            if loyalty is not None:
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
        
        vote = random.choices(vote_options, weights=weights)[0]
        votes[vote] += 1
        
        # Create voting record with safe access to influence (default to 0.5 if missing)
        voting_record.append(
            {
                "senator": senator["name"],
                "faction": senator["faction"],
                "vote": vote,
                "influence": senator.get("influence", 0.5),  # Default influence value if missing
                "debate_stance": debate_stance
            }
        )
        
        return vote
    
    async def _conduct_debate_with_interjections(self, topic: str, senators_list: List[Dict], rounds: int = 3, topic_category: str = None, officials=None):
        """
        Conduct a debate with interjections from senators and procedural rulings from officials.
        
        Args:
            topic: The topic to debate
            senators_list: List of senators participating
            rounds: Number of debate rounds
            topic_category: Category of the topic
            officials: Presiding officials object for rulings
            
        Returns:
            Debate summary including speeches and interjections
        """
        # Reset debate state for a new debate
        debate.reset_debate_state()
        
        # Handle case where topic might be None
        topic_display = topic if topic else "Unknown Topic"
        
        # Create a more informative debate introduction
        if topic_category:
            introduction = f"The Senate will now debate on a matter of [bold yellow]{topic_category}[/]:\n[italic]{topic_display}[/]"
        else:
            introduction = f"The Senate will now debate:\n[italic]{topic_display}[/]"
        
        # Display the debate panel with category context
        console.print(Panel(introduction, title="[bold cyan]SENATE DEBATE BEGINS[/]", border_style="cyan", width=100))

        debate_summary = []
        
        # Track which senators have already responded to which others to prevent loops
        responded_pairs = set()  # (responder_id, target_id) pairs
        
        # Generate faction stances for consistency
        faction_stances = {
            "Optimates": random.choice(["oppose", "oppose", "neutral"]),
            "Populares": random.choice(["support", "support", "neutral"]),
            "Military": random.choice(["support", "oppose", "neutral"]),
            "Religious": random.choice(["oppose", "neutral", "support"]),
            "Merchant": random.choice(["support", "neutral", "oppose"])
        }

        # Keep track of all previous speeches for context
        previous_speeches = []
        
        for round_num in range(1, rounds + 1):
            console.print(f"\n[bold blue]Round {round_num} of Debate[/]")

            # Select speakers for this round
            speakers = random.sample(senators_list, min(3, len(senators_list)))

            # Create speech generation tasks for all speakers in this round
            async def generate_senator_speech(senator, responding_to=None):
                """
                Helper function to generate a speech for a senator, handling response logic.
                Returns the speech and the responding_to information.
                """
                # Determine if this senator should respond to a previous speaker
                if not responding_to and previous_speeches and (round_num > 1 or len(previous_speeches) >= 2):
                    # Check for each previous speech if this senator might respond
                    for prev_speech in reversed(previous_speeches):  # Check most recent first
                        prev_senator_id = prev_speech.get("senator_id")
                        current_senator_id = senator.get("id")
                        
                        # Skip if they've already responded to each other
                        if prev_senator_id and current_senator_id:
                            pair = (current_senator_id, prev_senator_id)
                            if pair in responded_pairs:
                                continue
                        
                        # Calculate response probability based on stance agreement/disagreement
                        response_chance = 0.2  # Base chance
                        
                        if prev_speech.get("faction") == senator.get("faction"):
                            # More likely to respond to same faction
                            response_chance += 0.1
                        
                        # Strongly agree/disagree increases chance to respond
                        if prev_speech.get("stance") == senator.get("faction"):
                            # Same stance, more likely to support
                            response_chance += 0.2
                        elif prev_speech.get("stance") != senator.get("faction") and prev_speech.get("stance") != "neutral":
                            # Opposing stance, more likely to rebut
                            response_chance += 0.3
                        
                        # Check if random chance triggers a response
                        if random.random() < response_chance:
                            responding_to = prev_speech
                            
                            # Record that this senator has responded to prevent loops
                            if prev_senator_id and current_senator_id:
                                responded_pairs.add((current_senator_id, prev_senator_id))
                            
                            # Break out of the loop, we found someone to respond to
                            break

                # Generate senator's AI speech with historical context from the game year
                speech = debate.generate_speech(
                    senator,
                    topic,
                    faction_stances,
                    self.year,
                    responding_to=responding_to,
                    previous_speeches=previous_speeches
                )
                
                return speech, responding_to

            # Create tasks for parallel speech generation
            speech_tasks = []
            
            # Show which senators are preparing their speeches
            for senator in speakers:
                thought_text = f"[bold]{senator['name']} ({senator['faction']}) is preparing to speak...[/]"
                console.print(thought_text)
                
                # Create a task for each senator's speech generation
                speech_tasks.append(generate_senator_speech(senator))
            
            # Process all speakers in parallel
            speech_results = await asyncio.gather(*speech_tasks)
            
            # Display speeches in order with potential interjections
            for i, (speech, responding_to) in enumerate(speech_results):
                senator = speakers[i]
                
                # Display the speech in an immersive format with position summary
                debate.display_speech(senator, speech, topic)
                
                # Process potential interjections after this speech
                if hasattr(interjections, 'integrate_with_debate'):
                    interjection_results = interjections.integrate_with_debate(
                        speech,
                        senator,
                        senators_list,
                        officials=officials,
                        context={"topic": topic, "topic_category": topic_category}
                    )
                    
                    # Add interjections to the speech record
                    speech["interjections"] = interjection_results
                
                # Extract argument from speech for scoring
                argument = speech["full_text"]

                # Score the speech
                score = utils.score_argument(argument, topic)

                # Show the score
                score_table = Table(title="Speech Assessment")
                score_table.add_column("Criterion", style="cyan")
                score_table.add_column("Score", justify="right")

                for criterion, value in score.items():
                    if criterion != "total":
                        score_table.add_row(
                            criterion.replace("_", " ").title(), f"{value:.2f}"
                        )

                score_table.add_row("Overall", f"[bold]{score['total']:.2f}[/]")
                console.print(score_table)

                # Create enriched speech summary
                speech_summary = {
                    "round": round_num,
                    "senator_id": senator.get("id", 0),
                    "senator_name": senator["name"],
                    "faction": senator["faction"],
                    "speech": speech["full_text"],
                    "latin_speech": speech["latin_text"],
                    "english_speech": speech["english_text"],
                    "stance": speech["stance"],
                    "score": score["total"],
                    "is_response": speech.get("is_response", False),
                    "responding_to": speech.get("responding_to"),
                    "interjections": speech.get("interjections", [])
                }
                
                # Add to both the overall debate summary and the running list of speeches
                debate_summary.append(speech_summary)
                previous_speeches.append(speech_summary)

                # Pause for readability
                time.sleep(1)

        console.print("\n[bold green]✓[/] Debate concluded.\n")
        return debate_summary
        # (This line is duplicated and misplaced - removing)
        
        # Formal adjournment speech
        topic_count = len(results) if results else 0
        adjournment_text = f"""
        [bold]{self.presiding_magistrate['title']} {self.presiding_magistrate['name']}[/] rises to conclude the session:
        
        [italic]"Patres conscripti, we have completed our deliberations for this day. The Senate has
        expressed its will on {topic_count} matter{"s" if topic_count > 1 else ""} of state. The scribes have
        recorded our decisions, which shall be published in the acta diurna.
        
        If there is no other business, I declare this session of the Senate adjourned.
        
        May the gods continue to favor Rome."[/]
        """
        
        console.print(Panel(adjournment_text, border_style="blue", width=100))
        
        # Closing rituals
        console.print("[bold cyan]Closing Rituals[/]")
        console.print("The augurs perform the final observations and declare the session properly concluded.")
        
        # Calculate session duration
        if self.session_log:
            start_time = self.session_log[0]["timestamp"]
            end_time = time.time()
            duration_mins = (end_time - start_time) / 60
            console.print(f"\n[bold cyan]Session Duration:[/] {duration_mins:.1f} minutes")
        
        # Log session conclusion
        self._log_event("Session Concluded", f"Completed with {topic_count} topics decided")
        
        console.print(Panel(
            "[bold yellow]SENATE SESSION CONCLUDED[/]",
            border_style="yellow", 
            width=100
        ))

    async def conduct_vote_session(self, topic: str, debate_summary=None, topic_category: str = None):
        """
        Conduct a vote on the given topic after debate within a senate session.
        
        Args:
            topic: The topic to vote on
            debate_summary: Summary of the debate results
            topic_category: Category of the topic (e.g., Military funding)
            
        Returns:
            Vote result dictionary
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
            logger = get_logger()
            
            for speech in debate_summary:
                try:
                    senator_name = speech.get("senator_name")
                    if senator_name:
                        senator_speeches[senator_name] = speech
                        logger.log_response(f"Processed speech for {senator_name}")
                    else:
                        logger.log_error(f"Missing senator_name in speech: {speech}")
                except Exception as e:
                    logger.log_error(f"Error processing speech: {e}")
                    continue
            
            for senator_name, speech in senator_speeches.items():
                try:
                    debate_stances[senator_name] = speech.get("stance", "neutral")
                    logger.log_response(f"Recorded stance for {senator_name}: {debate_stances[senator_name]}")
                except Exception as e:
                    logger.log_error(f"Error recording stance for {senator_name}: {e}")
                    debate_stances[senator_name] = "neutral"  # Fallback to neutral
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold]Senators are casting their votes...[/]"),
            console=console,
        ) as progress:
            task = progress.add_task("Voting...", total=len(self.attending_senators))

            # Create tasks for parallel vote processing
            vote_tasks = []
            for senator in self.attending_senators:
                # Pass the senator's debate stance if available
                stance = debate_stances.get(senator["name"], None)
                # Create coroutine for each senator's vote
                vote_tasks.append(asyncio.create_task(self._process_senator_vote_async(senator, votes, voting_record, stance)))
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
            vote_value = record["vote"]
            
            # Determine if senator was swayed
            expected_vote = stance_to_vote.get(stance, None)
            swayed = ""
            
            if expected_vote and vote_value != expected_vote:
                swayed = "[bold yellow]*[/]"
            elif stance == "neutral" and vote_value != "abstain":
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
                vote_format.get(vote_value, f"[dim]{vote_value}[/]"),
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
            outcome = "TIE - CONSUL DECIDES"
            style = "bold yellow"
            
            # Use the presiding official to break the tie
            if hasattr(self, 'presiding_magistrate'):
                consul_vote, explanation = "for", "The consul votes in favor."
                outcome = "PASSED"
                style = "bold green"
            else:
                outcome = random.choice(["PASSED", "REJECTED"])
                style = "bold green" if outcome == "PASSED" else "bold red"

        console.print(f"\nThe motion has been [bold {style}]{outcome}[/].\n")

        # Record result
        result = {
            "topic": topic,
            "votes": votes,
            "outcome": outcome,
            "voting_record": voting_record,
            "debate_stances": debate_stances
        }

        return result