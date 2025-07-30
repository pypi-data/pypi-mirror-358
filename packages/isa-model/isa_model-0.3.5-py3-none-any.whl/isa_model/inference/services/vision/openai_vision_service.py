from typing import Dict, Any, Union, List, Optional, BinaryIO
import base64
import aiohttp
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
from isa_model.inference.services.vision.base_vision_service import BaseVisionService
from isa_model.inference.providers.base_provider import BaseProvider
from isa_model.inference.billing_tracker import ServiceType
import logging

logger = logging.getLogger(__name__)

class OpenAIVisionService(BaseVisionService):
    """OpenAI Vision service using gpt-4.1-nano with vision capabilities"""
    
    def __init__(self, provider: 'BaseProvider', model_name: str = "gpt-4.1-nano"):
        super().__init__(provider, model_name)
        
        # Get full configuration from provider (including sensitive data)
        provider_config = provider.get_full_config()
        
        # Initialize AsyncOpenAI client with provider configuration
        try:
            if not provider_config.get("api_key"):
                raise ValueError("OpenAI API key not found in provider configuration")
            
            self._client = AsyncOpenAI(
                api_key=provider_config["api_key"],
                base_url=provider_config.get("base_url", "https://api.openai.com/v1"),
                organization=provider_config.get("organization")
            )
            
            logger.info(f"Initialized OpenAIVisionService with model {self.model_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            raise ValueError(f"Failed to initialize OpenAI client. Check your API key configuration: {e}") from e
        
        self.max_tokens = provider_config.get('max_tokens', 1000)
        self.temperature = provider_config.get('temperature', 0.7)
    
    @property
    def client(self) -> AsyncOpenAI:
        """Get the underlying OpenAI client"""
        return self._client
    
    async def _download_image(self, image_url: str) -> bytes:
        """Download image from URL"""
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as response:
                if response.status == 200:
                    return await response.read()
                else:
                    raise ValueError(f"Failed to download image from {image_url}: {response.status}")
    
    def _encode_image(self, image_path_or_data: Union[str, bytes, BinaryIO]) -> str:
        """Encode image to base64"""
        if isinstance(image_path_or_data, str):
            # If it's a file path
            with open(image_path_or_data, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode("utf-8")
        elif hasattr(image_path_or_data, 'read'):
            # If it's a file-like object (BinaryIO)
            data = image_path_or_data.read()  # type: ignore
            if isinstance(data, bytes):
                return base64.b64encode(data).decode("utf-8")
            else:
                raise ValueError("File-like object did not return bytes")
        else:
            # If it's bytes data
            return base64.b64encode(image_path_or_data).decode("utf-8")  # type: ignore
    
    async def invoke(
        self, 
        image: Union[str, BinaryIO],
        prompt: Optional[str] = None,
        task: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Unified invoke method for all vision operations
        """
        task = task or "analyze"
        
        if task == "analyze":
            return await self.analyze_image(image, prompt, kwargs.get("max_tokens", 1000))
        elif task == "describe":
            return await self.describe_image(image, kwargs.get("detail_level", "medium"))
        elif task == "extract_text":
            return await self.extract_text(image)
        elif task == "detect_objects":
            return await self.detect_objects(image, kwargs.get("confidence_threshold", 0.5))
        elif task == "classify":
            return await self.classify_image(image, kwargs.get("categories"))
        else:
            # Default to analyze_image for unknown tasks
            return await self.analyze_image(image, prompt, kwargs.get("max_tokens", 1000))
    
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
        
        Args:
            image: Path to image file, URL, or image data
            prompt: Optional text prompt/question about the image
            max_tokens: Maximum tokens in response
            
        Returns:
            Dict containing analysis results
        """
        try:
            # Handle different input types
            if isinstance(image, str):
                if image.startswith(('http://', 'https://')):
                    # Download image from URL
                    image_bytes = await self._download_image(image)
                    base64_image = self._encode_image(image_bytes)
                else:
                    # File path
                    base64_image = self._encode_image(image)
            else:
                # BinaryIO or bytes data
                if hasattr(image, 'read'):
                    image_data = image.read()
                else:
                    image_data = image
                base64_image = self._encode_image(image_data)
            
            # Use default prompt if none provided
            if prompt is None:
                prompt = "Please describe what you see in this image in detail."
            
            # Use the standard chat completions API with vision
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                                "detail": "auto"
                            }
                        },
                    ],
                }
            ]
            
            response = await self._client.chat.completions.create(  # type: ignore
                model=self.model_name,
                messages=messages,  # type: ignore
                max_tokens=max_tokens,
                temperature=self.temperature
            )
            
            # Track usage for billing
            if response.usage:
                self._track_usage(
                    service_type=ServiceType.VISION,
                    operation="image_analysis",
                    input_tokens=response.usage.prompt_tokens,
                    output_tokens=response.usage.completion_tokens,
                    metadata={"prompt": prompt[:100], "model": self.model_name}
                )
            
            content = response.choices[0].message.content or ""
            
            return {
                "text": content,
                "confidence": 1.0,  # OpenAI doesn't provide confidence scores
                "detected_objects": [],  # Would need separate object detection
                "metadata": {
                    "model": self.model_name,
                    "prompt": prompt,
                    "tokens_used": response.usage.total_tokens if response.usage else 0
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
        detail_prompts = {
            "low": "Briefly describe what you see in this image.",
            "medium": "Describe what you see in this image in detail, including objects, colors, and scene.",
            "high": "Provide a comprehensive and detailed description of this image, including all visible objects, their positions, colors, textures, lighting, composition, and any text or symbols present."
        }
        
        prompt = detail_prompts.get(detail_level, detail_prompts["medium"])
        result = await self.analyze_image(image, prompt, 1500)
        
        return {
            "description": result["text"],
            "objects": [],  # Would need object detection API
            "scene": result["text"],  # Use same description
            "colors": [],  # Would need color analysis
            "detail_level": detail_level,
            "metadata": result["metadata"]
        }
    
    async def extract_text(self, image: Union[str, BinaryIO]) -> Dict[str, Any]:
        """Extract text from image (OCR)"""
        prompt = "Extract all text visible in this image. Provide only the text content, maintaining the original structure and formatting as much as possible."
        result = await self.analyze_image(image, prompt, 1000)
        
        return {
            "text": result["text"],
            "confidence": 1.0,
            "bounding_boxes": [],  # OpenAI vision doesn't provide bounding boxes
            "language": "unknown",  # Would need language detection
            "metadata": result["metadata"]
        }
    
    async def detect_objects(
        self, 
        image: Union[str, BinaryIO],
        confidence_threshold: float = 0.5
    ) -> Dict[str, Any]:
        """Detect objects in image"""
        prompt = """List all objects visible in this image. For each object, provide:
1. Object name
2. Approximate location as percentages from top-left corner (x%, y%)
3. Approximate size as percentages of image dimensions (width%, height%)
4. Brief description

Format each object as: "ObjectName: x=X%, y=Y%, width=W%, height=H% - Description"

Example: "Car: x=25%, y=40%, width=15%, height=12% - Red sedan in the center"
"""
        result = await self.analyze_image(image, prompt, 1500)
        
        # Parse the response to extract object information with coordinates
        objects = []
        bounding_boxes = []
        lines = result["text"].split('\n')
        
        for line in lines:
            line = line.strip()
            if line and ':' in line and ('x=' in line or 'width=' in line):
                try:
                    # Extract object name and details
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        object_name = parts[0].strip()
                        details = parts[1].strip()
                        
                        # Extract coordinates using regex-like parsing
                        coords = {}
                        for param in ['x', 'y', 'width', 'height']:
                            param_pattern = f"{param}="
                            if param_pattern in details:
                                start_idx = details.find(param_pattern) + len(param_pattern)
                                end_idx = details.find('%', start_idx)
                                if end_idx > start_idx:
                                    try:
                                        value = float(details[start_idx:end_idx])
                                        coords[param] = value
                                    except ValueError:
                                        continue
                        
                        # Extract description (after the coordinates)
                        desc_start = details.find(' - ')
                        description = details[desc_start + 3:] if desc_start != -1 else details
                        
                        objects.append({
                            "label": object_name,
                            "confidence": 1.0,
                            "coordinates": coords,
                            "description": description
                        })
                        
                        # Add bounding box if we have coordinates
                        if all(k in coords for k in ['x', 'y', 'width', 'height']):
                            bounding_boxes.append({
                                "label": object_name,
                                "x_percent": coords['x'],
                                "y_percent": coords['y'],
                                "width_percent": coords['width'],
                                "height_percent": coords['height']
                            })
                            
                except Exception:
                    # Fallback for objects that don't match expected format
                    objects.append({
                        "label": line,
                        "confidence": 1.0,
                        "coordinates": {},
                        "description": line
                    })
        
        return {
            "objects": objects,
            "count": len(objects),
            "bounding_boxes": bounding_boxes,
            "metadata": result["metadata"]
        }
    
    async def get_object_coordinates(
        self,
        image: Union[str, BinaryIO],
        object_name: str
    ) -> Dict[str, Any]:
        """Get coordinates of a specific object in the image"""
        prompt = f"""Locate the {object_name} in this image and return its center coordinates as [x, y] pixels.

Respond in this exact format:
FOUND: YES/NO
CENTER: [x, y]
DESCRIPTION: [Brief description]

If found, provide the pixel coordinates of the center point.
If not found, explain why.

Example:
FOUND: YES
CENTER: [640, 360]
DESCRIPTION: Blue login button in the center-left area
"""
        
        result = await self.analyze_image(image, prompt, 300)
        response_text = result["text"]
        
        # Parse the structured response
        found = False
        center_coords = None
        description = ""
        
        lines = response_text.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('FOUND:'):
                found = 'YES' in line.upper()
            elif line.startswith('CENTER:') and found:
                # Extract center coordinates [x, y]
                coords_text = line.replace('CENTER:', '').strip()
                try:
                    # Remove brackets and split
                    coords_text = coords_text.replace('[', '').replace(']', '')
                    if ',' in coords_text:
                        x_str, y_str = coords_text.split(',')
                        x = int(float(x_str.strip()))
                        y = int(float(y_str.strip()))
                        center_coords = [x, y]
                except (ValueError, IndexError):
                    pass
            elif line.startswith('DESCRIPTION:'):
                description = line.replace('DESCRIPTION:', '').strip()
        
        return {
            "found": found,
            "center_coordinates": center_coords,
            "confidence": 1.0 if found else 0.0,
            "description": description,
            "metadata": result["metadata"]
        }
    
    async def classify_image(
        self, 
        image: Union[str, BinaryIO],
        categories: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Classify image into categories"""
        if categories:
            category_list = ", ".join(categories)
            prompt = f"Classify this image into one of these categories: {category_list}. Respond with only the most appropriate category name."
        else:
            prompt = "What category best describes this image? Provide a single category name."
        
        result = await self.analyze_image(image, prompt, 100)
        category = result["text"].strip()
        
        return {
            "category": category,
            "confidence": 1.0,
            "all_predictions": [{"category": category, "confidence": 1.0}],
            "metadata": result["metadata"]
        }
    
    async def compare_images(
        self, 
        image1: Union[str, BinaryIO],
        image2: Union[str, BinaryIO]
    ) -> Dict[str, Any]:
        """Compare two images for similarity"""
        # For now, analyze both images separately and compare descriptions
        result1 = await self.analyze_image(image1, "Describe this image in detail.")
        result2 = await self.analyze_image(image2, "Describe this image in detail.")
        
        # Use LLM to compare the descriptions
        comparison_prompt = f"Compare these two image descriptions and provide a similarity analysis:\n\nImage 1: {result1['text']}\n\nImage 2: {result2['text']}\n\nProvide: 1) A similarity score from 0.0 to 1.0, 2) Key differences, 3) Common elements."
        
        comparison_result = await self._client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": comparison_prompt}],
            max_tokens=500,
            temperature=0.3
        )
        
        comparison_text = comparison_result.choices[0].message.content or ""
        
        return {
            "similarity_score": 0.5,  # Would need better parsing to extract actual score
            "differences": comparison_text,
            "common_elements": comparison_text,
            "metadata": {
                "model": self.model_name,
                "comparison_method": "description_based"
            }
        }
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported image formats"""
        return ['jpg', 'jpeg', 'png', 'gif', 'webp']
    
    def get_max_image_size(self) -> Dict[str, int]:
        """Get maximum supported image dimensions"""
        return {
            "width": 2048,
            "height": 2048,
            "file_size_mb": 20
        }
    
    async def close(self):
        """Clean up resources"""
        if hasattr(self._client, 'close'):
            await self._client.close()
