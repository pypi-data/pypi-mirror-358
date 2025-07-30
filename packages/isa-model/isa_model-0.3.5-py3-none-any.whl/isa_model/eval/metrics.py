"""
Evaluation Metrics for ISA Model Framework

This module provides various metrics for evaluating AI models:
- LLM metrics: perplexity, BLEU, ROUGE, accuracy, etc.
- Image metrics: FID, IS, LPIPS, etc.
- Custom metrics and benchmark runners
"""

import os
import json
import logging
import numpy as np
from typing import Dict, List, Any, Optional, Union
from enum import Enum
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class MetricType(str, Enum):
    """Types of evaluation metrics."""
    PERPLEXITY = "perplexity"
    BLEU = "bleu"
    ROUGE = "rouge"
    ACCURACY = "accuracy"
    F1_SCORE = "f1"
    DIVERSITY = "diversity"
    COHERENCE = "coherence"
    FLUENCY = "fluency"
    FID = "fid"
    IS = "is"
    LPIPS = "lpips"


class BaseMetric(ABC):
    """Base class for all metrics."""
    
    @abstractmethod
    def compute(self, predictions: List[str], references: List[str] = None, **kwargs) -> Dict[str, float]:
        """Compute the metric."""
        pass


class LLMMetrics:
    """
    Metrics calculator for Language Models.
    
    Supports various metrics including:
    - Perplexity
    - BLEU score
    - ROUGE score
    - Accuracy
    - F1 score
    - Generation quality metrics
    """
    
    def __init__(self):
        self.available_metrics = [
            MetricType.PERPLEXITY,
            MetricType.BLEU,
            MetricType.ROUGE,
            MetricType.ACCURACY,
            MetricType.F1_SCORE,
            MetricType.DIVERSITY,
            MetricType.COHERENCE,
            MetricType.FLUENCY
        ]
    
    def evaluate(
        self,
        model_path: str,
        dataset: List[Dict[str, Any]],
        metrics: List[str],
        batch_size: int = 8,
        provider: str = "ollama",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Evaluate LLM on dataset with specified metrics.
        
        Args:
            model_path: Path to the model
            dataset: Evaluation dataset
            metrics: List of metrics to compute
            batch_size: Batch size for evaluation
            provider: Model provider
            **kwargs: Additional parameters
            
        Returns:
            Dictionary with metric results
        """
        results = {
            "model_path": model_path,
            "num_samples": len(dataset),
            "metrics": {}
        }
        
        # Generate predictions
        predictions, references = self._generate_predictions(
            model_path, dataset, batch_size, provider, **kwargs
        )
        
        # Compute each metric
        for metric in metrics:
            try:
                if metric == MetricType.PERPLEXITY:
                    score = self._compute_perplexity(predictions, references)
                elif metric == MetricType.BLEU:
                    score = self._compute_bleu(predictions, references)
                elif metric == MetricType.ROUGE:
                    score = self._compute_rouge(predictions, references)
                elif metric == MetricType.ACCURACY:
                    score = self._compute_accuracy(predictions, references)
                elif metric == MetricType.F1_SCORE:
                    score = self._compute_f1(predictions, references)
                elif metric == MetricType.DIVERSITY:
                    score = self._compute_diversity(predictions)
                elif metric == MetricType.COHERENCE:
                    score = self._compute_coherence(predictions)
                elif metric == MetricType.FLUENCY:
                    score = self._compute_fluency(predictions)
                else:
                    logger.warning(f"Unknown metric: {metric}")
                    continue
                
                results["metrics"][metric] = score
                logger.info(f"Computed {metric}: {score}")
                
            except Exception as e:
                logger.error(f"Failed to compute {metric}: {e}")
                results["metrics"][metric] = {"error": str(e)}
        
        return results
    
    def evaluate_generation(
        self,
        model_path: str,
        prompts: List[str],
        reference_texts: List[str] = None,
        metrics: List[str] = None,
        provider: str = "ollama",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Evaluate text generation quality.
        
        Args:
            model_path: Path to the model
            prompts: Input prompts
            reference_texts: Reference texts (optional)
            metrics: Metrics to compute
            provider: Model provider
            **kwargs: Additional parameters
            
        Returns:
            Generation evaluation results
        """
        if metrics is None:
            metrics = [MetricType.DIVERSITY, MetricType.COHERENCE, MetricType.FLUENCY]
        
        # Generate texts
        generated_texts = self._generate_texts(model_path, prompts, provider, **kwargs)
        
        results = {
            "model_path": model_path,
            "num_prompts": len(prompts),
            "metrics": {}
        }
        
        # Compute metrics
        for metric in metrics:
            try:
                if metric == MetricType.DIVERSITY:
                    score = self._compute_diversity(generated_texts)
                elif metric == MetricType.COHERENCE:
                    score = self._compute_coherence(generated_texts)
                elif metric == MetricType.FLUENCY:
                    score = self._compute_fluency(generated_texts)
                elif metric == MetricType.BLEU and reference_texts:
                    score = self._compute_bleu(generated_texts, reference_texts)
                elif metric == MetricType.ROUGE and reference_texts:
                    score = self._compute_rouge(generated_texts, reference_texts)
                else:
                    continue
                
                results["metrics"][metric] = score
                
            except Exception as e:
                logger.error(f"Failed to compute {metric}: {e}")
                results["metrics"][metric] = {"error": str(e)}
        
        return results
    
    def _generate_predictions(
        self,
        model_path: str,
        dataset: List[Dict[str, Any]],
        batch_size: int,
        provider: str,
        **kwargs
    ) -> tuple:
        """Generate predictions from model."""
        predictions = []
        references = []
        
        # This is a simplified implementation
        # In practice, you'd use the actual model inference
        for item in dataset:
            if isinstance(item, dict):
                if "input" in item and "output" in item:
                    # Simulate prediction (replace with actual model inference)
                    predictions.append(f"Generated response for: {item['input']}")
                    references.append(item["output"])
                elif "prompt" in item and "response" in item:
                    predictions.append(f"Generated response for: {item['prompt']}")
                    references.append(item["response"])
        
        logger.info(f"Generated {len(predictions)} predictions")
        return predictions, references
    
    def _generate_texts(
        self,
        model_path: str,
        prompts: List[str],
        provider: str,
        **kwargs
    ) -> List[str]:
        """Generate texts from prompts."""
        # Simplified implementation - replace with actual model inference
        generated_texts = []
        for prompt in prompts:
            generated_texts.append(f"Generated response for: {prompt}")
        
        return generated_texts
    
    def _compute_perplexity(self, predictions: List[str], references: List[str]) -> Dict[str, float]:
        """Compute perplexity score (simplified implementation)."""
        # This is a placeholder - actual perplexity requires model probabilities
        return {
            "perplexity": np.random.uniform(10, 100),  # Placeholder
            "log_perplexity": np.random.uniform(2, 5)
        }
    
    def _compute_bleu(self, predictions: List[str], references: List[str]) -> Dict[str, float]:
        """Compute BLEU score (simplified implementation)."""
        try:
            # Placeholder implementation - use actual BLEU calculation
            # from nltk.translate.bleu_score import sentence_bleu
            scores = []
            for pred, ref in zip(predictions, references):
                # Simplified BLEU calculation
                pred_words = pred.lower().split()
                ref_words = ref.lower().split()
                
                # Simple overlap calculation (not actual BLEU)
                overlap = len(set(pred_words) & set(ref_words))
                total = len(set(pred_words) | set(ref_words))
                
                if total > 0:
                    scores.append(overlap / total)
                else:
                    scores.append(0.0)
            
            return {
                "bleu": np.mean(scores),
                "bleu_std": np.std(scores)
            }
        except Exception as e:
            logger.error(f"BLEU computation failed: {e}")
            return {"bleu": 0.0, "error": str(e)}
    
    def _compute_rouge(self, predictions: List[str], references: List[str]) -> Dict[str, float]:
        """Compute ROUGE score (simplified implementation)."""
        try:
            rouge_1_scores = []
            rouge_l_scores = []
            
            for pred, ref in zip(predictions, references):
                pred_words = set(pred.lower().split())
                ref_words = set(ref.lower().split())
                
                # ROUGE-1 (unigram overlap)
                if len(ref_words) > 0:
                    rouge_1 = len(pred_words & ref_words) / len(ref_words)
                    rouge_1_scores.append(rouge_1)
                
                # Simplified ROUGE-L (longest common subsequence)
                rouge_l = len(pred_words & ref_words) / max(len(pred_words), len(ref_words), 1)
                rouge_l_scores.append(rouge_l)
            
            return {
                "rouge_1": np.mean(rouge_1_scores),
                "rouge_l": np.mean(rouge_l_scores),
                "rouge_1_std": np.std(rouge_1_scores),
                "rouge_l_std": np.std(rouge_l_scores)
            }
        except Exception as e:
            logger.error(f"ROUGE computation failed: {e}")
            return {"rouge_1": 0.0, "rouge_l": 0.0, "error": str(e)}
    
    def _compute_accuracy(self, predictions: List[str], references: List[str]) -> Dict[str, float]:
        """Compute accuracy score."""
        try:
            correct = 0
            total = len(predictions)
            
            for pred, ref in zip(predictions, references):
                if pred.strip().lower() == ref.strip().lower():
                    correct += 1
            
            accuracy = correct / total if total > 0 else 0.0
            
            return {
                "accuracy": accuracy,
                "correct": correct,
                "total": total
            }
        except Exception as e:
            logger.error(f"Accuracy computation failed: {e}")
            return {"accuracy": 0.0, "error": str(e)}
    
    def _compute_f1(self, predictions: List[str], references: List[str]) -> Dict[str, float]:
        """Compute F1 score (simplified implementation)."""
        try:
            f1_scores = []
            
            for pred, ref in zip(predictions, references):
                pred_words = set(pred.lower().split())
                ref_words = set(ref.lower().split())
                
                if len(pred_words) == 0 and len(ref_words) == 0:
                    f1_scores.append(1.0)
                elif len(pred_words) == 0 or len(ref_words) == 0:
                    f1_scores.append(0.0)
                else:
                    intersection = len(pred_words & ref_words)
                    precision = intersection / len(pred_words)
                    recall = intersection / len(ref_words)
                    
                    if precision + recall > 0:
                        f1 = 2 * (precision * recall) / (precision + recall)
                        f1_scores.append(f1)
                    else:
                        f1_scores.append(0.0)
            
            return {
                "f1": np.mean(f1_scores),
                "f1_std": np.std(f1_scores)
            }
        except Exception as e:
            logger.error(f"F1 computation failed: {e}")
            return {"f1": 0.0, "error": str(e)}
    
    def _compute_diversity(self, texts: List[str]) -> Dict[str, float]:
        """Compute diversity metrics."""
        try:
            # Distinct-1 and Distinct-2
            all_unigrams = []
            all_bigrams = []
            
            for text in texts:
                words = text.lower().split()
                all_unigrams.extend(words)
                
                # Create bigrams
                for i in range(len(words) - 1):
                    all_bigrams.append((words[i], words[i + 1]))
            
            distinct_1 = len(set(all_unigrams)) / len(all_unigrams) if all_unigrams else 0
            distinct_2 = len(set(all_bigrams)) / len(all_bigrams) if all_bigrams else 0
            
            return {
                "distinct_1": distinct_1,
                "distinct_2": distinct_2,
                "vocab_size": len(set(all_unigrams))
            }
        except Exception as e:
            logger.error(f"Diversity computation failed: {e}")
            return {"distinct_1": 0.0, "distinct_2": 0.0, "error": str(e)}
    
    def _compute_coherence(self, texts: List[str]) -> Dict[str, float]:
        """Compute coherence score (simplified implementation)."""
        try:
            # Simplified coherence based on sentence length consistency
            coherence_scores = []
            
            for text in texts:
                sentences = text.split('.')
                if len(sentences) > 1:
                    lengths = [len(s.split()) for s in sentences if s.strip()]
                    if lengths:
                        # Coherence as inverse of length variance
                        coherence = 1.0 / (1.0 + np.var(lengths))
                        coherence_scores.append(coherence)
                    else:
                        coherence_scores.append(0.5)
                else:
                    coherence_scores.append(0.5)
            
            return {
                "coherence": np.mean(coherence_scores),
                "coherence_std": np.std(coherence_scores)
            }
        except Exception as e:
            logger.error(f"Coherence computation failed: {e}")
            return {"coherence": 0.5, "error": str(e)}
    
    def _compute_fluency(self, texts: List[str]) -> Dict[str, float]:
        """Compute fluency score (simplified implementation)."""
        try:
            fluency_scores = []
            
            for text in texts:
                # Simplified fluency based on word count and sentence structure
                words = text.split()
                sentences = text.split('.')
                
                if len(words) > 0 and len(sentences) > 0:
                    avg_words_per_sentence = len(words) / len(sentences)
                    # Fluency based on reasonable sentence length (5-20 words)
                    if 5 <= avg_words_per_sentence <= 20:
                        fluency = 1.0
                    else:
                        fluency = max(0.0, 1.0 - abs(avg_words_per_sentence - 12.5) / 12.5)
                    
                    fluency_scores.append(fluency)
                else:
                    fluency_scores.append(0.0)
            
            return {
                "fluency": np.mean(fluency_scores),
                "fluency_std": np.std(fluency_scores)
            }
        except Exception as e:
            logger.error(f"Fluency computation failed: {e}")
            return {"fluency": 0.0, "error": str(e)}


class ImageMetrics:
    """
    Metrics calculator for Image Generation Models.
    
    Supports metrics including:
    - FID (Fréchet Inception Distance)
    - IS (Inception Score)
    - LPIPS (Learned Perceptual Image Patch Similarity)
    """
    
    def __init__(self):
        self.available_metrics = [
            MetricType.FID,
            MetricType.IS,
            MetricType.LPIPS
        ]
    
    def evaluate(
        self,
        model_path: str,
        test_images_dir: str,
        reference_images_dir: Optional[str] = None,
        metrics: List[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Evaluate image generation model.
        
        Args:
            model_path: Path to the image model
            test_images_dir: Directory with test images
            reference_images_dir: Directory with reference images
            metrics: Metrics to compute
            **kwargs: Additional parameters
            
        Returns:
            Image evaluation results
        """
        if metrics is None:
            metrics = [MetricType.FID, MetricType.IS]
        
        results = {
            "model_path": model_path,
            "test_images_dir": test_images_dir,
            "reference_images_dir": reference_images_dir,
            "metrics": {}
        }
        
        for metric in metrics:
            try:
                if metric == MetricType.FID:
                    score = self._compute_fid(test_images_dir, reference_images_dir)
                elif metric == MetricType.IS:
                    score = self._compute_is(test_images_dir)
                elif metric == MetricType.LPIPS:
                    score = self._compute_lpips(test_images_dir, reference_images_dir)
                else:
                    logger.warning(f"Unknown image metric: {metric}")
                    continue
                
                results["metrics"][metric] = score
                logger.info(f"Computed {metric}: {score}")
                
            except Exception as e:
                logger.error(f"Failed to compute {metric}: {e}")
                results["metrics"][metric] = {"error": str(e)}
        
        return results
    
    def _compute_fid(self, test_dir: str, reference_dir: Optional[str]) -> Dict[str, float]:
        """Compute FID score (placeholder implementation)."""
        # This is a placeholder - actual FID requires complex neural network computations
        logger.warning("FID computation not fully implemented - returning placeholder")
        return {
            "fid": np.random.uniform(20, 100),  # Placeholder
            "note": "Placeholder implementation"
        }
    
    def _compute_is(self, images_dir: str) -> Dict[str, float]:
        """Compute Inception Score (placeholder implementation)."""
        # This is a placeholder - actual IS requires Inception network
        logger.warning("IS computation not fully implemented - returning placeholder")
        return {
            "is_mean": np.random.uniform(2, 10),  # Placeholder
            "is_std": np.random.uniform(0.1, 1.0),
            "note": "Placeholder implementation"
        }
    
    def _compute_lpips(self, test_dir: str, reference_dir: Optional[str]) -> Dict[str, float]:
        """Compute LPIPS score (placeholder implementation)."""
        # This is a placeholder - actual LPIPS requires perceptual loss networks
        logger.warning("LPIPS computation not fully implemented - returning placeholder")
        return {
            "lpips": np.random.uniform(0.1, 0.8),  # Placeholder
            "note": "Placeholder implementation"
        }


class BenchmarkRunner:
    """
    Runner for standard AI benchmarks.
    
    Supports running various benchmarks and collecting results.
    """
    
    def __init__(self):
        self.supported_benchmarks = ["mmlu", "hellaswag", "arc", "gsm8k"]
    
    def run(
        self,
        benchmark,
        model_path: str,
        num_shots: int = 0,
        max_samples: Optional[int] = None,
        provider: str = "ollama",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Run a benchmark evaluation.
        
        Args:
            benchmark: Benchmark instance
            model_path: Path to the model
            num_shots: Number of few-shot examples
            max_samples: Maximum samples to evaluate
            provider: Model provider
            **kwargs: Additional parameters
            
        Returns:
            Benchmark results
        """
        logger.info(f"Running benchmark {benchmark.name} on {model_path}")
        
        # Load benchmark data
        test_data = benchmark.load_data(max_samples=max_samples)
        
        # Run evaluation
        results = {
            "benchmark": benchmark.name,
            "model_path": model_path,
            "num_shots": num_shots,
            "num_samples": len(test_data),
            "results": {}
        }
        
        # Process each sample
        correct = 0
        total = 0
        
        for sample in test_data:
            try:
                # Generate prediction (simplified)
                prediction = self._generate_prediction(
                    model_path, sample, num_shots, provider, **kwargs
                )
                
                # Check if correct
                is_correct = benchmark.evaluate_sample(sample, prediction)
                if is_correct:
                    correct += 1
                total += 1
                
            except Exception as e:
                logger.error(f"Failed to process sample: {e}")
                continue
        
        # Calculate final score
        accuracy = correct / total if total > 0 else 0.0
        
        results["results"] = {
            "accuracy": accuracy,
            "correct": correct,
            "total": total
        }
        
        logger.info(f"Benchmark completed: {accuracy:.3f} accuracy ({correct}/{total})")
        return results
    
    def _generate_prediction(
        self,
        model_path: str,
        sample: Dict[str, Any],
        num_shots: int,
        provider: str,
        **kwargs
    ) -> str:
        """Generate prediction for a sample (simplified implementation)."""
        # This is a placeholder - replace with actual model inference
        return "A"  # Placeholder answer 