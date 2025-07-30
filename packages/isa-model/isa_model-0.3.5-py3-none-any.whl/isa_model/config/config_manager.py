"""
Configuration Manager

Central configuration management with environment support
"""

import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class ConfigSection:
    """Base configuration section"""
    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__

@dataclass 
class DeploymentConfig(ConfigSection):
    """Deployment configuration"""
    platform: str = "replicate"  # replicate, modal, aws, local
    modal_app_name: str = "isa-ui-analysis"
    modal_gpu_type: str = "A100-40GB"
    modal_memory: int = 32768
    modal_timeout: int = 1800
    modal_keep_warm: int = 1
    
@dataclass
class ModelConfig(ConfigSection):
    """Model configuration"""
    ui_detection_model: str = "microsoft/omniparser-v2"
    ui_planning_model: str = "gpt-4o-mini"
    fallback_detection: str = "yolov8n"
    quantization: bool = False
    batch_size: int = 1

@dataclass
class ServingConfig(ConfigSection):
    """Serving configuration"""
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1
    reload: bool = False
    log_level: str = "info"
    cors_origins: list = None
    
    def __post_init__(self):
        if self.cors_origins is None:
            self.cors_origins = ["*"]

@dataclass
class APIConfig(ConfigSection):
    """API configuration"""
    rate_limit: int = 100  # requests per minute
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    cache_ttl: int = 3600  # 1 hour
    enable_auth: bool = False

@dataclass
class ISAConfig:
    """Complete ISA configuration"""
    environment: str
    deployment: DeploymentConfig
    models: ModelConfig  
    serving: ServingConfig
    api: APIConfig
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "environment": self.environment,
            "deployment": self.deployment.to_dict(),
            "models": self.models.to_dict(),
            "serving": self.serving.to_dict(),
            "api": self.api.to_dict()
        }

class ConfigManager:
    """Configuration manager with environment support"""
    
    _instance = None
    _config = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._config is None:
            self._load_config()
    
    def _load_config(self):
        """Load configuration from environment and files"""
        env = os.getenv("ISA_ENV", "development")
        
        # Default configurations
        default_config = {
            "deployment": DeploymentConfig(),
            "models": ModelConfig(), 
            "serving": ServingConfig(),
            "api": APIConfig()
        }
        
        # Load environment-specific configuration
        config_file = self._get_config_file(env)
        if config_file and config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    file_config = yaml.safe_load(f)
                    
                # Merge configurations
                self._config = self._merge_configs(default_config, file_config, env)
                logger.info(f"Loaded configuration for environment: {env}")
                
            except Exception as e:
                logger.warning(f"Failed to load config file {config_file}: {e}")
                self._config = ISAConfig(environment=env, **default_config)
        else:
            logger.info(f"No config file found for {env}, using defaults")
            self._config = ISAConfig(environment=env, **default_config)
        
        # Override with environment variables
        self._apply_env_overrides()
    
    def _get_config_file(self, env: str) -> Optional[Path]:
        """Get configuration file path for environment"""
        # Try to find config file in multiple locations
        possible_paths = [
            Path(__file__).parent / "environments" / f"{env}.yaml",
            Path.cwd() / "config" / f"{env}.yaml",
            Path.cwd() / f"config_{env}.yaml"
        ]
        
        for path in possible_paths:
            if path.exists():
                return path
        return None
    
    def _merge_configs(self, default: Dict, file_config: Dict, env: str) -> ISAConfig:
        """Merge default and file configurations"""
        
        # Update deployment config
        deployment_data = {**default["deployment"].__dict__}
        if "deployment" in file_config:
            deployment_data.update(file_config["deployment"])
        deployment = DeploymentConfig(**deployment_data)
        
        # Update model config
        models_data = {**default["models"].__dict__}
        if "models" in file_config:
            models_data.update(file_config["models"])
        models = ModelConfig(**models_data)
        
        # Update serving config
        serving_data = {**default["serving"].__dict__}
        if "serving" in file_config:
            serving_data.update(file_config["serving"])
        serving = ServingConfig(**serving_data)
        
        # Update API config
        api_data = {**default["api"].__dict__}
        if "api" in file_config:
            api_data.update(file_config["api"])
        api = APIConfig(**api_data)
        
        return ISAConfig(
            environment=env,
            deployment=deployment,
            models=models,
            serving=serving,
            api=api
        )
    
    def _apply_env_overrides(self):
        """Apply environment variable overrides"""
        # Deployment overrides
        if os.getenv("ISA_DEPLOYMENT_PLATFORM"):
            self._config.deployment.platform = os.getenv("ISA_DEPLOYMENT_PLATFORM")
        
        # Model overrides
        if os.getenv("ISA_UI_DETECTION_MODEL"):
            self._config.models.ui_detection_model = os.getenv("ISA_UI_DETECTION_MODEL")
        
        # Serving overrides
        if os.getenv("ISA_SERVING_PORT"):
            self._config.serving.port = int(os.getenv("ISA_SERVING_PORT"))
        
        if os.getenv("ISA_SERVING_HOST"):
            self._config.serving.host = os.getenv("ISA_SERVING_HOST")
    
    def get_config(self) -> ISAConfig:
        """Get current configuration"""
        return self._config
    
    def reload(self):
        """Reload configuration"""
        self._config = None
        self._load_config()

# Singleton instance
_config_manager = ConfigManager()

def get_config() -> ISAConfig:
    """Get configuration instance"""
    return _config_manager.get_config()

def reload_config():
    """Reload configuration"""
    _config_manager.reload()