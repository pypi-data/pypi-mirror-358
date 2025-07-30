from isa_model.inference.providers.base_provider import BaseProvider
from isa_model.inference.base import ModelType, Capability
from typing import Dict, List, Any
import logging
import os

logger = logging.getLogger(__name__)

class OpenAIProvider(BaseProvider):
    """Provider for OpenAI API with proper API key management"""
    
    def __init__(self, config=None):
        """Initialize the OpenAI Provider with centralized config management"""
        super().__init__(config)
        self.name = "openai"
        
        logger.info(f"Initialized OpenAIProvider with URL: {self.config.get('base_url', 'https://api.openai.com/v1')}")
        
        if not self.has_valid_credentials():
            logger.warning("OpenAI API key not found. Set OPENAI_API_KEY environment variable or pass api_key in config.")
    
    def _load_provider_env_vars(self):
        """Load OpenAI-specific environment variables"""
        # Set defaults first
        defaults = {
            "base_url": "https://api.openai.com/v1",
            "timeout": 60,
            "temperature": 0.7,
            "top_p": 0.9,
            "max_tokens": 1024
        }
        
        # Apply defaults only if not already set
        for key, value in defaults.items():
            if key not in self.config:
                self.config[key] = value
        
        # Load from environment variables (override config if present)
        env_mappings = {
            "api_key": "OPENAI_API_KEY",
            "base_url": "OPENAI_API_BASE",
            "organization": "OPENAI_ORGANIZATION"
        }
        
        for config_key, env_var in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value:
                self.config[config_key] = env_value
    
    def _validate_config(self):
        """Validate OpenAI configuration"""
        if not self.config.get("api_key"):
            logger.debug("OpenAI API key not set - some functionality may not work")
    
    def get_model_pricing(self, model_name: str) -> Dict[str, float]:
        """Get pricing information for a model - delegated to ModelManager"""
        # Import here to avoid circular imports
        from isa_model.core.model_manager import ModelManager
        model_manager = ModelManager()
        return model_manager.get_model_pricing("openai", model_name)
    
    def calculate_cost(self, model_name: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost for a request - delegated to ModelManager"""
        # Import here to avoid circular imports
        from isa_model.core.model_manager import ModelManager
        model_manager = ModelManager()
        return model_manager.calculate_cost("openai", model_name, input_tokens, output_tokens)
    
    def set_api_key(self, api_key: str):
        """Set the API key after initialization"""
        self.config["api_key"] = api_key
        logger.info("OpenAI API key updated")
    
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
                Capability.IMAGE_GENERATION,
                Capability.MULTIMODAL_UNDERSTANDING
            ],
            ModelType.AUDIO: [
                Capability.SPEECH_TO_TEXT
            ]
        }
    
    def get_models(self, model_type: ModelType) -> List[str]:
        """Get available models for given type"""
        if model_type == ModelType.LLM:
            return ["gpt-4.1-nano", "gpt-4.1-mini", "gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"]
        elif model_type == ModelType.EMBEDDING:
            return ["text-embedding-3-large", "text-embedding-3-small", "text-embedding-ada-002"]
        elif model_type == ModelType.VISION:
            return ["gpt-4.1-nano", "gpt-4.1-mini", "gpt-4o-mini", "gpt-4o", "gpt-4-vision-preview"]
        elif model_type == ModelType.AUDIO:
            return ["whisper-1", "gpt-4o-transcribe", "tts-1", "tts-1-hd"]
        else:
            return []
    
    def get_default_model(self, model_type: ModelType) -> str:
        """Get default model for a given type"""
        if model_type == ModelType.LLM:
            return "gpt-4.1-nano"  # Cheapest and most cost-effective
        elif model_type == ModelType.EMBEDDING:
            return "text-embedding-3-small"
        elif model_type == ModelType.VISION:
            return "gpt-4.1-nano"
        elif model_type == ModelType.AUDIO:
            return "whisper-1"
        else:
            return ""
    
    def get_config(self) -> Dict[str, Any]:
        """Get provider configuration"""
        # Return a copy without sensitive information
        config_copy = self.config.copy()
        if "api_key" in config_copy:
            config_copy["api_key"] = "***" if config_copy["api_key"] else ""
        return config_copy
    
    def is_reasoning_model(self, model_name: str) -> bool:
        """Check if the model is optimized for reasoning tasks"""
        reasoning_models = ["gpt-4", "gpt-4o", "gpt-4-turbo", "gpt-4.1"]
        return any(rm in model_name.lower() for rm in reasoning_models) 