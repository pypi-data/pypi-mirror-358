"""
Base Stacked Service for orchestrating multiple AI models
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union, Callable
import time
import asyncio
import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class LayerType(Enum):
    """Types of processing layers"""
    INTELLIGENCE = "intelligence"      # High-level understanding
    DETECTION = "detection"           # Element/object detection  
    CLASSIFICATION = "classification" # Detailed classification
    VALIDATION = "validation"         # Result validation
    TRANSFORMATION = "transformation" # Data transformation
    GENERATION = "generation"         # Content generation
    ENHANCEMENT = "enhancement"       # Quality enhancement
    CONTROL = "control"              # Precise control/refinement
    UPSCALING = "upscaling"          # Resolution enhancement

@dataclass
class LayerConfig:
    """Configuration for a processing layer"""
    name: str
    layer_type: LayerType
    service_type: str                  # e.g., 'vision', 'llm'
    model_name: str
    parameters: Dict[str, Any]
    depends_on: List[str]             # Layer dependencies
    timeout: float = 30.0
    retry_count: int = 1
    fallback_enabled: bool = True

@dataclass
class LayerResult:
    """Result from a processing layer"""
    layer_name: str
    success: bool
    data: Any
    metadata: Dict[str, Any]
    execution_time: float
    error: Optional[str] = None

class BaseStackedService(ABC):
    """
    Base class for stacked services that orchestrate multiple AI models
    """
    
    def __init__(self, ai_factory, service_name: str):
        self.ai_factory = ai_factory
        self.service_name = service_name
        self.layers: List[LayerConfig] = []
        self.services: Dict[str, Any] = {}
        self.results: Dict[str, LayerResult] = {}
        
    def add_layer(self, config: LayerConfig):
        """Add a processing layer to the stack"""
        self.layers.append(config)
        logger.info(f"Added layer {config.name} ({config.layer_type.value}) to {self.service_name}")
    
    async def initialize_services(self):
        """Initialize all required services"""
        for layer in self.layers:
            service_key = f"{layer.service_type}_{layer.model_name}"
            
            if service_key not in self.services:
                if layer.service_type == 'vision':
                    if layer.model_name == "default":
                        # 使用默认vision服务
                        service = self.ai_factory.get_vision()
                    elif layer.model_name == "omniparser":
                        # 使用replicate omniparser
                        service = self.ai_factory.get_vision(model_name="omniparser", provider="replicate")
                    else:
                        # 其他指定模型
                        service = self.ai_factory.get_vision(model_name=layer.model_name)
                elif layer.service_type == 'llm':
                    if layer.model_name == "default":
                        service = self.ai_factory.get_llm()
                    else:
                        service = self.ai_factory.get_llm(model_name=layer.model_name)
                elif layer.service_type == 'image_gen':
                    if layer.model_name == "default":
                        service = self.ai_factory.get_image_gen()
                    else:
                        service = self.ai_factory.get_image_gen(model_name=layer.model_name)
                else:
                    raise ValueError(f"Unsupported service type: {layer.service_type}")
                
                self.services[service_key] = service
                logger.info(f"Initialized {service_key} service")
    
    async def execute_layer(self, layer: LayerConfig, context: Dict[str, Any]) -> LayerResult:
        """Execute a single layer"""
        start_time = time.time()
        
        try:
            # Check dependencies
            for dep in layer.depends_on:
                if dep not in self.results or not self.results[dep].success:
                    raise ValueError(f"Dependency {dep} failed or not executed")
            
            # Get the service
            service_key = f"{layer.service_type}_{layer.model_name}"
            service = self.services[service_key]
            
            # Execute layer with timeout
            data = await asyncio.wait_for(
                self.execute_layer_logic(layer, service, context),
                timeout=layer.timeout
            )
            
            execution_time = time.time() - start_time
            
            result = LayerResult(
                layer_name=layer.name,
                success=True,
                data=data,
                metadata={
                    "layer_type": layer.layer_type.value,
                    "model": layer.model_name,
                    "parameters": layer.parameters
                },
                execution_time=execution_time
            )
            
            logger.info(f"Layer {layer.name} completed in {execution_time:.2f}s")
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = str(e)
            
            logger.error(f"Layer {layer.name} failed after {execution_time:.2f}s: {error_msg}")
            
            result = LayerResult(
                layer_name=layer.name,
                success=False,
                data=None,
                metadata={
                    "layer_type": layer.layer_type.value,
                    "model": layer.model_name,
                    "parameters": layer.parameters
                },
                execution_time=execution_time,
                error=error_msg
            )
            
            # Try fallback if enabled
            if layer.fallback_enabled:
                fallback_result = await self.execute_fallback(layer, context, error_msg)
                if fallback_result:
                    result.data = fallback_result
                    result.success = True
                    result.error = f"Fallback used: {error_msg}"
            
            return result
    
    @abstractmethod
    async def execute_layer_logic(self, layer: LayerConfig, service: Any, context: Dict[str, Any]) -> Any:
        """Execute the specific logic for a layer - to be implemented by subclasses"""
        pass
    
    async def execute_fallback(self, layer: LayerConfig, context: Dict[str, Any], error: str) -> Optional[Any]:
        """Execute fallback logic for a failed layer - can be overridden by subclasses"""
        return None
    
    async def invoke(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Invoke the entire stack of layers"""
        logger.info(f"Starting {self.service_name} stack invocation")
        stack_start_time = time.time()
        
        # Initialize services if not done
        if not self.services:
            await self.initialize_services()
        
        # Clear previous results
        self.results.clear()
        
        # Build execution order based on dependencies
        execution_order = self._build_execution_order()
        
        # Execute layers in order
        context = {"input": input_data, "results": self.results}
        
        for layer in execution_order:
            result = await self.execute_layer(layer, context)
            self.results[layer.name] = result
            
            # Update context with result
            context["results"] = self.results
            
            # Stop if critical layer fails
            if not result.success and not layer.fallback_enabled:
                logger.error(f"Critical layer {layer.name} failed, stopping execution")
                break
        
        total_time = time.time() - stack_start_time
        
        # Generate final result
        final_result = {
            "service": self.service_name,
            "success": all(r.success for r in self.results.values()),
            "total_execution_time": total_time,
            "layer_results": {name: result for name, result in self.results.items()},
            "final_output": self.generate_final_output(self.results)
        }
        
        logger.info(f"{self.service_name} stack invocation completed in {total_time:.2f}s")
        return final_result
    
    def _build_execution_order(self) -> List[LayerConfig]:
        """Build execution order based on dependencies"""
        # Simple topological sort
        ordered = []
        remaining = self.layers.copy()
        
        while remaining:
            # Find layers with no unmet dependencies
            ready = []
            for layer in remaining:
                deps_met = all(dep in [l.name for l in ordered] for dep in layer.depends_on)
                if deps_met:
                    ready.append(layer)
            
            if not ready:
                raise ValueError("Circular dependency detected in layer configuration")
            
            # Add ready layers to order
            ordered.extend(ready)
            for layer in ready:
                remaining.remove(layer)
        
        return ordered
    
    @abstractmethod
    def generate_final_output(self, results: Dict[str, LayerResult]) -> Any:
        """Generate final output from all layer results - to be implemented by subclasses"""
        pass
    
    async def close(self):
        """Close all services"""
        for service in self.services.values():
            if hasattr(service, 'close'):
                await service.close()
        self.services.clear()
        logger.info(f"Closed all services for {self.service_name}")
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for the stack"""
        if not self.results:
            return {}
        
        metrics = {
            "total_layers": len(self.results),
            "successful_layers": sum(1 for r in self.results.values() if r.success),
            "failed_layers": sum(1 for r in self.results.values() if not r.success),
            "total_execution_time": sum(r.execution_time for r in self.results.values()),
            "layer_times": {name: r.execution_time for name, r in self.results.items()},
            "layer_success": {name: r.success for name, r in self.results.items()}
        }
        
        return metrics