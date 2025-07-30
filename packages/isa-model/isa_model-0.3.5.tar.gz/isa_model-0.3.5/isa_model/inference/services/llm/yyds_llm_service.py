import logging
from typing import Dict, Any, List, Union, AsyncGenerator

# (�� OpenAI �
from openai import AsyncOpenAI

from isa_model.inference.services.llm.base_llm_service import BaseLLMService
from isa_model.inference.providers.base_provider import BaseProvider
from isa_model.inference.billing_tracker import ServiceType

logger = logging.getLogger(__name__)

class YydsLLMService(BaseLLMService):
    """YYDS LLM service implementation with unified invoke interface"""
    
    def __init__(self, provider: 'BaseProvider', model_name: str = "claude-sonnet-4-20250514"):
        super().__init__(provider, model_name)
        
        # Get full configuration from provider (including sensitive data)
        provider_config = provider.get_full_config()
        
        # Initialize AsyncOpenAI client with provider configuration
        try:
            if not provider_config.get("api_key"):
                raise ValueError("YYDS API key not found in provider configuration")
            
            self.client = AsyncOpenAI(
                api_key=provider_config["api_key"],
                base_url=provider_config.get("base_url", "https://api.yyds.com/v1"),
                organization=provider_config.get("organization")
            )
            
            logger.info(f"Initialized YydsLLMService with model {self.model_name} and endpoint {self.client.base_url}")
            
        except Exception as e:
            logger.error(f"Failed to initialize YYDS client: {e}")
            raise ValueError(f"Failed to initialize YYDS client. Check your API key configuration: {e}") from e
            
        self.last_token_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        self.total_token_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0, "requests_count": 0}
        
    
    def _create_bound_copy(self) -> 'YydsLLMService':
        """Create a copy of this service for tool binding"""
        bound_service = YydsLLMService(self.provider, self.model_name)
        bound_service._bound_tools = self._bound_tools.copy()
        return bound_service
    
    def bind_tools(self, tools: List[Any], **kwargs) -> 'YydsLLMService':
        """
        Bind tools to this LLM service for function calling
        
        Args:
            tools: List of tools (functions, dicts, or LangChain tools)
            **kwargs: Additional arguments for tool binding
            
        Returns:
            New LLM service instance with tools bound
        """
        # Create a copy of this service
        bound_service = self._create_bound_copy()
        
        # Use base class method to bind tools
        bound_service._bound_tools = tools
        
        return bound_service
    
    async def astream(self, input_data: Union[str, List[Dict[str, str]], Any]) -> AsyncGenerator[str, None]:
        """
        True streaming method - yields tokens one by one as they arrive
        
        Args:
            input_data: Same as ainvoke
            
        Yields:
            Individual tokens as they arrive from the API
        """
        try:
            # Use adapter manager to prepare messages
            messages = self._prepare_messages(input_data)
            
            # Prepare request kwargs
            kwargs = {
                "model": self.model_name,
                "messages": messages,
                "temperature": self.config.get("temperature", 0.7),
                "max_tokens": self.config.get("max_tokens", 1024),
                "stream": True
            }
            
            # Add tools if bound using adapter manager
            tool_schemas = await self._prepare_tools_for_request()
            if tool_schemas:
                kwargs["tools"] = tool_schemas
                kwargs["tool_choice"] = "auto"
            
            # Stream tokens one by one
            content_chunks = []
            try:
                stream = await self.client.chat.completions.create(**kwargs)
                async for chunk in stream:
                    content = chunk.choices[0].delta.content
                    if content:
                        content_chunks.append(content)
                        yield content
                
                # Track usage after streaming is complete
                full_content = "".join(content_chunks)
                self._track_streaming_usage(messages, full_content)
                
            except Exception as e:
                logger.error(f"Error in streaming: {e}")
                raise
            
        except Exception as e:
            logger.error(f"Error in astream: {e}")
            raise
    
    async def ainvoke(self, input_data: Union[str, List[Dict[str, str]], Any]) -> Union[str, Any]:
        """Unified invoke method for all input types"""
        try:
            # Use adapter manager to prepare messages
            messages = self._prepare_messages(input_data)
            
            # Prepare request kwargs
            kwargs = {
                "model": self.model_name,
                "messages": messages,
                "temperature": self.config.get("temperature", 0.7),
                "max_tokens": self.config.get("max_tokens", 1024)
            }
            
            # Add tools if bound using adapter manager
            tool_schemas = await self._prepare_tools_for_request()
            if tool_schemas:
                kwargs["tools"] = tool_schemas
                kwargs["tool_choice"] = "auto"
            
            # Handle streaming vs non-streaming
            if self.streaming:
                # TRUE STREAMING MODE - collect all chunks from the stream
                content_chunks = []
                async for token in self.astream(input_data):
                    content_chunks.append(token)
                content = "".join(content_chunks)
                
                return self._format_response(content, input_data)
            else:
                # Non-streaming mode
                response = await self.client.chat.completions.create(**kwargs)
                message = response.choices[0].message
                
                # Update usage tracking
                if response.usage:
                    self._update_token_usage(response.usage)
                    self._track_billing(response.usage)
                
                # Handle tool calls if present - let adapter process the complete message
                if message.tool_calls:
                    # Pass the complete message object to adapter for proper tool_calls handling
                    return self._format_response(message, input_data)
                
                # Return appropriate format based on input type
                return self._format_response(message.content or "", input_data)
            
        except Exception as e:
            logger.error(f"Error in ainvoke: {e}")
            raise
    
    def _track_streaming_usage(self, messages: List[Dict[str, str]], content: str):
        """Track usage for streaming requests (estimated)"""
        # Create a mock usage object for tracking
        class MockUsage:
            def __init__(self):
                self.prompt_tokens = len(str(messages)) // 4  # Rough estimate
                self.completion_tokens = len(content) // 4   # Rough estimate  
                self.total_tokens = self.prompt_tokens + self.completion_tokens
        
        usage = MockUsage()
        self._update_token_usage(usage)
        self._track_billing(usage)
    
    async def _stream_response(self, kwargs: Dict[str, Any]) -> AsyncGenerator[str, None]:
        """Handle streaming responses - DEPRECATED: Use astream() instead"""
        kwargs["stream"] = True
        
        async def stream_generator():
            try:
                stream = await self.client.chat.completions.create(**kwargs)
                async for chunk in stream:
                    content = chunk.choices[0].delta.content
                    if content:
                        yield content
            except Exception as e:
                logger.error(f"Error in streaming: {e}")
                raise
        
        return stream_generator()
    
    
    def _update_token_usage(self, usage):
        """Update token usage statistics"""
        self.last_token_usage = {
            "prompt_tokens": usage.prompt_tokens,
            "completion_tokens": usage.completion_tokens,
            "total_tokens": usage.total_tokens
        }
        
        # Update total usage
        self.total_token_usage["prompt_tokens"] += self.last_token_usage["prompt_tokens"]
        self.total_token_usage["completion_tokens"] += self.last_token_usage["completion_tokens"]
        self.total_token_usage["total_tokens"] += self.last_token_usage["total_tokens"]
        self.total_token_usage["requests_count"] += 1
    
    def _track_billing(self, usage):
        """Track billing information"""
        self._track_usage(
            service_type=ServiceType.LLM,
            operation="chat",
            input_tokens=usage.prompt_tokens,
            output_tokens=usage.completion_tokens,
            metadata={
                "temperature": self.config.get("temperature", 0.7), 
                "max_tokens": self.config.get("max_tokens", 1024)
            }
        )
    
    def get_token_usage(self) -> Dict[str, Any]:
        """Get total token usage statistics"""
        return self.total_token_usage
    
    def get_last_token_usage(self) -> Dict[str, int]:
        """Get token usage from last request"""
        return self.last_token_usage
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model"""
        return {
            "name": self.model_name,
            "max_tokens": self.config.get("max_tokens", 1024),
            "supports_streaming": True,
            "supports_functions": True,
            "provider": "yyds",
            "pricing": {
                "input_tokens_per_1k": 0.0045,
                "output_tokens_per_1k": 0.0225,
                "currency": "USD"
            }
        }
    
        
    async def close(self):
        """Close the backend client"""
        await self.client.close()