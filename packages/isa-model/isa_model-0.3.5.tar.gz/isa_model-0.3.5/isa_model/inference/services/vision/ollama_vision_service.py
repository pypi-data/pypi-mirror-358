import os
import json
import base64
import ollama
from typing import Dict, Any, Union, List, Optional, BinaryIO
from tenacity import retry, stop_after_attempt, wait_exponential
from isa_model.inference.services.vision.base_vision_service import BaseVisionService
from isa_model.inference.providers.base_provider import BaseProvider
import logging
import requests

logger = logging.getLogger(__name__)

class OllamaVisionService(BaseVisionService):
    """Vision model service wrapper for Ollama using base64 encoded images"""
    
    def __init__(self, provider: 'BaseProvider', model_name: str = 'gemma3:4b'):
        super().__init__(provider, model_name)
        self.max_tokens = self.config.get('max_tokens', 1000)
        self.temperature = self.config.get('temperature', 0.7)
    
    def _get_image_data(self, image: Union[str, BinaryIO]) -> bytes:
        """获取图像数据，支持本地文件和URL"""
        if isinstance(image, str):
            # Check if it's a URL
            if image.startswith(('http://', 'https://')):
                response = requests.get(image)
                response.raise_for_status()
                return response.content
            else:
                # Local file path
                with open(image, 'rb') as f:
                    return f.read()
        else:
            return image.read()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    async def analyze_image(
        self, 
        image: Union[str, BinaryIO],
        prompt: Optional[str] = None,
        max_tokens: int = 1000
    ) -> Dict[str, Any]:
        """
        Analyze image and provide description or answer questions
        """
        try:
            # 获取图像数据
            image_data = self._get_image_data(image)
            
            # 转换为base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # 使用默认提示词如果没有提供
            query = prompt or "请描述这张图片的内容。"
            
            # 使用 ollama 库直接调用
            response = ollama.chat(
                model=self.model_name,
                messages=[{
                    'role': 'user',
                    'content': query,
                    'images': [image_base64]
                }]
            )
            
            content = response['message']['content']
            
            return {
                "text": content,
                "confidence": 1.0,  # Ollama doesn't provide confidence scores
                "detected_objects": [],  # Basic implementation
                "metadata": {
                    "model": self.model_name,
                    "prompt": query
                }
            }
            
        except Exception as e:
            logger.error(f"Error in image analysis: {e}")
            raise

    async def analyze_images(
        self, 
        images: List[Union[str, BinaryIO]],
        prompt: Optional[str] = None,
        max_tokens: int = 1000
    ) -> List[Dict[str, Any]]:
        """Analyze multiple images"""
        results = []
        for image in images:
            result = await self.analyze_image(image, prompt, max_tokens)
            results.append(result)
        return results

    async def describe_image(
        self, 
        image: Union[str, BinaryIO],
        detail_level: str = "medium"
    ) -> Dict[str, Any]:
        """Generate detailed description of image"""
        prompts = {
            "low": "简单描述这张图片。",
            "medium": "详细描述这张图片的内容、颜色、物体和场景。",
            "high": "非常详细地描述这张图片，包括所有可见的物体、颜色、纹理、场景、情感和任何其他细节。"
        }
        
        prompt = prompts.get(detail_level, prompts["medium"])
        result = await self.analyze_image(image, prompt)
        
        return {
            "description": result["text"],
            "objects": [],  # Basic implementation
            "scene": "未知",  # Basic implementation
            "colors": []  # Basic implementation
        }

    async def extract_text(self, image: Union[str, BinaryIO]) -> Dict[str, Any]:
        """Extract text from image (OCR)"""
        result = await self.analyze_image(image, "提取图片中的所有文字内容。")
        
        return {
            "text": result["text"],
            "confidence": 1.0,
            "bounding_boxes": [],  # Basic implementation
            "language": "未知"  # Basic implementation
        }

    async def detect_objects(
        self, 
        image: Union[str, BinaryIO],
        confidence_threshold: float = 0.5
    ) -> Dict[str, Any]:
        """Detect objects in image"""
        result = await self.analyze_image(image, "识别并列出图片中的所有物体。")
        
        return {
            "objects": [],  # Basic implementation - would need parsing
            "count": 0,
            "bounding_boxes": []
        }

    async def classify_image(
        self, 
        image: Union[str, BinaryIO],
        categories: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Classify image into categories"""
        if categories:
            category_str = "、".join(categories)
            prompt = f"将这张图片分类到以下类别之一：{category_str}"
        else:
            prompt = "这张图片属于什么类别？"
            
        result = await self.analyze_image(image, prompt)
        
        return {
            "category": result["text"],
            "confidence": 1.0,
            "all_predictions": [{"category": result["text"], "confidence": 1.0}]
        }

    async def compare_images(
        self, 
        image1: Union[str, BinaryIO],
        image2: Union[str, BinaryIO]
    ) -> Dict[str, Any]:
        """Compare two images for similarity"""
        # For now, analyze each image separately and compare descriptions
        result1 = await self.analyze_image(image1, "描述这张图片。")
        result2 = await self.analyze_image(image2, "描述这张图片。")
        
        return {
            "similarity_score": 0.5,  # Basic implementation
            "differences": "需要进一步分析",
            "common_elements": "需要进一步分析"
        }

    def get_supported_formats(self) -> List[str]:
        """Get list of supported image formats"""
        return ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']

    def get_max_image_size(self) -> Dict[str, int]:
        """Get maximum supported image dimensions"""
        return {"width": 4096, "height": 4096}

    async def close(self):
        """Cleanup resources"""
        pass

