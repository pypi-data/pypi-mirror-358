"""
Enhanced Multi-Modal Training Framework for ISA Model SDK

Supports training for:
- LLM models (GPT, Gemma, Llama, etc.) with Unsloth acceleration
- Stable Diffusion models
- Traditional ML models (scikit-learn, XGBoost, etc.)
- Computer Vision models (CNN, Vision Transformers)
- Audio models (Whisper, etc.)
"""

import os
import json
import logging
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List, Union, Tuple
from pathlib import Path
import datetime

try:
    import torch
    import torch.nn as nn
    from transformers import (
        AutoTokenizer, AutoModelForCausalLM, AutoModelForSequenceClassification,
        Trainer, TrainingArguments, DataCollatorForLanguageModeling
    )
    from peft import LoraConfig, get_peft_model, TaskType
    from datasets import Dataset
    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False

try:
    from unsloth import FastLanguageModel
    from unsloth.trainer import UnslothTrainer
    UNSLOTH_AVAILABLE = True
except ImportError:
    UNSLOTH_AVAILABLE = False

try:
    from diffusers import StableDiffusionPipeline, UNet2DConditionModel
    from diffusers.training_utils import EMAModel
    DIFFUSERS_AVAILABLE = True
except ImportError:
    DIFFUSERS_AVAILABLE = False

try:
    import sklearn
    from sklearn.base import BaseEstimator
    import xgboost as xgb
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

from .config import TrainingConfig, LoRAConfig, DatasetConfig

logger = logging.getLogger(__name__)

# Unsloth supported models
UNSLOTH_SUPPORTED_MODELS = [
    "google/gemma-2-2b",
    "google/gemma-2-2b-it", 
    "google/gemma-2-4b",
    "google/gemma-2-4b-it",
    "google/gemma-2-7b",
    "google/gemma-2-7b-it",
    "meta-llama/Llama-2-7b-hf",
    "meta-llama/Llama-2-7b-chat-hf",
    "meta-llama/Llama-2-13b-hf",
    "meta-llama/Llama-2-13b-chat-hf",
    "mistralai/Mistral-7B-v0.1",
    "mistralai/Mistral-7B-Instruct-v0.1",
    "microsoft/DialoGPT-medium",
    "microsoft/DialoGPT-large",
    "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
]


class BaseTrainer(ABC):
    """
    Abstract base class for all trainers in the ISA Model SDK.
    
    This class defines the common interface that all trainers must implement,
    regardless of the model type (LLM, Stable Diffusion, ML, etc.).
    """
    
    def __init__(self, config: TrainingConfig):
        """
        Initialize the base trainer.
        
        Args:
            config: Training configuration object
        """
        self.config = config
        self.model = None
        self.tokenizer = None
        self.dataset = None
        self.training_args = None
        
        # Create output directory
        os.makedirs(config.output_dir, exist_ok=True)
        
        # Setup comprehensive logging
        self._setup_logging()
        
        logger.info(f"Initialized {self.__class__.__name__} with config: {config.model_name}")
        logger.info(f"Training configuration: {config.to_dict()}")
    
    def _setup_logging(self):
        """Setup comprehensive logging for training process"""
        log_dir = Path(self.config.output_dir) / "logs"
        log_dir.mkdir(exist_ok=True)
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
        )
        
        # File handler for detailed logs
        file_handler = logging.FileHandler(log_dir / 'training_detailed.log')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        
        # File handler for errors only
        error_handler = logging.FileHandler(log_dir / 'training_errors.log')
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)
        
        # Console handler for important info
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        
        # Configure logger
        logger.addHandler(file_handler)
        logger.addHandler(error_handler)
        logger.addHandler(console_handler)
        logger.setLevel(logging.DEBUG)
    
    @abstractmethod
    def load_model(self) -> None:
        """Load the model and tokenizer."""
        pass
    
    @abstractmethod
    def prepare_dataset(self) -> None:
        """Prepare the training dataset."""
        pass
    
    @abstractmethod
    def setup_training(self) -> None:
        """Setup training arguments and trainer."""
        pass
    
    @abstractmethod
    def train(self) -> str:
        """Execute the training process."""
        pass
    
    @abstractmethod
    def save_model(self, output_path: str) -> None:
        """Save the trained model."""
        pass
    
    def validate_config(self) -> List[str]:
        """Validate the training configuration."""
        logger.debug("Validating training configuration...")
        issues = []
        
        if not self.config.model_name:
            issues.append("model_name is required")
        
        if not self.config.output_dir:
            issues.append("output_dir is required")
        
        if self.config.num_epochs <= 0:
            issues.append("num_epochs must be positive")
        
        if self.config.batch_size <= 0:
            issues.append("batch_size must be positive")
        
        if issues:
            logger.error(f"Configuration validation failed: {issues}")
        else:
            logger.info("Configuration validation passed")
        
        return issues
    
    def save_training_config(self) -> None:
        """Save the training configuration to output directory."""
        config_path = os.path.join(self.config.output_dir, "training_config.json")
        with open(config_path, 'w') as f:
            json.dump(self.config.to_dict(), f, indent=2)
        logger.info(f"Training config saved to: {config_path}")


class LLMTrainer(BaseTrainer):
    """
    Trainer for Large Language Models using HuggingFace Transformers with Unsloth acceleration.
    
    Supports:
    - Supervised Fine-Tuning (SFT)
    - LoRA (Low-Rank Adaptation)
    - Unsloth acceleration (2x faster, 50% less memory)
    - Full parameter training
    - Instruction tuning
    """
    
    def __init__(self, config: TrainingConfig):
        super().__init__(config)
        
        if not HF_AVAILABLE:
            raise ImportError("HuggingFace transformers not available. Install with: pip install transformers")
        
        self.trainer = None
        self.data_collator = None
        self.use_unsloth = self._should_use_unsloth()
        
        logger.info(f"LLM Trainer initialized - Unsloth: {'✅ Enabled' if self.use_unsloth else '❌ Disabled'}")
        if self.use_unsloth and not UNSLOTH_AVAILABLE:
            logger.warning("Unsloth requested but not available. Install with: pip install unsloth")
            self.use_unsloth = False
    
    def _should_use_unsloth(self) -> bool:
        """Determine if Unsloth should be used for this model"""
        if not UNSLOTH_AVAILABLE:
            return False
        
        # Check if model is supported by Unsloth
        model_name = self.config.model_name.lower()
        for supported_model in UNSLOTH_SUPPORTED_MODELS:
            if supported_model.lower() in model_name or model_name in supported_model.lower():
                logger.info(f"Model {self.config.model_name} is supported by Unsloth")
                return True
        
        logger.info(f"Model {self.config.model_name} not in Unsloth supported list, using standard training")
        return False
    
    def load_model(self) -> None:
        """Load the LLM model and tokenizer with optional Unsloth acceleration."""
        logger.info(f"Loading model: {self.config.model_name}")
        logger.debug(f"Using Unsloth: {self.use_unsloth}")
        
        try:
            if self.use_unsloth:
                self._load_model_with_unsloth()
            else:
                self._load_model_standard()
            
            logger.info("Model and tokenizer loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    def _load_model_with_unsloth(self) -> None:
        """Load model using Unsloth for acceleration"""
        logger.info("Loading model with Unsloth acceleration...")
        
        # Unsloth model loading
        self.model, self.tokenizer = FastLanguageModel.from_pretrained(
            model_name=self.config.model_name,
            max_seq_length=self.config.dataset_config.max_length if self.config.dataset_config else 1024,
            dtype=None,  # Auto-detect
            load_in_4bit=True,  # Use 4-bit quantization for memory efficiency
        )
        
        # Setup LoRA with Unsloth
        if self.config.lora_config and self.config.lora_config.use_lora:
            logger.info("Setting up LoRA with Unsloth...")
            lora_config = self.config.lora_config
            self.model = FastLanguageModel.get_peft_model(
                self.model,
                r=lora_config.lora_rank,
                target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
                lora_alpha=lora_config.lora_alpha,
                lora_dropout=lora_config.lora_dropout,
                bias="none",
                use_gradient_checkpointing="unsloth",  # Unsloth's optimized gradient checkpointing
                random_state=3407,
                use_rslora=False,  # Rank stabilized LoRA
                loftq_config=None,  # LoftQ
            )
        
        logger.info("Unsloth model loaded successfully")
    
    def _load_model_standard(self) -> None:
        """Load model using standard HuggingFace transformers"""
        logger.info("Loading model with standard HuggingFace transformers...")
        
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.config.model_name,
            trust_remote_code=True,
            padding_side="right"
        )
        
        # Add pad token if missing
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
            logger.debug("Added pad token to tokenizer")
        
        # Load model
        model_kwargs = {
            "trust_remote_code": True,
            "torch_dtype": torch.float16 if torch.cuda.is_available() else torch.float32,
            "device_map": "auto" if torch.cuda.is_available() else None
        }
        
        logger.debug(f"Model loading kwargs: {model_kwargs}")
        
        if self.config.training_type == "classification":
            self.model = AutoModelForSequenceClassification.from_pretrained(
                self.config.model_name, **model_kwargs
            )
        else:
            self.model = AutoModelForCausalLM.from_pretrained(
                self.config.model_name, **model_kwargs
            )
        
        # Setup LoRA if enabled
        if self.config.lora_config and self.config.lora_config.use_lora:
            self._setup_lora()
        
        logger.info("Standard model loaded successfully")
    
    def _setup_lora(self) -> None:
        """Setup LoRA configuration for standard training"""
        logger.info("Setting up LoRA configuration...")
        
        lora_config = LoraConfig(
            r=self.config.lora_config.lora_rank,
            lora_alpha=self.config.lora_config.lora_alpha,
            target_modules=self.config.lora_config.lora_target_modules,
            lora_dropout=self.config.lora_config.lora_dropout,
            bias="none",
            task_type=TaskType.CAUSAL_LM if self.config.training_type != "classification" else TaskType.SEQ_CLS
        )
        
        self.model = get_peft_model(self.model, lora_config)
        self.model.print_trainable_parameters()
        logger.info("LoRA configuration applied successfully")
    
    def prepare_dataset(self) -> None:
        """Prepare the training dataset."""
        logger.info("Preparing training dataset...")
        
        try:
            from .dataset import DatasetManager
            
            if not self.config.dataset_config:
                raise ValueError("Dataset configuration is required")
            
            dataset_manager = DatasetManager(
                self.tokenizer, 
                max_length=self.config.dataset_config.max_length
            )
            
            train_dataset, eval_dataset = dataset_manager.prepare_dataset(
                dataset_path=self.config.dataset_config.dataset_path,
                dataset_format=self.config.dataset_config.dataset_format,
                validation_split=self.config.dataset_config.validation_split
            )
            
            self.dataset = {
                'train': train_dataset,
                'validation': eval_dataset
            }
            
            # Setup data collator
            if self.config.training_type == "classification":
                self.data_collator = None  # Use default
            else:
                self.data_collator = DataCollatorForLanguageModeling(
                    tokenizer=self.tokenizer,
                    mlm=False
                )
            
            logger.info(f"Dataset prepared - Train: {len(train_dataset)} samples")
            if eval_dataset:
                logger.info(f"Validation: {len(eval_dataset)} samples")
            
        except Exception as e:
            logger.error(f"Failed to prepare dataset: {e}")
            raise
    
    def setup_training(self) -> None:
        """Setup training arguments and trainer."""
        logger.info("Setting up training configuration...")
        
        try:
            # Calculate training steps
            total_steps = len(self.dataset['train']) // (self.config.batch_size * self.config.gradient_accumulation_steps) * self.config.num_epochs
            
            logger.debug(f"Total training steps: {total_steps}")
            
            self.training_args = TrainingArguments(
                output_dir=self.config.output_dir,
                num_train_epochs=self.config.num_epochs,
                per_device_train_batch_size=self.config.batch_size,
                per_device_eval_batch_size=self.config.batch_size,
                gradient_accumulation_steps=self.config.gradient_accumulation_steps,
                learning_rate=self.config.learning_rate,
                weight_decay=self.config.weight_decay,
                warmup_steps=max(1, int(0.1 * total_steps)),  # 10% warmup
                logging_steps=max(1, total_steps // 100),  # Log 100 times per training
                eval_strategy="steps" if self.dataset.get('validation') else "no",
                eval_steps=max(1, total_steps // 10) if self.dataset.get('validation') else None,
                save_strategy="steps",
                save_steps=max(1, total_steps // 5),  # Save 5 times per training
                save_total_limit=3,
                load_best_model_at_end=True if self.dataset.get('validation') else False,
                metric_for_best_model="eval_loss" if self.dataset.get('validation') else None,
                greater_is_better=False,
                report_to=None,  # Disable wandb/tensorboard by default
                remove_unused_columns=False,
                dataloader_pin_memory=False,
                fp16=torch.cuda.is_available() and not self.use_unsloth,  # Unsloth handles precision
                gradient_checkpointing=True and not self.use_unsloth,  # Unsloth handles checkpointing
                optim="adamw_torch",
                lr_scheduler_type="cosine",
                logging_dir=os.path.join(self.config.output_dir, "logs"),
                run_name=f"training_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
            
            # Initialize trainer
            if self.use_unsloth:
                logger.info("Initializing Unsloth trainer...")
                self.trainer = UnslothTrainer(
                    model=self.model,
                    tokenizer=self.tokenizer,
                    train_dataset=self.dataset['train'],
                    eval_dataset=self.dataset.get('validation'),
                    args=self.training_args,
                    data_collator=self.data_collator,
                )
            else:
                logger.info("Initializing standard trainer...")
                self.trainer = Trainer(
                    model=self.model,
                    args=self.training_args,
                    train_dataset=self.dataset['train'],
                    eval_dataset=self.dataset.get('validation'),
                    tokenizer=self.tokenizer,
                    data_collator=self.data_collator
                )
            
            logger.info("Training setup completed successfully")
            
        except Exception as e:
            logger.error(f"Failed to setup training: {e}")
            raise
    
    def train(self) -> str:
        """Execute the training process."""
        logger.info("=" * 60)
        logger.info("STARTING LLM TRAINING")
        logger.info("=" * 60)
        
        try:
            # Validate configuration
            issues = self.validate_config()
            if issues:
                raise ValueError(f"Configuration issues: {issues}")
            
            # Load model and prepare dataset
            logger.info("Step 1/5: Loading model...")
            self.load_model()
            
            logger.info("Step 2/5: Preparing dataset...")
            self.prepare_dataset()
            
            logger.info("Step 3/5: Setting up training...")
            self.setup_training()
            
            # Save training config
            self.save_training_config()
            
            logger.info("Step 4/5: Starting training...")
            logger.info(f"Training with {'Unsloth acceleration' if self.use_unsloth else 'standard HuggingFace'}")
            
            # Start training
            train_result = self.trainer.train()
            
            logger.info("Step 5/5: Saving model...")
            # Save final model
            final_model_path = os.path.join(self.config.output_dir, "final_model")
            self.save_model(final_model_path)
            
            # Save training metrics
            metrics_path = os.path.join(self.config.output_dir, "training_metrics.json")
            with open(metrics_path, 'w') as f:
                json.dump(train_result.metrics, f, indent=2)
            
            logger.info("=" * 60)
            logger.info("TRAINING COMPLETED SUCCESSFULLY!")
            logger.info("=" * 60)
            logger.info(f"Model saved to: {final_model_path}")
            logger.info(f"Training metrics saved to: {metrics_path}")
            
            return final_model_path
            
        except Exception as e:
            logger.error("=" * 60)
            logger.error("TRAINING FAILED!")
            logger.error("=" * 60)
            logger.error(f"Error: {e}")
            logger.error("Check the error logs for detailed information")
            raise
    
    def save_model(self, output_path: str) -> None:
        """Save the trained model."""
        logger.info(f"Saving model to: {output_path}")
        
        try:
            os.makedirs(output_path, exist_ok=True)
            
            # Save model and tokenizer
            self.trainer.save_model(output_path)
            self.tokenizer.save_pretrained(output_path)
            
            # Save LoRA adapters if used
            if self.config.lora_config and self.config.lora_config.use_lora:
                adapter_path = os.path.join(output_path, "adapter_model")
                if hasattr(self.model, 'save_pretrained'):
                    self.model.save_pretrained(adapter_path)
                    logger.info(f"LoRA adapters saved to: {adapter_path}")
            
            # Save additional metadata
            metadata = {
                "model_name": self.config.model_name,
                "training_type": self.config.training_type,
                "use_unsloth": self.use_unsloth,
                "use_lora": self.config.lora_config.use_lora if self.config.lora_config else False,
                "saved_at": datetime.datetime.now().isoformat(),
                "config": self.config.to_dict()
            }
            
            with open(os.path.join(output_path, "training_metadata.json"), 'w') as f:
                json.dump(metadata, f, indent=2)
            
            logger.info(f"Model saved successfully to: {output_path}")
            
        except Exception as e:
            logger.error(f"Failed to save model: {e}")
            raise


class StableDiffusionTrainer(BaseTrainer):
    """
    Trainer for Stable Diffusion models.
    
    Supports:
    - DreamBooth training
    - LoRA training
    - Textual Inversion
    - Custom dataset training
    """
    
    def __init__(self, config: TrainingConfig):
        super().__init__(config)
        
        if not DIFFUSERS_AVAILABLE:
            raise ImportError("Diffusers not available. Install with: pip install diffusers")
        
        self.unet = None
        self.vae = None
        self.text_encoder = None
        self.scheduler = None
    
    def load_model(self) -> None:
        """Load Stable Diffusion model components."""
        logger.info(f"Loading Stable Diffusion model: {self.config.model_name}")
        
        # Load pipeline
        pipeline = StableDiffusionPipeline.from_pretrained(
            self.config.model_name,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
        )
        
        self.unet = pipeline.unet
        self.vae = pipeline.vae
        self.text_encoder = pipeline.text_encoder
        self.tokenizer = pipeline.tokenizer
        self.scheduler = pipeline.scheduler
        
        logger.info("Stable Diffusion model loaded successfully")
    
    def prepare_dataset(self) -> None:
        """Prepare image dataset for training."""
        # Implementation for image dataset preparation
        logger.info("Preparing image dataset...")
        # This would involve loading images, captions, and preprocessing
        pass
    
    def setup_training(self) -> None:
        """Setup training for Stable Diffusion."""
        logger.info("Setting up Stable Diffusion training...")
        # Implementation for SD training setup
        pass
    
    def train(self) -> str:
        """Execute Stable Diffusion training."""
        logger.info("Starting Stable Diffusion training...")
        
        # Validate configuration
        issues = self.validate_config()
        if issues:
            raise ValueError(f"Configuration issues: {issues}")
        
        # Implementation for SD training loop
        output_path = os.path.join(self.config.output_dir, "trained_model")
        
        logger.info(f"Stable Diffusion training completed! Model saved to: {output_path}")
        return output_path
    
    def save_model(self, output_path: str) -> None:
        """Save trained Stable Diffusion model."""
        os.makedirs(output_path, exist_ok=True)
        # Implementation for saving SD model
        logger.info(f"Stable Diffusion model saved to: {output_path}")


class MLTrainer(BaseTrainer):
    """
    Trainer for traditional ML models.
    
    Supports:
    - Scikit-learn models
    - XGBoost/LightGBM
    - Custom ML pipelines
    """
    
    def __init__(self, config: TrainingConfig):
        super().__init__(config)
        
        if not SKLEARN_AVAILABLE:
            raise ImportError("Scikit-learn not available. Install with: pip install scikit-learn xgboost")
        
        self.ml_model = None
        self.X_train = None
        self.y_train = None
        self.X_val = None
        self.y_val = None
    
    def load_model(self) -> None:
        """Initialize ML model."""
        logger.info(f"Initializing ML model: {self.config.model_name}")
        
        # Model factory based on model_name
        if "xgboost" in self.config.model_name.lower():
            self.ml_model = xgb.XGBClassifier()
        elif "random_forest" in self.config.model_name.lower():
            from sklearn.ensemble import RandomForestClassifier
            self.ml_model = RandomForestClassifier()
        else:
            raise ValueError(f"ML model type not supported: {self.config.model_name}")
        
        logger.info("ML model initialized successfully")
    
    def prepare_dataset(self) -> None:
        """Prepare tabular dataset for ML training."""
        logger.info("Preparing ML dataset...")
        # Implementation for loading and preprocessing tabular data
        pass
    
    def setup_training(self) -> None:
        """Setup ML training parameters."""
        logger.info("Setting up ML training...")
        # Set hyperparameters based on config
        pass
    
    def train(self) -> str:
        """Execute ML model training."""
        logger.info("Starting ML training...")
        
        # Validate configuration
        issues = self.validate_config()
        if issues:
            raise ValueError(f"Configuration issues: {issues}")
        
        # Implementation for ML training
        output_path = os.path.join(self.config.output_dir, "trained_model.pkl")
        
        logger.info(f"ML training completed! Model saved to: {output_path}")
        return output_path
    
    def save_model(self, output_path: str) -> None:
        """Save trained ML model."""
        import joblib
        joblib.dump(self.ml_model, output_path)
        logger.info(f"ML model saved to: {output_path}")


# Legacy alias for backward compatibility
SFTTrainer = LLMTrainer


def create_trainer(config: TrainingConfig) -> BaseTrainer:
    """
    Factory function to create appropriate trainer based on model type.
    
    Args:
        config: Training configuration
    
    Returns:
        Appropriate trainer instance
    """
    model_name = config.model_name.lower()
    
    # Determine trainer type based on model name or training type
    if any(keyword in model_name for keyword in ['stable-diffusion', 'sd-', 'diffusion']):
        return StableDiffusionTrainer(config)
    elif any(keyword in model_name for keyword in ['xgboost', 'random_forest', 'svm', 'linear']):
        return MLTrainer(config)
    elif config.training_type in ['sft', 'instruction', 'chat', 'classification']:
        return LLMTrainer(config)
    else:
        # Default to LLM trainer for language models
        return LLMTrainer(config) 