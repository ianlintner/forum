"""
Roman Senate Web Server Integration

This module provides integration between the Roman Senate simulation's event system
and the FastAPI websocket server.
"""

import asyncio
import logging
from typing import Optional, Dict, Any, List

from ..core.events.base import BaseEvent, EventHandler
from ..core.events.event_bus import EventBus
from .server import websocket_manager, EventSerializer

# Set up logging
logger = logging.getLogger(__name__)


class WebSocketEventBridge(EventHandler):
    """
    Bridge between the event bus and WebSocket connections.
    
    This class subscribes to the event bus and forwards events to
    connected WebSocket clients.
    """
    
    def __init__(self, event_types: Optional[List[str]] = None):
        """
        Initialize the WebSocket event bridge.
        
        Args:
            event_types: Optional list of event types to forward. If None, all events are forwarded.
        """
        self.event_types = event_types
        self.event_serializer = EventSerializer()
        logger.info(f"WebSocketEventBridge initialized with event types: {event_types or 'ALL'}")
        
    def handle_event(self, event: BaseEvent) -> None:
        """
        Handle an event by broadcasting it to all WebSocket clients.
        
        Args:
            event: The event to broadcast
        """
        # Check if we should forward this event type
        if self.event_types is not None and event.event_type not in self.event_types:
            logger.debug(f"Skipping event {event.event_type} (not in configured event types)")
            return
        # Log event details at debug level
        # Get event ID using either get_id() method or event_id attribute
        event_id = None
        if hasattr(event, "get_id"):
            event_id = event.get_id()
        elif hasattr(event, "event_id"):
            event_id = event.event_id
        else:
            # For events without an ID, use a placeholder
            event_id = "unknown-id"
            
        logger.debug(f"Processing event: type={event.event_type}, id={event_id}, source={event.source}, target={event.target}")
            
            
        # Serialize the event to JSON
        try:
            event_json = self.event_serializer.serialize_event(event)
            
            # Create a task to broadcast the event
            asyncio.create_task(websocket_manager.broadcast(event_json))
            
            # Log successful broadcast
            client_count = len(websocket_manager.active_connections)
            if client_count > 0:
                logger.info(f"Forwarded event {event.event_type} to {client_count} WebSocket client(s)")
            else:
                logger.debug(f"No active WebSocket clients to receive event {event.event_type}")
                
        except Exception as e:
            logger.error(f"Error processing event {event.event_type}: {e}")


def setup_event_bridge(event_bus: EventBus, event_types: Optional[List[str]] = None) -> WebSocketEventBridge:
    """
    Set up the WebSocket event bridge to listen for events.
    
    Args:
        event_bus: The event bus to subscribe to
        event_types: Optional list of event types to forward. If None, all events are forwarded.
        
    Returns:
        WebSocketEventBridge: The configured event bridge
    """
    # Default important event types if none specified
    if event_types is None:
        # Subscribe to all events by default
        logger.info("No specific event types provided, will forward all events")
    else:
        logger.info(f"Will forward these specific event types: {event_types}")
    
    # Create a WebSocket event bridge
    event_bridge = WebSocketEventBridge(event_types)
    
    # Subscribe to specific event types or all events
    if event_types:
        for event_type in event_types:
            event_bus.subscribe(event_type, event_bridge)
        logger.info(f"WebSocket event bridge subscribed to {len(event_types)} event types")
    else:
        event_bus.subscribe_to_all(event_bridge)
        logger.info("WebSocket event bridge subscribed to ALL events")
    
    # Log the active connection count
    logger.info(f"Current WebSocket connections: {len(websocket_manager.active_connections)}")
    
    return event_bridge


async def run_simulation_with_websocket(
    senators: int = 10,
    debate_rounds: int = 3,
    topics: int = 3,
    year: int = -100,
    provider: str = "mock",
    model: Optional[str] = None,
    event_bus: Optional[EventBus] = None
) -> Dict[str, Any]:
    """
    Run a simulation with WebSocket integration.
    
    This function runs a simulation and ensures events are forwarded to WebSocket clients.
    
    Args:
        senators: Number of senators to simulate
        debate_rounds: Number of debate rounds per topic
        topics: Number of topics to debate
        year: Year in Roman history (negative for BCE)
        provider: LLM provider to use
        model: LLM model to use
        event_bus: Optional event bus to use. If None, a new one is created.
        
    Returns:
        Dict[str, Any]: The simulation results
    """
    # Import the simulation function
    from ..cli import run_framework_simulation
    
    # Create an event bus if one wasn't provided
    if event_bus is None:
        event_bus = EventBus()
        
    # Set up the WebSocket event bridge
    setup_event_bridge(event_bus)
    
    # Run the simulation
    results = await run_framework_simulation(
        senators=senators,
        debate_rounds=debate_rounds,
        topics=topics,
        year=year,
        provider=provider,
        model=model
    )
    
    return results