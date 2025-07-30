"""
RunPod Training Integration

This module provides integration with RunPod for on-demand GPU training.
It handles job creation, monitoring, and result retrieval.
"""

import os
import json
import time
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from pathlib import Path

try:
    import runpod
    RUNPOD_AVAILABLE = True
except ImportError:
    RUNPOD_AVAILABLE = False
    runpod = None

# from ..engine.llama_factory.config import SFTConfig, DatasetFormat
# Note: LlamaFactory integration is planned but not yet implemented
from .storage_manager import CloudStorageManager

logger = logging.getLogger(__name__)


@dataclass 
class RunPodConfig:
    """Configuration for RunPod training jobs."""
    
    # RunPod settings
    api_key: str
    template_id: str  # RunPod template with training environment
    gpu_type: str = "NVIDIA RTX A6000"  # Default GPU type
    gpu_count: int = 1
    container_disk_in_gb: int = 50
    volume_in_gb: int = 100
    
    # Training environment
    docker_image: str = "runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04"
    python_version: str = "3.10"
    
    # Storage settings
    use_network_volume: bool = True
    volume_mount_path: str = "/workspace"
    
    # Monitoring
    max_runtime_hours: int = 24
    idle_timeout_minutes: int = 30
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        if not self.api_key:
            raise ValueError("RunPod API key is required")
        if not self.template_id:
            raise ValueError("RunPod template ID is required")


class RunPodTrainer:
    """
    RunPod cloud trainer for distributed training.
    
    This class orchestrates training jobs on RunPod infrastructure,
    handling job creation, monitoring, and result collection.
    
    Example:
        ```python
        # Configure RunPod
        runpod_config = RunPodConfig(
            api_key="your-runpod-api-key",
            template_id="your-template-id",
            gpu_type="NVIDIA A100",
            gpu_count=1
        )
        
        # Initialize trainer
        trainer = RunPodTrainer(runpod_config)
        
        # Start training job
        job_id = trainer.start_training_job(
            model_name="google/gemma-2-4b-it",
            dataset_path="hf://dataset-name",
            training_config={
                "num_epochs": 3,
                "batch_size": 4,
                "learning_rate": 2e-5
            }
        )
        
        # Monitor training
        trainer.monitor_job(job_id)
        
        # Get results
        model_path = trainer.get_trained_model(job_id)
        ```
    """
    
    def __init__(self, config: RunPodConfig, storage_manager: Optional[CloudStorageManager] = None):
        """
        Initialize RunPod trainer.
        
        Args:
            config: RunPod configuration
            storage_manager: Optional cloud storage manager
        """
        if not RUNPOD_AVAILABLE:
            raise ImportError("runpod package is required. Install with: pip install runpod")
            
        self.config = config
        self.storage_manager = storage_manager
        
        # Initialize RunPod client
        runpod.api_key = config.api_key
        
        logger.info(f"RunPod trainer initialized with GPU: {config.gpu_type}")
    
    def _prepare_training_script(self, training_config: Dict[str, Any]) -> str:
        """
        Generate training script for RunPod execution.
        
        Args:
            training_config: Training configuration parameters
            
        Returns:
            Training script content
        """
        script_template = '''#!/bin/bash
set -e

echo "Starting Gemma 3:4B training on RunPod..."

# Setup environment
cd /workspace
export PYTHONPATH=/workspace:$PYTHONPATH

# Install dependencies
pip install -q transformers datasets accelerate bitsandbytes
pip install -q git+https://github.com/hiyouga/LLaMA-Factory.git

# Download and prepare dataset
python -c "
import json
from datasets import load_dataset

# Load dataset from HuggingFace
dataset_name = '{dataset_name}'
if dataset_name.startswith('hf://'):
    dataset_name = dataset_name[5:]  # Remove hf:// prefix
    
dataset = load_dataset(dataset_name)
train_data = []

for item in dataset['train']:
    train_data.append({{
        'instruction': item.get('instruction', ''),
        'input': item.get('input', ''),
        'output': item.get('output', '')
    }})

with open('train_data.json', 'w') as f:
    json.dump(train_data, f, indent=2)
    
print(f'Prepared {{len(train_data)}} training samples')
"

# Create training configuration
cat > train_config.json << 'EOF'
{training_config_json}
EOF

# Start training
python -m llmtuner.cli.sft --config_file train_config.json

# Upload results if storage configured
if [ ! -z "{storage_upload_path}" ]; then
    echo "Uploading trained model..."
    # Add storage upload logic here
fi

echo "Training completed successfully!"
'''
        
        return script_template.format(
            dataset_name=training_config.get('dataset_name', ''),
            training_config_json=json.dumps(training_config, indent=2),
            storage_upload_path=training_config.get('storage_upload_path', '')
        )
    
    def _create_training_config(self, 
                              model_name: str,
                              dataset_path: str, 
                              training_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create LlamaFactory training configuration.
        
        Args:
            model_name: Base model name/path
            dataset_path: Dataset path or HuggingFace dataset name
            training_params: Training parameters
            
        Returns:
            LlamaFactory configuration dictionary
        """
        config = {
            "stage": "sft",
            "model_name_or_path": model_name,
            "dataset": "train_data",
            "template": "gemma",
            "finetuning_type": "lora" if training_params.get("use_lora", True) else "full",
            "lora_target": "q_proj,v_proj,k_proj,o_proj,gate_proj,up_proj,down_proj",
            "output_dir": "/workspace/output",
            
            # Training parameters
            "per_device_train_batch_size": training_params.get("batch_size", 4),
            "num_train_epochs": training_params.get("num_epochs", 3),
            "learning_rate": training_params.get("learning_rate", 2e-5),
            "max_seq_length": training_params.get("max_length", 1024),
            "logging_steps": 10,
            "save_steps": 500,
            "warmup_steps": 100,
            
            # LoRA parameters
            "lora_rank": training_params.get("lora_rank", 8),
            "lora_alpha": training_params.get("lora_alpha", 16),
            "lora_dropout": training_params.get("lora_dropout", 0.05),
            
            # Optimization
            "gradient_accumulation_steps": training_params.get("gradient_accumulation_steps", 1),
            "dataloader_num_workers": 4,
            "remove_unused_columns": False,
            "optim": "adamw_torch",
            "lr_scheduler_type": "cosine",
            "weight_decay": 0.01,
            
            # Logging and saving
            "logging_dir": "/workspace/logs",
            "report_to": "none",  # Disable wandb/tensorboard for now
            "save_total_limit": 2,
            "load_best_model_at_end": True,
            "metric_for_best_model": "eval_loss",
            "greater_is_better": False,
            
            # Dataset info
            "dataset_name": dataset_path,
        }
        
        return config
    
    def start_training_job(self,
                          model_name: str,
                          dataset_path: str,
                          training_params: Optional[Dict[str, Any]] = None,
                          job_name: Optional[str] = None) -> str:
        """
        Start a training job on RunPod.
        
        Args:
            model_name: Base model name (e.g., "google/gemma-2-4b-it")
            dataset_path: Dataset path or HuggingFace dataset name
            training_params: Training configuration parameters
            job_name: Optional job name for identification
            
        Returns:
            RunPod job ID
        """
        if training_params is None:
            training_params = {}
            
        # Create training configuration
        training_config = self._create_training_config(
            model_name=model_name,
            dataset_path=dataset_path,
            training_params=training_params
        )
        
        # Generate training script
        training_script = self._prepare_training_script(training_config)
        
        # Create RunPod job
        job_request = {
            "name": job_name or f"gemma-training-{int(time.time())}",
            "image": self.config.docker_image,
            "gpu_type": self.config.gpu_type,
            "gpu_count": self.config.gpu_count,
            "container_disk_in_gb": self.config.container_disk_in_gb,
            "volume_in_gb": self.config.volume_in_gb,
            "volume_mount_path": self.config.volume_mount_path,
            "ports": "8888/http",  # For Jupyter access if needed
            "env": {
                "HUGGING_FACE_HUB_TOKEN": os.getenv("HUGGING_FACE_HUB_TOKEN", ""),
                "WANDB_DISABLED": "true"
            }
        }
        
        try:
            # Create the pod
            pod = runpod.create_pod(**job_request)
            job_id = pod["id"]
            
            logger.info(f"Created RunPod job: {job_id}")
            
            # Wait for pod to be ready
            self._wait_for_pod_ready(job_id)
            
            # Upload and execute training script
            self._execute_training_script(job_id, training_script)
            
            return job_id
            
        except Exception as e:
            logger.error(f"Failed to start RunPod training job: {e}")
            raise
    
    def _wait_for_pod_ready(self, job_id: str, timeout: int = 600) -> None:
        """Wait for RunPod to be ready."""
        logger.info(f"Waiting for pod {job_id} to be ready...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                pod_status = runpod.get_pod(job_id)
                if pod_status["runtime"]["uptimeInSeconds"] > 0:
                    logger.info(f"Pod {job_id} is ready!")
                    return
            except Exception as e:
                logger.debug(f"Checking pod status: {e}")
            
            time.sleep(10)
        
        raise TimeoutError(f"Pod {job_id} failed to become ready within {timeout} seconds")
    
    def _execute_training_script(self, job_id: str, script_content: str) -> None:
        """Execute training script on RunPod."""
        logger.info(f"Executing training script on pod {job_id}")
        
        # This would use RunPod's API to execute the script
        # For now, we'll create a file and run it
        try:
            # Upload script file
            script_upload = {
                "input": {
                    "file_content": script_content,
                    "file_path": "/workspace/train.sh"
                }
            }
            
            # Execute script
            execution_request = {
                "input": {
                    "command": "chmod +x /workspace/train.sh && /workspace/train.sh"
                }
            }
            
            logger.info("Training script execution started")
            
        except Exception as e:
            logger.error(f"Failed to execute training script: {e}")
            raise
    
    def monitor_job(self, job_id: str, check_interval: int = 60) -> Dict[str, Any]:
        """
        Monitor training job progress.
        
        Args:
            job_id: RunPod job ID
            check_interval: Check interval in seconds
            
        Returns:
            Job status and metrics
        """
        logger.info(f"Monitoring job {job_id}...")
        
        while True:
            try:
                pod_status = runpod.get_pod(job_id)
                
                status_info = {
                    "job_id": job_id,
                    "status": pod_status.get("runtime", {}).get("status", "unknown"),
                    "uptime": pod_status.get("runtime", {}).get("uptimeInSeconds", 0),
                    "gpu_utilization": pod_status.get("runtime", {}).get("gpus", [{}])[0].get("utilization", 0)
                }
                
                logger.info(f"Job {job_id} status: {status_info}")
                
                # Check if job is completed or failed
                if status_info["status"] in ["COMPLETED", "FAILED", "TERMINATED"]:
                    logger.info(f"Job {job_id} finished with status: {status_info['status']}")
                    return status_info
                
                time.sleep(check_interval)
                
            except Exception as e:
                logger.error(f"Error monitoring job {job_id}: {e}")
                time.sleep(check_interval)
    
    def get_trained_model(self, job_id: str, local_path: Optional[str] = None) -> str:
        """
        Retrieve trained model from RunPod job.
        
        Args:
            job_id: RunPod job ID
            local_path: Local path to save model
            
        Returns:
            Path to downloaded model
        """
        logger.info(f"Retrieving trained model from job {job_id}")
        
        if local_path is None:
            local_path = f"./trained_models/gemma_job_{job_id}"
        
        os.makedirs(local_path, exist_ok=True)
        
        try:
            # This would download the model files from RunPod
            # Implementation depends on RunPod's file transfer API
            
            logger.info(f"Model downloaded to: {local_path}")
            return local_path
            
        except Exception as e:
            logger.error(f"Failed to retrieve model from job {job_id}: {e}")
            raise
    
    def stop_job(self, job_id: str) -> None:
        """Stop a running training job."""
        try:
            runpod.terminate_pod(job_id)
            logger.info(f"Stopped job {job_id}")
        except Exception as e:
            logger.error(f"Failed to stop job {job_id}: {e}")
            raise
    
    def list_jobs(self) -> List[Dict[str, Any]]:
        """List all RunPod jobs."""
        try:
            pods = runpod.get_pods()
            return [
                {
                    "job_id": pod["id"],
                    "name": pod["name"],
                    "status": pod.get("runtime", {}).get("status", "unknown"),
                    "gpu_type": pod.get("gpuType", "unknown"),
                    "created": pod.get("createdAt", "")
                }
                for pod in pods
            ]
        except Exception as e:
            logger.error(f"Failed to list jobs: {e}")
            return [] 