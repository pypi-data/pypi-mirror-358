from abc import ABC, abstractmethod
from typing import Dict, Any, List, Union, Optional, BinaryIO
from isa_model.inference.services.base_service import BaseService

class BaseSTTService(BaseService):
    """Base class for Speech-to-Text services"""
    
    @abstractmethod
    async def transcribe(
        self, 
        audio_file: Union[str, BinaryIO], 
        language: Optional[str] = None,
        prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Transcribe audio file to text
        
        Args:
            audio_file: Path to audio file or file-like object
            language: Language code (e.g., 'en', 'es', 'fr')
            prompt: Optional prompt to guide transcription
            
        Returns:
            Dict containing transcription results with keys:
            - text: The transcribed text
            - language: Detected/specified language
            - confidence: Confidence score (if available)
            - segments: Time-segmented transcription (if available)
        """
        pass
    
    @abstractmethod
    async def translate(
        self, 
        audio_file: Union[str, BinaryIO]
    ) -> Dict[str, Any]:
        """
        Translate audio file to English text
        
        Args:
            audio_file: Path to audio file or file-like object
            
        Returns:
            Dict containing translation results with keys:
            - text: The translated text (in English)
            - detected_language: Original language detected
            - confidence: Confidence score (if available)
        """
        pass
    
    @abstractmethod
    async def transcribe_batch(
        self, 
        audio_files: List[Union[str, BinaryIO]], 
        language: Optional[str] = None,
        prompt: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Transcribe multiple audio files
        
        Args:
            audio_files: List of audio file paths or file-like objects
            language: Language code (e.g., 'en', 'es', 'fr')
            prompt: Optional prompt to guide transcription
            
        Returns:
            List of transcription results
        """
        pass
    
    @abstractmethod
    async def detect_language(self, audio_file: Union[str, BinaryIO]) -> Dict[str, Any]:
        """
        Detect language of audio file
        
        Args:
            audio_file: Path to audio file or file-like object
            
        Returns:
            Dict containing language detection results with keys:
            - language: Detected language code
            - confidence: Confidence score
            - alternatives: List of alternative languages with scores
        """
        pass
    
    @abstractmethod
    def get_supported_formats(self) -> List[str]:
        """
        Get list of supported audio formats
        
        Returns:
            List of supported file extensions (e.g., ['mp3', 'wav', 'flac'])
        """
        pass
    
    @abstractmethod
    def get_supported_languages(self) -> List[str]:
        """
        Get list of supported language codes
        
        Returns:
            List of supported language codes (e.g., ['en', 'es', 'fr'])
        """
        pass
    
    @abstractmethod
    async def close(self):
        """Cleanup resources"""
        pass
