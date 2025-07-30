from isa_model.inference.providers.base_provider import BaseProvider
from isa_model.inference.base import ModelType, Capability
from typing import Dict, List, Any
import logging
import os

logger = logging.getLogger(__name__)

class ReplicateProvider(BaseProvider):
    """Provider for Replicate API with proper API key management"""
    
    def __init__(self, config=None):
        """Initialize the Replicate Provider with centralized config management"""
        super().__init__(config)
        self.name = "replicate"
        
        logger.info("Initialized ReplicateProvider")
        
        if not self.has_valid_credentials():
            logger.warning("Replicate API token not found. Set REPLICATE_API_TOKEN environment variable or pass api_token in config.")
    
    def _load_provider_env_vars(self):
        """Load Replicate-specific environment variables"""
        # Set defaults first
        defaults = {
            "timeout": 60,
            "max_tokens": 1024
        }
        
        # Apply defaults only if not already set
        for key, value in defaults.items():
            if key not in self.config:
                self.config[key] = value
        
        # Load from environment variables (override config if present)
        env_mappings = {
            "api_token": "REPLICATE_API_TOKEN",
        }
        
        for config_key, env_var in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value:
                self.config[config_key] = env_value
    
    def _validate_config(self):
        """Validate Replicate configuration"""
        if not self.config.get("api_token"):
            logger.debug("Replicate API token not set - some functionality may not work")
    
    def get_api_key(self) -> str:
        """Get the API token for this provider (override for Replicate naming)"""
        return self.config.get("api_token", "")
    
    def has_valid_credentials(self) -> bool:
        """Check if provider has valid credentials (override for Replicate naming)"""
        return bool(self.config.get("api_token"))
    
    def set_api_token(self, api_token: str):
        """Set the API token after initialization"""
        self.config["api_token"] = api_token
        logger.info("Replicate API token updated")
    
    def get_capabilities(self) -> Dict[ModelType, List[Capability]]:
        """Get provider capabilities by model type"""
        return {
            ModelType.LLM: [
                Capability.CHAT, 
                Capability.COMPLETION
            ],
            ModelType.VISION: [
                Capability.IMAGE_GENERATION,
                Capability.MULTIMODAL_UNDERSTANDING
            ],
            ModelType.AUDIO: [
                Capability.SPEECH_TO_TEXT,
                Capability.TEXT_TO_SPEECH
            ]
        }
    
    def get_models(self, model_type: ModelType) -> List[str]:
        """Get available models for given type"""
        if model_type == ModelType.LLM:
            return [
                "meta/llama-3-70b-instruct",
                "meta/llama-3-8b-instruct",
                "anthropic/claude-3-opus-20240229",
                "anthropic/claude-3-sonnet-20240229"
            ]
        elif model_type == ModelType.VISION:
            return [
                "black-forest-labs/flux-schnell",
                "black-forest-labs/flux-kontext-pro",
                "stability-ai/sdxl",
                "stability-ai/stable-diffusion-3-medium",
                "meta/llama-3-70b-vision",
                "anthropic/claude-3-opus-20240229",
                "anthropic/claude-3-sonnet-20240229"
            ]
        elif model_type == ModelType.AUDIO:
            return [
                "jaaari/kokoro-82m",
                "openai/whisper",
                "suno-ai/bark"
            ]
        else:
            return []
    
    def get_config(self) -> Dict[str, Any]:
        """Get provider configuration"""
        # Return a copy without sensitive information
        config_copy = self.config.copy()
        if "api_token" in config_copy:
            config_copy["api_token"] = "***" if config_copy["api_token"] else ""
        return config_copy
    
    def is_reasoning_model(self, model_name: str) -> bool:
        """Check if the model is optimized for reasoning tasks"""
        reasoning_models = ["llama-3-70b", "claude-3-opus", "claude-3-sonnet"]
        return any(rm in model_name.lower() for rm in reasoning_models) 