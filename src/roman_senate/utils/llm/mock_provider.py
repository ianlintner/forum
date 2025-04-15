"""
Mock LLM provider for testing purposes.
This provider returns predefined responses instead of making actual API calls.
"""

import json
import logging
import os
import random
import re
from typing import Dict, List, Optional, Union, Any

from ...mock_speeches import MOCK_SPEECHES

from .base import LLMProvider

logger = logging.getLogger(__name__)

class MockProvider(LLMProvider):
    """
    Mock LLM provider for testing and CI environments.
    Returns predetermined responses without making external API calls.
    """

    def __init__(self, **kwargs):
        """Initialize the mock provider with optional custom responses."""
        # No need to call super().__init__ as the ABC doesn't have an __init__ method that takes arguments
        logger.info("Initializing MockProvider for test mode")
        
        # Add provider name attribute that agent_simulation.py expects
        self.provider_name = "mock"
        
        # Store model name if provided
        self.model_name = kwargs.get("model_name", "mock_model")
        
        # Default mock responses for different prompt types
        self.mock_responses = {
            "topic": [
                "Should Rome expand its territories in Gaul?",
                "Should the grain dole be increased for the citizens of Rome?",
                "Should the Senate grant additional powers to the Consul?",
                "Should Rome form an alliance with the Kingdom of Parthia?",
                "Should the property requirements for military service be lowered?"
            ],
            "speech": {
                "Populares": [
                    "Citizens of Rome, this proposal would benefit the common people who form the backbone of our legions. Our military strength depends on supporting our plebeian soldiers and their families. The welfare of the many must outweigh the privileges of the few.\n\nI appeal to popular welfare and the support of common citizens to counter the aristocracy's resistance.",
                    "The traditions that truly matter are those that strengthen Rome through unity, not those that divide us into privileged classes. This measure would remove unfair barriers and allow more citizens to participate in Rome's future. The voice of the people must be heard!\n\nI'm using populist rhetoric to build support among my plebeian base.",
                    "I remind you that many great Roman reforms came when we listened to the needs of our citizens rather than clinging to outdated traditions. Our republic thrives when it adapts to serve all Romans, not just the elite.\n\nMy approach challenges aristocratic resistance by referencing successful past reforms."
                ],
                "Merchant": [
                    "Esteemed colleagues, this measure would stimulate trade and commerce throughout the republic. The economic benefits would spread to all regions under Roman control, increasing tax revenues and strengthening our treasury.\n\nI've focused on economic arguments to appeal to practical considerations.",
                    "As someone who understands the movement of goods and currency throughout our territories, I assure you this proposal represents a sound investment in Rome's future prosperity. New opportunities will emerge for merchants and farmers alike.\n\nI'm leveraging my commercial expertise to build credibility for my position.",
                    "The stability of markets depends on wise governance. This measure would create predictable conditions that allow businesses to flourish and trade routes to remain secure. Our economic strength underpins our military power.\n\nMy argument connects economic interests to broader Roman security concerns."
                ],
                "Military": [
                    "Senators, I have seen firsthand the challenges our legions face. This measure would strengthen our capacity to defend Roman territories and project power when necessary. The security of Rome must be our paramount concern.\n\nI'm drawing on military experience to establish authority on defense matters.",
                    "The glory of Rome is maintained through strength of arms. Our enemies are ever watchful for signs of weakness. This proposal ensures our legions remain the most formidable force in the known world.\n\nI appeal to Roman pride and the fear of appearing weak to our adversaries.",
                    "The campaigns I have participated in have taught me that preparation and resources determine victory. This measure provides both. To vote against it would be to gamble with Rome's security at a time when threats multiply.\n\nI'm using a risk-averse security argument to persuade cautious senators."
                ]
            },
            "stance_reasoning": {
                "Populares": [
                    "As a member of the Populares faction, I believe this policy will benefit the common citizens of Rome and align with our platform of reform. The plebeians who serve in our armies deserve our support.",
                    "This measure would reduce the power imbalance between patricians and plebeians, creating a more equitable republic where merit rather than birth determines influence.",
                    "My faction has long advocated for the rights of common citizens, and this proposal continues that tradition by distributing resources more fairly across Roman society."
                ],
                "Merchant": [
                    "As a merchant, I must consider the economic implications of this proposal. The trade routes and markets it would affect are vital to Rome's commerce and prosperity.",
                    "My trading interests would benefit from the stability this measure provides, allowing for more predictable movement of goods throughout Roman territories.",
                    "The financial aspects of this proposal are sound and would likely increase overall economic activity while securing important resources for the republic."
                ],
                "Military": [
                    "My military background compels me to approach this issue from a security perspective. I believe this measure will strengthen our legions' ability to defend Rome's interests.",
                    "Having commanded troops in the field, I recognize that our military readiness depends on proper funding and resources, which this proposal would provide.",
                    "The strategic implications of this measure are significant and would improve our position against potential threats from Carthage, Germanic tribes, and eastern kingdoms."
                ]
            },
            "vote_reasoning": {
                "Populares": [
                    "After considering the debate, I must support this measure as it aligns with the Populares' commitment to reforms that benefit common citizens rather than just the aristocracy.",
                    "The arguments against this proposal come primarily from those seeking to preserve their own privileges at the expense of Rome's overall strength. I vote for the people's interest.",
                    "While I recognize concerns about tradition, I believe Rome's greatest tradition is its ability to adapt and reform. This measure continues that proud legacy."
                ],
                "Merchant": [
                    "As a pragmatist concerned with Rome's prosperity, I support this measure because it would stabilize important trade routes and markets that benefit all Romans.",
                    "The economic benefits outweigh potential short-term costs. New commercial opportunities and increased tax revenue would strengthen Rome's finances.",
                    "My trading interests inform me that this proposal would create favorable conditions for commerce throughout our territories, benefiting both merchants and citizens."
                ],
                "Military": [
                    "Having assessed this matter from a strategic perspective, I support this measure as necessary for maintaining Rome's military readiness in a dangerous world.",
                    "The security implications are clear - failure to approve this funding would leave our borders vulnerable at a time when multiple threats are emerging.",
                    "My experience in campaigns against our enemies convinces me that this investment in our legions is essential for Rome's continued dominance."
                ]
            },
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
        """Generate a completion response based on the prompt type and faction if applicable."""
        logger.info(f"Mock completion requested for prompt: {prompt[:50]}...")
        
        # First check if this is a speech about a specific debate topic
        topic_speech = self._get_topic_specific_speech(prompt)
        if topic_speech:
            return topic_speech
            
        # Otherwise, determine the type of response needed
        response_type = self._detect_prompt_type(prompt)
        
        # Determine faction if relevant
        faction = self._detect_faction(prompt)
        
        # Get a response for that type
        if response_type in self.mock_responses:
            response_data = self.mock_responses[response_type]
            
            # Handle faction-specific responses
            if isinstance(response_data, dict) and faction in response_data:
                # This is a faction-based response dictionary
                return random.choice(response_data[faction])
            elif isinstance(response_data, dict) and faction not in response_data:
                # Use a random faction if the specific one isn't found
                random_faction = random.choice(list(response_data.keys()))
                return random.choice(response_data[random_faction])
            elif isinstance(response_data, list):
                # Simple list of responses
                return random.choice(response_data)
            else:
                # JSON content
                return json.dumps(response_data)
                
        # Default fallback response
        return "Mock response for testing purposes."
        
    def _detect_faction(self, prompt: str) -> str:
        """Detect which faction a senator belongs to based on prompt."""
        prompt_lower = prompt.lower()
        
        if "populares" in prompt_lower:
            return "Populares"
        elif "merchant" in prompt_lower:
            return "Merchant"
        elif "military" in prompt_lower:
            return "Military"
        elif "optimates" in prompt_lower:
            return "Optimates"
        
        # Default to a random faction if not found
        return random.choice(["Populares", "Merchant", "Military"])
        
    def _get_topic_specific_speech(self, prompt: str) -> Optional[str]:
        """
        Check if the prompt is about a specific debate topic and return an appropriate speech.
        
        Args:
            prompt: The prompt text
            
        Returns:
            A topic-specific speech if one is found, otherwise None
        """
        prompt_lower = prompt.lower()
        
        # Check if this is a speech generation request
        if "generate a brief speech" not in prompt_lower and "expressing your views" not in prompt_lower:
            return None
            
        # Extract the topic and faction
        topic_match = re.search(r"topic for debate: (.+?)(\n|$)", prompt, re.IGNORECASE)
        if not topic_match:
            return None
            
        topic_text = topic_match.group(1).strip()
        faction = self._detect_faction(prompt)
        
        # Determine topic category from keywords
        topic_category = None
        if any(keyword in topic_text.lower() for keyword in ["military", "legion", "army", "war", "troops", "defense"]):
            topic_category = "military_funding"
        elif any(keyword in topic_text.lower() for keyword in ["temple", "religion", "gods", "jupiter", "divine", "sacred"]):
            topic_category = "religious_matters"
            
        # Return appropriate speech if we have matching content
        if topic_category and topic_category in MOCK_SPEECHES and faction in MOCK_SPEECHES[topic_category]:
            speech = random.choice(MOCK_SPEECHES[topic_category][faction])
            
            # For speeches, add a matching rhetorical approach explanation
            rhetorical_approach = "\n\nI'm using rhetoric that appeals to my faction's interests and values."
            
            if faction == "Populares":
                rhetorical_approach = "\n\nI'm emphasizing the welfare of common citizens and reform to persuade the Senate."
            elif faction == "Merchant":
                rhetorical_approach = "\n\nI'm highlighting economic benefits and trade considerations to build support for my position."
            elif faction == "Military":
                rhetorical_approach = "\n\nI'm stressing security concerns and military expertise to convince my fellow senators."
                
            return speech + rhetorical_approach
            
        return None

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
        elif any(keyword in prompt_lower for keyword in ["stance", "position", "what stance would you take"]):
            # For stance decision with reasoning
            return "stance_reasoning"
        elif any(keyword in prompt_lower for keyword in ["how do you vote", "final decision"]):
            # For voting with reasoning (especially for neutral senators)
            return "vote_reasoning"
            
        # Default to speech as it's the most common type
        return "speech"