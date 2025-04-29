#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Roman Senate AI Game
Portrait Testing Endpoints

This module provides endpoints for testing portrait generation.
"""

import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any

from ..utils.portrait_generator import PortraitGenerator

logger = logging.getLogger(__name__)

# Create a router for portrait testing endpoints
router = APIRouter(prefix="/portrait-testing", tags=["portrait-testing"])

class GeneratePortraitRequest(BaseModel):
    """Request model for generating a portrait."""
    senator_name: str
    faction: str

class GeneratePortraitResponse(BaseModel):
    """Response model for portrait generation."""
    success: bool
    portrait_url: Optional[str] = None
    message: str

def setup_portrait_testing_endpoints(app, portrait_generator: PortraitGenerator):
    """
    Set up testing endpoints for portrait generation.
    
    Args:
        app: The FastAPI application
        portrait_generator: The portrait generator to use
    """
    @router.post("/generate", response_model=GeneratePortraitResponse)
    async def generate_portrait(request: GeneratePortraitRequest):
        """
        Generate a portrait for testing.
        
        Args:
            request: The portrait generation request
            
        Returns:
            The portrait generation response
        """
        try:
            # Force regenerate the portrait
            portrait_path = portrait_generator.generate_portrait(
                senator_name=request.senator_name,
                faction=request.faction
            )
            
            if portrait_path:
                portrait_url = portrait_generator.get_portrait_url(
                    senator_name=request.senator_name,
                    faction=request.faction
                )
                
                return GeneratePortraitResponse(
                    success=True,
                    portrait_url=portrait_url,
                    message=f"Portrait generated successfully at {portrait_path}"
                )
            else:
                return GeneratePortraitResponse(
                    success=False,
                    message="Failed to generate portrait"
                )
        except Exception as e:
            logger.error(f"Error generating portrait: {e}")
            return GeneratePortraitResponse(
                success=False,
                message=f"Error generating portrait: {str(e)}"
            )
    
    # Include the router in the FastAPI app
    app.include_router(router)
    
    logger.info("Portrait testing endpoints set up")