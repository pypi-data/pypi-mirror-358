"""
Triton LLM Service

Provides LLM-specific functionality using Triton Inference Server as the backend.
Integrates with the existing TritonProvider for low-level operations.
"""

import logging
from typing import Dict, Any, List, Optional, Union, AsyncGenerator
import json
import asyncio

from ..base_service import BaseService
from ...providers.triton_provider import TritonProvider
from ...base import ModelType, Capability

logger = logging.getLogger(__name__)


class TritonLLMService(BaseService):
    """
    LLM service using Triton Inference Server.
    
    This service provides high-level LLM operations like text generation,
    chat completion, and streaming responses using Triton as the backend.
    
    Features:
    - Text generation with customizable parameters
    - Chat completion with conversation context
    - Streaming responses for real-time interaction
    - Multiple model support
    - Automatic model loading and management
    - Integration with model registry
    
    Example:
        ```python
        from isa_model.inference.services.llm import TritonLLMService
        
        # Initialize service
        service = TritonLLMService({
            "triton_url": "localhost:8001",
            "default_model": "gemma-4b-alpaca"
        })
        
        # Generate text
        response = await service.generate_text(
            prompt="What is artificial intelligence?",
            model_name="gemma-4b-alpaca",
            max_tokens=100
        )
        
        # Chat completion
        messages = [
            {"role": "user", "content": "Hello, how are you?"}
        ]
        response = await service.chat_completion(
            messages=messages,
            model_name="gemma-4b-alpaca"
        )
        
        # Streaming generation
        async for chunk in service.generate_text_stream(
            prompt="Tell me a story",
            model_name="gemma-4b-alpaca"
        ):
            print(chunk["text"], end="")
        ```
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Triton LLM service.
        
        Args:
            config: Service configuration including Triton connection details
        """
        super().__init__(config)
        
        # Initialize Triton provider
        self.triton_provider = TritonProvider(config)
        
        # Service configuration
        self.default_model = config.get("default_model", "model")
        self.max_tokens_limit = config.get("max_tokens_limit", 2048)
        self.temperature_default = config.get("temperature_default", 0.7)
        self.top_p_default = config.get("top_p_default", 0.9)
        self.top_k_default = config.get("top_k_default", 50)
        
        # Chat templates
        self.chat_templates = {
            "gemma": self._format_gemma_chat,
            "llama": self._format_llama_chat,
            "default": self._format_default_chat
        }
        
        logger.info(f"TritonLLMService initialized with default model: {self.default_model}")
    
    async def initialize(self) -> bool:
        """Initialize the service and check Triton connectivity"""
        try:
            # Check if Triton server is live
            if not self.triton_provider.is_server_live():
                logger.error("Triton server is not live")
                return False
            
            # Check if default model is ready
            if not self.triton_provider.is_model_ready(self.default_model):
                logger.warning(f"Default model {self.default_model} is not ready")
            
            logger.info("TritonLLMService initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize TritonLLMService: {e}")
            return False
    
    async def generate_text(self, 
                           prompt: str,
                           model_name: Optional[str] = None,
                           max_tokens: int = 100,
                           temperature: float = None,
                           top_p: float = None,
                           top_k: int = None,
                           stop_sequences: Optional[List[str]] = None,
                           system_prompt: Optional[str] = None,
                           **kwargs) -> Dict[str, Any]:
        """
        Generate text using the specified model.
        
        Args:
            prompt: Input text prompt
            model_name: Name of the model to use (uses default if not specified)
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature (0.0 to 1.0)
            top_p: Top-p sampling parameter
            top_k: Top-k sampling parameter
            stop_sequences: List of sequences to stop generation
            system_prompt: System prompt for instruction-following models
            **kwargs: Additional generation parameters
            
        Returns:
            Dictionary containing generated text and metadata
        """
        try:
            # Use default model if not specified
            model_name = model_name or self.default_model
            
            # Validate parameters
            max_tokens = min(max_tokens, self.max_tokens_limit)
            temperature = temperature if temperature is not None else self.temperature_default
            top_p = top_p if top_p is not None else self.top_p_default
            top_k = top_k if top_k is not None else self.top_k_default
            
            # Prepare generation parameters
            params = {
                "temperature": temperature,
                "max_tokens": max_tokens,
                "top_p": top_p,
                "top_k": top_k,
                **kwargs
            }
            
            if system_prompt:
                params["system_prompt"] = system_prompt
            
            if stop_sequences:
                params["stop_sequences"] = stop_sequences
            
            logger.debug(f"Generating text with model {model_name}, prompt length: {len(prompt)}")
            
            # Call Triton provider
            result = await self.triton_provider.completions(
                prompt=prompt,
                model_name=model_name,
                params=params
            )
            
            if "error" in result:
                logger.error(f"Text generation failed: {result['error']}")
                return {
                    "success": False,
                    "error": result["error"],
                    "model_name": model_name
                }
            
            # Format response
            response = {
                "success": True,
                "text": result["completion"],
                "model_name": model_name,
                "usage": result.get("metadata", {}).get("token_usage", {}),
                "parameters": {
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "top_p": top_p,
                    "top_k": top_k
                }
            }
            
            logger.debug(f"Text generation completed, output length: {len(response['text'])}")
            return response
            
        except Exception as e:
            logger.error(f"Error in generate_text: {e}")
            return {
                "success": False,
                "error": str(e),
                "model_name": model_name or self.default_model
            }
    
    async def chat_completion(self,
                             messages: List[Dict[str, str]],
                             model_name: Optional[str] = None,
                             max_tokens: int = 100,
                             temperature: float = None,
                             top_p: float = None,
                             top_k: int = None,
                             stop_sequences: Optional[List[str]] = None,
                             **kwargs) -> Dict[str, Any]:
        """
        Generate chat completion using conversation messages.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model_name: Name of the model to use
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature
            top_p: Top-p sampling parameter
            top_k: Top-k sampling parameter
            stop_sequences: List of sequences to stop generation
            **kwargs: Additional parameters
            
        Returns:
            Dictionary containing the assistant's response and metadata
        """
        try:
            # Use default model if not specified
            model_name = model_name or self.default_model
            
            # Format messages into a prompt
            prompt = self._format_chat_messages(messages, model_name)
            
            logger.debug(f"Chat completion with {len(messages)} messages, model: {model_name}")
            
            # Generate response
            result = await self.generate_text(
                prompt=prompt,
                model_name=model_name,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
                stop_sequences=stop_sequences,
                **kwargs
            )
            
            if not result["success"]:
                return result
            
            # Format as chat completion response
            response = {
                "success": True,
                "message": {
                    "role": "assistant",
                    "content": result["text"]
                },
                "model_name": model_name,
                "usage": result.get("usage", {}),
                "parameters": result.get("parameters", {})
            }
            
            logger.debug("Chat completion completed successfully")
            return response
            
        except Exception as e:
            logger.error(f"Error in chat_completion: {e}")
            return {
                "success": False,
                "error": str(e),
                "model_name": model_name or self.default_model
            }
    
    async def generate_text_stream(self,
                                  prompt: str,
                                  model_name: Optional[str] = None,
                                  max_tokens: int = 100,
                                  temperature: float = None,
                                  top_p: float = None,
                                  top_k: int = None,
                                  stop_sequences: Optional[List[str]] = None,
                                  **kwargs) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Generate text with streaming response.
        
        Args:
            prompt: Input text prompt
            model_name: Name of the model to use
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature
            top_p: Top-p sampling parameter
            top_k: Top-k sampling parameter
            stop_sequences: List of sequences to stop generation
            **kwargs: Additional parameters
            
        Yields:
            Dictionary chunks containing partial text and metadata
        """
        try:
            # For now, simulate streaming by chunking the complete response
            # TODO: Implement true streaming when Triton supports it
            
            result = await self.generate_text(
                prompt=prompt,
                model_name=model_name,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
                stop_sequences=stop_sequences,
                **kwargs
            )
            
            if not result["success"]:
                yield {
                    "success": False,
                    "error": result["error"],
                    "model_name": model_name or self.default_model
                }
                return
            
            # Simulate streaming by yielding chunks
            text = result["text"]
            chunk_size = 10  # Characters per chunk
            
            for i in range(0, len(text), chunk_size):
                chunk = text[i:i + chunk_size]
                
                yield {
                    "success": True,
                    "text": chunk,
                    "is_complete": i + chunk_size >= len(text),
                    "model_name": model_name or self.default_model
                }
                
                # Small delay to simulate streaming
                await asyncio.sleep(0.05)
            
        except Exception as e:
            logger.error(f"Error in generate_text_stream: {e}")
            yield {
                "success": False,
                "error": str(e),
                "model_name": model_name or self.default_model
            }
    
    async def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """Get information about a specific model"""
        try:
            if not self.triton_provider.is_model_ready(model_name):
                return {
                    "success": False,
                    "error": f"Model {model_name} is not ready"
                }
            
            metadata = self.triton_provider.get_model_metadata(model_name)
            config = self.triton_provider.get_model_config(model_name)
            
            return {
                "success": True,
                "model_name": model_name,
                "metadata": metadata,
                "config": config,
                "is_ready": True
            }
            
        except Exception as e:
            logger.error(f"Error getting model info for {model_name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "model_name": model_name
            }
    
    async def list_available_models(self) -> List[str]:
        """List all available models"""
        try:
            return self.triton_provider.get_models(ModelType.LLM)
        except Exception as e:
            logger.error(f"Error listing models: {e}")
            return []
    
    def _format_chat_messages(self, messages: List[Dict[str, str]], model_name: str) -> str:
        """Format chat messages into a prompt based on model type"""
        # Determine chat template based on model name
        template_key = "default"
        if "gemma" in model_name.lower():
            template_key = "gemma"
        elif "llama" in model_name.lower():
            template_key = "llama"
        
        formatter = self.chat_templates.get(template_key, self.chat_templates["default"])
        return formatter(messages)
    
    def _format_gemma_chat(self, messages: List[Dict[str, str]]) -> str:
        """Format messages for Gemma models"""
        formatted = ""
        
        for message in messages:
            role = message["role"]
            content = message["content"]
            
            if role == "system":
                formatted += f"<start_of_turn>system\n{content}<end_of_turn>\n"
            elif role == "user":
                formatted += f"<start_of_turn>user\n{content}<end_of_turn>\n"
            elif role == "assistant":
                formatted += f"<start_of_turn>model\n{content}<end_of_turn>\n"
        
        # Add the start token for the assistant response
        formatted += "<start_of_turn>model\n"
        
        return formatted
    
    def _format_llama_chat(self, messages: List[Dict[str, str]]) -> str:
        """Format messages for Llama models"""
        formatted = "<s>"
        
        for message in messages:
            role = message["role"]
            content = message["content"]
            
            if role == "system":
                formatted += f"[INST] <<SYS>>\n{content}\n<</SYS>>\n\n"
            elif role == "user":
                if formatted.endswith("<s>"):
                    formatted += f"[INST] {content} [/INST]"
                else:
                    formatted += f"<s>[INST] {content} [/INST]"
            elif role == "assistant":
                formatted += f" {content} </s>"
        
        return formatted
    
    def _format_default_chat(self, messages: List[Dict[str, str]]) -> str:
        """Default chat formatting"""
        formatted = ""
        
        for message in messages:
            role = message["role"]
            content = message["content"]
            
            if role == "system":
                formatted += f"System: {content}\n\n"
            elif role == "user":
                formatted += f"User: {content}\n\n"
            elif role == "assistant":
                formatted += f"Assistant: {content}\n\n"
        
        # Add prompt for assistant response
        formatted += "Assistant:"
        
        return formatted
    
    def get_capabilities(self) -> List[Capability]:
        """Get service capabilities"""
        return [
            Capability.CHAT,
            Capability.COMPLETION
        ]
    
    def get_supported_models(self) -> List[str]:
        """Get list of supported model types"""
        return [
            "gemma-2-2b-it",
            "gemma-2-4b-it", 
            "gemma-2-7b-it",
            "llama-2-7b-chat",
            "llama-2-13b-chat",
            "mistral-7b-instruct",
            "custom-models"  # Support for custom deployed models
        ] 