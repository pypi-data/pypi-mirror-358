import logging
import httpx
import asyncio
from typing import List, Dict, Any, Optional

# 保留您指定的导入和框架结构
from isa_model.inference.services.embedding.base_embed_service import BaseEmbedService
from isa_model.inference.providers.base_provider import BaseProvider

logger = logging.getLogger(__name__)

class OllamaEmbedService(BaseEmbedService):
    """
    Ollama embedding service.
    此类遵循基础服务架构，但使用其自己的 HTTP 客户端与 Ollama API 通信，
    而不依赖于注入的 backend 对象。
    """
    
    def __init__(self, provider: 'BaseProvider', model_name: str = "bge-m3"):
        # 保持对基类和 provider 的兼容
        super().__init__(provider, model_name)
        
        # 从基类继承的 self.config 中获取配置
        host = self.config.get("host", "localhost")
        port = self.config.get("port", 11434)
        
        # 创建并持有自己的 httpx 客户端实例
        base_url = f"http://{host}:{port}"
        self.client = httpx.AsyncClient(base_url=base_url, timeout=30.0)
            
        logger.info(f"Initialized OllamaEmbedService with model '{self.model_name}' at {base_url}")
    
    async def create_text_embedding(self, text: str) -> List[float]:
        """为单个文本创建 embedding"""
        try:
            payload = {
                "model": self.model_name,
                "prompt": text
            }
            # 使用自己的 client 实例，而不是 self.backend
            response = await self.client.post("/api/embeddings", json=payload)
            response.raise_for_status() # 检查请求是否成功
            return response.json()["embedding"]
            
        except httpx.RequestError as e:
            logger.error(f"An error occurred while requesting {e.request.url!r}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error creating text embedding: {e}")
            raise
    
    async def create_text_embeddings(self, texts: List[str]) -> List[List[float]]:
        """为多个文本并发地创建 embeddings"""
        if not texts:
            return []
        
        tasks = [self.create_text_embedding(text) for text in texts]
        embeddings = await asyncio.gather(*tasks)
        return embeddings
    
    async def create_chunks(self, text: str, metadata: Optional[Dict] = None) -> List[Dict]:
        """将文本分块并为每个块创建 embedding"""
        chunk_size = 200  # 单词数量
        words = text.split()
        chunk_texts = [" ".join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]
        
        if not chunk_texts:
            return []

        embeddings = await self.create_text_embeddings(chunk_texts)
        
        chunks = [
            {
                "text": chunk_text,
                "embedding": emb,
                "metadata": metadata or {}
            }
            for chunk_text, emb in zip(chunk_texts, embeddings)
        ]
            
        return chunks
    
    async def compute_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """计算两个嵌入向量之间的余弦相似度"""
        dot_product = sum(a * b for a, b in zip(embedding1, embedding2))
        norm1 = sum(a * a for a in embedding1) ** 0.5
        norm2 = sum(b * b for b in embedding2) ** 0.5
        
        if norm1 * norm2 == 0:
            return 0.0
            
        return dot_product / (norm1 * norm2)
    
    async def find_similar_texts(
        self, 
        query_embedding: List[float], 
        candidate_embeddings: List[List[float]], 
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Find most similar texts based on embeddings"""
        similarities = []
        for i, candidate in enumerate(candidate_embeddings):
            similarity = await self.compute_similarity(query_embedding, candidate)
            similarities.append({"index": i, "similarity": similarity})
        
        # Sort by similarity in descending order and return top_k
        similarities.sort(key=lambda x: x["similarity"], reverse=True)
        return similarities[:top_k]
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings produced by this service"""
        # BGE-M3 produces 1024-dimensional embeddings
        return 1024
    
    def get_max_input_length(self) -> int:
        """Get maximum input text length supported"""
        # BGE-M3 supports up to 8192 tokens
        return 8192

    async def close(self):
        """关闭内置的 HTTP 客户端"""
        await self.client.aclose()
        logger.info("OllamaEmbedService's internal client has been closed.")