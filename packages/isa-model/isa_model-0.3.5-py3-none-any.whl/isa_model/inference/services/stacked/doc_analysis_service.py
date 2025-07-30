"""
Document Analysis Stacked Service

A comprehensive document analysis service that combines multiple vision models
to process complex documents through a five-step pipeline:

1. VLM Document Classification (GPT-4V/Claude)
2. Table Transformer Detection
3. Table Transformer Structure Recognition
4. PaddleOCR Text Extraction
5. VLM Intelligent Matching

The sixth step (predefined structure mapping) is handled by specific business services
that have their own templates and schemas for different use cases.

This service orchestrates OpenAI Vision Service and ISA Vision Service
using the BaseStackedService framework.
"""

import json
import logging
from typing import Dict, Any, List, Union, Optional, BinaryIO
from datetime import datetime

from isa_model.inference.services.stacked.base_stacked_service import (
    BaseStackedService, LayerConfig, LayerType, LayerResult
)

logger = logging.getLogger(__name__)

class DocAnalysisStackedService(BaseStackedService):
    """Stacked Document Analysis Service using multiple vision models (5-step pipeline)"""
    
    def __init__(self, ai_factory, service_name: str = "doc-analysis-stacked"):
        super().__init__(ai_factory, service_name)
        
        # Configure the 5-step pipeline layers
        self._configure_pipeline_layers()
        
        logger.info(f"Initialized DocAnalysisStackedService with 5-step pipeline")
    
    def _configure_pipeline_layers(self):
        """Configure the 5-step document analysis pipeline"""
        
        # Step 1: VLM Document Classification
        self.add_layer(LayerConfig(
            name="document_classification",
            layer_type=LayerType.CLASSIFICATION,
            service_type="vision",
            model_name="gpt-4.1-nano",  # Use OpenAI Vision Service
            parameters={
                "task": "classification",
                "max_tokens": 1500
            },
            depends_on=[],
            timeout=30.0,
            retry_count=2,
            fallback_enabled=True
        ))
        
        # Step 2: Table Detection
        self.add_layer(LayerConfig(
            name="table_detection",
            layer_type=LayerType.DETECTION,
            service_type="vision", 
            model_name="isa-vision-doc",  # Use ISA Vision Service
            parameters={
                "task": "analyze_document",
                "confidence_threshold": 0.5
            },
            depends_on=["document_classification"],
            timeout=45.0,
            retry_count=1,
            fallback_enabled=True
        ))
        
        # Step 3: Table Structure Recognition
        self.add_layer(LayerConfig(
            name="table_structure",
            layer_type=LayerType.DETECTION,
            service_type="vision",
            model_name="isa-vision-doc",
            parameters={
                "task": "table_structure_recognition"
            },
            depends_on=["table_detection"],
            timeout=30.0,
            retry_count=1,
            fallback_enabled=True
        ))
        
        # Step 4: OCR Text Extraction
        self.add_layer(LayerConfig(
            name="ocr_extraction",
            layer_type=LayerType.DETECTION,
            service_type="vision",
            model_name="isa-vision-doc",
            parameters={
                "task": "extract_text"
            },
            depends_on=["table_structure"],
            timeout=60.0,
            retry_count=2,
            fallback_enabled=False  # OCR is critical
        ))
        
        # Step 5: Intelligent Matching
        self.add_layer(LayerConfig(
            name="intelligent_matching",
            layer_type=LayerType.INTELLIGENCE,
            service_type="vision",
            model_name="gpt-4.1-nano",
            parameters={
                "task": "intelligent_matching",
                "max_tokens": 2000
            },
            depends_on=["document_classification", "ocr_extraction"],
            timeout=45.0,
            retry_count=2,
            fallback_enabled=True
        ))
    
    async def execute_layer_logic(self, layer: LayerConfig, service: Any, context: Dict[str, Any]) -> Any:
        """Execute the specific logic for each layer"""
        
        input_data = context.get("input", {})
        results = context.get("results", {})
        
        if layer.name == "document_classification":
            return await self._execute_document_classification(service, input_data, layer.parameters)
            
        elif layer.name == "table_detection":
            return await self._execute_table_detection(service, input_data, layer.parameters)
            
        elif layer.name == "table_structure":
            table_regions = results.get("table_detection", {}).data.get("table_regions", [])
            return await self._execute_table_structure(service, input_data, table_regions, layer.parameters)
            
        elif layer.name == "ocr_extraction":
            table_regions = results.get("table_detection", {}).data.get("table_regions", [])
            return await self._execute_ocr_extraction(service, input_data, table_regions, layer.parameters)
            
        elif layer.name == "intelligent_matching":
            classification_data = results.get("document_classification", {}).data
            ocr_data = results.get("ocr_extraction", {}).data
            return await self._execute_intelligent_matching(service, classification_data, ocr_data, layer.parameters)
            
        else:
            raise ValueError(f"Unknown layer: {layer.name}")
    
    async def _execute_document_classification(self, service, input_data: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Step 1: VLM Document Classification"""
        
        images = input_data.get("images", [])
        if not images:
            raise ValueError("No images provided for classification")
        
        classification_prompt = """
        请分析这些文档页面，识别：
        1. 文档类型（报关单、发票、合同、装箱单等）
        2. 公司信息（发货人、收货人）
        3. 业务类型（出口、进口、跨境电商等）
        4. 页面关系（是否属于同一份文档）
        
        请以JSON格式返回结果：
        {
            "document_classification": {
                "document_type": "文档类型",
                "business_type": "业务类型",
                "pages": [
                    {
                        "page_id": 1,
                        "page_type": "页面类型",
                        "company": "公司名称",
                        "confidence": 0.95
                    }
                ]
            }
        }
        """
        
        # Analyze each page
        page_results = []
        for i, image in enumerate(images):
            result = await service.analyze_image(
                image,
                classification_prompt,
                max_tokens=params.get("max_tokens", 1500)
            )
            
            page_results.append({
                "page_id": i + 1,
                "analysis": result.get("text", ""),
                "confidence": result.get("confidence", 0.8)
            })
        
        # Combine results for multi-page analysis if multiple pages
        if len(images) > 1:
            combined_prompt = f"""
            基于以下各页面的分析结果，提供整体文档分类：
            
            {json.dumps(page_results, ensure_ascii=False, indent=2)}
            
            请返回最终的分类结果，格式如前面所示。
            """
            
            final_result = await service.analyze_image(
                images[0],
                combined_prompt,
                max_tokens=1000
            )
        else:
            final_result = page_results[0] if page_results else {"analysis": ""}
        
        # Parse the classification result
        classification = self._parse_json_response(final_result.get("text", "{}"))
        
        return {
            "success": True,
            "step": "document_classification",
            "classification": classification,
            "page_count": len(images),
            "processing_time": datetime.now().isoformat(),
            "metadata": {
                "model": "gpt-4.1-nano",
                "service": "vlm_classification"
            }
        }
    
    async def _execute_table_detection(self, service, input_data: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Step 2: Table Transformer Detection"""
        
        image = input_data.get("image") or (input_data.get("images", [None])[0])
        if not image:
            raise ValueError("No image provided for table detection")
        
        # Use ISA Vision Service for table detection
        detection_result = await service.invoke(
            image,
            task="analyze_document"
        )
        
        if detection_result.get("success"):
            tables = detection_result.get("table_regions", [])
            
            return {
                "success": True,
                "step": "table_detection", 
                "table_count": len(tables),
                "table_regions": tables,
                "processing_time": datetime.now().isoformat(),
                "metadata": {
                    "model": "table-transformer-detection",
                    "service": "isa_vision"
                }
            }
        else:
            raise Exception(detection_result.get("error", "Table detection failed"))
    
    async def _execute_table_structure(self, service, input_data: Dict[str, Any], table_regions: List[Dict[str, Any]], params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Step 3: Table Transformer Structure Recognition"""
        
        structure_results = []
        
        for i, table_region in enumerate(table_regions):
            # Process each table region for structure recognition
            structure_result = {
                "table_id": i + 1,
                "bbox": table_region.get("bbox", []),
                "rows": table_region.get("rows", 0),
                "columns": table_region.get("columns", 0),
                "cells": table_region.get("cells", []),
                "confidence": table_region.get("confidence", 0.8)
            }
            structure_results.append(structure_result)
        
        return {
            "success": True,
            "step": "table_structure_recognition",
            "structures": structure_results,
            "processing_time": datetime.now().isoformat(),
            "metadata": {
                "model": "table-transformer-structure",
                "service": "isa_vision"
            }
        }
    
    async def _execute_ocr_extraction(self, service, input_data: Dict[str, Any], table_regions: List[Dict[str, Any]], params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Step 4: PaddleOCR Text Extraction"""
        
        image = input_data.get("image") or (input_data.get("images", [None])[0])
        if not image:
            raise ValueError("No image provided for OCR extraction")
        
        # Use ISA Vision Service for OCR
        ocr_result = await service.extract_text(image)
        
        if ocr_result.get("success"):
            extracted_text = ocr_result.get("text", "")
            bounding_boxes = ocr_result.get("bounding_boxes", [])
            
            # If table regions are provided, filter OCR results to table areas
            if table_regions:
                table_ocr_data = []
                for table in table_regions:
                    table_text = self._extract_text_from_region(
                        extracted_text,
                        bounding_boxes,
                        table.get("bbox", [])
                    )
                    table_ocr_data.append({
                        "table_id": table.get("table_id", 0),
                        "text": table_text,
                        "bbox": table.get("bbox", [])
                    })
                
                return {
                    "success": True,
                    "step": "ocr_extraction",
                    "full_text": extracted_text,
                    "table_ocr_data": table_ocr_data,
                    "confidence": ocr_result.get("confidence", 0.8),
                    "processing_time": datetime.now().isoformat(),
                    "metadata": {
                        "model": "PaddleOCR",
                        "service": "isa_vision"
                    }
                }
            else:
                return {
                    "success": True,
                    "step": "ocr_extraction",
                    "full_text": extracted_text,
                    "confidence": ocr_result.get("confidence", 0.8),
                    "processing_time": datetime.now().isoformat(),
                    "metadata": {
                        "model": "PaddleOCR",
                        "service": "isa_vision"
                    }
                }
        else:
            raise Exception(ocr_result.get("error", "OCR extraction failed"))
    
    async def _execute_intelligent_matching(self, service, classification_data: Dict[str, Any], ocr_data: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Step 5: VLM Intelligent Matching"""
        
        matching_prompt = f"""
        基于识别到的表格数据和文档上下文，请提取并整理以下信息：
        
        文档分类信息：
        {json.dumps(classification_data, ensure_ascii=False, indent=2)}
        
        OCR提取的数据：
        {json.dumps(ocr_data, ensure_ascii=False, indent=2)}
        
        请执行以下任务：
        1. 将表格数据转换为结构化格式
        2. 识别关键字段的含义和关系
        3. 处理跨表格的数据关联
        4. 识别并纠正OCR错误
        5. 提供标准化的结构化数据，供业务服务进行模板映射
        
        返回JSON格式：
        {{
            "structured_data": {{
                "basic_info": {{
                    "document_type": "文档类型",
                    "company_info": "公司信息",
                    "date": "日期",
                    "document_number": "文档编号"
                }},
                "items": [
                    {{
                        "item_name": "商品名称",
                        "quantity": "数量",
                        "unit_price": "单价",
                        "total_price": "总价"
                    }}
                ],
                "financial_summary": {{
                    "subtotal": "小计",
                    "tax": "税费",
                    "total": "总计"
                }},
                "additional_fields": {{
                    "field_name": "字段值"
                }}
            }},
            "field_confidence": {{
                "basic_info": 0.95,
                "items": 0.90,
                "financial_summary": 0.85
            }},
            "corrections_made": [
                "纠正了OCR错误示例"
            ],
            "ready_for_mapping": true
        }}
        """
        
        result = await service.analyze_image(
            None,  # Text-only analysis
            matching_prompt,
            max_tokens=params.get("max_tokens", 2000)
        )
        
        structured_data = self._parse_json_response(result.get("text", "{}"))
        
        return {
            "success": True,
            "step": "intelligent_matching",
            "structured_data": structured_data,
            "ready_for_business_mapping": True,
            "processing_time": datetime.now().isoformat(),
            "metadata": {
                "model": "gpt-4.1-nano",
                "service": "vlm_matching",
                "note": "Ready for business service template mapping"
            }
        }
    
    def generate_final_output(self, results: Dict[str, LayerResult]) -> Dict[str, Any]:
        """Generate final output from all layer results"""
        
        # Check if all critical steps succeeded
        critical_steps = ["document_classification", "ocr_extraction", "intelligent_matching"]
        success = all(
            step in results and results[step].success 
            for step in critical_steps
        )
        
        if success:
            # Get the final structured data from intelligent matching
            final_data = results["intelligent_matching"].data.get("structured_data", {})
            
            return {
                "success": True,
                "pipeline": "five_step_document_analysis",
                "final_structured_data": final_data,
                "ready_for_business_mapping": True,
                "classification": results.get("document_classification", {}).data.get("classification", {}),
                "table_info": {
                    "table_count": results.get("table_detection", {}).data.get("table_count", 0),
                    "table_regions": results.get("table_detection", {}).data.get("table_regions", [])
                },
                "ocr_info": {
                    "full_text": results.get("ocr_extraction", {}).data.get("full_text", ""),
                    "confidence": results.get("ocr_extraction", {}).data.get("confidence", 0)
                },
                "metadata": {
                    "service": "doc_analysis_stacked",
                    "pipeline_version": "5_step",
                    "processing_complete": True
                }
            }
        else:
            # Return error information
            failed_steps = [
                step for step in critical_steps 
                if step not in results or not results[step].success
            ]
            
            return {
                "success": False,
                "pipeline": "five_step_document_analysis",
                "error": f"Critical steps failed: {failed_steps}",
                "failed_steps": failed_steps,
                "partial_results": {
                    name: result.data for name, result in results.items() 
                    if result.success
                },
                "metadata": {
                    "service": "doc_analysis_stacked",
                    "pipeline_version": "5_step",
                    "processing_complete": False
                }
            }
    
    async def execute_fallback(self, layer: LayerConfig, context: Dict[str, Any], error: str) -> Optional[Any]:
        """Execute fallback logic for failed layers"""
        
        if layer.name == "table_detection":
            # Fallback: Continue without table regions
            logger.warning(f"Table detection failed: {error}. Continuing without table regions.")
            return {
                "success": True,
                "step": "table_detection",
                "table_count": 0,
                "table_regions": [],
                "fallback": True,
                "processing_time": datetime.now().isoformat(),
                "metadata": {
                    "model": "fallback",
                    "service": "fallback",
                    "error": error
                }
            }
        
        elif layer.name == "table_structure":
            # Fallback: Return empty structure
            logger.warning(f"Table structure recognition failed: {error}. Using empty structure.")
            return {
                "success": True,
                "step": "table_structure_recognition",
                "structures": [],
                "fallback": True,
                "processing_time": datetime.now().isoformat(),
                "metadata": {
                    "model": "fallback",
                    "service": "fallback",
                    "error": error
                }
            }
        
        elif layer.name == "document_classification":
            # Fallback: Use generic classification
            logger.warning(f"Document classification failed: {error}. Using generic classification.")
            return {
                "success": True,
                "step": "document_classification",
                "classification": {
                    "document_classification": {
                        "document_type": "unknown_document",
                        "business_type": "unknown",
                        "confidence": 0.1,
                        "pages": []
                    }
                },
                "fallback": True,
                "processing_time": datetime.now().isoformat(),
                "metadata": {
                    "model": "fallback",
                    "service": "fallback",
                    "error": error
                }
            }
        
        elif layer.name == "intelligent_matching":
            # Fallback: Use basic structured format
            logger.warning(f"Intelligent matching failed: {error}. Using basic structure.")
            return {
                "success": True,
                "step": "intelligent_matching",
                "structured_data": {
                    "structured_data": {
                        "basic_info": {},
                        "items": [],
                        "financial_summary": {},
                        "additional_fields": {}
                    },
                    "field_confidence": {},
                    "corrections_made": [],
                    "ready_for_mapping": False
                },
                "fallback": True,
                "processing_time": datetime.now().isoformat(),
                "metadata": {
                    "model": "fallback",
                    "service": "fallback",
                    "error": error
                }
            }
        
        return None
    
    # Helper methods
    
    def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """Parse JSON response from VLM"""
        try:
            # Try to find JSON in the response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                return json.loads(json_str)
            else:
                # Fallback to empty dict
                return {}
                
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse JSON from response: {response_text[:200]}...")
            return {}
    
    def _extract_text_from_region(
        self, 
        full_text: str, 
        bounding_boxes: List[Dict], 
        region_bbox: List[int]
    ) -> str:
        """Extract text that falls within a specific region"""
        # This is a simplified implementation
        # In practice, you would need to check if bounding boxes overlap with region
        return full_text  # For now, return full text
    
    # Convenience methods for direct usage
    
    async def analyze_document(self, image: Union[str, BinaryIO], images: Optional[List[Union[str, BinaryIO]]] = None) -> Dict[str, Any]:
        """Convenience method for complete document analysis"""
        
        if images is None:
            images = [image] if image else []
        
        input_data = {
            "image": image,
            "images": images
        }
        
        return await self.invoke(input_data)
    
    async def classify_document_only(self, images: List[Union[str, BinaryIO]]) -> Dict[str, Any]:
        """Convenience method for document classification only"""
        
        # Temporarily configure only classification layer
        original_layers = self.layers.copy()
        self.layers = [layer for layer in self.layers if layer.name == "document_classification"]
        
        try:
            input_data = {"images": images}
            result = await self.invoke(input_data)
            return result
        finally:
            # Restore original layers
            self.layers = original_layers
    
    async def extract_text_only(self, image: Union[str, BinaryIO]) -> Dict[str, Any]:
        """Convenience method for OCR extraction only"""
        
        # Temporarily configure only OCR layer
        original_layers = self.layers.copy()
        self.layers = [layer for layer in self.layers if layer.name == "ocr_extraction"]
        
        try:
            input_data = {"image": image}
            result = await self.invoke(input_data)
            return result
        finally:
            # Restore original layers
            self.layers = original_layers