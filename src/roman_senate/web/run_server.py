#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Roman Senate Websocket Server Runner

This script provides a standalone entry point to run the Roman Senate websocket server.
"""

import os
import sys
import asyncio
import argparse
import logging
from typing import Optional

# Add the project root directory to the Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(script_dir)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import the server and integration modules
from src.roman_senate.web.server import run_server
from src.roman_senate.web.integration import run_simulation_with_websocket
from src.roman_senate.core.events.event_bus import EventBus
from src.roman_senate.utils.logging_utils import setup_logging

# Set up logging
logger = setup_logging()

def main():
    """
    Main entry point for the websocket server.
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Roman Senate Websocket Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind the server to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind the server to")
    parser.add_argument("--senators", type=int, default=10, help="Number of senators to simulate")
    parser.add_argument("--debate-rounds", type=int, default=3, help="Number of debate rounds per topic")
    parser.add_argument("--topics", type=int, default=3, help="Number of topics to debate")
    parser.add_argument("--year", type=int, default=-100, help="Year in Roman history (negative for BCE)")
    parser.add_argument("--provider", default="mock", help="LLM provider (mock, openai, ollama)")
    parser.add_argument("--model", help="LLM model name")
    parser.add_argument("--auto-start", action="store_true", help="Automatically start a simulation when the server starts")
    parser.add_argument("--verbose", "-v", action="store_true", help="Increase output verbosity")
    parser.add_argument("--log-level", help="Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)")
    parser.add_argument("--log-file", help="Custom log file path")
    
    args = parser.parse_args()
    
    # Set up logging with the specified options
    logger = setup_logging(log_level=args.log_level, log_file=args.log_file, verbose=args.verbose)
    
    # Log server startup
    logger.info("Roman Senate Websocket Server starting")
    logger.info(f"Server will run at http://{args.host}:{args.port}")
    logger.info(f"WebSocket endpoint at ws://{args.host}:{args.port}/ws")
    
    # Create an event bus
    event_bus = EventBus()
    
    # Auto-start a simulation if requested
    if args.auto_start:
        logger.info("Auto-starting simulation...")
        
        # Create a background task to run the simulation
        async def start_simulation():
            # Wait a moment for the server to start
            await asyncio.sleep(2)
            
            logger.info("Starting simulation...")
            
            # Run the simulation with websocket integration
            await run_simulation_with_websocket(
                senators=args.senators,
                debate_rounds=args.debate_rounds,
                topics=args.topics,
                year=args.year,
                provider=args.provider,
                model=args.model,
                event_bus=event_bus
            )
            
        # Create and start the task
        # Using asyncio.create_task() instead of get_event_loop() to avoid deprecation warning
        asyncio.create_task(start_simulation())
    
    # Run the server
    run_server(host=args.host, port=args.port, event_bus=event_bus)

if __name__ == "__main__":
    main()