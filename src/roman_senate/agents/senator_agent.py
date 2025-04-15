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
            A tuple of (stance, reasoning) where stance is "support", "oppose", or "neutral"
            and reasoning explains the decision
        """
        # Generate the prompt for stance determination
        prompt = f"""
        You are {self.name}, a {self.faction} senator in the Roman Senate.
        Topic for debate: {topic}
        
        Based on your faction ({self.faction}) and your personality traits,
        what stance would you take on this topic: for, against, or neutral?
        Consider your past voting history and relationships with other senators.
        
        First provide your reasoning in 1-2 sentences, then on a new line
        return ONLY the word "for", "against", or "neutral".
        """
        
        # Get response from LLM
        response = await self.llm_provider.generate_text(prompt)
        
        # Parse response to extract reasoning and stance
        reasoning = ""
        stance_text = ""
        lines = response.strip().split('\n')
        
        if len(lines) > 1:
            # Multiple lines - take all but last as reasoning, last as stance
            reasoning = ' '.join(lines[:-1]).strip()
            stance_text = lines[-1].lower()
        else:
            # Single line - use same text for both
            reasoning = response.strip()
            stance_text = response.strip().lower()
        
        # Determine stance based on text keywords
        final_stance = "neutral"  # Default stance
        
        if "for" in stance_text or "support" in stance_text:
            final_stance = "support"
        elif "against" in stance_text or "oppose" in stance_text:
            final_stance = "oppose"
        
        # Save stance for later use
        self.current_stance = final_stance
        
        # Record the reasoning in memory
        self.memory.add_observation(f"Took {final_stance} position on '{topic}' because: {reasoning}")
        
        return final_stance, reasoning
    async def generate_speech(self, topic: str, context: Dict) -> Tuple[str, str, str, str]:
        """
        Generate a speech for the current debate topic, with separate Latin and English versions.
        
        Args:
            topic: The topic being debated
            context: Additional context about the debate
            
        Returns:
            A tuple of (speech, reasoning, latin_text, english_text) where:
            - speech is the combined text (for backward compatibility)
            - reasoning explains the rhetorical approach
            - latin_text is the Latin version of the speech
            - english_text is the English version of the speech
        """
        if not self.current_stance:
            await self.decide_stance(topic, context)
        
        # Generate the English speech first
        english_prompt = f"""
        You are {self.name}, a {self.faction} senator in the Roman Senate.
        Topic for debate: {topic}
        Your stance: {self.current_stance}
        
        Generate a brief speech (3-4 sentences) expressing your views on this topic in English.
        Your speech should reflect your faction's values and your personal style.
        
        After the speech, on a new line, briefly explain your rhetorical approach
        and why you chose it (1-2 sentences).
        """
        
        english_response = await self.llm_provider.generate_text(english_prompt)
        
        # Parse the response to separate English speech from reasoning
        english_parts = english_response.strip().split('\n\n', 1)
        if len(english_parts) > 1:
            english_text = english_parts[0].strip()
            reasoning = english_parts[1].strip()
        else:
            # If no clear separation, use the whole response as speech
            english_text = english_response.strip()
            reasoning = "Strategic approach based on faction interests and personal style."
        
        # Generate the Latin version of the speech
        latin_prompt = f"""
        You are a Classical Latin expert specialized in translating English to authentic Classical Latin.
        
        Translate the following English Roman Senate speech into authentic Classical Latin of the Republican era.
        
        Guidelines for your translation:
        1. Use Classical Latin vocabulary, syntax, and rhetorical devices from the Republican era
        2. Maintain the formal oratorical style appropriate for the Roman Senate
        5. Ensure it sounds like genuine Classical Latin that Cicero might have used
        Return ONLY the Latin translation, with no additional commentary or explanations.

        English speech:
        {english_text}
        """
        
        # Request Latin translation from LLM
        latin_text = await self.llm_provider.generate_text(latin_prompt)
        latin_text = latin_text.strip()
        
        # For backward compatibility, create a combined speech text
        speech = f"---LATIN---\n{latin_text}\n---ENGLISH---\n{english_text}"
        
        # Record the speech and reasoning in memory
        self.memory.record_debate_contribution(topic, self.current_stance, english_text)
        self.memory.add_observation(f"On topic '{topic}', used rhetorical approach: {reasoning}")
        
        return speech, reasoning, latin_text, english_text
        return speech, reasoning
    
    async def vote(self, topic: str, context: Dict) -> Tuple[str, str]:
        """
        Vote on the current topic based on stance and other factors.
        
        Args:
            topic: The topic being voted on
            context: Additional context about the vote
            
        Returns:
            A tuple of (vote_decision, reasoning) where vote_decision is "support" or "oppose"
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
            You were neutral during the debate, but now must vote either to support or oppose.
            
            First explain your reasoning in 1-2 sentences considering faction interests,
            political allies, and personal ambitions.
            
            Then on a new line, return ONLY the word "support" or "oppose".
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
                
            # Determine vote based on text keywords
            if "support" in vote_text or "for" in vote_text:
                vote_decision = "support"
            else:
                vote_decision = "oppose"
        else:
            vote_decision = self.current_stance
            reasoning = f"Consistent with my {self.current_stance} stance on this issue."
            
        # Record the vote in memory
        self.memory.record_vote(topic, vote_decision)
        self.memory.add_observation(f"Voted {vote_decision} on '{topic}' because: {reasoning}")
        
        return vote_decision, reasoning