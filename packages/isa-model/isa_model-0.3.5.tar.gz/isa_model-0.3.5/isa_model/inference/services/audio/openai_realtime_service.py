import logging
import json
import asyncio
from typing import Dict, Any, List, Optional, Callable, AsyncGenerator
import aiohttp
from tenacity import retry, stop_after_attempt, wait_exponential

from isa_model.inference.services.base_service import BaseService
from isa_model.inference.providers.base_provider import BaseProvider
from isa_model.inference.billing_tracker import ServiceType

logger = logging.getLogger(__name__)

class OpenAIRealtimeService(BaseService):
    """
    OpenAI Realtime API service for real-time audio conversations.
    Uses gpt-4o-mini-realtime-preview model for interactive audio chat.
    """
    
    def __init__(self, provider: 'BaseProvider', model_name: str = "gpt-4o-mini-realtime-preview"):
        super().__init__(provider, model_name)
        
        self.api_key = self.config.get('api_key')
        self.base_url = self.config.get('api_base', 'https://api.openai.com/v1')
        
        # Default session configuration
        self.default_config = {
            "model": self.model_name,
            "modalities": ["audio", "text"],
            "voice": "alloy",
            "input_audio_format": "pcm16",
            "output_audio_format": "pcm16",
            "input_audio_transcription": {
                "model": "whisper-1"
            },
            "turn_detection": None,
            "tools": [],
            "tool_choice": "none",
            "temperature": 0.7,
            "max_response_output_tokens": 200,
            "speed": 1.1,
            "tracing": "auto"
        }
        
        logger.info(f"Initialized OpenAIRealtimeService with model '{self.model_name}'")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    async def create_session(
        self, 
        instructions: str = "You are a friendly assistant.",
        modalities: Optional[List[str]] = None,
        voice: str = "alloy",
        **kwargs
    ) -> Dict[str, Any]:
        """Create a new realtime session"""
        try:
            # Prepare session configuration
            session_config = self.default_config.copy()
            session_config.update({
                "instructions": instructions,
                "modalities": modalities if modalities is not None else ["audio", "text"],
                "voice": voice,
                **kwargs
            })
            
            # Create session via REST API
            url = f"{self.base_url}/realtime/sessions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=session_config) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        # Track usage for billing
                        self._track_usage(
                            service_type=ServiceType.AUDIO_STT,  # Realtime combines STT/TTS
                            operation="create_session",
                            metadata={
                                "session_id": result.get("id"),
                                "model": self.model_name,
                                "modalities": session_config["modalities"]
                            }
                        )
                        
                        return result
                    else:
                        error_text = await response.text()
                        raise Exception(f"Failed to create session: {response.status} - {error_text}")
                        
        except Exception as e:
            logger.error(f"Error creating realtime session: {e}")
            raise
    
    async def connect_websocket(self, session_id: str) -> aiohttp.ClientWebSocketResponse:
        """Connect to the realtime WebSocket for a session"""
        try:
            ws_url = f"wss://api.openai.com/v1/realtime/sessions/{session_id}/ws"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "OpenAI-Beta": "realtime=v1"
            }
            
            session = aiohttp.ClientSession()
            ws = await session.ws_connect(ws_url, headers=headers)
            
            logger.info(f"Connected to realtime WebSocket for session {session_id}")
            return ws
            
        except Exception as e:
            logger.error(f"Error connecting to WebSocket: {e}")
            raise
    
    async def send_audio_message(
        self, 
        ws: aiohttp.ClientWebSocketResponse, 
        audio_data: bytes,
        format: str = "pcm16"
    ):
        """Send audio data to the realtime session"""
        try:
            message = {
                "type": "input_audio_buffer.append",
                "audio": audio_data.hex() if format == "pcm16" else audio_data
            }
            
            await ws.send_str(json.dumps(message))
            
            # Commit the audio buffer
            commit_message = {"type": "input_audio_buffer.commit"}
            await ws.send_str(json.dumps(commit_message))
            
        except Exception as e:
            logger.error(f"Error sending audio message: {e}")
            raise
    
    async def send_text_message(
        self, 
        ws: aiohttp.ClientWebSocketResponse, 
        text: str
    ):
        """Send text message to the realtime session"""
        try:
            message = {
                "type": "conversation.item.create",
                "item": {
                    "type": "message",
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": text
                        }
                    ]
                }
            }
            
            await ws.send_str(json.dumps(message))
            
            # Trigger response
            response_message = {"type": "response.create"}
            await ws.send_str(json.dumps(response_message))
            
        except Exception as e:
            logger.error(f"Error sending text message: {e}")
            raise
    
    async def listen_for_responses(
        self, 
        ws: aiohttp.ClientWebSocketResponse,
        message_handler: Optional[Callable] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Listen for responses from the realtime session"""
        try:
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    try:
                        data = json.loads(msg.data)
                        
                        # Handle different message types
                        if data.get("type") == "response.audio.delta":
                            # Audio response chunk
                            yield {
                                "type": "audio",
                                "data": data.get("delta", ""),
                                "format": "pcm16"
                            }
                        elif data.get("type") == "response.text.delta":
                            # Text response chunk
                            yield {
                                "type": "text",
                                "data": data.get("delta", "")
                            }
                        elif data.get("type") == "response.done":
                            # Response completed
                            usage = data.get("response", {}).get("usage", {})
                            
                            # Track usage for billing
                            self._track_usage(
                                service_type=ServiceType.AUDIO_STT,
                                operation="realtime_response",
                                input_tokens=usage.get("input_tokens", 0),
                                output_tokens=usage.get("output_tokens", 0),
                                metadata={
                                    "response_id": data.get("response", {}).get("id"),
                                    "model": self.model_name
                                }
                            )
                            
                            yield {
                                "type": "done",
                                "usage": usage
                            }
                        
                        # Call custom message handler if provided
                        if message_handler:
                            await message_handler(data)
                            
                    except json.JSONDecodeError as e:
                        logger.error(f"Error parsing WebSocket message: {e}")
                        continue
                        
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    logger.error(f"WebSocket error: {ws.exception()}")
                    break
                    
        except Exception as e:
            logger.error(f"Error listening for responses: {e}")
            raise
    
    async def simple_audio_chat(
        self, 
        audio_data: bytes, 
        instructions: str = "You are a helpful assistant. Respond in audio.",
        voice: str = "alloy"
    ) -> Dict[str, Any]:
        """Simple audio chat - send audio, get audio response"""
        try:
            # Create session
            session = await self.create_session(
                instructions=instructions,
                modalities=["audio"],
                voice=voice
            )
            session_id = session["id"]
            
            # Connect to WebSocket
            ws = await self.connect_websocket(session_id)
            
            try:
                # Send audio
                await self.send_audio_message(ws, audio_data)
                
                # Collect response
                audio_chunks = []
                usage_info = {}
                
                async for response in self.listen_for_responses(ws):
                    if response["type"] == "audio":
                        audio_chunks.append(response["data"])
                    elif response["type"] == "done":
                        usage_info = response["usage"]
                        break
                
                # Combine audio chunks
                full_audio = "".join(audio_chunks)
                
                return {
                    "audio_response": full_audio,
                    "session_id": session_id,
                    "usage": usage_info
                }
                
            finally:
                await ws.close()
                
        except Exception as e:
            logger.error(f"Error in simple audio chat: {e}")
            raise
    
    async def simple_text_chat(
        self, 
        text: str, 
        instructions: str = "You are a helpful assistant.",
        voice: str = "alloy"
    ) -> Dict[str, Any]:
        """Simple text chat - send text, get audio response"""
        try:
            # Create session
            session = await self.create_session(
                instructions=instructions,
                modalities=["text", "audio"],
                voice=voice
            )
            session_id = session["id"]
            
            # Connect to WebSocket
            ws = await self.connect_websocket(session_id)
            
            try:
                # Send text
                await self.send_text_message(ws, text)
                
                # Collect response
                text_response = ""
                audio_chunks = []
                usage_info = {}
                
                async for response in self.listen_for_responses(ws):
                    if response["type"] == "text":
                        text_response += response["data"]
                    elif response["type"] == "audio":
                        audio_chunks.append(response["data"])
                    elif response["type"] == "done":
                        usage_info = response["usage"]
                        break
                
                # Combine audio chunks
                full_audio = "".join(audio_chunks)
                
                return {
                    "text_response": text_response,
                    "audio_response": full_audio,
                    "session_id": session_id,
                    "usage": usage_info
                }
                
            finally:
                await ws.close()
                
        except Exception as e:
            logger.error(f"Error in simple text chat: {e}")
            raise
    
    def get_supported_voices(self) -> List[str]:
        """Get list of supported voice options"""
        return ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported audio formats"""
        return ["pcm16", "g711_ulaw", "g711_alaw"]
    
    async def close(self):
        """Cleanup resources"""
        # No persistent connections to close for REST API
        pass 