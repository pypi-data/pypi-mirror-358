from typing import Dict, Optional, List, Any
import logging
from pathlib import Path
from huggingface_hub import hf_hub_download, snapshot_download
from huggingface_hub.errors import HfHubHTTPError
from .model_storage import ModelStorage, LocalModelStorage
from .model_registry import ModelRegistry, ModelType, ModelCapability

logger = logging.getLogger(__name__)

class ModelManager:
    """Model management service for handling model downloads, versions, and caching"""
    
    # 统一的模型计费信息 (per 1M tokens)
    MODEL_PRICING = {
        # OpenAI Models
        "openai": {
            "gpt-4o-mini": {"input": 0.15, "output": 0.6},
            "gpt-4.1-mini": {"input": 0.4, "output": 1.6},
            "gpt-4.1-nano": {"input": 0.1, "output": 0.4},
            "gpt-4o": {"input": 5.0, "output": 15.0},
            "gpt-4-turbo": {"input": 10.0, "output": 30.0},
            "gpt-4": {"input": 30.0, "output": 60.0},
            "gpt-3.5-turbo": {"input": 0.5, "output": 1.5},
            "text-embedding-3-small": {"input": 0.02, "output": 0.0},
            "text-embedding-3-large": {"input": 0.13, "output": 0.0},
            "whisper-1": {"input": 6.0, "output": 0.0},
            "tts-1": {"input": 15.0, "output": 0.0},
            "tts-1-hd": {"input": 30.0, "output": 0.0},
        },
        # Ollama Models (免费本地模型)
        "ollama": {
            "llama3.2:3b-instruct-fp16": {"input": 0.0, "output": 0.0},
            "llama3.2-vision:latest": {"input": 0.0, "output": 0.0},
            "bge-m3": {"input": 0.0, "output": 0.0},
        },
        # Replicate Models
        "replicate": {
            "black-forest-labs/flux-schnell": {"input": 3.0, "output": 0.0},  # $3 per 1000 images
            "black-forest-labs/flux-kontext-pro": {"input": 40.0, "output": 0.0},  # $0.04 per image = $40 per 1000 images
            "meta/meta-llama-3-8b-instruct": {"input": 0.05, "output": 0.25},
            "kokoro-82m": {"input": 0.0, "output": 0.4},  # ~$0.0004 per second
            "jaaari/kokoro-82m:f559560eb822dc509045f3921a1921234918b91739db4bf3daab2169b71c7a13": {"input": 0.0, "output": 0.4},
        },
        # YYDS Models
        "yyds": {
            "claude-sonnet-4-20250514": {"input": 4.5, "output": 22.5},  # $0.0045/1K = $4.5/1M, $0.0225/1K = $22.5/1M
            "claude-3-5-sonnet-20241022": {"input": 3.0, "output": 15.0},  # $0.003/1K = $3.0/1M, $0.015/1K = $15.0/1M
        }
    }
    
    def __init__(self, 
                 storage: Optional[ModelStorage] = None,
                 registry: Optional[ModelRegistry] = None):
        self.storage = storage or LocalModelStorage()
        self.registry = registry or ModelRegistry()
    
    def get_model_pricing(self, provider: str, model_name: str) -> Dict[str, float]:
        """获取模型定价信息"""
        return self.MODEL_PRICING.get(provider, {}).get(model_name, {"input": 0.0, "output": 0.0})
    
    def calculate_cost(self, provider: str, model_name: str, input_tokens: int, output_tokens: int) -> float:
        """计算请求成本"""
        pricing = self.get_model_pricing(provider, model_name)
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        return input_cost + output_cost
    
    def get_cheapest_model(self, provider: str, model_type: str = "llm") -> Optional[str]:
        """获取最便宜的模型"""
        provider_models = self.MODEL_PRICING.get(provider, {})
        if not provider_models:
            return None
        
        # 计算每个模型的平均成本 (假设输入输出比例 1:1)
        cheapest_model = None
        lowest_cost = float('inf')
        
        for model_name, pricing in provider_models.items():
            avg_cost = (pricing["input"] + pricing["output"]) / 2
            if avg_cost < lowest_cost:
                lowest_cost = avg_cost
                cheapest_model = model_name
        
        return cheapest_model

    async def get_model(self, 
                       model_id: str, 
                       repo_id: str,
                       model_type: ModelType,
                       capabilities: List[ModelCapability],
                       revision: Optional[str] = None,
                       force_download: bool = False) -> Optional[Path]:
        """
        Get model files, downloading if necessary
        
        Args:
            model_id: Unique identifier for the model
            repo_id: Hugging Face repository ID
            model_type: Type of model (LLM, embedding, etc.)
            capabilities: List of model capabilities
            revision: Specific model version/tag
            force_download: Force re-download even if cached
            
        Returns:
            Path to the model files or None if failed
        """
        # Check if model is already downloaded
        if not force_download:
            model_path = await self.storage.load_model(model_id)
            if model_path:
                logger.info(f"Using cached model {model_id}")
                return model_path
        
        try:
            # Download model files
            logger.info(f"Downloading model {model_id} from {repo_id}")
            model_dir = Path(f"./models/temp/{model_id}")
            model_dir.mkdir(parents=True, exist_ok=True)
            
            snapshot_download(
                repo_id=repo_id,
                revision=revision,
                local_dir=model_dir,
                local_dir_use_symlinks=False
            )
            
            # Save model and metadata
            metadata = {
                "repo_id": repo_id,
                "revision": revision,
                "downloaded_at": str(Path(model_dir).stat().st_mtime)
            }
            
            # Register model
            self.registry.register_model(
                model_id=model_id,
                model_type=model_type,
                capabilities=capabilities,
                metadata=metadata
            )
            
            # Save model files
            await self.storage.save_model(model_id, str(model_dir), metadata)
            
            return await self.storage.load_model(model_id)
            
        except HfHubHTTPError as e:
            logger.error(f"Failed to download model {model_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error downloading model {model_id}: {e}")
            return None
    
    async def list_models(self) -> List[Dict[str, Any]]:
        """List all downloaded models with their metadata"""
        models = await self.storage.list_models()
        return [
            {
                "model_id": model_id,
                **metadata,
                **(self.registry.get_model_info(model_id) or {})
            }
            for model_id, metadata in models.items()
        ]
    
    async def remove_model(self, model_id: str) -> bool:
        """Remove a model and its metadata"""
        try:
            # Remove from storage
            storage_success = await self.storage.delete_model(model_id)
            
            # Unregister from registry
            registry_success = self.registry.unregister_model(model_id)
            
            return storage_success and registry_success
            
        except Exception as e:
            logger.error(f"Failed to remove model {model_id}: {e}")
            return False
    
    async def get_model_info(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific model"""
        storage_info = await self.storage.get_metadata(model_id)
        registry_info = self.registry.get_model_info(model_id)
        
        if not storage_info and not registry_info:
            return None
            
        return {
            **(storage_info or {}),
            **(registry_info or {})
        }
    
    async def update_model(self, 
                          model_id: str, 
                          repo_id: str,
                          model_type: ModelType,
                          capabilities: List[ModelCapability],
                          revision: Optional[str] = None) -> bool:
        """Update a model to a new version"""
        try:
            return bool(await self.get_model(
                model_id=model_id,
                repo_id=repo_id,
                model_type=model_type,
                capabilities=capabilities,
                revision=revision,
                force_download=True
            ))
        except Exception as e:
            logger.error(f"Failed to update model {model_id}: {e}")
            return False 