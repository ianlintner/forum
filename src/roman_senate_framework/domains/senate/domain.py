"""
Roman Senate Domain Implementation for Agentic Game Framework.

This module defines the Senate domain and its extension points.
"""

from typing import Any, Dict, List, Optional, Set, Type

from src.agentic_game_framework.domains.extension_points import (
    AgentBehaviorExtension,
    DomainConfigExtension,
    DomainExtensionPoint,
    EventTypeRegistry,
    MemoryTypeExtension,
    RelationshipTypeExtension,
)
from src.agentic_game_framework.domains.domain_registry import DomainRegistry
from src.agentic_game_framework.events.base import BaseEvent
from src.agentic_game_framework.memory.memory_interface import MemoryItem
from src.agentic_game_framework.relationships.base_relationship import BaseRelationship
from src.agentic_game_framework.agents.base_agent import BaseAgent

# Domain identifier
SENATE_DOMAIN = "roman_senate"


class SenateEventRegistry(EventTypeRegistry):
    """
    Registry for Senate-specific event types.
    
    This class registers all event types used in the Senate domain,
    such as debate events, speech events, etc.
    """
    
    def register_event_types(self) -> Dict[str, Type[BaseEvent]]:
        """
        Register Senate-specific event types.
        
        Returns:
            Dict[str, Type[BaseEvent]]: Map of event type IDs to event classes
        """
        from .events.senate_events import (
            SenateEvent,
            SpeechEvent,
            DebateEvent,
            ReactionEvent,
            InterjectionEvent,
            RelationshipEvent,
        )
        
        return {
            "senate.base": SenateEvent,
            "senate.speech": SpeechEvent,
            "senate.debate": DebateEvent,
            "senate.reaction": ReactionEvent,
            "senate.interjection": InterjectionEvent,
            "senate.relationship": RelationshipEvent,
        }
    
    def get_event_type_metadata(self, event_type: str) -> Dict[str, Any]:
        """
        Get metadata for a specific event type.
        
        Args:
            event_type: Event type identifier
            
        Returns:
            Dict[str, Any]: Metadata for the event type
        """
        metadata = {
            "senate.base": {
                "description": "Base event for all Senate events",
                "affects_relationship": False,
                "creates_memory": False,
            },
            "senate.speech": {
                "description": "Speech given by a senator",
                "affects_relationship": True,
                "relationship_impact_range": (-0.2, 0.3),
                "creates_memory": True,
                "memory_importance": 0.7,
            },
            "senate.debate": {
                "description": "Debate event in the Senate",
                "affects_relationship": False,
                "creates_memory": True,
                "memory_importance": 0.6,
            },
            "senate.reaction": {
                "description": "Reaction to a speech or event",
                "affects_relationship": True,
                "relationship_impact_range": (-0.1, 0.2),
                "creates_memory": True,
                "memory_importance": 0.5,
            },
            "senate.interjection": {
                "description": "Interjection during a speech",
                "affects_relationship": True,
                "relationship_impact_range": (-0.3, 0.1),
                "creates_memory": True,
                "memory_importance": 0.6,
            },
            "senate.relationship": {
                "description": "Relationship change between senators",
                "affects_relationship": True,
                "relationship_impact_range": (-0.5, 0.5),
                "creates_memory": True,
                "memory_importance": 0.8,
            },
        }
        
        return metadata.get(event_type, {})


class SenateMemoryExtension(MemoryTypeExtension):
    """
    Extension for Senate-specific memory types.
    
    This class defines custom memory types for the Senate domain,
    such as speech memories, debate memories, etc.
    """
    
    def register_memory_types(self) -> Dict[str, Type[MemoryItem]]:
        """
        Register Senate-specific memory types.
        
        Returns:
            Dict[str, Type[MemoryItem]]: Map of memory type IDs to memory classes
        """
        from .memory.senate_memory import (
            SpeechMemory,
            DebateMemory,
            RelationshipMemory,
        )
        
        return {
            "speech": SpeechMemory,
            "debate": DebateMemory,
            "relationship": RelationshipMemory,
        }
    
    def create_memory_from_event(self, event: BaseEvent) -> Optional[MemoryItem]:
        """
        Create a domain-specific memory from an event.
        
        Args:
            event: The event to create a memory from
            
        Returns:
            Optional[MemoryItem]: The created memory, or None if not applicable
        """
        from .memory.senate_memory import (
            SpeechMemory,
            DebateMemory,
            RelationshipMemory,
        )
        import time
        import uuid
        
        if event.event_type == "senate.speech":
            return SpeechMemory(
                memory_id=f"speech_{str(uuid.uuid4())}",
                timestamp=time.time(),
                event=event,
                importance=0.7,
            )
        elif event.event_type == "senate.debate":
            return DebateMemory(
                memory_id=f"debate_{str(uuid.uuid4())}",
                timestamp=time.time(),
                event=event,
                importance=0.6,
            )
        elif event.event_type == "senate.relationship":
            return RelationshipMemory(
                memory_id=f"relationship_{str(uuid.uuid4())}",
                timestamp=time.time(),
                event=event,
                importance=0.8,
            )
        
        return None
    
    def enhance_memory_retrieval(
        self,
        query: Dict[str, Any],
        memories: List[MemoryItem]
    ) -> List[MemoryItem]:
        """
        Enhance memory retrieval with domain-specific logic.
        
        Args:
            query: The retrieval query
            memories: The initially retrieved memories
            
        Returns:
            List[MemoryItem]: The enhanced list of memories
        """
        # Sort by relevance to Senate activities
        if "relevance" in query:
            if query["relevance"] == "speech":
                # Prioritize speech memories
                memories.sort(key=lambda m: 1.0 if hasattr(m, "speech_data") else 0.5, reverse=True)
            elif query["relevance"] == "debate":
                # Prioritize debate memories
                memories.sort(key=lambda m: 1.0 if hasattr(m, "debate_data") else 0.5, reverse=True)
            elif query["relevance"] == "relationship":
                # Prioritize relationship memories
                memories.sort(key=lambda m: 1.0 if hasattr(m, "relationship_data") else 0.5, reverse=True)
        
        return memories


class SenateRelationshipExtension(RelationshipTypeExtension):
    """
    Extension for Senate-specific relationship types.
    
    This class defines custom relationship types for the Senate domain,
    such as political alliances, rivalries, etc.
    """
    
    def register_relationship_types(self) -> Dict[str, Type[BaseRelationship]]:
        """
        Register Senate-specific relationship types.
        
        Returns:
            Dict[str, Type[BaseRelationship]]: Map of relationship type IDs to relationship classes
        """
        from .relationships.senate_relationships import (
            PoliticalRelationship,
            FactionRelationship,
            PersonalRelationship,
        )
        
        return {
            "political": PoliticalRelationship,
            "faction": FactionRelationship,
            "personal": PersonalRelationship,
        }
    
    def create_default_relationships(
        self,
        agent_ids: List[str]
    ) -> List[BaseRelationship]:
        """
        Create default relationships between agents.
        
        Args:
            agent_ids: List of agent IDs
            
        Returns:
            List[BaseRelationship]: List of created relationships
        """
        from .relationships.senate_relationships import (
            PoliticalRelationship,
            FactionRelationship,
            PersonalRelationship,
        )
        import random
        
        relationships = []
        
        # Create a mix of relationship types between agents
        for i, agent_a_id in enumerate(agent_ids):
            for j, agent_b_id in enumerate(agent_ids):
                if i != j:  # Don't create relationships with self
                    # Create political relationships (all senators have these)
                    political_value = random.uniform(-0.5, 0.5)
                    relationships.append(
                        PoliticalRelationship(
                            source_id=agent_a_id,
                            target_id=agent_b_id,
                            value=political_value
                        )
                    )
                    
                    # Create personal relationships (50% chance)
                    if random.random() < 0.5:
                        personal_value = random.uniform(-0.7, 0.7)
                        relationships.append(
                            PersonalRelationship(
                                source_id=agent_a_id,
                                target_id=agent_b_id,
                                value=personal_value
                            )
                        )
        
        return relationships
    
    def get_relationship_dynamics(
        self,
        relationship_type: str
    ) -> Dict[str, Any]:
        """
        Get dynamics information for a relationship type.
        
        Args:
            relationship_type: Relationship type identifier
            
        Returns:
            Dict[str, Any]: Dynamics information
        """
        dynamics = {
            "political": {
                "description": "Political relationship between senators",
                "decay_rate": 0.01,  # Slow decay
                "volatility": 0.2,   # Moderate volatility
                "event_impact": {
                    "senate.speech": 0.1,
                    "senate.debate": 0.05,
                    "senate.interjection": 0.15,
                    "senate.relationship": 0.3,
                }
            },
            "faction": {
                "description": "Faction-based relationship between senators",
                "decay_rate": 0.005,  # Very slow decay
                "volatility": 0.1,    # Low volatility
                "event_impact": {
                    "senate.speech": 0.05,
                    "senate.debate": 0.03,
                    "senate.interjection": 0.1,
                    "senate.relationship": 0.2,
                }
            },
            "personal": {
                "description": "Personal relationship between senators",
                "decay_rate": 0.02,  # Moderate decay
                "volatility": 0.3,   # High volatility
                "event_impact": {
                    "senate.speech": 0.15,
                    "senate.debate": 0.1,
                    "senate.interjection": 0.2,
                    "senate.relationship": 0.4,
                }
            }
        }
        
        return dynamics.get(relationship_type, {})


class SenateAgentBehaviorExtension(AgentBehaviorExtension):
    """
    Extension for Senate-specific agent behaviors.
    
    This class defines custom behaviors for agents in the Senate domain,
    such as giving speeches, participating in debates, etc.
    """
    
    def extend_agent(self, agent: BaseAgent) -> None:
        """
        Extend an agent with Senate-specific behaviors.
        
        Args:
            agent: The agent to extend
        """
        # Add Senate-specific attributes
        if "faction" not in agent.attributes:
            agent.attributes["faction"] = "Neutral"
        
        if "rank" not in agent.attributes:
            agent.attributes["rank"] = 1
        
        if "oratory_skill" not in agent.attributes:
            agent.attributes["oratory_skill"] = 0.5
        
        # Add Senate-specific state
        if "current_stance" not in agent.state:
            agent.state["current_stance"] = None
        
        if "active_debate_topic" not in agent.state:
            agent.state["active_debate_topic"] = None
        
        if "current_speaker" not in agent.state:
            agent.state["current_speaker"] = None
        
        if "debate_in_progress" not in agent.state:
            agent.state["debate_in_progress"] = False
    
    def process_domain_event(self, agent: BaseAgent, event: BaseEvent) -> None:
        """
        Process a Senate-specific event for an agent.
        
        Args:
            agent: The agent processing the event
            event: The event to process
        """
        # Handle different event types
        if event.event_type == "senate.speech":
            self._process_speech_event(agent, event)
        elif event.event_type == "senate.debate":
            self._process_debate_event(agent, event)
        elif event.event_type == "senate.reaction":
            self._process_reaction_event(agent, event)
        elif event.event_type == "senate.interjection":
            self._process_interjection_event(agent, event)
        elif event.event_type == "senate.relationship":
            self._process_relationship_event(agent, event)
    
    def _process_speech_event(self, agent: BaseAgent, event: BaseEvent) -> None:
        """Process a speech event."""
        # Skip own speeches
        if event.source == agent.id:
            return
        
        # Update agent state
        agent.state["current_speaker"] = event.source
        
        # Record the event in memory if available
        if hasattr(agent, "memory") and agent.memory:
            agent.memory.add_memory({
                "type": "speech",
                "speaker": event.source,
                "topic": event.data.get("topic"),
                "stance": event.data.get("stance"),
                "content": event.data.get("content")
            })
    
    def _process_debate_event(self, agent: BaseAgent, event: BaseEvent) -> None:
        """Process a debate event."""
        debate_event_type = event.data.get("debate_event_type")
        
        if debate_event_type == "debate_start":
            agent.state["debate_in_progress"] = True
            agent.state["active_debate_topic"] = event.data.get("topic")
            
        elif debate_event_type == "debate_end":
            agent.state["debate_in_progress"] = False
            agent.state["active_debate_topic"] = None
            agent.state["current_speaker"] = None
            
        elif debate_event_type == "speaker_change":
            agent.state["current_speaker"] = event.data.get("speaker_id")
        
        # Record the event in memory if available
        if hasattr(agent, "memory") and agent.memory:
            agent.memory.add_memory({
                "type": "debate",
                "debate_event_type": debate_event_type,
                "topic": event.data.get("topic")
            })
    
    def _process_reaction_event(self, agent: BaseAgent, event: BaseEvent) -> None:
        """Process a reaction event."""
        # Skip own reactions
        if event.source == agent.id:
            return
        
        # Record the event in memory if available
        if hasattr(agent, "memory") and agent.memory:
            agent.memory.add_memory({
                "type": "reaction",
                "reactor": event.source,
                "target_event_id": event.data.get("target_event_id"),
                "reaction_type": event.data.get("reaction_type"),
                "content": event.data.get("content")
            })
    
    def _process_interjection_event(self, agent: BaseAgent, event: BaseEvent) -> None:
        """Process an interjection event."""
        # Skip own interjections
        if event.source == agent.id:
            return
        
        # Record the event in memory if available
        if hasattr(agent, "memory") and agent.memory:
            agent.memory.add_memory({
                "type": "interjection",
                "interjecter": event.source,
                "target_speaker": event.target,
                "interjection_type": event.data.get("interjection_type"),
                "content": event.data.get("content")
            })
    
    def _process_relationship_event(self, agent: BaseAgent, event: BaseEvent) -> None:
        """Process a relationship event."""
        # Record the event in memory if available
        if hasattr(agent, "memory") and agent.memory:
            agent.memory.add_memory({
                "type": "relationship",
                "source_id": event.data.get("source_id"),
                "target_id": event.data.get("target_id"),
                "relationship_type": event.data.get("relationship_type"),
                "change_value": event.data.get("change_value"),
                "reason": event.data.get("reason")
            })
    
    def generate_domain_actions(self, agent: BaseAgent) -> List[BaseEvent]:
        """
        Generate Senate-specific actions for an agent.
        
        Args:
            agent: The agent generating actions
            
        Returns:
            List[BaseEvent]: List of generated events
        """
        from .events.senate_events import (
            SpeechEvent,
            ReactionEvent,
            InterjectionEvent,
        )
        import random
        
        events = []
        
        # If in a debate and not currently speaking, consider generating a speech
        if agent.state.get("debate_in_progress", False) and agent.state.get("active_debate_topic") and agent.state.get("current_speaker") != agent.id:
            # Chance to speak based on rank and oratory skill
            speak_chance = 0.1 + (agent.attributes.get("rank", 1) * 0.05) + (agent.attributes.get("oratory_skill", 0.5) * 0.2)
            
            if random.random() < speak_chance:
                # Generate a speech
                topic = agent.state.get("active_debate_topic")
                stance = agent.state.get("current_stance") or random.choice(["support", "oppose", "neutral"])
                
                # Create speech event
                speech_event = SpeechEvent(
                    speaker_id=agent.id,
                    content=f"As a {agent.attributes.get('faction', 'Neutral')} senator, I {stance} this proposal about {topic}.",
                    topic=topic,
                    stance=stance,
                    source=agent.id
                )
                
                events.append(speech_event)
        
        # If someone else is speaking, consider generating a reaction or interjection
        current_speaker = agent.state.get("current_speaker")
        if current_speaker and current_speaker != agent.id:
            # Chance to react based on personality
            react_chance = 0.05 + (agent.attributes.get("rank", 1) * 0.02)
            
            if random.random() < react_chance:
                # Generate a reaction
                reaction_types = ["approval", "disapproval", "surprise", "confusion"]
                reaction_type = random.choice(reaction_types)
                
                # Create reaction event
                reaction_event = ReactionEvent(
                    reactor_id=agent.id,
                    target_event_id="current_speech",  # This would be the actual event ID in practice
                    reaction_type=reaction_type,
                    content=f"Reacts with {reaction_type}",
                    source=agent.id,
                    target=current_speaker
                )
                
                events.append(reaction_event)
            
            # Chance to interject based on personality and rank
            interject_chance = 0.03 + (agent.attributes.get("rank", 1) * 0.03)
            
            if random.random() < interject_chance:
                # Generate an interjection
                interjection_types = ["support", "opposition", "question", "clarification", "procedural"]
                interjection_type = random.choice(interjection_types)
                
                # Create interjection event
                interjection_event = InterjectionEvent(
                    interjecter_id=agent.id,
                    target_speaker_id=current_speaker,
                    interjection_type=interjection_type,
                    content=f"Interjects with {interjection_type}",
                    source=agent.id,
                    target=current_speaker
                )
                
                events.append(interjection_event)
        
        return events


class SenateConfigExtension(DomainConfigExtension):
    """
    Extension for Senate-specific configuration.
    
    This class defines configuration parameters for the Senate domain,
    such as debate rules, voting thresholds, etc.
    """
    
    def get_default_config(self) -> Dict[str, Any]:
        """
        Get the default configuration for the Senate domain.
        
        Returns:
            Dict[str, Any]: Default configuration
        """
        return {
            "debate": {
                "max_rounds": 3,
                "speech_time_limit": 120,  # seconds
                "interjection_limit": 2,   # per speech
                "reaction_limit": 5,       # per speech
            },
            "voting": {
                "majority_threshold": 0.5,
                "supermajority_threshold": 0.67,
                "abstention_allowed": True,
            },
            "factions": {
                "enabled": True,
                "faction_list": ["Optimates", "Populares", "Neutral"],
            },
            "relationships": {
                "initial_range": (-0.3, 0.3),
                "max_change_per_event": 0.2,
            },
            "simulation": {
                "year": -100,  # 100 BCE
                "historical_accuracy": 0.7,  # 0.0 to 1.0
                "random_seed": None,  # Set for reproducible results
            }
        }
    
    def validate_config(self, config: Dict[str, Any]) -> List[str]:
        """
        Validate a configuration for the Senate domain.
        
        Args:
            config: The configuration to validate
            
        Returns:
            List[str]: List of validation errors, empty if valid
        """
        errors = []
        
        # Check debate settings
        if "debate" in config:
            debate_config = config["debate"]
            if "max_rounds" in debate_config and not isinstance(debate_config["max_rounds"], int):
                errors.append("debate.max_rounds must be an integer")
            if "speech_time_limit" in debate_config and not isinstance(debate_config["speech_time_limit"], int):
                errors.append("debate.speech_time_limit must be an integer")
        
        # Check voting settings
        if "voting" in config:
            voting_config = config["voting"]
            if "majority_threshold" in voting_config:
                threshold = voting_config["majority_threshold"]
                if not isinstance(threshold, (int, float)) or threshold < 0 or threshold > 1:
                    errors.append("voting.majority_threshold must be a number between 0 and 1")
        
        # Check simulation settings
        if "simulation" in config:
            sim_config = config["simulation"]
            if "year" in sim_config and not isinstance(sim_config["year"], int):
                errors.append("simulation.year must be an integer")
            if "historical_accuracy" in sim_config:
                accuracy = sim_config["historical_accuracy"]
                if not isinstance(accuracy, (int, float)) or accuracy < 0 or accuracy > 1:
                    errors.append("simulation.historical_accuracy must be a number between 0 and 1")
        
        return errors
    
    def apply_config(self, config: Dict[str, Any]) -> None:
        """
        Apply a configuration to the Senate domain.
        
        Args:
            config: The configuration to apply
        """
        # This would typically set global parameters or initialize components
        # based on the configuration. For now, we'll just log that it's applied.
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Applied Senate domain configuration: {config}")


class SenateDomain:
    """
    Roman Senate domain implementation.
    
    This class represents the Roman Senate domain and provides access to
    its extension points and components.
    """
    
    def __init__(self):
        """Initialize the Senate domain."""
        self.event_registry = SenateEventRegistry()
        self.memory_extension = SenateMemoryExtension()
        self.relationship_extension = SenateRelationshipExtension()
        self.agent_behavior_extension = SenateAgentBehaviorExtension()
        self.config_extension = SenateConfigExtension()
        
        # Default configuration
        self.config = self.config_extension.get_default_config()
    
    def get_extension(self, extension_point_id: str) -> Optional[DomainExtensionPoint]:
        """
        Get an extension point implementation.
        
        Args:
            extension_point_id: Extension point identifier
            
        Returns:
            Optional[DomainExtensionPoint]: The extension point implementation, or None if not found
        """
        extension_map = {
            "event_type_registry": self.event_registry,
            "memory_type_extension": self.memory_extension,
            "relationship_type_extension": self.relationship_extension,
            "agent_behavior_extension": self.agent_behavior_extension,
            "domain_config_extension": self.config_extension,
        }
        
        return extension_map.get(extension_point_id)
    
    def configure(self, config: Dict[str, Any]) -> List[str]:
        """
        Configure the Senate domain.
        
        Args:
            config: Configuration parameters
            
        Returns:
            List[str]: List of validation errors, empty if valid
        """
        # Validate the configuration
        errors = self.config_extension.validate_config(config)
        if errors:
            return errors
        
        # Apply the configuration
        self.config = config
        self.config_extension.apply_config(config)
        
        return []


def register_senate_domain() -> SenateDomain:
    """
    Create and initialize the Senate domain.
    
    This function creates a new Senate domain instance and initializes it,
    making it ready for use in simulations.
    
    Returns:
        SenateDomain: The initialized Senate domain
    """
    # Create domain instance
    domain = SenateDomain()
    
    # Initialize the domain components
    domain.event_registry.register_event_types()
    domain.memory_extension.register_memory_types()
    domain.relationship_extension.register_relationship_types()
    
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Roman Senate domain initialized with all components")
    
    return domain