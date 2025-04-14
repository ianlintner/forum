#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Roman Senate Game
Presiding Officials Module

This module manages the presiding officials of the Roman Senate, including
consuls, praetors, and other authorized officials based on historical accuracy.
Officials have unique personalities, influences, and biases that affect how they
preside over Senate sessions, introduce topics, control debates, and finalize votes.
"""

import random
import time
from typing import List, Dict, Optional, Any, Tuple

from rich.panel import Panel
from rich.console import Console
from rich.text import Text

import utils
from logging_utils import get_logger

# Initialize console and logger
console = utils.console
logger = get_logger()

class PresidingOfficials:
    """
    Manages the various officials who could preside over Senate sessions.
    
    In the Roman Republic, several types of magistrates could preside over the Senate:
    - Consuls: The highest ranking magistrates (2 per year)
    - Praetors: Lower ranking magistrates who could preside in absence of consuls
    - Dictator: Appointed in times of emergency (rare)
    - Tribunes of the Plebs: Could convene the Senate after 287 BCE
    - Interrex: Temporary official during vacancy or electoral disputes
    
    Officials have personalities and biases that affect how they run Senate sessions.
    """
    
    def __init__(self, year: int, senators: List[Dict], game_state: Any = None):
        """
        Initialize the presiding officials manager.
        
        Args:
            year: Current year in the game (negative for BCE)
            senators: List of senator dictionaries with their attributes
            game_state: The global game state object
        """
        self.year = year
        self.year_display = f"{abs(year)} BCE"
        self.original_senators = senators.copy()  # Keep a copy for reference
        self.available_senators = senators.copy()  # The list we'll modify
        self.game_state = game_state
        self.officials = []
        self.current_presiding_official = None
        
        # Create historically accurate officials based on the year
        self.generate_officials(year)
        
        # Log initialization
        logger.log_response(f"Presiding officials initialized for {self.year_display}")
    
    def generate_officials(self, year: int) -> None:
        """
        Generate historically accurate officials based on the given year.
        
        The Roman Republic's magistracies evolved over time:
        - Early Republic (509-367 BCE): Consuls only
        - Mid Republic (366-133 BCE): Consuls, Praetors
        - Late Republic (132-27 BCE): Consuls, Praetors, occasionally Dictators
        
        Args:
            year: The year to generate officials for (negative for BCE)
        """
        self.officials = []
        
        # Determine which official types are available based on historical period
        official_types = self._get_official_types_for_year(year)
        
        # Sort senators by influence for magistrate selection
        sorted_senators = sorted(
            self.available_senators, 
            key=lambda s: s.get("influence", 0), 
            reverse=True
        )

        # Generate consuls (always 2 per year in the Republic)
        if "Consul" in official_types and len(sorted_senators) >= 2:
            for i in range(2):
                if sorted_senators:
                    senator = sorted_senators.pop(0)  # Get the most influential senator
                    
                    # Remove from available senators to avoid duplication
                    self.available_senators = [s for s in self.available_senators if s.get("id") != senator.get("id")]
                    
                    # Create consul with personality traits
                    consul = self._create_official(
                        senator,
                        "Consul",
                        seniority="Senior" if i == 0 else "Junior"
                    )
                    self.officials.append(consul)
   
        # Generate praetors (number varied over time)
        if "Praetor" in official_types:
            praetor_count = self._get_praetor_count_for_year(year)
            for i in range(min(praetor_count, len(sorted_senators))):
                if sorted_senators:
                    senator = sorted_senators.pop(0)
                    
                    # Remove from available senators
                    self.available_senators = [s for s in self.available_senators if s.get("id") != senator.get("id")]
                    
                    # Create praetor
                    praetor = self._create_official(
                        senator,
                        "Praetor",
                        seniority=f"Praetor {i+1}"
                    )
                    self.officials.append(praetor)
        
        # Generate tribune of the plebs (if applicable to year)
        if "Tribune of the Plebs" in official_types and sorted_senators:
            # Find senators from Populares faction if possible
            populares_senators = [s for s in sorted_senators if s.get("faction") == "Populares"]
            
            if populares_senators:
                senator = populares_senators[0]
            else:
                senator = sorted_senators[0]
            
            # Remove from list
            sorted_senators.remove(senator)
            self.available_senators = [s for s in self.available_senators if s.get("id") != senator.get("id")]
            
            # Create tribune
            tribune = self._create_official(
                senator,
                "Tribune of the Plebs"
            )
            self.officials.append(tribune)
        
        # Generate interrex (rare, temporary position)
        if "Interrex" in official_types and sorted_senators:
            senator = sorted_senators.pop(0)
            self.available_senators = [s for s in self.available_senators if s.get("id") != senator.get("id")]
            
            interrex = self._create_official(
                senator,
                "Interrex"
            )
            self.officials.append(interrex)
        
        # Special case: Dictator (very rare)
        if "Dictator" in official_types and random.random() < 0.05:  # 5% chance
            if sorted_senators:
                senator = sorted_senators.pop(0)
                self.available_senators = [s for s in self.available_senators if s.get("id") != senator.get("id")]
                
                dictator = self._create_official(
                    senator,
                    "Dictator"
                )
                self.officials.append(dictator)
        
        # Log officials creation
        logger.log_response(f"Generated {len(self.officials)} officials for {self.year_display}")
    
    def _get_official_types_for_year(self, year: int) -> List[str]:
        """
        Determine which official types existed in a given year.
        
        Args:
            year: The year to check (negative for BCE)
            
        Returns:
            List of official titles available in that year
        """
        officials = ["Consul"]  # Consuls existed throughout the Republic
        
        # Praetors introduced in 366 BCE
        if year <= -366:
            officials.append("Praetor")
        
        # Tribune of the Plebs could convene Senate after Lex Hortensia (287 BCE)
        if year <= -287:
            officials.append("Tribune of the Plebs")
        
        # Dictator was a special emergency position throughout the Republic
        # but especially common in the late Republic
        if year <= -82:
            officials.append("Dictator")
        
        # Interrex was used throughout the Republic during vacancies
        officials.append("Interrex")
        
        return officials
    
    def _get_praetor_count_for_year(self, year: int) -> int:
        """
        Get the historically accurate number of praetors for a given year.
        
        The number of praetors increased over time:
        - 366-227 BCE: 1 praetor
        - 227-197 BCE: 2 praetors
        - 197-81 BCE: 4 praetors
        - 81-27 BCE: 8 praetors (after Sulla's reforms)
        
        Args:
            year: The year to check (negative for BCE)
            
        Returns:
            Number of praetors for that year
        """
        if year > -366:
            return 0  # No praetors before 366 BCE
        elif year > -227:
            return 1  # 1 praetor from 366-227 BCE
        elif year > -197:
            return 2  # 2 praetors from 227-197 BCE
        elif year > -81:
            return 4  # 4 praetors from 197-81 BCE
        else:
            return 8  # 8 praetors after Sulla's reforms
    
    def _create_official(self, senator: Dict, title: str, seniority: str = None) -> Dict:
        """
        Create an official with personality traits and biases.
        
        Args:
            senator: Base senator to convert to official
            title: Official title
            seniority: Optional seniority designation
            
        Returns:
            Official dictionary
        """
        # Start with the senator's data
        official = senator.copy()
        
        # Ensure traits exist and have default values if missing
        if "traits" not in official or official["traits"] is None:
            official["traits"] = {}
            
        # Ensure all required traits exist
        traits = official["traits"]
        if "loyalty" not in traits or traits["loyalty"] is None:
            traits["loyalty"] = random.uniform(0.5, 1.0)
        if "eloquence" not in traits or traits["eloquence"] is None:
            traits["eloquence"] = random.uniform(0.5, 1.0)
        if "corruption" not in traits or traits["corruption"] is None:
            traits["corruption"] = random.uniform(0.0, 0.5)
        
        # Add official-specific attributes
        official["title"] = title
        official["is_official"] = True
        
        if seniority:
            official["seniority"] = seniority
        
        # Add personality traits that influence official behavior
        official["personality"] = {
            "authoritarianism": random.uniform(0.3, 1.0),  # How strictly they enforce rules
            "impartiality": random.uniform(0.2, 0.9),  # How fair they are when presiding
            "traditionalism": random.uniform(0.4, 1.0),  # How much they adhere to traditions
            "decisiveness": random.uniform(0.4, 1.0),  # How quickly they make decisions
            "eloquence": random.uniform(0.5, 1.0)  # How well they articulate
        }
        
        # Add biases based on faction and year
        official["biases"] = self._generate_biases(senator, title, self.year)
        
        # Track whether this official has made any rulings in this session
        official["rulings_made"] = []
        
        return official
    
    def _generate_biases(self, senator: Dict, title: str, year: int) -> Dict:
        """
        Generate realistic biases for this official based on faction and historical context.
        
        Args:
            senator: The senator becoming an official
            title: The official title
            year: The current year
            
        Returns:
            Dictionary of biases
        """
        biases = {}
        faction = senator.get("faction", "")
        
        # Policy biases
        if faction == "Optimates":
            biases["foreign_policy"] = random.uniform(-0.8, -0.2)  # Conservative, cautious
            biases["domestic_policy"] = random.uniform(-0.9, -0.3)  # Traditional
            biases["economic_policy"] = random.uniform(-0.7, 0.0)  # Pro-aristocracy
        elif faction == "Populares":
            biases["foreign_policy"] = random.uniform(-0.4, 0.4)  # Mixed
            biases["domestic_policy"] = random.uniform(0.3, 0.9)  # Progressive
            biases["economic_policy"] = random.uniform(0.2, 0.8)  # Pro-people
        elif faction == "Military":
            biases["foreign_policy"] = random.uniform(0.5, 1.0)  # Expansionist
            biases["domestic_policy"] = random.uniform(-0.3, 0.5)  # Mixed
            biases["economic_policy"] = random.uniform(-0.2, 0.6)  # Varied
        elif faction == "Religious":
            biases["foreign_policy"] = random.uniform(-0.7, 0.0)  # Conservative
            biases["domestic_policy"] = random.uniform(-0.8, -0.2)  # Traditional
            biases["economic_policy"] = random.uniform(-0.5, 0.2)  # Mixed
        elif faction == "Merchant":
            biases["foreign_policy"] = random.uniform(0.2, 0.8)  # Pro-trade
            biases["domestic_policy"] = random.uniform(-0.3, 0.5)  # Mixed
            biases["economic_policy"] = random.uniform(0.5, 1.0)  # Pro-commerce
        
        # Faction biases (preference or dislike for other factions)
        for other_faction in ["Optimates", "Populares", "Military", "Religious", "Merchant"]:
            if other_faction == faction:
                # Favor own faction
                biases[f"faction_{other_faction.lower()}"] = random.uniform(0.5, 1.0)
            else:
                # Based on historical faction relations
                if (faction == "Optimates" and other_faction == "Populares") or \
                   (faction == "Populares" and other_faction == "Optimates"):
                    # These factions were traditional rivals
                    biases[f"faction_{other_faction.lower()}"] = random.uniform(-1.0, -0.3)
                else:
                    # Other faction relationships varied
                    biases[f"faction_{other_faction.lower()}"] = random.uniform(-0.5, 0.5)
        
        # Title-specific biases
        if title == "Dictator":
            # Dictators tended to be authoritarian
            biases["authoritarianism"] = random.uniform(0.7, 1.0)
        elif title == "Tribune of the Plebs":
            # Tribunes typically favored the common people
            biases["populism"] = random.uniform(0.6, 1.0)
        
        # Time period-specific biases
        if year <= -133:  # After the Gracchi reforms
            biases["land_reform"] = random.uniform(-0.8, 0.8)  # Hot topic of the time
        
        if year <= -107:  # After Marius's military reforms
            biases["military_reform"] = random.uniform(-0.7, 0.7)
        
        if year <= -88:  # During/after Social War
            biases["italian_citizenship"] = random.uniform(-0.6, 0.8)
        
        return biases
    
    def select_presiding_official(self) -> Dict:
        """
        Choose the appropriate official to lead the session based on Roman protocol.
        
        In Roman tradition, the hierarchy for presiding was generally:
        1. Dictator (if one existed)
        2. Consuls (with the senior consul presiding)
        3. Praetors (in order of seniority)
        4. Other authorized officials
        
        Returns:
            The selected presiding official
        """
        if not self.officials:
            # If no officials were generated, create a default one
            console.print("[bold yellow]Warning:[/] No officials available, creating default consul")
            
            # Get the most influential senator
            if self.available_senators:
                senator = max(self.available_senators, key=lambda s: s.get("influence", 0))
                self.officials.append(self._create_official(senator, "Consul"))
            else:
                # Create a completely new official as fallback
                fallback_official = {
                    "name": "Lucius Valerius Flaccus",
                    "id": 9999,
                    "faction": "Optimates",
                    "influence": 9,
                    "traits": {
                        "eloquence": 0.8,
                        "loyalty": 0.9,
                        "corruption": 0.2,
                    }
                }
                self.officials.append(self._create_official(fallback_official, "Consul"))
        
        # Select based on proper Roman hierarchy
        for title in ["Dictator", "Consul", "Praetor", "Interrex", "Tribune of the Plebs"]:
            matching_officials = [o for o in self.officials if o["title"] == title]
            
            if matching_officials:
                # For consuls, the senior consul would preside
                if title == "Consul":
                    # Find the senior consul if specified
                    senior_consuls = [o for o in matching_officials if o.get("seniority") == "Senior"]
                    if senior_consuls:
                        self.current_presiding_official = senior_consuls[0]
                    else:
                        # Otherwise take the first consul
                        self.current_presiding_official = matching_officials[0]
                else:
                    # For other officials, take the first one
                    self.current_presiding_official = matching_officials[0]
                
                return self.current_presiding_official
        
        # Fallback: just take the first official
        self.current_presiding_official = self.officials[0]
        return self.current_presiding_official
    
    def introduce_topic(self, topic: str, category: str = None) -> str:
        """
        Formulate how the official introduces a topic to the Senate.
        
        The introduction style depends on the official's personality and the topic.
        
        Args:
            topic: The topic to introduce
            category: Optional category of the topic
            
        Returns:
            Formatted string of the official's introduction
        """
        if not self.current_presiding_official:
            self.select_presiding_official()
        
        official = self.current_presiding_official
        
        # Check if this official has bias on this category
        bias_level = 0
        if category:
            category_lower = category.lower()
            for bias_key, bias_value in official.get("biases", {}).items():
                if category_lower in bias_key:
                    bias_level = bias_value
        
        # Get personality traits
        traditionalism = official.get("personality", {}).get("traditionalism", 0.7)
        eloquence = official.get("personality", {}).get("eloquence", 0.7)
        authoritarianism = official.get("personality", {}).get("authoritarianism", 0.5)
        
        # Opening formalities
        formality_level = "high" if traditionalism > 0.7 else "medium" if traditionalism > 0.4 else "low"
        
        # Traditional formal opening phrases
        traditional_openings = [
            "Patres conscripti, I bring before you a matter of state that requires our deliberation.",
            "Senators of Rome, I convene this body to address an issue of significance to the Republic.",
            "By the authority vested in me, I submit for your consideration this matter of public interest."
        ]
        
        # Less formal opening phrases
        less_formal_openings = [
            "Fellow senators, our attention is required on an important matter.",
            "Senators, I now present a topic that demands our consideration.",
            "Let us turn to the next matter requiring senatorial deliberation."
        ]
        
        # Direct, authoritarian opening phrases
        direct_openings = [
            "Senators, we must now decide on this matter without delay.",
            "The Senate will now address the following issue.",
            "I bring forward this matter which requires immediate consideration."
        ]
        
        # Select appropriate opening based on formality and authoritarianism
        if formality_level == "high":
            opening = random.choice(traditional_openings)
        elif authoritarianism > 0.7:
            opening = random.choice(direct_openings)
        else:
            opening = random.choice(less_formal_openings)
        
        # Build topic introduction
        introduction = f"{opening}\n\n"
        
        # Add topic description
        if category:
            introduction += f"The matter concerns {category}: {topic}\n\n"
        else:
            introduction += f"The matter is as follows: {topic}\n\n"
        
        # Add biased statement if the official has strong feelings
        if abs(bias_level) > 0.6:
            if bias_level > 0.6:
                biased_phrases = [
                    f"I believe this proposal has merit and deserves your favorable consideration.",
                    f"In my estimation, this matter aligns with the interests of Rome.",
                    f"I would note this proposal appears to serve the Republic well."
                ]
                introduction += random.choice(biased_phrases) + "\n\n"
            elif bias_level < -0.6:
                biased_phrases = [
                    f"I have reservations about this proposal and urge careful scrutiny.",
                    f"This matter requires the Senate's most cautious deliberation.",
                    f"I would counsel restraint in our approach to this issue."
                ]
                introduction += random.choice(biased_phrases) + "\n\n"
        
        # Add procedural information
        if authoritarianism > 0.7:
            introduction += "I expect orderly debate and will recognize senators to speak in turn. Disruptions will not be tolerated.\n\n"
        else:
            introduction += "Let us proceed with an orderly debate. Senators wishing to speak should make themselves known.\n\n"
        
        # Add traditional closing to open debate
        closings = [
            "The floor is now open for debate.",
            "Let the debate commence.",
            "You may now present your views on this matter."
        ]
        introduction += random.choice(closings)
        
        # Log the introduction
        logger.log_response(f"Official {official['name']} introduced topic: {topic}")
        
        return introduction
    
    def cast_deciding_vote(self, official: Dict = None, topic: str = None, votes: Dict = None) -> Tuple[str, str]:
        """
        Cast a deciding vote in case of a tie in the Senate.
        
        Args:
            official: The official casting the vote (defaults to current presiding)
            topic: The topic being voted on
            votes: Current vote counts
            
        Returns:
            Tuple of (vote_decision, explanation)
        """
        if not official:
            official = self.current_presiding_official
            if not official:
                official = self.select_presiding_official()
        
        # Default vote is "for" unless biases suggest otherwise
        vote_decision = "for"
        explanation = ""
        
        # Consider the official's biases if topic category can be inferred
        if topic:
            topic_lower = topic.lower()
            
            # Check for biases that might be relevant to this topic
            relevant_biases = []
            for bias_key, bias_value in official.get("biases", {}).items():
                # If any word in the bias key appears in the topic, consider it relevant
                if any(word in topic_lower for word in bias_key.split('_')):
                    relevant_biases.append((bias_key, bias_value))
            
            # If relevant biases were found, use them to determine the vote
            if relevant_biases:
                # Calculate the average bias value - ensure None values are filtered out
                valid_bias_values = [value for _, value in relevant_biases if value is not None]
                
                # Only calculate if we have valid values
                if valid_bias_values:
                    avg_bias = sum(valid_bias_values) / len(valid_bias_values)
                    
                    # Strong negative bias leads to voting against
                    if avg_bias < -0.3:
                        vote_decision = "against"
                else:
                    # Default to a neutral position if no valid biases
                    avg_bias = 0.0
                
                # Generate explanation based on biases
                if abs(avg_bias) > 0.5:
                    if vote_decision == "for":
                        explanation = f"As {official['title']}, I cast my vote in favor, believing this serves Rome's interests."
                    else:
                        explanation = f"As {official['title']}, I must vote against this proposal as I do not believe it serves Rome well."
                else:
                    explanation = f"As the vote is tied, I cast the deciding vote {vote_decision} this proposal."
            else:
                # No relevant biases, use personality traits
                traditionalism = official.get("personality", {}).get("traditionalism", 0.7)
                
                # Traditional officials tend to vote against change
                if "change" in topic_lower or "reform" in topic_lower or "new" in topic_lower:
                    if traditionalism > 0.7:
                        vote_decision = "against"
                        explanation = "As is proper in matters of change, I cast my vote against, to preserve our traditions."
                    else:
                        explanation = "In this tie, I cast my vote for this proposal, believing measured change can benefit Rome."
                else:
                    explanation = f"With the Senate divided equally, I cast the deciding vote {vote_decision} this measure."
        else:
            # Without topic context, base it on official's general inclinations
            explanation = f"As the presiding magistrate, I cast the deciding vote {vote_decision} this measure."
        
        # Log the deciding vote
        logger.log_response(f"Official {official['name']} cast deciding vote: {vote_decision}")
        
        return vote_decision, explanation
    
    def make_ruling(self, official: Dict = None, context: str = "", topic: str = "") -> Tuple[str, str]:
        """
        Make a ruling on a procedural matter or debate issue.
        
        Args:
            official: The official making the ruling (defaults to current presiding)
            context: Description of the procedural context requiring a ruling
            topic: The topic currently under discussion
            
        Returns:
            Tuple of (ruling_type, ruling_text)
        """
        if not official:
            official = self.current_presiding_official
            if not official:
                official = self.select_presiding_official()
        
        # Possible ruling types
        ruling_types = [
            "order_violation",  # Senator violating rules of order
            "time_limit",  # Imposing time limits on speeches
            "relevance",  # Ruling a speech off-topic
            "procedure_clarification",  # Clarifying a procedural point
            "debate_extension",  # Extending debate time
            "debate_conclusion"  # Concluding debate and moving to vote
        ]
        
        # Determine ruling type based on context if not specified
        ruling_type = "procedure_clarification"  # Default
        
        for r_type in ruling_types:
            if r_type.lower() in context.lower():
                ruling_type = r_type
                break
        
        # Get personality traits that affect rulings
        authoritarianism = official.get("personality", {}).get("authoritarianism", 0.5)
        impartiality = official.get("personality", {}).get("impartiality", 0.7)
        decisiveness = official.get("personality", {}).get("decisiveness", 0.6)
        
        # Prepare ruling text based on ruling type and personality
        ruling_text = ""
        
        if ruling_type == "order_violation":
            if authoritarianism > 0.7:
                ruling_text = "Order! The Senate will maintain decorum. The senator will cease such behavior immediately or be removed."
            else:
                ruling_text = "I remind the honorable senator to observe the traditions of debate in this chamber."
        
        elif ruling_type == "time_limit":
            if decisiveness > 0.7:
                ruling_text = "In the interest of hearing from all senators, speeches will be limited to three minutes each."
            else:
                ruling_text = "I suggest we limit the remaining speeches to allow all to be heard before voting."
        
        elif ruling_type == "relevance":
            if authoritarianism > 0.7:
                ruling_text = "The senator's remarks are not germane to the topic at hand. Please confine your comments to the matter before us."
            else:
                ruling_text = "I would gently encourage the senator to return to the topic currently under consideration."
        
        elif ruling_type == "procedure_clarification":
            ruling_text = "To clarify the procedure: we will hear from all senators who wish to speak, followed by a voice vote. If the result is unclear, we will proceed to a counted vote."
        
        elif ruling_type == "debate_extension":
            if impartiality > 0.6:
                ruling_text = "As significant points remain to be discussed, I will allow additional time for debate before calling the vote."
            else:
                ruling_text = "Despite some senators wishing to conclude, I believe further debate will serve the Senate's understanding of this issue."
        
        elif ruling_type == "debate_conclusion":
            if decisiveness > 0.6:
                ruling_text = "The matter has been thoroughly debated. I now call the Senate to vote on the proposal before us."
            else:
                ruling_text = "It appears that all views have been expressed. Unless there are strong objections, we shall proceed to the vote."
        
        # Record that this ruling was made
        official["rulings_made"].append({
            "type": ruling_type,
            "text": ruling_text,
            "topic": topic,
            "timestamp": time.time()
        })
        
        # Log the ruling
        logger.log_response(f"Official {official['name']} made ruling: {ruling_type}")
        
        return ruling_type, ruling_text
    
    def get_official_by_id(self, official_id: int) -> Optional[Dict]:
        """
        Get an official by their ID.
        
        Args:
            official_id: The ID of the official to retrieve
            
        Returns:
            The official dictionary or None if not found
        """
        for official in self.officials:
            if official.get("id") == official_id:
                return official
        return None
    
    def get_all_officials(self) -> List[Dict]:
        """
        Get all generated officials.
        
        Returns:
            List of all official dictionaries
        """
        return self.officials
    
    def display_officials_info(self) -> None:
        """Display information about all officials using Rich."""
        from rich.table import Table
        
        console.print("\n[bold yellow]Presiding Officials of the Senate[/]")
        
        if not self.officials:
            console.print("[italic]No officials have been generated yet.[/]")
            return
        
        # Create a table for officials
        table = Table(title=f"Senate Officials - {self.year_display}")
        table.add_column("Name", style="cyan")
        table.add_column("Title", style="yellow")
        table.add_column("Faction", style="magenta")
        table.add_column("Personality", style="green")
        
        for official in self.officials:
            # Format personality traits
            personality_traits = []
            for trait, value in official.get("personality", {}).items():
                # Only show strongest traits
                if value > 0.7:
                    personality_traits.append(f"{trait.capitalize()}: {value:.1f}")
            
            personality_str = ", ".join(personality_traits) if personality_traits else "Balanced"
            
            # Add row to table
            table.add_row(
                official["name"],
                f"{official['title']}{' (' + official.get('seniority', '') + ')' if official.get('seniority') else ''}",
                official["faction"],
                personality_str
            )
        
        console.print(table)
        
        # Highlight the current presiding official
        if self.current_presiding_official:
            console.print(f"\n[bold green]Current Presiding Official:[/] {self.current_presiding_official['title']} {self.current_presiding_official['name']} ({self.current_presiding_official['faction']})")