"""
Roman Senate AI Game
Agent Environment Module

This module defines the simulation environment for senate agents.
"""
from typing import Dict, List, Optional, Any
import asyncio
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
    
    def set_topics(self, topics: List[Dict]):
        """
        Set the topics for debate.
        
        Args:
            topics: List of topic objects with 'text' and 'category' keys
        """
        self.topics = topics
        console.print(f"[green]✓[/] Set {len(topics)} topics for debate")
    
    async def run_debate(self, topic: Dict, rounds: int = 3):
        """
        Run a debate on a given topic.
        
        Args:
            topic: The topic to debate (dict with 'text' and 'category')
            rounds: Number of debate rounds
            
        Returns:
            Dict containing debate results and voting outcome
        """
        topic_text = topic['text']
        category = topic['category']
        self.current_topic = topic
        
        console.print(f"\n[bold cyan]DEBATE TOPIC:[/] {topic_text}")
        console.print(f"[bold cyan]CATEGORY:[/] {category}")
        
        # Setup debate context
        context = {
            "topic": topic_text,
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
        
        for round_num in range(1, rounds + 1):
            console.print(f"\n[bold cyan]DEBATE ROUND {round_num}[/]")
            
            for agent in self.agents:
                speech, reasoning = await agent.generate_speech(topic_text, context)
                speeches.append({
                    "senator": agent.name,
                    "faction": agent.faction,
                    "stance": stances[agent.name],
                    "speech": speech,
                    "reasoning": reasoning
                })
                
                console.print(f"[bold]{agent.name} ({agent.faction}) | {stances[agent.name].upper()}:[/]")
                console.print(f"{speech}")
                console.print(f"[dim](Rhetorical approach: {reasoning})[/dim]\n")
                
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
        votes = {"for": 0, "against": 0, "senators": {}, "reasoning": {}}
        
        for agent in self.agents:
            vote, reasoning = await agent.vote(topic_text, context)
            votes["senators"][agent.name] = vote
            votes["reasoning"][agent.name] = reasoning
            
            if vote == "for":
                votes["for"] += 1
            else:
                votes["against"] += 1
                
            console.print(f"[dim]• {agent.name} votes {vote}:[/]")
            console.print(f"  [dim italic]{reasoning}[/dim italic]")
        
        # Determine the outcome
        total_votes = votes["for"] + votes["against"]
        votes["total"] = total_votes
        votes["passed"] = votes["for"] > votes["against"]
        
        # Display the result
        if votes["passed"]:
            result = f"[bold green]PASSED[/] ({votes['for']} to {votes['against']})"
        else:
            result = f"[bold red]REJECTED[/] ({votes['for']} to {votes['against']})"
            
        console.print(f"\n[bold]VOTE RESULT:[/] {result}")
        
        return votes
    
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
        # Extract votes
        votes = topic_result['vote_result']['senators']
        
        # For each pair of senators
        for i, agent1 in enumerate(self.agents):
            for j, agent2 in enumerate(self.agents[i+1:], i+1):
                # Calculate relationship change based on voting alignment
                change = 0
                
                # Positive change if they voted the same way
                if votes[agent1.name] == votes[agent2.name]:
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