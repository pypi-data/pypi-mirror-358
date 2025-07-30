"""
Dataset Management

Handles loading and preprocessing of datasets for training.
"""

import json
import logging
from typing import Optional, Tuple, Dict, Any, List, Union
from pathlib import Path
from datasets import Dataset, load_dataset

logger = logging.getLogger(__name__)


class DatasetManager:
    """Manages dataset loading and preprocessing."""
    
    def __init__(self, tokenizer, max_length: int = 1024):
        """
        Initialize dataset manager.
        
        Args:
            tokenizer: HuggingFace tokenizer
            max_length: Maximum sequence length
        """
        self.tokenizer = tokenizer
        self.max_length = max_length
        
    def prepare_dataset(
        self,
        dataset_path: str,
        dataset_format: str = "alpaca",
        validation_split: float = 0.1
    ) -> Tuple[Dataset, Optional[Dataset]]:
        """
        Prepare training and validation datasets.
        
        Args:
            dataset_path: Path to dataset file or HuggingFace dataset name
            dataset_format: Format of the dataset (alpaca, sharegpt, custom)
            validation_split: Fraction of data to use for validation
            
        Returns:
            Tuple of (train_dataset, eval_dataset)
        """
        logger.info(f"Preparing dataset: {dataset_path}")
        
        # Load raw dataset
        raw_dataset = self._load_raw_dataset(dataset_path)
        
        # Convert to training format
        if dataset_format == "alpaca":
            processed_dataset = self._process_alpaca_format(raw_dataset)
        elif dataset_format == "sharegpt":
            processed_dataset = self._process_sharegpt_format(raw_dataset)
        else:
            processed_dataset = self._process_custom_format(raw_dataset)
        
        # Tokenize dataset
        tokenized_dataset = processed_dataset.map(
            self._tokenize_function,
            batched=True,
            remove_columns=processed_dataset.column_names
        )
        
        # Split into train/eval
        if validation_split > 0:
            split_dataset = tokenized_dataset.train_test_split(
                test_size=validation_split,
                seed=42
            )
            train_dataset = split_dataset["train"]
            eval_dataset = split_dataset["test"]
        else:
            train_dataset = tokenized_dataset
            eval_dataset = None
        
        logger.info(f"Dataset prepared: {len(train_dataset)} training samples")
        if eval_dataset:
            logger.info(f"Validation samples: {len(eval_dataset)}")
        
        return train_dataset, eval_dataset
    
    def _load_raw_dataset(self, dataset_path: str) -> Dataset:
        """Load raw dataset from file or HuggingFace."""
        try:
            # Check if it's a local file
            if Path(dataset_path).exists():
                logger.info(f"Loading local dataset: {dataset_path}")
                
                if dataset_path.endswith('.json'):
                    with open(dataset_path, 'r') as f:
                        data = json.load(f)
                    return Dataset.from_list(data)
                elif dataset_path.endswith('.jsonl'):
                    data = []
                    with open(dataset_path, 'r') as f:
                        for line in f:
                            data.append(json.loads(line))
                    return Dataset.from_list(data)
                else:
                    raise ValueError(f"Unsupported file format: {dataset_path}")
            
            else:
                # Try loading from HuggingFace Hub
                logger.info(f"Loading HuggingFace dataset: {dataset_path}")
                dataset = load_dataset(dataset_path, split="train")
                return dataset
                
        except Exception as e:
            logger.error(f"Failed to load dataset: {e}")
            raise
    
    def _process_alpaca_format(self, dataset: Dataset) -> Dataset:
        """Process Alpaca format dataset."""
        def format_alpaca(example):
            instruction = example.get("instruction", "")
            input_text = example.get("input", "")
            output = example.get("output", "")
            
            # Format prompt
            if input_text:
                prompt = f"### Instruction:\n{instruction}\n\n### Input:\n{input_text}\n\n### Response:\n"
            else:
                prompt = f"### Instruction:\n{instruction}\n\n### Response:\n"
            
            # Combine prompt and response
            text = prompt + output
            
            return {"text": text}
        
        return dataset.map(format_alpaca)
    
    def _process_sharegpt_format(self, dataset: Dataset) -> Dataset:
        """Process ShareGPT format dataset."""
        def format_sharegpt(example):
            conversations = example.get("conversations", [])
            
            text = ""
            for conv in conversations:
                role = conv.get("from", "")
                content = conv.get("value", "")
                
                if role == "human":
                    text += f"### Human:\n{content}\n\n"
                elif role == "gpt":
                    text += f"### Assistant:\n{content}\n\n"
            
            return {"text": text.strip()}
        
        return dataset.map(format_sharegpt)
    
    def _process_custom_format(self, dataset: Dataset) -> Dataset:
        """Process custom format dataset."""
        # Assume the dataset already has a 'text' column
        if "text" not in dataset.column_names:
            raise ValueError("Custom format dataset must have a 'text' column")
        
        return dataset
    
    def _tokenize_function(self, examples):
        """Tokenize examples for training."""
        # Tokenize inputs
        tokenized = self.tokenizer(
            examples["text"],
            truncation=True,
            padding=False,
            max_length=self.max_length,
            return_tensors=None,
        )
        
        # For language modeling, labels are the same as input_ids
        tokenized["labels"] = tokenized["input_ids"].copy()
        
        return tokenized
    
    @staticmethod
    def convert_hf_dataset_to_alpaca(
        dataset_name: str,
        output_path: str,
        instruction_column: str = "instruction",
        input_column: str = "input",
        output_column: str = "output"
    ) -> str:
        """
        Convert a HuggingFace dataset to Alpaca format.
        
        Args:
            dataset_name: Name of the HuggingFace dataset
            output_path: Path to save the converted dataset
            instruction_column: Column name for instructions
            input_column: Column name for inputs
            output_column: Column name for outputs
            
        Returns:
            Path to the saved dataset
        """
        logger.info(f"Converting {dataset_name} to Alpaca format")
        
        # Load dataset
        dataset = load_dataset(dataset_name, split="train")
        
        # Convert to Alpaca format
        alpaca_data = []
        for example in dataset:
            alpaca_example = {
                "instruction": example.get(instruction_column, ""),
                "input": example.get(input_column, ""),
                "output": example.get(output_column, "")
            }
            alpaca_data.append(alpaca_example)
        
        # Save to file
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(alpaca_data, f, indent=2)
        
        logger.info(f"Dataset converted and saved to: {output_path}")
        return str(output_path) 