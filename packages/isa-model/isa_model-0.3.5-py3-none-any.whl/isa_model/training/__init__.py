"""
ISA Model Training Module

Provides unified training capabilities for AI models including:
- Local training with SFT (Supervised Fine-Tuning)
- Cloud training on RunPod
- Model evaluation and management
- HuggingFace integration

Example usage:
    ```python
    from isa_model.training import TrainingFactory, train_gemma
    
    # Quick Gemma training
    model_path = train_gemma(
        dataset_path="tatsu-lab/alpaca",
        model_size="4b",
        num_epochs=3
    )
    
    # Advanced training with custom configuration
    factory = TrainingFactory()
    model_path = factory.train_model(
        model_name="google/gemma-2-4b-it",
        dataset_path="your-dataset.json",
        use_lora=True,
        batch_size=4,
        num_epochs=3
    )
    ```
"""

# Import the new clean factory
from .factory import TrainingFactory, train_gemma

# Import core components
from .core import (
    TrainingConfig,
    LoRAConfig, 
    DatasetConfig,
    BaseTrainer,
    SFTTrainer,
    TrainingUtils,
    DatasetManager
)

# Import cloud training components
from .cloud import (
    RunPodConfig,
    StorageConfig,
    JobConfig,
    TrainingJobOrchestrator
)

__all__ = [
    # Main factory
    'TrainingFactory',
    'train_gemma',
    
    # Core components
    'TrainingConfig',
    'LoRAConfig',
    'DatasetConfig', 
    'BaseTrainer',
    'SFTTrainer',
    'TrainingUtils',
    'DatasetManager',
    
    # Cloud components
    'RunPodConfig',
    'StorageConfig',
    'JobConfig',
    'TrainingJobOrchestrator'
] 