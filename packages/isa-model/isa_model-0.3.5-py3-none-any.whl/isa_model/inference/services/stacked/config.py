"""
Configuration system for stacked services
"""

from typing import Dict, Any, List
from dataclasses import dataclass, field
from enum import Enum

from .base_stacked_service import LayerConfig, LayerType

class WorkflowType(Enum):
    """Predefined workflow types"""
    UI_ANALYSIS_FAST = "ui_analysis_fast"
    UI_ANALYSIS_ACCURATE = "ui_analysis_accurate"
    UI_ANALYSIS_COMPREHENSIVE = "ui_analysis_comprehensive"
    SEARCH_PAGE_ANALYSIS = "search_page_analysis"
    CONTENT_EXTRACTION = "content_extraction"
    FORM_INTERACTION = "form_interaction"
    NAVIGATION_ANALYSIS = "navigation_analysis"
    CUSTOM = "custom"

@dataclass
class StackedServiceConfig:
    """Configuration for a stacked service workflow"""
    name: str
    workflow_type: WorkflowType
    layers: List[LayerConfig] = field(default_factory=list)
    global_timeout: float = 120.0
    parallel_execution: bool = False
    fail_fast: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

class ConfigManager:
    """Manager for stacked service configurations"""
    
    PREDEFINED_CONFIGS = {
        WorkflowType.UI_ANALYSIS_FAST: {
            "name": "Fast UI Analysis",
            "layers": [
                LayerConfig(
                    name="page_intelligence",
                    layer_type=LayerType.INTELLIGENCE,
                    service_type="vision",
                    model_name="gpt-4.1-nano",
                    parameters={"max_tokens": 300},
                    depends_on=[],
                    timeout=10.0,
                    fallback_enabled=True
                ),
                LayerConfig(
                    name="element_detection",
                    layer_type=LayerType.DETECTION,
                    service_type="vision",
                    model_name="omniparser",
                    parameters={
                        "imgsz": 480,
                        "box_threshold": 0.08,
                        "iou_threshold": 0.2
                    },
                    depends_on=["page_intelligence"],
                    timeout=15.0,
                    fallback_enabled=True
                ),
                LayerConfig(
                    name="element_classification",
                    layer_type=LayerType.CLASSIFICATION,
                    service_type="vision",
                    model_name="gpt-4.1-nano",
                    parameters={"max_tokens": 200},
                    depends_on=["page_intelligence", "element_detection"],
                    timeout=20.0,
                    fallback_enabled=False
                )
            ],
            "global_timeout": 60.0,
            "parallel_execution": False,
            "fail_fast": False,
            "metadata": {
                "description": "Fast UI analysis optimized for speed",
                "expected_time": "30-45 seconds",
                "accuracy": "medium"
            }
        },
        
        WorkflowType.UI_ANALYSIS_ACCURATE: {
            "name": "Accurate UI Analysis",
            "layers": [
                LayerConfig(
                    name="page_intelligence",
                    layer_type=LayerType.INTELLIGENCE,
                    service_type="vision",
                    model_name="gpt-4-vision-preview",
                    parameters={"max_tokens": 800},
                    depends_on=[],
                    timeout=20.0,
                    fallback_enabled=True
                ),
                LayerConfig(
                    name="element_detection",
                    layer_type=LayerType.DETECTION,
                    service_type="vision",
                    model_name="omniparser",
                    parameters={
                        "imgsz": 640,
                        "box_threshold": 0.05,
                        "iou_threshold": 0.1
                    },
                    depends_on=["page_intelligence"],
                    timeout=25.0,
                    fallback_enabled=True
                ),
                LayerConfig(
                    name="element_classification",
                    layer_type=LayerType.CLASSIFICATION,
                    service_type="vision",
                    model_name="gpt-4-vision-preview",
                    parameters={"max_tokens": 500},
                    depends_on=["page_intelligence", "element_detection"],
                    timeout=30.0,
                    fallback_enabled=False
                )
            ],
            "global_timeout": 90.0,
            "parallel_execution": False,
            "fail_fast": False,
            "metadata": {
                "description": "Balanced UI analysis for production use",
                "expected_time": "60-75 seconds",
                "accuracy": "high"
            }
        },
        
        WorkflowType.SEARCH_PAGE_ANALYSIS: {
            "name": "Search Page Analysis",
            "layers": [
                LayerConfig(
                    name="page_intelligence",
                    layer_type=LayerType.INTELLIGENCE,
                    service_type="vision",
                    model_name="default",
                    parameters={
                        "task": "search_page_intelligence",
                        "max_tokens": 400
                    },
                    depends_on=[],
                    timeout=15.0,
                    fallback_enabled=True
                ),
                LayerConfig(
                    name="element_detection",
                    layer_type=LayerType.DETECTION,
                    service_type="vision",
                    model_name="omniparser",
                    parameters={
                        "task": "element_detection",
                        "imgsz": 640,
                        "box_threshold": 0.05,
                        "iou_threshold": 0.1
                    },
                    depends_on=["page_intelligence"],
                    timeout=20.0,
                    fallback_enabled=True
                ),
                LayerConfig(
                    name="element_classification",
                    layer_type=LayerType.CLASSIFICATION,
                    service_type="vision",
                    model_name="default",
                    parameters={
                        "task": "search_element_classification",
                        "max_tokens": 300
                    },
                    depends_on=["page_intelligence", "element_detection"],
                    timeout=25.0,
                    fallback_enabled=False
                )
            ],
            "global_timeout": 80.0,
            "parallel_execution": False,
            "fail_fast": False,
            "metadata": {
                "description": "Analysis for search pages (Google, Bing, etc.)",
                "expected_time": "45-60 seconds",
                "accuracy": "high",
                "page_types": ["search", "query", "results"]
            }
        },
        
        WorkflowType.CONTENT_EXTRACTION: {
            "name": "Content Extraction",
            "layers": [
                LayerConfig(
                    name="page_intelligence",
                    layer_type=LayerType.INTELLIGENCE,
                    service_type="vision",
                    model_name="default",
                    parameters={
                        "task": "content_page_intelligence",
                        "max_tokens": 500
                    },
                    depends_on=[],
                    timeout=15.0,
                    fallback_enabled=True
                ),
                LayerConfig(
                    name="content_detection",
                    layer_type=LayerType.DETECTION,
                    service_type="vision",
                    model_name="florence-2",
                    parameters={
                        "task": "<OPEN_VOCABULARY_DETECTION>",
                        "text_input": "article content, text blocks, headings, paragraphs, links"
                    },
                    depends_on=["page_intelligence"],
                    timeout=25.0,
                    fallback_enabled=True
                ),
                LayerConfig(
                    name="content_classification",
                    layer_type=LayerType.CLASSIFICATION,
                    service_type="vision",
                    model_name="default",
                    parameters={
                        "task": "content_classification",
                        "max_tokens": 400
                    },
                    depends_on=["page_intelligence", "content_detection"],
                    timeout=30.0,
                    fallback_enabled=False
                )
            ],
            "global_timeout": 90.0,
            "parallel_execution": False,
            "fail_fast": False,
            "metadata": {
                "description": "Extract and analyze content from web pages",
                "expected_time": "60-75 seconds",
                "accuracy": "high",
                "page_types": ["article", "blog", "news", "documentation"]
            }
        },
        
        WorkflowType.UI_ANALYSIS_COMPREHENSIVE: {
            "name": "Comprehensive UI Analysis",
            "layers": [
                LayerConfig(
                    name="page_intelligence",
                    layer_type=LayerType.INTELLIGENCE,
                    service_type="vision",
                    model_name="gpt-4-vision-preview",
                    parameters={"max_tokens": 1000},
                    depends_on=[],
                    timeout=25.0,
                    fallback_enabled=True
                ),
                LayerConfig(
                    name="primary_detection",
                    layer_type=LayerType.DETECTION,
                    service_type="vision",
                    model_name="omniparser",
                    parameters={
                        "imgsz": 1024,
                        "box_threshold": 0.03,
                        "iou_threshold": 0.1
                    },
                    depends_on=["page_intelligence"],
                    timeout=30.0,
                    fallback_enabled=True
                ),
                LayerConfig(
                    name="secondary_detection",
                    layer_type=LayerType.DETECTION,
                    service_type="vision",
                    model_name="florence-2",
                    parameters={
                        "task": "<OPEN_VOCABULARY_DETECTION>",
                        "text_input": "login form elements, input fields, buttons, checkboxes"
                    },
                    depends_on=["page_intelligence"],
                    timeout=25.0,
                    fallback_enabled=True
                ),
                LayerConfig(
                    name="detection_fusion",
                    layer_type=LayerType.TRANSFORMATION,
                    service_type="custom",
                    model_name="fusion_algorithm",
                    parameters={"fusion_method": "confidence_weighted"},
                    depends_on=["primary_detection", "secondary_detection"],
                    timeout=5.0,
                    fallback_enabled=False
                ),
                LayerConfig(
                    name="element_classification",
                    layer_type=LayerType.CLASSIFICATION,
                    service_type="vision",
                    model_name="gpt-4-vision-preview",
                    parameters={"max_tokens": 600},
                    depends_on=["page_intelligence", "detection_fusion"],
                    timeout=40.0,
                    fallback_enabled=False
                ),
                LayerConfig(
                    name="result_validation",
                    layer_type=LayerType.VALIDATION,
                    service_type="vision",
                    model_name="gpt-4.1-nano",
                    parameters={"validation_criteria": ["completeness", "consistency", "accuracy"]},
                    depends_on=["element_classification"],
                    timeout=15.0,
                    fallback_enabled=True
                )
            ],
            "global_timeout": 180.0,
            "parallel_execution": True,  # Enable parallel execution for detection layers
            "fail_fast": False,
            "metadata": {
                "description": "Most comprehensive UI analysis with multi-model fusion",
                "expected_time": "120-150 seconds",
                "accuracy": "very high"
            }
        }
    }
    
    @classmethod
    def get_config(cls, workflow_type: WorkflowType) -> StackedServiceConfig:
        """Get predefined configuration for a workflow type"""
        if workflow_type not in cls.PREDEFINED_CONFIGS:
            raise ValueError(f"Unknown workflow type: {workflow_type}")
        
        config_data = cls.PREDEFINED_CONFIGS[workflow_type]
        
        return StackedServiceConfig(
            name=config_data["name"],
            workflow_type=workflow_type,
            layers=config_data["layers"],
            global_timeout=config_data["global_timeout"],
            parallel_execution=config_data["parallel_execution"],
            fail_fast=config_data["fail_fast"],
            metadata=config_data["metadata"]
        )
    
    @classmethod
    def create_custom_config(
        cls,
        name: str,
        layers: List[LayerConfig],
        global_timeout: float = 120.0,
        parallel_execution: bool = False,
        fail_fast: bool = False,
        metadata: Dict[str, Any] = None
    ) -> StackedServiceConfig:
        """Create a custom configuration"""
        return StackedServiceConfig(
            name=name,
            workflow_type=WorkflowType.CUSTOM,
            layers=layers,
            global_timeout=global_timeout,
            parallel_execution=parallel_execution,
            fail_fast=fail_fast,
            metadata=metadata or {}
        )
    
    @classmethod
    def modify_config(
        cls,
        base_config: StackedServiceConfig,
        modifications: Dict[str, Any]
    ) -> StackedServiceConfig:
        """Modify an existing configuration"""
        # Create a copy
        new_config = StackedServiceConfig(
            name=base_config.name,
            workflow_type=base_config.workflow_type,
            layers=base_config.layers.copy(),
            global_timeout=base_config.global_timeout,
            parallel_execution=base_config.parallel_execution,
            fail_fast=base_config.fail_fast,
            metadata=base_config.metadata.copy()
        )
        
        # Apply modifications
        for key, value in modifications.items():
            if hasattr(new_config, key):
                setattr(new_config, key, value)
            elif key == "layer_modifications":
                # Modify specific layers
                for layer_name, layer_mods in value.items():
                    for layer in new_config.layers:
                        if layer.name == layer_name:
                            for mod_key, mod_value in layer_mods.items():
                                if hasattr(layer, mod_key):
                                    setattr(layer, mod_key, mod_value)
                                elif mod_key == "parameters":
                                    layer.parameters.update(mod_value)
        
        return new_config
    
    @classmethod
    def get_available_workflows(cls) -> Dict[WorkflowType, Dict[str, Any]]:
        """Get information about all available workflows"""
        workflows = {}
        
        for workflow_type in cls.PREDEFINED_CONFIGS:
            config_data = cls.PREDEFINED_CONFIGS[workflow_type]
            workflows[workflow_type] = {
                "name": config_data["name"],
                "layer_count": len(config_data["layers"]),
                "expected_time": config_data["metadata"].get("expected_time", "unknown"),
                "accuracy": config_data["metadata"].get("accuracy", "unknown"),
                "description": config_data["metadata"].get("description", "")
            }
        
        return workflows

# Convenience function for quick access
def get_ui_analysis_config(speed: str = "accurate") -> StackedServiceConfig:
    """Get UI analysis configuration by speed preference"""
    speed_mapping = {
        "fast": WorkflowType.UI_ANALYSIS_FAST,
        "accurate": WorkflowType.UI_ANALYSIS_ACCURATE,
        "comprehensive": WorkflowType.UI_ANALYSIS_COMPREHENSIVE
    }
    
    workflow_type = speed_mapping.get(speed.lower(), WorkflowType.UI_ANALYSIS_ACCURATE)
    return ConfigManager.get_config(workflow_type)