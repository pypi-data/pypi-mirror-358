from isa_model.inference.providers.base_provider import BaseProvider
from isa_model.inference.base import ModelType, Capability
from typing import Dict, List, Any
import logging
import os

logger = logging.getLogger(__name__)

class OllamaProvider(BaseProvider):
    """Provider for Ollama API with proper configuration management"""
    
    def __init__(self, config=None):
        """Initialize the Ollama Provider with centralized config management"""
        super().__init__(config)
        self.name = "ollama"
        
        logger.info(f"Initialized OllamaProvider with URL: {self.config.get('base_url', 'http://localhost:11434')}")
    
    def _load_provider_env_vars(self):
        """Load Ollama-specific environment variables"""
        # Set defaults first
        defaults = {
            "base_url": "http://localhost:11434",
            "timeout": 60,
            "temperature": 0.7,
            "top_p": 0.9,
            "max_tokens": 2048,
            "keep_alive": "5m"
        }
        
        # Apply defaults only if not already set
        for key, value in defaults.items():
            if key not in self.config:
                self.config[key] = value
        
        # Load from environment variables (override config if present)
        env_mappings = {
            "base_url": "OLLAMA_BASE_URL",
        }
        
        for config_key, env_var in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value:
                self.config[config_key] = env_value
    
    def _validate_config(self):
        """Validate Ollama configuration"""
        # Ollama doesn't require API keys, just validate base_url is set
        if not self.config.get("base_url"):
            logger.warning("Ollama base_url not set, using default: http://localhost:11434")
            self.config["base_url"] = "http://localhost:11434"
    
    def has_valid_credentials(self) -> bool:
        """Check if provider has valid credentials (Ollama doesn't need API keys)"""
        return True  # Ollama typically doesn't require authentication
    
    def get_capabilities(self) -> Dict[ModelType, List[Capability]]:
        """Get provider capabilities by model type"""
        return {
            ModelType.LLM: [
                Capability.CHAT, 
                Capability.COMPLETION
            ],
            ModelType.EMBEDDING: [
                Capability.EMBEDDING
            ],
            ModelType.VISION: [
                Capability.MULTIMODAL_UNDERSTANDING
            ]
        }
    
    def get_models(self, model_type: ModelType) -> List[str]:
        """Get available models for given type"""
        # Placeholder: In real implementation, this would query Ollama API
        if model_type == ModelType.LLM:
            return ["llama3.2:3b", "llama3", "mistral", "phi3", "llama3.1", "codellama", "gemma"]
        elif model_type == ModelType.EMBEDDING:
            return ["bge-m3", "nomic-embed-text"]
        elif model_type == ModelType.VISION:
            return ["gemma3:4b", "llava", "bakllava", "llama3-vision"]
        else:
            return []
    
    def get_config(self) -> Dict[str, Any]:
        """Get provider configuration"""
        return self.config
    
    def is_reasoning_model(self, model_name: str) -> bool:
        """Check if the model is optimized for reasoning tasks"""
        # Default implementation: consider larger models as reasoning-capable
        reasoning_models = ["llama3.1", "llama3", "claude3", "gpt4", "mixtral", "gemma", "palm2"]
        return any(rm in model_name.lower() for rm in reasoning_models)