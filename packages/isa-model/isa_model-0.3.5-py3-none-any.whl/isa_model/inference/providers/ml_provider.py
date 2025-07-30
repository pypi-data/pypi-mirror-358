from isa_model.inference.providers.base_provider import BaseProvider
from isa_model.inference.base import ModelType, Capability
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class MLProvider(BaseProvider):
    """Provider for traditional ML models"""
    
    def __init__(self, config=None):
        default_config = {
            "model_directory": "./models/ml",
            "cache_models": True,
            "max_cache_size": 5
        }
        
        merged_config = {**default_config, **(config or {})}
        super().__init__(config=merged_config)
        self.name = "ml"
        
        logger.info(f"Initialized MLProvider with model directory: {self.config['model_directory']}")
    
    def get_capabilities(self) -> Dict[ModelType, List[Capability]]:
        """Get provider capabilities"""
        return {
            ModelType.LLM: [],  # ML models are not LLMs
            ModelType.EMBEDDING: [],
            ModelType.VISION: [],
            "ML": [  # Custom model type for traditional ML
                "CLASSIFICATION",
                "REGRESSION", 
                "CLUSTERING",
                "FEATURE_EXTRACTION"
            ]
        }
    
    def get_models(self, model_type: str = "ML") -> List[str]:
        """Get available ML models"""
        # In practice, this would scan the model directory
        return [
            "fraud_detection_rf",
            "customer_churn_xgb", 
            "price_prediction_lr",
            "recommendation_kmeans"
        ]
    
    def get_config(self) -> Dict[str, Any]:
        """Get provider configuration"""
        return self.config