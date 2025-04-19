"""
Knowledge Management for Agentic Game Framework.

This package provides vector storage and retrieval-augmented generation (RAG)
capabilities for agents, allowing them to store, retrieve, and leverage
knowledge for decision-making.
"""

from .vector_store import VectorStore, VectorStoreConfig
from .rag_client import RAGClient

__all__ = [
    "VectorStore",
    "VectorStoreConfig",
    "RAGClient",
]