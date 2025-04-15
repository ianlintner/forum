"""
Mock LLM provider for testing purposes.
This provider returns predefined responses instead of making actual API calls.
"""

import json
import logging
import os
import random
from typing import Dict, List, Optional, Union, Any

from .base import LLMProvider

logger = logging.getLogger(__name__)

class MockProvider(LLMProvider):
    """
    Mock LLM provider for testing and CI environments.
    Returns predetermined responses without making external API calls.
    """

    def __init__(self, **kwargs):
        """Initialize the mock provider with optional custom responses."""
        super().__init__(**kwargs)
        logger.info("Initializing MockProvider for test mode")
        
        # Default mock responses for different prompt types
        self.mock_responses = {
            "topic": [
                "Should Rome expand its territories in Gaul?",
                "Should the grain dole be increased for the citizens of Rome?",
                "Should the Senate grant additional powers to the Consul?",
                "Should Rome form an alliance with the Kingdom of Parthia?",
                "Should the property requirements for military service be lowered?"
            ],
            "speech": [
                "Citizens of Rome, I stand before you today to argue that we must consider the welfare of all Romans in this matter. The republic was founded on principles of justice and equality under law. Let us not abandon these principles now.",
                "Senators, colleagues, friends - I speak to you not merely as a fellow senator, but as a Roman who holds dear the traditions of our ancestors. The mos maiorum must guide our decision today.",
                "The wisdom of our forefathers has served Rome well for centuries. To deviate from their example in this matter would be to invite disaster upon our republic.",
                "I ask you, what Roman worthy of the name could support such a proposal? It undermines the very foundations upon which our great republic stands!",
                "Let us consider the practical matters at hand. This proposal would strain our treasury, weaken our defenses, and embolden our enemies abroad."
            ],
            "interjection": [
                "Your words betray your lack of understanding in matters of state!",
                "I must remind the esteemed senator that Rome was not built on such reckless ideas!",
                "The senator speaks wisely and with the voice of reason!",
                "By Jupiter, I cannot remain silent in the face of such bold claims!",
                "The senator's argument has more holes than a fisherman's net!"
            ],
            "vote": {
                "result": "The motion passes with a majority vote.",
                "for": 12,
                "against": 8,
                "abstain": 3
            }
        }
        
        # Allow custom responses to be passed in
        if "custom_responses" in kwargs:
            self.mock_responses.update(kwargs["custom_responses"])
            
        # Add some randomization to make tests more realistic
        self.seed = int(os.environ.get("ROMAN_SENATE_TEST_SEED", "42"))
        random.seed(self.seed)
        logger.info(f"MockProvider initialized with seed {self.seed}")

    def generate_completion(self, prompt: str, **kwargs) -> str:
        """Generate a completion response based on the prompt type."""
        logger.info(f"Mock completion requested for prompt: {prompt[:50]}...")
        
        # Attempt to determine the type of response needed
        response_type = self._detect_prompt_type(prompt)
        
        # Get a random response for that type
        if response_type in self.mock_responses:
            if isinstance(self.mock_responses[response_type], list):
                return random.choice(self.mock_responses[response_type])
            else:
                return json.dumps(self.mock_responses[response_type])
                
        # Default fallback response
        return "Mock response for testing purposes."

    def generate_chat_completion(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """Generate a chat completion response."""
        logger.info(f"Mock chat completion requested with {len(messages)} messages")
        
        # Extract the last user message to determine response type
        last_message = messages[-1]["content"] if messages else ""
        response_type = self._detect_prompt_type(last_message)
        
        # Get a response for that type
        if response_type in self.mock_responses:
            if isinstance(self.mock_responses[response_type], list):
                content = random.choice(self.mock_responses[response_type])
            else:
                content = json.dumps(self.mock_responses[response_type])
        else:
            content = "Mock chat response for testing purposes."
            
        # Format as a chat completion response
        return {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": content
                    }
                }
            ]
        }
        
    async def generate_text(self, prompt: str, **kwargs) -> str:
        """Generate text asynchronously (mock implementation)."""
        logger.info(f"Mock async text generation requested for prompt: {prompt[:50]}...")
        return self.generate_completion(prompt, **kwargs)
        
    def _detect_prompt_type(self, prompt: str) -> str:
        """
        Attempt to determine the type of prompt to select an appropriate response.
        """
        prompt_lower = prompt.lower()
        
        if any(keyword in prompt_lower for keyword in ["topic", "debate", "issue", "question"]):
            return "topic"
        elif any(keyword in prompt_lower for keyword in ["speech", "address", "oration"]):
            return "speech"
        elif any(keyword in prompt_lower for keyword in ["interject", "interrupt", "interjection"]):
            return "interjection"
        elif any(keyword in prompt_lower for keyword in ["vote", "tally", "result"]):
            return "vote"
            
        # Default to speech as it's the most common type
        return "speech"