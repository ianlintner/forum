"""
Roman Senate AI Game
Event Memory Module

This module extends the AgentMemory class with event-driven capabilities,
allowing senators to store and recall events they've observed or participated in.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

from .agent_memory import AgentMemory
from ..core.events import Event

logger = logging.getLogger(__name__)

class EventMemory(AgentMemory):
    """
    Enhanced memory for event-driven senator agents.
    
    This class extends the base AgentMemory with capabilities for storing
    and retrieving events, reactions, and event-related context.
    """
    
    def __init__(self):
        """Initialize an empty event memory."""
        super().__init__()
        # Store observed events
        self.event_history: List[Dict[str, Any]] = []
        # Store reactions to events
        self.reaction_history: List[Dict[str, Any]] = []
        # Store stance changes triggered by events
        self.stance_changes: Dict[str, List[Dict[str, Any]]] = {}
        # Track event-based relationships (how events affected relationships)
        self.event_relationships: Dict[str, List[Dict[str, Any]]] = {}
        
    def record_event(self, event: Event) -> None:
        """
        Record an observed event in memory.
        
        Args:
            event: The event to record
        """
        # Store basic event data
        event_data = {
            "event_id": event.event_id,
            "event_type": event.event_type,
            "timestamp": event.timestamp,
            "source": getattr(event.source, "name", str(event.source)) if event.source else "Unknown",
            "metadata": event.metadata.copy(),
            "recorded_at": datetime.now().isoformat()
        }
        
        # Add to event history
        self.event_history.append(event_data)
        
        # Also add as a general observation for backward compatibility
        source_name = getattr(event.source, "name", str(event.source)) if event.source else "Unknown"
        self.add_observation(f"Observed {event.event_type} event from {source_name}")
        
        logger.debug(f"Recorded event {event.event_id} in memory")
        
    def record_reaction(self, event_id: str, reaction_type: str, content: str) -> None:
        """
        Record a reaction to an event.
        
        Args:
            event_id: ID of the event being reacted to
            reaction_type: Type of reaction
            content: Content of the reaction
        """
        reaction_data = {
            "event_id": event_id,
            "reaction_type": reaction_type,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        
        self.reaction_history.append(reaction_data)
        logger.debug(f"Recorded reaction to event {event_id}")
        
    def record_stance_change(self, topic: str, old_stance: str, new_stance: str, reason: str, event_id: Optional[str] = None) -> None:
        """
        Record a change in stance on a topic.
        
        Args:
            topic: The topic the stance is about
            old_stance: Previous stance
            new_stance: New stance
            reason: Reason for the change
            event_id: Optional ID of the event that triggered the change
        """
        if topic not in self.stance_changes:
            self.stance_changes[topic] = []
            
        change_data = {
            "old_stance": old_stance,
            "new_stance": new_stance,
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        }
        
        if event_id:
            change_data["event_id"] = event_id
            
        self.stance_changes[topic].append(change_data)
        
        # Update voting history for backward compatibility
        self.record_vote(topic, new_stance)
        
        logger.debug(f"Recorded stance change on {topic} from {old_stance} to {new_stance}")
        
    def record_event_relationship_impact(self, senator_name: str, event_id: str, impact: float, reason: str) -> None:
        """
        Record how an event impacted a relationship with another senator.
        
        Args:
            senator_name: Name of the senator
            event_id: ID of the event that affected the relationship
            impact: Impact on relationship score
            reason: Reason for the impact
        """
        if senator_name not in self.event_relationships:
            self.event_relationships[senator_name] = []
            
        impact_data = {
            "event_id": event_id,
            "impact": impact,
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        }
        
        self.event_relationships[senator_name].append(impact_data)
        
        # Update relationship score for backward compatibility
        self.update_relationship(senator_name, impact)
        
        logger.debug(f"Recorded event {event_id} impact on relationship with {senator_name}: {impact}")
        
    def get_events_by_type(self, event_type: str) -> List[Dict[str, Any]]:
        """
        Get all events of a specific type.
        
        Args:
            event_type: The type of events to retrieve
            
        Returns:
            List of matching events
        """
        return [e for e in self.event_history if e["event_type"] == event_type]
        
    def get_events_by_source(self, source_name: str) -> List[Dict[str, Any]]:
        """
        Get all events from a specific source.
        
        Args:
            source_name: The source to filter by
            
        Returns:
            List of matching events
        """
        return [e for e in self.event_history if e["source"] == source_name]
        
    def get_reactions_to_event(self, event_id: str) -> List[Dict[str, Any]]:
        """
        Get all reactions to a specific event.
        
        Args:
            event_id: The event ID to filter by
            
        Returns:
            List of matching reactions
        """
        return [r for r in self.reaction_history if r["event_id"] == event_id]
        
    def get_stance_changes_for_topic(self, topic: str) -> List[Dict[str, Any]]:
        """
        Get all stance changes for a specific topic.
        
        Args:
            topic: The topic to filter by
            
        Returns:
            List of stance changes
        """
        return self.stance_changes.get(topic, [])
        
    def get_relationship_impacts_by_senator(self, senator_name: str) -> List[Dict[str, Any]]:
        """
        Get all relationship impacts with a specific senator.
        
        Args:
            senator_name: The senator to filter by
            
        Returns:
            List of relationship impacts
        """
        return self.event_relationships.get(senator_name, [])
        
    def get_recent_events(self, count: int = 5) -> List[Dict[str, Any]]:
        """
        Get the most recent events.
        
        Args:
            count: Maximum number of events to return
            
        Returns:
            List of recent events
        """
        # Sort by timestamp (most recent first)
        sorted_events = sorted(self.event_history, key=lambda e: e["timestamp"], reverse=True)
        return sorted_events[:count]