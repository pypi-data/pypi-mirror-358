"""
Deployment Configuration Classes

Defines configuration classes for different deployment scenarios including
RunPod serverless, Triton inference server, and TensorRT-LLM backend.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from enum import Enum
from pathlib import Path


class DeploymentProvider(str, Enum):
    """Deployment providers"""
    RUNPOD_SERVERLESS = "runpod_serverless"
    RUNPOD_PODS = "runpod_pods"
    AWS_LAMBDA = "aws_lambda"
    GOOGLE_CLOUD_RUN = "google_cloud_run"
    AZURE_CONTAINER_INSTANCES = "azure_container_instances"
    LOCAL = "local"


class InferenceEngine(str, Enum):
    """Inference engines"""
    TRITON = "triton"
    VLLM = "vllm"
    TENSORRT_LLM = "tensorrt_llm"
    HUGGINGFACE = "huggingface"
    ONNX = "onnx"
    TORCHSCRIPT = "torchscript"


class ModelFormat(str, Enum):
    """Model formats for deployment"""
    HUGGINGFACE = "huggingface"
    TENSORRT = "tensorrt"
    ONNX = "onnx"
    TORCHSCRIPT = "torchscript"
    SAFETENSORS = "safetensors"


@dataclass
class TritonConfig:
    """Configuration for Triton Inference Server"""
    
    # Model repository configuration
    model_repository: str = "/models"
    model_name: str = "model"
    model_version: str = "1"
    
    # Backend configuration
    backend: str = "tensorrtllm"  # tensorrtllm, python, onnxruntime
    max_batch_size: int = 8
    max_sequence_length: int = 2048
    
    # TensorRT-LLM specific
    tensorrt_llm_model_dir: str = "/models/tensorrt_llm"
    engine_dir: str = "/models/engines"
    tokenizer_dir: str = "/models/tokenizer"
    
    # Performance settings
    instance_group_count: int = 1
    instance_group_kind: str = "KIND_GPU"  # KIND_GPU, KIND_CPU
    
    # Memory settings
    optimization_level: str = "OPTIMIZATION_LEVEL_ENABLED"
    enable_pinned_input: bool = True
    enable_pinned_output: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return self.__dict__.copy()


@dataclass
class RunPodServerlessConfig:
    """Configuration for RunPod Serverless deployment"""
    
    # RunPod settings
    api_key: str
    endpoint_id: Optional[str] = None
    template_id: Optional[str] = None
    
    # Container configuration
    container_image: str = "runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04"
    container_disk_in_gb: int = 20
    
    # GPU configuration
    gpu_type: str = "NVIDIA RTX A6000"
    gpu_count: int = 1
    
    # Scaling configuration
    min_workers: int = 0
    max_workers: int = 3
    idle_timeout: int = 5  # seconds
    
    # Network configuration
    network_volume_id: Optional[str] = None
    
    # Environment variables
    env_vars: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return self.__dict__.copy()


@dataclass
class ModelConfig:
    """Configuration for model deployment"""
    
    # Model identification
    model_id: str
    model_name: str
    model_version: str = "1.0.0"
    
    # Model source
    source_type: str = "huggingface"  # huggingface, local, s3, gcs
    source_path: str = ""
    
    # Model format and engine
    model_format: ModelFormat = ModelFormat.HUGGINGFACE
    inference_engine: InferenceEngine = InferenceEngine.TRITON
    
    # Model metadata
    model_type: str = "llm"  # llm, embedding, vision, audio
    capabilities: List[str] = field(default_factory=lambda: ["text_generation"])
    
    # Performance configuration
    max_batch_size: int = 8
    max_sequence_length: int = 2048
    dtype: str = "float16"  # float32, float16, int8, int4
    
    # Optimization settings
    use_tensorrt: bool = True
    use_quantization: bool = False
    quantization_method: str = "int8"  # int8, int4, awq, gptq
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return self.__dict__.copy()


@dataclass
class DeploymentConfig:
    """Main deployment configuration"""
    
    # Deployment identification
    deployment_id: str
    deployment_name: str
    description: Optional[str] = None
    
    # Provider and engine configuration
    provider: DeploymentProvider = DeploymentProvider.RUNPOD_SERVERLESS
    inference_engine: InferenceEngine = InferenceEngine.TRITON
    
    # Model configuration
    model_config: ModelConfig = None
    
    # Provider-specific configurations
    runpod_config: Optional[RunPodServerlessConfig] = None
    triton_config: Optional[TritonConfig] = None
    
    # Health check configuration
    health_check_path: str = "/health"
    health_check_timeout: int = 30
    
    # Monitoring configuration
    enable_logging: bool = True
    log_level: str = "INFO"
    enable_metrics: bool = True
    
    # Networking
    custom_domain: Optional[str] = None
    allowed_origins: List[str] = field(default_factory=lambda: ["*"])
    
    # Additional settings
    extra_config: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate configuration after initialization"""
        if not self.deployment_id:
            raise ValueError("deployment_id is required")
        
        if not self.deployment_name:
            raise ValueError("deployment_name is required")
        
        if not self.model_config:
            raise ValueError("model_config is required")
        
        # Set default provider configs if not provided
        if self.provider == DeploymentProvider.RUNPOD_SERVERLESS and not self.runpod_config:
            self.runpod_config = RunPodServerlessConfig(api_key="")
        
        if self.inference_engine == InferenceEngine.TRITON and not self.triton_config:
            self.triton_config = TritonConfig()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        config_dict = {}
        
        for key, value in self.__dict__.items():
            if key in ['model_config', 'runpod_config', 'triton_config']:
                if value is not None:
                    config_dict[key] = value.to_dict()
                else:
                    config_dict[key] = None
            elif isinstance(value, Enum):
                config_dict[key] = value.value
            else:
                config_dict[key] = value
        
        return config_dict
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'DeploymentConfig':
        """Create config from dictionary"""
        # Handle nested configs
        if 'model_config' in config_dict and config_dict['model_config'] is not None:
            config_dict['model_config'] = ModelConfig(**config_dict['model_config'])
        
        if 'runpod_config' in config_dict and config_dict['runpod_config'] is not None:
            config_dict['runpod_config'] = RunPodServerlessConfig(**config_dict['runpod_config'])
        
        if 'triton_config' in config_dict and config_dict['triton_config'] is not None:
            config_dict['triton_config'] = TritonConfig(**config_dict['triton_config'])
        
        # Handle enums
        if 'provider' in config_dict:
            config_dict['provider'] = DeploymentProvider(config_dict['provider'])
        
        if 'inference_engine' in config_dict:
            config_dict['inference_engine'] = InferenceEngine(config_dict['inference_engine'])
        
        return cls(**config_dict)


# Predefined configurations for common deployment scenarios

def create_gemma_runpod_triton_config(
    model_id: str,
    runpod_api_key: str,
    model_source_path: str = "xenobordom/gemma-4b-alpaca-v1"
) -> DeploymentConfig:
    """
    Create a deployment configuration for Gemma model on RunPod with Triton + TensorRT-LLM.
    
    Args:
        model_id: Unique identifier for the deployment
        runpod_api_key: RunPod API key
        model_source_path: HuggingFace model path or local path
        
    Returns:
        DeploymentConfig for Gemma deployment
    """
    model_config = ModelConfig(
        model_id=model_id,
        model_name="gemma-4b-alpaca",
        source_type="huggingface",
        source_path=model_source_path,
        model_format=ModelFormat.HUGGINGFACE,
        inference_engine=InferenceEngine.TRITON,
        model_type="llm",
        capabilities=["text_generation", "chat"],
        max_batch_size=8,
        max_sequence_length=2048,
        dtype="float16",
        use_tensorrt=True
    )
    
    runpod_config = RunPodServerlessConfig(
        api_key=runpod_api_key,
        container_image="nvcr.io/nvidia/tritonserver:23.10-trtllm-python-py3",
        container_disk_in_gb=30,
        gpu_type="NVIDIA RTX A6000",
        gpu_count=1,
        min_workers=0,
        max_workers=3,
        idle_timeout=5,
        env_vars={
            "TRITON_MODEL_REPOSITORY": "/models",
            "CUDA_VISIBLE_DEVICES": "0"
        }
    )
    
    triton_config = TritonConfig(
        model_repository="/models",
        model_name="gemma-4b-alpaca",
        backend="tensorrtllm",
        max_batch_size=8,
        max_sequence_length=2048,
        tensorrt_llm_model_dir="/models/tensorrt_llm",
        engine_dir="/models/engines",
        tokenizer_dir="/models/tokenizer"
    )
    
    return DeploymentConfig(
        deployment_id=f"gemma-deployment-{model_id}",
        deployment_name=f"Gemma 4B Alpaca - {model_id}",
        description="Gemma 4B model fine-tuned on Alpaca dataset, deployed with Triton + TensorRT-LLM",
        provider=DeploymentProvider.RUNPOD_SERVERLESS,
        inference_engine=InferenceEngine.TRITON,
        model_config=model_config,
        runpod_config=runpod_config,
        triton_config=triton_config
    )


def create_local_triton_config(
    model_id: str,
    model_source_path: str,
    triton_model_repository: str = "./models/triton"
) -> DeploymentConfig:
    """
    Create a deployment configuration for local Triton deployment.
    
    Args:
        model_id: Unique identifier for the deployment
        model_source_path: Path to the model
        triton_model_repository: Path to Triton model repository
        
    Returns:
        DeploymentConfig for local deployment
    """
    model_config = ModelConfig(
        model_id=model_id,
        model_name=f"local-model-{model_id}",
        source_type="local",
        source_path=model_source_path,
        model_format=ModelFormat.HUGGINGFACE,
        inference_engine=InferenceEngine.TRITON,
        model_type="llm",
        capabilities=["text_generation"],
        max_batch_size=4,
        max_sequence_length=1024,
        dtype="float16"
    )
    
    triton_config = TritonConfig(
        model_repository=triton_model_repository,
        model_name=f"local-model-{model_id}",
        backend="python",  # Use Python backend for local development
        max_batch_size=4,
        max_sequence_length=1024
    )
    
    return DeploymentConfig(
        deployment_id=f"local-deployment-{model_id}",
        deployment_name=f"Local Model - {model_id}",
        description="Local model deployment for development and testing",
        provider=DeploymentProvider.LOCAL,
        inference_engine=InferenceEngine.TRITON,
        model_config=model_config,
        triton_config=triton_config
    ) 