"""
Training Utilities

Helper functions and utilities for training operations.
"""

import os
import json
import logging
import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)


class TrainingUtils:
    """Utility functions for training operations."""
    
    @staticmethod
    def generate_output_dir(model_name: str, training_type: str, base_dir: str = "training_outputs") -> str:
        """Generate a timestamped output directory."""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_model_name = model_name.replace("/", "_").replace(":", "_")
        output_dir = os.path.join(base_dir, f"{safe_model_name}_{training_type}_{timestamp}")
        return output_dir
    
    @staticmethod
    def save_training_args(args: Dict[str, Any], output_dir: str) -> None:
        """Save training arguments to file."""
        args_path = Path(output_dir) / "training_args.json"
        args_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(args_path, 'w') as f:
            json.dump(args, f, indent=2, default=str)
        
        logger.info(f"Training arguments saved to: {args_path}")
    
    @staticmethod
    def load_training_args(output_dir: str) -> Dict[str, Any]:
        """Load training arguments from file."""
        args_path = Path(output_dir) / "training_args.json"
        
        if not args_path.exists():
            raise FileNotFoundError(f"Training args not found: {args_path}")
        
        with open(args_path, 'r') as f:
            args = json.load(f)
        
        return args
    
    @staticmethod
    def get_model_info(model_name: str) -> Dict[str, Any]:
        """Get information about a model."""
        try:
            from transformers import AutoConfig
            
            config = AutoConfig.from_pretrained(model_name, trust_remote_code=True)
            
            model_info = {
                "model_name": model_name,
                "model_type": config.model_type,
                "vocab_size": getattr(config, 'vocab_size', None),
                "hidden_size": getattr(config, 'hidden_size', None),
                "num_layers": getattr(config, 'num_hidden_layers', None),
                "num_attention_heads": getattr(config, 'num_attention_heads', None),
                "max_position_embeddings": getattr(config, 'max_position_embeddings', None),
            }
            
            return model_info
            
        except Exception as e:
            logger.warning(f"Could not get model info for {model_name}: {e}")
            return {"model_name": model_name, "error": str(e)}
    
    @staticmethod
    def estimate_memory_usage(
        model_name: str,
        batch_size: int = 1,
        max_length: int = 1024,
        use_lora: bool = True
    ) -> Dict[str, Any]:
        """Estimate memory usage for training."""
        try:
            model_info = TrainingUtils.get_model_info(model_name)
            
            # Rough estimation based on model parameters
            hidden_size = model_info.get('hidden_size', 4096)
            num_layers = model_info.get('num_layers', 32)
            vocab_size = model_info.get('vocab_size', 32000)
            
            # Estimate model parameters (in millions)
            param_count = (hidden_size * hidden_size * 12 * num_layers + vocab_size * hidden_size) / 1e6
            
            # Base memory for model (assuming fp16)
            model_memory_gb = param_count * 2 / 1024  # 2 bytes per parameter
            
            # Training memory overhead (gradients, optimizer states, activations)
            if use_lora:
                training_overhead = 2.0  # LoRA reduces memory usage significantly
            else:
                training_overhead = 4.0  # Full fine-tuning needs more memory
            
            # Batch and sequence length impact
            sequence_memory = batch_size * max_length * hidden_size * 2 / (1024**3)  # Activation memory
            
            total_memory_gb = model_memory_gb * training_overhead + sequence_memory
            
            return {
                "estimated_params_millions": param_count,
                "model_memory_gb": model_memory_gb,
                "total_training_memory_gb": total_memory_gb,
                "recommended_gpu": TrainingUtils._recommend_gpu(total_memory_gb),
                "use_lora": use_lora,
                "batch_size": batch_size,
                "max_length": max_length
            }
            
        except Exception as e:
            logger.warning(f"Could not estimate memory usage: {e}")
            return {"error": str(e)}
    
    @staticmethod
    def _recommend_gpu(memory_gb: float) -> str:
        """Recommend GPU based on memory requirements."""
        if memory_gb <= 8:
            return "RTX 3080/4070 (8-12GB)"
        elif memory_gb <= 16:
            return "RTX 4080/4090 (16GB)"
        elif memory_gb <= 24:
            return "RTX A6000/4090 (24GB)"
        elif memory_gb <= 40:
            return "A100 40GB"
        elif memory_gb <= 80:
            return "A100 80GB"
        else:
            return "Multiple A100 80GB (Multi-GPU required)"
    
    @staticmethod
    def validate_training_config(config: Dict[str, Any]) -> List[str]:
        """Validate training configuration and return any issues."""
        issues = []
        
        # Check required fields
        required_fields = ["model_name", "output_dir"]
        for field in required_fields:
            if field not in config:
                issues.append(f"Missing required field: {field}")
        
        # Check batch size
        if config.get("batch_size", 0) <= 0:
            issues.append("batch_size must be positive")
        
        # Check learning rate
        lr = config.get("learning_rate", 0)
        if lr <= 0 or lr > 1:
            issues.append("learning_rate should be between 0 and 1")
        
        # Check epochs
        if config.get("num_epochs", 0) <= 0:
            issues.append("num_epochs must be positive")
        
        # Check LoRA config
        if config.get("use_lora", False):
            lora_rank = config.get("lora_rank", 8)
            if lora_rank <= 0 or lora_rank > 256:
                issues.append("lora_rank should be between 1 and 256")
        
        return issues
    
    @staticmethod
    def format_training_summary(
        config: Dict[str, Any],
        model_info: Dict[str, Any],
        memory_estimate: Dict[str, Any]
    ) -> str:
        """Format a training summary for display."""
        summary = []
        summary.append("=" * 60)
        summary.append("TRAINING CONFIGURATION SUMMARY")
        summary.append("=" * 60)
        
        # Model information
        summary.append(f"Model: {config.get('model_name', 'Unknown')}")
        summary.append(f"Model Type: {model_info.get('model_type', 'Unknown')}")
        summary.append(f"Parameters: ~{memory_estimate.get('estimated_params_millions', 0):.1f}M")
        
        # Training configuration
        summary.append(f"\nTraining Configuration:")
        summary.append(f"  Training Type: {config.get('training_type', 'sft')}")
        summary.append(f"  Epochs: {config.get('num_epochs', 3)}")
        summary.append(f"  Batch Size: {config.get('batch_size', 4)}")
        summary.append(f"  Learning Rate: {config.get('learning_rate', 2e-5)}")
        summary.append(f"  Max Length: {config.get('max_length', 1024)}")
        
        # LoRA configuration
        if config.get('use_lora', True):
            summary.append(f"\nLoRA Configuration:")
            summary.append(f"  LoRA Rank: {config.get('lora_rank', 8)}")
            summary.append(f"  LoRA Alpha: {config.get('lora_alpha', 16)}")
            summary.append(f"  LoRA Dropout: {config.get('lora_dropout', 0.05)}")
        
        # Memory estimation
        summary.append(f"\nMemory Estimation:")
        summary.append(f"  Estimated Memory: ~{memory_estimate.get('total_training_memory_gb', 0):.1f}GB")
        summary.append(f"  Recommended GPU: {memory_estimate.get('recommended_gpu', 'Unknown')}")
        
        # Output
        summary.append(f"\nOutput Directory: {config.get('output_dir', 'Unknown')}")
        
        summary.append("=" * 60)
        
        return "\n".join(summary) 