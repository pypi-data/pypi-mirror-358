from abc import ABC, abstractmethod
from typing import Dict, Any, List, Union, Optional
from isa_model.inference.services.base_service import BaseService

class BaseEmbedService(BaseService):
    """Base class for embedding services"""
    
    @abstractmethod
    async def create_text_embedding(self, text: str) -> List[float]:
        """
        Create embedding for single text
        
        Args:
            text: Input text to embed
            
        Returns:
            List of float values representing the embedding vector
        """
        pass
    
    @abstractmethod
    async def create_text_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Create embeddings for multiple texts
        
        Args:
            texts: List of input texts to embed
            
        Returns:
            List of embedding vectors, one for each input text
        """
        pass
    
    @abstractmethod
    async def create_chunks(self, text: str, metadata: Optional[Dict] = None) -> List[Dict]:
        """
        Create text chunks with embeddings
        
        Args:
            text: Input text to chunk and embed
            metadata: Optional metadata to attach to chunks
            
        Returns:
            List of dictionaries containing:
            - text: The chunk text
            - embedding: The embedding vector
            - metadata: Associated metadata
            - start_index: Start position in original text
            - end_index: End position in original text
        """
        pass
    
    @abstractmethod
    async def compute_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Compute similarity between two embeddings
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Similarity score (typically cosine similarity, range -1 to 1)
        """
        pass
    
    @abstractmethod
    async def find_similar_texts(
        self, 
        query_embedding: List[float], 
        candidate_embeddings: List[List[float]], 
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find most similar texts based on embeddings
        
        Args:
            query_embedding: Query embedding vector
            candidate_embeddings: List of candidate embedding vectors
            top_k: Number of top similar results to return
            
        Returns:
            List of dictionaries containing:
            - index: Index in candidate_embeddings
            - similarity: Similarity score
        """
        pass
    
    @abstractmethod
    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of embeddings produced by this service
        
        Returns:
            Integer dimension of embedding vectors
        """
        pass
    
    @abstractmethod
    def get_max_input_length(self) -> int:
        """
        Get maximum input text length supported
        
        Returns:
            Maximum number of characters/tokens supported
        """
        pass
    
    @abstractmethod
    async def close(self):
        """Cleanup resources"""
        pass
