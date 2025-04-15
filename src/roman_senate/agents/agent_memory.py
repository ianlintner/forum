"""
Roman Senate AI Game
Agent Memory Module

This module defines the memory structure for senate agents.
"""

class AgentMemory:
    """Represents the memory of a senator agent, storing past interactions and experiences."""
    
    def __init__(self):
        """Initialize an empty agent memory."""
        self.observations = []
        self.interactions = {}
        self.voting_history = {}
        self.debate_history = []
        self.relationship_scores = {}
    
    def add_observation(self, observation):
        """Add a new observation to the agent's memory."""
        self.observations.append(observation)
    
    def add_interaction(self, senator_name, interaction_type, details):
        """Record an interaction with another senator."""
        if senator_name not in self.interactions:
            self.interactions[senator_name] = []
        
        self.interactions[senator_name].append({
            "type": interaction_type,
            "details": details
        })
    
    def record_vote(self, topic, position):
        """Record how the agent voted on a particular topic."""
        self.voting_history[topic] = position
    
    def record_debate_contribution(self, topic, stance, speech):
        """Record the agent's contribution to a debate."""
        self.debate_history.append({
            "topic": topic,
            "stance": stance,
            "speech": speech
        })
    
    def update_relationship(self, senator_name, score_change):
        """Update relationship score with another senator."""
        if senator_name not in self.relationship_scores:
            self.relationship_scores[senator_name] = 0
        
        self.relationship_scores[senator_name] += score_change