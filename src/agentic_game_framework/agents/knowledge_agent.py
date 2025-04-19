"""
Knowledge-Augmented Agent for Agentic Game Framework.

This module extends the base agent with knowledge retrieval and
context augmentation capabilities using RAG (Retrieval-Augmented Generation).
"""

from typing import Any, Dict, List, Optional, Tuple

from ..events.base import BaseEvent
from ..knowledge.rag_client import RAGClient
from ..knowledge.vector_store import VectorStoreConfig
from .base_agent import BaseAgent


class KnowledgeAgent(BaseAgent):
    """
    Agent with knowledge retrieval and context augmentation capabilities.
    
    This agent extends the base agent with RAG capabilities, allowing it to
    retrieve relevant knowledge and incorporate it into its decision-making.
    
    Attributes:
        rag_client: Client for retrieval-augmented generation
        context_window_size: Maximum size of the context window
    """
    
    def __init__(
        self,
        name: str,
        attributes: Optional[Dict[str, Any]] = None,
        agent_id: Optional[str] = None,
        initial_state: Optional[Dict[str, Any]] = None,
        rag_client: Optional[RAGClient] = None,
        vector_store_config: Optional[VectorStoreConfig] = None,
        context_window_size: int = 4000
    ):
        """Initialize a new knowledge agent.
        
        Args:
            name: Human-readable name for the agent
            attributes: Agent-specific attributes
            agent_id: Unique identifier (generated if not provided)
            initial_state: Initial internal state
            rag_client: Client for retrieval-augmented generation
            vector_store_config: Configuration for the vector store
            context_window_size: Maximum size of the context window
        """
        super().__init__(name, attributes, agent_id, initial_state)
        
        # Initialize RAG client
        self.rag_client = rag_client or RAGClient(config=vector_store_config)
        self.context_window_size = context_window_size
        
        # Add knowledge-related state
        self.state.setdefault("knowledge_context", {})
        self.state.setdefault("last_queries", [])
    
    def add_knowledge(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Add knowledge to the agent's knowledge base.
        
        Args:
            content: The knowledge content
            metadata: Additional metadata about the knowledge
            
        Returns:
            str: The ID of the added knowledge
        """
        return self.rag_client.add_knowledge(content, metadata)
    
    def retrieve_knowledge(
        self,
        query: str,
        limit: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[str, float]]:
        """Retrieve relevant knowledge based on a query.
        
        Args:
            query: The search query
            limit: Maximum number of results
            filter_metadata: Filter results by metadata
            
        Returns:
            List[Tuple[str, float]]: List of (content, relevance) tuples
        """
        # Track queries for context management
        self._add_query_to_history(query)
        
        return self.rag_client.search(query, limit, filter_metadata)
    
    def augment_context(
        self,
        context: str,
        query: Optional[str] = None,
        limit: int = 3
    ) -> str:
        """Augment a context with relevant knowledge.
        
        Args:
            context: The original context to augment
            query: The query to search for relevant knowledge (generated from context if None)
            limit: Maximum number of knowledge items to include
            
        Returns:
            str: The augmented context
        """
        # Generate query from context if not provided
        if query is None:
            query = self.rag_client.generate_query_from_context(context)
        
        # Track queries for context management
        self._add_query_to_history(query)
        
        # Augment context
        augmented_context = self.rag_client.augment_context(
            query=query,
            context=context,
            limit=limit
        )
        
        # Manage context window size
        if len(augmented_context) > self.context_window_size:
            augmented_context = self._manage_context_window(augmented_context)
        
        return augmented_context
    
    def process_event_with_knowledge(self, event: BaseEvent) -> None:
        """Process an event with knowledge augmentation.
        
        This method augments the event with relevant knowledge before processing.
        
        Args:
            event: The event to process
        """
        # Convert event to string representation for querying
        event_str = str(event.to_dict())
        
        # Augment with relevant knowledge
        augmented_event_str = self.augment_context(event_str)
        
        # Store in state for use in decision-making
        self.state["knowledge_context"]["last_event"] = augmented_event_str
        
        # Process the event normally
        self.process_event(event)
    
    def _add_query_to_history(self, query: str) -> None:
        """Add a query to the history.
        
        Args:
            query: The query to add
        """
        # Add to history
        self.state["last_queries"].append(query)
        
        # Keep only the last 10 queries
        if len(self.state["last_queries"]) > 10:
            self.state["last_queries"] = self.state["last_queries"][-10:]
    
    def _manage_context_window(self, context: str) -> str:
        """Manage the context window size.
        
        Args:
            context: The context to manage
            
        Returns:
            str: The managed context
        """
        # Simple truncation strategy
        if len(context) > self.context_window_size:
            # Keep the beginning and end, truncate the middle
            half_size = self.context_window_size // 2
            return context[:half_size] + "\n...[content truncated]...\n" + context[-half_size:]
        
        return context
    
    def save_knowledge_base(self, path: str) -> bool:
        """Save the agent's knowledge base to disk.
        
        Args:
            path: Path to save to
            
        Returns:
            bool: True if successful, False otherwise
        """
        return self.rag_client.save(path)
    
    def load_knowledge_base(self, path: str) -> bool:
        """Load the agent's knowledge base from disk.
        
        Args:
            path: Path to load from
            
        Returns:
            bool: True if successful, False otherwise
        """
        return self.rag_client.load(path)
