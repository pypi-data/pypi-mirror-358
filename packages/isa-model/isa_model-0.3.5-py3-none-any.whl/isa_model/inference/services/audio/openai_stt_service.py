import logging
import aiohttp
from typing import Dict, Any, List, Union, Optional, BinaryIO
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from isa_model.inference.services.audio.base_stt_service import BaseSTTService
from isa_model.inference.providers.base_provider import BaseProvider
from isa_model.inference.billing_tracker import ServiceType

logger = logging.getLogger(__name__)

class OpenAISTTService(BaseSTTService):
    """
    OpenAI Speech-to-Text service using whisper-1 model.
    Supports transcription and translation to English.
    """
    
    def __init__(self, provider: 'BaseProvider', model_name: str = "whisper-1"):
        super().__init__(provider, model_name)
        
        # Get full configuration from provider (including sensitive data)
        provider_config = provider.get_full_config()
        
        # Initialize AsyncOpenAI client with provider configuration
        try:
            if not provider_config.get("api_key"):
                raise ValueError("OpenAI API key not found in provider configuration")
            
            self.client = AsyncOpenAI(
                api_key=provider_config["api_key"],
                base_url=provider_config.get("base_url", "https://api.openai.com/v1"),
                organization=provider_config.get("organization")
            )
            
            logger.info(f"Initialized OpenAISTTService with model '{self.model_name}'")
            
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            raise ValueError(f"Failed to initialize OpenAI client. Check your API key configuration: {e}") from e
        
        # Model configurations
        self.max_file_size = provider_config.get('max_file_size', 25 * 1024 * 1024)  # 25MB
        self.supported_formats = ['mp3', 'mp4', 'mpeg', 'mpga', 'm4a', 'wav', 'webm']
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    async def _download_audio(self, audio_url: str) -> bytes:
        """Download audio from URL"""
        async with aiohttp.ClientSession() as session:
            async with session.get(audio_url) as response:
                if response.status == 200:
                    return await response.read()
                else:
                    raise ValueError(f"Failed to download audio from {audio_url}: {response.status}")

    async def transcribe(
        self, 
        audio_file: Union[str, BinaryIO], 
        language: Optional[str] = None,
        prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """Transcribe audio file to text using whisper-1"""
        try:
            # Prepare the audio file
            if isinstance(audio_file, str):
                if audio_file.startswith(('http://', 'https://')):
                    # Download audio from URL
                    audio_data = await self._download_audio(audio_file)
                    filename = audio_file.split('/')[-1] or 'audio.wav'
                else:
                    # Local file path
                    with open(audio_file, 'rb') as f:
                        audio_data = f.read()
                        filename = audio_file
            else:
                audio_data = audio_file.read()
                filename = getattr(audio_file, 'name', 'audio.wav')
            
            # Check file size
            if len(audio_data) > self.max_file_size:
                raise ValueError(f"Audio file size ({len(audio_data)} bytes) exceeds maximum ({self.max_file_size} bytes)")
            
            # Prepare transcription parameters
            kwargs = {
                "model": self.model_name,
                "file": (filename, audio_data),
                "response_format": "verbose_json"
            }
            
            if language:
                kwargs["language"] = language
            if prompt:
                kwargs["prompt"] = prompt
            
            # Transcribe audio
            response = await self.client.audio.transcriptions.create(**kwargs)
            
            # Track usage for billing
            usage = getattr(response, 'usage', {})
            input_tokens = usage.get('input_tokens', 0) if usage else 0
            output_tokens = usage.get('output_tokens', 0) if usage else 0
            
            # For audio, also track duration in minutes
            duration_minutes = getattr(response, 'duration', 0) / 60.0 if getattr(response, 'duration', 0) else 0
            
            self._track_usage(
                service_type=ServiceType.AUDIO_STT,
                operation="transcribe",
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                input_units=duration_minutes,  # Duration in minutes
                metadata={
                    "language": language,
                    "model": self.model_name,
                    "file_size": len(audio_data)
                }
            )
            
            # Format response
            result = {
                "text": response.text,
                "language": getattr(response, 'language', language or 'unknown'),
                "duration": getattr(response, 'duration', None),
                "segments": getattr(response, 'segments', []),
                "confidence": None,  # whisper-1 doesn't provide confidence scores
                "usage": usage  # Include usage information
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            raise
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    async def translate(
        self, 
        audio_file: Union[str, BinaryIO]
    ) -> Dict[str, Any]:
        """Translate audio file to English text"""
        try:
            # Prepare the audio file
            if isinstance(audio_file, str):
                with open(audio_file, 'rb') as f:
                    audio_data = f.read()
                    filename = audio_file
            else:
                audio_data = audio_file.read()
                filename = getattr(audio_file, 'name', 'audio.wav')
            
            # Check file size
            if len(audio_data) > self.max_file_size:
                raise ValueError(f"Audio file size ({len(audio_data)} bytes) exceeds maximum ({self.max_file_size} bytes)")
            
            # Translate audio to English
            response = await self.client.audio.translations.create(
                model=self.model_name,
                file=(filename, audio_data),
                response_format="verbose_json"
            )
            
            # Format response
            result = {
                "text": response.text,
                "detected_language": getattr(response, 'language', 'unknown'),
                "duration": getattr(response, 'duration', None),
                "segments": getattr(response, 'segments', []),
                "confidence": None  # Whisper doesn't provide confidence scores
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error translating audio: {e}")
            raise
    
    async def transcribe_batch(
        self, 
        audio_files: List[Union[str, BinaryIO]], 
        language: Optional[str] = None,
        prompt: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Transcribe multiple audio files"""
        results = []
        
        for audio_file in audio_files:
            try:
                result = await self.transcribe(audio_file, language, prompt)
                results.append(result)
            except Exception as e:
                logger.error(f"Error transcribing audio file: {e}")
                results.append({
                    "text": "",
                    "language": "unknown",
                    "duration": None,
                    "segments": [],
                    "confidence": None,
                    "error": str(e)
                })
        
        return results
    
    async def detect_language(self, audio_file: Union[str, BinaryIO]) -> Dict[str, Any]:
        """Detect language of audio file"""
        try:
            # Transcribe with language detection
            result = await self.transcribe(audio_file, language=None)
            
            return {
                "language": result["language"],
                "confidence": 1.0,  # Whisper is generally confident
                "alternatives": []  # Whisper doesn't provide alternatives
            }
            
        except Exception as e:
            logger.error(f"Error detecting language: {e}")
            raise
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported audio formats"""
        return self.supported_formats.copy()
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported language codes"""
        # Whisper supports 99+ languages
        return [
            'af', 'am', 'ar', 'as', 'az', 'ba', 'be', 'bg', 'bn', 'bo', 'br', 'bs', 'ca', 
            'cs', 'cy', 'da', 'de', 'el', 'en', 'es', 'et', 'eu', 'fa', 'fi', 'fo', 'fr', 
            'gl', 'gu', 'ha', 'haw', 'he', 'hi', 'hr', 'ht', 'hu', 'hy', 'id', 'is', 'it', 
            'ja', 'jw', 'ka', 'kk', 'km', 'kn', 'ko', 'la', 'lb', 'ln', 'lo', 'lt', 'lv', 
            'mg', 'mi', 'mk', 'ml', 'mn', 'mr', 'ms', 'mt', 'my', 'ne', 'nl', 'nn', 'no', 
            'oc', 'pa', 'pl', 'ps', 'pt', 'ro', 'ru', 'sa', 'sd', 'si', 'sk', 'sl', 'sn', 
            'so', 'sq', 'sr', 'su', 'sv', 'sw', 'ta', 'te', 'tg', 'th', 'tk', 'tl', 'tr', 
            'tt', 'uk', 'ur', 'uz', 'vi', 'yi', 'yo', 'zh'
        ]
    
    def get_max_file_size(self) -> int:
        """Get maximum file size in bytes"""
        return self.max_file_size
    
    async def close(self):
        """Cleanup resources"""
        await self.client.close()
        logger.info("OpenAISTTService client has been closed.") 