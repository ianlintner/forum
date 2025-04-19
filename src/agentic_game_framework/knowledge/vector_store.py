"""
Vector Store for Agentic Game Framework.

This module provides a flexible vector storage system that supports multiple
backends (FAISS, Chroma, etc.) for efficient similarity search and retrieval.
"""

import json
import os
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np

# Optional imports for different backends
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

try:
    import chromadb
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False


class VectorStoreBackend(Enum):
    """Supported vector store backends."""
    MEMORY = auto()  # In-memory vector store
    FAISS = auto()   # Facebook AI Similarity Search
    CHROMA = auto()  # ChromaDB


@dataclass
class VectorStoreConfig:
    """Configuration for vector stores.
    
    Attributes:
        backend: The vector store backend to use
        dimension: Dimension of the vector embeddings
        storage_path: Path to store persistent vector data (if applicable)
        collection_name: Name of the collection/index
        distance_metric: Distance metric for similarity search
        embedding_model: Model to use for generating embeddings
    """
    backend: VectorStoreBackend = VectorStoreBackend.MEMORY
    dimension: int = 768  # Default for many embedding models
    storage_path: Optional[str] = None
    collection_name: str = "default"
    distance_metric: str = "cosine"  # cosine, euclidean, dot_product
    embedding_model: str = "default"  # Can be a model name or identifier


class VectorStoreItem:
    """A single item in the vector store.
    
    Attributes:
        id: Unique identifier for the item
        vector: The embedding vector
        metadata: Additional metadata about the item
        content: The original content that was embedded
    """
    
    def __init__(
        self,
        vector: np.ndarray,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        item_id: Optional[str] = None
    ):
        """Initialize a new vector store item.
        
        Args:
            vector: The embedding vector
            content: The original content that was embedded
            metadata: Additional metadata about the item
            item_id: Unique identifier (generated if not provided)
        """
        self.id = item_id or str(uuid.uuid4())
        self.vector = vector
        self.content = content
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the item to a dictionary representation.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the item
        """
        return {
            "id": self.id,
            "vector": self.vector.tolist() if isinstance(self.vector, np.ndarray) else self.vector,
            "content": self.content,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VectorStoreItem':
        """Create an item from a dictionary representation.
        
        Args:
            data: Dictionary containing item data
            
        Returns:
            VectorStoreItem: A new vector store item
        """
        vector = np.array(data["vector"]) if isinstance(data["vector"], list) else data["vector"]
        return cls(
            vector=vector,
            content=data["content"],
            metadata=data.get("metadata", {}),
            item_id=data.get("id")
        )


class VectorStoreBase(ABC):
    """Abstract base class for vector store implementations."""
    
    @abstractmethod
    def add_item(self, item: VectorStoreItem) -> str:
        """Add an item to the vector store.
        
        Args:
            item: The item to add
            
        Returns:
            str: The ID of the added item
        """
        pass
    
    @abstractmethod
    def add_items(self, items: List[VectorStoreItem]) -> List[str]:
        """Add multiple items to the vector store.
        
        Args:
            items: The items to add
            
        Returns:
            List[str]: The IDs of the added items
        """
        pass
    
    @abstractmethod
    def get_item(self, item_id: str) -> Optional[VectorStoreItem]:
        """Get an item by ID.
        
        Args:
            item_id: ID of the item to retrieve
            
        Returns:
            Optional[VectorStoreItem]: The item, or None if not found
        """
        pass
    
    @abstractmethod
    def delete_item(self, item_id: str) -> bool:
        """Delete an item from the vector store.
        
        Args:
            item_id: ID of the item to delete
            
        Returns:
            bool: True if the item was deleted, False if not found
        """
        pass
    
    @abstractmethod
    def search_by_vector(
        self,
        query_vector: np.ndarray,
        limit: int = 10,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[VectorStoreItem, float]]:
        """Search for similar items by vector.
        
        Args:
            query_vector: The query vector
            limit: Maximum number of results
            filter_metadata: Filter results by metadata
            
        Returns:
            List[Tuple[VectorStoreItem, float]]: List of (item, similarity) tuples
        """
        pass
    
    @abstractmethod
    def search_by_text(
        self,
        query_text: str,
        limit: int = 10,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[VectorStoreItem, float]]:
        """Search for similar items by text.
        
        Args:
            query_text: The query text
            limit: Maximum number of results
            filter_metadata: Filter results by metadata
            
        Returns:
            List[Tuple[VectorStoreItem, float]]: List of (item, similarity) tuples
        """
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """Clear all items from the vector store."""
        pass
    
    @abstractmethod
    def save(self, path: Optional[str] = None) -> bool:
        """Save the vector store to disk.
        
        Args:
            path: Path to save to (uses config.storage_path if None)
            
        Returns:
            bool: True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def load(self, path: Optional[str] = None) -> bool:
        """Load the vector store from disk.
        
        Args:
            path: Path to load from (uses config.storage_path if None)
            
        Returns:
            bool: True if successful, False otherwise
        """
        pass

class MemoryVectorStore(VectorStoreBase):
    """In-memory implementation of a vector store."""
    
    def __init__(self, config: VectorStoreConfig):
        """Initialize a new in-memory vector store.
        
        Args:
            config: Vector store configuration
        """
        self.config = config
        self.items: Dict[str, VectorStoreItem] = {}
    
    def add_item(self, item: VectorStoreItem) -> str:
        """Add an item to the vector store.
        
        Args:
            item: The item to add
            
        Returns:
            str: The ID of the added item
        """
        self.items[item.id] = item
        return item.id
    
    def add_items(self, items: List[VectorStoreItem]) -> List[str]:
        """Add multiple items to the vector store.
        
        Args:
            items: The items to add
            
        Returns:
            List[str]: The IDs of the added items
        """
        item_ids = []
        for item in items:
            item_id = self.add_item(item)
            item_ids.append(item_id)
        return item_ids
    
    def get_item(self, item_id: str) -> Optional[VectorStoreItem]:
        """Get an item by ID.
        
        Args:
            item_id: ID of the item to retrieve
            
        Returns:
            Optional[VectorStoreItem]: The item, or None if not found
        """
        return self.items.get(item_id)
    
    def delete_item(self, item_id: str) -> bool:
        """Delete an item from the vector store.
        
        Args:
            item_id: ID of the item to delete
            
        Returns:
            bool: True if the item was deleted, False if not found
        """
        if item_id in self.items:
            del self.items[item_id]
            return True
        return False
    
    def search_by_vector(
        self,
        query_vector: np.ndarray,
        limit: int = 10,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[VectorStoreItem, float]]:
        """Search for similar items by vector.
        
        Args:
            query_vector: The query vector
            limit: Maximum number of results
            filter_metadata: Filter results by metadata
            
        Returns:
            List[Tuple[VectorStoreItem, float]]: List of (item, similarity) tuples
        """
        results = []
        
        # Apply metadata filter if provided
        filtered_items = self.items.values()
        if filter_metadata:
            filtered_items = [
                item for item in filtered_items
                if all(item.metadata.get(k) == v for k, v in filter_metadata.items())
            ]
        
        # Calculate similarities
        for item in filtered_items:
            similarity = self._calculate_similarity(query_vector, item.vector)
            results.append((item, similarity))
        
        # Sort by similarity (higher is better)
        results.sort(key=lambda x: x[1], reverse=True)
        
        return results[:limit]
    
    def search_by_text(
        self,
        query_text: str,
        limit: int = 10,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[VectorStoreItem, float]]:
        """Search for similar items by text.
        
        Args:
            query_text: The query text
            limit: Maximum number of results
            filter_metadata: Filter results by metadata
            
        Returns:
            List[Tuple[VectorStoreItem, float]]: List of (item, similarity) tuples
        """
        # Generate embedding for the query text
        query_vector = self._get_embedding(query_text)
        
        # Search by vector
        return self.search_by_vector(query_vector, limit, filter_metadata)
    
    def clear(self) -> None:
        """Clear all items from the vector store."""
        self.items.clear()
    
    def save(self, path: Optional[str] = None) -> bool:
        """Save the vector store to disk.
        
        Args:
            path: Path to save to (uses config.storage_path if None)
            
        Returns:
            bool: True if successful, False otherwise
        """
        save_path = path or self.config.storage_path
        if not save_path:
            return False
        
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            # Convert items to dictionaries
            items_dict = {item_id: item.to_dict() for item_id, item in self.items.items()}
            
            # Save to file
            with open(save_path, 'w') as f:
                json.dump(items_dict, f, indent=2)
                
            return True
        except Exception as e:
            print(f"Error saving vector store: {e}")
            return False
    
    def load(self, path: Optional[str] = None) -> bool:
        """Load the vector store from disk.
        
        Args:
            path: Path to load from (uses config.storage_path if None)
            
        Returns:
            bool: True if successful, False otherwise
        """
        load_path = path or self.config.storage_path
        if not load_path or not os.path.exists(load_path):
            return False
        
        try:
            # Load from file
            with open(load_path, 'r') as f:
                items_dict = json.load(f)
                
            # Convert dictionaries to items
            self.items = {
                item_id: VectorStoreItem.from_dict(item_data)
                for item_id, item_data in items_dict.items()
            }
            
            return True
        except Exception as e:
            print(f"Error loading vector store: {e}")
            return False
    
    def _calculate_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate similarity between two vectors.
        
        Args:
            vec1: First vector
            vec2: Second vector
            
        Returns:
            float: Similarity score (higher is more similar)
        """
        if self.config.distance_metric == "cosine":
            # Cosine similarity
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            if norm1 == 0 or norm2 == 0:
                return 0.0
            return np.dot(vec1, vec2) / (norm1 * norm2)
        elif self.config.distance_metric == "euclidean":
            # Euclidean distance (converted to similarity)
            distance = np.linalg.norm(vec1 - vec2)
            return 1.0 / (1.0 + distance)
        else:  # dot_product
            # Dot product
            return np.dot(vec1, vec2)
    
    def _get_embedding(self, text: str) -> np.ndarray:
        """Generate an embedding for the given text.
        
        Args:
            text: The text to embed
            
        Returns:
            np.ndarray: The embedding vector
        """
        # In a real implementation, this would use an actual embedding model
        # For now, we'll use a simple hash-based approach for demonstration
        import hashlib
        
        # Create a deterministic but simple embedding based on text hash
        hash_obj = hashlib.md5(text.encode())
        hash_bytes = hash_obj.digest()
        
        # Convert hash to a vector of the configured dimension
        vector = np.zeros(self.config.dimension)
        for i in range(min(16, self.config.dimension)):
            vector[i] = float(hash_bytes[i]) / 255.0
        
        # Normalize the vector
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
            
        return vector

class VectorStore:
    """
    Main vector store class that provides a unified interface for different backends.
    
    This class serves as a factory for creating vector stores with different backends
    and provides a consistent interface for working with them.
    """
    
    def __init__(self, config: Optional[VectorStoreConfig] = None):
        """Initialize a new vector store.
        
        Args:
            config: Vector store configuration (uses default if None)
        """
        self.config = config or VectorStoreConfig()
        
        # Create the appropriate backend
        if self.config.backend == VectorStoreBackend.FAISS:
            if not FAISS_AVAILABLE:
                raise ImportError("FAISS is not installed. Install it with 'pip install faiss-cpu' or 'pip install faiss-gpu'.")
            self._store = self._create_faiss_store()
        elif self.config.backend == VectorStoreBackend.CHROMA:
            if not CHROMA_AVAILABLE:
                raise ImportError("ChromaDB is not installed. Install it with 'pip install chromadb'.")
            self._store = self._create_chroma_store()
        else:  # Memory
            self._store = MemoryVectorStore(self.config)
    
    def _create_faiss_store(self):
        """Create a FAISS vector store.
        
        Returns:
            VectorStoreBase: A FAISS vector store
        """
        # This would be implemented with the FAISSVectorStore class
        # For now, we'll use the memory store as a fallback
        print("FAISS backend requested but not fully implemented. Using in-memory store instead.")
        return MemoryVectorStore(self.config)
    
    def _create_chroma_store(self):
        """Create a ChromaDB vector store.
        
        Returns:
            VectorStoreBase: A ChromaDB vector store
        """
        # This would be implemented with the ChromaVectorStore class
        # For now, we'll use the memory store as a fallback
        print("ChromaDB backend requested but not fully implemented. Using in-memory store instead.")
        return MemoryVectorStore(self.config)
    
    def add_item(self, vector: np.ndarray, content: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Add an item to the vector store.
        
        Args:
            vector: The embedding vector
            content: The original content that was embedded
            metadata: Additional metadata about the item
            
        Returns:
            str: The ID of the added item
        """
        item = VectorStoreItem(vector=vector, content=content, metadata=metadata)
        return self._store.add_item(item)
    
    def add_text(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Add text to the vector store.
        
        This method automatically generates an embedding for the text.
        
        Args:
            text: The text to add
            metadata: Additional metadata about the item
            
        Returns:
            str: The ID of the added item
        """
        # Generate embedding
        if isinstance(self._store, MemoryVectorStore):
            vector = self._store._get_embedding(text)
        else:
            # Fallback for other backends
            import hashlib
            hash_obj = hashlib.md5(text.encode())
            hash_bytes = hash_obj.digest()
            
            vector = np.zeros(self.config.dimension)
            for i in range(min(16, self.config.dimension)):
                vector[i] = float(hash_bytes[i]) / 255.0
            
            norm = np.linalg.norm(vector)
            if norm > 0:
                vector = vector / norm
        
        # Add to store
        return self.add_item(vector=vector, content=text, metadata=metadata)
    
    def add_texts(self, texts: List[str], metadatas: Optional[List[Dict[str, Any]]] = None) -> List[str]:
        """Add multiple texts to the vector store.
        
        Args:
            texts: The texts to add
            metadatas: Additional metadata for each text
            
        Returns:
            List[str]: The IDs of the added items
        """
        if metadatas is None:
            metadatas = [{} for _ in texts]
        elif len(metadatas) != len(texts):
            raise ValueError("Length of metadatas must match length of texts")
        
        items = []
        for text, metadata in zip(texts, metadatas):
            # Generate embedding
            if isinstance(self._store, MemoryVectorStore):
                vector = self._store._get_embedding(text)
            else:
                # Fallback for other backends
                import hashlib
                hash_obj = hashlib.md5(text.encode())
                hash_bytes = hash_obj.digest()
                
                vector = np.zeros(self.config.dimension)
                for i in range(min(16, self.config.dimension)):
                    vector[i] = float(hash_bytes[i]) / 255.0
                
                norm = np.linalg.norm(vector)
                if norm > 0:
                    vector = vector / norm
            
            items.append(VectorStoreItem(vector=vector, content=text, metadata=metadata))
        
        return self._store.add_items(items)
    
    def search(
        self,
        query: str,
        limit: int = 10,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[str, float]]:
        """Search for similar items by text.
        
        Args:
            query: The query text
            limit: Maximum number of results
            filter_metadata: Filter results by metadata
            
        Returns:
            List[Tuple[str, float]]: List of (content, similarity) tuples
        """
        results = self._store.search_by_text(query, limit, filter_metadata)
        return [(item.content, similarity) for item, similarity in results]
    
    def search_by_vector(
        self,
        query_vector: np.ndarray,
        limit: int = 10,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[str, float]]:
        """Search for similar items by vector.
        
        Args:
            query_vector: The query vector
            limit: Maximum number of results
            filter_metadata: Filter results by metadata
            
        Returns:
            List[Tuple[str, float]]: List of (content, similarity) tuples
        """
        results = self._store.search_by_vector(query_vector, limit, filter_metadata)
        return [(item.content, similarity) for item, similarity in results]
    
    def get_item(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Get an item by ID.
        
        Args:
            item_id: ID of the item to retrieve
            
        Returns:
            Optional[Dict[str, Any]]: The item as a dictionary, or None if not found
        """
        item = self._store.get_item(item_id)
        if item:
            return {
                "id": item.id,
                "content": item.content,
                "metadata": item.metadata
            }
        return None
    
    def delete_item(self, item_id: str) -> bool:
        """Delete an item from the vector store.
        
        Args:
            item_id: ID of the item to delete
            
        Returns:
            bool: True if the item was deleted, False if not found
        """
        return self._store.delete_item(item_id)
    
    def clear(self) -> None:
        """Clear all items from the vector store."""
        self._store.clear()
    
    def save(self, path: Optional[str] = None) -> bool:
        """Save the vector store to disk.
        
        Args:
            path: Path to save to (uses config.storage_path if None)
            
        Returns:
            bool: True if successful, False otherwise
        """
        return self._store.save(path)
    
    def load(self, path: Optional[str] = None) -> bool:
        """Load the vector store from disk.
        
        Args:
            path: Path to load from (uses config.storage_path if None)
            
        Returns:
            bool: True if successful, False otherwise
        """
        return self._store.load(path)
