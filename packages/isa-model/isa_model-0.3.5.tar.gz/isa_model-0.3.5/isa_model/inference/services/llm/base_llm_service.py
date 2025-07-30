from abc import ABC, abstractmethod
from typing import Dict, Any, List, Union, Optional, AsyncGenerator, Callable
from isa_model.inference.services.base_service import BaseService
from isa_model.inference.services.llm.llm_adapter import AdapterManager

class BaseLLMService(BaseService):
    """Base class for Large Language Model services with unified invoke interface"""
    
    def __init__(self, provider, model_name: str):
        super().__init__(provider, model_name)
        self._bound_tools: List[Any] = []  # 改为存储原始工具对象
        self._tool_mappings: Dict[str, tuple] = {}  # 工具名到(工具, 适配器)的映射
        
        # 初始化适配器管理器
        self.adapter_manager = AdapterManager()
        
        # Get streaming config from provider config
        self.streaming = self.config.get("streaming", False)
    
    def bind_tools(self, tools: List[Any], **kwargs) -> 'BaseLLMService':
        """
        Bind tools to this LLM service for function calling
        
        Args:
            tools: List of tools to bind (functions, LangChain tools, etc.)
            **kwargs: Additional tool binding parameters
            
        Returns:
            Self for method chaining
        """
        self._bound_tools = tools
        return self
    
    async def _prepare_tools_for_request(self) -> List[Dict[str, Any]]:
        """准备工具用于请求"""
        if not self._bound_tools:
            return []
        
        schemas, self._tool_mappings = await self.adapter_manager.convert_tools_to_schemas(self._bound_tools)
        return schemas
    
    def _prepare_messages(self, input_data: Union[str, List[Dict[str, str]], Any]) -> List[Dict[str, str]]:
        """使用适配器管理器转换消息格式"""
        return self.adapter_manager.convert_messages(input_data)
    
    def _format_response(self, response: str, original_input: Any) -> Union[str, Any]:
        """使用适配器管理器格式化响应"""
        return self.adapter_manager.format_response(response, original_input)
    
    async def _execute_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """使用适配器管理器执行工具调用"""
        return await self.adapter_manager.execute_tool(tool_name, arguments, self._tool_mappings)
    
    @abstractmethod
    async def astream(self, input_data: Union[str, List[Dict[str, str]], Any]) -> AsyncGenerator[str, None]:
        """
        True streaming method that yields tokens one by one as they arrive
        
        Args:
            input_data: Can be:
                - str: Simple text prompt
                - list: Message history like [{"role": "user", "content": "hello"}]
                - Any: LangChain message objects or other formats
            
        Yields:
            Individual tokens as they arrive from the model
        """
        pass
    
    @abstractmethod
    async def ainvoke(self, input_data: Union[str, List[Dict[str, str]], Any]) -> Union[str, Any]:
        """
        Universal async invocation method that handles different input types
        
        Args:
            input_data: Can be:
                - str: Simple text prompt
                - list: Message history like [{"role": "user", "content": "hello"}]
                - Any: LangChain message objects or other formats
            
        Returns:
            Model response (string for simple cases, object for complex cases)
        """
        pass
    
    def stream(self, input_data: Union[str, List[Dict[str, str]], Any]):
        """
        Synchronous wrapper for astream - returns the async generator
        
        Args:
            input_data: Same as astream
            
        Returns:
            AsyncGenerator that yields tokens
            
        Usage:
            async for token in llm.stream("Hello"):
                print(token, end="", flush=True)
        """
        return self.astream(input_data)
    
    def invoke(self, input_data: Union[str, List[Dict[str, str]], Any]) -> Union[str, Any]:
        """
        Synchronous wrapper for ainvoke
        
        Args:
            input_data: Same as ainvoke
            
        Returns:
            Model response
        """
        import asyncio
        try:
            # Try to get current event loop
            loop = asyncio.get_running_loop()
            # If we're in an event loop, create a new thread
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, self.ainvoke(input_data))
                return future.result()
        except RuntimeError:
            # No event loop running, create a new one
            return asyncio.run(self.ainvoke(input_data))
    
    def _has_bound_tools(self) -> bool:
        """Check if this service has bound tools"""
        return bool(self._bound_tools)
    
    def _get_bound_tools(self) -> List[Any]:
        """Get the bound tools"""
        return self._bound_tools
    
    @abstractmethod
    def get_token_usage(self) -> Dict[str, Any]:
        """Get cumulative token usage statistics"""
        pass
    
    @abstractmethod
    def get_last_token_usage(self) -> Dict[str, int]:
        """Get token usage from the last request"""
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model"""
        pass
    
    @abstractmethod
    async def close(self):
        """Cleanup resources and close connections"""
        pass
    
    def get_last_usage_with_cost(self) -> Dict[str, Any]:
        """Get last request usage with cost information"""
        usage = self.get_last_token_usage()
        
        # Calculate cost using provider
        if hasattr(self.provider, 'calculate_cost'):
            cost = getattr(self.provider, 'calculate_cost')(
                self.model_name,
                usage["prompt_tokens"],
                usage["completion_tokens"]
            )
        else:
            cost = 0.0
        
        return {
            **usage,
            "cost_usd": cost,
            "model": self.model_name,
            "provider": getattr(self.provider, 'name', 'unknown')
        }
