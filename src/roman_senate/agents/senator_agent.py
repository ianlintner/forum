"""
Roman Senate AI Game
Senator Agent Module

This module defines the agent architecture for simulated senators.
"""

import asyncio
from typing import Dict, List, Optional, Tuple, Any

from ..utils.llm.base import LLMProvider
from .agent_memory import AgentMemory

class SenatorAgent:
    """
    Agent-based implementation of a Roman Senator.
    
    This class extends the senator dictionary with agent capabilities,
    including memory, decision-making, and interaction with other senators.
    """
    
    def __init__(self, senator: Dict[str, Any], llm_provider: LLMProvider):
        """
        Initialize a senator agent.
        
        Args:
            senator: The senator dictionary with properties like name, faction, etc.
            llm_provider: The LLM provider to use for generating responses
        """
        self.senator = senator
        self.memory = AgentMemory()
        self.llm_provider = llm_provider
        self.current_stance = None
        
    @property
    def name(self) -> str:
        """Get the senator's name."""
        return self.senator["name"]
        
    @property
    def faction(self) -> str:
        """Get the senator's faction."""
        return self.senator["faction"]
    
    async def decide_stance(self, topic: str, context: Dict) -> Tuple[str, str]:
        """
        Decide the stance on a given topic based on the senator's characteristics.
        
        Args:
            topic: The topic being debated
            context: Additional context about the topic
            
        Returns:
            A tuple of (stance, reasoning) where stance is "for", "against", or "neutral"
            and reasoning explains the decision
        """
        # This would typically use the LLM to decide the stance based on
        # senator personality, faction alignment, and memory of past interactions
        prompt = f"""
        You are {self.name}, a {self.faction} senator in the Roman Senate.
        Topic for debate: {topic}
        
        Based on your faction ({self.faction}) and your personality traits,
        what stance would you take on this topic: for, against, or neutral?
        Consider your past voting history and relationships with other senators.
        
        First provide your reasoning in 1-2 sentences, then on a new line
        return ONLY the word "for", "against", or "neutral".
        """
        
        response = await self.llm_provider.generate_text(prompt)
        
        # Parse the response to separate reasoning from stance
        lines = response.strip().split('\n')
        if len(lines) > 1:
            # Take all but the last line as reasoning
            reasoning = ' '.join(lines[:-1]).strip()
            stance_text = lines[-1].lower()
        else:
            # If no clear separation, use the whole response as both
            reasoning = response.strip()
            stance_text = response.strip().lower()
            
        # Normalize the stance
        if "for" in stance_text:
            stance = "for"
        elif "against" in stance_text:
            stance = "against"
        else:
            stance = "neutral"
            
        self.current_stance = stance
        
        # Record the reasoning in memory
        self.memory.add_observation(f"Took {stance} position on '{topic}' because: {reasoning}")
        
        return stance, reasoning
    
    async def generate_speech(self, topic: str, context: Dict) -> Tuple[str, str]:
        """
        Generate a speech for the current debate topic.
        
        Args:
            topic: The topic being debated
            context: Additional context about the debate
            
        Returns:
            A tuple of (speech, reasoning) where speech is the generated text
            and reasoning explains the rhetorical approach
        """
        if not self.current_stance:
            await self.decide_stance(topic, context)
            
        prompt = f"""
        You are {self.name}, a {self.faction} senator in the Roman Senate.
        Topic for debate: {topic}
        Your stance: {self.current_stance}
        
        Generate a brief speech (3-4 sentences) expressing your views on this topic.
        Your speech should reflect your faction's values and your personal style.
        
        After the speech, on a new line, briefly explain your rhetorical approach
        and why you chose it (1-2 sentences).
        """
        
        response = await self.llm_provider.generate_text(prompt)
        
        # Parse the response to separate speech from reasoning
        parts = response.strip().split('\n\n', 1)
        if len(parts) > 1:
            speech = parts[0].strip()
            reasoning = parts[1].strip()
        else:
            # If no clear separation, use the whole response as speech
            speech = response.strip()
            reasoning = "Strategic approach based on faction interests and personal style."
        
        # Record the speech and reasoning in memory
        self.memory.record_debate_contribution(topic, self.current_stance, speech)
        self.memory.add_observation(f"On topic '{topic}', used rhetorical approach: {reasoning}")
        
        return speech, reasoning
    
    async def vote(self, topic: str, context: Dict) -> Tuple[str, str]:
        """
        Vote on the current topic based on stance and other factors.
        
        Args:
            topic: The topic being voted on
            context: Additional context about the vote
            
        Returns:
            A tuple of (vote_decision, reasoning) where vote_decision is "for" or "against"
            and reasoning explains the decision
        """
        # If we haven't decided a stance yet, do so now
        if not self.current_stance:
            await self.decide_stance(topic, context)
            
        # For now, the vote aligns with the stance unless it was neutral
        if self.current_stance == "neutral":
            # Neutral senators need to make a final decision
            prompt = f"""
            You are {self.name}, a {self.faction} senator in the Roman Senate.
            Topic for vote: {topic}
            You were neutral during the debate, but now must vote either for or against.
            
            First explain your reasoning in 1-2 sentences considering faction interests,
            political allies, and personal ambitions.
            
            Then on a new line, return ONLY the word "for" or "against".
            """
            
            response = await self.llm_provider.generate_text(prompt)
            
            # Parse the response to separate reasoning from vote
            lines = response.strip().split('\n')
            if len(lines) > 1:
                # Take all but the last line as reasoning
                reasoning = ' '.join(lines[:-1]).strip()
                vote_text = lines[-1].lower()
            else:
                # If no clear separation, use the whole response as both
                reasoning = f"Decision based on {self.faction} faction interests."
                vote_text = response.strip().lower()
                
            vote_decision = "for" if "for" in vote_text else "against"
        else:
            vote_decision = self.current_stance
            reasoning = f"Consistent with my {self.current_stance} stance on this issue."
            
        # Record the vote in memory
        self.memory.record_vote(topic, vote_decision)
        self.memory.add_observation(f"Voted {vote_decision} on '{topic}' because: {reasoning}")
        
        return vote_decision, reasoning