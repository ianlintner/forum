"""
Roman Senate AI Game
Enhanced Senator Agent Module

This module provides an enhanced version of the EventDrivenSenatorAgent
with persistent memory capabilities.
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
    Enhanced implementation of a Roman Senator agent with persistent memory.
    
    This class extends the EventDrivenSenatorAgent with:
    - Persistent memory between sessions
    - Memory decay and importance weighting
    - Memory-based decision making
    - Memory narrative generation
    """
    
    def __init__(
        self, 
        senator: Dict[str, Any], 
        llm_provider: LLMProvider, 
        event_bus: EventBus,
        memory_manager: Optional[MemoryPersistenceManager] = None
    ):
        """Initialize an enhanced senator agent."""
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
        
        # Try to load existing memory
        self._load_memory()
        
        # Subscribe to relevant event types
        self.subscribe_to_events()
        
        logger.info(f"Enhanced senator agent initialized for {self.name}")
