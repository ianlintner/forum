"""
Roman Senate AI Game
Enhanced Senator Agent Module

This module provides an enhanced version of the EventDrivenSenatorAgent
with persistent memory and relationship capabilities.

Part of the Migration Plan: Phase 3 - Relationship System.
"""

import asyncio
import logging
import random
import datetime
from typing import Dict, List, Any, Optional, Tuple, Union

from ..utils.llm.base import LLMProvider
from ..core.interjection import Interjection, InterjectionTiming, generate_fallback_interjection
from .agent_memory import AgentMemory
from .event_memory import EventMemory
from .enhanced_event_memory import EnhancedEventMemory
from .memory_persistence_manager import MemoryPersistenceManager
from .event_driven_senator_agent import EventDrivenSenatorAgent
from .relationship_manager import RelationshipManager, SenatorRelationship
from ..core.events import (
    Event, 
    EventBus, 
    SpeechEvent, 
    DebateEvent,
    DebateEventType,
    ReactionEvent,
    InterjectionEvent,
    InterjectionType
)

logger = logging.getLogger(__name__)


class EnhancedSenatorAgent(EventDrivenSenatorAgent):
    """
    Enhanced implementation of a Roman Senator agent with persistent memory and relationships.
    
    This class extends the EventDrivenSenatorAgent with:
    - Persistent memory between sessions
    - Memory decay and importance weighting
    - Memory-based decision making
    - Memory narrative generation
    - Relationship tracking and influence
    - Relationship-based decision making
    """
    
    def __init__(
        self,
        senator: Dict[str, Any],
        llm_provider: LLMProvider,
        event_bus: EventBus,
        memory_manager: Optional[MemoryPersistenceManager] = None,
        relationship_manager: Optional[RelationshipManager] = None
    ):
        """
        Initialize an enhanced senator agent.
        
        Args:
            senator: Dictionary of senator attributes
            llm_provider: Language model provider for generating responses
            event_bus: Event bus for event handling
            memory_manager: Optional memory persistence manager
            relationship_manager: Optional relationship manager for senator relationships
        """
        # Initialize with base senator properties
        self.senator = senator
        self.llm_provider = llm_provider
        self.current_stance = None
        
        # Generate a unique ID for this senator if not present
        if "id" not in self.senator:
            self.senator["id"] = f"senator_{self.senator['name'].lower().replace(' ', '_')}"
        
        # Create enhanced memory
        self.memory = EnhancedEventMemory(senator_id=self.senator["id"])
        
        self.event_bus = event_bus
        self.active_debate_topic = None
        self.current_speaker = None
        self.debate_in_progress = False
        
        # Memory persistence manager
        self.memory_manager = memory_manager or MemoryPersistenceManager()
        
        # Relationship manager
        self.relationship_manager = relationship_manager or RelationshipManager(event_bus=event_bus)
        
        # Try to load existing memory
        self._load_memory()
        
        # Subscribe to relevant event types
        self.subscribe_to_events()
        
        logger.info(f"Enhanced senator agent initialized for {self.name}")
        
    def get_relationship_with(self, other_senator_id: str) -> Optional[SenatorRelationship]:
        """
        Get this senator's relationship with another senator.
        
        Args:
            other_senator_id: ID of the other senator
            
        Returns:
            Optional[SenatorRelationship]: The relationship, or None if not found
        """
        return self.relationship_manager.get_relationship_between(
            self.senator["id"],
            other_senator_id
        )
        
    def get_relationship_sentiment(self, other_senator_id: str) -> float:
        """
        Get the sentiment between this senator and another senator.
        
        Args:
            other_senator_id: ID of the other senator
            
        Returns:
            float: Sentiment score (-1.0 to 1.0), 0.0 if no relationship exists
        """
        return self.relationship_manager.get_relationship_sentiment(
            self.senator["id"],
            other_senator_id
        )
        
    def get_allies(self, limit: int = 5) -> List[Tuple[str, float]]:
        """
        Get this senator's strongest allies.
        
        Args:
            limit: Maximum number of allies to return
            
        Returns:
            List[Tuple[str, float]]: List of (ally_id, sentiment) pairs, sorted by sentiment
        """
        return self.relationship_manager.get_strongest_allies(self.senator["id"], limit)
        
    def get_rivals(self, limit: int = 5) -> List[Tuple[str, float]]:
        """
        Get this senator's strongest rivals.
        
        Args:
            limit: Maximum number of rivals to return
            
        Returns:
            List[Tuple[str, float]]: List of (rival_id, sentiment) pairs, sorted by sentiment
        """
        return self.relationship_manager.get_strongest_rivals(self.senator["id"], limit)
        
    def create_relationship(
        self,
        other_senator_id: str,
        relationship_type: str = "political",
        strength: float = 0.0,
        attributes: Optional[Dict[str, Any]] = None
    ) -> SenatorRelationship:
        """
        Create a relationship with another senator.
        
        Args:
            other_senator_id: ID of the other senator
            relationship_type: Type of relationship (political, family, etc.)
            strength: Initial strength (-1.0 to 1.0)
            attributes: Additional relationship attributes
            
        Returns:
            SenatorRelationship: The created relationship
            
        Raises:
            ValueError: If a relationship already exists
        """
        return self.relationship_manager.create_relationship(
            self.senator["id"],
            other_senator_id,
            relationship_type,
            strength,
            attributes
        )
        
    def get_relationships_summary(self) -> Dict[str, Any]:
        """
        Get a summary of this senator's relationships.
        
        Returns:
            Dict[str, Any]: Summary of relationships, including allies and rivals
        """
        allies = self.get_allies()
        rivals = self.get_rivals()
        
        ally_count = len(allies)
        rival_count = len(rivals)
        
        strongest_ally = allies[0] if allies else (None, 0)
        strongest_rival = rivals[0] if rivals else (None, 0)
        
        return {
            "total_relationships": ally_count + rival_count,
            "allies": {
                "count": ally_count,
                "strongest": strongest_ally
            },
            "rivals": {
                "count": rival_count,
                "strongest": strongest_rival
            }
        }
        
    async def consider_relationships(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Consider relationships when making decisions.
        
        This method extends the decision-making process to take into account
        the senator's relationships with other senators.
        
        Args:
            context: Context information for decision making
            
        Returns:
            Dict[str, Any]: Updated context with relationship considerations
        """
        # Get relationships relevant to the context
        relevant_relationships = []
        
        # Check if there's a target senator in the context
        target_senator_id = context.get("target_senator_id")
        if target_senator_id:
            relationship = self.get_relationship_with(target_senator_id)
            if relationship:
                sentiment = relationship.get_sentiment()
                relevant_relationships.append({
                    "senator_id": target_senator_id,
                    "sentiment": sentiment,
                    "history": relationship.get_history()[-3:] if relationship.get_history() else []
                })
                
        # Add relationship information to context
        context["relationships"] = {
            "relevant": relevant_relationships,
            "allies": self.get_allies(3),  # Just get top 3 allies
            "rivals": self.get_rivals(3)   # Just get top 3 rivals
        }
        
        return context
