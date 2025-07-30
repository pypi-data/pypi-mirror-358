"""
UI Analysis Stacked Service

A stacked service for analyzing UI screenshots using multiple AI models:
- Layer 1: Page Intelligence (GPT-4V)
- Layer 2: Element Detection (OmniParser/Florence-2/YOLO)  
- Layer 3: Classification (GPT-4V)
"""

from typing import Dict, Any, List, Optional, Union, BinaryIO
import json
from PIL import Image, ImageDraw, ImageFont

from .base_stacked_service import BaseStackedService, LayerConfig, LayerType, LayerResult

class UIAnalysisService(BaseStackedService):
    """
    Generic UI Analysis service using stacked AI models for comprehensive UI understanding.
    Can handle different page types: login, search, content extraction, navigation, etc.
    """
    
    def __init__(self, ai_factory, config=None):
        super().__init__(ai_factory, "ui_analysis")
        self.ai_factory = ai_factory
        self.config = config or {}
        self.task_type = self.config.get("task_type", "login")  # Default to login for backward compatibility
        self._setup_layers_by_task()
    
    def _setup_layers_by_task(self):
        """Setup layer configuration based on task type"""
        
        if self.task_type == "search":
            self._setup_search_layers()
        elif self.task_type == "content":
            self._setup_content_layers()
        elif self.task_type == "navigation":
            self._setup_navigation_layers()
        else:
            # Default to login/form analysis
            self._setup_default_layers()
    
    def _setup_default_layers(self):
        """Setup simplified two-layer architecture for UI analysis"""
        
        # Layer 1: OmniParser 元素检测
        self.add_layer(LayerConfig(
            name="ui_detection",
            layer_type=LayerType.DETECTION,
            service_type="vision",
            model_name="omniparser",
            parameters={
                "task": "ui_detection",
                "imgsz": 640,
                "box_threshold": 0.05,
                "iou_threshold": 0.1
            },
            depends_on=[],
            timeout=30.0,
            fallback_enabled=True
        ))
        
        # Layer 2: GPT-4.1-nano 智能决策
        self.add_layer(LayerConfig(
            name="action_planning",
            layer_type=LayerType.INTELLIGENCE,
            service_type="vision",
            model_name="default",
            parameters={
                "task": "action_planning",
                "max_tokens": 500
            },
            depends_on=["ui_detection"],
            timeout=15.0,
            fallback_enabled=False
        ))
    
    def _setup_search_layers(self):
        """Setup simplified two-layer architecture for search page analysis"""
        
        self.add_layer(LayerConfig(
            name="ui_detection",
            layer_type=LayerType.DETECTION,
            service_type="vision",
            model_name="omniparser",
            parameters={
                "task": "ui_detection",
                "imgsz": 640,
                "box_threshold": 0.05,
                "iou_threshold": 0.1
            },
            depends_on=[],
            timeout=30.0,
            fallback_enabled=True
        ))
        
        self.add_layer(LayerConfig(
            name="action_planning",
            layer_type=LayerType.INTELLIGENCE,
            service_type="vision",
            model_name="default",
            parameters={
                "task": "search_action_planning",
                "max_tokens": 500
            },
            depends_on=["ui_detection"],
            timeout=15.0,
            fallback_enabled=False
        ))
    
    def _setup_content_layers(self):
        """Setup simplified two-layer architecture for content extraction"""
        
        self.add_layer(LayerConfig(
            name="ui_detection",
            layer_type=LayerType.DETECTION,
            service_type="vision",
            model_name="omniparser",
            parameters={
                "task": "ui_detection",
                "imgsz": 640,
                "box_threshold": 0.05,
                "iou_threshold": 0.1
            },
            depends_on=[],
            timeout=30.0,
            fallback_enabled=True
        ))
        
        self.add_layer(LayerConfig(
            name="action_planning",
            layer_type=LayerType.INTELLIGENCE,
            service_type="vision",
            model_name="default",
            parameters={
                "task": "content_action_planning",
                "max_tokens": 500
            },
            depends_on=["ui_detection"],
            timeout=15.0,
            fallback_enabled=False
        ))
    
    def _setup_navigation_layers(self):
        """Setup simplified two-layer architecture for navigation analysis"""
        
        self.add_layer(LayerConfig(
            name="ui_detection",
            layer_type=LayerType.DETECTION,
            service_type="vision",
            model_name="omniparser",
            parameters={
                "task": "ui_detection",
                "imgsz": 640,
                "box_threshold": 0.05,
                "iou_threshold": 0.1
            },
            depends_on=[],
            timeout=30.0,
            fallback_enabled=True
        ))
        
        self.add_layer(LayerConfig(
            name="action_planning",
            layer_type=LayerType.INTELLIGENCE,
            service_type="vision",
            model_name="default",
            parameters={
                "task": "navigation_action_planning",
                "max_tokens": 500
            },
            depends_on=["ui_detection"],
            timeout=15.0,
            fallback_enabled=False
        ))
    
    def configure_detection_model(self, model_name: str, parameters: Dict[str, Any]):
        """Configure the detection model and parameters"""
        for layer in self.layers:
            if layer.name == "element_detection":
                layer.model_name = model_name
                layer.parameters.update(parameters)
                break
    
    def configure_intelligence_model(self, model_name: str, parameters: Dict[str, Any]):
        """Configure the page intelligence model"""
        for layer in self.layers:
            if layer.name == "page_intelligence":
                layer.model_name = model_name
                layer.parameters.update(parameters)
                break
    
    async def execute_layer_logic(self, layer: LayerConfig, service: Any, context: Dict[str, Any]) -> Any:
        """Execute specific logic for each layer type using unified invoke method"""
        
        task = layer.parameters.get("task")
        image_path = context["input"]["image_path"]
        
        if task == "ui_detection":
            return await self._invoke_ui_detection(service, image_path, layer.parameters)
        
        elif task in ["action_planning", "search_action_planning", "content_action_planning", "navigation_action_planning"]:
            ui_elements = context["results"]["ui_detection"].data
            return await self._invoke_action_planning(service, image_path, ui_elements, layer.parameters)
        
        else:
            raise ValueError(f"Unsupported task: {task}")
    
    # ==================== SIMPLIFIED TWO-LAYER METHODS ====================
    
    async def _invoke_ui_detection(self, service: Any, image_path: str, parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """执行UI元素检测（第一层）"""
        
        if hasattr(service, 'run_omniparser'):
            result = await service.run_omniparser(
                image=image_path,
                **{k: v for k, v in parameters.items() if k != "task"}
            )
            
            # 返回所有元素（包括文本和交互元素）
            elements = result.get("parsed_elements", [])
            
            # 添加更多有用的信息
            for i, element in enumerate(elements):
                element['element_id'] = i
                element['element_index'] = i
                
                # 计算中心点坐标
                bbox = element.get('bbox', [0, 0, 0, 0])
                if len(bbox) == 4:
                    # 转换归一化坐标到像素坐标
                    img = Image.open(image_path)
                    img_width, img_height = img.size
                    
                    x1, y1, x2, y2 = bbox
                    pixel_x1 = int(x1 * img_width)
                    pixel_y1 = int(y1 * img_height)
                    pixel_x2 = int(x2 * img_width)
                    pixel_y2 = int(y2 * img_height)
                    
                    element['pixel_bbox'] = [pixel_x1, pixel_y1, pixel_x2, pixel_y2]
                    element['center'] = [
                        (pixel_x1 + pixel_x2) // 2,
                        (pixel_y1 + pixel_y2) // 2
                    ]
                    element['size'] = [pixel_x2 - pixel_x1, pixel_y2 - pixel_y1]
            
            return elements
        else:
            raise ValueError("OmniParser service not available")
    
    async def _invoke_action_planning(self, service: Any, image_path: str, ui_elements: List[Dict[str, Any]], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """执行行动规划（第二层）"""
        
        task_type = parameters.get("task", "action_planning")
        
        # 构建元素摘要
        elements_summary = []
        interactive_elements = []
        
        for element in ui_elements:
            summary = {
                "id": element.get('element_id'),
                "type": element.get('type'),
                "center": element.get('center'),
                "content": element.get('content', ''),
                "interactivity": element.get('interactivity', False),
                "size": element.get('size')
            }
            elements_summary.append(summary)
            
            if element.get('interactivity', False):
                interactive_elements.append(summary)
        
        # 构建智能决策提示词
        prompt = self._build_action_planning_prompt(
            task_type=task_type,
            elements_summary=elements_summary,
            interactive_elements=interactive_elements
        )
        
        # 调用GPT进行决策
        result = await service.invoke(
            image=image_path,
            prompt=prompt,
            task="analyze",
            max_tokens=parameters.get("max_tokens", 500)
        )
        
        # 解析决策结果
        decision = self._parse_action_plan(result.get('text', ''))
        
        # 将决策与实际元素匹配
        action_plan = self._match_actions_to_elements(decision, ui_elements)
        
        return action_plan

    # ==================== UNIFIED INVOKE METHODS ====================
    
    async def _invoke_page_intelligence(self, service: Any, image_path: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Invoke page intelligence analysis using unified interface"""
        
        task = parameters.get("task", "page_intelligence")
        prompt = self._get_intelligence_prompt(task)

        # Use unified invoke method
        result = await service.invoke(
            image=image_path,
            prompt=prompt,
            task="analyze",
            max_tokens=parameters.get("max_tokens", 500)
        )
        
        # Parse JSON response
        response_text = result['text'].strip()
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        
        if json_start >= 0 and json_end > json_start:
            json_text = response_text[json_start:json_end]
            try:
                intelligence_data = json.loads(json_text)
            except json.JSONDecodeError:
                intelligence_data = self._parse_intelligence_fallback(response_text)
        else:
            intelligence_data = self._parse_intelligence_fallback(response_text)
        
        return intelligence_data
    
    def _get_intelligence_prompt(self, task: str) -> str:
        """Get task-specific prompt for page intelligence"""
        
        if task == "search_page_intelligence":
            return '''Analyze this webpage screenshot to understand the search interface structure.

Identify:
1. Page type (search_engine, search_results, query_page, homepage)
2. Search elements (search box, search button, filters, suggestions)
3. Layout pattern (header_search, center_search, sidebar_search)
4. Language used in the interface
5. Additional features (voice search, image search, advanced options)
6. Visible text elements and labels

Return analysis as JSON with this exact structure:
{
  "page_type": "search_engine|search_results|query_page|homepage|other",
  "layout_pattern": "header_search|center_search|sidebar_search|embedded",
  "language": "en|zh|es|fr|de|other",
  "search_features": ["voice_search", "image_search", "advanced_options", "suggestions"],
  "complexity_score": 0.1-1.0,
  "visible_text_elements": ["Search", "Google Search", "I'm Feeling Lucky"],
  "search_area_estimate": {"x": 0, "y": 0, "width": 0, "height": 0},
  "confidence": 0.1-1.0,
  "analysis_notes": "brief description of what you observe"
}

Be precise and only include elements you can clearly see.'''
            
        elif task == "content_page_intelligence":
            return '''Analyze this webpage screenshot to understand the content structure.

Identify:
1. Page type (article, blog, news, documentation, product_page)
2. Content layout (single_column, multi_column, grid, sidebar)
3. Content elements (headings, paragraphs, images, videos, links)
4. Language used in the interface
5. Navigation elements (menu, breadcrumbs, pagination)
6. Visible text content and structure

Return analysis as JSON with this exact structure:
{
  "page_type": "article|blog|news|documentation|product_page|other",
  "layout_pattern": "single_column|multi_column|grid|sidebar",
  "language": "en|zh|es|fr|de|other",
  "content_features": ["headings", "paragraphs", "images", "videos", "links", "navigation"],
  "complexity_score": 0.1-1.0,
  "visible_text_elements": ["Title", "Content", "Read More"],
  "content_area_estimate": {"x": 0, "y": 0, "width": 0, "height": 0},
  "confidence": 0.1-1.0,
  "analysis_notes": "brief description of what you observe"
}

Be precise and only include elements you can clearly see.'''
            
        elif task == "navigation_page_intelligence":
            return '''Analyze this webpage screenshot to understand the navigation structure.

Identify:
1. Page type (homepage, category_page, landing_page, dashboard)
2. Navigation elements (menu, toolbar, sidebar, footer)
3. Layout pattern (horizontal_nav, vertical_nav, dropdown_nav, mega_menu)
4. Language used in the interface
5. Interactive elements (buttons, links, icons, search)
6. Visible navigation labels and structure

Return analysis as JSON with this exact structure:
{
  "page_type": "homepage|category_page|landing_page|dashboard|other",
  "layout_pattern": "horizontal_nav|vertical_nav|dropdown_nav|mega_menu",
  "language": "en|zh|es|fr|de|other",
  "navigation_features": ["main_menu", "sidebar", "footer", "breadcrumbs", "search"],
  "complexity_score": 0.1-1.0,
  "visible_text_elements": ["Home", "About", "Contact", "Products"],
  "navigation_area_estimate": {"x": 0, "y": 0, "width": 0, "height": 0},
  "confidence": 0.1-1.0,
  "analysis_notes": "brief description of what you observe"
}

Be precise and only include elements you can clearly see.'''
            
        else:
            # Default login/form analysis prompt
            return '''Analyze this webpage screenshot to understand the login interface structure.

Identify:
1. Page type (login, register, multi-step auth, SSO)
2. Layout pattern (vertical form, horizontal, modal, tabs)
3. Language used in the interface
4. Security features visible (CAPTCHA, 2FA indicators)
5. Form complexity level
6. Visible text elements that indicate field purposes

Return analysis as JSON with this exact structure:
{
  "page_type": "login|register|multi_step|sso|other",
  "layout_pattern": "vertical|horizontal|modal|tabs|embedded",
  "language": "en|zh|es|fr|de|other",
  "security_features": ["captcha", "recaptcha", "2fa_indicator", "security_questions"],
  "complexity_score": 0.1-1.0,
  "visible_text_elements": ["Login", "Password", "Sign In"],
  "form_area_estimate": {"x": 0, "y": 0, "width": 0, "height": 0},
  "confidence": 0.1-1.0,
  "analysis_notes": "brief description of what you observe"
}

Be precise and only include elements you can clearly see.'''
    
    async def _invoke_element_detection(self, service: Any, image_path: str, intelligence: Dict[str, Any], parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Invoke element detection using unified interface"""
        
        # Adapt parameters based on page intelligence
        complexity = intelligence.get('complexity_score', 0.5)
        
        # Check if this is omniparser service
        if hasattr(service, 'run_omniparser'):
            # Use replicate omniparser
            params = {}
            if complexity > 0.7:
                params.update({
                    "box_threshold": 0.03,
                    "iou_threshold": 0.1,
                    "imgsz": 1024
                })
            else:
                params.update({
                    "box_threshold": parameters.get("box_threshold", 0.05),
                    "iou_threshold": parameters.get("iou_threshold", 0.1),
                    "imgsz": parameters.get("imgsz", 640)
                })
            
            result = await service.run_omniparser(image=image_path, **params)
            # Filter for interactive elements only
            elements = [e for e in result.get("parsed_elements", []) if e.get("interactivity", False)]
            return elements
        else:
            # Use fallback generic detection
            return await self._fallback_element_detection(service, image_path, intelligence)
    
    async def _invoke_element_classification(self, service: Any, image_path: str, elements: List[Dict[str, Any]], intelligence: Dict[str, Any], parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Invoke element classification using unified interface"""
        
        classified_elements = []
        img = Image.open(image_path)
        
        for i, element in enumerate(elements):
            # Crop element region with padding
            bbox = element['bbox']
            x1, y1, x2, y2 = bbox
            
            padding_x = max(20, int((x2 - x1) * 0.2))
            padding_y = max(20, int((y2 - y1) * 0.2))
            
            crop_x1 = max(0, x1 - padding_x)
            crop_y1 = max(0, y1 - padding_y)
            crop_x2 = min(img.width, x2 + padding_x)
            crop_y2 = min(img.height, y2 + padding_y)
            
            cropped_img = img.crop((crop_x1, crop_y1, crop_x2, crop_y2))
            crop_path = f"temp_classify_{i}.png"
            cropped_img.save(crop_path)
            
            try:
                context_info = f'''Page Context:
- Type: {intelligence.get('page_type', 'unknown')}
- Layout: {intelligence.get('layout_pattern', 'unknown')}
- Language: {intelligence.get('language', 'en')}
- Complexity: {intelligence.get('complexity_score', 0.5)}

Element Context:
- Position: {element.get('center', [0, 0])} (center)
- Size: {element.get('size', [0, 0])} (width x height)
- Element {i+1} of {len(elements)} total elements'''

                prompt = f'''Classify this UI element from a login/authentication interface.

{context_info}

Classify as one of:
- username_field: for username, email, user ID inputs
- password_field: for password inputs
- confirm_password: for password confirmation fields
- login_button: for sign in/login buttons
- register_button: for sign up/register buttons  
- submit_button: for general form submission
- checkbox: for remember me, terms agreement
- link: for forgot password, register links
- other: for unrelated elements

Response format:
{{
  "classification": "username_field|password_field|login_button|other",
  "confidence": 0.1-1.0,
  "reasoning": "brief explanation of classification decision",
  "visual_evidence": ["text_visible", "styling_clues", "position_indicators"],
  "interaction_priority": 1-10
}}'''

                # Use unified invoke method
                result = await service.invoke(
                    image=crop_path,
                    prompt=prompt,
                    task="analyze",
                    max_tokens=parameters.get("max_tokens", 300)
                )
                
                classification_data = self._parse_classification_result(result['text'])
                
                # Use original detection center coordinates
                classified_element = {
                    **element,
                    'classification': classification_data.get('classification', 'other'),
                    'classification_confidence': classification_data.get('confidence', 0.5),
                    'precise_center': element.get('center', [0, 0]),
                    'reasoning': classification_data.get('reasoning', ''),
                    'visual_evidence': classification_data.get('visual_evidence', []),
                    'interaction_priority': classification_data.get('interaction_priority', 5),
                    'crop_region': [crop_x1, crop_y1, crop_x2, crop_y2]
                }
                
                classified_elements.append(classified_element)
                
            except Exception as e:
                # Keep element with basic classification
                classified_element = {
                    **element,
                    'classification': 'other',
                    'classification_confidence': 0.3,
                    'precise_center': element.get('center', [0, 0]),
                    'reasoning': f'Classification failed: {str(e)}',
                    'visual_evidence': [],
                    'interaction_priority': 5,
                    'error': str(e)
                }
                classified_elements.append(classified_element)
            
            finally:
                # Cleanup temp file
                try:
                    import os
                    os.remove(crop_path)
                except:
                    pass
        
        return classified_elements
    
    # ==================== LEGACY METHODS (for compatibility) ====================
    
    async def _execute_page_intelligence(self, layer: LayerConfig, service: Any, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute page intelligence analysis"""
        image_path = context["input"]["image_path"]
        
        prompt = '''Analyze this webpage screenshot to understand the login interface structure.

Identify:
1. Page type (login, register, multi-step auth, SSO)
2. Layout pattern (vertical form, horizontal, modal, tabs)
3. Language used in the interface
4. Security features visible (CAPTCHA, 2FA indicators)
5. Form complexity level
6. Visible text elements that indicate field purposes

Return analysis as JSON with this exact structure:
{
  "page_type": "login|register|multi_step|sso|other",
  "layout_pattern": "vertical|horizontal|modal|tabs|embedded",
  "language": "en|zh|es|fr|de|other",
  "security_features": ["captcha", "recaptcha", "2fa_indicator", "security_questions"],
  "complexity_score": 0.1-1.0,
  "visible_text_elements": ["Login", "Password", "Sign In"],
  "form_area_estimate": {"x": 0, "y": 0, "width": 0, "height": 0},
  "confidence": 0.1-1.0,
  "analysis_notes": "brief description of what you observe"
}

Be precise and only include elements you can clearly see.'''
        
        result = await service.invoke(
            image=image_path,
            prompt=prompt,
            task="analyze",
            max_tokens=layer.parameters.get("max_tokens", 500)
        )
        
        # Parse JSON response
        response_text = result['text'].strip()
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        
        if json_start >= 0 and json_end > json_start:
            json_text = response_text[json_start:json_end]
            try:
                intelligence_data = json.loads(json_text)
            except json.JSONDecodeError:
                # Fallback parsing
                intelligence_data = self._parse_intelligence_fallback(response_text)
        else:
            intelligence_data = self._parse_intelligence_fallback(response_text)
        
        return intelligence_data
    
    async def _execute_element_detection(self, layer: LayerConfig, service: Any, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute element detection"""
        image_path = context["input"]["image_path"]
        intelligence = context["results"]["page_intelligence"].data
        
        # Adapt parameters based on page intelligence
        complexity = intelligence.get('complexity_score', 0.5)
        params = layer.parameters.copy()
        
        if complexity > 0.7:
            params.update({
                "box_threshold": 0.03,
                "iou_threshold": 0.1,
                "imgsz": 1024
            })
        elif complexity > 0.4:
            params.update({
                "box_threshold": 0.05,
                "iou_threshold": 0.1,
                "imgsz": 640
            })
        else:
            params.update({
                "box_threshold": 0.08,
                "iou_threshold": 0.2,
                "imgsz": 640
            })
        
        # Run detection based on model type
        if layer.model_name == "omniparser":
            if hasattr(service, 'run_omniparser'):
                result = await service.run_omniparser(
                    image=image_path,
                    **params
                )
                # Filter for interactive elements only
                elements = [e for e in result.get("parsed_elements", []) if e.get("interactivity", False)]
            else:
                # Fallback for services without omniparser support
                elements = await self._fallback_element_detection(service, image_path, intelligence)
            
        elif layer.model_name == "florence-2":
            if hasattr(service, 'run_florence2'):
                result = await service.run_florence2(
                    image=image_path,
                    task="<OPEN_VOCABULARY_DETECTION>",
                    text_input="login form elements, input fields, buttons"
                )
                elements = result.get("parsed_objects", [])
            else:
                elements = await self._fallback_element_detection(service, image_path, intelligence)
            
        elif layer.model_name == "yolov8":
            if hasattr(service, 'run_yolo'):
                result = await service.run_yolo(
                    image=image_path,
                    confidence=params.get("box_threshold", 0.5)
                )
                elements = result.get("detected_objects", [])
            else:
                elements = await self._fallback_element_detection(service, image_path, intelligence)
            
        else:
            # Fallback to generic object detection
            elements = await self._fallback_element_detection(service, image_path, intelligence)
        
        return elements
    
    async def _execute_element_classification(self, layer: LayerConfig, service: Any, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute element classification"""
        image_path = context["input"]["image_path"]
        elements = context["results"]["element_detection"].data
        intelligence = context["results"]["page_intelligence"].data
        
        classified_elements = []
        img = Image.open(image_path)
        
        for i, element in enumerate(elements):
            # Crop element region with padding
            bbox = element['bbox']
            x1, y1, x2, y2 = bbox
            
            padding_x = max(20, int((x2 - x1) * 0.2))
            padding_y = max(20, int((y2 - y1) * 0.2))
            
            crop_x1 = max(0, x1 - padding_x)
            crop_y1 = max(0, y1 - padding_y)
            crop_x2 = min(img.width, x2 + padding_x)
            crop_y2 = min(img.height, y2 + padding_y)
            
            cropped_img = img.crop((crop_x1, crop_y1, crop_x2, crop_y2))
            crop_path = f"temp_classify_{i}.png"
            cropped_img.save(crop_path)
            
            try:
                context_info = f'''Page Context:
- Type: {intelligence.get('page_type', 'unknown')}
- Layout: {intelligence.get('layout_pattern', 'unknown')}
- Language: {intelligence.get('language', 'en')}
- Complexity: {intelligence.get('complexity_score', 0.5)}

Element Context:
- Position: {element.get('center', [0, 0])} (center)
- Size: {element.get('size', [0, 0])} (width x height)
- Element {i+1} of {len(elements)} total elements'''

                # Get task-specific classification prompt
                prompt = self._get_classification_prompt(
                    parameters.get("task", "element_classification"), 
                    context_info
                )

                result = await service.invoke(
                    image=crop_path,
                    prompt=prompt,
                    task="analyze",
                    max_tokens=layer.parameters.get("max_tokens", 300)
                )
                
                classification_data = self._parse_classification_result(result['text'])
                
                # Use original detection center coordinates
                classified_element = {
                    **element,
                    'classification': classification_data.get('classification', 'other'),
                    'classification_confidence': classification_data.get('confidence', 0.5),
                    'precise_center': element.get('center', [0, 0]),
                    'reasoning': classification_data.get('reasoning', ''),
                    'visual_evidence': classification_data.get('visual_evidence', []),
                    'interaction_priority': classification_data.get('interaction_priority', 5),
                    'crop_region': [crop_x1, crop_y1, crop_x2, crop_y2]
                }
                
                classified_elements.append(classified_element)
                
            except Exception as e:
                # Keep element with basic classification
                classified_element = {
                    **element,
                    'classification': 'other',
                    'classification_confidence': 0.3,
                    'precise_center': element.get('center', [0, 0]),
                    'reasoning': f'Classification failed: {str(e)}',
                    'visual_evidence': [],
                    'interaction_priority': 5,
                    'error': str(e)
                }
                classified_elements.append(classified_element)
            
            finally:
                # Cleanup temp file
                try:
                    import os
                    os.remove(crop_path)
                except:
                    pass
        
        return classified_elements
    
    async def execute_fallback(self, layer: LayerConfig, context: Dict[str, Any], error: str) -> Optional[Any]:
        """Execute fallback logic for failed layers"""
        
        if layer.layer_type == LayerType.INTELLIGENCE:
            # Return basic page intelligence
            return {
                "page_type": "login",
                "layout_pattern": "vertical",
                "language": "en",
                "security_features": [],
                "complexity_score": 0.5,
                "visible_text_elements": ["Login", "Password"],
                "form_area_estimate": {"x": 200, "y": 200, "width": 600, "height": 400},
                "confidence": 0.3,
                "analysis_notes": f"Fallback analysis due to error: {error}"
            }
        
        elif layer.layer_type == LayerType.DETECTION:
            # Create fallback elements based on typical form layout
            intelligence = context["results"]["page_intelligence"].data
            return self._create_fallback_elements(context["input"]["image_path"], intelligence)
        
        return None
    
    def generate_final_output(self, results: Dict[str, LayerResult]) -> Dict[str, Any]:
        """Generate final UI analysis output for simplified two-layer architecture"""
        
        # Extract data from the two layers
        ui_elements = results.get("ui_detection", {}).data or []
        action_plan = results.get("action_planning", {}).data or {}
        
        # 分离交互和非交互元素
        interactive_elements = [e for e in ui_elements if e.get('interactivity', False)]
        text_elements = [e for e in ui_elements if not e.get('interactivity', False)]
        
        return {
            "ui_elements": {
                "total_elements": len(ui_elements),
                "interactive_elements": interactive_elements,
                "text_elements": text_elements,
                "summary": {
                    "interactive_count": len(interactive_elements),
                    "text_count": len(text_elements)
                }
            },
            "action_plan": action_plan,
            "automation_ready": {
                "ready": action_plan.get("success_probability", 0) > 0.7,
                "confidence": action_plan.get("success_probability", 0),
                "steps_count": len(action_plan.get("action_plan", [])),
                "page_type": action_plan.get("page_analysis", {}).get("page_type", "unknown")
            },
            "execution_summary": {
                "can_automate": len(action_plan.get("action_plan", [])) > 0,
                "recommended_action": action_plan.get("action_plan", [{}])[0] if action_plan.get("action_plan") else None
            }
        }
    
    async def visualize_results(self, image_path: str, analysis_result: Dict[str, Any], 
                              output_path: str = "ui_analysis_result.png") -> str:
        """Generate visualization of the analysis results"""
        
        # Load original image
        img = Image.open(image_path)
        img_copy = img.copy()
        draw = ImageDraw.Draw(img_copy)
        
        try:
            font_large = ImageFont.truetype("arial.ttf", 24)
            font_small = ImageFont.truetype("arial.ttf", 16)
        except:
            font_large = None
            font_small = None
        
        colors = {
            'username_field': 'red',
            'password_field': 'blue', 
            'login_button': 'green',
            'register_button': 'orange',
            'submit_button': 'purple',
            'checkbox': 'yellow',
            'link': 'cyan',
            'other': 'gray'
        }
        
        final_output = analysis_result.get("final_output", {})
        classified_elements = final_output.get("classified_elements", [])
        
        # Draw each classified element
        for element in classified_elements:
            classification = element.get('classification', 'other')
            confidence = element.get('classification_confidence', 0)
            center = element.get('precise_center', element.get('center', [0, 0]))
            bbox = element.get('bbox', [0, 0, 100, 100])
            priority = element.get('interaction_priority', 5)
            
            color = colors.get(classification, 'gray')
            center_x, center_y = center
            x1, y1, x2, y2 = bbox
            
            # Draw bounding box
            draw.rectangle([x1, y1, x2, y2], outline=color, width=2)
            
            # Draw center crosshair
            crosshair_size = 35
            draw.line([center_x - crosshair_size, center_y, center_x + crosshair_size, center_y], 
                     fill=color, width=8)
            draw.line([center_x, center_y - crosshair_size, center_x, center_y + crosshair_size], 
                     fill=color, width=8)
            
            # Draw center circle
            circle_radius = 20
            draw.ellipse([center_x - circle_radius, center_y - circle_radius, 
                         center_x + circle_radius, center_y + circle_radius], 
                       outline=color, width=8)
            
            # Draw labels
            label = f"{classification.replace('_', ' ').title()}"
            detail = f"Conf: {confidence:.2f} | Pri: {priority}"
            
            if font_large:
                draw.text((x1, y1 - 50), label, fill=color, font=font_large)
                draw.text((x1, y1 - 25), detail, fill=color, font=font_small)
            else:
                draw.text((x1, y1 - 40), label, fill=color)
                draw.text((x1, y1 - 20), detail, fill=color)
        
        # Add header information
        intelligence = final_output.get("page_intelligence", {})
        summary = final_output.get("analysis_summary", {})
        
        header_text = f"UI Analysis: {summary.get('page_type', 'unknown')} | Elements: {summary.get('interactive_elements', 0)} | Confidence: {summary.get('overall_confidence', 0):.2f}"
        
        if font_large:
            draw.text((10, 10), "Stacked UI Analysis", fill='black', font=font_large)
            draw.text((10, 40), header_text, fill='black', font=font_small)
        else:
            draw.text((10, 10), "Stacked UI Analysis", fill='black')
            draw.text((10, 30), header_text, fill='black')
        
        # Save visualization
        img_copy.save(output_path)
        return output_path
    
    # Helper methods
    def _parse_intelligence_fallback(self, text: str) -> Dict[str, Any]:
        """Fallback parser for intelligence data"""
        return {
            "page_type": "login",
            "layout_pattern": "vertical",
            "language": "en",
            "security_features": [],
            "complexity_score": 0.6,
            "visible_text_elements": ["Username", "Password", "Login"],
            "form_area_estimate": {"x": 200, "y": 200, "width": 600, "height": 400},
            "confidence": 0.4,
            "analysis_notes": "Parsed from text analysis"
        }
    
    def _parse_classification_result(self, text: str) -> Dict[str, Any]:
        """Parse classification result from GPT response"""
        try:
            json_start = text.find('{')
            json_end = text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_text = text[json_start:json_end]
                return json.loads(json_text)
        except:
            pass
        
        # Fallback text parsing
        classification = 'other'
        confidence = 0.5
        
        text_lower = text.lower()
        if 'username' in text_lower or 'email' in text_lower:
            classification = 'username_field'
            confidence = 0.7
        elif 'password' in text_lower:
            classification = 'password_field'
            confidence = 0.7
        elif 'button' in text_lower and ('login' in text_lower or 'sign' in text_lower):
            classification = 'login_button'
            confidence = 0.7
        
        return {
            'classification': classification,
            'confidence': confidence,
            'reasoning': 'Parsed from text',
            'visual_evidence': ['text_analysis'],
            'interaction_priority': 5
        }
    
    def _get_classification_prompt(self, task: str, context_info: str) -> str:
        """Get task-specific classification prompt"""
        
        if task == "search_element_classification":
            return f'''Classify this UI element from a search interface.

{context_info}

Classify as one of:
- search_field: for search input boxes, query fields
- search_button: for search/go buttons, submit search
- search_suggestion: for autocomplete suggestions
- filter: for search filters, sorting options
- voice_search: for voice search buttons
- image_search: for image search options
- advanced_search: for advanced search links/options
- nav_link: for navigation menu items
- other: for unrelated elements

Response format:
{{
  "classification": "search_field|search_button|filter|nav_link|other",
  "confidence": 0.1-1.0,
  "reasoning": "brief explanation of classification decision",
  "visual_evidence": ["text_visible", "styling_clues", "position_indicators"],
  "interaction_priority": 1-10
}}'''
        
        elif task == "content_element_classification":
            return f'''Classify this UI element from a content page.

{context_info}

Classify as one of:
- article_title: for main article/page titles
- article_body: for main content/article text
- sidebar_content: for sidebar information
- navigation_menu: for navigation elements
- related_links: for related articles/links
- comment: for comment sections
- share_button: for social sharing
- read_more: for read more links
- image: for content images
- video: for embedded videos
- other: for unrelated elements

Response format:
{{
  "classification": "article_title|article_body|sidebar_content|navigation_menu|other",
  "confidence": 0.1-1.0,
  "reasoning": "brief explanation of classification decision",
  "visual_evidence": ["text_visible", "styling_clues", "position_indicators"],
  "interaction_priority": 1-10
}}'''
        
        elif task == "navigation_element_classification":
            return f'''Classify this UI element from a navigation-focused page.

{context_info}

Classify as one of:
- nav_link: for main navigation links
- menu_item: for menu items and categories
- breadcrumb: for breadcrumb navigation
- dropdown_menu: for dropdown menu elements
- footer_link: for footer navigation
- logo: for site logos/branding
- search_box: for site search functionality
- user_menu: for user account menus
- cta_button: for call-to-action buttons
- other: for unrelated elements

Response format:
{{
  "classification": "nav_link|menu_item|breadcrumb|dropdown_menu|other",
  "confidence": 0.1-1.0,
  "reasoning": "brief explanation of classification decision",
  "visual_evidence": ["text_visible", "styling_clues", "position_indicators"],
  "interaction_priority": 1-10
}}'''
        
        else:
            # Default login classification
            return f'''Classify this UI element from a login/authentication interface.

{context_info}

Classify as one of:
- username_field: for username, email, user ID inputs
- password_field: for password inputs
- confirm_password: for password confirmation fields
- login_button: for sign in/login buttons
- register_button: for sign up/register buttons  
- submit_button: for general form submission
- checkbox: for remember me, terms agreement
- link: for forgot password, register links
- other: for unrelated elements

Response format:
{{
  "classification": "username_field|password_field|login_button|other",
  "confidence": 0.1-1.0,
  "reasoning": "brief explanation of classification decision",
  "visual_evidence": ["text_visible", "styling_clues", "position_indicators"],
  "interaction_priority": 1-10
}}'''
    
    def _build_action_planning_prompt(self, task_type: str, elements_summary: List[Dict], interactive_elements: List[Dict]) -> str:
        """构建行动规划提示词"""
        
        # 任务特定的指引
        if "search" in task_type:
            instruction = """
目标：完成搜索操作
需要识别：
1. 搜索输入框
2. 搜索按钮（可选，通常可以按回车）
操作顺序：点击搜索框 → 输入搜索内容 → 点击搜索按钮或按回车
"""
        elif "content" in task_type:
            instruction = """
目标：识别和提取页面内容
需要识别：
1. 主要内容区域
2. 标题和正文
3. 相关链接
4. 导航元素
"""
        elif "navigation" in task_type:
            instruction = """
目标：识别页面导航结构
需要识别：
1. 主导航菜单
2. 子菜单项
3. 面包屑导航
4. 页脚链接
"""
        else:
            instruction = """
目标：完成登录操作
需要识别：
1. 用户名/邮箱输入框
2. 密码输入框  
3. 登录/提交按钮
操作顺序：点击用户名框 → 输入用户名 → 点击密码框 → 输入密码 → 点击登录按钮
"""
        
        # 构建元素列表
        elements_text = "可用的UI元素：\n"
        for i, elem in enumerate(elements_summary):
            interactivity_mark = "🔴" if elem['interactivity'] else "⚪"
            elements_text += f"{interactivity_mark} 元素{elem['id']}: {elem['type']} - \"{elem['content'][:50]}\" - 中心点{elem['center']}\n"
        
        interactive_text = f"\n交互元素（共{len(interactive_elements)}个）：\n"
        for elem in interactive_elements:
            interactive_text += f"🔴 元素{elem['id']}: \"{elem['content'][:30]}\" - 中心点{elem['center']}\n"
        
        return f"""你是一个UI自动化专家。基于以下信息，为网页操作制定精确的行动计划。

{instruction}

{elements_text}
{interactive_text}

请分析这个页面并提供操作计划：

1. 确定页面类型和当前状态
2. 识别完成目标所需的关键元素
3. 提供精确的操作步骤（包括点击坐标）

返回JSON格式：
{{
  "page_analysis": {{
    "page_type": "登录页面|搜索页面|内容页面|导航页面",
    "confidence": 0.1-1.0,
    "key_elements_found": ["element_type1", "element_type2"]
  }},
  "action_plan": [
    {{
      "step": 1,
      "action": "click|type|scroll",
      "target_element_id": 元素ID,
      "target_coordinates": [x, y],
      "description": "操作描述",
      "input_text": "要输入的文本（如果是type操作）"
    }}
  ],
  "success_probability": 0.1-1.0,
  "notes": "额外说明"
}}

只基于实际看到的元素制定计划，确保坐标准确。"""
    
    def _parse_action_plan(self, text: str) -> Dict[str, Any]:
        """解析行动计划"""
        try:
            # 尝试解析JSON
            json_start = text.find('{')
            json_end = text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_text = text[json_start:json_end]
                return json.loads(json_text)
        except:
            pass
        
        # 失败时返回基础计划
        return {
            "page_analysis": {
                "page_type": f"{self.task_type}页面",
                "confidence": 0.5,
                "key_elements_found": []
            },
            "action_plan": [],
            "success_probability": 0.3,
            "notes": "解析失败，使用fallback计划"
        }
    
    def _match_actions_to_elements(self, decision: Dict[str, Any], ui_elements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """将决策与实际UI元素匹配"""
        
        action_plan = decision.get("action_plan", [])
        
        # 为每个行动步骤匹配实际元素
        for step in action_plan:
            target_id = step.get("target_element_id")
            
            if target_id is not None:
                # 找到对应的元素
                target_element = None
                for element in ui_elements:
                    if element.get('element_id') == target_id:
                        target_element = element
                        break
                
                if target_element:
                    # 使用实际元素的坐标
                    step["actual_coordinates"] = target_element.get("center")
                    step["actual_bbox"] = target_element.get("pixel_bbox")
                    step["element_content"] = target_element.get("content")
                    step["element_type"] = target_element.get("type")
                    step["element_size"] = target_element.get("size")
        
        return {
            "page_analysis": decision.get("page_analysis", {}),
            "action_plan": action_plan,
            "success_probability": decision.get("success_probability", 0.5),
            "notes": decision.get("notes", ""),
            "total_steps": len(action_plan),
            "interactive_elements_available": len([e for e in ui_elements if e.get('interactivity')])
        }
    
    def _create_fallback_elements(self, image_path: str, intelligence: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create fallback elements based on typical layouts"""
        img = Image.open(image_path)
        img_width, img_height = img.size
        
        layout = intelligence.get('layout_pattern', 'vertical')
        
        if layout == 'vertical':
            form_center_x = img_width // 2
            form_start_y = img_height // 3
            
            return [
                {
                    'id': 'fallback_username',
                    'bbox': [form_center_x - 150, form_start_y, form_center_x + 150, form_start_y + 40],
                    'center': [form_center_x, form_start_y + 20],
                    'size': [300, 40],
                    'confidence': 0.6,
                    'type': 'input'
                },
                {
                    'id': 'fallback_password',
                    'bbox': [form_center_x - 150, form_start_y + 70, form_center_x + 150, form_start_y + 110],
                    'center': [form_center_x, form_start_y + 90],
                    'size': [300, 40],
                    'confidence': 0.6,
                    'type': 'input'
                },
                {
                    'id': 'fallback_button',
                    'bbox': [form_center_x - 75, form_start_y + 140, form_center_x + 75, form_start_y + 180],
                    'center': [form_center_x, form_start_y + 160],
                    'size': [150, 40],
                    'confidence': 0.5,
                    'type': 'button'
                }
            ]
        else:
            return [
                {
                    'id': 'fallback_form',
                    'bbox': [img_width//4, img_height//3, 3*img_width//4, 2*img_height//3],
                    'center': [img_width//2, img_height//2],
                    'size': [img_width//2, img_height//3],
                    'confidence': 0.4,
                    'type': 'form'
                }
            ]
    
    async def _fallback_element_detection(self, service: Any, image_path: str, intelligence: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fallback element detection using generic methods"""
        try:
            # Try generic object detection
            result = await service.detect_objects(image_path, confidence_threshold=0.5)
            objects = result.get("objects", [])
            
            # Convert to standard format
            elements = []
            for i, obj in enumerate(objects):
                coords = obj.get("coordinates", {})
                if all(k in coords for k in ['x', 'y', 'width', 'height']):
                    # Convert percentage to pixels
                    img = Image.open(image_path)
                    img_width, img_height = img.size
                    
                    x = int(coords['x'] * img_width / 100)
                    y = int(coords['y'] * img_height / 100)
                    w = int(coords['width'] * img_width / 100)
                    h = int(coords['height'] * img_height / 100)
                    
                    element = {
                        'id': f'fallback_{i}',
                        'bbox': [x, y, x + w, y + h],
                        'center': [x + w//2, y + h//2],
                        'size': [w, h],
                        'confidence': obj.get('confidence', 0.7),
                        'type': 'detected'
                    }
                    elements.append(element)
            
            return elements
            
        except Exception:
            # Ultimate fallback
            return self._create_fallback_elements(image_path, intelligence)