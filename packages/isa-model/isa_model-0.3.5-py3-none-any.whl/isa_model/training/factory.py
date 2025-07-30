"""
ISA Model Training Factory

A clean, simplified training factory that uses HuggingFace Transformers directly
without external dependencies like LlamaFactory.
"""

import os
import logging
from typing import Optional, Dict, Any, Union, List
from pathlib import Path
import datetime

from .core import (
    TrainingConfig, 
    LoRAConfig, 
    DatasetConfig,
    BaseTrainer,
    SFTTrainer,
    TrainingUtils,
    DatasetManager,
)
from .cloud import TrainingJobOrchestrator

logger = logging.getLogger(__name__)


class TrainingFactory:
    """
    Unified Training Factory for ISA Model SDK
    
    Provides a clean interface for:
    - Local training with SFT (Supervised Fine-Tuning)
    - Cloud training on RunPod
    - Model evaluation and management
    
    Example usage:
        ```python
        from isa_model.training import TrainingFactory
        
        factory = TrainingFactory()
        
        # Local training
        model_path = factory.train_model(
            model_name="google/gemma-2-4b-it",
            dataset_path="tatsu-lab/alpaca",
            use_lora=True,
            num_epochs=3
        )
        
        # Cloud training on RunPod
        result = factory.train_on_runpod(
            model_name="google/gemma-2-4b-it",
            dataset_path="tatsu-lab/alpaca",
            runpod_api_key="your-api-key",
            template_id="your-template-id"
        )
        ```
    """
    
    def __init__(self, base_output_dir: Optional[str] = None):
        """
        Initialize the training factory.
        
        Args:
            base_output_dir: Base directory for training outputs
        """
        self.base_output_dir = base_output_dir or os.path.join(os.getcwd(), "training_outputs")
        os.makedirs(self.base_output_dir, exist_ok=True)
        
        logger.info(f"TrainingFactory initialized with output dir: {self.base_output_dir}")
    
    def train_model(
        self,
        model_name: str,
        dataset_path: str,
        output_dir: Optional[str] = None,
        training_type: str = "sft",
        dataset_format: str = "alpaca",
        use_lora: bool = True,
        batch_size: int = 4,
        num_epochs: int = 3,
        learning_rate: float = 2e-5,
        max_length: int = 1024,
        lora_rank: int = 8,
        lora_alpha: int = 16,
        validation_split: float = 0.1,
        **kwargs
    ) -> str:
        """
        Train a model locally.
        
        Args:
            model_name: Model identifier (e.g., "google/gemma-2-4b-it")
            dataset_path: Path to dataset or HuggingFace dataset name
            output_dir: Custom output directory
            training_type: Type of training ("sft" supported)
            dataset_format: Dataset format ("alpaca", "sharegpt", "custom")
            use_lora: Whether to use LoRA for efficient training
            batch_size: Training batch size
            num_epochs: Number of training epochs
            learning_rate: Learning rate
            max_length: Maximum sequence length
            lora_rank: LoRA rank parameter
            lora_alpha: LoRA alpha parameter
            validation_split: Fraction of data for validation
            **kwargs: Additional training parameters
            
        Returns:
            Path to the trained model
            
        Example:
            ```python
            model_path = factory.train_model(
                model_name="google/gemma-2-4b-it",
                dataset_path="tatsu-lab/alpaca",
                use_lora=True,
                num_epochs=3,
                batch_size=4
            )
            ```
        """
        # Generate output directory if not provided
        if not output_dir:
            output_dir = TrainingUtils.generate_output_dir(
                model_name, training_type, self.base_output_dir
            )
        
        # Create configurations
        lora_config = LoRAConfig(
            use_lora=use_lora,
            lora_rank=lora_rank,
            lora_alpha=lora_alpha
        ) if use_lora else None
        
        dataset_config = DatasetConfig(
            dataset_path=dataset_path,
            dataset_format=dataset_format,
            max_length=max_length,
            validation_split=validation_split
        )
        
        training_config = TrainingConfig(
            model_name=model_name,
            output_dir=output_dir,
            training_type=training_type,
            num_epochs=num_epochs,
            batch_size=batch_size,
            learning_rate=learning_rate,
            lora_config=lora_config,
            dataset_config=dataset_config,
            **kwargs
        )
        
        # Print training summary
        model_info = TrainingUtils.get_model_info(model_name)
        memory_estimate = TrainingUtils.estimate_memory_usage(
            model_name, batch_size, max_length, use_lora
        )
        
        summary = TrainingUtils.format_training_summary(
            training_config.to_dict(), model_info, memory_estimate
        )
        print(summary)
        
        # Validate configuration
        issues = TrainingUtils.validate_training_config(training_config.to_dict())
        if issues:
            raise ValueError(f"Training configuration issues: {issues}")
        
        # Initialize trainer based on training type
        if training_type.lower() == "sft":
            trainer = SFTTrainer(training_config)
        else:
            raise ValueError(f"Training type '{training_type}' not supported yet")
        
        # Execute training
        logger.info(f"Starting {training_type.upper()} training...")
        result_path = trainer.train()
        
        logger.info(f"Training completed! Model saved to: {result_path}")
        return result_path
    
    def train_on_runpod(
        self,
        model_name: str,
        dataset_path: str,
        runpod_api_key: str,
        template_id: str,
        gpu_type: str = "NVIDIA RTX A6000",
        storage_config: Optional[Dict[str, Any]] = None,
        job_name: Optional[str] = None,
        **training_params
    ) -> Dict[str, Any]:
        """
        Train a model on RunPod cloud infrastructure.
        
        Args:
            model_name: Model identifier
            dataset_path: Dataset path or HuggingFace dataset name
            runpod_api_key: RunPod API key
            template_id: RunPod template ID
            gpu_type: GPU type to use
            storage_config: Optional cloud storage configuration
            job_name: Optional job name
            **training_params: Additional training parameters
            
        Returns:
            Training job results
            
        Example:
            ```python
            result = factory.train_on_runpod(
                model_name="google/gemma-2-4b-it",
                dataset_path="tatsu-lab/alpaca",
                runpod_api_key="your-api-key",
                template_id="your-template-id",
                use_lora=True,
                num_epochs=3
            )
            ```
        """
        # Import cloud components
        from .cloud import TrainingJobOrchestrator
        from .cloud.runpod_trainer import RunPodConfig
        from .cloud.storage_manager import StorageConfig
        from .cloud.job_orchestrator import JobConfig
        
        # Create RunPod configuration
        runpod_config = RunPodConfig(
            api_key=runpod_api_key,
            template_id=template_id,
            gpu_type=gpu_type
        )
        
        # Create storage configuration if provided
        storage_cfg = None
        if storage_config:
            storage_cfg = StorageConfig(**storage_config)
        
        # Create job configuration
        job_config = JobConfig(
            model_name=model_name,
            dataset_source=dataset_path,
            job_name=job_name or f"gemma-training-{int(datetime.datetime.now().timestamp())}",
            **training_params
        )
        
        # Initialize orchestrator and execute training
        orchestrator = TrainingJobOrchestrator(
            runpod_config=runpod_config,
            storage_config=storage_cfg
        )
        
        logger.info(f"Starting RunPod training for {model_name}")
        result = orchestrator.execute_training_workflow(job_config)
        
        return result
    
    async def upload_to_huggingface(
        self,
        model_path: str,
        hf_model_name: str,
        hf_token: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Upload a trained model to HuggingFace Hub using HuggingFaceStorage.
        
        Args:
            model_path: Path to the trained model
            hf_model_name: Name for the model on HuggingFace Hub
            hf_token: HuggingFace token
            metadata: Additional metadata for the model
            
        Returns:
            URL of the uploaded model
        """
        try:
            from ..core.storage.hf_storage import HuggingFaceStorage
            
            logger.info(f"Uploading model to HuggingFace: {hf_model_name}")
            
            # Initialize HuggingFace storage
            storage = HuggingFaceStorage(
                username="xenobordom",
                token=hf_token
            )
            
            # Prepare metadata
            upload_metadata = metadata or {}
            upload_metadata.update({
                "description": f"Fine-tuned model: {hf_model_name}",
                "training_framework": "ISA Model SDK",
                "uploaded_from": "training_factory"
            })
            
            # Upload model
            success = await storage.save_model(
                model_id=hf_model_name,
                model_path=model_path,
                metadata=upload_metadata
            )
            
            if success:
                model_url = storage.get_public_url(hf_model_name)
                logger.info(f"Model uploaded successfully: {model_url}")
                return model_url
            else:
                raise Exception("Failed to upload model")
            
        except Exception as e:
            logger.error(f"Failed to upload to HuggingFace: {e}")
            raise
    
    def get_training_status(self, output_dir: str) -> Dict[str, Any]:
        """
        Get training status from output directory.
        
        Args:
            output_dir: Training output directory
            
        Returns:
            Dictionary with training status information
        """
        status = {
            "output_dir": output_dir,
            "exists": os.path.exists(output_dir),
            "files": []
        }
        
        if status["exists"]:
            status["files"] = os.listdir(output_dir)
            
            # Check for specific files
            config_path = os.path.join(output_dir, "training_config.json")
            metrics_path = os.path.join(output_dir, "training_metrics.json")
            model_path = os.path.join(output_dir, "pytorch_model.bin")
            
            status["has_config"] = os.path.exists(config_path)
            status["has_metrics"] = os.path.exists(metrics_path)
            status["has_model"] = os.path.exists(model_path) or os.path.exists(os.path.join(output_dir, "adapter_model.bin"))
            
            if status["has_config"]:
                try:
                    status["config"] = TrainingUtils.load_training_args(output_dir)
                except:
                    pass
        
        return status
    
    def list_trained_models(self) -> List[Dict[str, Any]]:
        """
        List all trained models in the output directory.
        
        Returns:
            List of model information dictionaries
        """
        models = []
        
        if os.path.exists(self.base_output_dir):
            for item in os.listdir(self.base_output_dir):
                item_path = os.path.join(self.base_output_dir, item)
                if os.path.isdir(item_path):
                    status = self.get_training_status(item_path)
                    models.append({
                        "name": item,
                        "path": item_path,
                        "created": datetime.datetime.fromtimestamp(
                            os.path.getctime(item_path)
                        ).isoformat(),
                        "status": status
                    })
        
        return sorted(models, key=lambda x: x["created"], reverse=True)


# Convenience functions for quick access
def train_gemma(
    dataset_path: str,
    model_size: str = "4b",
    output_dir: Optional[str] = None,
    **kwargs
) -> str:
    """
    Quick function to train Gemma models.
    
    Args:
        dataset_path: Path to training dataset
        model_size: Model size ("2b", "4b", "7b")
        output_dir: Output directory
        **kwargs: Additional training parameters
        
    Returns:
        Path to trained model
        
    Example:
        ```python
        from isa_model.training import train_gemma
        
        model_path = train_gemma(
            dataset_path="tatsu-lab/alpaca",
            model_size="4b",
            num_epochs=3,
            batch_size=4
        )
        ```
    """
    factory = TrainingFactory()
    
    model_map = {
        "2b": "google/gemma-2-2b-it",
        "4b": "google/gemma-2-4b-it", 
        "7b": "google/gemma-2-7b-it"
    }
    
    model_name = model_map.get(model_size, "google/gemma-2-4b-it")
    
    return factory.train_model(
        model_name=model_name,
        dataset_path=dataset_path,
        output_dir=output_dir,
        **kwargs
    ) 