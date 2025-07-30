from typing import Dict, Any, Union, List, Optional, BinaryIO
import base64
import os
import replicate
import re
import ast
from isa_model.inference.services.vision.base_vision_service import BaseVisionService
from isa_model.inference.providers.base_provider import BaseProvider
from isa_model.inference.billing_tracker import ServiceType
import logging

logger = logging.getLogger(__name__)

class ReplicateVisionService(BaseVisionService):
    """Enhanced Replicate Vision service supporting multiple specialized models"""
    
    # Supported model configurations
    MODELS = {
        "cogvlm": "cjwbw/cogvlm:a5092d718ea77a073e6d8f6969d5c0fb87d0ac7e4cdb7175427331e1798a34ed",
        "florence-2": "microsoft/florence-2-large:fcdb54e52322b9e6dce7a35e5d8ad173dce30b46ef49a236c1a71bc6b78b5bed",
        "omniparser": "microsoft/omniparser-v2:49cf3d41b8d3aca1360514e83be4c97131ce8f0d99abfc365526d8384caa88df",
        "yolov8": "adirik/yolov8:3b21ba0e5da47bb2c69a96f72894a31b7c1e77b3e8a7b6ba43b7eb93b7b2c4f4"
    }
    
    def __init__(self, provider: 'BaseProvider', model_name: str = "cogvlm"):
        # Resolve model name to full model path
        self.model_key = model_name
        resolved_model = self.MODELS.get(model_name, model_name)
        super().__init__(provider, resolved_model)
        
        # Get full configuration from provider
        provider_config = provider.get_full_config()
        
        # Initialize Replicate client
        try:
            # Get API token - try different possible keys like the image gen service
            self.api_token = provider_config.get("api_token") or provider_config.get("replicate_api_token") or provider_config.get("api_key")
            
            if not self.api_token:
                raise ValueError("Replicate API token not found in provider configuration")
            
            # Set API token for replicate
            os.environ["REPLICATE_API_TOKEN"] = self.api_token
            
            logger.info(f"Initialized ReplicateVisionService with model {self.model_key} ({self.model_name})")
            
        except Exception as e:
            logger.error(f"Failed to initialize Replicate client: {e}")
            raise ValueError(f"Failed to initialize Replicate client. Check your API key configuration: {e}") from e
        
        self.temperature = provider_config.get('temperature', 0.7)
    
    def _prepare_image(self, image: Union[str, BinaryIO]) -> str:
        """Prepare image for Replicate API - convert to URL or base64"""
        if isinstance(image, str):
            if image.startswith(('http://', 'https://')):
                # Already a URL
                return image
            else:
                # Local file path - need to convert to base64 data URL
                with open(image, "rb") as f:
                    image_data = f.read()
                    image_b64 = base64.b64encode(image_data).decode()
                    # Determine file extension for MIME type
                    ext = os.path.splitext(image)[1].lower()
                    mime_type = {
                        '.jpg': 'image/jpeg',
                        '.jpeg': 'image/jpeg', 
                        '.png': 'image/png',
                        '.gif': 'image/gif',
                        '.webp': 'image/webp'
                    }.get(ext, 'image/jpeg')
                    return f"data:{mime_type};base64,{image_b64}"
        else:
            # BinaryIO or bytes data - convert to base64 data URL
            if hasattr(image, 'read'):
                image_data = image.read()
                if isinstance(image_data, bytes):
                    image_b64 = base64.b64encode(image_data).decode()
                else:
                    raise ValueError("File-like object did not return bytes")
            else:
                # Assume it's bytes
                image_b64 = base64.b64encode(image).decode()  # type: ignore
            return f"data:image/jpeg;base64,{image_b64}"
    
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
        elif task == "element_detection":
            if self.model_key == "omniparser":
                return await self.run_omniparser(image, **kwargs)
            elif self.model_key == "florence-2":
                return await self.run_florence2(image, **kwargs)
            elif self.model_key == "yolov8":
                return await self.run_yolo(image, **kwargs)
            else:
                return await self.detect_objects(image, kwargs.get("confidence_threshold", 0.5))
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
            # Prepare image for API
            image_input = self._prepare_image(image)
            
            # Use default prompt if none provided
            if prompt is None:
                prompt = "Describe this image in detail."
            
            # Run CogVLM model
            output = replicate.run(
                self.model_name,
                input={
                    "vqa": True,  # Visual Question Answering mode
                    "image": image_input,
                    "query": prompt
                }
            )
            
            # CogVLM returns a string response
            response_text = str(output) if output else ""
            
            # Track usage for billing
            self._track_usage(
                service_type=ServiceType.VISION,
                operation="image_analysis",
                input_tokens=len(prompt.split()) if prompt else 0,
                output_tokens=len(response_text.split()),
                metadata={"prompt": prompt[:100] if prompt else "", "model": self.model_name}
            )
            
            return {
                "text": response_text,
                "confidence": 1.0,  # CogVLM doesn't provide confidence scores
                "detected_objects": [],  # Would need separate object detection
                "metadata": {
                    "model": self.model_name,
                    "prompt": prompt,
                    "tokens_used": len(response_text.split())
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
            "bounding_boxes": [],  # CogVLM doesn't provide bounding boxes
            "language": "unknown",  # Would need language detection
            "metadata": result["metadata"]
        }
    
    async def detect_objects(
        self, 
        image: Union[str, BinaryIO],
        confidence_threshold: float = 0.5
    ) -> Dict[str, Any]:
        """Detect objects in image"""
        prompt = """Analyze this image and identify all distinct objects, UI elements, or regions. For each element you identify, provide its location and size as percentages.

Look carefully at the image and identify distinct visual elements like:
- Text regions, buttons, input fields, images
- Distinct objects, shapes, or regions
- Interactive elements like buttons or form controls

For each element, respond in this EXACT format:
ElementName: x=X%, y=Y%, width=W%, height=H% - Description

Where:
- x% = horizontal position from left edge (0-100%)
- y% = vertical position from top edge (0-100%) 
- width% = element width as percentage of image width (0-100%)
- height% = element height as percentage of image height (0-100%)

Be precise about the actual visual boundaries of each element.

Example: "Submit Button: x=25%, y=60%, width=15%, height=5% - Blue rectangular button with white text"
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

Look carefully at the image to find the exact element described. Be very precise about the location.

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
        
        # Use another CogVLM call to compare the descriptions
        comparison_prompt = f"Compare these two image descriptions and provide a similarity analysis:\n\nImage 1: {result1['text']}\n\nImage 2: {result2['text']}\n\nProvide: 1) A similarity score from 0.0 to 1.0, 2) Key differences, 3) Common elements."
        
        # Create a simple text prompt for comparison
        comparison_result = await self.analyze_image(image1, comparison_prompt)
        
        comparison_text = comparison_result["text"]
        
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
            "file_size_mb": 10
        }
    
    # ==================== MODEL-SPECIFIC METHODS ====================
    
    async def run_omniparser(
        self, 
        image: Union[str, BinaryIO],
        imgsz: int = 640,
        box_threshold: float = 0.05,
        iou_threshold: float = 0.1
    ) -> Dict[str, Any]:
        """Run OmniParser-v2 for UI element detection"""
        if self.model_key != "omniparser":
            # Switch to OmniParser model temporarily
            original_model = self.model_name
            self.model_name = self.MODELS["omniparser"]
        
        try:
            image_input = self._prepare_image(image)
            
            output = replicate.run(
                self.model_name,
                input={
                    "image": image_input,
                    "imgsz": imgsz,
                    "box_threshold": box_threshold,
                    "iou_threshold": iou_threshold
                }
            )
            
            # Parse OmniParser output format
            elements = []
            if isinstance(output, dict) and 'elements' in output:
                elements_text = output['elements']
                elements = self._parse_omniparser_elements(elements_text, image)
            
            return {
                "model": "omniparser",
                "raw_output": output,
                "parsed_elements": elements,
                "metadata": {
                    "imgsz": imgsz,
                    "box_threshold": box_threshold,
                    "iou_threshold": iou_threshold
                }
            }
            
        finally:
            if self.model_key != "omniparser":
                # Restore original model
                self.model_name = original_model
    
    async def run_florence2(
        self,
        image: Union[str, BinaryIO],
        task: str = "<OPEN_VOCABULARY_DETECTION>",
        text_input: Optional[str] = None
    ) -> Dict[str, Any]:
        """Run Florence-2 for object detection and description"""
        if self.model_key != "florence-2":
            original_model = self.model_name
            self.model_name = self.MODELS["florence-2"]
        
        try:
            image_input = self._prepare_image(image)
            
            input_params = {
                "image": image_input,
                "task": task
            }
            if text_input:
                input_params["text_input"] = text_input
            
            output = replicate.run(self.model_name, input=input_params)
            
            # Parse Florence-2 output
            parsed_objects = []
            if isinstance(output, dict):
                parsed_objects = self._parse_florence2_output(output, image)
            
            return {
                "model": "florence-2",
                "task": task,
                "raw_output": output,
                "parsed_objects": parsed_objects,
                "metadata": {"task": task, "text_input": text_input}
            }
            
        finally:
            if self.model_key != "florence-2":
                self.model_name = original_model
    
    async def run_yolo(
        self,
        image: Union[str, BinaryIO],
        confidence: float = 0.5,
        iou_threshold: float = 0.45
    ) -> Dict[str, Any]:
        """Run YOLO for general object detection"""
        if self.model_key != "yolov8":
            original_model = self.model_name
            self.model_name = self.MODELS["yolov8"]
        
        try:
            image_input = self._prepare_image(image)
            
            output = replicate.run(
                self.model_name,
                input={
                    "image": image_input,
                    "confidence": confidence,
                    "iou_threshold": iou_threshold
                }
            )
            
            # Parse YOLO output
            detected_objects = []
            if output:
                detected_objects = self._parse_yolo_output(output, image)
            
            return {
                "model": "yolov8",
                "raw_output": output,
                "detected_objects": detected_objects,
                "metadata": {
                    "confidence": confidence,
                    "iou_threshold": iou_threshold
                }
            }
            
        finally:
            if self.model_key != "yolov8":
                self.model_name = original_model
    
    # ==================== PARSING HELPERS ====================
    
    def _parse_omniparser_elements(self, elements_text: str, image: Union[str, BinaryIO]) -> List[Dict[str, Any]]:
        """Parse OmniParser-v2 elements format"""
        elements = []
        
        # Get image dimensions for coordinate conversion
        from PIL import Image as PILImage
        if isinstance(image, str):
            img = PILImage.open(image)
        else:
            img = PILImage.open(image)
        img_width, img_height = img.size
        
        try:
            # Extract individual icon entries
            icon_pattern = r"icon (\d+): ({.*?})\n?"
            matches = re.findall(icon_pattern, elements_text, re.DOTALL)
            
            for icon_id, icon_data_str in matches:
                try:
                    icon_data = eval(icon_data_str)  # Safe since we control the source
                    
                    bbox = icon_data.get('bbox', [])
                    element_type = icon_data.get('type', 'unknown')
                    interactivity = icon_data.get('interactivity', False)
                    content = icon_data.get('content', '').strip()
                    
                    if len(bbox) == 4:
                        # Convert normalized coordinates to pixel coordinates
                        x1_norm, y1_norm, x2_norm, y2_norm = bbox
                        x1 = int(x1_norm * img_width)
                        y1 = int(y1_norm * img_height)
                        x2 = int(x2_norm * img_width)
                        y2 = int(y2_norm * img_height)
                        
                        element = {
                            'id': f'omni_icon_{icon_id}',
                            'bbox': [x1, y1, x2, y2],
                            'center': [int((x1 + x2) / 2), int((y1 + y2) / 2)],
                            'size': [x2 - x1, y2 - y1],
                            'type': element_type,
                            'interactivity': interactivity,
                            'content': content,
                            'confidence': 0.9
                        }
                        elements.append(element)
                        
                except Exception as e:
                    logger.warning(f"Failed to parse icon {icon_id}: {e}")
                    
        except Exception as e:
            logger.error(f"Failed to parse OmniParser elements: {e}")
        
        return elements
    
    def _parse_florence2_output(self, output: Dict[str, Any], image: Union[str, BinaryIO]) -> List[Dict[str, Any]]:
        """Parse Florence-2 detection output"""
        objects = []
        
        try:
            # Florence-2 typically returns nested detection data
            for key, value in output.items():
                if isinstance(value, dict) and ('bboxes' in value and 'labels' in value):
                    bboxes = value['bboxes']
                    labels = value['labels']
                    
                    for i, (label, bbox) in enumerate(zip(labels, bboxes)):
                        if len(bbox) >= 4:
                            x1, y1, x2, y2 = bbox[:4]
                            obj = {
                                'id': f'florence_{i}',
                                'label': label,
                                'bbox': [int(x1), int(y1), int(x2), int(y2)],
                                'center': [int((x1 + x2) / 2), int((y1 + y2) / 2)],
                                'size': [int(x2 - x1), int(y2 - y1)],
                                'confidence': 0.9
                            }
                            objects.append(obj)
                            
        except Exception as e:
            logger.error(f"Failed to parse Florence-2 output: {e}")
        
        return objects
    
    def _parse_yolo_output(self, output: Any, image: Union[str, BinaryIO]) -> List[Dict[str, Any]]:
        """Parse YOLO detection output"""
        objects = []
        
        try:
            # YOLO output format varies, handle common formats
            if isinstance(output, list):
                for i, detection in enumerate(output):
                    if isinstance(detection, dict):
                        bbox = detection.get('bbox', detection.get('box', []))
                        label = detection.get('class', detection.get('label', f'object_{i}'))
                        confidence = detection.get('confidence', detection.get('score', 0.9))
                        
                        if len(bbox) >= 4:
                            x1, y1, x2, y2 = bbox[:4]
                            obj = {
                                'id': f'yolo_{i}',
                                'label': label,
                                'bbox': [int(x1), int(y1), int(x2), int(y2)],
                                'center': [int((x1 + x2) / 2), int((y1 + y2) / 2)],
                                'size': [int(x2 - x1), int(y2 - y1)],
                                'confidence': float(confidence)
                            }
                            objects.append(obj)
                            
        except Exception as e:
            logger.error(f"Failed to parse YOLO output: {e}")
        
        return objects

    async def close(self):
        """Clean up resources"""
        # Replicate doesn't need explicit cleanup
        pass