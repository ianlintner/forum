"""
Roman Senate AI Game - Relationship Events

This module defines events specific to senator relationships in the Roman Senate simulation.
These events are used to track and update relationships between senators.

Part of the Migration Plan: Phase 3 - Relationship System.
"""

from typing import Dict, Any, Optional, List, Set

from .base import RomanEvent

class RelationshipEvent(RomanEvent):
    """
    Base class for all relationship-related events in the Roman Senate.
    
    Relationship events track changes in relationships between senators.
    They include both direct relationship changes (like alliance formation)
    and indirect impacts (like supporting/opposing another's proposal).
    """
    
    def __init__(
        self,
        event_type: str,
        source: str,
        target: str,
        relationship_impact: float = 0.0,
        relationship_reason: Optional[str] = None,
        participants: Optional[List[str]] = None,
        **kwargs
    ):
        """
        Initialize a relationship event.
        
        Args:
            event_type: Type of the event
            source: ID of the source agent (initiator)
            target: ID of the target agent (recipient)
            relationship_impact: Change in relationship strength (-1.0 to 1.0)
            relationship_reason: Reason for the relationship change
            participants: Optional additional participants involved
            **kwargs: Additional event data
        """
        # Set up base data
        data = kwargs.get('data', {})
        data['relationship_impact'] = relationship_impact
        
        if relationship_reason:
            data['relationship_reason'] = relationship_reason
            
        if participants:
            data['participants'] = participants
            
        super().__init__(
            event_type=event_type,
            source=source,
            target=target,
            data=data,
            **kwargs
        )


class AllianceFormedEvent(RelationshipEvent):
    """Event indicating an alliance formed between two senators."""
    
    def __init__(
        self,
        source: str,
        target: str,
        alliance_type: str = "general",
        alliance_strength: float = 0.5,
        reason: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize an alliance formed event.
        
        Args:
            source: ID of the first senator
            target: ID of the second senator
            alliance_type: Type of alliance (political, family, etc.)
            alliance_strength: Strength of the alliance (0.0 to 1.0)
            reason: Reason for forming the alliance
            **kwargs: Additional event data
        """
        data = kwargs.get('data', {})
        data['alliance_type'] = alliance_type
        
        super().__init__(
            event_type='alliance_formed',
            source=source,
            target=target,
            relationship_impact=alliance_strength,
            relationship_reason=reason or f"Alliance formed: {alliance_type}",
            data=data,
            **kwargs
        )


class AllianceDissolvedEvent(RelationshipEvent):
    """Event indicating an alliance dissolved between two senators."""
    
    def __init__(
        self,
        source: str,
        target: str, 
        alliance_type: str = "general",
        impact_strength: float = -0.3,
        reason: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize an alliance dissolved event.
        
        Args:
            source: ID of the first senator
            target: ID of the second senator
            alliance_type: Type of dissolved alliance
            impact_strength: Negative impact on relationship (-1.0 to 0.0)
            reason: Reason for dissolving the alliance
            **kwargs: Additional event data
        """
        data = kwargs.get('data', {})
        data['alliance_type'] = alliance_type
        
        super().__init__(
            event_type='alliance_dissolved',
            source=source,
            target=target,
            relationship_impact=impact_strength,
            relationship_reason=reason or f"Alliance dissolved: {alliance_type}",
            data=data,
            **kwargs
        )


class RelationshipChangedEvent(RelationshipEvent):
    """Event indicating a general change in relationship between senators."""
    
    def __init__(
        self,
        source: str,
        target: str,
        impact: float,
        reason: str,
        **kwargs
    ):
        """
        Initialize a relationship changed event.
        
        Args:
            source: ID of the first senator
            target: ID of the second senator
            impact: Change in relationship strength (-1.0 to 1.0)
            reason: Reason for the relationship change
            **kwargs: Additional event data
        """
        super().__init__(
            event_type='relationship_changed',
            source=source,
            target=target,
            relationship_impact=impact,
            relationship_reason=reason,
            **kwargs
        )


class SupportProposalEvent(RelationshipEvent):
    """Event indicating a senator supported another's proposal."""
    
    def __init__(
        self,
        supporter_id: str,
        proposer_id: str,
        topic: str,
        support_strength: float = 0.2,
        **kwargs
    ):
        """
        Initialize a support proposal event.
        
        Args:
            supporter_id: ID of the supporting senator
            proposer_id: ID of the proposing senator
            topic: Topic of the proposal
            support_strength: Strength of support (0.0 to 1.0)
            **kwargs: Additional event data
        """
        data = kwargs.get('data', {})
        data['topic'] = topic
        data['support_strength'] = support_strength
        
        super().__init__(
            event_type='support_proposal',
            source=supporter_id,
            target=proposer_id,
            relationship_impact=support_strength,
            relationship_reason=f"Supported proposal on {topic}",
            data=data,
            **kwargs
        )


class OpposeProposalEvent(RelationshipEvent):
    """Event indicating a senator opposed another's proposal."""
    
    def __init__(
        self,
        opposer_id: str,
        proposer_id: str,
        topic: str,
        opposition_strength: float = -0.2,
        **kwargs
    ):
        """
        Initialize an oppose proposal event.
        
        Args:
            opposer_id: ID of the opposing senator
            proposer_id: ID of the proposing senator
            topic: Topic of the proposal
            opposition_strength: Strength of opposition (-1.0 to 0.0)
            **kwargs: Additional event data
        """
        data = kwargs.get('data', {})
        data['topic'] = topic
        data['opposition_strength'] = opposition_strength
        
        super().__init__(
            event_type='oppose_proposal',
            source=opposer_id,
            target=proposer_id,
            relationship_impact=opposition_strength,
            relationship_reason=f"Opposed proposal on {topic}",
            data=data,
            **kwargs
        )


class PersonalInteractionEvent(RelationshipEvent):
    """Event indicating a personal interaction between senators."""
    
    def __init__(
        self,
        initiator_id: str,
        recipient_id: str,
        interaction_type: str,
        impact: float,
        context: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize a personal interaction event.
        
        Args:
            initiator_id: ID of the initiating senator
            recipient_id: ID of the receiving senator
            interaction_type: Type of interaction (praise, insult, etc.)
            impact: Impact on relationship (-1.0 to 1.0)
            context: Optional context for the interaction
            **kwargs: Additional event data
        """
        data = kwargs.get('data', {})
        data['interaction_type'] = interaction_type
        
        if context:
            data['context'] = context
            
        reason = f"{interaction_type.capitalize()}"
        if context:
            reason += f" during {context}"
            
        super().__init__(
            event_type='personal_interaction',
            source=initiator_id,
            target=recipient_id,
            relationship_impact=impact,
            relationship_reason=reason,
            data=data,
            **kwargs
        )


class FactionAlignmentEvent(RelationshipEvent):
    """Event indicating senators aligning on faction interests."""
    
    def __init__(
        self,
        senator_a_id: str,
        senator_b_id: str,
        faction: str,
        alignment_type: str,
        impact: float,
        **kwargs
    ):
        """
        Initialize a faction alignment event.
        
        Args:
            senator_a_id: ID of the first senator
            senator_b_id: ID of the second senator
            faction: Name of the faction
            alignment_type: Type of alignment (mutual, opposing)
            impact: Impact on relationship (-1.0 to 1.0)
            **kwargs: Additional event data
        """
        data = kwargs.get('data', {})
        data['faction'] = faction
        data['alignment_type'] = alignment_type
        
        reason = f"Faction alignment: {alignment_type} on {faction} interests"
        
        super().__init__(
            event_type='faction_alignment',
            source=senator_a_id,
            target=senator_b_id,
            relationship_impact=impact,
            relationship_reason=reason,
            data=data,
            **kwargs
        )