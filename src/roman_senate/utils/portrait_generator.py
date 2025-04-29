#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Roman Senate AI Game
Senator Portrait Generator

This module generates portraits for Roman senators using OpenAI's DALL-E model
and implements caching to avoid regenerating the same portraits.
"""

import os
import logging
import hashlib
import requests
from typing import Optional, Dict, Any
import openai
from pathlib import Path

logger = logging.getLogger(__name__)

class PortraitGenerator:
    """Generates and manages portraits for Roman senators."""
    
    def __init__(
        self, 
        portraits_dir: str = "portraits",
        model: str = "dall-e-3",
        size: str = "1024x1024",
        quality: str = "standard",
        style: str = "vivid"
    ):
        """
        Initialize the portrait generator.
        
        Args:
            portraits_dir: Directory to store portrait images
            model: DALL-E model to use
            size: Image size
            quality: Image quality
            style: Image style
        """
        self.portraits_dir = portraits_dir
        self.model = model
        self.size = size
        self.quality = quality
        self.style = style
        
        # Create portraits directory if it doesn't exist
        os.makedirs(self.portraits_dir, exist_ok=True)
        
        logger.info(f"Initialized PortraitGenerator with model: {model}")
    
    def _get_portrait_path(self, senator_name: str, faction: str) -> str:
        """
        Get the file path for a senator's portrait.
        
        Args:
            senator_name: Name of the senator
            faction: Political faction of the senator
            
        Returns:
            Path to the portrait file
        """
        # Sanitize the name and faction for use as a filename
        safe_name = senator_name.replace(" ", "_").lower()
        safe_faction = faction.replace(" ", "_").lower()
        
        # Create a filename using the naming convention {senator_name}_{faction}.png
        filename = f"{safe_name}_{safe_faction}.png"
        
        return os.path.join(self.portraits_dir, filename)
    
    def portrait_exists(self, senator_name: str, faction: str) -> bool:
        """
        Check if a portrait already exists for the given senator.
        
        Args:
            senator_name: Name of the senator
            faction: Political faction of the senator
            
        Returns:
            True if the portrait exists, False otherwise
        """
        portrait_path = self._get_portrait_path(senator_name, faction)
        return os.path.exists(portrait_path)
    
    def get_portrait_url(self, senator_name: str, faction: str) -> Optional[str]:
        """
        Get the URL for a senator's portrait.
        
        Args:
            senator_name: Name of the senator
            faction: Political faction of the senator
            
        Returns:
            URL to the portrait if it exists, None otherwise
        """
        if self.portrait_exists(senator_name, faction):
            # Get the relative path for use in URLs
            relative_path = os.path.relpath(
                self._get_portrait_path(senator_name, faction)
            )
            return f"/portraits/{os.path.basename(relative_path)}"
        return None
    
    def generate_portrait_prompt(self, senator_name: str, faction: str) -> str:
        """
        Generate a prompt for DALL-E to create a senator portrait.
        
        Args:
            senator_name: Name of the senator
            faction: Political faction of the senator
            
        Returns:
            Prompt string for DALL-E
        """
        # Base prompt for Roman senator portraits in KOEI strategy game style
        base_prompt = (
            f"Create a detailed portrait of Roman Senator {senator_name}. "
            "The style should resemble KOEI strategy game character portraits like those in SNES/PC Era - "
            "elegant, somewhat realistic but stylized ancient portraiture with a serious, dignified expression. "
            "The senator should be wearing a traditional Roman toga with appropriate rank insignia. "
            "The portrait should be a frontal face and upper shoulders view against a textured background. "
            "Use rich colors with warm tones and subtle lighting to highlight facial features. "
            "The overall aesthetic should evoke ancient Rome while maintaining the distinctive KOEI artistic style."
        )
        
        # Add faction-specific details
        if faction.lower() == "optimates":
            # Conservative aristocrats
            base_prompt += (
                "He should have a stern, traditional appearance with "
                "patrician features, possibly gray hair, and conservative styling. "
                "Include subtle symbols of wealth and traditional Roman values."
            )
        elif faction.lower() == "populares":
            # Populist reformers
            base_prompt += (
                "He should have a slightly more approachable expression, "
                "possibly younger appearance, with a less ostentatious but still dignified style. "
                "His expression should suggest determination and reformist ideals."
            )
        elif faction.lower() == "neutral":
            # Politically neutral
            base_prompt += (
                "He should have a balanced, thoughtful expression "
                "suggesting wisdom and careful deliberation. His appearance should be dignified but "
                "without strong signals of partisan alignment."
            )
            
        return base_prompt
    
    def generate_portrait(self, senator_name: str, faction: str) -> Optional[str]:
        """
        Generate a portrait for a senator using DALL-E.
        
        Args:
            senator_name: Name of the senator
            faction: Political faction of the senator
            
        Returns:
            Path to the generated portrait, or None if generation failed
        """
        portrait_path = self._get_portrait_path(senator_name, faction)
        
        # Check if portrait already exists
        if os.path.exists(portrait_path):
            logger.debug(f"Portrait already exists for {senator_name} ({faction})")
            return portrait_path
        
        # Generate prompt for DALL-E
        prompt = self.generate_portrait_prompt(senator_name, faction)
        logger.info(f"Generating new portrait for {senator_name} ({faction})")
        
        try:
            # Generate image using DALL-E
            response = openai.images.generate(
                model=self.model,
                prompt=prompt,
                size=self.size,
                quality=self.quality,
                style=self.style,
                n=1,
            )
            
            # Get the image URL from the response
            image_url = response.data[0].url
            
            # Download the image
            image_response = requests.get(image_url, stream=True)
            if image_response.status_code == 200:
                with open(portrait_path, "wb") as img_file:
                    for chunk in image_response.iter_content(1024):
                        img_file.write(chunk)
                
                logger.info(f"Portrait generated and saved to {portrait_path}")
                return portrait_path
            else:
                logger.error(f"Failed to download portrait image: {image_response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error generating portrait with DALL-E: {e}")
            return None