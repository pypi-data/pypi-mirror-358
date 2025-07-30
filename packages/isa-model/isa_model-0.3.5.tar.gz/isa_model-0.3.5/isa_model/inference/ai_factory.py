#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Simplified AI Factory for creating inference services
Uses the new service architecture with proper base classes and centralized API key management
"""

from typing import Dict, Type, Any, Optional, Tuple, List, TYPE_CHECKING, cast
import logging
from isa_model.inference.providers.base_provider import BaseProvider
from isa_model.inference.services.base_service import BaseService
from isa_model.inference.base import ModelType
from isa_model.inference.services.vision.base_vision_service import BaseVisionService
from isa_model.inference.services.vision.base_image_gen_service import BaseImageGenService
from isa_model.inference.services.stacked import UIAnalysisService, BaseStackedService, DocAnalysisStackedService, FluxProfessionalService

if TYPE_CHECKING:
    from isa_model.inference.services.audio.base_stt_service import BaseSTTService
    from isa_model.inference.services.audio.base_tts_service import BaseTTSService

logger = logging.getLogger(__name__)

class AIFactory:
    """
    Simplified Factory for creating AI services with proper inheritance hierarchy
    API key management is handled by individual providers
    """
    
    _instance = None
    _is_initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the AI Factory."""
        if not self._is_initialized:
            self._providers: Dict[str, Type[BaseProvider]] = {}
            self._services: Dict[Tuple[str, ModelType], Type[BaseService]] = {}
            self._cached_services: Dict[str, BaseService] = {}
            self._initialize_services()
            AIFactory._is_initialized = True
    
    def _initialize_services(self):
        """Initialize available providers and services"""
        try:
            # Register Ollama services
            self._register_ollama_services()
            
            # Register OpenAI services
            self._register_openai_services()
            
            # Register Replicate services
            self._register_replicate_services()
            
            # Register ISA Modal services
            self._register_isa_services()
            
            # Register YYDS services
            self._register_yyds_services()
            
            logger.info("AI Factory initialized with centralized provider API key management")
            
        except Exception as e:
            logger.error(f"Error initializing services: {e}")
            logger.warning("Some services may not be available")
    
    def _register_ollama_services(self):
        """Register Ollama provider and services"""
        try:
            from isa_model.inference.providers.ollama_provider import OllamaProvider
            from isa_model.inference.services.llm.ollama_llm_service import OllamaLLMService
            from isa_model.inference.services.embedding.ollama_embed_service import OllamaEmbedService
            from isa_model.inference.services.vision.ollama_vision_service import OllamaVisionService
            
            self.register_provider('ollama', OllamaProvider)
            self.register_service('ollama', ModelType.LLM, OllamaLLMService)
            self.register_service('ollama', ModelType.EMBEDDING, OllamaEmbedService)
            self.register_service('ollama', ModelType.VISION, OllamaVisionService)
            
            logger.info("Ollama services registered successfully")
            
        except ImportError as e:
            logger.warning(f"Ollama services not available: {e}")
    
    def _register_openai_services(self):
        """Register OpenAI provider and services"""
        try:
            from isa_model.inference.providers.openai_provider import OpenAIProvider
            from isa_model.inference.services.llm.openai_llm_service import OpenAILLMService
            from isa_model.inference.services.audio.openai_tts_service import OpenAITTSService
            from isa_model.inference.services.audio.openai_stt_service import OpenAISTTService
            from isa_model.inference.services.embedding.openai_embed_service import OpenAIEmbedService
            from isa_model.inference.services.vision.openai_vision_service import OpenAIVisionService
            
            self.register_provider('openai', OpenAIProvider)
            self.register_service('openai', ModelType.LLM, OpenAILLMService)
            self.register_service('openai', ModelType.AUDIO, OpenAITTSService)
            self.register_service('openai', ModelType.EMBEDDING, OpenAIEmbedService)
            self.register_service('openai', ModelType.VISION, OpenAIVisionService)
            
            logger.info("OpenAI services registered successfully")
            
        except ImportError as e:
            logger.warning(f"OpenAI services not available: {e}")
    
    def _register_replicate_services(self):
        """Register Replicate provider and services"""
        try:
            from isa_model.inference.providers.replicate_provider import ReplicateProvider
            from isa_model.inference.services.vision.replicate_image_gen_service import ReplicateImageGenService
            from isa_model.inference.services.vision.replicate_vision_service import ReplicateVisionService
            from isa_model.inference.services.audio.replicate_tts_service import ReplicateTTSService
            
            self.register_provider('replicate', ReplicateProvider)
            # Register vision service for general vision tasks
            self.register_service('replicate', ModelType.VISION, ReplicateVisionService)
            # Register image generation service for FLUX, ControlNet, LoRA, Upscaling
            # Note: Using VISION type as IMAGE_GEN is not defined in ModelType
            # ReplicateImageGenService will be accessed through get_img() methods
            # Register audio service
            self.register_service('replicate', ModelType.AUDIO, ReplicateTTSService)
            
            logger.info("Replicate services registered successfully")
            
        except ImportError as e:
            logger.warning(f"Replicate services not available: {e}")
    
    def _register_isa_services(self):
        """Register ISA Modal provider and services"""
        try:
            from isa_model.inference.services.vision.isA_vision_service import ISAVisionService
            from isa_model.inference.providers.modal_provider import ModalProvider
            
            self.register_provider('modal', ModalProvider)
            self.register_service('modal', ModelType.VISION, ISAVisionService)
            
            logger.info("ISA Modal services registered successfully")
            
        except ImportError as e:
            logger.warning(f"ISA Modal services not available: {e}")
    
    def _register_yyds_services(self):
        """Register YYDS provider and services"""
        try:
            from isa_model.inference.providers.yyds_provider import YydsProvider
            from isa_model.inference.services.llm.yyds_llm_service import YydsLLMService
            
            self.register_provider('yyds', YydsProvider)
            self.register_service('yyds', ModelType.LLM, YydsLLMService)
            
            logger.info("YYDS services registered successfully")
            
        except ImportError as e:
            logger.warning(f"YYDS services not available: {e}")
    
    def register_provider(self, name: str, provider_class: Type[BaseProvider]) -> None:
        """Register an AI provider"""
        self._providers[name] = provider_class
    
    def register_service(self, provider_name: str, model_type: ModelType, 
                        service_class: Type[BaseService]) -> None:
        """Register a service type with its provider"""
        self._services[(provider_name, model_type)] = service_class
    
    def create_service(self, provider_name: str, model_type: ModelType, 
                      model_name: str, config: Optional[Dict[str, Any]] = None) -> BaseService:
        """Create a service instance with provider-managed configuration"""
        try:
            cache_key = f"{provider_name}_{model_type}_{model_name}"
            
            if cache_key in self._cached_services:
                return self._cached_services[cache_key]
            
            # Get provider and service classes
            provider_class = self._providers.get(provider_name)
            service_class = self._services.get((provider_name, model_type))
            
            if not provider_class:
                raise ValueError(f"No provider registered for '{provider_name}'")
            
            if not service_class:
                raise ValueError(
                    f"No service registered for provider '{provider_name}' and model type '{model_type}'"
                )
            
            # Create provider with user config (provider handles .env loading)
            provider = provider_class(config=config)
            service = service_class(provider=provider, model_name=model_name)
            
            self._cached_services[cache_key] = service
            return service
            
        except Exception as e:
            logger.error(f"Error creating service: {e}")
            raise
    
    # Convenient methods for common services with updated defaults
    def get_llm_service(self, model_name: Optional[str] = None, provider: Optional[str] = None,
                       config: Optional[Dict[str, Any]] = None) -> BaseService:
        """
        Get a LLM service instance with automatic defaults
        
        Args:
            model_name: Name of the model to use (defaults: OpenAI="gpt-4.1-nano", Ollama="llama3.2:3b", YYDS="claude-sonnet-4-20250514")
            provider: Provider name (defaults to 'openai' for production, 'ollama' for dev)
            config: Optional configuration dictionary (auto-loads from .env if not provided)
                   Can include: streaming=True/False, temperature, max_tokens, etc.
            
        Returns:
            LLM service instance
        """
        # Set defaults based on provider
        if provider == "openai":
            final_model_name = model_name or "gpt-4.1-nano"
            final_provider = provider
        elif provider == "ollama":
            final_model_name = model_name or "llama3.2:3b-instruct-fp16"
            final_provider = provider
        elif provider == "yyds":
            final_model_name = model_name or "claude-sonnet-4-20250514"
            final_provider = provider
        else:
            # Default provider selection - OpenAI with cheapest model
            final_provider = provider or "openai"
            if final_provider == "openai":
                final_model_name = model_name or "gpt-4.1-nano"
            else:
                final_model_name = model_name or "llama3.2:3b-instruct-fp16"
        
        return self.create_service(final_provider, ModelType.LLM, final_model_name, config)
    
    def get_embedding_service(self, model_name: Optional[str] = None, provider: Optional[str] = None,
                             config: Optional[Dict[str, Any]] = None) -> BaseService:
        """
        Get an embedding service instance with automatic defaults
        
        Args:
            model_name: Name of the model to use (defaults: OpenAI="text-embedding-3-small", Ollama="bge-m3")
            provider: Provider name (defaults to 'openai' for production, 'ollama' for dev)
            config: Optional configuration dictionary (auto-loads from .env if not provided)
            
        Returns:
            Embedding service instance
        """
        # Set defaults based on provider
        if provider == "openai":
            final_model_name = model_name or "text-embedding-3-small"
            final_provider = provider
        elif provider == "ollama":
            final_model_name = model_name or "bge-m3"
            final_provider = provider
        else:
            # Default provider selection
            final_provider = provider or "openai"
            if final_provider == "openai":
                final_model_name = model_name or "text-embedding-3-small"
            else:
                final_model_name = model_name or "bge-m3"
        
        return self.create_service(final_provider, ModelType.EMBEDDING, final_model_name, config)
    
    def get_vision_service(self, model_name: Optional[str] = None, provider: Optional[str] = None,
                          config: Optional[Dict[str, Any]] = None) -> BaseVisionService:
        """
        Get a vision service instance with automatic defaults
        
        Args:
            model_name: Name of the model to use (defaults: OpenAI="gpt-4.1-mini", Ollama="gemma3:4b")
            provider: Provider name (defaults to 'openai' for production, 'ollama' for dev)
            config: Optional configuration dictionary (auto-loads from .env if not provided)
            
        Returns:
            Vision service instance
        """
        # Set defaults based on provider
        if provider == "openai":
            final_model_name = model_name or "gpt-4.1-mini"
            final_provider = provider
        elif provider == "ollama":
            final_model_name = model_name or "llama3.2-vision:latest"
            final_provider = provider
        else:
            # Default provider selection
            final_provider = provider or "openai"
            if final_provider == "openai":
                final_model_name = model_name or "gpt-4.1-mini"
            else:
                final_model_name = model_name or "llama3.2-vision:latest"
        
        return cast(BaseVisionService, self.create_service(final_provider, ModelType.VISION, final_model_name, config))
    
    def get_image_gen(self, model_name: Optional[str] = None, provider: Optional[str] = None,
                     config: Optional[Dict[str, Any]] = None) -> 'BaseImageGenService':
        """
        Get an image generation service instance with automatic defaults
        
        Args:
            model_name: Name of the model to use. Supports:
                - FLUX models: "flux-pro", "flux-schnell", "flux-dev"
                - ControlNet: "flux-controlnet", "xlabs-ai/flux-dev-controlnet"  
                - LoRA: "flux-lora", "flux-dev-lora"
                - InstantID: "instant-id", "zsxkib/instant-id"
                - Character: "consistent-character", "fofr/consistent-character"
                - Upscaling: "ultimate-upscaler", "ultimate-sd-upscale"
                - Detail: "adetailer"
            provider: Provider name (defaults to 'replicate')
            config: Optional configuration dictionary
            
        Returns:
            Image generation service instance with FLUX, ControlNet, LoRA, InstantID, Upscaling support
        """
        # Set defaults based on provider
        final_provider = provider or "replicate"
        
        # Default model selection
        if not model_name:
            final_model_name = "black-forest-labs/flux-schnell"
        else:
            # Map short names to full Replicate model names
            model_mapping = {
                "flux-pro": "black-forest-labs/flux-pro",
                "flux-schnell": "black-forest-labs/flux-schnell", 
                "flux-dev": "black-forest-labs/flux-dev",
                "flux-controlnet": "xlabs-ai/flux-dev-controlnet",
                "flux-lora": "xlabs-ai/flux-lora",
                "instant-id": "zsxkib/instant-id",
                "consistent-character": "fofr/consistent-character", 
                "ultimate-upscaler": "philz1337x/clarity-upscaler",
                "ultimate-sd-upscale": "philz1337x/clarity-upscaler",
                "adetailer": "sczhou/codeformer"
            }
            final_model_name = model_mapping.get(model_name, model_name)
        
        # Create ReplicateImageGenService directly for image generation
        try:
            from isa_model.inference.services.vision.replicate_image_gen_service import ReplicateImageGenService
            from isa_model.inference.providers.replicate_provider import ReplicateProvider
            
            # Create provider with config
            provider_instance = ReplicateProvider(config=config)
            service = ReplicateImageGenService(provider=provider_instance, model_name=final_model_name)
            
            return service
            
        except ImportError as e:
            logger.error(f"Failed to import ReplicateImageGenService: {e}")
            raise ValueError(f"Image generation service not available: {e}")
        except Exception as e:
            logger.error(f"Failed to create image generation service: {e}")
            raise
    
    def get_image_generation_service(self, model_name: Optional[str] = None, provider: Optional[str] = None,
                                   config: Optional[Dict[str, Any]] = None) -> 'BaseImageGenService':
        """Alias for get_image_gen() method"""
        return self.get_image_gen(model_name, provider, config)
    
    def get_img(self, type: str = "t2i", model_name: Optional[str] = None, provider: Optional[str] = None,
                config: Optional[Dict[str, Any]] = None) -> 'BaseImageGenService':
        """
        Get an image generation service with type-specific defaults
        
        Args:
            type: Image generation type:
                  - "t2i" (text-to-image): Uses flux-schnell ($3 per 1000 images)
                  - "i2i" (image-to-image): Uses flux-kontext-pro ($0.04 per image)
            model_name: Optional model name override
            provider: Provider name (defaults to 'replicate')
            config: Optional configuration dictionary
            
        Returns:
            Image generation service instance
            
        Usage:
            # Text-to-image (default)
            img_service = AIFactory().get_img()
            img_service = AIFactory().get_img(type="t2i")
            
            # Image-to-image
            img_service = AIFactory().get_img(type="i2i")
            
            # Custom model
            img_service = AIFactory().get_img(type="t2i", model_name="custom-model")
        """
        # Set defaults based on type
        final_provider = provider or "replicate"
        
        if type == "t2i":
            # Text-to-image: flux-schnell
            final_model_name = model_name or "black-forest-labs/flux-schnell"
        elif type == "i2i":
            # Image-to-image: flux-kontext-pro
            final_model_name = model_name or "black-forest-labs/flux-kontext-pro"
        else:
            raise ValueError(f"Unknown image generation type: {type}. Use 't2i' or 'i2i'")
        
        # Use the new get_image_gen method
        return self.get_image_gen(final_model_name, final_provider, config)
    
    def get_audio_service(self, model_name: Optional[str] = None, provider: Optional[str] = None,
                         config: Optional[Dict[str, Any]] = None) -> BaseService:
        """
        Get an audio service instance (TTS) with automatic defaults
        
        Args:
            model_name: Name of the model to use (defaults: OpenAI="tts-1")
            provider: Provider name (defaults to 'openai')
            config: Optional configuration dictionary (auto-loads from .env if not provided)
            
        Returns:
            Audio service instance
        """
        # Set defaults based on provider
        final_provider = provider or "openai"
        if final_provider == "openai":
            final_model_name = model_name or "tts-1"
        else:
            final_model_name = model_name or "tts-1"
        
        return self.create_service(final_provider, ModelType.AUDIO, final_model_name, config)
    
    def get_tts_service(self, model_name: Optional[str] = None, provider: Optional[str] = None,
                       config: Optional[Dict[str, Any]] = None) -> 'BaseTTSService':
        """
        Get a Text-to-Speech service instance with automatic defaults
        
        Args:
            model_name: Name of the model to use (defaults: Replicate="kokoro-82m", OpenAI="tts-1")
            provider: Provider name (defaults to 'replicate' for production, 'openai' for dev)
            config: Optional configuration dictionary (auto-loads from .env if not provided)
            
        Returns:
            TTS service instance
        """
        # Set defaults based on provider
        if provider == "replicate":
            model_name = model_name or "kokoro-82m"
        elif provider == "openai":
            model_name = model_name or "tts-1"
        else:
            # Default provider selection
            provider = provider or "replicate"
            if provider == "replicate":
                model_name = model_name or "kokoro-82m"
            else:
                model_name = model_name or "tts-1"
        
        # Ensure model_name is never None
        if model_name is None:
            model_name = "tts-1"
        
        if provider == "replicate":
            from isa_model.inference.services.audio.replicate_tts_service import ReplicateTTSService
            from isa_model.inference.providers.replicate_provider import ReplicateProvider
            
            # Use full model name for Replicate
            if model_name == "kokoro-82m":
                model_name = "jaaari/kokoro-82m:f559560eb822dc509045f3921a1921234918b91739db4bf3daab2169b71c7a13"
            
            provider_instance = ReplicateProvider(config=config)
            return ReplicateTTSService(provider=provider_instance, model_name=model_name)
        else:
            return cast('BaseTTSService', self.get_audio_service(model_name, provider, config))
    
    def get_stt_service(self, model_name: Optional[str] = None, provider: Optional[str] = None,
                       config: Optional[Dict[str, Any]] = None) -> 'BaseSTTService':
        """
        Get a Speech-to-Text service instance with automatic defaults
        
        Args:
            model_name: Name of the model to use (defaults: "whisper-1")
            provider: Provider name (defaults to 'openai')
            config: Optional configuration dictionary (auto-loads from .env if not provided)
            
        Returns:
            STT service instance
        """
        # Set defaults based on provider
        provider = provider or "openai"
        if provider == "openai":
            model_name = model_name or "whisper-1"
        
        # Ensure model_name is never None
        if model_name is None:
            model_name = "whisper-1"
        
        from isa_model.inference.services.audio.openai_stt_service import OpenAISTTService
        from isa_model.inference.providers.openai_provider import OpenAIProvider
        
        # Create provider and service directly with config
        provider_instance = OpenAIProvider(config=config)
        return OpenAISTTService(provider=provider_instance, model_name=model_name)
    
    def get_available_services(self) -> Dict[str, List[str]]:
        """Get information about available services"""
        services = {}
        for (provider, model_type), service_class in self._services.items():
            if provider not in services:
                services[provider] = []
            services[provider].append(f"{model_type.value}: {service_class.__name__}")
        return services
    
    def clear_cache(self):
        """Clear the service cache"""
        self._cached_services.clear()
        logger.info("Service cache cleared")
    
    @classmethod
    def get_instance(cls) -> 'AIFactory':
        """Get the singleton instance"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    # Alias method for cleaner API
    def get_llm(self, model_name: Optional[str] = None, provider: Optional[str] = None,
                config: Optional[Dict[str, Any]] = None) -> BaseService:
        """
        Alias for get_llm_service with cleaner naming
        
        Usage:
            llm = AIFactory().get_llm()  # Uses gpt-4.1-nano by default
            llm = AIFactory().get_llm(model_name="llama3.2", provider="ollama")
            llm = AIFactory().get_llm(provider="yyds")  # Uses claude-sonnet-4-20250514 by default
            llm = AIFactory().get_llm(model_name="gpt-4.1-mini", provider="openai", config={"streaming": True})
        """
        return self.get_llm_service(model_name, provider, config)
    
    def get_embed(self, model_name: Optional[str] = None, provider: Optional[str] = None,
                     config: Optional[Dict[str, Any]] = None) -> BaseService:
        """
        Get embedding service with automatic defaults
        
        Args:
            model_name: Name of the model to use (defaults: OpenAI="text-embedding-3-small", Ollama="bge-m3")
            provider: Provider name (defaults to 'openai' for production)
            config: Optional configuration dictionary (auto-loads from .env if not provided)
            
        Returns:
            Embedding service instance
            
        Usage:
            # Default (OpenAI text-embedding-3-small)
            embed = AIFactory().get_embed()
            
            # Custom model
            embed = AIFactory().get_embed(model_name="text-embedding-3-large", provider="openai")
            
            # Development (Ollama)
            embed = AIFactory().get_embed(provider="ollama")
        """
        return self.get_embedding_service(model_name, provider, config)

    def get_stt(self, model_name: Optional[str] = None, provider: Optional[str] = None,
                config: Optional[Dict[str, Any]] = None) -> 'BaseSTTService':
        """
        Get Speech-to-Text service with automatic defaults
        
        Args:
            model_name: Name of the model to use (defaults: "whisper-1")
            provider: Provider name (defaults to 'openai')
            config: Optional configuration dictionary (auto-loads from .env if not provided)
            
        Returns:
            STT service instance
            
        Usage:
            # Default (OpenAI whisper-1)
            stt = AIFactory().get_stt()
            
            # Custom configuration
            stt = AIFactory().get_stt(model_name="whisper-1", provider="openai")
        """
        return self.get_stt_service(model_name, provider, config)

    def get_tts(self, model_name: Optional[str] = None, provider: Optional[str] = None,
                config: Optional[Dict[str, Any]] = None) -> 'BaseTTSService':
        """
        Get Text-to-Speech service with automatic defaults
        
        Args:
            model_name: Name of the model to use (defaults: Replicate="kokoro-82m", OpenAI="tts-1")
            provider: Provider name (defaults to 'replicate' for production, 'openai' for dev)
            config: Optional configuration dictionary (auto-loads from .env if not provided)
            
        Returns:
            TTS service instance
            
        Usage:
            # Default (Replicate kokoro-82m)
            tts = AIFactory().get_tts()
            
            # Development (OpenAI tts-1)
            tts = AIFactory().get_tts(provider="openai")
            
            # Custom model
            tts = AIFactory().get_tts(model_name="tts-1-hd", provider="openai")
        """
        return self.get_tts_service(model_name, provider, config)
    
    def get_vision_model(self, model_name: str, provider: str,
                        config: Optional[Dict[str, Any]] = None) -> BaseService:
        """Alias for get_vision_service and get_image_generation_service"""
        if provider == "replicate":
            return self.get_image_generation_service(model_name, provider, config)
        else:
            return self.get_vision_service(model_name, provider, config)
    
    def get_vision(
        self,
        model_name: Optional[str] = None,
        provider: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> 'BaseVisionService':
        """
        Get vision service with automatic defaults
        
        Args:
            model_name: Model name (default: gpt-4.1-nano)
            provider: Provider name (default: openai)
            config: Optional configuration override
            
        Returns:
            Vision service instance
        """
        # Set defaults
        if provider is None:
            provider = "openai"
        if model_name is None:
            model_name = "gpt-4.1-nano"
        
        return self.get_vision_service(
            model_name=model_name,
            provider=provider,
            config=config
        )
    
    def get_provider(self, provider_name: str, config: Optional[Dict[str, Any]] = None) -> BaseProvider:
        """
        Get a provider instance
        
        Args:
            provider_name: Name of the provider ('openai', 'ollama', 'replicate')
            config: Optional configuration override
            
        Returns:
            Provider instance
        """
        if provider_name not in self._providers:
            raise ValueError(f"No provider registered for '{provider_name}'")
        
        provider_class = self._providers[provider_name]
        return provider_class(config=config)
    
    def get_stacked(
        self,
        service_name: str,
        config: Optional[Dict[str, Any]] = None
    ) -> BaseStackedService:
        """
        Get a stacked service by name with automatic defaults
        
        Args:
            service_name: Name of the stacked service ('ui_analysis', etc.)
            config: Optional configuration override
            
        Returns:
            Stacked service instance
            
        Usage:
            ui_service = AIFactory().get_stacked("ui_analysis", {"task_type": "search"})
        """
        if service_name == "ui_analysis":
            return UIAnalysisService(self, config)
        elif service_name == "search_analysis":
            if config is None:
                config = {}
            config["task_type"] = "search"
            return UIAnalysisService(self, config)
        elif service_name == "content_analysis":
            if config is None:
                config = {}
            config["task_type"] = "content"
            return UIAnalysisService(self, config)
        elif service_name == "navigation_analysis":
            if config is None:
                config = {}
            config["task_type"] = "navigation"
            return UIAnalysisService(self, config)
        elif service_name == "doc_analysis":
            return DocAnalysisStackedService(self, config)
        elif service_name == "flux_professional":
            return FluxProfessionalService(self)
        else:
            raise ValueError(f"Unknown stacked service: {service_name}. Available: ui_analysis, search_analysis, content_analysis, navigation_analysis, doc_analysis, flux_professional")
    
    def get_ui_analysis(
        self,
        task_type: str = "login",
        config: Optional[Dict[str, Any]] = None
    ) -> UIAnalysisService:
        """
        Get UI Analysis service with task-specific configuration
        
        Args:
            task_type: Type of UI task ('login', 'search', 'content', 'navigation')
            config: Optional configuration override
        
        Usage:
            # For login pages (default)
            ui_service = AIFactory().get_ui_analysis()
            
            # For search pages
            ui_service = AIFactory().get_ui_analysis(task_type="search")
            
            # For content extraction
            ui_service = AIFactory().get_ui_analysis(task_type="content")
        """
        if config is None:
            config = {}
        config["task_type"] = task_type
        return cast(UIAnalysisService, self.get_stacked("ui_analysis", config))
    
    def get_doc_analysis(
        self,
        config: Optional[Dict[str, Any]] = None
    ) -> DocAnalysisStackedService:
        """
        Get Document Analysis service with 5-step pipeline
        
        Args:
            config: Optional configuration override
        
        Usage:
            # Basic document analysis
            doc_service = AIFactory().get_doc_analysis()
            
            # Analyze a document image
            result = await doc_service.analyze_document("document.png")
            
            # Get structured data ready for business mapping
            structured_data = result["final_output"]["final_structured_data"]
        """
        return cast(DocAnalysisStackedService, self.get_stacked("doc_analysis", config))
    
    def get_flux_professional(
        self,
        config: Optional[Dict[str, Any]] = None
    ) -> FluxProfessionalService:
        """
        Get FLUX Professional Pipeline service for multi-stage image generation
        
        Args:
            config: Optional configuration override
        
        Usage:
            # Basic professional image generation
            flux_service = AIFactory().get_flux_professional()
            
            # Generate professional image with character consistency
            result = await flux_service.invoke({
                "prompt": "portrait of a warrior in fantasy armor",
                "face_image": "reference_face.jpg",  # For character consistency
                "lora_style": "realism",
                "upscale_factor": 4
            })
            
            # Get final high-quality image
            final_image_url = result["final_output"]["image_url"]
        """
        return cast(FluxProfessionalService, self.get_stacked("flux_professional", config)) 