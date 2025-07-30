from abc import ABC, abstractmethod
from typing import Dict, Any, List, Union, AsyncGenerator, TypeVar, Optional
from isa_model.inference.providers.base_provider import BaseProvider
from isa_model.inference.billing_tracker import track_usage, ServiceType, Provider

T = TypeVar('T')  # Generic type for responses

class BaseService(ABC):
    """Base class for all AI services"""
    
    def __init__(self, provider: 'BaseProvider', model_name: str):
        self.provider = provider
        self.model_name = model_name
        self.config = provider.get_full_config()
        
    def _track_usage(
        self,
        service_type: Union[str, ServiceType],
        operation: str,
        input_tokens: Optional[int] = None,
        output_tokens: Optional[int] = None,
        input_units: Optional[float] = None,
        output_units: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Track usage for billing purposes"""
        try:
            # Determine provider name - try multiple attributes
            provider_name = getattr(self.provider, 'name', None) or \
                          getattr(self.provider, 'provider_name', None) or \
                          getattr(self.provider, '__class__', type(None)).__name__.lower().replace('provider', '') or \
                          'unknown'
            
            track_usage(
                provider=provider_name,
                service_type=service_type,
                model_name=self.model_name,
                operation=operation,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                input_units=input_units,
                output_units=output_units,
                metadata=metadata
            )
        except Exception as e:
            # Don't let billing tracking break the service
            import logging
            logging.getLogger(__name__).warning(f"Failed to track usage: {e}")
        
    def __await__(self):
        """Make the service awaitable"""
        yield
        return self

class BaseEmbeddingService(BaseService):
    """Base class for embedding services"""
    
    @abstractmethod
    async def create_text_embedding(self, text: str) -> List[float]:
        """Create embedding for single text"""
        pass
    
    @abstractmethod
    async def create_text_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Create embeddings for multiple texts"""
        pass
    
    @abstractmethod
    async def create_chunks(self, text: str, metadata: Optional[Dict] = None) -> List[Dict]:
        """Create text chunks with embeddings"""
        pass
    
    @abstractmethod
    async def compute_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Compute similarity between two embeddings"""
        pass
    
    @abstractmethod
    async def close(self):
        """Cleanup resources"""
        pass

class BaseRerankService(BaseService):
    """Base class for reranking services"""
    
    @abstractmethod
    async def rerank(
        self,
        query: str,
        documents: List[Dict],
        top_k: int = 5
    ) -> List[Dict]:
        """Rerank documents based on query relevance"""
        pass
    
    @abstractmethod
    async def rerank_texts(
        self,
        query: str,
        texts: List[str]
    ) -> List[Dict]:
        """Rerank raw texts based on query relevance"""
        pass
