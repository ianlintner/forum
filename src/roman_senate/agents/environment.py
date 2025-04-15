"""
Roman Senate AI Game
Agent Environment Module

This module defines the simulation environment for senate agents.
"""
from typing import Dict, List, Optional, Any
import asyncio
import json
from rich.console import Console
from ..utils.llm.base import LLMProvider
from .senator_agent import SenatorAgent

console = Console()

class SenateEnvironment:
    """
    Environment for agent-based simulation of the Roman Senate.
    
    This class manages the interactions between senator agents and simulates
    the senate environment, including debates and voting procedures.
    """
    
    def __init__(self, llm_provider: LLMProvider):
        """
        Initialize the senate environment.
        
        Args:
            llm_provider: The LLM provider to use for simulation
        """
        self.agents: List[SenatorAgent] = []
        self.llm_provider = llm_provider
        self.topics = []
        self.current_topic = None
        self.year = -100  # Default to 100 BCE
    
    def initialize_agents(self, senators: List[Dict[str, Any]]):
        """
        Initialize agents from a list of senators.
        
        Args:
            senators: List of senator dictionaries to create agents from
        """
        self.agents = [SenatorAgent(senator, self.llm_provider) for senator in senators]
        console.print(f"[green]✓[/] Initialized {len(self.agents)} senator agents")
    
    def set_topics(self, topics):
        """
        Set the topics for debate.
        
        Args:
            topics: List of topic objects, which can be either:
                  - Dictionaries with 'text' and 'category' keys
                  - Tuples of (text, category)
        """
        # Convert any tuples to dictionaries for consistent handling
        normalized_topics = []
        for topic in topics:
            if isinstance(topic, tuple) and len(topic) == 2:
                # Topic is a tuple of (text, category)
                text, category = topic
                normalized_topics.append({'text': text, 'category': category})
            else:
                # Topic is already a dictionary
                normalized_topics.append(topic)
                
        self.topics = normalized_topics
        console.print(f"[green]✓[/] Set {len(topics)} topics for debate")
    
    async def run_debate(self, topic, rounds: int = 3):
        """
        Run a debate on a given topic.
        
        Args:
            topic: The topic to debate (either a dict with 'text' and 'category' keys
                  or a tuple of (text, category))
            rounds: Number of debate rounds
            
        Returns:
            Dict containing debate results and voting outcome
        """
        # Handle both dictionary and tuple formats for topics
        if isinstance(topic, tuple) and len(topic) == 2:
            # Topic is a tuple of (text, category)
            topic_text, category = topic
            # Create a consistent topic dictionary for internal use
            self.current_topic = {'text': topic_text, 'category': category}
        else:
            # Topic is a dictionary
            topic_text = topic['text']
            category = topic['category']
            self.current_topic = topic
        
        # Clean any remaining JSON artifacts in the topic text
        clean_topic_text = self._clean_display_text(topic_text)
        
        console.print(f"\n[bold cyan]DEBATE TOPIC:[/] {clean_topic_text}")
        console.print(f"[bold cyan]CATEGORY:[/] {category}")
        
        # Setup debate context
        context = {
            "topic": clean_topic_text,  # Use cleaned text in the context
            "category": category,
            "year": self.year
        }
        
        # First, have agents decide their stances
        stances = {}
        console.print("\n[bold]Senators are considering their positions...[/]")
        
        # Gather stances with reasoning for all agents
        stance_reasoning = {}
        for agent in self.agents:
            stance, reasoning = await agent.decide_stance(topic_text, context)
            stances[agent.name] = stance
            stance_reasoning[agent.name] = reasoning
            console.print(f"[dim]• {agent.name} ({agent.faction}) takes a {stance} position:[/]")
            console.print(f"  [dim]{reasoning}[/dim]")
        
        # Run debate rounds
        speeches = []
        
        from ..core.debate import display_speech, score_argument
        
        for round_num in range(1, rounds + 1):
            console.print(f"\n[bold cyan]DEBATE ROUND {round_num}[/]")
            
            for agent in self.agents:
                speech_text, reasoning = await agent.generate_speech(topic_text, context)
                
                # Format speech data for traditional display
                speech_data = {
                    "senator": agent.name,
                    "senator_name": agent.name,
                    "faction": agent.faction,
                    "stance": stances[agent.name],
                    "speech": speech_text,
                    "reasoning": reasoning,
                    # Split the speech into Latin and English if it contains "---LATIN---" markers
                    "latin_text": self._extract_latin(speech_text),
                    "english_text": self._extract_english(speech_text),
                    "full_text": speech_text,  # For backward compatibility
                    "key_points": reasoning.split(". ")[:2] if reasoning else [],
                    "year": self.year,
                    "year_display": f"{abs(self.year)} BCE",
                    "speech_length": "3-4",  # Default values
                    "argument_quality": "sound and reasonable",
                    "rhetorical_flourishes": "2-3",
                    "quality_factor": 0.7,
                    "eloquence": 0.7,
                }
                
                # Add to speeches collection
                speeches.append(speech_data)
                
                # Display the speech using the traditional rich formatting
                senator_info = {"name": agent.name, "faction": agent.faction}
                display_speech(senator_info, speech_data, topic_text)
                
                # Score and display speech evaluation
                if speech_data["english_text"]:
                    score = score_argument(speech_data["english_text"], topic_text)
                else:
                    score = score_argument(speech_text, topic_text)
                
                # Display score
                console.print(f"[dim](Rhetorical approach: {reasoning})[/dim]")
                
                # Show the score as in traditional simulation
                from rich.table import Table
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
                
                # Simulate a short delay between speeches for readability
                await asyncio.sleep(0.5)
        
        # Run the vote
        console.print("\n[bold magenta]VOTING BEGINS[/]")
        vote_results = await self.run_vote(topic_text, context)
        
        return {
            "topic": topic,
            "stances": stances,
            "speeches": speeches,
            "vote_result": vote_results
        }
    
    async def run_vote(self, topic_text: str, context: Dict):
        """
        Run a vote on the current topic.
        
        Args:
            topic_text: The topic text
            context: Additional context
            
        Returns:
            Dict containing vote results
        """
        from ..core.vote import conduct_vote, display_vote_result
        from rich.progress import Progress, SpinnerColumn, TextColumn
        import random
        
        # Format votes in the same structure as the traditional simulation
        votes = {"for": 0, "against": 0, "abstain": 0}
        voting_record = []
        
        # Create a map of senator stances for context
        stances = {}
        for speech in context.get("previous_speeches", []):
            stances[speech.get("senator_name")] = speech.get("stance")
        
        # Format the voting introduction panel
        from rich.panel import Panel
        category = self.current_topic.get('category', '')
        
        # Create a more informative vote introduction
        if category:
            introduction = f"The Senate will now vote on a matter of [bold yellow]{category}[/]:\n[italic]{topic_text}[/]"
        else:
            introduction = f"The Senate will now vote on:\n[italic]{topic_text}[/]"
        
        # Display the vote panel with category context
        console.print(Panel(introduction, title="[bold magenta]SENATE VOTE BEGINS[/]", border_style="magenta", width=100))
        
        # Show progress of senators casting votes
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold]Senators are casting their votes...[/]"),
            console=console,
        ) as progress:
            task = progress.add_task("Voting...", total=len(self.agents))
            
            # Process votes for each senator
            for agent in self.agents:
                vote, reasoning = await agent.vote(topic_text, context)
                
                # Map the agent's vote to "for", "against", or "abstain"
                # The agent system only returns "for" or "against", but we'll add
                # a small chance of abstention for realism
                if random.random() < 0.05:  # 5% chance to abstain
                    final_vote = "abstain"
                else:
                    final_vote = vote
                
                # Update vote counts
                votes[final_vote] += 1
                
                # Add to voting record
                stance = stances.get(agent.name, "unknown")
                voting_record.append({
                    "senator": agent.name,
                    "faction": agent.faction,
                    "vote": final_vote,
                    "influence": agent.senator.get("influence", 5),
                    "debate_stance": stance
                })
                
                # Update progress
                progress.update(task, advance=1)
                await asyncio.sleep(0.1)  # Small delay for visual effect
        
        # Calculate outcome - passed if more "for" than "against"
        passed = votes["for"] > votes["against"]
        outcome = "PASSED" if passed else "REJECTED"
        
        # Create complete vote result object
        vote_result = {
            "topic": topic_text,
            "category": self.current_topic.get('category', ''),
            "votes": votes,
            "outcome": outcome,
            "passed": passed,
            "voting_record": voting_record,
            "total": sum(votes.values())
        }
        
        # Display detailed voting breakdown as in traditional simulation
        self._display_vote_breakdown(vote_result, stances)
        
        # Display the final result
        result_style = "green" if passed else "red"
        console.print(f"\nThe motion has been [bold {result_style}]{outcome}[/] ({votes['for']} to {votes['against']}).\n")
        
        return vote_result
        
    def _display_vote_breakdown(self, vote_result, debate_stances):
        """
        Display a detailed breakdown of votes similar to the traditional simulation.
        
        Args:
            vote_result: Vote result dictionary
            debate_stances: Dictionary mapping senator names to their debate stances
        """
        from rich.table import Table
        
        # Display voting results summary
        console.print("\n[bold yellow]Voting Results Summary:[/]")
        
        results_table = Table()
        results_table.add_column("Option", style="cyan")
        results_table.add_column("Votes", justify="right")
        results_table.add_column("Percentage", justify="right")
        
        total_votes = vote_result.get("total", 0)
        votes = vote_result["votes"]
        
        for option, count in votes.items():
            percentage = (count / total_votes) * 100 if total_votes > 0 else 0
            results_table.add_row(option.title(), str(count), f"{percentage:.1f}%")
        
        console.print(results_table)
        
        # Display detailed voting breakdown
        console.print("\n[bold yellow]Detailed Voting Breakdown:[/]")
        
        detailed_table = Table(title=f"Vote on: {vote_result['topic']}")
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
        sorted_record = sorted(vote_result["voting_record"], key=lambda x: (x["faction"], x["senator"]))
        
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
    
    async def run_simulation(self, senators: List[Dict[str, Any]], topics: List[Dict],
                           debate_rounds: int = 3, year: int = -100):
        """
        Run a full simulation of senate debates and votes.
        
        Args:
            senators: List of senator dictionaries
            topics: List of topic dicts
            debate_rounds: Number of debate rounds per topic
            year: Year of the simulation
            
        Returns:
            List of results for each topic
        """
        self.year = year
        self.initialize_agents(senators)
        self.set_topics(topics)
        
        results = []
        
        for i, topic in enumerate(self.topics):
            console.print(f"\n[bold cyan]===== TOPIC {i+1}/{len(self.topics)} =====[/]")
            topic_result = await self.run_debate(topic, debate_rounds)
            results.append(topic_result)
            
            # Update relationships based on voting alignment
            self._update_relationships(topic_result)
            
            # Brief pause between topics
            if i < len(self.topics) - 1:
                console.print("\n[bold]Moving to next topic...[/]")
                await asyncio.sleep(1)
        
        # After all topics, display relationship graph
        self._display_relationship_network()
        
        return results
        
    def _update_relationships(self, topic_result: Dict):
        """
        Update relationships between senators based on stance and voting alignment.
        
        Args:
            topic_result: The result dict from a debate topic
        """
        # Skip relationship updates if vote_result is missing required data
        if 'vote_result' not in topic_result or 'voting_record' not in topic_result['vote_result']:
            console.print("[dim]Skipping relationship updates due to missing voting data[/dim]")
            return
            
        # Extract voting records from the vote result
        voting_record = topic_result['vote_result']['voting_record']
        
        # Create a dictionary mapping senator names to their votes for easier lookup
        vote_map = {}
        for record in voting_record:
            vote_map[record['senator']] = record['vote']
        
        # For each pair of senators
        for i, agent1 in enumerate(self.agents):
            for j, agent2 in enumerate(self.agents[i+1:], i+1):
                # Calculate relationship change based on voting alignment
                change = 0
                
                # Only process if both senators have recorded votes
                if agent1.name in vote_map and agent2.name in vote_map:
                    # Positive change if they voted the same way
                    if vote_map[agent1.name] == vote_map[agent2.name]:
                        change = 0.2
                    else:
                        change = -0.1
                
                # Update each agent's relationship with the other
                agent1.memory.update_relationship(agent2.name, change)
                agent2.memory.update_relationship(agent1.name, change)
    
    def _display_relationship_network(self):
        """
        Display a simple text-based visualization of senator relationships.
        """
        console.print("\n[bold cyan]===== SENATOR RELATIONSHIPS =====[/]")
        console.print("[dim]A simple visualization of senator relationships based on voting patterns:[/]")
        
        # For each senator, display their top allies and rivals
        for agent in self.agents:
            # Get all relationships for this senator
            relationships = agent.memory.relationship_scores
            
            if not relationships:
                continue
                
            # Sort relationships by score
            sorted_relationships = sorted(
                relationships.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            # Display the top allies (positive scores) and rivals (negative scores)
            allies = [f"{name} (+{score:.1f})" for name, score in sorted_relationships if score > 0]
            rivals = [f"{name} ({score:.1f})" for name, score in sorted_relationships if score < 0]
            
            console.print(f"\n[bold]{agent.name} ({agent.faction})[/]")
            
            if allies:
                console.print(f"  [green]Allies:[/] {', '.join(allies[:3])}")
            if rivals:
                console.print(f"  [red]Rivals:[/] {', '.join(rivals[:3])}")
            
            # If no significant relationships yet
            if not allies and not rivals:
                console.print("  [dim]No strong relationships formed yet[/]")
                
    def _extract_latin(self, speech_text: str) -> str:
        """
        Extract Latin text from a speech that may contain Latin/English markers.
        
        Args:
            speech_text: The full speech text
            
        Returns:
            The Latin portion or a placeholder if not found
        """
        if not speech_text:
            return "Lorem ipsum dolor sit amet."
            
        # If the speech contains the Latin marker
        if "---LATIN---" in speech_text:
            sections = speech_text.split("---LATIN---")
            if len(sections) > 1:
                latin_english = sections[1].split("---ENGLISH---")
                if len(latin_english) > 0:
                    return latin_english[0].strip()
                    
        # If the speech doesn't have markers, just return a placeholder
        return "Lorem ipsum dolor sit amet."
        
    def _extract_english(self, speech_text: str) -> str:
        """
        Extract English text from a speech that may contain Latin/English markers.
        
        Args:
            speech_text: The full speech text
            
        Returns:
            The English portion or the full text if no markers found
        """
        if not speech_text:
            return ""
            
        # If the speech contains the English marker
        if "---ENGLISH---" in speech_text:
            sections = speech_text.split("---ENGLISH---")
            if len(sections) > 1:
                return sections[1].strip()
                
        # If no English marker, check if there's only a Latin marker
        elif "---LATIN---" in speech_text:
            sections = speech_text.split("---LATIN---")
            if len(sections) > 1 and len(sections) < 3:  # Should have at most 2 sections
                return speech_text  # Return the whole thing as English if unclear
                
        # If no markers at all, just return the text as English
        return speech_text
        
    def _clean_display_text(self, text: str) -> str:
        """
        Clean text for display by removing any JSON artifacts.
        
        Args:
            text: Original text which may contain JSON artifacts
            
        Returns:
            str: Cleaned text for display
        """
        if not text:
            return ""
            
        # If string looks like a JSON array (starts with '[' and ends with ']')
        if text.startswith('[') and text.endswith(']'):
            try:
                # Try to parse it as JSON
                parsed = json.loads(text)
                if isinstance(parsed, list):
                    # Return the first item if it's a list
                    if parsed and parsed[0]:
                        return str(parsed[0])
                    return ""
            except:
                pass
                
        # Remove common JSON artifacts
        cleaned = text.strip()
        cleaned = cleaned.lstrip('[ \'"').rstrip('] \'",.')
        cleaned = cleaned.replace('\\"', '"').replace('\\\'', '\'')
        
        # If it still looks like escaped JSON
        if '\\\"' in cleaned or '\\"]' in cleaned:
            # Try more aggressive cleaning
            cleaned = cleaned.replace('\\\"', '').replace('\\"]', '')
            cleaned = cleaned.replace('[\"', '').replace('\"]', '')
            
        return cleaned.strip()