"""
Roman Senate Web Server

This module provides a FastAPI server with websocket endpoints to stream
the Roman Senate simulation events to connected clients.
"""

import asyncio
import json
import logging
import datetime
from typing import Dict, List, Any, Optional, Set

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from ..core.events.base import BaseEvent
from ..core.events.event_bus import EventBus

# Set up logging
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Roman Senate Simulation API",
    description="API for streaming Roman Senate simulation events",
    version="0.1.0",
)

# Add static files directory
from fastapi.staticfiles import StaticFiles
import os

# Get the directory of this file
current_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(current_dir, "static")

# Mount the static directory
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Store active websocket connections
active_connections: Set[WebSocket] = set()


class WebSocketManager:
    """
    Manager for WebSocket connections.
    
    This class handles the connection, disconnection, and broadcasting of messages
    to all connected WebSocket clients.
    """
    
    def __init__(self):
        """Initialize the WebSocket manager."""
        self.active_connections: Set[WebSocket] = set()
        self.connection_count = 0
        
    async def connect(self, websocket: WebSocket) -> int:
        """
        Connect a new WebSocket client.
        
        Args:
            websocket: The WebSocket connection to add
            
        Returns:
            int: A unique connection ID
        """
        await websocket.accept()
        self.active_connections.add(websocket)
        self.connection_count += 1
        connection_id = self.connection_count
        logger.info(f"Client connected. Connection ID: {connection_id}. Total connections: {len(self.active_connections)}")
        return connection_id
        
    def disconnect(self, websocket: WebSocket) -> None:
        """
        Disconnect a WebSocket client.
        
        Args:
            websocket: The WebSocket connection to remove
        """
        self.active_connections.remove(websocket)
        logger.info(f"Client disconnected. Total connections: {len(self.active_connections)}")
        
    async def broadcast(self, message: str) -> None:
        """
        Broadcast a message to all connected clients.
        
        Args:
            message: The message to broadcast
        """
        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error sending message to client: {e}")
                disconnected.add(connection)
                
        # Clean up any disconnected clients
        for connection in disconnected:
            self.disconnect(connection)


class EventSerializer:
    """
    Serializes Roman Senate events to JSON for websocket transmission.
    """
    
    @staticmethod
    def serialize_event(event: BaseEvent) -> str:
        """
        Convert an event to a JSON string.
        
        Args:
            event: The event to serialize
            
        Returns:
            str: JSON string representation of the event
        """
        # Get event ID using either get_id() method or event_id attribute
        event_id = None
        if hasattr(event, "get_id"):
            event_id = event.get_id()
        elif hasattr(event, "event_id"):
            event_id = event.event_id
        else:
            # For events without an ID, generate a simple one
            event_id = str(id(event))
        
        event_dict = {
            "event_id": event_id,
            "event_type": event.event_type,
            "timestamp": event.timestamp.isoformat(),
            "source": event.source,
            "target": event.target,
            "data": event.data
        }
        
        # Add additional metadata for better client-side display
        if hasattr(event, 'category'):
            event_dict['category'] = event.category
            
        # Ensure data is serializable
        try:
            return json.dumps(event_dict)
        except TypeError as e:
            logger.error(f"Error serializing event {event.event_type}: {e}")
            # Try to make data serializable by converting problematic values to strings
            if 'data' in event_dict and event_dict['data']:
                event_dict['data'] = {k: str(v) if not isinstance(v, (str, int, float, bool, list, dict, type(None)))
                                     else v for k, v in event_dict['data'].items()}
            return json.dumps(event_dict)


class WebSocketEventHandler:
    """
    Event handler that broadcasts events to WebSocket clients.
    
    This class subscribes to the event bus and forwards events to
    connected WebSocket clients.
    """
    
    def __init__(self, websocket_manager: WebSocketManager):
        """
        Initialize the WebSocket event handler.
        
        Args:
            websocket_manager: The WebSocket manager to use for broadcasting
        """
        self.websocket_manager = websocket_manager
        self.event_serializer = EventSerializer()
        
    def handle_event(self, event: BaseEvent) -> None:
        """
        Handle an event by broadcasting it to all WebSocket clients.
        
        Args:
            event: The event to broadcast
        """
        # Serialize the event to JSON
        event_json = self.event_serializer.serialize_event(event)
        
        # Create a task to broadcast the event
        asyncio.create_task(self.websocket_manager.broadcast(event_json))


# Create a WebSocket manager
websocket_manager = WebSocketManager()


@app.get("/")
async def root():
    """
    Root endpoint that redirects to the static HTML page.
    """
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/static/index.html")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for streaming simulation events.
    
    This endpoint accepts WebSocket connections and streams events to clients.
    """
    connection_id = await websocket_manager.connect(websocket)
    logger.info(f"New WebSocket connection established: ID={connection_id}")
    
    try:
        # Send a welcome message with simulation status
        simulation_status = "Active" if hasattr(app, "simulation_running") and app.simulation_running else "Inactive"
        
        await websocket.send_json({
            "type": "connection_established",
            "connection_id": connection_id,
            "message": "Connected to Roman Senate simulation",
            "timestamp": datetime.datetime.now().isoformat(),
            "data": {
                "simulation_status": simulation_status,
                "active_connections": len(websocket_manager.active_connections),
                "server_version": "0.2.0"  # Update version number when making significant changes
            }
        })
        
        # Keep the connection open
        while True:
            # Wait for any message from the client
            data = await websocket.receive_text()
            
            try:
                # Try to parse as JSON
                message = json.loads(data)
                
                # Handle different message types
                if isinstance(message, dict) and "type" in message:
                    if message["type"] == "ping":
                        # Respond to ping
                        await websocket.send_json({
                            "type": "pong",
                            "timestamp": datetime.datetime.now().isoformat()
                        })
                    elif message["type"] == "get_status":
                        # Send current status
                        await websocket.send_json({
                            "type": "status",
                            "timestamp": datetime.datetime.now().isoformat(),
                            "data": {
                                "simulation_status": simulation_status,
                                "active_connections": len(websocket_manager.active_connections)
                            }
                        })
                    else:
                        # Echo back unknown message types
                        await websocket.send_json({
                            "type": "echo",
                            "message": message,
                            "timestamp": datetime.datetime.now().isoformat()
                        })
                else:
                    # Echo back non-typed messages
                    await websocket.send_json({
                        "type": "echo",
                        "message": data,
                        "timestamp": datetime.datetime.now().isoformat()
                    })
            except json.JSONDecodeError:
                # For plain text messages
                await websocket.send_json({
                    "type": "echo",
                    "message": data,
                    "timestamp": datetime.datetime.now().isoformat()
                })
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)
        logger.info(f"WebSocket connection closed: ID={connection_id}")


class SimulationConfig(BaseModel):
    """Configuration for the simulation."""
    senators: int = Field(default=10, description="Number of senators to simulate")
    debate_rounds: int = Field(default=3, description="Number of debate rounds per topic")
    topics: int = Field(default=3, description="Number of topics to debate")
    year: int = Field(default=-100, description="Year in Roman history (negative for BCE)")
    provider: Optional[str] = Field(default="mock", description="LLM provider (mock, openai, ollama)")
    model: Optional[str] = Field(default=None, description="LLM model name")


@app.post("/start-simulation")
async def start_simulation(config: SimulationConfig):
    """
    Start a new simulation with the given configuration.
    
    Args:
        config: The simulation configuration
        
    Returns:
        dict: A response indicating the simulation has started
    """
    try:
        # Import the simulation function
        from ..cli import run_framework_simulation
        from ..web.integration import run_simulation_with_websocket
        
        # Set simulation status flag
        setattr(app, "simulation_running", True)
        
        # Log simulation start
        logger.info(f"Starting simulation with config: {config.dict()}")
        
        # Broadcast simulation start event to all connected clients
        start_message = {
            "type": "simulation_started",
            "event_type": "SimulationEvent",
            "timestamp": datetime.datetime.now().isoformat(),
            "source": "server",
            "target": "all_clients",
            "data": {
                "config": config.dict(),
                "message": "Roman Senate simulation is starting"
            }
        }
        
        await websocket_manager.broadcast(json.dumps(start_message))
        
        # Start the simulation in a background task using the websocket integration
        task = asyncio.create_task(
            run_simulation_with_websocket(
                senators=config.senators,
                debate_rounds=config.debate_rounds,
                topics=config.topics,
                year=config.year,
                provider=config.provider,
                model=config.model
            )
        )
        
        # Add a callback to update the simulation status when done
        def simulation_done(future):
            setattr(app, "simulation_running", False)
            logger.info("Simulation completed")
            
            # Broadcast simulation end event
            asyncio.create_task(
                websocket_manager.broadcast(
                    json.dumps({
                        "type": "simulation_ended",
                        "event_type": "SimulationEvent",
                        "timestamp": datetime.datetime.now().isoformat(),
                        "source": "server",
                        "target": "all_clients",
                        "data": {
                            "message": "Roman Senate simulation has ended"
                        }
                    })
                )
            )
            
        task.add_done_callback(simulation_done)
        
        return {
            "status": "success",
            "message": "Simulation started",
            "config": config.dict(),
            "active_connections": len(websocket_manager.active_connections)
        }
    except Exception as e:
        logger.error(f"Error starting simulation: {e}")
        # Set simulation status flag to false in case of error
        setattr(app, "simulation_running", False)
        
        # Try to notify clients about the error
        try:
            error_message = {
                "type": "simulation_error",
                "event_type": "ErrorEvent",
                "timestamp": datetime.datetime.now().isoformat(),
                "source": "server",
                "target": "all_clients",
                "data": {
                    "message": f"Failed to start simulation: {str(e)}"
                }
            }
            asyncio.create_task(websocket_manager.broadcast(json.dumps(error_message)))
        except Exception:
            pass  # Ignore errors in error handling
            
        raise HTTPException(status_code=500, detail=f"Failed to start simulation: {str(e)}")


def setup_event_handler(event_bus: EventBus) -> None:
    """
    Set up the WebSocket event handler to listen for events.
    
    Args:
        event_bus: The event bus to subscribe to
    """
    # Create a WebSocket event handler
    event_handler = WebSocketEventHandler(websocket_manager)
    
    # Subscribe to all events
    event_bus.subscribe_to_all(event_handler)
    
    logger.info("WebSocket event handler set up and subscribed to all events")


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Returns:
        FastAPI: The configured FastAPI application
    """
    return app


def run_server(host: str = "0.0.0.0", port: int = 8000, event_bus: Optional[EventBus] = None) -> None:
    """
    Run the FastAPI server.
    
    Args:
        host: The host to bind to
        port: The port to bind to
        event_bus: Optional event bus to subscribe to
    """
    import uvicorn
    
    # Set up the event handler if an event bus was provided
    if event_bus:
        setup_event_handler(event_bus)
    
    # Run the server
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    # Run the server directly if this module is executed as a script
    run_server()