#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Roman Senate AI Game
Player Actions Module

This module provides functionality for player actions during Senate sessions.
"""

import logging
import random
from typing import Dict, List, Any, Optional, Tuple

from .player import Player
from .player_ui import PlayerUI
from ..utils.config import LLM_PROVIDER, LLM_MODEL
from ..debate.speech_generator import generate_speech_text, generate_chat_completion

logger = logging.getLogger(__name__)

class PlayerActions:
    """Handles player actions during Senate sessions."""
    
    def __init__(self, player: Player, ui: PlayerUI):
        """
        Initialize the PlayerActions handler.
        
        Args:
            player: The player instance
            ui: The PlayerUI instance for user interaction
        """
        self.player = player
        self.ui = ui
        logger.info(f"PlayerActions initialized for player: {player.name}")
    
    async def make_speech(
        self, 
        topic: str, 
        stance: str = "neutral",
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Allow the player to make a speech on the current topic.
        
        Args:
            topic: The debate topic
            stance: The player's stance on the topic ('support', 'oppose', 'neutral')
            context: Additional context for speech generation
            
        Returns:
            Dictionary with speech result information
        """
        if context is None:
            context = {}
            
        # Get player attributes
        player_info = {
            "name": self.player.name,
            "faction": self.player.faction,
            "background": self.player.background,
            "skills": self.player.skills,
            "oratory_skill": self.player.skills.get("oratory", 1)
        }
        
        # Generate speech options based on topic and player attributes
        speech_options = await self._generate_speech_options(topic, stance, player_info, context)
        
        # Present options to player
        selected_option_index = self.ui.display_speech_options(topic, speech_options)
        selected_option = speech_options[selected_option_index]
        
        # Generate full speech based on selected option
        with self.ui.display_loading(message=f"Generating your speech...") as progress:
            task = progress.add_task("Generating...", total=1)
            
            speech_text = await self._generate_full_speech(
                topic, 
                selected_option,
                player_info,
                context
            )
            
            progress.update(task, advance=1)
        
        # Calculate impact based on player skills and speech option
        oratory_skill = self.player.skills.get("oratory", 1)
        base_impact = 10 + (oratory_skill * 3)
        
        # Apply special ability bonus if applicable
        speech_bonus = 0
        for ability in self.player.special_abilities:
            if ability["name"] == "Master Orator":
                speech_bonus = int(base_impact * 0.5)  # 50% bonus
                logger.info(f"Applied Master Orator ability: +{speech_bonus} impact")
                break
        
        total_impact = base_impact + speech_bonus
        
        # Calculate experience gain
        exp_gain = random.randint(1, 3) if oratory_skill < 5 else 1
        
        # Update player's skills
        skill_improved = self.player.gain_experience("oratory", exp_gain)
        
        # Record the speech for the session
        speech_record = {
            "speaker": self.player.name,
            "speaker_type": "player",
            "topic": topic,
            "stance": stance,
            "content": speech_text,
            "impact": total_impact,
            "skill_level": oratory_skill,
            "option_chosen": selected_option["title"]
        }
        
        logger.info(f"Player made speech on topic '{topic}' with impact: {total_impact}")
        
        return {
            "speech": speech_record,
            "impact": total_impact,
            "experience_gained": exp_gain,
            "skill_improved": skill_improved
        }
    
    async def make_interjection(
        self,
        speaker: str,
        speech_segment: str,
        topic: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Allow the player to interject during another senator's speech.
        
        Args:
            speaker: The name of the speaking senator
            speech_segment: The segment of speech to interject on
            topic: The current debate topic
            context: Additional context for interjection
            
        Returns:
            Dictionary with interjection result information
        """
        if context is None:
            context = {}
            
        # Get player attributes
        player_info = {
            "name": self.player.name,
            "faction": self.player.faction,
            "skills": self.player.skills,
            "oratory_skill": self.player.skills.get("oratory", 1),
            "intrigue_skill": self.player.skills.get("intrigue", 1),
            "political_capital": self.player.political_capital
        }
        
        # Generate interjection options
        interjection_options = await self._generate_interjection_options(
            speaker, 
            speech_segment, 
            topic, 
            player_info,
            context
        )
        
        # Present options to player
        selected_option_index = self.ui.display_interjection_options(
            speaker, 
            speech_segment, 
            interjection_options
        )
        
        # If player chose not to interject
        if selected_option_index < 0:
            logger.info(f"Player chose not to interject during {speaker}'s speech")
            return {
                "interjected": False,
                "speaker": speaker,
                "topic": topic
            }
        
        selected_option = interjection_options[selected_option_index]
        
        # Spend political capital
        cost = selected_option.get("cost", 1)
        if not self.player.spend_political_capital(cost):
            logger.warning(f"Not enough political capital for interjection, needed {cost}")
            return {
                "interjected": False,
                "speaker": speaker,
                "topic": topic,
                "error": "Not enough political capital"
            }
        
        # Generate full interjection based on selected option
        with self.ui.display_loading(message=f"Generating your interjection...") as progress:
            task = progress.add_task("Generating...", total=1)
            
            interjection_text = await self._generate_interjection_text(
                speaker,
                speech_segment,
                selected_option,
                player_info,
                context
            )
            
            progress.update(task, advance=1)
        
        # Calculate impact based on skills and option
        oratory_skill = self.player.skills.get("oratory", 1)
        intrigue_skill = self.player.skills.get("intrigue", 1)
        
        # Interjections use both oratory and intrigue skills
        base_impact = (oratory_skill * 2) + intrigue_skill + selected_option.get("impact_bonus", 0)
        
        # Experience gain in both skills
        oratory_exp = random.randint(0, 1)
        intrigue_exp = 1  # Interjections always improve intrigue
        
        # Update skills
        oratory_improved = self.player.gain_experience("oratory", oratory_exp) if oratory_exp > 0 else False
        intrigue_improved = self.player.gain_experience("intrigue", intrigue_exp)
        
        # Record the interjection
        interjection_record = {
            "interjector": self.player.name,
            "interjector_type": "player",
            "target_speaker": speaker,
            "topic": topic,
            "speech_segment": speech_segment,
            "content": interjection_text,
            "impact": base_impact,
            "cost": cost,
            "option_chosen": selected_option["title"]
        }
        
        logger.info(f"Player made interjection during {speaker}'s speech with impact: {base_impact}")
        
        return {
            "interjected": True,
            "interjection": interjection_record,
            "impact": base_impact,
            "experience_gained": {
                "oratory": oratory_exp,
                "intrigue": intrigue_exp
            },
            "skills_improved": {
                "oratory": oratory_improved,
                "intrigue": intrigue_improved
            }
        }
    
    def cast_vote(
        self,
        proposal: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Allow the player to vote on a proposal.
        
        Args:
            proposal: The proposal being voted on
            context: Additional context for the vote
            
        Returns:
            Dictionary with vote information
        """
        if context is None:
            context = {}
            
        # Present voting options to player
        vote = self.ui.display_vote_options(proposal, context)
        
        # Record the vote
        vote_record = {
            "voter": self.player.name,
            "voter_type": "player",
            "proposal": proposal,
            "vote": vote
        }
        
        logger.info(f"Player voted '{vote}' on proposal: {proposal}")
        
        return vote_record
    
    def perform_political_action(
        self,
        available_actions: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Allow the player to perform a political action.
        
        Args:
            available_actions: List of available actions
            context: Additional context
            
        Returns:
            Dictionary with action result
        """
        if context is None:
            context = {}
            
        # Present action options to player
        selected_index = self.ui.display_political_action_menu(available_actions)
        
        # If player cancelled
        if selected_index < 0:
            logger.info("Player cancelled political action")
            return {
                "action_performed": False
            }
            
        selected_action = available_actions[selected_index]
        
        # Check costs and requirements
        costs = selected_action.get("cost", {})
        requirements_met = True
        
        # Check wealth cost
        if "wealth" in costs and self.player.wealth < costs["wealth"]:
            requirements_met = False
            
        # Check influence cost
        if "influence" in costs and self.player.influence < costs["influence"]:
            requirements_met = False
            
        # Check political capital cost
        if "political_capital" in costs and self.player.political_capital < costs["political_capital"]:
            requirements_met = False
            
        if not requirements_met:
            logger.warning(f"Player doesn't meet requirements for action: {selected_action['name']}")
            return {
                "action_performed": False,
                "error": "Requirements not met"
            }
            
        # Pay costs
        if "wealth" in costs:
            self.player.change_wealth(-costs["wealth"])
            
        if "influence" in costs:
            self.player.change_influence(-costs["influence"])
            
        if "political_capital" in costs:
            self.player.spend_political_capital(costs["political_capital"])
            
        # Process action effects
        effects = selected_action.get("effects", {})
        
        # Apply reputation changes
        if "reputation" in effects:
            self.player.change_reputation(effects["reputation"])
            
        # Apply relationship changes
        if "relationships" in effects:
            for senator_id, change in effects["relationships"].items():
                self.player.update_relationship(senator_id, change)
                
        logger.info(f"Player performed political action: {selected_action['name']}")
        
        return {
            "action_performed": True,
            "action": selected_action["name"],
            "costs_paid": costs,
            "effects_applied": effects
        }
    
    async def _generate_speech_options(
        self,
        topic: str,
        stance: str,
        player_info: Dict[str, Any],
        context: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """
        Generate speech options for the player based on the topic.
        
        Args:
            topic: The debate topic
            stance: Player's stance on the topic
            player_info: Player information
            context: Additional context
            
        Returns:
            List of speech option dictionaries
        """
        # Create prompt for generating speech options
        prompt = f"""
        You are generating speech options for a player in a Roman Senate simulation game.
        
        TOPIC: {topic}
        PLAYER STANCE: {stance}
        PLAYER NAME: {player_info['name']}
        PLAYER FACTION: {player_info['faction']}
        PLAYER BACKGROUND: {player_info['background']}
        PLAYER ORATORY SKILL (1-10): {player_info['oratory_skill']}
        
        Generate THREE distinct speech approaches the player could take.
        Each option should be unique in its rhetorical approach and potential effect.
        
        For each option, provide:
        1. A title/name for the approach
        2. A brief description of the rhetorical strategy
        3. The expected effect on the Senate
        
        Format your response as a valid JSON array with objects containing:
        - "id": A unique identifier (1, 2, 3)
        - "title": The name of the approach
        - "description": A paragraph describing the approach
        - "effect": A brief description of the likely effect
        
        Make sure the options are historically plausible for ancient Rome and match
        the player's faction and background.
        """
        
        # Add additional context if provided
        if context:
            context_str = "\nADDITIONAL CONTEXT:\n"
            for key, value in context.items():
                context_str += f"{key.upper()}: {value}\n"
            prompt += context_str
        
        # Get speech options from LLM
        response_text = await generate_speech_text(
            prompt=prompt,
            temperature=0.7,
            max_tokens=1000
        )
        
        # Parse response as JSON
        try:
            import json
            options = json.loads(response_text)
            
            # Ensure we have the required fields
            for option in options:
                if not all(key in option for key in ["id", "title", "description", "effect"]):
                    raise ValueError("Missing required fields in speech options")
                    
            return options
            
        except Exception as e:
            logger.error(f"Error parsing speech options: {e}")
            
            # Fallback options if parsing fails
            return [
                {
                    "id": 1,
                    "title": "Principled Appeal",
                    "description": "Make a principled appeal based on Roman virtues and traditions.",
                    "effect": "Moderate impact across all factions."
                },
                {
                    "id": 2,
                    "title": "Passionate Argument",
                    "description": "Deliver an emotionally charged argument with rhetorical flourishes.",
                    "effect": "Strong impact on those who already agree with you."
                },
                {
                    "id": 3,
                    "title": "Pragmatic Approach",
                    "description": "Present a practical, measured argument focused on outcomes.",
                    "effect": "Appeals to moderates and pragmatists."
                }
            ]
    
    async def _generate_full_speech(
        self,
        topic: str,
        selected_option: Dict[str, str],
        player_info: Dict[str, Any],
        context: Dict[str, Any]
    ) -> str:
        """
        Generate the full speech text based on the selected option.
        
        Args:
            topic: The debate topic
            selected_option: The option selected by the player
            player_info: Player information
            context: Additional context
            
        Returns:
            Generated speech text
        """
        # Create prompt for generating full speech
        prompt = f"""
        You are generating a full speech for a player in a Roman Senate simulation game.
        Write a historically plausible speech that a Roman Senator would deliver.
        
        TOPIC: {topic}
        SPEECH APPROACH: {selected_option['title']}
        SPEECH STRATEGY: {selected_option['description']}
        
        PLAYER NAME: {player_info['name']}
        PLAYER FACTION: {player_info['faction']}
        PLAYER BACKGROUND: {player_info['background']}
        PLAYER ORATORY SKILL (1-10): {player_info['oratory_skill']}
        
        Create a complete speech (300-500 words) that:
        1. Opens with an appropriate Roman greeting/salutation
        2. Presents arguments relevant to the topic
        3. Uses rhetorical devices appropriate to {selected_option['title']}
        4. Includes appropriate Latin phrases and terms
        5. Concludes with a clear position and call to action
        
        Make the speech quality and sophistication match the player's oratory skill level.
        Include at least 2-3 appropriate Latin phrases (with translations in parentheses).
        Use historically accurate references to Roman values, customs, and institutions.
        """
        
        # Add additional context if provided
        if context:
            context_str = "\nADDITIONAL CONTEXT:\n"
            for key, value in context.items():
                context_str += f"{key.upper()}: {value}\n"
            prompt += context_str
        
        # Get full speech from LLM
        speech_text = await generate_speech_text(
            prompt=prompt,
            temperature=0.8,
            max_tokens=1500
        )
        
        return speech_text
    
    async def _generate_interjection_options(
        self,
        speaker: str,
        speech_segment: str,
        topic: str,
        player_info: Dict[str, Any],
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate interjection options for the player.
        
        Args:
            speaker: The senator currently speaking
            speech_segment: The segment to interject on
            topic: The debate topic
            player_info: Player information
            context: Additional context
            
        Returns:
            List of interjection option dictionaries
        """
        # Create prompt for generating interjection options
        prompt = f"""
        You are generating interjection options for a player in a Roman Senate simulation game.
        
        CURRENT SPEAKER: {speaker}
        SPEECH SEGMENT: "{speech_segment}"
        TOPIC: {topic}
        
        PLAYER NAME: {player_info['name']}
        PLAYER FACTION: {player_info['faction']}
        PLAYER ORATORY SKILL (1-10): {player_info['oratory_skill']}
        PLAYER INTRIGUE SKILL (1-10): {player_info['intrigue_skill']}
        PLAYER POLITICAL CAPITAL: {player_info['political_capital']}
        
        Generate THREE distinct interjection options the player could use.
        Each should have a different approach and potential effect.
        
        For each option, provide:
        1. A title/name for the interjection type
        2. A brief description of what the player will say/do
        3. The political capital cost (between 1-5)
        4. The expected effect
        
        Format your response as a valid JSON array with objects containing:
        - "id": A unique identifier (1, 2, 3)
        - "title": The name of the interjection type
        - "description": A paragraph describing what the player will say/do
        - "cost": Political capital cost (number)
        - "effect": A brief description of the likely effect
        - "impact_bonus": A numerical bonus to impact (0-5)
        
        Make options historically plausible for ancient Rome.
        Ensure costs are proportional to potential impact.
        """
        
        # Add additional context if provided
        if context:
            context_str = "\nADDITIONAL CONTEXT:\n"
            for key, value in context.items():
                context_str += f"{key.upper()}: {value}\n"
            prompt += context_str
        
        # Get interjection options from LLM
        response_text = await generate_speech_text(
            prompt=prompt,
            temperature=0.7,
            max_tokens=1000
        )
        
        # Parse response as JSON
        try:
            import json
            options = json.loads(response_text)
            
            # Ensure we have the required fields and costs are valid
            for option in options:
                if not all(key in option for key in ["id", "title", "description", "cost", "effect"]):
                    raise ValueError("Missing required fields in interjection options")
                
                # Ensure cost is within player's means
                option["cost"] = min(option["cost"], player_info["political_capital"])
                
                # Ensure impact_bonus exists
                if "impact_bonus" not in option:
                    option["impact_bonus"] = 0
                    
            return options
            
        except Exception as e:
            logger.error(f"Error parsing interjection options: {e}")
            
            # Fallback options if parsing fails
            return [
                {
                    "id": 1,
                    "title": "Point of Order",
                    "description": "Raise a procedural objection to the speaker's argument.",
                    "cost": 1,
                    "effect": "Temporarily disrupts their speech flow.",
                    "impact_bonus": 1
                },
                {
                    "id": 2,
                    "title": "Factual Challenge",
                    "description": "Challenge a specific factual claim in their argument.",
                    "cost": 2,
                    "effect": "Forces them to defend their position with evidence.",
                    "impact_bonus": 2
                },
                {
                    "id": 3,
                    "title": "Withering Retort",
                    "description": "Deliver a sharp, witty criticism of their entire position.",
                    "cost": 3,
                    "effect": "Significant disruption but risks creating an enemy.",
                    "impact_bonus": 3
                }
            ]
    
    async def _generate_interjection_text(
        self,
        speaker: str,
        speech_segment: str,
        selected_option: Dict[str, Any],
        player_info: Dict[str, Any],
        context: Dict[str, Any]
    ) -> str:
        """
        Generate the interjection text based on the selected option.
        
        Args:
            speaker: The senator currently speaking
            speech_segment: The segment to interject on
            selected_option: The option selected by the player
            player_info: Player information
            context: Additional context
            
        Returns:
            Generated interjection text
        """
        # Create prompt for generating interjection
        prompt = f"""
        You are generating an interjection for a player in a Roman Senate simulation game.
        Write a brief, impactful interjection that a Roman Senator would make.
        
        CURRENT SPEAKER: {speaker}
        SPEECH SEGMENT: "{speech_segment}"
        
        INTERJECTION TYPE: {selected_option['title']}
        INTERJECTION APPROACH: {selected_option['description']}
        
        PLAYER NAME: {player_info['name']}
        PLAYER FACTION: {player_info['faction']}
        PLAYER ORATORY SKILL (1-10): {player_info['oratory_skill']}
        PLAYER INTRIGUE SKILL (1-10): {player_info['intrigue_skill']}
        
        Create a brief interjection (50-100 words) that:
        1. Interrupts the speaker appropriately
        2. Clearly conveys the intent of the {selected_option['title']}
        3. Uses language appropriate to the Roman Senate
        4. Has potential to create the effect: {selected_option['effect']}
        
        Make the interjection's quality match the player's skills.
        Optionally include an appropriate Latin phrase (with translation).
        Use historically accurate references to Roman practices when relevant.
        """
        
        # Add additional context if provided
        if context:
            context_str = "\nADDITIONAL CONTEXT:\n"
            for key, value in context.items():
                context_str += f"{key.upper()}: {value}\n"
            prompt += context_str
        
        # Get interjection from LLM
        interjection_text = await generate_speech_text(
            prompt=prompt,
            temperature=0.8,
            max_tokens=300
        )
        
        return interjection_text