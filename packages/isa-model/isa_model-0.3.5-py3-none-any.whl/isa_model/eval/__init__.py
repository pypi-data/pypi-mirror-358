"""
ISA Model Evaluation Framework

This module provides comprehensive evaluation capabilities for AI models:
- LLM evaluation (perplexity, BLEU, ROUGE, custom metrics)
- Image model evaluation (FID, IS, LPIPS)
- Benchmark testing (MMLU, HellaSwag, ARC, etc.)
- Custom evaluation pipelines

Usage:
    from isa_model.eval import EvaluationFactory
    
    # Create evaluation factory
    evaluator = EvaluationFactory()
    
    # Evaluate LLM performance
    results = evaluator.evaluate_llm(
        model_path="path/to/model",
        dataset_path="test_data.json",
        metrics=["perplexity", "bleu", "rouge"]
    )
    
    # Run benchmark tests
    benchmark_results = evaluator.run_benchmark(
        model_path="path/to/model",
        benchmark="mmlu"
    )
"""

from .factory import EvaluationFactory
from .metrics import (
    LLMMetrics,
    ImageMetrics,
    BenchmarkRunner,
    MetricType
)
from .benchmarks import (
    MMLU,
    HellaSwag,
    ARC,
    GSM8K,
    BenchmarkConfig
)

__all__ = [
    "EvaluationFactory",
    "LLMMetrics",
    "ImageMetrics", 
    "BenchmarkRunner",
    "MetricType",
    "MMLU",
    "HellaSwag",
    "ARC",
    "GSM8K",
    "BenchmarkConfig"
] 