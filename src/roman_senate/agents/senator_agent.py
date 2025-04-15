"""
Roman Senate AI Game
Senator Agent Module

This module defines the agent architecture for simulated senators.
Senators can generate speeches, vote on topics, and interject during
other senators' speeches with historically authentic reactions.
"""

import asyncio
import random
from typing import Dict, List, Optional, Tuple, Any

from ..utils.llm.base import LLMProvider
from ..core.interjection import Interjection, InterjectionType, InterjectionTiming, generate_fallback_interjection
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
        
    async def generate_interjection(
        self,
        speaker_name: str,
        speech_content: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Optional[Interjection]:
        """
        Generate an interjection in response to another senator's speech.
        
        Args:
            speaker_name: The name of the senator who is speaking
            speech_content: The content of the speech being responded to
            context: Additional context about the debate
            
        Returns:
            An Interjection object if the senator decides to interject, None otherwise
        """
        # First, determine if this senator should interject
        if not self._should_interject(speaker_name, speech_content):
            return None
            
        # Determine the type of interjection
        interjection_type = self._determine_interjection_type(speaker_name, speech_content)
        
        # Determine the timing of the interjection
        timing = self._determine_interjection_timing(interjection_type)
        
        # Generate interjection content using LLM
        latin_content, english_content = await self._generate_interjection_content(
            speaker_name,
            speech_content,
            interjection_type
        )
        
        # Create and return the interjection
        return Interjection(
            senator_name=self.name,
            type=interjection_type,
            latin_content=latin_content,
            english_content=english_content,
            target_senator=speaker_name,
            timing=timing,
            intensity=self._calculate_interjection_intensity(speaker_name, interjection_type),
            causes_disruption=interjection_type in [
                InterjectionType.PROCEDURAL,
                InterjectionType.EMOTIONAL
            ]
        )
    
    def _should_interject(self, speaker_name: str, speech_content: Dict[str, Any]) -> bool:
        """
        Determine whether this senator should interject during another's speech.
        
        Args:
            speaker_name: The name of the senator who is speaking
            speech_content: The content of the speech
            
        Returns:
            True if the senator should interject, False otherwise
        """
        # Don't interject during your own speech
        if speaker_name == self.name:
            return False
            
        # Base probability of interjection
        base_probability = 0.15  # 15% chance by default
        
        # Adjust based on relationship with speaker (stronger feelings = more likely to interject)
        relationship = self.memory.relationship_scores.get(speaker_name, 0)
        relationship_factor = abs(relationship) * 0.2  # Max +/- 0.2
        
        # Faction alignment affects interjection probability
        speaker_faction = speech_content.get('faction', '')
        if speaker_faction == self.faction:
            # More likely to interject positively for same faction
            if relationship >= 0:
                base_probability += 0.1
        else:
            # More likely to interject negatively for different faction
            if relationship < 0:
                base_probability += 0.15
                
        # Prominence affects willingness to speak up
        prominence = self.senator.get('prominence', 0.5)
        prominence_factor = (prominence - 0.5) * 0.1  # -0.05 to +0.05
        
        # Calculate final probability
        final_probability = min(0.7, max(0.05, base_probability + relationship_factor + prominence_factor))
        
        # Roll the dice
        return random.random() < final_probability
    
    def _determine_interjection_type(self, speaker_name: str, speech_content: Dict[str, Any]) -> InterjectionType:
        """
        Determine what type of interjection to make.
        
        Args:
            speaker_name: The name of the senator who is speaking
            speech_content: The content of the speech
            
        Returns:
            The type of interjection to make
        """
        relationship = self.memory.relationship_scores.get(speaker_name, 0)
        
        # Relationship strongly influences interjection type
        if relationship > 0.3:
            # Positive relationship - more likely to acclaim
            weights = {
                InterjectionType.ACCLAMATION: 0.6,
                InterjectionType.OBJECTION: 0.05,
                InterjectionType.PROCEDURAL: 0.15,
                InterjectionType.EMOTIONAL: 0.1,
                InterjectionType.COLLECTIVE: 0.1
            }
        elif relationship < -0.3:
            # Negative relationship - more likely to object
            weights = {
                InterjectionType.ACCLAMATION: 0.05,
                InterjectionType.OBJECTION: 0.6,
                InterjectionType.PROCEDURAL: 0.15,
                InterjectionType.EMOTIONAL: 0.15,
                InterjectionType.COLLECTIVE: 0.05
            }
        else:
            # Neutral relationship - balanced distribution
            weights = {
                InterjectionType.ACCLAMATION: 0.25,
                InterjectionType.OBJECTION: 0.25,
                InterjectionType.PROCEDURAL: 0.2,
                InterjectionType.EMOTIONAL: 0.15,
                InterjectionType.COLLECTIVE: 0.15
            }
            
        # Faction alignment also affects interjection type
        speaker_faction = speech_content.get('faction', '')
        speaker_stance = speech_content.get('stance', '')
        
        if speaker_faction == self.faction:
            # Same faction - more support, less opposition
            weights[InterjectionType.ACCLAMATION] *= 1.5
            weights[InterjectionType.OBJECTION] *= 0.5
        else:
            # Different faction - more opposition, less support
            weights[InterjectionType.ACCLAMATION] *= 0.5
            weights[InterjectionType.OBJECTION] *= 1.5
            
        # Match probability to weights
        total = sum(weights.values())
        normalized_weights = {k: v/total for k, v in weights.items()}
        
        # Random selection based on weights
        selection = random.random()
        cumulative = 0
        for interjection_type, weight in normalized_weights.items():
            cumulative += weight
            if selection <= cumulative:
                return interjection_type
                
        # Fallback
        return InterjectionType.ACCLAMATION
    
    def _determine_interjection_timing(self, interjection_type: InterjectionType) -> InterjectionTiming:
        """
        Determine when during the speech the interjection should occur.
        
        Args:
            interjection_type: The type of interjection
            
        Returns:
            The timing of the interjection
        """
        # Different timings for different types
        timing_weights = {
            InterjectionType.ACCLAMATION: {
                InterjectionTiming.BEGINNING: 0.1,
                InterjectionTiming.MIDDLE: 0.2,
                InterjectionTiming.END: 0.7,  # Most acclamations come at the end
            },
            InterjectionType.OBJECTION: {
                InterjectionTiming.BEGINNING: 0.2,
                InterjectionTiming.MIDDLE: 0.6,  # Most objections come during the speech
                InterjectionTiming.END: 0.2,
            },
            InterjectionType.PROCEDURAL: {
                InterjectionTiming.BEGINNING: 0.4,  # Procedural points often at beginning
                InterjectionTiming.MIDDLE: 0.4,
                InterjectionTiming.END: 0.2,
            },
            InterjectionType.EMOTIONAL: {
                InterjectionTiming.BEGINNING: 0.2,
                InterjectionTiming.MIDDLE: 0.5,
                InterjectionTiming.END: 0.3,
            },
            InterjectionType.COLLECTIVE: {
                InterjectionTiming.BEGINNING: 0.1,
                InterjectionTiming.MIDDLE: 0.3,
                InterjectionTiming.END: 0.6,  # Collective reactions often at end
            }
        }
        
        # Use appropriate weights for this interjection type
        weights = timing_weights.get(interjection_type, {
            InterjectionTiming.BEGINNING: 0.2,
            InterjectionTiming.MIDDLE: 0.5,
            InterjectionTiming.END: 0.3,
        })
        
        # Random selection based on weights
        selection = random.random()
        cumulative = 0
        for timing, weight in weights.items():
            cumulative += weight
            if selection <= cumulative:
                return timing
                
        # Fallback
        return InterjectionTiming.MIDDLE
    
    def _calculate_interjection_intensity(self, speaker_name: str, interjection_type: InterjectionType) -> float:
        """
        Calculate the intensity of the interjection.
        
        Args:
            speaker_name: The name of the senator who is speaking
            interjection_type: The type of interjection
            
        Returns:
            Intensity value between 0.0 and 1.0
        """
        # Base intensity depends on interjection type
        base_intensity = {
            InterjectionType.ACCLAMATION: 0.4,
            InterjectionType.OBJECTION: 0.6,
            InterjectionType.PROCEDURAL: 0.5,
            InterjectionType.EMOTIONAL: 0.8,
            InterjectionType.COLLECTIVE: 0.4
        }.get(interjection_type, 0.5)
        
        # Adjust based on relationship strength
        relationship = self.memory.relationship_scores.get(speaker_name, 0)
        relationship_factor = abs(relationship) * 0.3  # Strong feelings (positive or negative) intensify
        
        # Random variation
        random_factor = random.uniform(-0.1, 0.1)
        
        # Calculate final intensity
        intensity = base_intensity + relationship_factor + random_factor
        
        # Ensure within bounds
        return min(1.0, max(0.1, intensity))
    
    async def _generate_interjection_content(
        self,
        speaker_name: str,
        speech_content: Dict[str, Any],
        interjection_type: InterjectionType
    ) -> Tuple[str, str]:
        """
        Generate the content of the interjection using LLM.
        
        Args:
            speaker_name: The name of the senator who is speaking
            speech_content: The content of the speech
            interjection_type: The type of interjection
            
        Returns:
            Tuple of (latin_content, english_content)
        """
        # Create a descriptive prompt for the LLM
        prompt = f"""
        You are Senator {self.name}, a {self.faction} senator in the Roman Senate.
        Senator {speaker_name} from the {speech_content.get('faction', 'unknown')} faction is giving a speech.
        
        Generate a brief, historically authentic interjection in the style of a {interjection_type.value} reaction.
        Your interjection should be only 1-3 short sentences or phrases.
        
        For context:
        - Your stance on the topic: {self.current_stance if hasattr(self, 'current_stance') else 'unknown'}
        - Speaker's stance: {speech_content.get('stance', 'unknown')}
        - Your relationship with speaker: {self.memory.relationship_scores.get(speaker_name, 0):.2f} (-1.0 hostile to 1.0 friendly)
        
        Return ONLY your interjection in this exact format:
        LATIN: [Your interjection in Classical Latin]
        ENGLISH: [English translation of your interjection]
        """
        
        try:
            # Get response from LLM
            response = await self.llm_provider.generate_text(prompt)
            
            # Parse Latin and English content from response
            latin_content = ""
            english_content = ""
            
            lines = response.strip().split('\n')
            for line in lines:
                if line.startswith("LATIN:"):
                    latin_content = line[6:].strip()
                elif line.startswith("ENGLISH:"):
                    english_content = line[8:].strip()
            
            # Verify we have both parts
            if not latin_content or not english_content:
                # Use fallback if parsing failed
                fallback = generate_fallback_interjection(self.name, speaker_name, interjection_type)
                return fallback.latin_content, fallback.english_content
                
            return latin_content, english_content
            
        except Exception as e:
            # If LLM generation fails, use fallback
            fallback = generate_fallback_interjection(self.name, speaker_name, interjection_type)
            return fallback.latin_content, fallback.english_content
    
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