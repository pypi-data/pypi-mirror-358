"""
Stacked Services - Multi-model orchestration services

This module provides stacked services that combine multiple AI models 
in sequence or parallel to solve complex tasks.
"""

from .base_stacked_service import BaseStackedService, LayerConfig, LayerType, LayerResult
from .ui_analysis_service import UIAnalysisService
from .doc_analysis_service import DocAnalysisStackedService
from .flux_professional_service import FluxProfessionalService
from .config import ConfigManager, StackedServiceConfig, WorkflowType, get_ui_analysis_config

__all__ = [
    'BaseStackedService',
    'LayerConfig', 
    'LayerType',
    'LayerResult',
    'UIAnalysisService',
    'DocAnalysisStackedService',
    'FluxProfessionalService',
    'ConfigManager',
    'StackedServiceConfig',
    'WorkflowType',
    'get_ui_analysis_config'
]