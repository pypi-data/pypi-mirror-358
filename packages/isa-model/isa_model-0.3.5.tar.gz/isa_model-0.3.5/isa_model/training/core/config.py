"""
Training Configuration Classes

Defines configuration classes for different training scenarios.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from pathlib import Path


@dataclass
class LoRAConfig:
    """LoRA (Low-Rank Adaptation) configuration."""
    
    use_lora: bool = True
    lora_rank: int = 8
    lora_alpha: int = 16
    lora_dropout: float = 0.05
    lora_target_modules: Optional[List[str]] = None
    
    def __post_init__(self):
        if self.lora_target_modules is None:
            # Default target modules for most transformer models
            self.lora_target_modules = ["q_proj", "v_proj", "k_proj", "o_proj"]


@dataclass
class DatasetConfig:
    """Dataset configuration."""
    
    dataset_path: str
    dataset_format: str = "alpaca"  # alpaca, sharegpt, custom
    max_length: int = 1024
    validation_split: float = 0.1
    preprocessing_num_workers: int = 4
    
    def __post_init__(self):
        if not Path(self.dataset_path).exists() and not self.dataset_path.startswith("http"):
            # Assume it's a HuggingFace dataset name
            pass


@dataclass
class TrainingConfig:
    """Main training configuration."""
    
    # Model configuration
    model_name: str
    output_dir: str
    
    # Training hyperparameters
    num_epochs: int = 3
    batch_size: int = 4
    learning_rate: float = 2e-5
    warmup_steps: int = 100
    weight_decay: float = 0.01
    gradient_accumulation_steps: int = 1
    max_grad_norm: float = 1.0
    
    # Training strategy
    training_type: str = "sft"  # sft, dpo, rlhf
    fp16: bool = True
    bf16: bool = False
    gradient_checkpointing: bool = True
    
    # Saving and logging
    save_steps: int = 500
    logging_steps: int = 10
    eval_steps: int = 500
    save_total_limit: int = 3
    
    # LoRA configuration
    lora_config: Optional[LoRAConfig] = field(default_factory=LoRAConfig)
    
    # Dataset configuration
    dataset_config: Optional[DatasetConfig] = None
    
    # Additional parameters
    extra_params: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        # Create output directory if it doesn't exist
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        
        # Set BF16 for newer GPUs, FP16 for older ones
        if self.bf16:
            self.fp16 = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        config_dict = {}
        
        for key, value in self.__dict__.items():
            if key in ['lora_config', 'dataset_config']:
                if value is not None:
                    config_dict[key] = value.__dict__
                else:
                    config_dict[key] = None
            else:
                config_dict[key] = value
        
        return config_dict
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'TrainingConfig':
        """Create config from dictionary."""
        # Handle nested configs
        if 'lora_config' in config_dict and config_dict['lora_config'] is not None:
            config_dict['lora_config'] = LoRAConfig(**config_dict['lora_config'])
        
        if 'dataset_config' in config_dict and config_dict['dataset_config'] is not None:
            config_dict['dataset_config'] = DatasetConfig(**config_dict['dataset_config'])
        
        return cls(**config_dict)


@dataclass
class RunPodConfig:
    """RunPod cloud training configuration."""
    
    api_key: str
    template_id: str
    gpu_type: str = "NVIDIA RTX A6000"
    gpu_count: int = 1
    container_disk_in_gb: int = 50
    volume_in_gb: int = 100
    max_runtime_hours: int = 24
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return self.__dict__.copy()


@dataclass
class StorageConfig:
    """Cloud storage configuration."""
    
    provider: str  # s3, gcs, local
    bucket_name: Optional[str] = None
    region: Optional[str] = None
    access_key: Optional[str] = None
    secret_key: Optional[str] = None
    service_account_path: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return self.__dict__.copy()


@dataclass 
class JobConfig:
    """Training job configuration for cloud training."""
    
    model_name: str
    dataset_source: str
    job_name: Optional[str] = None
    description: Optional[str] = None
    
    # Training parameters
    training_type: str = "sft"
    num_epochs: int = 3
    batch_size: int = 4
    learning_rate: float = 2e-5
    max_length: int = 1024
    
    # LoRA parameters
    use_lora: bool = True
    lora_rank: int = 8
    lora_alpha: int = 16
    lora_dropout: float = 0.05
    
    # Storage parameters
    save_model_to_storage: bool = True
    model_name_in_storage: Optional[str] = None
    upload_to_hf: bool = False
    hf_model_name: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return self.__dict__.copy() 