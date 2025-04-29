#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Roman Senate AI Game
Portrait Server

This module provides functionality to serve senator portrait images
through FastAPI endpoints.
"""

import os
import logging
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

logger = logging.getLogger(__name__)

def setup_portrait_endpoints(app: FastAPI, portraits_dir: str = "portraits"):
    """
    Set up FastAPI endpoints to serve portrait images.
    
    Args:
        app: The FastAPI application
        portraits_dir: Directory containing portrait images
    """
    # Create portraits directory if it doesn't exist
    os.makedirs(portraits_dir, exist_ok=True)
    
    # Mount the portraits directory as a static files location
    app.mount("/portraits", StaticFiles(directory=portraits_dir), name="portraits")
    
    logger.info(f"Portrait endpoints set up with directory: {portraits_dir}")
    
    @app.get("/portrait/{senator_name}/{faction}")
    async def get_portrait(senator_name: str, faction: str):
        """
        Get a senator's portrait by name and faction.
        
        Args:
            senator_name: Name of the senator
            faction: Political faction of the senator
            
        Returns:
            The portrait image file
        """
        # Sanitize inputs for filename
        safe_name = senator_name.replace(" ", "_").lower()
        safe_faction = faction.replace(" ", "_").lower()
        
        # Create the filename
        filename = f"{safe_name}_{safe_faction}.png"
        filepath = os.path.join(portraits_dir, filename)
        
        # Check if the portrait exists
        if not os.path.exists(filepath):
            logger.warning(f"Portrait not found: {filepath}")
            raise HTTPException(status_code=404, detail="Portrait not found")
        
        return FileResponse(filepath)