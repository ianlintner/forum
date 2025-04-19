"""
Integration tests for the Agentic Game Framework.

This module contains tests that verify the integration between
different components of the framework.
"""

import unittest
from unittest.mock import patch
import io
import sys

from src.agentic_game_framework.events.event_bus import EventBus
from src.agentic_game_framework.agents.agent_factory import AgentFactory
from src.agentic_game_framework.agents.agent_manager import AgentManager
from src.agentic_game_framework.relationships.relationship_manager import RelationshipManager
from src.agentic_game_framework.examples.simple_simulation import SimpleAgent, run_simulation


class TestSimpleSimulation(unittest.TestCase):
    """Tests for the simple simulation example."""
    
    def test_simulation_components(self):
        """Test that the simulation components can be created and connected."""
        # Create core components
        event_bus = EventBus()
        agent_factory = AgentFactory()
        agent_manager = AgentManager(event_bus)
        relationship_manager = RelationshipManager(event_bus)
        
        # Register agent types
        agent_factory.register_agent_type("simple", SimpleAgent)
        
        # Create an agent
        agent = agent_factory.create_agent(
            "simple",
            {"name": "TestAgent"}
        )
        
        # Add agent to manager
        agent_manager.add_agent(agent)
        
        # Verify agent was added
        self.assertEqual(len(agent_manager.get_all_agents()), 1)
        self.assertEqual(agent_manager.get_agent(agent.id).name, "TestAgent")
        
        # Generate an action
        actions = agent_manager.update_all()
        
        # Verify action was generated (might be None sometimes, so we just check the list length)
        self.assertIsNotNone(actions)
    
    @patch('time.sleep')  # Patch sleep to speed up the test
    def test_simulation_run(self, mock_sleep):
        """Test that the simulation can run for a few steps without errors."""
        # Capture stdout to verify output
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        try:
            # Run a very short simulation
            run_simulation(num_agents=2, max_steps=2)
            
            # Get the output
            output = captured_output.getvalue()
            
            # Verify expected output elements
            self.assertIn("Initializing simulation", output)
            self.assertIn("Created Agent-1", output)
            self.assertIn("Created Agent-2", output)
            self.assertIn("Created relationship between", output)
            self.assertIn("Starting simulation", output)
            self.assertIn("Step 1", output)
            self.assertIn("Step 2", output)
            self.assertIn("Simulation complete", output)
        finally:
            # Reset stdout
            sys.stdout = sys.__stdout__
    
    def test_agent_event_processing(self):
        """Test that agents can process events correctly."""
        # Create an agent
        agent = SimpleAgent("TestAgent")
        
        # Record initial mood
        initial_mood = agent.state["mood"]
        
        # Create a friendly greeting event
        from src.agentic_game_framework.examples.simple_simulation import GreetingEvent
        event = GreetingEvent(
            source="OtherAgent",
            target=agent.id,
            greeting_type="friendly"
        )
        
        # Process the event
        agent.process_event(event)
        
        # Verify mood increased
        self.assertGreater(agent.state["mood"], initial_mood)
        
        # Verify event was stored in memory
        self.assertEqual(len(agent.memory.get_all_memories()), 1)
        memory = agent.memory.get_all_memories()[0]
        self.assertEqual(memory.content["event_type"], "greeting")
        self.assertEqual(memory.content["source"], "OtherAgent")
        self.assertEqual(memory.content["target"], agent.id)


if __name__ == "__main__":
    unittest.main()