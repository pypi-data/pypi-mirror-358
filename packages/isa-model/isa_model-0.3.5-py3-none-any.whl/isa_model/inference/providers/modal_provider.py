"""
Modal Provider

Provider for ISA self-hosted Modal services
No API keys needed since we deploy our own services
"""

import os
import logging
from typing import Dict, Any, Optional, List
from .base_provider import BaseProvider
from isa_model.inference.base import ModelType, Capability

logger = logging.getLogger(__name__)

class ModalProvider(BaseProvider):
    """Provider for ISA Modal services"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.name = "modal"
        self.base_url = "https://modal.com"  # Not used directly
    
    def _load_provider_env_vars(self):
        """Load Modal-specific environment variables"""
        # Modal doesn't need API keys for deployed services
        # But we can load Modal token if available
        modal_token = os.getenv("MODAL_TOKEN_ID") or os.getenv("MODAL_TOKEN_SECRET")
        if modal_token:
            self.config["modal_token"] = modal_token
        
        # Set default config
        if "timeout" not in self.config:
            self.config["timeout"] = 300
        if "deployment_region" not in self.config:
            self.config["deployment_region"] = "us-east-1"
        if "gpu_type" not in self.config:
            self.config["gpu_type"] = "T4"
        
    def get_api_key(self) -> str:
        """Modal services don't need API keys for deployed apps"""
        return "modal-deployed-service"  # Placeholder
    
    def get_base_url(self) -> str:
        """Get base URL for Modal services"""
        return self.base_url
    
    def validate_credentials(self) -> bool:
        """
        Validate Modal credentials
        For deployed services, we assume they're accessible
        """
        try:
            # Check if Modal is available
            import modal
            return True
        except ImportError:
            logger.warning("Modal package not available")
            return False
    
    def get_capabilities(self) -> Dict[ModelType, List[Capability]]:
        """Get Modal provider capabilities"""
        return {
            ModelType.VISION: [
                Capability.OBJECT_DETECTION,
                Capability.IMAGE_ANALYSIS,
                Capability.UI_DETECTION,
                Capability.OCR,
                Capability.DOCUMENT_ANALYSIS
            ]
        }
    
    def get_models(self, model_type: ModelType) -> List[str]:
        """Get available models for given type"""
        if model_type == ModelType.VISION:
            return [
                "omniparser-v2.0",
                "table-transformer-detection",
                "table-transformer-structure-v1.1",
                "paddleocr-3.0",
                "yolov8"
            ]
        return []
    
    def is_reasoning_model(self, model_name: str) -> bool:
        """Check if the model is optimized for reasoning tasks"""
        # Vision models are not reasoning models
        return False
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for Modal services"""
        return {
            "timeout": 300,  # 5 minutes
            "max_retries": 3,
            "deployment_region": "us-east-1",
            "gpu_type": "T4"
        }
    
    def get_billing_info(self) -> Dict[str, Any]:
        """Get billing information for Modal services"""
        return {
            "provider": "modal",
            "billing_model": "compute_usage",
            "cost_per_hour": {
                "T4": 0.60,
                "A100": 4.00
            },
            "note": "Costs depend on actual usage time, scales to zero when not in use"
        }