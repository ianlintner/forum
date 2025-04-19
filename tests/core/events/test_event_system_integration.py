"""
Integration tests for the event-driven architecture.

This module tests the interaction between all components of the event system
in realistic scenarios, ensuring they work together correctly.
"""

import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch

from roman_senate.core.events.event_bus import EventBus
from roman_senate.core.events.debate_manager import DebateManager
from roman_senate.agents.event_driven_senator_agent import EventDrivenSenatorAgent
from roman_senate.core.events.debate_events import (
    DebateEvent,
    DebateEventType,
    SpeechEvent,
    ReactionEvent,
    InterjectionEvent,
    InterjectionType
)


class TestEventSystemIntegration:
    """Integration tests for the event-driven architecture components."""
    
    @pytest.fixture
    def event_bus(self):
        """Create a real EventBus for integration testing."""
        return EventBus()
    
    @pytest.fixture
    def game_state(self):
        """Create a mock game state for testing."""
        return MagicMock()
    
    @pytest.fixture
    def llm_provider(self):
        """Create a mock LLM provider for testing."""
        mock_provider = MagicMock()
        mock_provider.generate_text = AsyncMock(return_value="Generated text")
        return mock_provider
    
    @pytest.fixture
    def debate_manager(self, event_bus, game_state):
        """Create a DebateManager for testing."""
        return DebateManager(event_bus, game_state)
    
    @pytest.fixture
    def sample_senators(self):
        """Create sample senators for testing."""
        return [
            {"id": "senator1", "name": "Cato", "faction": "Optimates", "rank": 4},
            {"id": "senator2", "name": "Caesar", "faction": "Populares", "rank": 3},
            {"id": "senator3", "name": "Cicero", "faction": "Optimates", "rank": 2},
            {"id": "senator4", "name": "Brutus", "faction": "Optimates", "rank": 1},
            {"id": "senator5", "name": "Clodius", "faction": "Populares", "rank": 2}
        ]
    
    @pytest.fixture
    def senator_agents(self, sample_senators, llm_provider, event_bus):
        """Create EventDrivenSenatorAgent instances for testing."""
        agents = []
        
        for senator in sample_senators:
            with patch('roman_senate.agents.event_driven_senator_agent.EventMemory'):
                agent = EventDrivenSenatorAgent(senator, llm_provider, event_bus)
                agents.append(agent)
                
        return agents
    
    @pytest.mark.asyncio
    async def test_debate_start_event_propagation(self, debate_manager, senator_agents):
        """Test that debate start events are properly propagated to senator agents."""
        # Patch decide_stance to avoid actual LLM calls
        for agent in senator_agents:
            agent.decide_stance = AsyncMock()
            agent.memory.record_event = MagicMock()
        
        # Start debate
        topic = "Whether Rome should go to war with Carthage"
        senators = [agent.senator for agent in senator_agents]
        await debate_manager.start_debate(topic, senators)
        
        # Allow event to propagate (small delay)
        await asyncio.sleep(0.1)
        
        # Check that all agents received and processed the event
        for agent in senator_agents:
            # Event should be recorded in memory
            assert agent.memory.record_event.called
            
            # Debate state should be updated
            assert agent.debate_in_progress is True
            assert agent.active_debate_topic == topic
            
            # Stance should be decided
            agent.decide_stance.assert_called_once_with(topic, {})
    
    @pytest.mark.asyncio
    async def test_speech_event_reactions(self, debate_manager, senator_agents, event_bus):
        """Test that speech events trigger reactions from other senators."""
        # Patch methods to ensure deterministic behavior
        for agent in senator_agents:
            agent._should_react_to_speech = AsyncMock(return_value=True)
            agent._should_interject = AsyncMock(return_value=False)
            agent._consider_stance_change = AsyncMock()
            agent._generate_reaction_content = AsyncMock(return_value="Reaction content")
            agent.memory.record_event = MagicMock()
            agent.memory.record_reaction = MagicMock()
            agent.memory.add_interaction = MagicMock()
        
        # Start debate
        topic = "Whether Rome should go to war with Carthage"
        senators = [agent.senator for agent in senator_agents]
        await debate_manager.start_debate(topic, senators)
        
        # Allow event to propagate
        await asyncio.sleep(0.1)
        
        # Reset the publish method to track new calls
        event_bus.publish = AsyncMock(wraps=event_bus.publish)
        
        # Get the first speaking senator and others
        speaker_agent = senator_agents[0]
        listening_agents = senator_agents[1:]
        
        # Publish a speech
        speech_event = await debate_manager.publish_speech(
            speaker=speaker_agent.senator,
            topic=topic,
            latin_content="Ceterum censeo Carthaginem esse delendam",
            english_content="Furthermore, I think Carthage must be destroyed",
            stance="support",
            key_points=["Carthage is a threat", "War is necessary"]
        )
        
        # Allow reactions to be generated and published
        await asyncio.sleep(0.1)
        
        # Count reaction events published
        reaction_count = 0
        for call_args in event_bus.publish.call_args_list:
            if isinstance(call_args[0][0], ReactionEvent):
                reaction_count += 1
        
        # Should have reactions from listening agents who all have _should_react_to_speech return True
        assert reaction_count == len(listening_agents)
        
        # Check that all listening agents recorded the speech event
        for agent in listening_agents:
            agent.memory.record_event.assert_any_call(speech_event)
    
    @pytest.mark.asyncio
    async def test_speech_event_interjections(self, debate_manager, senator_agents, event_bus):
        """Test that speech events can trigger interjections."""
        # Patch methods to ensure deterministic behavior
        for agent in senator_agents:
            agent._should_react_to_speech = AsyncMock(return_value=False)
            agent._should_interject = AsyncMock(return_value=True)
            agent._consider_stance_change = AsyncMock()
            agent._determine_interjection_type = AsyncMock(return_value=InterjectionType.CHALLENGE)
            agent._generate_interjection_content = AsyncMock(return_value=("Nego!", "I disagree!"))
            agent.memory.record_event = MagicMock()
            agent.memory.add_interaction = MagicMock()
        
        # Start debate
        topic = "Whether Rome should go to war with Carthage"
        senators = [agent.senator for agent in senator_agents]
        await debate_manager.start_debate(topic, senators)
        
        # Allow event to propagate
        await asyncio.sleep(0.1)
        
        # Reset the publish method to track new calls
        event_bus.publish = AsyncMock(wraps=event_bus.publish)
        
        # Get the first speaking senator and others
        speaker_agent = senator_agents[0]
        listening_agents = senator_agents[1:]
        
        # Publish a speech
        speech_event = await debate_manager.publish_speech(
            speaker=speaker_agent.senator,
            topic=topic,
            latin_content="Ceterum censeo Carthaginem esse delendam",
            english_content="Furthermore, I think Carthage must be destroyed",
            stance="support",
            key_points=["Carthage is a threat", "War is necessary"]
        )
        
        # Allow interjections to be generated and published
        await asyncio.sleep(0.1)
        
        # Count interjection events published
        interjection_count = 0
        for call_args in event_bus.publish.call_args_list:
            if isinstance(call_args[0][0], InterjectionEvent):
                interjection_count += 1
        
        # Should have interjections from listening agents who all have _should_interject return True
        assert interjection_count == len(listening_agents)
    
    @pytest.mark.asyncio
    async def test_stance_changes_from_speeches(self, debate_manager, senator_agents, event_bus):
        """Test that senators can change their stance based on speeches."""
        # Start with a clean setup
        for agent in senator_agents:
            agent._should_react_to_speech = AsyncMock(return_value=False)
            agent._should_interject = AsyncMock(return_value=False)
            
            # Ensure at least one agent will change stance
            # First agent has a stance of "oppose"
            if agent == senator_agents[0]:
                agent.current_stance = "oppose"
                # This agent will always change stance when considering
                agent._consider_stance_change = AsyncMock(side_effect=lambda event: setattr(agent, 'current_stance', 'neutral'))
            else:
                agent.current_stance = "neutral"
                agent._consider_stance_change = AsyncMock()
                
            agent.memory.record_event = MagicMock()
            agent.memory.record_stance_change = MagicMock()
            agent.memory.add_interaction = MagicMock()
        
        # Start debate
        topic = "Whether Rome should go to war with Carthage"
        senators = [agent.senator for agent in senator_agents]
        await debate_manager.start_debate(topic, senators)
        
        # Allow event to propagate
        await asyncio.sleep(0.1)
        
        # Get the second speaking senator (first is the one we'll check for stance change)
        speaker_agent = senator_agents[1]
        changing_agent = senator_agents[0]
        
        # Initial stance check
        assert changing_agent.current_stance == "oppose"
        
        # Publish a persuasive speech
        speech_event = await debate_manager.publish_speech(
            speaker=speaker_agent.senator,
            topic=topic,
            latin_content="Carthago delenda est!",
            english_content="Carthage must be destroyed!",
            stance="support",
            key_points=["Carthage is dangerous", "War is inevitable"]
        )
        
        # Allow stance change to be processed
        await asyncio.sleep(0.1)
        
        # Check that the stance changed (from oppose to neutral)
        assert changing_agent.current_stance == "neutral"
        
        # Check that stance change was recorded
        changing_agent._consider_stance_change.assert_called_once_with(speech_event)
    
    @pytest.mark.asyncio
    async def test_interjection_handling_by_debate_manager(self, debate_manager, senator_agents, event_bus, caplog):
        """Test that the debate manager properly handles interjections based on rank."""
        # Start with a clean setup
        for agent in senator_agents:
            agent._should_react_to_speech = AsyncMock(return_value=False)
            agent._should_interject = AsyncMock(return_value=False)
            agent._consider_stance_change = AsyncMock()
            agent.memory.record_event = MagicMock()
            agent.memory.add_interaction = MagicMock()
        
        # Start debate
        topic = "Whether Rome should go to war with Carthage"
        senators = [agent.senator for agent in senator_agents]
        await debate_manager.start_debate(topic, senators)
        
        # Current speaker is lowest rank
        current_speaker = senators[3]  # Brutus, rank 1
        debate_manager.current_speaker = current_speaker
        
        # Create interjections from different senators
        high_rank_interjector = senators[0]  # Cato, rank 4
        equal_rank_interjector = senators[4]  # Clodius, rank 2 (higher than current speaker)
        
        # Create and publish interjections
        high_rank_interjection = InterjectionEvent(
            interjector=high_rank_interjector,
            target_speaker=current_speaker,
            interjection_type=InterjectionType.CHALLENGE,
            latin_content="Ego dissentio!",
            english_content="I strongly disagree!",
            causes_disruption=True
        )
        
        equal_rank_interjection = InterjectionEvent(
            interjector=equal_rank_interjector,
            target_speaker=current_speaker,
            interjection_type=InterjectionType.EMOTIONAL,
            latin_content="Absurdum!",
            english_content="Absurd!",
            causes_disruption=True
        )
        
        # Reset caplog
        caplog.clear()
        
        # Handle high rank interjection
        with caplog.at_level("INFO"):
            await debate_manager.handle_interjection(high_rank_interjection)
            
            # High rank should be allowed to interrupt
            assert "INTERJECTION: I strongly disagree!" in caplog.text
            assert "Allowed: True" in caplog.text
        
        # Reset caplog
        caplog.clear()
        
        # Handle equal rank interjection (higher than current speaker)
        with caplog.at_level("INFO"):
            await debate_manager.handle_interjection(equal_rank_interjection)
            
            # Higher rank should be allowed to interrupt
            assert "INTERJECTION: Absurd!" in caplog.text
            assert "Allowed: True" in caplog.text
    
    @pytest.mark.asyncio
    async def test_full_debate_cycle(self, debate_manager, senator_agents, event_bus):
        """Test a full debate cycle from start to finish with all components."""
        # Setup agents with more realistic behavior
        for agent in senator_agents:
            # Random chance of reacting
            agent._should_react_to_speech = AsyncMock(side_effect=lambda event: random.random() < 0.5)
            # Lower chance of interjecting
            agent._should_interject = AsyncMock(side_effect=lambda event: random.random() < 0.2)
            # Allow real interjection type determination but mock content generation
            agent._determine_interjection_type = AsyncMock(return_value=InterjectionType.CHALLENGE)
            agent._generate_reaction_content = AsyncMock(return_value="Reaction content")
            agent._generate_interjection_content = AsyncMock(return_value=("Latin content", "English content"))
            # Skip stance changes for simplicity
            agent._consider_stance_change = AsyncMock()
            
            # Initial stance
            agent.current_stance = random.choice(["support", "oppose", "neutral"])
            
            # Avoid actual record calls
            agent.memory.record_event = MagicMock()
            agent.memory.record_reaction = MagicMock()
            agent.memory.add_interaction = MagicMock()
            agent.memory.record_event_relationship_impact = MagicMock()
            
            # Avoid actual decide_stance calls
            agent.decide_stance = AsyncMock()
        
        # Mock key methods to avoid display and history effects
        with patch('roman_senate.core.events.debate_manager.display_speech', MagicMock()), \
             patch('roman_senate.core.events.debate_manager.add_to_debate_history', MagicMock()), \
             patch('random.random', side_effect=lambda: 0.3):  # Ensures some reactions but not all
            
            # Conduct complete debate
            topic = "Whether Rome should go to war with Carthage"
            senators = [agent.senator for agent in senator_agents]
            
            # Track published events
            debate_events = []
            speech_events = []
            reaction_events = []
            interjection_events = []
            
            # Replace publish with a version that tracks events
            original_publish = event_bus.publish
            
            async def tracking_publish(event):
                if isinstance(event, DebateEvent):
                    debate_events.append(event)
                elif isinstance(event, SpeechEvent):
                    speech_events.append(event)
                elif isinstance(event, ReactionEvent):
                    reaction_events.append(event)
                elif isinstance(event, InterjectionEvent):
                    interjection_events.append(event)
                    
                return await original_publish(event)
                
            event_bus.publish = tracking_publish
            
            # Conduct the debate
            await debate_manager.conduct_debate(topic, senators)
            
            # Check that all expected events were published
            
            # Should have start and end events
            assert len(debate_events) >= 2
            assert any(e.debate_event_type == DebateEventType.DEBATE_START for e in debate_events)
            assert any(e.debate_event_type == DebateEventType.DEBATE_END for e in debate_events)
            
            # Should have speech events for each senator
            assert len(speech_events) == len(senators)
            speaker_names = [event.speaker.get("name") for event in speech_events]
            for senator in senators:
                assert senator.get("name") in speaker_names
            
            # Should have some reaction events (not necessarily all senators reacted)
            assert len(reaction_events) > 0
            
            # May have some interjection events
            # (We don't assert a specific number because it depends on the random behavior)
            
            # All events should have the correct topic
            for event in debate_events:
                if hasattr(event, "metadata") and "topic" in event.metadata:
                    assert event.metadata["topic"] == topic
                    
            for event in speech_events:
                assert event.metadata["topic"] == topic