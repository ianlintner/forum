#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Roman Senate AI Game
Speech Evaluation Module

This module provides functionality for evaluating the effectiveness of speeches
based on rhetorical techniques, historical authenticity, and persuasiveness.
"""

import re
import random
from typing import Dict, List, Optional, Any, Tuple

from .rhetorical_devices import RHETORICAL_DEVICES
from .latin_flourishes import score_latin_usage

class SpeechEvaluator:
    """
    Evaluates speeches based on multiple criteria including rhetorical effectiveness,
    historical authenticity, and persuasiveness based on the audience.
    """
    
    def __init__(self):
        """Initialize the speech evaluator with default weights."""
        # Default category weights
        self.category_weights = {
            "rhetorical_devices": 0.25,
            "structure": 0.20,
            "latin_usage": 0.15,
            "historical_authenticity": 0.15,
            "audience_appeal": 0.15,
            "topic_relevance": 0.10
        }
    
    def evaluate_speech(self, speech_text: str, speech_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate a speech based on its text content and metadata.
        
        Args:
            speech_text: The full text of the speech
            speech_data: Dictionary with speech metadata including archetype, devices used,
                        historical references, etc.
        
        Returns:
            Dictionary with evaluation scores and detailed breakdown
        """
        # Individual scores
        rhetoric_score = self._evaluate_rhetorical_devices(speech_text, speech_data)
        structure_score = self._evaluate_structure(speech_text, speech_data)
        latin_score = self._evaluate_latin_usage(speech_text, speech_data)
        historical_score = self._evaluate_historical_authenticity(speech_text, speech_data)
        audience_score = self._evaluate_audience_appeal(speech_text, speech_data)
        relevance_score = self._evaluate_topic_relevance(speech_text, speech_data)
        
        # Calculate weighted total
        total_score = (
            rhetoric_score * self.category_weights["rhetorical_devices"] +
            structure_score * self.category_weights["structure"] +
            latin_score * self.category_weights["latin_usage"] +
            historical_score * self.category_weights["historical_authenticity"] +
            audience_score * self.category_weights["audience_appeal"] +
            relevance_score * self.category_weights["topic_relevance"]
        )
        
        # Scale to 0-100 for easier interpretation
        scaled_score = int(total_score * 100)
        
        # Create evaluation result
        evaluation = {
            "overall_score": scaled_score,
            "scores": {
                "rhetorical_devices": round(rhetoric_score, 2),
                "structure": round(structure_score, 2),
                "latin_usage": round(latin_score, 2),
                "historical_authenticity": round(historical_score, 2),
                "audience_appeal": round(audience_score, 2),
                "topic_relevance": round(relevance_score, 2)
            },
            "detailed_feedback": self._generate_detailed_feedback(speech_data, {
                "rhetorical_devices": rhetoric_score,
                "structure": structure_score,
                "latin_usage": latin_score,
                "historical_authenticity": historical_score,
                "audience_appeal": audience_score,
                "topic_relevance": relevance_score
            }),
            "ranking": self._get_ranking(scaled_score)
        }
        
        return evaluation
    
    def _evaluate_rhetorical_devices(self, speech_text: str, speech_data: Dict[str, Any]) -> float:
        """Evaluate the effective use of rhetorical devices."""
        # Check for devices used (from speech metadata)
        used_devices = speech_data.get("selected_devices", [])
        num_devices = len(used_devices)
        
        # Text analysis for device detection
        detected_devices = []
        device_score = 0.0
        
        # Simplified detection of some common devices
        # In a full implementation, this would use more sophisticated NLP techniques
        if re.search(r'(\b\w+\b)(?:\s+\w+){1,5}\s+\1\b', speech_text):
            detected_devices.append("anaphora")
        
        if "?" in speech_text and not speech_text.endswith("?"):
            detected_devices.append("rhetorical_question")
        
        # Pattern for tricolon (series of three)
        if re.search(r'[\w\s]+,\s+[\w\s]+,\s+(and|et)\s+[\w\s]+', speech_text):
            detected_devices.append("tricolon")
        
        # Check for antithesis (not X but Y)
        if re.search(r'\bnot\b.*\bbut\b', speech_text, re.IGNORECASE):
            detected_devices.append("antithesis")
        
        # Score based on both declared and detected devices
        all_devices = list(set(used_devices + detected_devices))
        
        # A good speech has 3-5 devices
        optimal_device_count = 4
        device_count_score = 1.0 - min(1.0, abs(len(all_devices) - optimal_device_count) / optimal_device_count)
        
        # Check for variety
        variety_score = min(1.0, len(all_devices) / 3)
        
        # Combine scores
        device_score = (device_count_score * 0.6) + (variety_score * 0.4)
        return min(1.0, device_score)
    
    def _evaluate_structure(self, speech_text: str, speech_data: Dict[str, Any]) -> float:
        """Evaluate the classical structure of the speech."""
        # Look for evidence of classical parts
        structure_score = 0.0
        
        # Check if speech has defined structure parts
        structure_parts = speech_data.get("structure", {})
        
        if structure_parts:
            # If structure data is available, score based on completeness
            required_parts = ["exordium", "narratio", "confirmatio", "peroratio"]
            optional_parts = ["partitio", "refutatio"]
            
            # Score required parts (70% of structure score)
            required_score = sum(1 for part in required_parts if part in structure_parts) / len(required_parts)
            
            # Score optional parts (30% of structure score)
            optional_score = sum(1 for part in optional_parts if part in structure_parts) / len(optional_parts)
            
            structure_score = (required_score * 0.7) + (optional_score * 0.3)
        else:
            # Text-based heuristic evaluation
            # In a real implementation, this would use more advanced NLP
            
            # Check for introduction (greeting or opening statement)
            has_intro = bool(re.match(r'^[^.!?]+[.!?]', speech_text))
            
            # Check for conclusion (final statement)
            has_conclusion = bool(re.search(r'[.!?][^.!?]+[.!?]$', speech_text))
            
            # Check for logical flow (transitional phrases)
            has_transitions = any(phrase in speech_text.lower() for phrase in 
                                ["therefore", "thus", "consequently", "however", "moreover"])
            
            # Simple structure score based on these elements
            structure_elements = [has_intro, has_conclusion, has_transitions]
            structure_score = sum(1 for element in structure_elements if element) / len(structure_elements)
        
        return structure_score
    
    def _evaluate_latin_usage(self, speech_text: str, speech_data: Dict[str, Any]) -> float:
        """Evaluate the appropriate use of Latin terms and phrases."""
        # Get Latin usage score from the latin_flourishes module
        latin_scores = score_latin_usage(speech_text)
        return latin_scores.get("authenticity_score", 0.5)
    
    def _evaluate_historical_authenticity(self, speech_text: str, speech_data: Dict[str, Any]) -> float:
        """Evaluate historical authenticity based on references and context."""
        # Check for historical references
        historical_references = speech_data.get("historical_references", [])
        
        # If no explicit references provided, try to detect them
        if not historical_references:
            # Look for historical names, events, etc.
            from .historical_context import HISTORICAL_FIGURES, HISTORICAL_EVENTS
            
            year = speech_data.get("year", -100)
            
            # Find appropriate time period for checking references
            figure_period = None
            for period in HISTORICAL_FIGURES:
                if period[0] <= year <= period[1]:
                    figure_period = period
                    break
            
            event_period = None
            for period in HISTORICAL_EVENTS:
                if period[0] <= year <= period[1]:
                    event_period = period
                    break
            
            # Check for anachronistic references (figures/events from future periods)
            anachronism_penalty = 0.0
            
            if figure_period:
                for other_period in HISTORICAL_FIGURES:
                    if other_period[0] > year:  # Future period
                        future_figures = HISTORICAL_FIGURES[other_period]
                        for figure in future_figures:
                            if figure["name"] in speech_text:
                                anachronism_penalty += 0.2  # Penalty for each anachronistic reference
            
            if event_period:
                for other_period in HISTORICAL_EVENTS:
                    if other_period[0] > year:  # Future period
                        future_events = HISTORICAL_EVENTS[other_period]
                        for event in future_events:
                            if event["name"] in speech_text:
                                anachronism_penalty += 0.2  # Penalty for each anachronistic reference
            
            # Check for appropriate references
            reference_score = 0.0
            
            # Look for historical figures from appropriate period
            if figure_period and HISTORICAL_FIGURES.get(figure_period):
                for figure in HISTORICAL_FIGURES[figure_period]:
                    if figure["name"] in speech_text:
                        reference_score += 0.25
            
            # Look for historical events from appropriate period
            if event_period and HISTORICAL_EVENTS.get(event_period):
                for event in HISTORICAL_EVENTS[event_period]:
                    if event["name"] in speech_text:
                        reference_score += 0.25
            
            # Cap scores
            reference_score = min(1.0, reference_score)
            anachronism_penalty = min(1.0, anachronism_penalty)
            
            historical_authenticity_score = max(0.0, reference_score - anachronism_penalty)
        else:
            # If references explicitly provided, score based on their count
            optimal_reference_count = 3
            historical_authenticity_score = 1.0 - min(1.0, abs(len(historical_references) - optimal_reference_count) / optimal_reference_count)
        
        return historical_authenticity_score
    
    def _evaluate_audience_appeal(self, speech_text: str, speech_data: Dict[str, Any]) -> float:
        """Evaluate how well the speech appeals to its intended audience."""
        # Get audience data
        faction = speech_data.get("faction", "")
        archetype = speech_data.get("archetype", {}).get("primary", "")
        
        # Default score
        audience_score = 0.5  # Neutral score
        
        # Check for appeal to specific factions
        if faction == "Optimates" and archetype in ["traditionalist", "philosopher"]:
            # Good match - traditionalist approach for conservative faction
            audience_score += 0.3
        elif faction == "Populares" and archetype in ["populist", "pragmatist"]:
            # Good match - populist approach for reform faction
            audience_score += 0.3
        elif faction == "Military" and archetype in ["militarist"]:
            # Good match
            audience_score += 0.3
        
        # Check emotional vs. logical appeals based on faction
        emotional_terms = ["heart", "feel", "suffer", "pain", "glory", "honor", "courage"]
        logical_terms = ["reason", "logic", "evidence", "proof", "therefore", "consequently"]
        
        emotional_count = sum(1 for term in emotional_terms if term in speech_text.lower())
        logical_count = sum(1 for term in logical_terms if term in speech_text.lower())
        
        # Adjust score based on appeals matching faction preferences
        if faction == "Optimates" and logical_count > emotional_count:
            audience_score += 0.1
        elif faction == "Populares" and emotional_count > logical_count:
            audience_score += 0.1
        
        return min(1.0, audience_score)
    
    def _evaluate_topic_relevance(self, speech_text: str, speech_data: Dict[str, Any]) -> float:
        """Evaluate how well the speech addresses the relevant topic."""
        # Extract topic
        topic = speech_data.get("topic", "")
        
        if not topic:
            return 0.5  # Neutral score if no topic provided
        
        # Check for topic keywords in speech
        topic_words = re.findall(r'\b\w+\b', topic.lower())
        topic_words = [word for word in topic_words if len(word) > 3]  # Filter out short words
        
        if not topic_words:
            return 0.5  # Neutral score if no significant topic words
        
        # Count occurrences of topic words
        speech_lower = speech_text.lower()
        topic_word_count = sum(1 for word in topic_words if word in speech_lower)
        
        # Score based on coverage of topic words
        topic_score = min(1.0, topic_word_count / (len(topic_words) + 1))
        
        # Check for direct mentions of the topic
        if topic.lower() in speech_lower:
            topic_score += 0.2
            
        return min(1.0, topic_score)
    
    def _generate_detailed_feedback(self, speech_data: Dict[str, Any], 
                                    scores: Dict[str, float]) -> List[str]:
        """Generate detailed feedback based on evaluation scores."""
        feedback = []
        
        # Rhetorical devices feedback
        rhetoric_score = scores["rhetorical_devices"]
        if rhetoric_score > 0.8:
            feedback.append("Excellent use of rhetorical devices adds persuasive power.")
        elif rhetoric_score > 0.6:
            feedback.append("Good use of rhetorical devices enhances the speech.")
        elif rhetoric_score > 0.4:
            feedback.append("Some rhetorical techniques used, but could be more varied.")
        else:
            feedback.append("Limited use of rhetorical devices reduces persuasiveness.")
        
        # Structure feedback
        structure_score = scores["structure"]
        if structure_score > 0.8:
            feedback.append("Well-structured speech following classical arrangement.")
        elif structure_score > 0.6:
            feedback.append("Good structure with clear beginning, middle, and end.")
        elif structure_score > 0.4:
            feedback.append("Adequate structure, but some classical elements are missing.")
        else:
            feedback.append("Disorganized speech lacking clear classical structure.")
        
        # Latin usage feedback
        latin_score = scores["latin_usage"]
        if latin_score > 0.8:
            feedback.append("Impressive and appropriate use of Latin phrases and terms.")
        elif latin_score > 0.6:
            feedback.append("Good integration of Latin elements adds authenticity.")
        elif latin_score > 0.4:
            feedback.append("Some Latin usage, but could be more integrated.")
        else:
            feedback.append("Limited Latin usage reduces the speech's Roman character.")
        
        # Historical authenticity feedback
        historical_score = scores["historical_authenticity"]
        if historical_score > 0.8:
            feedback.append("Excellent use of historical references adds credibility.")
        elif historical_score > 0.6:
            feedback.append("Good historical references strengthen arguments.")
        elif historical_score > 0.4:
            feedback.append("Some historical context, but could be more specific.")
        else:
            feedback.append("Lack of historical context weakens the speech's impact.")
        
        # Audience appeal feedback
        audience_score = scores["audience_appeal"]
        if audience_score > 0.8:
            feedback.append("Exceptionally well-tailored to the audience's preferences.")
        elif audience_score > 0.6:
            feedback.append("Arguments align well with audience expectations.")
        elif audience_score > 0.4:
            feedback.append("Some appeal to audience, but could be more targeted.")
        else:
            feedback.append("Speech fails to connect with its intended audience.")
        
        # Topic relevance feedback
        relevance_score = scores["topic_relevance"]
        if relevance_score > 0.8:
            feedback.append("Addresses the topic with clear focus and relevance.")
        elif relevance_score > 0.6:
            feedback.append("Stays on topic with minor digressions.")
        elif relevance_score > 0.4:
            feedback.append("Somewhat related to the topic, but loses focus.")
        else:
            feedback.append("Strays significantly from the central topic.")
        
        return feedback
    
    def _get_ranking(self, scaled_score: int) -> str:
        """Get a qualitative ranking based on the overall score."""
        if scaled_score >= 90:
            return "Ciceronian Excellence"
        elif scaled_score >= 80:
            return "Senatorial Mastery"
        elif scaled_score >= 70:
            return "Patrician Standard"
        elif scaled_score >= 60:
            return "Equestrian Quality" 
        elif scaled_score >= 50:
            return "Plebeian Effort"
        elif scaled_score >= 40:
            return "Provincial Attempt"
        else:
            return "Barbarian Rambling"

def evaluate_speech(speech_text: str, speech_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluate a speech and return a detailed assessment.
    
    Args:
        speech_text: The text of the speech
        speech_data: Dictionary with speech metadata
        
    Returns:
        Dictionary with evaluation scores and feedback
    """
    evaluator = SpeechEvaluator()
    return evaluator.evaluate_speech(speech_text, speech_data)

def calculate_audience_reaction(evaluation: Dict[str, Any], 
                              audience_composition: Dict[str, float]) -> Dict[str, Any]:
    """
    Calculate audience reaction based on speech evaluation and audience composition.
    
    Args:
        evaluation: Speech evaluation from evaluate_speech()
        audience_composition: Dictionary mapping factions to their proportion in audience
        
    Returns:
        Dictionary with reaction data including applause level, vocal reactions, etc.
    """
    overall_score = evaluation["overall_score"] / 100.0  # Convert to 0-1 scale
    
    # Base reaction on overall score
    base_reaction = {
        "applause": overall_score * 0.8,  # 0-0.8 scale
        "vocal_support": overall_score * 0.7,  # 0-0.7 scale
        "opposition": (1 - overall_score) * 0.6  # More for worse speeches
    }
    
    # Adjust based on audience composition and specific scores
    reaction = base_reaction.copy()
    
    # If audience composition data is available, adjust reactions
    if audience_composition:
        optimates_ratio = audience_composition.get("Optimates", 0.33)
        populares_ratio = audience_composition.get("Populares", 0.33)
        military_ratio = audience_composition.get("Military", 0.20)
        other_ratio = audience_composition.get("Other", 0.14)
        
        # Get audience appeal score
        audience_appeal = evaluation["scores"]["audience_appeal"]
        
        # Adjust reactions based on appeal and audience composition
        faction_appeal_modifier = 0.0
        
        # Specific faction modifiers based on detailed scores
        if "archetype" in evaluation:
            archetype = evaluation.get("archetype", {}).get("primary", "")
            
            if archetype == "traditionalist":
                faction_appeal_modifier += optimates_ratio * 0.2
                faction_appeal_modifier -= populares_ratio * 0.1
            elif archetype == "populist": 
                faction_appeal_modifier += populares_ratio * 0.2
                faction_appeal_modifier -= optimates_ratio * 0.1
            elif archetype == "militarist":
                faction_appeal_modifier += military_ratio * 0.3
        
        # Apply modifier
        reaction["applause"] = min(1.0, reaction["applause"] + faction_appeal_modifier)
        reaction["vocal_support"] = min(1.0, reaction["vocal_support"] + faction_appeal_modifier)
        reaction["opposition"] = max(0.0, reaction["opposition"] - faction_appeal_modifier)
    
    # Generate descriptive reaction text
    if reaction["applause"] > 0.7:
        reaction_text = "Thunderous applause erupts from the chamber."
    elif reaction["applause"] > 0.5:
        reaction_text = "Solid applause follows the speech."
    elif reaction["applause"] > 0.3:
        reaction_text = "Polite applause from some senators."
    else:
        reaction_text = "Minimal applause; the speech falls flat."
    
    # Add vocal reactions if significant
    if reaction["vocal_support"] > 0.6:
        reaction_text += " Many senators call out in support."
    
    if reaction["opposition"] > 0.6:
        reaction_text += " Vocal opposition and heckling from opponents."
    elif reaction["opposition"] > 0.4:
        reaction_text += " Some grumbling from unconvinced senators."
    
    reaction["description"] = reaction_text
    
    return reaction