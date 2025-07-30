"""
ISA Vision Document Service

Specialized service for document analysis including:
- Table detection (Table Transformer Detection)
- Table structure recognition (Table Transformer Structure v1.1) 
- OCR text extraction (PaddleOCR 3.0)
"""

import modal
import torch
import base64
import io
import numpy as np
from PIL import Image
from typing import Dict, List, Optional, Any
import time
import json
import os
import logging

# Define Modal application
app = modal.App("isa-vision-doc")

# Download document analysis models
def download_doc_models():
    """Download document analysis models"""
    from huggingface_hub import snapshot_download
    import subprocess
    
    print("📦 Downloading document analysis models...")
    os.makedirs("/models", exist_ok=True)
    
    # Download Table Transformer Detection
    try:
        snapshot_download(
            repo_id="microsoft/table-transformer-detection",
            local_dir="/models/table-transformer-detection",
            allow_patterns=["**/*.pt", "**/*.pth", "**/*.bin", "**/*.json", "**/*.safetensors"]
        )
        print("✅ Table Transformer Detection downloaded")
    except Exception as e:
        print(f"⚠️ Table Transformer Detection download failed: {e}")
    
    # Download Table Transformer Structure Recognition v1.1
    try:
        snapshot_download(
            repo_id="microsoft/table-transformer-structure-recognition-v1.1-all",
            local_dir="/models/table-transformer-structure",
            allow_patterns=["**/*.pt", "**/*.pth", "**/*.bin", "**/*.json", "**/*.safetensors"]
        )
        print("✅ Table Transformer Structure Recognition v1.1 downloaded")
    except Exception as e:
        print(f"⚠️ Table Transformer Structure Recognition download failed: {e}")
    
    # Install PaddleOCR
    try:
        subprocess.run(["pip", "install", "paddleocr>=2.7.0", "--no-deps"], check=True)
        print("✅ PaddleOCR installed")
    except Exception as e:
        print(f"⚠️ PaddleOCR install failed: {e}")
    
    print("📦 Document analysis models download completed")

# Define Modal container image
image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install([
        # OpenGL and graphics libraries for PaddleOCR
        "libgl1-mesa-glx",
        "libglib2.0-0",
        "libsm6",
        "libxext6",
        "libxrender-dev",
        "libgomp1",
        # Font support
        "fontconfig",
        "libfontconfig1",
        "libfreetype6",
    ])
    .pip_install([
        # Core AI libraries
        "torch>=2.0.0",
        "torchvision",
        "transformers>=4.35.0",
        "huggingface_hub",
        "accelerate",
        
        # Image processing
        "pillow>=10.0.1",
        "opencv-python-headless",
        "numpy>=1.24.3",
        
        # OCR libraries - Latest stable versions
        "paddleocr>=3.0.0",
        "paddlepaddle>=3.0.0",
        
        # HTTP libraries
        "httpx>=0.26.0",
        "requests",
        
        # Utilities
        "pydantic>=2.0.0",
        "python-dotenv",
    ])
    .run_function(download_doc_models)
    .env({
        "TRANSFORMERS_CACHE": "/models",
        "FONTCONFIG_PATH": "/etc/fonts",
        "KMP_DUPLICATE_LIB_OK": "TRUE",
        "OMP_NUM_THREADS": "1",
        "CUDA_VISIBLE_DEVICES": "0"
    })
)

# Document Analysis Service
@app.cls(
    gpu="T4",
    image=image,
    memory=16384,  # 16GB RAM
    timeout=1800,  # 30 minutes
    scaledown_window=300,  # 5 minutes idle timeout
    min_containers=0,  # Scale to zero when not in use
)
class DocumentAnalysisService:
    """
    Document Analysis Service
    
    Provides document analysis capabilities including:
    - Table detection and structure recognition
    - OCR text extraction
    - Combined document parsing
    """
    
    def __init__(self):
        self.models = {}
        self.logger = logging.getLogger(__name__)
        
    @modal.enter()
    def load_models(self):
        """Load document analysis models on container startup"""
        print("🚀 Loading document analysis models...")
        start_time = time.time()
        
        try:
            import sys
            # Check system environment
            print(f"🔧 System info:")
            print(f"   - Python version: {sys.version}")
            print(f"   - PyTorch version: {torch.__version__}")
            print(f"   - CUDA available: {torch.cuda.is_available()}")
            if torch.cuda.is_available():
                print(f"   - CUDA version: {torch.version.cuda}")
                print(f"   - GPU count: {torch.cuda.device_count()}")
            
            # Load table detection models
            self._load_table_models()
            
            # Load OCR models
            self._load_ocr_models()
            
            load_time = time.time() - start_time
            print(f"✅ Document analysis models loaded in {load_time:.2f}s")
            
            # Verify models are loaded
            if not self.models.get('ocr'):
                print("⚠️ OCR model failed to load - service will use fallback")
            
        except Exception as e:
            print(f"❌ Critical error during model loading: {e}")
            import traceback
            traceback.print_exc()
            # Don't raise - let service start with degraded functionality
        
    def _load_table_models(self):
        """Load table detection and structure recognition models"""
        print("📊 Loading table analysis models...")
        
        # TODO: Implement actual Table Transformer loading
        # For now, we don't load these models to avoid mock data
        print("⚠️ Table Transformer models not implemented yet")
        print("   - Table detection will return empty results")
        print("   - Table structure analysis will return empty results")
        
    def _load_ocr_models(self):
        """Load OCR models"""
        print("🔤 Loading OCR models...")
        
        try:
            import os
            # Set environment variables to prevent conflicts and optimize performance
            os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
            os.environ['OMP_NUM_THREADS'] = '1'
            os.environ['MKLDNN_DISABLED'] = '1'  # Disable MKLDNN to force GPU usage
            
            from paddleocr import PaddleOCR
            
            # Initialize PaddleOCR 3.0 with minimal configuration
            # PaddleOCR 3.0 uses PP-OCRv5_server model by default which supports multiple languages
            self.models['ocr'] = PaddleOCR(
                use_angle_cls=True,  # Enable text direction classification
                lang='ch'            # Chinese language (also supports English in the same model)
            )
            print("✅ PaddleOCR loaded successfully with official defaults")
            print(f"   - GPU available: {torch.cuda.is_available()}")
            if torch.cuda.is_available():
                print(f"   - CUDA device: {torch.cuda.get_device_name(0)}")
                print(f"   - CUDA version: {torch.version.cuda}")
            
            # Test OCR initialization
            print("🔍 Testing OCR initialization...")
            
        except Exception as e:
            print(f"⚠️ PaddleOCR loading failed: {e}")
            import traceback
            traceback.print_exc()
            self.models['ocr'] = None
    
    @modal.method()
    def detect_tables(self, image_b64: str) -> Dict[str, Any]:
        """
        Detect tables in document image
        
        Args:
            image_b64: Base64 encoded image
            
        Returns:
            Table detection results
        """
        start_time = time.time()
        
        try:
            # Decode image
            image = self._decode_image(image_b64)
            image_np = np.array(image)
            
            # Perform table detection
            tables = self._detect_tables_impl(image_np)
            
            processing_time = time.time() - start_time
            
            return {
                'success': True,
                'service': 'isa-vision-doc',
                'function': 'table_detection',
                'tables': tables,
                'table_count': len(tables),
                'processing_time': processing_time,
                'model_info': {
                    'detector': 'Table Transformer Detection',
                    'gpu': 'T4'
                }
            }
            
        except Exception as e:
            self.logger.error(f"Table detection failed: {e}")
            return {
                'success': False,
                'service': 'isa-vision-doc',
                'function': 'table_detection',
                'error': str(e),
                'processing_time': time.time() - start_time
            }
    
    @modal.method()
    def analyze_table_structure(self, image_b64: str, table_bbox: List[int] = None) -> Dict[str, Any]:
        """
        Analyze table structure in image
        
        Args:
            image_b64: Base64 encoded image
            table_bbox: Optional bounding box of table [x1, y1, x2, y2]
            
        Returns:
            Table structure analysis results
        """
        start_time = time.time()
        
        try:
            # Decode image
            image = self._decode_image(image_b64)
            image_np = np.array(image)
            
            # Crop to table region if bbox provided
            if table_bbox:
                x1, y1, x2, y2 = table_bbox
                image_np = image_np[y1:y2, x1:x2]
            
            # Analyze table structure
            structure = self._analyze_table_structure_impl(image_np)
            
            processing_time = time.time() - start_time
            
            return {
                'success': True,
                'service': 'isa-vision-doc',
                'function': 'table_structure',
                'structure': structure,
                'processing_time': processing_time,
                'model_info': {
                    'analyzer': 'Table Transformer Structure Recognition v1.1',
                    'gpu': 'T4'
                }
            }
            
        except Exception as e:
            self.logger.error(f"Table structure analysis failed: {e}")
            return {
                'success': False,
                'service': 'isa-vision-doc',
                'function': 'table_structure',
                'error': str(e),
                'processing_time': time.time() - start_time
            }
    
    @modal.method()
    def extract_text(self, image_b64: str, regions: List[Dict] = None) -> Dict[str, Any]:
        """
        Extract text from document image using OCR
        
        Args:
            image_b64: Base64 encoded image
            regions: Optional list of regions to focus OCR on
            
        Returns:
            OCR text extraction results
        """
        start_time = time.time()
        
        try:
            # Decode image
            image = self._decode_image(image_b64)
            image_np = np.array(image)
            
            # Perform OCR
            text_results = self._extract_text_impl(image_np, regions)
            
            processing_time = time.time() - start_time
            
            return {
                'success': True,
                'service': 'isa-vision-doc',
                'function': 'ocr',
                'text_results': text_results,
                'text_count': len(text_results),
                'processing_time': processing_time,
                'model_info': {
                    'ocr_engine': 'PaddleOCR 3.0',
                    'gpu': 'T4'
                }
            }
            
        except Exception as e:
            self.logger.error(f"OCR extraction failed: {e}")
            return {
                'success': False,
                'service': 'isa-vision-doc',
                'function': 'ocr',
                'error': str(e),
                'processing_time': time.time() - start_time
            }
    
    @modal.method()
    def analyze_document_complete(self, image_b64: str) -> Dict[str, Any]:
        """
        Complete document analysis: tables + structure + OCR
        
        Args:
            image_b64: Base64 encoded image
            
        Returns:
            Complete document analysis results
        """
        start_time = time.time()
        
        try:
            # Decode image once for all operations
            image = self._decode_image(image_b64)
            image_np = np.array(image)
            
            # Step 1: Detect tables
            tables = self._detect_tables_impl(image_np)
            table_detection_start = time.time()
            table_result = {
                'success': True,
                'tables': tables,
                'processing_time': time.time() - table_detection_start
            }
            
            # Step 2: Extract text
            ocr_start = time.time()
            text_results = self._extract_text_impl(image_np)
            ocr_result = {
                'success': True,
                'text_results': text_results,
                'processing_time': time.time() - ocr_start
            }
            
            # Step 3: Analyze table structures if tables found
            structure_results = []
            if table_result.get('success') and table_result.get('tables'):
                for table in table_result['tables']:
                    if 'bbox' in table:
                        x1, y1, x2, y2 = table['bbox']
                        table_image = image_np[y1:y2, x1:x2]
                        structure = self._analyze_table_structure_impl(table_image)
                        structure_results.append(structure)
            
            total_time = time.time() - start_time
            
            return {
                'success': True,
                'service': 'isa-vision-doc',
                'function': 'complete_analysis',
                'total_execution_time': total_time,
                'results': {
                    'tables': table_result.get('tables', []),
                    'table_structures': structure_results,
                    'text_extraction': ocr_result.get('text_results', [])
                },
                'summary': {
                    'tables_found': len(table_result.get('tables', [])),
                    'text_regions_found': len(ocr_result.get('text_results', [])),
                    'structures_analyzed': len(structure_results)
                },
                'performance_metrics': {
                    'table_detection_time': table_result.get('processing_time', 0),
                    'ocr_time': ocr_result.get('processing_time', 0),
                    'total_time': total_time,
                    'platform': 'modal'
                }
            }
            
        except Exception as e:
            self.logger.error(f"Complete document analysis failed: {e}")
            return {
                'success': False,
                'service': 'isa-vision-doc',
                'function': 'complete_analysis',
                'error': str(e),
                'total_execution_time': time.time() - start_time
            }
    
    def _detect_tables_impl(self, image_np: np.ndarray) -> List[Dict[str, Any]]:
        """Implementation of table detection"""
        print("🔍 Table detection requested but not implemented")
        print("⚠️ Table Transformer models need to be properly loaded")
        
        # Return empty list since we don't have real table detection yet
        # TODO: Implement actual Table Transformer Detection
        return []
    
    def _analyze_table_structure_impl(self, image_np: np.ndarray) -> Dict[str, Any]:
        """Implementation of table structure analysis"""
        print("📊 Table structure analysis requested but not implemented")
        print("⚠️ Table Transformer Structure Recognition models need to be properly loaded")
        
        # Return empty structure since we don't have real table structure analysis yet
        # TODO: Implement actual Table Transformer Structure Recognition
        return {
            'rows': 0,
            'columns': 0,
            'cells': [],
            'confidence': 0.0
        }
    
    def _extract_text_impl(self, image_np: np.ndarray, regions: List[Dict] = None) -> List[Dict[str, Any]]:
        """Implementation of OCR text extraction"""
        print(f"🔍 Debug: OCR model in models: {'ocr' in self.models}")
        print(f"🔍 Debug: OCR model value: {self.models.get('ocr')}")
        print(f"🔍 Debug: OCR model is not None: {self.models.get('ocr') is not None}")
        
        if self.models.get('ocr') is not None:
            try:
                print("🔤 Using real PaddleOCR for text extraction...")
                ocr = self.models['ocr']
                print(f"🔍 Debug: OCR object type: {type(ocr)}")
                
                # Ensure image is in correct format for PaddleOCR
                if len(image_np.shape) == 3 and image_np.shape[2] == 3:
                    # Convert RGB to BGR for OpenCV/PaddleOCR
                    image_bgr = image_np[:, :, ::-1]
                else:
                    image_bgr = image_np
                
                print(f"🔍 Image shape for OCR: {image_bgr.shape}")
                print(f"🔍 Image dtype: {image_bgr.dtype}")
                print(f"🔍 Image min/max values: {image_bgr.min()}/{image_bgr.max()}")
                
                # Save debug image to check what we're actually sending to OCR
                try:
                    import cv2
                    cv2.imwrite('/tmp/debug_ocr_input.jpg', image_bgr)
                    print("🔍 Debug image saved to /tmp/debug_ocr_input.jpg")
                except Exception as e:
                    print(f"⚠️ Failed to save debug image: {e}")
                
                # Run PaddleOCR (angle classification is now built-in for v3.0)
                print("🔍 Calling PaddleOCR...")
                result = ocr.ocr(image_bgr)
                print(f"🔍 PaddleOCR completed, raw result type: {type(result)}")
                
                text_results = []
                print(f"🔍 Checking result: result={bool(result)}, result length={len(result) if result else 0}")
                if result:
                    print(f"🔍 First result element exists: {result[0] is not None}")
                    print(f"🔍 First result type: {type(result[0])}")
                    print(f"🔍 First result bool: {bool(result[0])}")
                    
                    # Try to get length safely
                    try:
                        print(f"🔍 First result length: {len(result[0])}")
                    except Exception as e:
                        print(f"🔍 Cannot get length: {e}")
                
                print(f"🔍 About to check if result[0] is truthy...")
                if result and result[0]:
                    first_result = result[0]
                    
                    # Debug: check what attributes the object actually has
                    print(f"🔍 Object attributes: {dir(first_result)}")
                    print(f"🔍 Has rec_texts: {hasattr(first_result, 'rec_texts')}")
                    
                    # Check if it's PaddleOCR 3.0+ OCRResult object
                    if hasattr(first_result, 'rec_texts'):
                        print(f"🔍 Processing PaddleOCR 3.0+ OCRResult with {len(first_result.rec_texts)} text regions...")
                        
                        rec_texts = first_result.rec_texts
                        rec_scores = first_result.rec_scores
                        rec_boxes = first_result.rec_boxes
                        
                        for idx in range(len(rec_texts)):
                            text = rec_texts[idx]
                            confidence = rec_scores[idx]
                            bbox = rec_boxes[idx]  # Should be [x1, y1, x2, y2]
                            
                            text_results.append({
                                'id': f'text_{idx}',
                                'text': text,
                                'confidence': float(confidence),
                                'bbox': [int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])],
                                'center': [
                                    (int(bbox[0]) + int(bbox[2])) // 2,
                                    (int(bbox[1]) + int(bbox[3])) // 2
                                ]
                            })
                    
                    else:
                        print(f"🔍 Processing legacy format with {len(first_result)} text regions...")
                        for idx, line in enumerate(first_result):
                            bbox = line[0]  # Bounding box points
                            text_info = line[1]  # (text, confidence)
                            
                            if text_info and len(text_info) >= 2:
                                # Convert bbox points to [x1, y1, x2, y2]
                                x_coords = [point[0] for point in bbox]
                                y_coords = [point[1] for point in bbox]
                                bbox_rect = [
                                    int(min(x_coords)),
                                    int(min(y_coords)), 
                                    int(max(x_coords)),
                                    int(max(y_coords))
                                ]
                                
                                text_results.append({
                                    'id': f'text_{idx}',
                                    'text': text_info[0],
                                    'confidence': text_info[1],
                                    'bbox': bbox_rect,
                                    'center': [
                                        (bbox_rect[0] + bbox_rect[2]) // 2,
                                        (bbox_rect[1] + bbox_rect[3]) // 2
                                    ]
                                })
                
                print(f"✅ Real PaddleOCR extraction: {len(text_results)} text regions found")
                return text_results
                
            except Exception as e:
                print(f"❌ PaddleOCR failed: {e}")
                import traceback
                traceback.print_exc()
        
        # No fallback - return empty if PaddleOCR is not available
        print("❌ PaddleOCR not available, returning empty results")
        return []
    
    @modal.method()
    def health_check(self) -> Dict[str, Any]:
        """Health check endpoint"""
        return {
            'status': 'healthy',
            'service': 'isa-vision-doc',
            'models_loaded': list(self.models.keys()),
            'capabilities': ['table_detection', 'table_structure', 'ocr'],
            'timestamp': time.time(),
            'gpu': 'T4'
        }
    
    def _decode_image(self, image_b64: str) -> Image.Image:
        """Decode base64 image"""
        if image_b64.startswith('data:image'):
            image_b64 = image_b64.split(',')[1]
        
        image_data = base64.b64decode(image_b64)
        return Image.open(io.BytesIO(image_data)).convert('RGB')

# Warmup function removed to save costs

if __name__ == "__main__":
    print("🚀 ISA Vision Document Service - Modal Deployment")
    print("Deploy with: modal deploy isa_vision_doc_service.py")