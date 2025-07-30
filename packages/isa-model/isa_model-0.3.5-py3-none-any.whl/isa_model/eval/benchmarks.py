"""
Standard AI Benchmarks for ISA Model Framework

This module provides implementations of standard AI benchmarks:
- MMLU (Massive Multitask Language Understanding)
- HellaSwag (Commonsense Reasoning)
- ARC (AI2 Reasoning Challenge)
- GSM8K (Grade School Math)
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class BenchmarkConfig:
    """Configuration for benchmark evaluation."""
    name: str
    description: str
    num_choices: int = 4
    few_shot_examples: int = 5
    max_samples: Optional[int] = None
    subjects: Optional[List[str]] = None


class BaseBenchmark(ABC):
    """Base class for all benchmarks."""
    
    def __init__(self, config: BenchmarkConfig):
        self.config = config
        self.name = config.name
        self.data = None
    
    @abstractmethod
    def load_data(self, max_samples: Optional[int] = None) -> List[Dict[str, Any]]:
        """Load benchmark data."""
        pass
    
    @abstractmethod
    def evaluate_sample(self, sample: Dict[str, Any], prediction: str) -> bool:
        """Evaluate a single sample."""
        pass
    
    def format_prompt(self, sample: Dict[str, Any], few_shot_examples: Optional[List[Dict[str, Any]]] = None) -> str:
        """Format prompt for the sample."""
        prompt = ""
        
        # Add few-shot examples if provided
        if few_shot_examples:
            for example in few_shot_examples:
                prompt += self._format_single_example(example, include_answer=True) + "\n\n"
        
        # Add the actual question
        prompt += self._format_single_example(sample, include_answer=False)
        
        return prompt
    
    @abstractmethod
    def _format_single_example(self, sample: Dict[str, Any], include_answer: bool = False) -> str:
        """Format a single example."""
        pass


class MMLU(BaseBenchmark):
    """
    MMLU (Massive Multitask Language Understanding) Benchmark
    
    Tests knowledge across 57 subjects including mathematics, history, 
    computer science, law, and more.
    """
    
    def __init__(self, subjects: Optional[List[str]] = None):
        config = BenchmarkConfig(
            name="MMLU",
            description="Massive Multitask Language Understanding",
            num_choices=4,
            few_shot_examples=5,
            subjects=subjects
        )
        super().__init__(config)
        
        # MMLU subjects
        self.all_subjects = [
            "abstract_algebra", "anatomy", "astronomy", "business_ethics",
            "clinical_knowledge", "college_biology", "college_chemistry",
            "college_computer_science", "college_mathematics", "college_medicine",
            "college_physics", "computer_security", "conceptual_physics",
            "econometrics", "electrical_engineering", "elementary_mathematics",
            "formal_logic", "global_facts", "high_school_biology",
            "high_school_chemistry", "high_school_computer_science",
            "high_school_european_history", "high_school_geography",
            "high_school_government_and_politics", "high_school_macroeconomics",
            "high_school_mathematics", "high_school_microeconomics",
            "high_school_physics", "high_school_psychology", "high_school_statistics",
            "high_school_us_history", "high_school_world_history", "human_aging",
            "human_sexuality", "international_law", "jurisprudence",
            "logical_fallacies", "machine_learning", "management", "marketing",
            "medical_genetics", "miscellaneous", "moral_disputes", "moral_scenarios",
            "nutrition", "philosophy", "prehistory", "professional_accounting",
            "professional_law", "professional_medicine", "professional_psychology",
            "public_relations", "security_studies", "sociology", "us_foreign_policy",
            "virology", "world_religions"
        ]
        
        self.subjects = subjects or self.all_subjects[:10]  # Use first 10 subjects by default
    
    def load_data(self, max_samples: Optional[int] = None) -> List[Dict[str, Any]]:
        """Load MMLU data (simplified implementation)."""
        # This is a simplified implementation
        # In practice, you'd load from the actual MMLU dataset
        
        data = []
        
        for subject in self.subjects:
            # Generate sample questions for each subject
            for i in range(min(10, max_samples // len(self.subjects) if max_samples else 10)):
                sample = {
                    "subject": subject,
                    "question": f"Sample {subject} question {i+1}",
                    "choices": [
                        f"Option A for {subject}",
                        f"Option B for {subject}",
                        f"Option C for {subject}",
                        f"Option D for {subject}"
                    ],
                    "answer": "A",  # Simplified
                    "id": f"{subject}_{i}"
                }
                data.append(sample)
        
        if max_samples:
            data = data[:max_samples]
        
        logger.info(f"Loaded {len(data)} MMLU samples across {len(self.subjects)} subjects")
        return data
    
    def evaluate_sample(self, sample: Dict[str, Any], prediction: str) -> bool:
        """Evaluate a single MMLU sample."""
        # Extract the letter choice from prediction
        prediction = prediction.strip().upper()
        
        # Handle various response formats
        if prediction in ["A", "B", "C", "D"]:
            return prediction == sample["answer"]
        elif prediction.startswith("(") and prediction.endswith(")"):
            letter = prediction[1]
            return letter == sample["answer"]
        else:
            # Try to find A, B, C, or D in the response
            for choice in ["A", "B", "C", "D"]:
                if choice in prediction:
                    return choice == sample["answer"]
        
        return False
    
    def _format_single_example(self, sample: Dict[str, Any], include_answer: bool = False) -> str:
        """Format a single MMLU example."""
        prompt = f"Subject: {sample['subject'].replace('_', ' ').title()}\n"
        prompt += f"Question: {sample['question']}\n"
        
        choices = sample['choices']
        for i, choice in enumerate(choices):
            letter = chr(65 + i)  # A, B, C, D
            prompt += f"{letter}. {choice}\n"
        
        if include_answer:
            prompt += f"Answer: {sample['answer']}"
        else:
            prompt += "Answer:"
        
        return prompt


class HellaSwag(BaseBenchmark):
    """
    HellaSwag Benchmark
    
    Tests commonsense reasoning about physical situations.
    """
    
    def __init__(self):
        config = BenchmarkConfig(
            name="HellaSwag",
            description="Commonsense Reasoning about Physical Situations",
            num_choices=4,
            few_shot_examples=10
        )
        super().__init__(config)
    
    def load_data(self, max_samples: Optional[int] = None) -> List[Dict[str, Any]]:
        """Load HellaSwag data (simplified implementation)."""
        # This is a simplified implementation
        # In practice, you'd load from the actual HellaSwag dataset
        
        data = []
        
        sample_contexts = [
            "A person is washing dishes in the kitchen",
            "Someone is riding a bicycle down a hill",
            "A chef is preparing ingredients for cooking",
            "A student is taking notes in class",
            "A gardener is planting flowers"
        ]
        
        for i, context in enumerate(sample_contexts):
            if max_samples and i >= max_samples:
                break
                
            sample = {
                "context": context,
                "question": "What happens next?",
                "choices": [
                    f"They continue with the logical next step for scenario {i+1}",
                    f"They do something completely unrelated to scenario {i+1}",
                    f"They stop and do something random in scenario {i+1}",
                    f"They repeat the same action in scenario {i+1}"
                ],
                "answer": "A",  # First choice is usually most logical
                "id": f"hellaswag_{i}"
            }
            data.append(sample)
        
        logger.info(f"Loaded {len(data)} HellaSwag samples")
        return data
    
    def evaluate_sample(self, sample: Dict[str, Any], prediction: str) -> bool:
        """Evaluate a single HellaSwag sample."""
        prediction = prediction.strip().upper()
        
        if prediction in ["A", "B", "C", "D"]:
            return prediction == sample["answer"]
        
        # Try to extract choice from longer response
        for choice in ["A", "B", "C", "D"]:
            if choice in prediction:
                return choice == sample["answer"]
        
        return False
    
    def _format_single_example(self, sample: Dict[str, Any], include_answer: bool = False) -> str:
        """Format a single HellaSwag example."""
        prompt = f"Context: {sample['context']}\n"
        prompt += f"Question: {sample['question']}\n"
        
        choices = sample['choices']
        for i, choice in enumerate(choices):
            letter = chr(65 + i)  # A, B, C, D
            prompt += f"{letter}. {choice}\n"
        
        if include_answer:
            prompt += f"Answer: {sample['answer']}"
        else:
            prompt += "Answer:"
        
        return prompt


class ARC(BaseBenchmark):
    """
    ARC (AI2 Reasoning Challenge) Benchmark
    
    Tests scientific reasoning with grade-school level science questions.
    """
    
    def __init__(self, challenge_set: str = "easy"):
        config = BenchmarkConfig(
            name=f"ARC-{challenge_set}",
            description=f"AI2 Reasoning Challenge ({challenge_set})",
            num_choices=4,
            few_shot_examples=25
        )
        super().__init__(config)
        self.challenge_set = challenge_set  # "easy" or "challenge"
    
    def load_data(self, max_samples: Optional[int] = None) -> List[Dict[str, Any]]:
        """Load ARC data (simplified implementation)."""
        # This is a simplified implementation
        # In practice, you'd load from the actual ARC dataset
        
        data = []
        
        sample_questions = [
            {
                "question": "What happens to water when it freezes?",
                "choices": ["It becomes ice", "It becomes gas", "It disappears", "It becomes hot"],
                "answer": "A"
            },
            {
                "question": "Which planet is closest to the Sun?",
                "choices": ["Earth", "Mars", "Mercury", "Venus"],
                "answer": "C"
            },
            {
                "question": "What do plants need to make their own food?",
                "choices": ["Sunlight and water", "Only water", "Only sunlight", "Soil only"],
                "answer": "A"
            },
            {
                "question": "What is the main gas in Earth's atmosphere?",
                "choices": ["Oxygen", "Carbon dioxide", "Nitrogen", "Hydrogen"],
                "answer": "C"
            },
            {
                "question": "How many legs does a spider have?",
                "choices": ["6", "8", "10", "12"],
                "answer": "B"
            }
        ]
        
        for i, q in enumerate(sample_questions):
            if max_samples and i >= max_samples:
                break
                
            sample = {
                "question": q["question"],
                "choices": q["choices"],
                "answer": q["answer"],
                "challenge_set": self.challenge_set,
                "id": f"arc_{self.challenge_set}_{i}"
            }
            data.append(sample)
        
        logger.info(f"Loaded {len(data)} ARC-{self.challenge_set} samples")
        return data
    
    def evaluate_sample(self, sample: Dict[str, Any], prediction: str) -> bool:
        """Evaluate a single ARC sample."""
        prediction = prediction.strip().upper()
        
        if prediction in ["A", "B", "C", "D"]:
            return prediction == sample["answer"]
        
        # Try to extract choice from longer response
        for choice in ["A", "B", "C", "D"]:
            if choice in prediction:
                return choice == sample["answer"]
        
        return False
    
    def _format_single_example(self, sample: Dict[str, Any], include_answer: bool = False) -> str:
        """Format a single ARC example."""
        prompt = f"Question: {sample['question']}\n"
        
        choices = sample['choices']
        for i, choice in enumerate(choices):
            letter = chr(65 + i)  # A, B, C, D
            prompt += f"{letter}. {choice}\n"
        
        if include_answer:
            prompt += f"Answer: {sample['answer']}"
        else:
            prompt += "Answer:"
        
        return prompt


class GSM8K(BaseBenchmark):
    """
    GSM8K Benchmark
    
    Tests mathematical reasoning with grade school math word problems.
    """
    
    def __init__(self):
        config = BenchmarkConfig(
            name="GSM8K",
            description="Grade School Math 8K",
            num_choices=1,  # Open-ended numerical answers
            few_shot_examples=8
        )
        super().__init__(config)
    
    def load_data(self, max_samples: Optional[int] = None) -> List[Dict[str, Any]]:
        """Load GSM8K data (simplified implementation)."""
        # This is a simplified implementation
        # In practice, you'd load from the actual GSM8K dataset
        
        data = []
        
        sample_problems = [
            {
                "question": "Janet has 12 apples. She gives 3 apples to her friend and eats 2 apples. How many apples does Janet have left?",
                "answer": "7"
            },
            {
                "question": "A school has 24 students in each class. If there are 5 classes, how many students are there in total?",
                "answer": "120"
            },
            {
                "question": "Tom buys 4 books for $8 each. How much money does Tom spend in total?",
                "answer": "32"
            },
            {
                "question": "Sarah has 36 stickers. She wants to put them equally into 6 albums. How many stickers will be in each album?",
                "answer": "6"
            },
            {
                "question": "A rectangle has a length of 15 cm and a width of 8 cm. What is the area of the rectangle?",
                "answer": "120"
            }
        ]
        
        for i, problem in enumerate(sample_problems):
            if max_samples and i >= max_samples:
                break
                
            sample = {
                "question": problem["question"],
                "answer": problem["answer"],
                "id": f"gsm8k_{i}"
            }
            data.append(sample)
        
        logger.info(f"Loaded {len(data)} GSM8K samples")
        return data
    
    def evaluate_sample(self, sample: Dict[str, Any], prediction: str) -> bool:
        """Evaluate a single GSM8K sample."""
        # Extract numerical answer from prediction
        prediction = prediction.strip()
        
        # Try to find the numerical answer
        import re
        numbers = re.findall(r'\d+', prediction)
        
        if numbers:
            # Take the last number found (often the final answer)
            predicted_answer = numbers[-1]
            return predicted_answer == sample["answer"]
        
        return False
    
    def _format_single_example(self, sample: Dict[str, Any], include_answer: bool = False) -> str:
        """Format a single GSM8K example."""
        prompt = f"Problem: {sample['question']}\n"
        
        if include_answer:
            prompt += f"Answer: {sample['answer']}"
        else:
            prompt += "Answer:"
        
        return prompt


# Convenience functions for creating benchmark instances
def create_mmlu_benchmark(subjects: Optional[List[str]] = None) -> MMLU:
    """Create MMLU benchmark instance."""
    return MMLU(subjects=subjects)


def create_hellaswag_benchmark() -> HellaSwag:
    """Create HellaSwag benchmark instance."""
    return HellaSwag()


def create_arc_benchmark(challenge_set: str = "easy") -> ARC:
    """Create ARC benchmark instance."""
    return ARC(challenge_set=challenge_set)


def create_gsm8k_benchmark() -> GSM8K:
    """Create GSM8K benchmark instance."""
    return GSM8K() 