"""
Roman Senate AI Game
Agent System Demo

This script demonstrates the use of the Event-Driven Senator Agent and Event Memory systems
implemented in Phase 2 of the migration plan. It creates several senator agents, publishes
events, and shows how agents respond to and generate events.
"""

import asyncio
import datetime
from typing import List, Dict, Any

from ..core.events.base import BaseEvent as RomanEvent
from ..core.events.event_bus import EventBus
from ..agents.event_driven_senator_agent import EventDrivenSenatorAgent
from ..agents.event_memory import EventMemory

# Simple mock LLM provider for demonstration purposes - synchronous version
class MockLLMProvider:
    """Mock LLM provider that returns predefined responses."""
    
    # This is synchronous (not async) to avoid event loop issues in our demo
    def generate_text(self, prompt: str) -> str:
        """Generate text based on prompt keywords."""
        if "stance" in prompt.lower():
            if "military" in prompt.lower():
                return "As a member of the Optimates faction, I believe we must strengthen our military to protect Rome's interests. I support additional funding for our legions.\n\nfor"
            elif "taxes" in prompt.lower():
                return "I cannot support increased taxes on Roman citizens. This would only burden our people unnecessarily.\n\nagainst"
            else:
                return "I have no strong opinion on this matter and will listen to the debate before deciding.\n\nneutral"
        elif "speech" in prompt.lower():
            return "Senators of Rome, we must consider the consequences of our actions for future generations. This matter requires careful deliberation and wisdom.\n\nI have used a balanced approach to appeal to reason and tradition."
        elif "translate" in prompt.lower() and "latin" in prompt.lower():
            return "Senatores Romani, consequentias actionum nostrarum pro futuris generationibus considerare debemus. Haec res deliberationem sapientiamque requirit."
        elif "interjection" in prompt.lower():
            return "I must disagree with the honorable senator on this point!"
        else:
            return "Default response for: " + prompt[:50] + "..."


async def main():
    """Run the agent system demonstration."""
    # Create event bus
    event_bus = EventBus()
    
    # Create mock LLM provider
    llm_provider = MockLLMProvider()
    
    # Create several senator agents
    senators = [
        {"name": "Marcus Porcius Cato", "faction": "Optimates"},
        {"name": "Gaius Julius Caesar", "faction": "Populares"},
        {"name": "Marcus Tullius Cicero", "faction": "Moderates"}
    ]
    
    senator_agents: List[EventDrivenSenatorAgent] = []
    
    for senator in senators:
        agent = EventDrivenSenatorAgent(
            senator=senator,
            llm_provider=llm_provider,
            event_bus=event_bus
        )
        senator_agents.append(agent)
        print(f"Created senator agent: {agent.name} of {agent.faction} faction")
    
    # Demonstrate event publication and handling
    print("\n=== Starting Senate Session ===")
    
    # Publish senate session start event
    session_event = RomanEvent(
        event_type="senate.session_started",
        data={"date": datetime.datetime.now().isoformat()}
    )
    event_bus.publish(session_event)
    
    # Introduce a debate topic
    print("\n=== Introducing Debate Topic ===")
    topic_event = RomanEvent(
        event_type="debate.topic_introduced",
        data={
            "topic": "Increasing military funding for the Gallic campaign",
            "sponsor": "Gaius Julius Caesar"
        }
    )
    event_bus.publish(topic_event)
    
    # Allow agents to process events and potentially generate actions
    print("\n=== Senator Responses ===")
    for agent in senator_agents:
        action_event = agent.generate_action()
        if action_event:
            print(f"\n{agent.name} delivers a speech:")
            latin = action_event.data.get("latin_text", "")
            english = action_event.data.get("english_text", "")
            stance = action_event.data.get("stance", "unknown")
            print(f"Stance: {stance}")
            print(f"Latin: {latin}")
            print(f"English: {english}")
            
            # Publish the speech event
            event_bus.publish(action_event)
    
    # Request votes on the topic
    print("\n=== Requesting Votes ===")
    vote_request = RomanEvent(
        event_type="debate.vote_requested",
        data={
            "topic": "Increasing military funding for the Gallic campaign",
            "sponsor": "Gaius Julius Caesar"
        }
    )
    event_bus.publish(vote_request)
    
    # Check memory contents for Cato
    cato = senator_agents[0]
    print(f"\n=== {cato.name}'s Memory ===")
    recent_events = cato.memory.get_recent_events(5)
    for i, event in enumerate(recent_events, 1):
        print(f"{i}. Event Type: {event.event_type}")
        print(f"   Source: {event.source or 'None'}")
        print(f"   Target: {event.target or 'None'}")
        print(f"   Data Keys: {list(event.data.keys())}")
    
    print("\n=== End of Demonstration ===")


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())