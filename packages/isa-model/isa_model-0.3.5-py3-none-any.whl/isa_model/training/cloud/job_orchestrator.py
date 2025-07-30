"""
Training Job Orchestrator

This module orchestrates the complete training workflow:
- Dataset preparation and validation
- Job submission to cloud providers
- Training monitoring and progress tracking
- Model artifact collection and storage
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime

from .runpod_trainer import RunPodTrainer, RunPodConfig
from .storage_manager import CloudStorageManager, StorageConfig
# from ..engine.llama_factory.config import SFTConfig, DatasetFormat
# Note: LlamaFactory integration is planned but not yet implemented

logger = logging.getLogger(__name__)


@dataclass
class JobConfig:
    """Configuration for training job orchestration."""
    
    # Model and dataset
    model_name: str  # e.g., "google/gemma-2-4b-it"
    dataset_source: str  # HuggingFace dataset name or local path
    
    # Training parameters
    training_type: str = "sft"  # "sft", "dpo", "rlhf"
    use_lora: bool = True
    batch_size: int = 4
    num_epochs: int = 3
    learning_rate: float = 2e-5
    max_length: int = 1024
    
    # LoRA parameters
    lora_rank: int = 8
    lora_alpha: int = 16
    lora_dropout: float = 0.05
    
    # Job settings
    job_name: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[Dict[str, str]] = None
    
    # Storage settings
    save_model_to_storage: bool = True
    model_name_in_storage: Optional[str] = None
    
    def __post_init__(self):
        """Validate configuration."""
        if not self.model_name:
            raise ValueError("Model name is required")
        if not self.dataset_source:
            raise ValueError("Dataset source is required")
        
        if self.job_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            model_short = self.model_name.split("/")[-1] if "/" in self.model_name else self.model_name
            self.job_name = f"{model_short}_{self.training_type}_{timestamp}"


class TrainingJobOrchestrator:
    """
    Orchestrates complete training workflows.
    
    This class manages the entire training pipeline from dataset preparation
    to model deployment, handling cloud resources and storage automatically.
    
    Example:
        ```python
        # Configure components
        runpod_config = RunPodConfig(
            api_key="your-runpod-key",
            template_id="your-template-id"
        )
        
        storage_config = StorageConfig(
            provider="s3",
            bucket_name="my-training-bucket"
        )
        
        # Initialize orchestrator
        orchestrator = TrainingJobOrchestrator(
            runpod_config=runpod_config,
            storage_config=storage_config
        )
        
        # Configure training job
        job_config = JobConfig(
            model_name="google/gemma-2-4b-it",
            dataset_source="tatsu-lab/alpaca",
            num_epochs=3,
            batch_size=4
        )
        
        # Execute training workflow
        result = orchestrator.execute_training_workflow(job_config)
        print(f"Training completed: {result['model_path']}")
        ```
    """
    
    def __init__(self, 
                 runpod_config: RunPodConfig,
                 storage_config: Optional[StorageConfig] = None):
        """
        Initialize training job orchestrator.
        
        Args:
            runpod_config: RunPod configuration
            storage_config: Optional cloud storage configuration
        """
        self.runpod_trainer = RunPodTrainer(runpod_config)
        self.storage_manager = CloudStorageManager(storage_config) if storage_config else None
        
        self.active_jobs: Dict[str, Dict[str, Any]] = {}
        
        logger.info("Training job orchestrator initialized")
    
    def prepare_dataset(self, dataset_source: str, local_cache_dir: str = "./dataset_cache") -> str:
        """
        Prepare and validate dataset for training.
        
        Args:
            dataset_source: Dataset source (HuggingFace name or local path)
            local_cache_dir: Local directory to cache dataset
            
        Returns:
            Path to prepared dataset
        """
        os.makedirs(local_cache_dir, exist_ok=True)
        
        try:
            if dataset_source.startswith("hf://") or not os.path.exists(dataset_source):
                # HuggingFace dataset
                dataset_name = dataset_source.replace("hf://", "") if dataset_source.startswith("hf://") else dataset_source
                
                logger.info(f"Loading HuggingFace dataset: {dataset_name}")
                
                # Use datasets library to load and convert
                from datasets import load_dataset
                
                dataset = load_dataset(dataset_name)
                train_data = []
                
                # Convert to Alpaca format
                for item in dataset['train']:
                    if 'instruction' in item and 'output' in item:
                        train_data.append({
                            'instruction': item['instruction'],
                            'input': item.get('input', ''),
                            'output': item['output']
                        })
                    elif 'text' in item:
                        # Handle raw text datasets
                        train_data.append({
                            'instruction': "Continue the following text:",
                            'input': item['text'][:512],  # First part as input
                            'output': item['text'][512:1024]  # Next part as output
                        })
                
                # Save prepared dataset
                dataset_path = os.path.join(local_cache_dir, f"{dataset_name.replace('/', '_')}.json")
                with open(dataset_path, 'w') as f:
                    json.dump(train_data, f, indent=2)
                
                logger.info(f"Prepared {len(train_data)} training samples")
                
            else:
                # Local dataset file
                dataset_path = dataset_source
                
                # Validate format
                with open(dataset_path, 'r') as f:
                    data = json.load(f)
                
                if not isinstance(data, list):
                    raise ValueError("Dataset must be a list of training examples")
                
                # Validate required fields
                required_fields = {'instruction', 'output'}
                for i, item in enumerate(data[:5]):  # Check first 5 items
                    if not all(field in item for field in required_fields):
                        raise ValueError(f"Item {i} missing required fields: {required_fields}")
                
                logger.info(f"Validated local dataset with {len(data)} samples")
            
            return dataset_path
            
        except Exception as e:
            logger.error(f"Failed to prepare dataset {dataset_source}: {e}")
            raise
    
    def execute_training_workflow(self, job_config: JobConfig) -> Dict[str, Any]:
        """
        Execute complete training workflow.
        
        Args:
            job_config: Training job configuration
            
        Returns:
            Training results with model path and metrics
        """
        workflow_start_time = datetime.now()
        
        try:
            logger.info(f"Starting training workflow: {job_config.job_name}")
            
            # Step 1: Prepare dataset
            logger.info("Step 1: Preparing dataset...")
            dataset_path = self.prepare_dataset(job_config.dataset_source)
            
            # Step 2: Upload dataset to storage if configured
            dataset_url = dataset_path
            if self.storage_manager:
                logger.info("Step 2: Uploading dataset to cloud storage...")
                dataset_url = self.storage_manager.upload_dataset(
                    local_path=dataset_path,
                    dataset_name=f"{job_config.job_name}_dataset",
                    metadata={
                        "source": job_config.dataset_source,
                        "job_name": job_config.job_name,
                        "created_at": workflow_start_time.isoformat()
                    }
                )
            
            # Step 3: Start training job
            logger.info("Step 3: Starting RunPod training job...")
            training_params = {
                "use_lora": job_config.use_lora,
                "batch_size": job_config.batch_size,
                "num_epochs": job_config.num_epochs,
                "learning_rate": job_config.learning_rate,
                "max_length": job_config.max_length,
                "lora_rank": job_config.lora_rank,
                "lora_alpha": job_config.lora_alpha,
                "lora_dropout": job_config.lora_dropout,
                "dataset_name": dataset_url
            }
            
            job_id = self.runpod_trainer.start_training_job(
                model_name=job_config.model_name,
                dataset_path=dataset_url,
                training_params=training_params,
                job_name=job_config.job_name
            )
            
            # Track job
            self.active_jobs[job_id] = {
                "config": job_config,
                "start_time": workflow_start_time,
                "dataset_path": dataset_path,
                "dataset_url": dataset_url,
                "status": "running"
            }
            
            # Step 4: Monitor training
            logger.info("Step 4: Monitoring training progress...")
            final_status = self.runpod_trainer.monitor_job(job_id)
            
            # Step 5: Collect results
            logger.info("Step 5: Collecting training results...")
            if final_status["status"] == "COMPLETED":
                # Download trained model
                local_model_path = self.runpod_trainer.get_trained_model(job_id)
                
                # Upload to storage if configured
                model_storage_url = None
                if self.storage_manager and job_config.save_model_to_storage:
                    model_name = job_config.model_name_in_storage or job_config.job_name
                    model_storage_url = self.storage_manager.upload_model(
                        local_model_dir=local_model_path,
                        model_name=model_name,
                        metadata={
                            "base_model": job_config.model_name,
                            "dataset_source": job_config.dataset_source,
                            "training_params": training_params,
                            "job_id": job_id,
                            "completed_at": datetime.now().isoformat(),
                            "training_duration": str(datetime.now() - workflow_start_time)
                        }
                    )
                
                # Update job status
                self.active_jobs[job_id].update({
                    "status": "completed",
                    "local_model_path": local_model_path,
                    "model_storage_url": model_storage_url,
                    "final_status": final_status,
                    "end_time": datetime.now()
                })
                
                logger.info(f"Training workflow completed successfully: {job_config.job_name}")
                
                return {
                    "success": True,
                    "job_id": job_id,
                    "job_name": job_config.job_name,
                    "model_path": local_model_path,
                    "model_storage_url": model_storage_url,
                    "training_duration": str(datetime.now() - workflow_start_time),
                    "final_status": final_status
                }
            else:
                # Training failed
                self.active_jobs[job_id].update({
                    "status": "failed",
                    "final_status": final_status,
                    "end_time": datetime.now()
                })
                
                raise RuntimeError(f"Training job failed with status: {final_status['status']}")
                
        except Exception as e:
            logger.error(f"Training workflow failed: {e}")
            
            # Update job status if job_id exists
            if 'job_id' in locals():
                self.active_jobs[job_id].update({
                    "status": "error",
                    "error": str(e),
                    "end_time": datetime.now()
                })
            
            return {
                "success": False,
                "error": str(e),
                "job_name": job_config.job_name,
                "training_duration": str(datetime.now() - workflow_start_time)
            }
    
    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get status of a training job."""
        if job_id in self.active_jobs:
            job_info = self.active_jobs[job_id].copy()
            
            # Get real-time status from RunPod if job is still running
            if job_info["status"] == "running":
                try:
                    runpod_status = self.runpod_trainer.monitor_job(job_id, check_interval=0)
                    job_info["runpod_status"] = runpod_status
                except:
                    pass
            
            return job_info
        else:
            return {"error": f"Job {job_id} not found"}
    
    def list_active_jobs(self) -> List[Dict[str, Any]]:
        """List all active training jobs."""
        return [
            {
                "job_id": job_id,
                "job_name": info["config"].job_name,
                "status": info["status"],
                "start_time": info["start_time"].isoformat(),
                "model_name": info["config"].model_name,
                "dataset_source": info["config"].dataset_source
            }
            for job_id, info in self.active_jobs.items()
        ]
    
    def stop_job(self, job_id: str) -> bool:
        """Stop a running training job."""
        try:
            self.runpod_trainer.stop_job(job_id)
            
            if job_id in self.active_jobs:
                self.active_jobs[job_id].update({
                    "status": "stopped",
                    "end_time": datetime.now()
                })
            
            logger.info(f"Stopped training job: {job_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop job {job_id}: {e}")
            return False
    
    def cleanup_job(self, job_id: str) -> None:
        """Clean up job resources and remove from tracking."""
        try:
            # Stop job if still running
            if job_id in self.active_jobs and self.active_jobs[job_id]["status"] == "running":
                self.stop_job(job_id)
            
            # Remove from tracking
            if job_id in self.active_jobs:
                del self.active_jobs[job_id]
            
            logger.info(f"Cleaned up job: {job_id}")
            
        except Exception as e:
            logger.error(f"Failed to cleanup job {job_id}: {e}") 