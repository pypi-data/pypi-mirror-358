"""
Unified Evaluation Factory for ISA Model Framework

This factory provides a single interface for all evaluation operations:
- LLM evaluation (perplexity, BLEU, ROUGE, custom metrics)
- Image model evaluation (FID, IS, LPIPS)
- Benchmark testing (MMLU, HellaSwag, ARC, etc.)
- Custom evaluation pipelines
- Weights & Biases integration for experiment tracking
"""

import os
import json
import logging
from typing import Optional, Dict, Any, List, Union
from pathlib import Path
import datetime

try:
    import wandb
    WANDB_AVAILABLE = True
except ImportError:
    WANDB_AVAILABLE = False

try:
    import mlflow
    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False

from .metrics import LLMMetrics, ImageMetrics, BenchmarkRunner
from .benchmarks import MMLU, HellaSwag, ARC, GSM8K

logger = logging.getLogger(__name__)


class EvaluationFactory:
    """
    Unified factory for all AI model evaluation operations with experiment tracking.
    
    This class provides simplified interfaces for:
    - LLM evaluation with various metrics
    - Image model evaluation
    - Benchmark testing on standard datasets
    - Custom evaluation pipelines
    - Experiment tracking with W&B and MLflow
    
    Example usage:
        ```python
        from isa_model.eval import EvaluationFactory
        
        evaluator = EvaluationFactory(
            output_dir="eval_results",
            use_wandb=True,
            wandb_project="model-evaluation"
        )
        
        # Evaluate LLM on custom dataset
        results = evaluator.evaluate_llm(
            model_path="path/to/model",
            dataset_path="test_data.json",
            metrics=["perplexity", "bleu", "rouge"],
            experiment_name="gemma-4b-evaluation"
        )
        
        # Run MMLU benchmark
        mmlu_results = evaluator.run_benchmark(
            model_path="path/to/model",
            benchmark="mmlu",
            subjects=["math", "physics", "chemistry"]
        )
        
        # Compare multiple models
        comparison = evaluator.compare_models([
            "model1/path",
            "model2/path"
        ], benchmark="hellaswag")
        ```
    """
    
    def __init__(
        self, 
        output_dir: Optional[str] = None,
        use_wandb: bool = False,
        wandb_project: Optional[str] = None,
        wandb_entity: Optional[str] = None,
        use_mlflow: bool = False,
        mlflow_tracking_uri: Optional[str] = None
    ):
        """
        Initialize the evaluation factory with experiment tracking.
        
        Args:
            output_dir: Base directory for evaluation outputs
            use_wandb: Whether to use Weights & Biases for tracking
            wandb_project: W&B project name
            wandb_entity: W&B entity/team name
            use_mlflow: Whether to use MLflow for tracking
            mlflow_tracking_uri: MLflow tracking server URI
        """
        self.output_dir = output_dir or os.path.join(os.getcwd(), "evaluation_results")
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize metrics calculators
        self.llm_metrics = LLMMetrics()
        self.image_metrics = ImageMetrics()
        self.benchmark_runner = BenchmarkRunner()
        
        # Setup experiment tracking
        self.use_wandb = use_wandb and WANDB_AVAILABLE
        self.use_mlflow = use_mlflow and MLFLOW_AVAILABLE
        
        if self.use_wandb:
            self.wandb_project = wandb_project or "isa-model-evaluation"
            self.wandb_entity = wandb_entity
            logger.info(f"W&B tracking enabled for project: {self.wandb_project}")
        
        if self.use_mlflow:
            if mlflow_tracking_uri:
                mlflow.set_tracking_uri(mlflow_tracking_uri)
            logger.info(f"MLflow tracking enabled with URI: {mlflow.get_tracking_uri()}")
        
        logger.info(f"EvaluationFactory initialized with output dir: {self.output_dir}")
    
    def _start_experiment(self, experiment_name: str, config: Dict[str, Any]) -> None:
        """Start experiment tracking."""
        if self.use_wandb:
            wandb.init(
                project=self.wandb_project,
                entity=self.wandb_entity,
                name=experiment_name,
                config=config,
                reinit=True
            )
        
        if self.use_mlflow:
            mlflow.start_run(run_name=experiment_name)
            mlflow.log_params(config)
    
    def _log_metrics(self, metrics: Dict[str, Any], step: Optional[int] = None) -> None:
        """Log metrics to experiment tracking systems."""
        if self.use_wandb:
            wandb.log(metrics, step=step)
        
        if self.use_mlflow:
            for key, value in metrics.items():
                if isinstance(value, (int, float)):
                    mlflow.log_metric(key, value, step=step)
    
    def _end_experiment(self) -> None:
        """End experiment tracking."""
        if self.use_wandb:
            wandb.finish()
        
        if self.use_mlflow:
            mlflow.end_run()
    
    def _get_output_path(self, model_name: str, eval_type: str) -> str:
        """Generate timestamped output path for evaluation results."""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_model_name = os.path.basename(model_name).replace("/", "_").replace(":", "_")
        filename = f"{safe_model_name}_{eval_type}_{timestamp}.json"
        return os.path.join(self.output_dir, filename)
    
    # =================
    # LLM Evaluation Methods
    # =================
    
    def evaluate_llm(
        self,
        model_path: str,
        dataset_path: str,
        metrics: List[str] = None,
        output_path: Optional[str] = None,
        batch_size: int = 8,
        max_samples: Optional[int] = None,
        provider: str = "ollama",
        experiment_name: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Evaluate an LLM model on a dataset with specified metrics.
        
        Args:
            model_path: Path to the model or model identifier
            dataset_path: Path to evaluation dataset (JSON format)
            metrics: List of metrics to compute ["perplexity", "bleu", "rouge", "accuracy"]
            output_path: Path to save results
            batch_size: Batch size for evaluation
            max_samples: Maximum number of samples to evaluate
            provider: Model provider ("ollama", "openai", "hf")
            experiment_name: Name for experiment tracking
            **kwargs: Additional parameters
            
        Returns:
            Dictionary containing evaluation results
            
        Example:
            ```python
            results = evaluator.evaluate_llm(
                model_path="google/gemma-2-4b-it",
                dataset_path="test_data.json",
                metrics=["perplexity", "bleu", "rouge"],
                max_samples=1000,
                experiment_name="gemma-4b-eval"
            )
            ```
        """
        if metrics is None:
            metrics = ["perplexity", "bleu", "rouge"]
        
        if not output_path:
            output_path = self._get_output_path(model_path, "llm_eval")
        
        # Setup experiment tracking
        config = {
            "model_path": model_path,
            "dataset_path": dataset_path,
            "metrics": metrics,
            "batch_size": batch_size,
            "max_samples": max_samples,
            "provider": provider
        }
        
        experiment_name = experiment_name or f"llm_eval_{os.path.basename(model_path)}"
        self._start_experiment(experiment_name, config)
        
        logger.info(f"Evaluating LLM {model_path} with metrics: {metrics}")
        
        try:
            # Load dataset
            with open(dataset_path, 'r') as f:
                dataset = json.load(f)
            
            if max_samples:
                dataset = dataset[:max_samples]
            
            # Run evaluation
            results = self.llm_metrics.evaluate(
                model_path=model_path,
                dataset=dataset,
                metrics=metrics,
                batch_size=batch_size,
                provider=provider,
                **kwargs
            )
            
            # Log metrics to tracking systems
            self._log_metrics(results.get("metrics", {}))
            
            # Add metadata
            results["metadata"] = {
                "model_path": model_path,
                "dataset_path": dataset_path,
                "metrics": metrics,
                "num_samples": len(dataset),
                "timestamp": datetime.datetime.now().isoformat(),
                "provider": provider,
                "experiment_name": experiment_name
            }
            
            # Save results
            with open(output_path, 'w') as f:
                json.dump(results, f, indent=2)
            
            logger.info(f"Evaluation results saved to: {output_path}")
            
        finally:
            self._end_experiment()
        
        return results
    
    def evaluate_generation_quality(
        self,
        model_path: str,
        prompts: List[str],
        reference_texts: List[str] = None,
        metrics: List[str] = None,
        output_path: Optional[str] = None,
        provider: str = "ollama",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Evaluate text generation quality.
        
        Args:
            model_path: Path to the model
            prompts: List of input prompts
            reference_texts: Reference texts for comparison (optional)
            metrics: Metrics to compute
            output_path: Output path for results
            provider: Model provider
            **kwargs: Additional parameters
            
        Returns:
            Evaluation results dictionary
        """
        if metrics is None:
            metrics = ["diversity", "coherence", "fluency"]
        
        if not output_path:
            output_path = self._get_output_path(model_path, "generation_eval")
        
        results = self.llm_metrics.evaluate_generation(
            model_path=model_path,
            prompts=prompts,
            reference_texts=reference_texts,
            metrics=metrics,
            provider=provider,
            **kwargs
        )
        
        # Save results
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        return results
    
    # =================
    # Benchmark Testing Methods
    # =================
    
    def run_benchmark(
        self,
        model_path: str,
        benchmark: str,
        output_path: Optional[str] = None,
        num_shots: int = 0,
        max_samples: Optional[int] = None,
        provider: str = "ollama",
        experiment_name: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Run a specific benchmark on a model with experiment tracking.
        
        Args:
            model_path: Path to the model
            benchmark: Benchmark name ("mmlu", "hellaswag", "arc", "gsm8k")
            output_path: Path to save results
            num_shots: Number of few-shot examples
            max_samples: Maximum samples to evaluate
            provider: Model provider
            experiment_name: Name for experiment tracking
            **kwargs: Additional parameters
            
        Returns:
            Benchmark results dictionary
        """
        if not output_path:
            output_path = self._get_output_path(model_path, f"{benchmark}_benchmark")
        
        # Setup experiment tracking
        config = {
            "model_path": model_path,
            "benchmark": benchmark,
            "num_shots": num_shots,
            "max_samples": max_samples,
            "provider": provider
        }
        
        experiment_name = experiment_name or f"{benchmark}_{os.path.basename(model_path)}"
        self._start_experiment(experiment_name, config)
        
        logger.info(f"Running {benchmark.upper()} benchmark on {model_path}")
        
        try:
            # Initialize benchmark
            benchmark_map = {
                "mmlu": MMLU(),
                "hellaswag": HellaSwag(),
                "arc": ARC(),
                "gsm8k": GSM8K()
            }
            
            if benchmark.lower() not in benchmark_map:
                raise ValueError(f"Benchmark '{benchmark}' not supported. Available: {list(benchmark_map.keys())}")
            
            benchmark_instance = benchmark_map[benchmark.lower()]
            
            # Run benchmark
            results = self.benchmark_runner.run_benchmark(
                model_path=model_path,
                benchmark=benchmark_instance,
                num_shots=num_shots,
                max_samples=max_samples,
                provider=provider,
                **kwargs
            )
            
            # Log metrics to tracking systems
            self._log_metrics(results.get("metrics", {}))
            
            # Add metadata
            results["metadata"] = {
                "model_path": model_path,
                "benchmark": benchmark,
                "num_shots": num_shots,
                "max_samples": max_samples,
                "timestamp": datetime.datetime.now().isoformat(),
                "provider": provider,
                "experiment_name": experiment_name
            }
            
            # Save results
            with open(output_path, 'w') as f:
                json.dump(results, f, indent=2)
            
            logger.info(f"Benchmark results saved to: {output_path}")
            
        finally:
            self._end_experiment()
        
        return results
    
    def run_multiple_benchmarks(
        self,
        model_path: str,
        benchmarks: List[str] = None,
        output_dir: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Run multiple benchmarks on a model.
        
        Args:
            model_path: Path to the model
            benchmarks: List of benchmark names
            output_dir: Directory to save results
            **kwargs: Additional parameters
            
        Returns:
            Combined results dictionary
        """
        if benchmarks is None:
            benchmarks = ["mmlu", "hellaswag", "arc"]
        
        if not output_dir:
            output_dir = os.path.join(self.output_dir, "multi_benchmark")
            os.makedirs(output_dir, exist_ok=True)
        
        all_results = {}
        
        for benchmark in benchmarks:
            try:
                output_path = os.path.join(output_dir, f"{benchmark}_results.json")
                results = self.run_benchmark(
                    model_path=model_path,
                    benchmark=benchmark,
                    output_path=output_path,
                    **kwargs
                )
                all_results[benchmark] = results
            except Exception as e:
                logger.error(f"Failed to run benchmark {benchmark}: {e}")
                all_results[benchmark] = {"error": str(e)}
        
        # Save combined results
        combined_path = os.path.join(output_dir, "combined_results.json")
        with open(combined_path, 'w') as f:
            json.dump(all_results, f, indent=2)
        
        return all_results
    
    # =================
    # Model Comparison Methods
    # =================
    
    def compare_models(
        self,
        model_paths: List[str],
        dataset_path: Optional[str] = None,
        benchmark: Optional[str] = None,
        metrics: List[str] = None,
        output_path: Optional[str] = None,
        experiment_name: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Compare multiple models on the same evaluation task.
        
        Args:
            model_paths: List of model paths to compare
            dataset_path: Dataset for evaluation (if not using benchmark)
            benchmark: Benchmark name (if not using custom dataset)
            metrics: Metrics to compute
            output_path: Path to save comparison results
            experiment_name: Name for experiment tracking
            **kwargs: Additional parameters
            
        Returns:
            Comparison results dictionary
        """
        if not dataset_path and not benchmark:
            raise ValueError("Either dataset_path or benchmark must be provided")
        
        if not output_path:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(self.output_dir, f"model_comparison_{timestamp}.json")
        
        # Setup experiment tracking
        config = {
            "model_paths": model_paths,
            "dataset_path": dataset_path,
            "benchmark": benchmark,
            "metrics": metrics
        }
        
        experiment_name = experiment_name or f"model_comparison_{len(model_paths)}_models"
        self._start_experiment(experiment_name, config)
        
        logger.info(f"Comparing {len(model_paths)} models")
        
        try:
            results = {"models": {}, "comparison": {}}
            
            # Evaluate each model
            for i, model_path in enumerate(model_paths):
                logger.info(f"Evaluating model {i+1}/{len(model_paths)}: {model_path}")
                
                if benchmark:
                    model_results = self.run_benchmark(
                        model_path=model_path,
                        benchmark=benchmark,
                        experiment_name=None,  # Don't start new experiment
                        **kwargs
                    )
                else:
                    model_results = self.evaluate_llm(
                        model_path=model_path,
                        dataset_path=dataset_path,
                        metrics=metrics,
                        experiment_name=None,  # Don't start new experiment
                        **kwargs
                    )
                
                results["models"][model_path] = model_results
                
                # Log individual model metrics
                model_metrics = model_results.get("metrics", {})
                for metric_name, value in model_metrics.items():
                    self._log_metrics({f"{os.path.basename(model_path)}_{metric_name}": value})
            
            # Generate comparison summary
            results["comparison"] = self._generate_comparison_summary(results["models"])
            
            # Add metadata
            results["metadata"] = {
                "model_paths": model_paths,
                "dataset_path": dataset_path,
                "benchmark": benchmark,
                "metrics": metrics,
                "timestamp": datetime.datetime.now().isoformat(),
                "experiment_name": experiment_name
            }
            
            # Save results
            with open(output_path, 'w') as f:
                json.dump(results, f, indent=2)
            
            logger.info(f"Comparison results saved to: {output_path}")
            
        finally:
            self._end_experiment()
        
        return results
    
    def _generate_comparison_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comparison summary from multiple model results."""
        summary = {
            "best_model": {},
            "rankings": {},
            "metric_comparisons": {}
        }
        
        # Extract all metrics across models
        all_metrics = set()
        for model_results in results.values():
            if "metrics" in model_results:
                all_metrics.update(model_results["metrics"].keys())
        
        # Compare each metric
        for metric in all_metrics:
            metric_values = {}
            for model_path, model_results in results.items():
                if "metrics" in model_results and metric in model_results["metrics"]:
                    metric_values[model_path] = model_results["metrics"][metric]
            
            if metric_values:
                # Determine if higher is better (most metrics, higher is better)
                higher_is_better = metric not in ["perplexity", "loss", "error_rate"]
                
                best_model = max(metric_values.items(), key=lambda x: x[1]) if higher_is_better else min(metric_values.items(), key=lambda x: x[1])
                summary["best_model"][metric] = {
                    "model": best_model[0],
                    "value": best_model[1]
                }
                
                # Create ranking
                sorted_models = sorted(metric_values.items(), key=lambda x: x[1], reverse=higher_is_better)
                summary["rankings"][metric] = [{"model": model, "value": value} for model, value in sorted_models]
                
                summary["metric_comparisons"][metric] = metric_values
        
        return summary
    
    # =================
    # Image Model Evaluation Methods
    # =================
    
    def evaluate_image_model(
        self,
        model_path: str,
        test_images_dir: str,
        reference_images_dir: Optional[str] = None,
        metrics: List[str] = None,
        output_path: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Evaluate image generation model.
        
        Args:
            model_path: Path to the image model
            test_images_dir: Directory with test images
            reference_images_dir: Directory with reference images
            metrics: Metrics to compute ["fid", "is", "lpips"]
            output_path: Output path for results
            **kwargs: Additional parameters
            
        Returns:
            Image evaluation results
        """
        if metrics is None:
            metrics = ["fid", "is"]
        
        if not output_path:
            output_path = self._get_output_path(model_path, "image_eval")
        
        results = self.image_metrics.evaluate(
            model_path=model_path,
            test_images_dir=test_images_dir,
            reference_images_dir=reference_images_dir,
            metrics=metrics,
            **kwargs
        )
        
        # Save results
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        return results
    
    # =================
    # Utility Methods
    # =================
    
    def load_results(self, results_path: str) -> Dict[str, Any]:
        """Load evaluation results from file."""
        with open(results_path, 'r') as f:
            return json.load(f)
    
    def list_evaluation_results(self) -> List[Dict[str, Any]]:
        """List all evaluation results in the output directory."""
        results = []
        
        if os.path.exists(self.output_dir):
            for filename in os.listdir(self.output_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(self.output_dir, filename)
                    try:
                        with open(filepath, 'r') as f:
                            data = json.load(f)
                            results.append({
                                "filename": filename,
                                "path": filepath,
                                "metadata": data.get("metadata", {}),
                                "created": datetime.datetime.fromtimestamp(
                                    os.path.getctime(filepath)
                                ).isoformat()
                            })
                    except Exception as e:
                        logger.warning(f"Failed to load {filename}: {e}")
        
        return sorted(results, key=lambda x: x["created"], reverse=True)
    
    def generate_report(
        self,
        results_paths: List[str],
        output_path: Optional[str] = None,
        format: str = "json"
    ) -> str:
        """
        Generate evaluation report from multiple results.
        
        Args:
            results_paths: List of result file paths
            output_path: Output path for report
            format: Report format ("json", "html", "markdown")
            
        Returns:
            Path to generated report
        """
        if not output_path:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(self.output_dir, f"evaluation_report_{timestamp}.{format}")
        
        # Load all results
        all_results = []
        for path in results_paths:
            try:
                results = self.load_results(path)
                all_results.append(results)
            except Exception as e:
                logger.warning(f"Failed to load results from {path}: {e}")
        
        # Generate report based on format
        if format == "json":
            report_data = {
                "report_generated": datetime.datetime.now().isoformat(),
                "num_evaluations": len(all_results),
                "results": all_results
            }
            
            with open(output_path, 'w') as f:
                json.dump(report_data, f, indent=2)
        
        # TODO: Implement HTML and Markdown report generation
        
        logger.info(f"Evaluation report generated: {output_path}")
        return output_path

    def evaluate_multimodal_model(
        self,
        model_path: str,
        text_dataset_path: Optional[str] = None,
        image_dataset_path: Optional[str] = None,
        audio_dataset_path: Optional[str] = None,
        metrics: List[str] = None,
        experiment_name: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Evaluate multimodal models across different modalities.
        
        Args:
            model_path: Path to the multimodal model
            text_dataset_path: Path to text evaluation dataset
            image_dataset_path: Path to image evaluation dataset  
            audio_dataset_path: Path to audio evaluation dataset
            metrics: Metrics to compute for each modality
            experiment_name: Name for experiment tracking
            **kwargs: Additional parameters
            
        Returns:
            Multimodal evaluation results
        """
        config = {
            "model_path": model_path,
            "text_dataset_path": text_dataset_path,
            "image_dataset_path": image_dataset_path,
            "audio_dataset_path": audio_dataset_path,
            "metrics": metrics
        }
        
        experiment_name = experiment_name or f"multimodal_eval_{os.path.basename(model_path)}"
        self._start_experiment(experiment_name, config)
        
        logger.info(f"Evaluating multimodal model: {model_path}")
        
        try:
            results = {"modalities": {}}
            
            # Text evaluation
            if text_dataset_path:
                logger.info("Evaluating text modality...")
                text_results = self.evaluate_llm(
                    model_path=model_path,
                    dataset_path=text_dataset_path,
                    metrics=metrics or ["perplexity", "bleu", "rouge"],
                    experiment_name=None,
                    **kwargs
                )
                results["modalities"]["text"] = text_results
                self._log_metrics({f"text_{k}": v for k, v in text_results.get("metrics", {}).items()})
            
            # Image evaluation
            if image_dataset_path:
                logger.info("Evaluating image modality...")
                image_results = self.evaluate_image_model(
                    model_path=model_path,
                    test_images_dir=image_dataset_path,
                    metrics=metrics or ["fid", "is", "lpips"],
                    experiment_name=None,
                    **kwargs
                )
                results["modalities"]["image"] = image_results
                self._log_metrics({f"image_{k}": v for k, v in image_results.get("metrics", {}).items()})
            
            # Audio evaluation (placeholder for future implementation)
            if audio_dataset_path:
                logger.info("Audio evaluation not yet implemented")
                results["modalities"]["audio"] = {"status": "not_implemented"}
            
            # Add metadata
            results["metadata"] = {
                "model_path": model_path,
                "modalities_evaluated": list(results["modalities"].keys()),
                "timestamp": datetime.datetime.now().isoformat(),
                "experiment_name": experiment_name
            }
            
            # Save results
            output_path = self._get_output_path(model_path, "multimodal_eval")
            with open(output_path, 'w') as f:
                json.dump(results, f, indent=2)
            
            logger.info(f"Multimodal evaluation results saved to: {output_path}")
            
        finally:
            self._end_experiment()
        
        return results 