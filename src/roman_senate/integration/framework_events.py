"""
Event Bridging between Roman Senate and agentic_game_framework.

This module provides adapter classes that translate events between the
Roman Senate event system and the agentic_game_framework event system.

Part of the Migration Plan: Phase 4 - Integration Layer.
"""

from typing import Dict, Any, Optional, Type, Mapping, Union, cast
from datetime import datetime

from agentic_game_framework.events.base import BaseEvent as FrameworkBaseEvent
from agentic_game_framework.events.event_bus import EventBus as FrameworkEventBus

from ..core.events.base import BaseEvent as RomanBaseEvent
from ..core.events.event_bus import EventBus as RomanEventBus


class EventBridgeAdapter:
    """
    Bidirectional event bridge between Roman Senate and agentic_game_framework.
    
    This adapter subscribes to events from both systems and forwards them
    appropriately to the other system, translating between event formats.
    
    Attributes:
        roman_event_bus: The Roman Senate event bus
        framework_event_bus: The agentic_game_framework event bus
        roman_to_framework_adapter: Adapter for Roman -> Framework events
        framework_to_roman_adapter: Adapter for Framework -> Roman events
        event_type_mappings: Mappings between Roman and Framework event types
    """
    
    def __init__(
        self,
        roman_event_bus: RomanEventBus,
        framework_event_bus: FrameworkEventBus,
        event_type_mappings: Optional[Dict[str, str]] = None
    ):
        """
        Initialize the event bridge.
        
        Args:
            roman_event_bus: The Roman Senate event bus
            framework_event_bus: The agentic_game_framework event bus
            event_type_mappings: Optional mappings between event types.
                Keys are Roman event types, values are Framework event types.
        """
        self.roman_event_bus = roman_event_bus
        self.framework_event_bus = framework_event_bus
        self.event_type_mappings = event_type_mappings or {}
        
        # Create the adapters
        self.roman_to_framework_adapter = RomanToFrameworkEventAdapter(
            self.event_type_mappings)
        self.framework_to_roman_adapter = FrameworkToRomanEventAdapter(
            {v: k for k, v in self.event_type_mappings.items()})
        
        # Set up event handlers
        self._setup_event_handlers()
    
    def _setup_event_handlers(self) -> None:
        """Set up event handlers for both systems."""
        # Create handler for Roman events
        class RomanEventHandler:
            def __init__(self, bridge: 'EventBridgeAdapter'):
                self.bridge = bridge
                
            def handle_event(self, event: RomanBaseEvent) -> None:
                # Convert and forward Roman events to Framework
                framework_event = self.bridge.roman_to_framework_adapter.adapt(event)
                if framework_event:
                    self.bridge.framework_event_bus.publish(framework_event)
        
        # Create handler for Framework events
        class FrameworkEventHandler:
            def __init__(self, bridge: 'EventBridgeAdapter'):
                self.bridge = bridge
                
            def handle_event(self, event: FrameworkBaseEvent) -> None:
                # Convert and forward Framework events to Roman
                roman_event = self.bridge.framework_to_roman_adapter.adapt(event)
                if roman_event:
                    self.bridge.roman_event_bus.publish(roman_event)
        
        # Register handlers with both event buses
        roman_handler = RomanEventHandler(self)
        framework_handler = FrameworkEventHandler(self)
        
        # Subscribe to all events
        self.roman_event_bus.subscribe_to_all(roman_handler)
        # For framework bus, we need to wrap the handler in a callable
        # that matches the framework's handler signature
        self.framework_event_bus.subscribe_to_all(framework_handler)
    
    def add_event_type_mapping(self, roman_type: str, framework_type: str) -> None:
        """
        Add a mapping between Roman and Framework event types.
        
        Args:
            roman_type: Roman Senate event type
            framework_type: Corresponding agentic_game_framework event type
        """
        self.event_type_mappings[roman_type] = framework_type
        # Update adapters
        self.roman_to_framework_adapter.add_mapping(roman_type, framework_type)
        self.framework_to_roman_adapter.add_mapping(framework_type, roman_type)


class RomanToFrameworkEventAdapter:
    """
    Adapter that converts Roman Senate events to agentic_game_framework events.
    
    This adapter translates events from the Roman Senate format to the
    agentic_game_framework format, handling differences in attributes
    and structure.
    
    Attributes:
        event_type_mappings: Mappings from Roman event types to Framework event types
    """
    
    def __init__(self, event_type_mappings: Dict[str, str] = None):
        """
        Initialize the adapter.
        
        Args:
            event_type_mappings: Mappings from Roman event types to Framework event types.
                If a type is not in this mapping, it will use the original type.
        """
        self.event_type_mappings = event_type_mappings or {}
    
    def adapt(self, roman_event: RomanBaseEvent) -> Optional[FrameworkBaseEvent]:
        """
        Convert a Roman event to a Framework event.
        
        Args:
            roman_event: The Roman Senate event to convert
            
        Returns:
            Optional[FrameworkBaseEvent]: The converted Framework event,
                or None if conversion is not possible
        """
        # Map the event type
        framework_event_type = self.event_type_mappings.get(
            roman_event.event_type, roman_event.event_type)
        
        # Convert the timestamp - Framework uses datetime objects directly
        timestamp = roman_event.timestamp
        
        # Create the framework event
        framework_event = FrameworkBaseEvent(
            event_type=framework_event_type,
            source=roman_event.source,
            target=roman_event.target,
            data=roman_event.data,
            timestamp=timestamp,
            event_id=roman_event.get_id()
        )
        
        return framework_event
    
    def add_mapping(self, roman_type: str, framework_type: str) -> None:
        """
        Add a mapping from a Roman event type to a Framework event type.
        
        Args:
            roman_type: Roman Senate event type
            framework_type: Corresponding agentic_game_framework event type
        """
        self.event_type_mappings[roman_type] = framework_type


class FrameworkToRomanEventAdapter:
    """
    Adapter that converts agentic_game_framework events to Roman Senate events.
    
    This adapter translates events from the agentic_game_framework format to the
    Roman Senate format, handling differences in attributes and structure.
    
    Attributes:
        event_type_mappings: Mappings from Framework event types to Roman event types
    """
    
    def __init__(self, event_type_mappings: Dict[str, str] = None):
        """
        Initialize the adapter.
        
        Args:
            event_type_mappings: Mappings from Framework event types to Roman event types.
                If a type is not in this mapping, it will use the original type.
        """
        self.event_type_mappings = event_type_mappings or {}
    
    def adapt(self, framework_event: FrameworkBaseEvent) -> Optional[RomanBaseEvent]:
        """
        Convert a Framework event to a Roman event.
        
        Args:
            framework_event: The agentic_game_framework event to convert
            
        Returns:
            Optional[RomanBaseEvent]: The converted Roman Senate event,
                or None if conversion is not possible
        """
        # Map the event type
        roman_event_type = self.event_type_mappings.get(
            framework_event.event_type, framework_event.event_type)
        
        # Create the Roman event
        roman_event = RomanBaseEvent(
            event_type=roman_event_type,
            source=framework_event.source,
            target=framework_event.target,
            data=framework_event.data,
            timestamp=framework_event.timestamp,
            event_id=framework_event.get_id()
        )
        
        return roman_event
    
    def add_mapping(self, framework_type: str, roman_type: str) -> None:
        """
        Add a mapping from a Framework event type to a Roman event type.
        
        Args:
            framework_type: agentic_game_framework event type
            roman_type: Corresponding Roman Senate event type
        """
        self.event_type_mappings[framework_type] = roman_type