"""
ISA Model Deployment Module

Provides comprehensive deployment capabilities for AI models including:
- Multi-cloud deployment (RunPod, AWS, GCP, Azure)
- Multiple inference engines (Triton, vLLM, TensorRT-LLM)
- Model optimization and containerization
- Deployment monitoring and management

Main Components:
- DeploymentManager: Orchestrates complete deployment workflow
- DeploymentConfig: Configuration classes for different deployment scenarios
- Cloud providers: RunPod, AWS, GCP, Azure integrations
- Inference engines: Triton, vLLM, TensorRT-LLM support
"""

from .core.deployment_manager import DeploymentManager
from .core.deployment_config import (
    DeploymentConfig,
    DeploymentProvider,
    InferenceEngine,
    ModelConfig,
    ModelFormat,
    TritonConfig,
    RunPodServerlessConfig,
    create_gemma_runpod_triton_config,
    create_local_triton_config
)

__all__ = [
    # Main classes
    "DeploymentManager",
    "DeploymentConfig",
    
    # Configuration classes
    "ModelConfig",
    "TritonConfig", 
    "RunPodServerlessConfig",
    
    # Enums
    "DeploymentProvider",
    "InferenceEngine",
    "ModelFormat",
    
    # Helper functions
    "create_gemma_runpod_triton_config",
    "create_local_triton_config"
]

# Version info
__version__ = "0.1.0"
__author__ = "ISA Model Team" 