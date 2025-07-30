from abc import ABC, abstractmethod
from typing import Dict, Any, List, Union, Optional, BinaryIO
from isa_model.inference.services.base_service import BaseService

class BaseImageGenService(BaseService):
    """Base class for image generation services"""
    
    @abstractmethod
    async def generate_image(
        self, 
        prompt: str,
        negative_prompt: Optional[str] = None,
        width: int = 512,
        height: int = 512,
        num_inference_steps: int = 20,
        guidance_scale: float = 7.5,
        seed: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate a single image from text prompt
        
        Args:
            prompt: Text description of the desired image
            negative_prompt: Text describing what to avoid in the image
            width: Image width in pixels
            height: Image height in pixels
            num_inference_steps: Number of denoising steps
            guidance_scale: How closely to follow the prompt
            seed: Random seed for reproducible results
            
        Returns:
            Dict containing generation results with keys:
            - image_data: Binary image data or PIL Image
            - format: Image format (e.g., 'png', 'jpg')
            - width: Actual image width
            - height: Actual image height
            - seed: Seed used for generation
        """
        pass
    
    @abstractmethod
    async def generate_images(
        self, 
        prompt: str,
        num_images: int = 1,
        negative_prompt: Optional[str] = None,
        width: int = 512,
        height: int = 512,
        num_inference_steps: int = 20,
        guidance_scale: float = 7.5,
        seed: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate multiple images from text prompt
        
        Args:
            prompt: Text description of the desired image
            num_images: Number of images to generate
            negative_prompt: Text describing what to avoid in the image
            width: Image width in pixels
            height: Image height in pixels
            num_inference_steps: Number of denoising steps
            guidance_scale: How closely to follow the prompt
            seed: Random seed for reproducible results
            
        Returns:
            List of generation result dictionaries
        """
        pass
    
    @abstractmethod
    async def image_to_image(
        self,
        prompt: str,
        init_image: Union[str, BinaryIO],
        strength: float = 0.8,
        negative_prompt: Optional[str] = None,
        num_inference_steps: int = 20,
        guidance_scale: float = 7.5,
        seed: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate image based on existing image and prompt
        
        Args:
            prompt: Text description of desired modifications
            init_image: Path to initial image or image data
            strength: How much to transform the initial image (0.0-1.0)
            negative_prompt: Text describing what to avoid
            num_inference_steps: Number of denoising steps
            guidance_scale: How closely to follow the prompt
            seed: Random seed for reproducible results
            
        Returns:
            Dict containing generation results
        """
        pass
    
    @abstractmethod
    def get_supported_sizes(self) -> List[Dict[str, int]]:
        """
        Get list of supported image dimensions
        
        Returns:
            List of dictionaries with 'width' and 'height' keys
        """
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the image generation model
        
        Returns:
            Dict containing model information:
            - name: Model name
            - max_width: Maximum supported width
            - max_height: Maximum supported height
            - supports_negative_prompt: Whether negative prompts are supported
            - supports_img2img: Whether image-to-image is supported
        """
        pass
    
    @abstractmethod
    async def close(self):
        """Cleanup resources"""
        pass
