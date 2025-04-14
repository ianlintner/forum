#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Roman Senate Game
Political Maneuvering Module

This module handles the behind-the-scenes political dealings, negotiations, and amendment
processes in the Roman Senate. It models faction alliances, backroom negotiations,
amendment proposals, political favors, and corruption mechanics.

Historical context:
In the Roman Republic, much of the real political work happened outside the formal
debate process through private negotiations, client-patron relationships, and informal
alliances between powerful senators. Amendments to proposals were common tactics to
alter legislation in ways that benefited certain factions.
"""

import random
import time
from typing import List, Dict, Tuple, Any, Optional
from collections import defaultdict

from rich.panel import Panel
from rich.console import Console
from rich.text import Text
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

import utils
from logging_utils import get_logger

# Initialize console and logger
console = utils.console
logger = get_logger()

class PoliticalManeuvering:
    """
    Models the political maneuvering, faction negotiations, amendment processes,
    and backroom dealings in the Roman Senate.
    
    This class handles the informal but crucial political activities that historically
    occurred alongside formal debate including:
    - Pre-debate faction negotiations
    - Amendment proposals and counter-proposals
    - Political favor trading and client-patron relationships
    - Corruption and bribery mechanics
    """
    
    def __init__(self, senators: List[Dict], year: int, game_state: Any = None):
        """
        Initialize political maneuvering system.
        
        Args:
            senators: List of senator dictionaries with their attributes
            year: Current year in the game (negative for BCE)
            game_state: The global game state object
        """
        self.senators = senators
        self.year = year
        self.game_state = game_state
        self.year_display = f"{abs(year)} BCE"
        
        # Political favor tracking (who owes favors to whom)
        # Format: {senator_id: {benefactor_id: favor_intensity}}
        # Intensity ranges from 0.1 (small favor) to 1.0 (life debt)
        self.political_favors = defaultdict(lambda: defaultdict(float))
        
        # Faction alliances - dynamically changes based on shared interests
        # Ranges from -1.0 (hostile) to 1.0 (aligned)
        self.faction_relations = self._initialize_faction_relations()
        
        # Track corruption levels for factions (tendency toward bribery)
        self.faction_corruption = {
            "Optimates": random.uniform(0.2, 0.6),  # Traditional aristocrats
            "Populares": random.uniform(0.1, 0.5),  # Popular reformers
            "Military": random.uniform(0.3, 0.8),   # Military leaders
            "Religious": random.uniform(0.1, 0.4),  # Religious conservatives
            "Merchant": random.uniform(0.4, 0.9),   # Business interests
        }
        
        # Faction influence (political power)
        self.faction_influence = self._calculate_faction_influence()
        
        # Amendment history for the current topic
        self.amendments = []
        
        # Backroom dealing outcomes
        self.backroom_outcomes = []
        
        # Log initialization
        logger.log_response(f"Political maneuvering initialized for {self.year_display}")
    
    def _initialize_faction_relations(self) -> Dict[str, Dict[str, float]]:
        """
        Initialize relationship values between factions based on historical trends.
        
        Returns:
            Dict: Nested dictionary of faction relationships
        """
        relations = defaultdict(lambda: defaultdict(float))
        
        # Historical faction tensions
        # Optimates (aristocratic conservatives) vs Populares (reform populists)
        relations["Optimates"]["Populares"] = -0.7
        relations["Populares"]["Optimates"] = -0.7
        
        # Military generally supported by Optimates but variable with Populares
        relations["Military"]["Optimates"] = 0.3
        relations["Optimates"]["Military"] = 0.3
        relations["Military"]["Populares"] = random.uniform(-0.3, 0.3)
        relations["Populares"]["Military"] = relations["Military"]["Populares"]
        
        # Religious faction generally conservative, aligned with Optimates
        relations["Religious"]["Optimates"] = 0.5
        relations["Optimates"]["Religious"] = 0.5
        relations["Religious"]["Populares"] = -0.2
        relations["Populares"]["Religious"] = -0.2
        
        # Merchant class had variable relationships
        relations["Merchant"]["Optimates"] = random.uniform(-0.1, 0.4)
        relations["Optimates"]["Merchant"] = relations["Merchant"]["Optimates"]
        relations["Merchant"]["Populares"] = random.uniform(-0.1, 0.4)
        relations["Populares"]["Merchant"] = relations["Merchant"]["Populares"]
        relations["Merchant"]["Military"] = 0.2  # Suppliers to military
        relations["Military"]["Merchant"] = 0.2
        
        # Default neutral relationships for any unspecified pairs
        for faction1 in ["Optimates", "Populares", "Military", "Religious", "Merchant"]:
            for faction2 in ["Optimates", "Populares", "Military", "Religious", "Merchant"]:
                if faction1 != faction2 and relations[faction1][faction2] == 0:
                    relations[faction1][faction2] = random.uniform(-0.2, 0.2)
        
        return relations
    
    def _calculate_faction_influence(self) -> Dict[str, float]:
        """
        Calculate the current influence of each faction based on their senators.
        
        Returns:
            Dict: Faction name to influence score mapping
        """
        influence = defaultdict(float)
        faction_counts = defaultdict(int)
        
        # Sum influence of all senators by faction
        for senator in self.senators:
            faction = senator.get("faction", "Independent")
            senator_influence = senator.get("influence", 1)
            influence[faction] += senator_influence
            faction_counts[faction] += 1
        
        # Normalize by faction size and add historical context
        for faction in influence:
            if faction_counts[faction] > 0:
                # Base influence is average of senators' influence
                avg_influence = influence[faction] / faction_counts[faction]
                
                # Historical context adjustments
                if faction == "Optimates" and self.year > -100:
                    # Optimates were losing power in the late Republic
                    avg_influence *= 0.9
                elif faction == "Populares" and self.year > -150:
                    # Populares gained power during the Gracchi reforms and after
                    avg_influence *= 1.2
                elif faction == "Military" and self.year > -107:
                    # Military influence grew substantially after Marius' reforms
                    avg_influence *= 1.3
                
                influence[faction] = avg_influence
        
        return influence
    
    def simulate_backroom_dealings(self, senators: List[Dict], topic: str, topic_category: str = None) -> Dict:
        """
        Simulate the backroom political negotiations that happen before formal debate.
        This models the informal discussions, deals, and alliances that were crucial
        in Roman politics.
        
        Args:
            senators: List of senators participating in the session
            topic: The topic being discussed
            topic_category: Category of the topic (e.g., Military, Religious)
            
        Returns:
            Dict: Outcome of backroom dealings including alliances formed and deals made
        """
        console.print("\n[bold yellow]BACKROOM POLITICAL DEALINGS[/]")
        console.print("Senators engage in private negotiations before the formal debate...")
        
        # Identify the most influential senators (top 25%)
        influential_senators = sorted(
            senators, 
            key=lambda s: s.get("influence", 0), 
            reverse=True
        )[:max(3, len(senators) // 4)]
        
        # Identify key stakeholders based on topic category
        stake_factors = {
            "Military Affairs": ["Military", "Optimates"],
            "Foreign Policy": ["Military", "Merchant"],
            "Domestic Policy": ["Populares", "Optimates"],
            "Religious Matters": ["Religious", "Optimates"],
            "Economic Policy": ["Merchant", "Populares"],
            "Legal Reforms": ["Optimates", "Populares"],
        }
        
        stakeholder_factions = stake_factors.get(topic_category, [])
        stakeholders = [s for s in senators if s.get("faction") in stakeholder_factions]
        
        # Select actors for backroom dealings - use IDs for deduplication since dicts aren't hashable
        influential_ids = {s.get("id"): s for s in influential_senators}
        stakeholder_ids = {s.get("id"): s for s in stakeholders[:5]}
        
        # Merge the dictionaries and get the combined list of senators
        all_actor_ids = {**influential_ids, **stakeholder_ids}
        backroom_actors = list(all_actor_ids.values())
        
        # Simulate private meetings between key actors
        meetings = []
        deals_made = []
        alliances_formed = []
        
        # Track which senators have met to avoid duplication
        met_pairs = set()
        
        # Process influential senators first
        for i, initiator in enumerate(backroom_actors):
            # Number of meetings initiated depends on influence
            meeting_count = min(3, max(1, initiator.get("influence", 5) // 2))
            
            for _ in range(meeting_count):
                # Select another senator to meet with (who hasn't been met yet)
                potential_targets = [
                    s for s in backroom_actors 
                    if s != initiator and (initiator.get("id", 0), s.get("id", 0)) not in met_pairs
                ]
                
                if not potential_targets:
                    continue
                
                # Prefer senators from aligned factions or with complementary interests
                weighted_targets = []
                for target in potential_targets:
                    weight = 1.0  # Base weight
                    
                    # Increase weight for same faction
                    if target.get("faction") == initiator.get("faction"):
                        weight += 1.0
                    
                    # Adjust weight based on faction relations
                    faction_relation = self.faction_relations[initiator.get("faction", "")][target.get("faction", "")]
                    weight += faction_relation * 2
                    
                    # Adjust weight based on personal relationships or past favor exchanges
                    favor_owed = self.political_favors[target.get("id", 0)][initiator.get("id", 0)]
                    if favor_owed > 0:
                        weight += favor_owed * 3  # Strong incentive to meet with those who owe favors
                    
                    # Only include positive weights
                    if weight > 0:
                        weighted_targets.append((target, weight))
                
                if not weighted_targets:
                    continue
                
                # Select target based on weights
                targets, weights = zip(*weighted_targets)
                target = random.choices(targets, weights=weights, k=1)[0]
                
                # Record the meeting
                met_pairs.add((initiator.get("id", 0), target.get("id", 0)))
                met_pairs.add((target.get("id", 0), initiator.get("id", 0)))
                
                # Determine meeting outcome
                meeting_result = self._simulate_private_meeting(initiator, target, topic)
                meetings.append(meeting_result)
                
                # Process any deals or alliances formed
                if meeting_result.get("deal_made"):
                    deals_made.append(meeting_result.get("deal_details"))
                
                if meeting_result.get("alliance_formed"):
                    alliances_formed.append(meeting_result.get("alliance_details"))
        
        # Compile and display results
        outcome = {
            "meetings": meetings,
            "deals_made": deals_made,
            "alliances_formed": alliances_formed,
            "influential_senators": [s["name"] for s in influential_senators],
            "stakeholder_factions": stakeholder_factions
        }
        
        self.backroom_outcomes = outcome
        
        # Display a summary of the backroom dealings
        self._display_backroom_dealings_summary(outcome)
        
        return outcome
    
    def _simulate_private_meeting(self, senator1: Dict, senator2: Dict, topic: str) -> Dict:
        """
        Simulate a private political meeting between two senators.
        
        Args:
            senator1: The initiating senator
            senator2: The responding senator
            topic: The topic being discussed
            
        Returns:
            Dict: Details of the meeting outcome
        """
        # Determine the stance of each senator on the topic
        # This is highly simplified - in a real implementation this would use more factors
        s1_faction = senator1.get("faction", "Independent")
        s2_faction = senator2.get("faction", "Independent")
        
        s1_stance = random.choices(
            ["support", "oppose", "neutral"],
            weights=[0.6, 0.3, 0.1] if s1_faction == "Populares" else
                    [0.3, 0.6, 0.1] if s1_faction == "Optimates" else
                    [0.4, 0.4, 0.2],
            k=1
        )[0]
        
        s2_stance = random.choices(
            ["support", "oppose", "neutral"],
            weights=[0.6, 0.3, 0.1] if s2_faction == "Populares" else
                    [0.3, 0.6, 0.1] if s2_faction == "Optimates" else
                    [0.4, 0.4, 0.2],
            k=1
        )[0]
        
        # Determine if they agree or disagree
        agreement = s1_stance == s2_stance
        
        # Calculate deal probability based on multiple factors
        deal_prob = 0.2  # Base probability
        
        # Modify based on agreement/disagreement
        if agreement:
            deal_prob += 0.3  # Easier to make deals when in agreement
        else:
            deal_prob += 0.1  # Harder but still possible to compromise
        
        # Factor in corruption - corrupt senators more likely to make deals
        # Ensure traits dictionary exists and has valid corruption values
        traits1 = senator1.get("traits", {}) or {}
        traits2 = senator2.get("traits", {}) or {}
        corruption1 = traits1.get("corruption", 0.1)
        corruption2 = traits2.get("corruption", 0.1)
        # Handle potential None values
        corruption1 = 0.1 if corruption1 is None else corruption1
        corruption2 = 0.1 if corruption2 is None else corruption2
        avg_corruption = (corruption1 + corruption2) / 2
        deal_prob += avg_corruption * 0.5
        
        # Check if a deal is made
        deal_made = random.random() < deal_prob
        deal_details = None
        alliance_formed = False
        alliance_details = None
        favor_exchanged = False
        favor_details = None
        
        if deal_made:
            # Generate deal details
            deal_type = random.choice([
                "vote_exchange", "amendment_support", "speaking_opportunity", 
                "favor_exchange", "resource_allocation"
            ])
            
            # Determine details based on deal type
            if deal_type == "vote_exchange":
                deal_details = {
                    "type": "vote_exchange",
                    "description": f"{senator1['name']} agrees to support {senator2['name']}'s position on a future matter in exchange for support on this issue.",
                    "participants": [senator1['name'], senator2['name']],
                    "favor_created": True
                }
                # Record the political favor
                self._create_political_favor(senator2["id"], senator1["id"], 0.3)
                favor_exchanged = True
                favor_details = deal_details
                
            elif deal_type == "amendment_support":
                deal_details = {
                    "type": "amendment_support",
                    "description": f"{senator1['name']} and {senator2['name']} agree to cooperate on an amendment to the proposal.",
                    "participants": [senator1['name'], senator2['name']],
                    "amendment": True
                }
                
            elif deal_type == "speaking_opportunity":
                deal_details = {
                    "type": "speaking_opportunity",
                    "description": f"{senator1['name']} offers {senator2['name']} a prime speaking slot in exchange for adjusting their position.",
                    "participants": [senator1['name'], senator2['name']],
                    "favor_created": True
                }
                # Record the political favor
                self._create_political_favor(senator2["id"], senator1["id"], 0.2)
                favor_exchanged = True
                favor_details = deal_details
                
            elif deal_type == "favor_exchange":
                # One senator calls in an existing favor or creates a new one
                if self.political_favors[senator2["id"]][senator1["id"]] > 0:
                    # Senator2 owes senator1 a favor, which is being called in
                    favor_value = self.political_favors[senator2["id"]][senator1["id"]]
                    deal_details = {
                        "type": "favor_called_in",
                        "description": f"{senator1['name']} calls in a previous favor owed by {senator2['name']}.",
                        "participants": [senator1['name'], senator2['name']],
                        "favor_value": favor_value,
                        "favor_resolved": True
                    }
                    # Reduce or clear the favor
                    self.political_favors[senator2["id"]][senator1["id"]] = max(0, favor_value - 0.3)
                else:
                    # Create a new favor
                    deal_details = {
                        "type": "new_favor_created",
                        "description": f"{senator1['name']} does a favor for {senator2['name']}, creating a political debt.",
                        "participants": [senator1['name'], senator2['name']],
                        "favor_created": True
                    }
                    # Record the political favor
                    self._create_political_favor(senator2["id"], senator1["id"], 0.4)
                
                favor_exchanged = True
                favor_details = deal_details
                
            elif deal_type == "resource_allocation":
                deal_details = {
                    "type": "resource_allocation",
                    "description": f"{senator1['name']} and {senator2['name']} negotiate allocation of resources related to the proposal.",
                    "participants": [senator1['name'], senator2['name']],
                    "bribery": avg_corruption > 0.5
                }
            
            # Determine if this deal constitutes a political alliance
            if deal_type in ["vote_exchange", "amendment_support"] and random.random() < 0.3:
                alliance_formed = True
                alliance_details = {
                    "members": [senator1['name'], senator2['name']],
                    "factions": [senator1['faction'], senator2['faction']],
                    "purpose": "short_term_cooperation" if deal_type == "vote_exchange" else "amendment_coalition",
                    "description": f"A temporary political alliance between {senator1['name']} and {senator2['name']} to {'exchange support' if deal_type == 'vote_exchange' else 'coordinate on amendments'}."
                }
        
        # Return the meeting results
        return {
            "initiator": senator1["name"],
            "responder": senator2["name"],
            "factions": [senator1["faction"], senator2["faction"]],
            "agreement": agreement,
            "deal_made": deal_made,
            "deal_details": deal_details,
            "alliance_formed": alliance_formed,
            "alliance_details": alliance_details,
            "favor_exchanged": favor_exchanged,
            "favor_details": favor_details
        }
    
    def _create_political_favor(self, debtor_id: int, benefactor_id: int, intensity: float):
        """
        Create or increase a political favor debt between senators.
        
        Args:
            debtor_id: ID of the senator who owes the favor
            benefactor_id: ID of the senator to whom the favor is owed
            intensity: Strength of the favor (0.1 to 1.0)
        """
        # Cap the intensity at 1.0
        capped_intensity = min(1.0, intensity)
        
        # Add to existing favor debt (if any)
        current_debt = self.political_favors[debtor_id][benefactor_id]
        self.political_favors[debtor_id][benefactor_id] = min(1.0, current_debt + capped_intensity)
        
        logger.log_response(f"Political favor created: Senator {debtor_id} now owes Senator {benefactor_id} a favor of intensity {self.political_favors[debtor_id][benefactor_id]:.1f}")
    
    def _display_backroom_dealings_summary(self, outcome: Dict):
        """
        Display a summary of backroom political dealings.
        
        Args:
            outcome: Dictionary containing results of backroom dealings
        """
        # Create a table for significant meetings
        meetings_table = Table(title="Notable Backroom Meetings")
        meetings_table.add_column("Senators Involved", style="cyan")
        meetings_table.add_column("Result", style="yellow")
        
        # Add the most significant meetings (deals or alliances)
        significant_meetings = [m for m in outcome["meetings"] if m["deal_made"] or m["alliance_formed"]]
        
        for meeting in significant_meetings[:5]:  # Show up to 5 meetings
            senators = f"{meeting['initiator']} & {meeting['responder']}"
            
            if meeting["deal_made"]:
                result = meeting["deal_details"]["description"]
            elif meeting["alliance_formed"]:
                result = meeting["alliance_details"]["description"]
            else:
                result = "Discussed the upcoming debate"
                
            meetings_table.add_row(senators, result)
        
        console.print(meetings_table)
        
        # Display alliances if any formed
        if outcome["alliances_formed"]:
            console.print("\n[bold cyan]Political Alliances Formed:[/]")
            for alliance in outcome["alliances_formed"]:
                console.print(f"• {', '.join(alliance['members'])} - {alliance['description']}")
        
        # Show influential factions based on the topic
        console.print("\n[bold cyan]Faction Interests:[/]")
        for faction in outcome["stakeholder_factions"]:
            influence = self.faction_influence.get(faction, 0)
            corruption = self.faction_corruption.get(faction, 0)
            
            stance = "strongly interested in" if influence > 7 else "concerned with"
            methods = "using their significant influence" if influence > 7 else "through political maneuvering"
            corruption_note = " (willing to use bribes)" if corruption > 0.6 else ""
            
            console.print(f"• The [bold]{faction}[/] faction is {stance} this matter, {methods}{corruption_note}.")
    
    def generate_amendment(self, senator: Dict, original_topic: str, faction_stances: Dict) -> Dict:
        """
        Generate an amendment to the original proposal based on political interests.
        
        In the Roman Senate, amendments were a key way to alter proposals to better
        align with certain factional interests or to build broader support.
        
        Args:
            senator: The senator proposing the amendment
            original_topic: The original proposal topic
            faction_stances: Dictionary of faction stances on the original topic
            
        Returns:
            Dict: Amendment details including text, intent, and likely support
        """
        # Determine senator's stance based on faction
        senator_faction = senator.get("faction", "Independent")
        senator_stance = faction_stances.get(senator_faction, "neutral")
        
        # Determine amendment type based on stance and traits
        corruption = senator.get("traits", {}).get("corruption", 0.1)
        loyalty = senator.get("traits", {}).get("loyalty", 0.5)
        
        # Calculate amendment intent
        if senator_stance == "support":
            if corruption > 0.7:
                # Corrupt supporter seeks personal benefit
                intent = "strengthen_with_benefits"
            elif loyalty > 0.7:
                # Loyal supporter seeks to enhance
                intent = "strengthen_broadly"
            else:
                # General supporter
                intent = "clarify_supportively"
        elif senator_stance == "oppose":
            if corruption > 0.7:
                # Corrupt opponent seeks to redirect benefits
                intent = "redirect_benefits"
            elif loyalty > 0.7:
                # Loyal opponent seeks to weaken
                intent = "weaken_substantially"
            else:
                # General opponent
                intent = "limit_scope"
        else:  # neutral
            if corruption > 0.5:
                # Corrupt neutral seeks opportunity
                intent = "insert_unrelated_benefits"
            else:
                # General neutral seeks compromise
                intent = "moderate_compromise"
        
        # Generate amendment text based on intent
        amendment_prefix = random.choice([
            f"provided that",
            f"on condition that",
            f"with the stipulation that",
            f"except that",
            f"with the following amendments:"
        ])
        
        amendment_text = None
        
        if intent == "strengthen_with_benefits":
            amendment_text = f"{amendment_prefix} additional provisions be made for {senator_faction} interests, specifically in areas of oversight and resource allocation"
            
        elif intent == "strengthen_broadly":
            amendment_text = f"{amendment_prefix} the scope be expanded to include additional {senator_faction} priorities while maintaining the core proposal"
            
        elif intent == "clarify_supportively":
            amendment_text = f"{amendment_prefix} specific language be added to clarify implementation procedures to ensure effective execution"
            
        elif intent == "redirect_benefits":
            amendment_text = f"{amendment_prefix} all benefits and resources provided shall be administered by a committee with {senator_faction} representation"
            
        elif intent == "weaken_substantially":
            amendment_text = f"{amendment_prefix} the proposal's scope be significantly reduced and subject to annual review by the Senate"
            
        elif intent == "limit_scope":
            amendment_text = f"{amendment_prefix} the application be limited to specific regions and circumstances to be determined by Senate committee"
            
        elif intent == "insert_unrelated_benefits":
            amendment_text = f"{amendment_prefix} additional funding be allocated for {random.choice(['public works', 'military provisions', 'religious ceremonies', 'grain distribution'])} in regions supporting the {senator_faction}"
            
        elif intent == "moderate_compromise":
            amendment_text = f"{amendment_prefix} a balanced approach be taken, incorporating reasonable concerns from both supporting and opposing factions"
        
        # Calculate probable support from different factions
        faction_support = {}
        for faction, stance in faction_stances.items():
            # Base support is neutral (0.5)
            support = 0.5
            
            # Adjust based on relationship with proposing faction
            relationship = self.faction_relations[faction][senator_faction]
            support += relationship * 0.2
            
            # Adjust based on original stance
            if stance == "support":
                # Supporting factions more likely to support amendments from supporters
                if senator_stance == "support":
                    support += 0.2
                else:
                    support -= 0.2
            elif stance == "oppose":
                # Opposing factions more likely to support amendments from opponents
                if senator_stance == "oppose":
                    support += 0.2
                else:
                    support -= 0.1
            
            # Adjust based on amendment intent
            if intent.startswith("strengthen") and stance == "support":
                support += 0.1
            elif intent.startswith("weaken") and stance == "oppose":
                support += 0.1
            elif intent == "moderate_compromise":
                support += 0.05  # Small boost for compromises
            
            # Cap between 0 and 1
            faction_support[faction] = max(0.0, min(1.0, support))
        
        # Create amendment record
        amendment = {
            "proposer": senator["name"],
            "proposer_faction": senator_faction,
            "original_topic": original_topic,
            "amendment_text": amendment_text,
            "intent": intent,
            "likely_support": faction_support,
            "corruption_involved": corruption > 0.6,
            "personal_benefit": corruption > 0.5,
            "timestamp": time.time()
        }
        
        # Add to amendments list
        self.amendments.append(amendment)
        
        return amendment
    
    def process_faction_stance(self, faction: str, topic: str, amendments: List[Dict]) -> Dict:
        """
        Determine how a faction reacts to a set of amendments on a topic.
        
        Args:
            faction: The faction name
            topic: The original topic
            amendments: List of amendment dictionaries
            
        Returns:
            Dict: The faction's stance and reasoning
        """
        # Default initial stance is neutral
        initial_stance = 0.0  # -1.0 (oppose) to 1.0 (support)
        
        # Adjust for faction biases on topic categories
        if "military" in topic.lower():
            if faction == "Military":
                initial_stance += 0.6
            elif faction == "Merchant":
                initial_stance += 0.3  # Merchants often supported military spending (supplies)
                
        elif "tax" in topic.lower():
            if faction == "Merchant":
                initial_stance -= 0.4  # Merchants typically opposed new taxes
            elif faction == "Populares":
                initial_stance += 0.3  # Populares often supported taxes on wealthy
                
        elif "land" in topic.lower():
            if faction == "Optimates":
                initial_stance -= 0.5  # Optimates opposed land redistribution
            elif faction == "Populares":
                initial_stance += 0.7  # Populares strongly supported land reform
                
        elif "religious" in topic.lower():
            if faction == "Religious":
                initial_stance += 0.6  # Religious faction supported religious matters
                
        # Process influence of amendments
        amendment_effects = []
        
        for amendment in amendments:
            # Base effect starts neutral
            effect = 0.0
            
            # Proposer's faction relationship affects reception
            proposer_faction = amendment.get("proposer_faction")
            relationship = self.faction_relations[faction][proposer_faction]
            effect += relationship * 0.3
            
            # Check likely support from faction data in amendment
            direct_support = amendment.get("likely_support", {}).get(faction, 0.5)
            effect += (direct_support - 0.5) * 0.5  # Convert from 0-1 scale to -0.5 to 0.5 effect
            
            # Corruption-based modifications
            faction_corruptibility = self.faction_corruption.get(faction, 0.3)
            if amendment.get("corruption_involved") and faction_corruptibility > 0.4:
                effect += 0.2  # Corrupt factions more likely to support corrupt amendments
            
            # Record the effect
            reasoning = ""
            if effect > 0.3:
                reasoning = f"strongly supports the amendment by {amendment['proposer']}"
            elif effect > 0.1:
                reasoning = f"moderately supports the amendment by {amendment['proposer']}"
            elif effect < -0.3:
                reasoning = f"strongly opposes the amendment by {amendment['proposer']}"
            elif effect < -0.1:
                reasoning = f"moderately opposes the amendment by {amendment['proposer']}"
            else:
                reasoning = f"is neutral toward the amendment by {amendment['proposer']}"
                
            amendment_effects.append({
                "amendment_proposer": amendment["proposer"],
                "effect": effect,
                "reasoning": reasoning
            })
            
            # Update stance based on amendment
            initial_stance += effect
        
        # Normalize final stance to -1 to 1 range
        final_stance = max(-1.0, min(1.0, initial_stance))
        
        # Convert numerical stance to categorical
        if final_stance > 0.3:
            stance_category = "support"
        elif final_stance < -0.3:
            stance_category = "oppose"
        else:
            stance_category = "neutral"
        
        # Process reasoning
        if not amendment_effects:
            primary_reasoning = "based on faction interests"
        else:
            # Sort by absolute effect value to find most significant
            most_significant = sorted(amendment_effects, key=lambda x: abs(x["effect"]), reverse=True)[0]
            primary_reasoning = most_significant["reasoning"]
        
        return {
            "faction": faction,
            "original_stance_value": initial_stance,
            "final_stance_value": final_stance,
            "stance": stance_category,
            "amendment_effects": amendment_effects,
            "primary_reasoning": primary_reasoning
        }
    
    def resolve_political_favors(self, senator: Dict, favor_target: Dict, intensity: float) -> Dict:
        """
        Resolve a political favor being called in from one senator to another.
        
        Args:
            senator: The senator calling in the favor
            favor_target: The senator from whom the favor is being called
            intensity: The size of the favor being requested (0.1 to 1.0)
            
        Returns:
            Dict: The result of the favor request
        """
        # Get current favor balance
        target_id = favor_target.get("id", 0)
        senator_id = senator.get("id", 0)
        
        existing_favor = self.political_favors[target_id][senator_id]
        
        # Determine if the favor can be fulfilled
        can_fulfill = existing_favor >= intensity
        
        # Calculate compliance probability
        compliance_prob = min(1.0, existing_favor)  # Base on existing favor
        
        # Adjust for loyalty
        target_loyalty = favor_target.get("traits", {}).get("loyalty", 0.5)
        compliance_prob *= (0.5 + target_loyalty)  # Loyal senators more likely to honor favors
        
        # Determine outcome
        complies = random.random() < compliance_prob
        
        # Update favor tracking
        if complies:
            # Reduce favor owed by the intensity used
            self.political_favors[target_id][senator_id] = max(0, existing_favor - intensity)
            
            # There's a small chance a counter-favor is created
            if random.random() < 0.2:
                self._create_political_favor(senator_id, target_id, intensity * 0.5)
                counter_favor = True
            else:
                counter_favor = False
        else:
            # Failed to comply, but favor is still partially reduced
            self.political_favors[target_id][senator_id] = max(0, existing_favor - (intensity * 0.3))
            
            # Relationship deteriorates
            relationship_impact = -0.2
            counter_favor = False
        
        # Generate result description
        favor_size = "significant" if intensity > 0.6 else "moderate" if intensity > 0.3 else "small"
        
        if complies:
            if counter_favor:
                result_description = f"{favor_target['name']} honors the {favor_size} favor requested by {senator['name']}, but expects support in return."
            else:
                result_description = f"{favor_target['name']} honors the {favor_size} favor requested by {senator['name']}."
        else:
            result_description = f"{favor_target['name']} refuses to honor the {favor_size} favor requested by {senator['name']}, straining their relationship."
        
        return {
            "requester": senator["name"],
            "target": favor_target["name"],
            "intensity": intensity,
            "favor_size": favor_size,
            "existing_favor": existing_favor,
            "complies": complies,
            "counter_favor": counter_favor if complies else False,
            "remaining_favor": self.political_favors[target_id][senator_id],
            "result_description": result_description
        }
    
    def display_political_outcome(self, negotiations: Dict, amendments: List[Dict]) -> None:
        """
        Display the results of political maneuvering and amendments in a visually
        engaging way.
        
        Args:
            negotiations: Outcomes of backroom negotiations
            amendments: List of amendments proposed
        """
        console.print("\n[bold yellow]POLITICAL MANEUVERING OUTCOMES[/]")
        
        # Display amendment outcomes
        if amendments:
            amendments_table = Table(title="Proposed Amendments")
            amendments_table.add_column("Proposer", style="cyan")
            amendments_table.add_column("Amendment", style="yellow")
            amendments_table.add_column("Likely Outcome", style="green")
            
            for amendment in amendments:
                # Calculate overall support
                support_values = amendment.get("likely_support", {}).values()
                avg_support = sum(support_values) / max(1, len(support_values))
                
                if avg_support > 0.7:
                    outcome = "[bold green]Likely to pass[/]"
                elif avg_support > 0.45:
                    outcome = "[yellow]Vote will be close[/]"
                else:
                    outcome = "[bold red]Likely to fail[/]"
                
                amendments_table.add_row(
                    f"{amendment['proposer']} ({amendment['proposer_faction']})",
                    amendment["amendment_text"],
                    outcome
                )
            
            console.print(amendments_table)
        
        # Display political alignments
        console.print("\n[bold cyan]Political Alignments:[/]")
        
        alliances = negotiations.get("alliances_formed", [])
        if alliances:
            for alliance in alliances:
                console.print(f"• Alliance between [bold]{', '.join(alliance['members'])}[/]: {alliance['description']}")
        else:
            console.print("• No formal alliances were formed during negotiations.")
        
        # Display significant deals
        deals = negotiations.get("deals_made", [])
        if deals:
            console.print("\n[bold cyan]Significant Political Deals:[/]")
            for deal in deals:
                console.print(f"• [bold]{', '.join(deal.get('participants', []))}[/]: {deal['description']}")
        
        # Display faction positions
        console.print("\n[bold cyan]Faction Positions After Maneuvering:[/]")
        
        # Process faction stances based on amendments
        factions = ["Optimates", "Populares", "Military", "Religious", "Merchant"]
        original_topic = amendments[0]["original_topic"] if amendments else "the proposal"
        
        for faction in factions:
            # Only show if we have amendments to process
            if amendments:
                stance = self.process_faction_stance(faction, original_topic, amendments)
                
                stance_text = {
                    "support": "[bold green]supports[/]",
                    "oppose": "[bold red]opposes[/]",
                    "neutral": "[yellow]is neutral toward[/]"
                }.get(stance["stance"], "[yellow]is neutral toward[/]")
                
                console.print(f"• The [bold]{faction}[/] faction {stance_text} the proposal. {stance['primary_reasoning']}.")
    
    def get_amendment_effects_on_voting(self, amendments: List[Dict], senators: List[Dict]) -> Dict[int, float]:
        """
        Calculate how amendments affect individual senators' voting probabilities.
        
        Args:
            amendments: List of amendment dictionaries
            senators: List of senator dictionaries
            
        Returns:
            Dict: Mapping of senator IDs to voting modifiers (-1.0 to 1.0)
        """
        voting_modifiers = {}
        
        for senator in senators:
            senator_id = senator.get("id", 0)
            faction = senator.get("faction", "Independent")
            
            # Start with no modification
            modifier = 0.0
            
            # Process each amendment's effect on this senator
            for amendment in amendments:
                # Check if this senator proposed the amendment
                if amendment.get("proposer") == senator.get("name"):
                    # Senators strongly support their own amendments
                    modifier += 0.3
                    continue
                
                # Check faction support for the amendment
                faction_support = amendment.get("likely_support", {}).get(faction, 0.5)
                
                # Convert from 0-1 scale to effect
                effect = (faction_support - 0.5) * 0.4  # Max effect ±0.2
                
                # Check for political favor effects
                proposer_name = amendment.get("proposer")
                proposer = next((s for s in senators if s.get("name") == proposer_name), None)
                
                if proposer:
                    proposer_id = proposer.get("id", 0)
                    
                    # Check if senator owes the proposer a favor
                    favor_owed = self.political_favors[senator_id][proposer_id]
                    if favor_owed > 0:
                        # Owing a favor increases likelihood of supporting their amendment
                        effect += favor_owed * 0.2  # Max +0.2 for a full favor
                
                # Add this amendment's effect to the total modifier
                modifier += effect
            
            # Cap the modifier between -0.5 and 0.5
            voting_modifiers[senator_id] = max(-0.5, min(0.5, modifier))
        
        return voting_modifiers

"""
Integration Notes:

To integrate this module with SenateSession:

1. In the SenateSession class:
   - Add a PoliticalManeuvering instance to the session
   - Call simulate_backroom_dealings() before debate begins
   - Call generate_amendment() after initial debate but before voting
   - Use get_amendment_effects_on_voting() to modify vote probabilities

2. Update the voting mechanism to account for political favor effects

3. Display political outcomes before the final vote using display_political_outcome()

Example integration points would be:
- After conduct_attendance_and_seating() but before conduct_debate()
- After conduct_debate() but before conduct_vote()
"""