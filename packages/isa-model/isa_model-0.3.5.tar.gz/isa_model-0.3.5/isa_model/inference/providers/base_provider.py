from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import os
import logging
from pathlib import Path
import dotenv

from isa_model.inference.base import ModelType, Capability

logger = logging.getLogger(__name__)

class BaseProvider(ABC):
    """Base class for all AI providers - handles API key management"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self._load_environment_config()
        self._validate_config()
    
    def _load_environment_config(self):
        """Load configuration from environment variables"""
        # Load .env file if it exists
        project_root = Path(__file__).parent.parent.parent.parent
        env_path = project_root / ".env"
        
        if env_path.exists():
            dotenv.load_dotenv(env_path)
        
        # Subclasses should override this to load provider-specific env vars
        self._load_provider_env_vars()
    
    @abstractmethod
    def _load_provider_env_vars(self):
        """Load provider-specific environment variables"""
        pass
    
    def _validate_config(self):
        """Validate that required configuration is present"""
        # Subclasses should override this to validate provider-specific config
        pass
    
    def get_api_key(self) -> Optional[str]:
        """Get the API key for this provider"""
        return self.config.get("api_key")
    
    def has_valid_credentials(self) -> bool:
        """Check if provider has valid credentials"""
        return bool(self.get_api_key())
    
    @abstractmethod
    def get_capabilities(self) -> Dict[ModelType, List[Capability]]:
        """Get provider capabilities by model type"""
        pass
    
    @abstractmethod
    def get_models(self, model_type: ModelType) -> List[str]:
        """Get available models for given type"""
        pass
    
    def get_config(self) -> Dict[str, Any]:
        """Get provider configuration (without sensitive data)"""
        # Return a copy without sensitive information
        config_copy = self.config.copy()
        if "api_key" in config_copy:
            config_copy["api_key"] = "***" if config_copy["api_key"] else ""
        if "api_token" in config_copy:
            config_copy["api_token"] = "***" if config_copy["api_token"] else ""
        return config_copy
    
    def get_full_config(self) -> Dict[str, Any]:
        """Get full provider configuration (including sensitive data) - for internal use only"""
        return self.config.copy()
    
    @abstractmethod
    def is_reasoning_model(self, model_name: str) -> bool:
        """Check if the model is optimized for reasoning tasks"""
        pass