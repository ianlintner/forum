"""
RAG (Retrieval-Augmented Generation) Client for Agentic Game Framework.

This module provides functionality for semantic search and context augmentation
to enhance agent decision-making with relevant knowledge.
"""

from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np

from .vector_store import VectorStore, VectorStoreConfig


class RAGClient:
    """
    Client for retrieval-augmented generation.
    
    The RAGClient provides a high-level interface for semantic search and
    context augmentation, allowing agents to retrieve relevant knowledge
    and incorporate it into their decision-making processes.
    """
    
    def __init__(
        self,
        vector_store: Optional[VectorStore] = None,
        config: Optional[VectorStoreConfig] = None
    ):
        """Initialize a new RAG client.
        
        Args:
            vector_store: Existing vector store to use (creates new one if None)
            config: Configuration for the vector store (if creating a new one)
        """
        self.vector_store = vector_store or VectorStore(config)
    
    def add_knowledge(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Add knowledge to the vector store.
        
        Args:
            content: The knowledge content
            metadata: Additional metadata about the knowledge
            
        Returns:
            str: The ID of the added knowledge
        """
        return self.vector_store.add_text(content, metadata)
    
    def add_knowledge_batch(
        self,
        contents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None
    ) -> List[str]:
        """Add multiple knowledge items to the vector store.
        
        Args:
            contents: The knowledge contents
            metadatas: Additional metadata for each knowledge item
            
        Returns:
            List[str]: The IDs of the added knowledge items
        """
        return self.vector_store.add_texts(contents, metadatas)
    
    def search(
        self,
        query: str,
        limit: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[str, float]]:
        """Search for relevant knowledge.
        
        Args:
            query: The search query
            limit: Maximum number of results
            filter_metadata: Filter results by metadata
            
        Returns:
            List[Tuple[str, float]]: List of (content, relevance) tuples
        """
        return self.vector_store.search(query, limit, filter_metadata)
    
    def augment_context(
        self,
        query: str,
        context: str,
        limit: int = 3,
        filter_metadata: Optional[Dict[str, Any]] = None,
        prefix: str = "Relevant knowledge:\n",
        separator: str = "\n\n"
    ) -> str:
        """Augment a context with relevant knowledge.
        
        Args:
            query: The query to search for relevant knowledge
            context: The original context to augment
            limit: Maximum number of knowledge items to include
            filter_metadata: Filter knowledge by metadata
            prefix: Text to prepend to the knowledge section
            separator: Separator between knowledge items
            
        Returns:
            str: The augmented context
        """
        # Search for relevant knowledge
        results = self.search(query, limit, filter_metadata)
        
        if not results:
            return context
        
        # Format the knowledge
        knowledge_texts = [content for content, _ in results]
        knowledge_section = prefix + separator.join(knowledge_texts)
        
        # Combine with the original context
        return f"{knowledge_section}\n\n{context}"
    
    def generate_query_from_context(self, context: str, max_length: int = 100) -> str:
        """Generate a search query from a context.
        
        This is a simple implementation that extracts key information from the context.
        In a real implementation, this would use more sophisticated techniques.
        
        Args:
            context: The context to generate a query from
            max_length: Maximum length of the generated query
            
        Returns:
            str: The generated query
        """
        # Simple implementation: take the first sentence or up to max_length characters
        query = context.split('.')[0].strip()
        if len(query) > max_length:
            query = query[:max_length].strip()
        return query
    
    def retrieve_and_format(
        self,
        query: str,
        limit: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None,
        format_template: str = "{content}"
    ) -> str:
        """Retrieve knowledge and format it according to a template.
        
        Args:
            query: The search query
            limit: Maximum number of results
            filter_metadata: Filter results by metadata
            format_template: Template for formatting each result
            
        Returns:
            str: The formatted knowledge
        """
        results = self.search(query, limit, filter_metadata)
        
        if not results:
            return ""
        
        formatted_results = []
        for i, (content, relevance) in enumerate(results, 1):
            formatted_result = format_template.format(
                index=i,
                content=content,
                relevance=relevance,
                relevance_percent=int(relevance * 100)
            )
            formatted_results.append(formatted_result)
        
        return "\n\n".join(formatted_results)
    
    def get_knowledge(self, knowledge_id: str) -> Optional[Dict[str, Any]]:
        """Get a knowledge item by ID.
        
        Args:
            knowledge_id: ID of the knowledge to retrieve
            
        Returns:
            Optional[Dict[str, Any]]: The knowledge item, or None if not found
        """
        return self.vector_store.get_item(knowledge_id)
    
    def delete_knowledge(self, knowledge_id: str) -> bool:
        """Delete a knowledge item.
        
        Args:
            knowledge_id: ID of the knowledge to delete
            
        Returns:
            bool: True if the knowledge was deleted, False if not found
        """
        return self.vector_store.delete_item(knowledge_id)
    
    def clear(self) -> None:
        """Clear all knowledge from the vector store."""
        self.vector_store.clear()
    
    def save(self, path: Optional[str] = None) -> bool:
        """Save the knowledge base to disk.
        
        Args:
            path: Path to save to
            
        Returns:
            bool: True if successful, False otherwise
        """
        return self.vector_store.save(path)
    
    def load(self, path: Optional[str] = None) -> bool:
        """Load the knowledge base from disk.
        
        Args:
            path: Path to load from
            
        Returns:
            bool: True if successful, False otherwise
        """
        return self.vector_store.load(path)
