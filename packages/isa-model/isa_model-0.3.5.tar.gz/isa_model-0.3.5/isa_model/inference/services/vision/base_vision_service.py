from abc import ABC, abstractmethod
from typing import Dict, Any, List, Union, Optional, BinaryIO
from isa_model.inference.services.base_service import BaseService

class BaseVisionService(BaseService):
    """Base class for vision understanding services"""
    
    @abstractmethod
    async def invoke(
        self, 
        image: Union[str, BinaryIO],
        prompt: Optional[str] = None,
        task: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Unified invoke method for all vision operations
        
        Args:
            image: Path to image file or image data
            prompt: Optional text prompt/question about the image
            task: Task type (analyze, describe, extract_text, detect_objects, etc.)
            **kwargs: Additional task-specific parameters
            
        Returns:
            Dict containing task results
        """
        pass
    
    @abstractmethod
    async def analyze_image(
        self, 
        image: Union[str, BinaryIO],
        prompt: Optional[str] = None,
        max_tokens: int = 1000
    ) -> Dict[str, Any]:
        """
        Analyze image and provide description or answer questions
        
        Args:
            image: Path to image file or image data
            prompt: Optional text prompt/question about the image
            max_tokens: Maximum tokens in response
            
        Returns:
            Dict containing analysis results with keys:
            - text: Description or answer about the image
            - confidence: Confidence score (if available)
            - detected_objects: List of detected objects (if available)
            - metadata: Additional metadata about the analysis
        """
        pass
    
    @abstractmethod
    async def analyze_images(
        self, 
        images: List[Union[str, BinaryIO]],
        prompt: Optional[str] = None,
        max_tokens: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        Analyze multiple images
        
        Args:
            images: List of image paths or image data
            prompt: Optional text prompt/question about the images
            max_tokens: Maximum tokens in response
            
        Returns:
            List of analysis result dictionaries
        """
        pass
    
    @abstractmethod
    async def describe_image(
        self, 
        image: Union[str, BinaryIO],
        detail_level: str = "medium"
    ) -> Dict[str, Any]:
        """
        Generate detailed description of image
        
        Args:
            image: Path to image file or image data
            detail_level: Level of detail ("low", "medium", "high")
            
        Returns:
            Dict containing description results with keys:
            - description: Detailed text description
            - objects: List of detected objects
            - scene: Scene description
            - colors: Dominant colors
        """
        pass
    
    @abstractmethod
    async def extract_text(self, image: Union[str, BinaryIO]) -> Dict[str, Any]:
        """
        Extract text from image (OCR)
        
        Args:
            image: Path to image file or image data
            
        Returns:
            Dict containing OCR results with keys:
            - text: Extracted text
            - confidence: Overall confidence score
            - bounding_boxes: Text regions with coordinates (if available)
            - language: Detected language (if available)
        """
        pass
    
    @abstractmethod
    async def detect_objects(
        self, 
        image: Union[str, BinaryIO],
        confidence_threshold: float = 0.5
    ) -> Dict[str, Any]:
        """
        Detect objects in image
        
        Args:
            image: Path to image file or image data
            confidence_threshold: Minimum confidence for detections
            
        Returns:
            Dict containing detection results with keys:
            - objects: List of detected objects with labels, confidence, and coordinates
            - count: Number of objects detected
            - bounding_boxes: Object locations with coordinates
        """
        pass
    
    @abstractmethod
    async def get_object_coordinates(
        self,
        image: Union[str, BinaryIO],
        object_name: str
    ) -> Dict[str, Any]:
        """
        Get coordinates of a specific object in the image
        
        Args:
            image: Path to image file or image data
            object_name: Name of the object to locate
            
        Returns:
            Dict containing coordinate results with keys:
            - found: Boolean indicating if object was found
            - center_coordinates: List [x, y] with pixel coordinates of center point
            - confidence: Confidence score for the detection
            - description: Description of the object location
        """
        pass
    
    @abstractmethod
    async def classify_image(
        self, 
        image: Union[str, BinaryIO],
        categories: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Classify image into categories
        
        Args:
            image: Path to image file or image data
            categories: Optional list of specific categories to consider
            
        Returns:
            Dict containing classification results with keys:
            - category: Top predicted category
            - confidence: Confidence score
            - all_predictions: List of all predictions with scores
        """
        pass
    
    @abstractmethod
    async def compare_images(
        self, 
        image1: Union[str, BinaryIO],
        image2: Union[str, BinaryIO]
    ) -> Dict[str, Any]:
        """
        Compare two images for similarity
        
        Args:
            image1: First image path or data
            image2: Second image path or data
            
        Returns:
            Dict containing comparison results with keys:
            - similarity_score: Numerical similarity score
            - differences: Description of key differences
            - common_elements: Description of common elements
        """
        pass
    
    @abstractmethod
    def get_supported_formats(self) -> List[str]:
        """
        Get list of supported image formats
        
        Returns:
            List of supported file extensions (e.g., ['jpg', 'png', 'gif'])
        """
        pass
    
    @abstractmethod
    def get_max_image_size(self) -> Dict[str, int]:
        """
        Get maximum supported image dimensions
        
        Returns:
            Dict with 'width' and 'height' keys for maximum dimensions
        """
        pass
    
    @abstractmethod
    async def close(self):
        """Cleanup resources"""
        pass
