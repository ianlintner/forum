"""
Roman Senate Relationships for Agentic Game Framework.

This module implements relationship types specific to the Roman Senate domain.
"""

import logging
from typing import Any, Dict, Optional

from src.agentic_game_framework.relationships.base_relationship import BaseRelationship

logger = logging.getLogger(__name__)


class SenateRelationship(BaseRelationship):
    """Base class for all Senate-specific relationships."""
    
    def __init__(
        self,
        source_id: str,
        target_id: str,
        value: float = 0.0,
        relationship_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a Senate relationship.
        
        Args:
            source_id: ID of the source agent
            target_id: ID of the target agent
            value: Relationship value (-1.0 to 1.0)
            relationship_id: Optional unique identifier
            metadata: Additional metadata
        """
        super().__init__(
            source_id=source_id,
            target_id=target_id,
            value=value,
            relationship_id=relationship_id,
            metadata=metadata or {}
        )
    
    def update_from_event(self, event_type: str, event_data: Dict[str, Any]) -> float:
        """
        Update relationship based on an event.
        
        Args:
            event_type: Type of event
            event_data: Event data
            
        Returns:
            float: Change in relationship value
        """
        # Base implementation does nothing
        return 0.0
    
    def get_description(self) -> str:
        """
        Get a human-readable description of this relationship.
        
        Returns:
            str: Relationship description
        """
        # Base implementation just gives a generic description
        if self.value > 0.7:
            strength = "very strong"
        elif self.value > 0.3:
            strength = "strong"
        elif self.value > 0.0:
            strength = "positive"
        elif self.value > -0.3:
            strength = "negative"
        elif self.value > -0.7:
            strength = "poor"
        else:
            strength = "very poor"
            
        return f"{strength} relationship"


class PoliticalRelationship(SenateRelationship):
    """Political relationship between senators."""
    
    RELATIONSHIP_TYPE = "political"
    
    def __init__(
        self,
        source_id: str,
        target_id: str,
        value: float = 0.0,
        relationship_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a political relationship.
        
        Args:
            source_id: ID of the source senator
            target_id: ID of the target senator
            value: Relationship value (-1.0 to 1.0)
            relationship_id: Optional unique identifier
            metadata: Additional metadata
        """
        super().__init__(
            source_id=source_id,
            target_id=target_id,
            value=value,
            relationship_id=relationship_id,
            metadata=metadata or {}
        )
        
        # Set relationship type
        self.metadata["relationship_type"] = self.RELATIONSHIP_TYPE
        
        # Political-specific metadata
        if "votes_aligned" not in self.metadata:
            self.metadata["votes_aligned"] = 0
        
        if "votes_opposed" not in self.metadata:
            self.metadata["votes_opposed"] = 0
    
    def update_from_event(self, event_type: str, event_data: Dict[str, Any]) -> float:
        """
        Update political relationship based on an event.
        
        Args:
            event_type: Type of event
            event_data: Event data
            
        Returns:
            float: Change in relationship value
        """
        change = 0.0
        
        if event_type == "senate.speech":
            # Speeches can affect political relationships
            if "stance" in event_data and "topic" in event_data:
                # Record the stance for later comparison
                self.metadata[f"stance_{event_data['topic']}"] = event_data["stance"]
                
                # If we already know the other senator's stance, compare them
                other_stance_key = f"other_stance_{event_data['topic']}"
                if other_stance_key in self.metadata:
                    other_stance = self.metadata[other_stance_key]
                    if event_data["stance"] == other_stance:
                        change = 0.05  # Small positive change for alignment
                    else:
                        change = -0.05  # Small negative change for disagreement
        
        elif event_type == "senate.vote":
            # Voting has a stronger effect on political relationships
            if "vote" in event_data and "other_vote" in event_data:
                if event_data["vote"] == event_data["other_vote"]:
                    change = 0.1  # Positive change for voting together
                    self.metadata["votes_aligned"] += 1
                else:
                    change = -0.1  # Negative change for voting against each other
                    self.metadata["votes_opposed"] += 1
        
        # Apply the change
        old_value = self.value
        self.value = max(-1.0, min(1.0, self.value + change))
        
        return self.value - old_value
    
    def get_description(self) -> str:
        """
        Get a human-readable description of this political relationship.
        
        Returns:
            str: Relationship description
        """
        if self.value > 0.7:
            return "strong political allies"
        elif self.value > 0.3:
            return "political allies"
        elif self.value > 0.0:
            return "politically aligned"
        elif self.value > -0.3:
            return "politically opposed"
        elif self.value > -0.7:
            return "political rivals"
        else:
            return "bitter political enemies"


class FactionRelationship(SenateRelationship):
    """Faction-based relationship between senators."""
    
    RELATIONSHIP_TYPE = "faction"
    
    def __init__(
        self,
        source_id: str,
        target_id: str,
        value: float = 0.0,
        relationship_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        source_faction: Optional[str] = None,
        target_faction: Optional[str] = None
    ):
        """
        Initialize a faction relationship.
        
        Args:
            source_id: ID of the source senator
            target_id: ID of the target senator
            value: Relationship value (-1.0 to 1.0)
            relationship_id: Optional unique identifier
            metadata: Additional metadata
            source_faction: Faction of the source senator
            target_faction: Faction of the target senator
        """
        super().__init__(
            source_id=source_id,
            target_id=target_id,
            value=value,
            relationship_id=relationship_id,
            metadata=metadata or {}
        )
        
        # Set relationship type
        self.metadata["relationship_type"] = self.RELATIONSHIP_TYPE
        
        # Faction-specific metadata
        self.metadata["source_faction"] = source_faction
        self.metadata["target_faction"] = target_faction
        
        # Initialize the relationship value based on factions if provided
        if source_faction and target_faction:
            self.initialize_from_factions(source_faction, target_faction)
    
    def initialize_from_factions(self, source_faction: str, target_faction: str) -> None:
        """
        Initialize relationship value based on factions.
        
        Args:
            source_faction: Faction of the source senator
            target_faction: Faction of the target senator
        """
        # Same faction means positive relationship
        if source_faction == target_faction:
            self.value = 0.5
            return
        
        # Different factions have different relationships
        faction_relations = {
            ("Optimates", "Populares"): -0.5,  # Traditional rivals
            ("Populares", "Optimates"): -0.5,
            ("Optimates", "Neutral"): 0.0,     # Neutral with neutrals
            ("Neutral", "Optimates"): 0.0,
            ("Populares", "Neutral"): 0.0,     # Neutral with neutrals
            ("Neutral", "Populares"): 0.0,
        }
        
        # Set value based on faction pairing
        key = (source_faction, target_faction)
        self.value = faction_relations.get(key, 0.0)
    
    def update_from_event(self, event_type: str, event_data: Dict[str, Any]) -> float:
        """
        Update faction relationship based on an event.
        
        Args:
            event_type: Type of event
            event_data: Event data
            
        Returns:
            float: Change in relationship value
        """
        change = 0.0
        
        if event_type == "senate.speech":
            # Speeches about faction-related topics have more impact
            if "topic" in event_data and "stance" in event_data:
                topic = event_data["topic"].lower()
                # Check if the topic is related to factions
                faction_keywords = ["faction", "party", "optimates", "populares", "reform", "tradition"]
                is_faction_topic = any(keyword in topic for keyword in faction_keywords)
                
                if is_faction_topic:
                    # Get the factions
                    source_faction = self.metadata.get("source_faction")
                    target_faction = self.metadata.get("target_faction")
                    
                    if source_faction and target_faction:
                        if source_faction == target_faction:
                            # Same faction, positive change
                            change = 0.05
                        else:
                            # Different factions, negative change
                            change = -0.05
        
        # Apply the change
        old_value = self.value
        self.value = max(-1.0, min(1.0, self.value + change))
        
        return self.value - old_value
    
    def get_description(self) -> str:
        """
        Get a human-readable description of this faction relationship.
        
        Returns:
            str: Relationship description
        """
        source_faction = self.metadata.get("source_faction", "unknown")
        target_faction = self.metadata.get("target_faction", "unknown")
        
        if source_faction == target_faction:
            if self.value > 0.7:
                return f"loyal faction members ({source_faction})"
            elif self.value > 0.3:
                return f"faction allies ({source_faction})"
            else:
                return f"faction colleagues ({source_faction})"
        else:
            if self.value > 0.3:
                return f"cross-faction allies ({source_faction} and {target_faction})"
            elif self.value > -0.3:
                return f"cross-faction acquaintances ({source_faction} and {target_faction})"
            elif self.value > -0.7:
                return f"faction rivals ({source_faction} vs {target_faction})"
            else:
                return f"faction enemies ({source_faction} vs {target_faction})"


class PersonalRelationship(SenateRelationship):
    """Personal relationship between senators."""
    
    RELATIONSHIP_TYPE = "personal"
    
    def __init__(
        self,
        source_id: str,
        target_id: str,
        value: float = 0.0,
        relationship_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a personal relationship.
        
        Args:
            source_id: ID of the source senator
            target_id: ID of the target senator
            value: Relationship value (-1.0 to 1.0)
            relationship_id: Optional unique identifier
            metadata: Additional metadata
        """
        super().__init__(
            source_id=source_id,
            target_id=target_id,
            value=value,
            relationship_id=relationship_id,
            metadata=metadata or {}
        )
        
        # Set relationship type
        self.metadata["relationship_type"] = self.RELATIONSHIP_TYPE
        
        # Personal-specific metadata
        if "interactions" not in self.metadata:
            self.metadata["interactions"] = 0
        
        if "positive_interactions" not in self.metadata:
            self.metadata["positive_interactions"] = 0
        
        if "negative_interactions" not in self.metadata:
            self.metadata["negative_interactions"] = 0
    
    def update_from_event(self, event_type: str, event_data: Dict[str, Any]) -> float:
        """
        Update personal relationship based on an event.
        
        Args:
            event_type: Type of event
            event_data: Event data
            
        Returns:
            float: Change in relationship value
        """
        change = 0.0
        
        # Track interaction
        self.metadata["interactions"] += 1
        
        if event_type == "senate.reaction":
            # Reactions can affect personal relationships
            if "reaction_type" in event_data:
                reaction_type = event_data["reaction_type"]
                
                if reaction_type in ["approval", "agreement"]:
                    change = 0.1
                    self.metadata["positive_interactions"] += 1
                elif reaction_type in ["disapproval", "disagreement"]:
                    change = -0.1
                    self.metadata["negative_interactions"] += 1
        
        elif event_type == "senate.interjection":
            # Interjections can affect personal relationships
            if "interjection_type" in event_data:
                interjection_type = event_data["interjection_type"]
                
                if interjection_type in ["support", "clarification"]:
                    change = 0.05
                    self.metadata["positive_interactions"] += 1
                elif interjection_type in ["opposition", "procedural"]:
                    change = -0.05
                    self.metadata["negative_interactions"] += 1
        
        elif event_type == "senate.relationship":
            # Direct relationship events
            if "change_value" in event_data and event_data.get("relationship_type") == "personal":
                change = event_data["change_value"]
                
                if change > 0:
                    self.metadata["positive_interactions"] += 1
                elif change < 0:
                    self.metadata["negative_interactions"] += 1
        
        # Apply the change
        old_value = self.value
        self.value = max(-1.0, min(1.0, self.value + change))
        
        return self.value - old_value
    
    def get_description(self) -> str:
        """
        Get a human-readable description of this personal relationship.
        
        Returns:
            str: Relationship description
        """
        if self.value > 0.7:
            return "close friends"
        elif self.value > 0.3:
            return "friends"
        elif self.value > 0.0:
            return "friendly acquaintances"
        elif self.value > -0.3:
            return "distant acquaintances"
        elif self.value > -0.7:
            return "personal rivals"
        else:
            return "personal enemies"