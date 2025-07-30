"""
Deployment Manager

Orchestrates the complete deployment workflow including model preparation,
container building, deployment to cloud providers, and monitoring.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime
import asyncio

from .deployment_config import (
    DeploymentConfig, DeploymentProvider, InferenceEngine,
    ModelConfig, TritonConfig, RunPodServerlessConfig
)
from ...core.model_manager import ModelManager
from ...core.model_registry import ModelRegistry, ModelType, ModelCapability
from ...core.storage.hf_storage import HuggingFaceStorage

logger = logging.getLogger(__name__)


class DeploymentManager:
    """
    Manages the complete deployment lifecycle for AI models.
    
    This manager coordinates:
    - Model preparation and optimization
    - Container building and configuration
    - Deployment to cloud providers
    - Health monitoring and scaling
    - Integration with model registry
    
    Example:
        ```python
        from isa_model.deployment import DeploymentManager
        from isa_model.deployment.core import create_gemma_runpod_triton_config
        
        # Initialize deployment manager
        manager = DeploymentManager()
        
        # Create deployment configuration
        config = create_gemma_runpod_triton_config(
            model_id="gemma-v1",
            runpod_api_key="your-api-key",
            model_source_path="xenobordom/gemma-4b-alpaca-v1"
        )
        
        # Deploy the model
        deployment = await manager.deploy_model(config)
        print(f"Model deployed: {deployment['endpoint_url']}")
        ```
    """
    
    def __init__(self, 
                 model_manager: Optional[ModelManager] = None,
                 storage_backend: str = "huggingface",
                 workspace_dir: str = "./deployments"):
        """
        Initialize deployment manager.
        
        Args:
            model_manager: Model manager instance
            storage_backend: Storage backend to use ("huggingface", "local")
            workspace_dir: Directory for deployment artifacts
        """
        self.workspace_dir = Path(workspace_dir)
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize model management
        if storage_backend == "huggingface":
            storage = HuggingFaceStorage()
        else:
            from ...core.model_storage import LocalModelStorage
            storage = LocalModelStorage()
        
        self.model_manager = model_manager or ModelManager(storage=storage)
        self.model_registry = ModelRegistry()
        
        # Deployment tracking
        self.deployments: Dict[str, Dict[str, Any]] = {}
        self.deployments_file = self.workspace_dir / "deployments.json"
        self._load_deployments()
        
        # Setup logging
        self._setup_logging()
        
        logger.info(f"Deployment manager initialized with {storage_backend} storage")
        logger.info(f"Workspace directory: {self.workspace_dir}")
    
    def _setup_logging(self):
        """Setup deployment logging"""
        log_dir = self.workspace_dir / "logs"
        log_dir.mkdir(exist_ok=True)
        
        # Create deployment-specific logger
        deployment_logger = logging.getLogger("deployment")
        deployment_logger.setLevel(logging.DEBUG)
        
        # File handler for deployment logs
        file_handler = logging.FileHandler(log_dir / "deployments.log")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
        ))
        
        deployment_logger.addHandler(file_handler)
    
    def _load_deployments(self):
        """Load deployment tracking data"""
        if self.deployments_file.exists():
            with open(self.deployments_file, 'r') as f:
                self.deployments = json.load(f)
        else:
            self.deployments = {}
            self._save_deployments()
    
    def _save_deployments(self):
        """Save deployment tracking data"""
        with open(self.deployments_file, 'w') as f:
            json.dump(self.deployments, f, indent=2, default=str)
    
    async def deploy_model(self, config: DeploymentConfig) -> Dict[str, Any]:
        """
        Deploy a model using the specified configuration.
        
        Args:
            config: Deployment configuration
            
        Returns:
            Deployment result with endpoint information
        """
        deployment_id = config.deployment_id
        
        logger.info("=" * 60)
        logger.info(f"STARTING DEPLOYMENT: {deployment_id}")
        logger.info("=" * 60)
        
        try:
            # Step 1: Validate configuration
            logger.info("Step 1/6: Validating deployment configuration...")
            self._validate_config(config)
            
            # Step 2: Prepare model
            logger.info("Step 2/6: Preparing model...")
            model_path = await self._prepare_model(config.model_config)
            
            # Step 3: Optimize model (TensorRT conversion if needed)
            logger.info("Step 3/6: Optimizing model...")
            optimized_model_path = await self._optimize_model(config, model_path)
            
            # Step 4: Prepare deployment artifacts
            logger.info("Step 4/6: Preparing deployment artifacts...")
            artifacts_path = await self._prepare_deployment_artifacts(config, optimized_model_path)
            
            # Step 5: Deploy to provider
            logger.info("Step 5/6: Deploying to provider...")
            deployment_result = await self._deploy_to_provider(config, artifacts_path)
            
            # Step 6: Register deployment
            logger.info("Step 6/6: Registering deployment...")
            await self._register_deployment(config, deployment_result)
            
            logger.info("=" * 60)
            logger.info("DEPLOYMENT COMPLETED SUCCESSFULLY!")
            logger.info("=" * 60)
            logger.info(f"Deployment ID: {deployment_id}")
            logger.info(f"Endpoint URL: {deployment_result.get('endpoint_url', 'N/A')}")
            
            return deployment_result
            
        except Exception as e:
            logger.error("=" * 60)
            logger.error("DEPLOYMENT FAILED!")
            logger.error("=" * 60)
            logger.error(f"Error: {e}")
            
            # Update deployment status
            self.deployments[deployment_id] = {
                "config": config.to_dict(),
                "status": "failed",
                "error": str(e),
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            self._save_deployments()
            
            raise
    
    def _validate_config(self, config: DeploymentConfig):
        """Validate deployment configuration"""
        logger.debug("Validating deployment configuration...")
        
        # Check required fields
        if not config.deployment_id:
            raise ValueError("deployment_id is required")
        
        if not config.model_config:
            raise ValueError("model_config is required")
        
        # Provider-specific validation
        if config.provider == DeploymentProvider.RUNPOD_SERVERLESS:
            if not config.runpod_config or not config.runpod_config.api_key:
                raise ValueError("RunPod API key is required for RunPod deployment")
        
        # Engine-specific validation
        if config.inference_engine == InferenceEngine.TRITON:
            if not config.triton_config:
                raise ValueError("Triton configuration is required for Triton engine")
        
        logger.info("Configuration validation passed")
    
    async def _prepare_model(self, model_config: ModelConfig) -> Path:
        """Prepare model for deployment"""
        logger.info(f"Preparing model: {model_config.model_id}")
        
        # Determine model type for registry
        if model_config.model_type == "llm":
            model_type = ModelType.LLM
        elif model_config.model_type == "embedding":
            model_type = ModelType.EMBEDDING
        elif model_config.model_type == "vision":
            model_type = ModelType.VISION
        else:
            model_type = ModelType.LLM  # Default
        
        # Convert capabilities
        capabilities = []
        for cap in model_config.capabilities:
            if cap == "text_generation":
                capabilities.append(ModelCapability.TEXT_GENERATION)
            elif cap == "chat":
                capabilities.append(ModelCapability.CHAT)
            elif cap == "embedding":
                capabilities.append(ModelCapability.EMBEDDING)
            else:
                capabilities.append(ModelCapability.TEXT_GENERATION)  # Default
        
        # Get or download model
        if model_config.source_type == "huggingface":
            model_path = await self.model_manager.get_model(
                model_id=model_config.model_id,
                repo_id=model_config.source_path,
                model_type=model_type,
                capabilities=capabilities
            )
        elif model_config.source_type == "local":
            model_path = Path(model_config.source_path)
            if not model_path.exists():
                raise FileNotFoundError(f"Model not found at {model_path}")
        else:
            raise ValueError(f"Unsupported source type: {model_config.source_type}")
        
        logger.info(f"Model prepared at: {model_path}")
        return model_path
    
    async def _optimize_model(self, config: DeploymentConfig, model_path: Path) -> Path:
        """Optimize model for deployment"""
        logger.info("Optimizing model for deployment...")
        
        # For now, return the original path
        # TODO: Implement TensorRT optimization, quantization, etc.
        if config.model_config.use_tensorrt:
            logger.info("TensorRT optimization requested (not yet implemented)")
        
        if config.model_config.use_quantization:
            logger.info(f"Quantization requested: {config.model_config.quantization_method}")
        
        logger.info("Model optimization completed (pass-through for now)")
        return model_path
    
    async def _prepare_deployment_artifacts(self, config: DeploymentConfig, model_path: Path) -> Path:
        """Prepare deployment artifacts"""
        logger.info("Preparing deployment artifacts...")
        
        # Create deployment workspace
        deployment_workspace = self.workspace_dir / config.deployment_id
        deployment_workspace.mkdir(exist_ok=True)
        
        artifacts = {
            "config": config.to_dict(),
            "model_path": str(model_path),
            "created_at": datetime.now().isoformat()
        }
        
        # Save deployment artifacts
        with open(deployment_workspace / "deployment_config.json", 'w') as f:
            json.dump(artifacts, f, indent=2)
        
        # Generate Triton model configuration if needed
        if config.inference_engine == InferenceEngine.TRITON:
            await self._generate_triton_config(config, deployment_workspace, model_path)
        
        # Generate Docker configuration if needed
        await self._generate_docker_config(config, deployment_workspace)
        
        logger.info(f"Deployment artifacts prepared at: {deployment_workspace}")
        return deployment_workspace
    
    async def _generate_triton_config(self, config: DeploymentConfig, workspace: Path, model_path: Path):
        """Generate Triton model configuration"""
        logger.info("Generating Triton model configuration...")
        
        triton_config = config.triton_config
        model_config = config.model_config
        
        # Create model repository structure
        model_repo = workspace / "model_repository"
        model_dir = model_repo / triton_config.model_name / "1"
        model_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy model files
        import shutil
        if model_path.is_file():
            shutil.copy2(model_path, model_dir)
        else:
            shutil.copytree(model_path, model_dir / "model", dirs_exist_ok=True)
        
        # Generate config.pbtxt
        config_content = f"""
name: "{triton_config.model_name}"
backend: "{triton_config.backend}"
max_batch_size: {triton_config.max_batch_size}

input [
  {{
    name: "input_ids"
    data_type: TYPE_INT32
    dims: [ -1 ]
  }},
  {{
    name: "attention_mask"
    data_type: TYPE_INT32
    dims: [ -1 ]
    optional: true
  }}
]

output [
  {{
    name: "output"
    data_type: TYPE_STRING
    dims: [ -1 ]
  }}
]

instance_group [
  {{
    count: {triton_config.instance_group_count}
    kind: {triton_config.instance_group_kind}
  }}
]

dynamic_batching {{
  max_queue_delay_microseconds: 100
}}
"""
        
        with open(model_repo / triton_config.model_name / "config.pbtxt", 'w') as f:
            f.write(config_content.strip())
        
        logger.info("Triton configuration generated")
    
    async def _generate_docker_config(self, config: DeploymentConfig, workspace: Path):
        """Generate Docker configuration"""
        logger.info("Generating Docker configuration...")
        
        # Generate Dockerfile
        dockerfile_content = f"""
FROM {config.runpod_config.container_image if config.runpod_config else 'nvidia/tritonserver:23.10-py3'}

WORKDIR /workspace

# Copy model repository
COPY model_repository /models

# Copy deployment configuration
COPY deployment_config.json /workspace/

# Set environment variables
ENV TRITON_MODEL_REPOSITORY=/models
ENV CUDA_VISIBLE_DEVICES=0

# Expose Triton ports
EXPOSE 8000 8001 8002

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \\
  CMD curl -f http://localhost:8000/v2/health/ready || exit 1

# Start Triton server
CMD ["tritonserver", "--model-repository=/models", "--allow-http=true", "--allow-grpc=true", "--allow-metrics=true"]
"""
        
        with open(workspace / "Dockerfile", 'w') as f:
            f.write(dockerfile_content.strip())
        
        # Generate docker-compose.yml for local testing
        compose_content = f"""
version: '3.8'

services:
  triton-server:
    build: .
    ports:
      - "8000:8000"
      - "8001:8001"
      - "8002:8002"
    environment:
      - CUDA_VISIBLE_DEVICES=0
    volumes:
      - ./model_repository:/models
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
"""
        
        with open(workspace / "docker-compose.yml", 'w') as f:
            f.write(compose_content.strip())
        
        logger.info("Docker configuration generated")
    
    async def _deploy_to_provider(self, config: DeploymentConfig, artifacts_path: Path) -> Dict[str, Any]:
        """Deploy to the specified provider"""
        logger.info(f"Deploying to provider: {config.provider.value}")
        
        if config.provider == DeploymentProvider.RUNPOD_SERVERLESS:
            return await self._deploy_to_runpod_serverless(config, artifacts_path)
        elif config.provider == DeploymentProvider.LOCAL:
            return await self._deploy_locally(config, artifacts_path)
        else:
            raise ValueError(f"Provider {config.provider} not yet implemented")
    
    async def _deploy_to_runpod_serverless(self, config: DeploymentConfig, artifacts_path: Path) -> Dict[str, Any]:
        """Deploy to RunPod Serverless"""
        logger.info("Deploying to RunPod Serverless...")
        
        # TODO: Implement RunPod Serverless deployment
        # This would involve:
        # 1. Building and pushing Docker image
        # 2. Creating RunPod serverless endpoint
        # 3. Configuring scaling and networking
        
        # For now, return mock result
        result = {
            "provider": "runpod_serverless",
            "endpoint_id": f"mock-endpoint-{config.deployment_id}",
            "endpoint_url": f"https://api.runpod.ai/v2/{config.deployment_id}/run",
            "status": "deployed",
            "deployed_at": datetime.now().isoformat()
        }
        
        logger.info(f"RunPod deployment completed: {result['endpoint_url']}")
        return result
    
    async def _deploy_locally(self, config: DeploymentConfig, artifacts_path: Path) -> Dict[str, Any]:
        """Deploy locally using Docker"""
        logger.info("Deploying locally using Docker...")
        
        # TODO: Implement local Docker deployment
        result = {
            "provider": "local",
            "endpoint_url": "http://localhost:8000",
            "status": "deployed",
            "deployed_at": datetime.now().isoformat(),
            "container_id": f"triton-{config.deployment_id}"
        }
        
        logger.info(f"Local deployment completed: {result['endpoint_url']}")
        return result
    
    async def _register_deployment(self, config: DeploymentConfig, deployment_result: Dict[str, Any]):
        """Register deployment in tracking system"""
        logger.info("Registering deployment...")
        
        deployment_info = {
            "config": config.to_dict(),
            "result": deployment_result,
            "status": "active",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        self.deployments[config.deployment_id] = deployment_info
        self._save_deployments()
        
        logger.info(f"Deployment registered: {config.deployment_id}")
    
    async def list_deployments(self) -> List[Dict[str, Any]]:
        """List all deployments"""
        return [
            {
                "deployment_id": deployment_id,
                **info
            }
            for deployment_id, info in self.deployments.items()
        ]
    
    async def get_deployment(self, deployment_id: str) -> Optional[Dict[str, Any]]:
        """Get deployment information"""
        return self.deployments.get(deployment_id)
    
    async def delete_deployment(self, deployment_id: str) -> bool:
        """Delete a deployment"""
        logger.info(f"Deleting deployment: {deployment_id}")
        
        try:
            if deployment_id in self.deployments:
                # TODO: Implement actual provider cleanup
                
                # Remove from tracking
                del self.deployments[deployment_id]
                self._save_deployments()
                
                # Clean up workspace
                deployment_workspace = self.workspace_dir / deployment_id
                if deployment_workspace.exists():
                    import shutil
                    shutil.rmtree(deployment_workspace)
                
                logger.info(f"Deployment deleted: {deployment_id}")
                return True
            else:
                logger.warning(f"Deployment not found: {deployment_id}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to delete deployment {deployment_id}: {e}")
            return False
    
    async def update_deployment_status(self, deployment_id: str, status: str, **kwargs):
        """Update deployment status"""
        if deployment_id in self.deployments:
            self.deployments[deployment_id]["status"] = status
            self.deployments[deployment_id]["updated_at"] = datetime.now().isoformat()
            
            for key, value in kwargs.items():
                self.deployments[deployment_id][key] = value
            
            self._save_deployments()
            logger.info(f"Updated deployment {deployment_id} status to {status}") 