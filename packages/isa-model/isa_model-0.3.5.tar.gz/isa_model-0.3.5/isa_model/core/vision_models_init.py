"""
Initialize Vision Models in Model Registry

Simple function to register vision models for UI analysis in Supabase
"""

from .model_registry import ModelRegistry, ModelType, ModelCapability

def register_vision_models():
    """Register vision models for UI analysis pipeline"""
    
    registry = ModelRegistry()  # Auto-detects Supabase from .env
    
    # Vision models for UI analysis
    models = [
        {
            "model_id": "omniparser-v2.0",
            "model_type": ModelType.VISION,
            "capabilities": [ModelCapability.UI_DETECTION, ModelCapability.IMAGE_ANALYSIS],
            "metadata": {
                "repo_id": "microsoft/OmniParser-v2.0",
                "provider": "microsoft",
                "version": "2.0",
                "description": "Advanced UI element detection",
                "gpu_memory_mb": 8192,
                "modal_service": "isa-vision"
            }
        },
        {
            "model_id": "table-transformer-detection",
            "model_type": ModelType.VISION,
            "capabilities": [ModelCapability.TABLE_DETECTION, ModelCapability.IMAGE_ANALYSIS],
            "metadata": {
                "repo_id": "microsoft/table-transformer-detection",
                "provider": "microsoft",
                "version": "1.1",
                "description": "Table detection in documents",
                "gpu_memory_mb": 4096,
                "modal_service": "isa-vision"
            }
        },
        {
            "model_id": "table-transformer-structure",
            "model_type": ModelType.VISION,
            "capabilities": [ModelCapability.TABLE_STRUCTURE_RECOGNITION, ModelCapability.IMAGE_ANALYSIS],
            "metadata": {
                "repo_id": "microsoft/table-transformer-structure-recognition-v1.1-all",
                "provider": "microsoft",
                "version": "1.1",
                "description": "Table structure recognition",
                "gpu_memory_mb": 4096,
                "modal_service": "isa-vision"
            }
        },
        {
            "model_id": "paddleocr-v3.0",
            "model_type": ModelType.VISION,
            "capabilities": [ModelCapability.OCR, ModelCapability.IMAGE_ANALYSIS],
            "metadata": {
                "repo_id": "PaddlePaddle/PaddleOCR",
                "provider": "paddlepaddle",
                "version": "3.0",
                "description": "Multilingual OCR",
                "gpu_memory_mb": 2048,
                "modal_service": "isa-vision"
            }
        }
    ]
    
    print("🔧 Registering vision models in Supabase...")
    
    success_count = 0
    for model in models:
        success = registry.register_model(
            model_id=model["model_id"],
            model_type=model["model_type"],
            capabilities=model["capabilities"],
            metadata=model["metadata"]
        )
        
        if success:
            print(f"✅ {model['model_id']}")
            success_count += 1
        else:
            print(f"❌ {model['model_id']}")
    
    print(f"\n📊 Registered {success_count}/{len(models)} models")
    return success_count == len(models)

def get_model_for_capability(capability: ModelCapability) -> str:
    """Get best model for a capability"""
    
    registry = ModelRegistry()
    models = registry.get_models_by_capability(capability)
    
    # Priority mapping
    priorities = {
        ModelCapability.UI_DETECTION: ["omniparser-v2.0"],
        ModelCapability.OCR: ["paddleocr-v3.0"],
        ModelCapability.TABLE_DETECTION: ["table-transformer-detection"],
        ModelCapability.TABLE_STRUCTURE_RECOGNITION: ["table-transformer-structure"]
    }
    
    preferred = priorities.get(capability, [])
    for model_id in preferred:
        if model_id in models:
            return model_id
    
    return list(models.keys())[0] if models else None

if __name__ == "__main__":
    success = register_vision_models()
    if success:
        print("🎉 All vision models registered successfully!")
    else:
        print("⚠️ Some models failed to register")