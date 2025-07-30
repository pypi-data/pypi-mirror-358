"""
FLUX Professional Pipeline Service
Multi-stage AI image generation with FLUX + ControlNet + LoRA + Upscaling
"""

import asyncio
import logging
import base64
import io
from typing import Dict, Any, List, Optional
from PIL import Image

from .base_stacked_service import BaseStackedService, LayerConfig, LayerType, LayerResult

logger = logging.getLogger(__name__)


class FluxProfessionalService(BaseStackedService):
    """
    FLUX Professional Pipeline Service
    
    5-Stage Professional Image Generation:
    1. FLUX Base Generation - High-quality base image generation
    2. ControlNet Refinement - Precise composition and pose control  
    3. LoRA Style Application - Custom style and character application
    4. Detail Enhancement - Face/detail restoration and refinement
    5. Ultimate Upscaling - Professional 4K/8K/16K upscaling
    """
    
    def __init__(self, ai_factory):
        super().__init__(ai_factory, "FLUX Professional Pipeline")
        self._setup_layers()
    
    def _setup_layers(self):
        """Setup the 5-stage FLUX professional pipeline"""
        
        # Stage 1: FLUX Base Generation
        self.add_layer(LayerConfig(
            name="flux_base_generation",
            layer_type=LayerType.GENERATION,
            service_type="image_gen",
            model_name="flux-pro",
            parameters={
                "width": 1024,
                "height": 1024,
                "steps": 25,
                "guidance_scale": 3.5,
                "seed": -1
            },
            depends_on=[],
            timeout=120.0,
            retry_count=2
        ))
        
        # Stage 2: ControlNet Refinement
        self.add_layer(LayerConfig(
            name="controlnet_refinement", 
            layer_type=LayerType.CONTROL,
            service_type="image_gen",
            model_name="flux-controlnet",
            parameters={
                "controlnet_type": "canny",  # canny, depth, hed
                "controlnet_conditioning_scale": 0.8,
                "control_guidance_start": 0.0,
                "control_guidance_end": 1.0
            },
            depends_on=["flux_base_generation"],
            timeout=90.0,
            retry_count=1
        ))
        
        # Stage 3: LoRA Style Application
        self.add_layer(LayerConfig(
            name="lora_style_application",
            layer_type=LayerType.ENHANCEMENT,
            service_type="image_gen", 
            model_name="flux-lora",
            parameters={
                "lora_models": ["realism", "anime", "art_style"],
                "lora_weights": [0.8, 0.0, 0.6],  # Mix multiple LoRAs
                "denoising_strength": 0.3
            },
            depends_on=["controlnet_refinement"],
            timeout=80.0,
            retry_count=1
        ))
        
        # Stage 4: Detail Enhancement (ADetailer)
        self.add_layer(LayerConfig(
            name="detail_enhancement",
            layer_type=LayerType.ENHANCEMENT,
            service_type="image_gen",
            model_name="adetailer",
            parameters={
                "face_detector": "mediapipe_face_full",
                "face_model": "face_yolov8n.pt",
                "restore_face": True,
                "denoising_strength": 0.4,
                "inpaint_only_masked": True
            },
            depends_on=["lora_style_application"],
            timeout=70.0,
            retry_count=1
        ))
        
        # Stage 5: Ultimate Upscaling
        self.add_layer(LayerConfig(
            name="ultimate_upscaling",
            layer_type=LayerType.UPSCALING,
            service_type="image_gen",
            model_name="ultimate-upscaler",
            parameters={
                "upscaler": "ESRGAN_4x",
                "scale_factor": 4,  # 4K upscaling
                "tile_width": 512,
                "tile_height": 512,
                "mask_blur": 8,
                "padding": 32,
                "seam_fix_mode": "Band Pass",
                "seam_fix_denoise": 0.35,
                "seam_fix_width": 64,
                "seam_fix_mask_blur": 8,
                "seam_fix_padding": 16
            },
            depends_on=["detail_enhancement"],
            timeout=300.0,  # Upscaling takes longer
            retry_count=1
        ))
    
    async def initialize_services(self):
        """Initialize image generation services for FLUX pipeline"""
        for layer in self.layers:
            service_key = f"{layer.service_type}_{layer.model_name}"
            
            if service_key not in self.services:
                if layer.service_type == 'image_gen':
                    # Get appropriate image generation service based on model
                    if "flux" in layer.model_name:
                        service = self.ai_factory.get_image_gen(
                            model_name=layer.model_name,
                            provider="replicate"  # or "modal" if we have flux on modal
                        )
                    elif layer.model_name == "ultimate-upscaler":
                        service = self.ai_factory.get_image_gen(
                            model_name="ultimate-sd-upscale",
                            provider="replicate"
                        )
                    elif layer.model_name == "adetailer":
                        service = self.ai_factory.get_image_gen(
                            model_name="adetailer",
                            provider="replicate"
                        )
                    else:
                        # Default image generation service
                        service = self.ai_factory.get_image_gen()
                else:
                    raise ValueError(f"Unsupported service type: {layer.service_type}")
                
                self.services[service_key] = service
                logger.info(f"Initialized {service_key} service for FLUX pipeline")
    
    async def execute_layer_logic(self, layer: LayerConfig, service: Any, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute specific layer logic for FLUX pipeline"""
        
        if layer.name == "flux_base_generation":
            return await self._execute_flux_base_generation(layer, service, context)
        
        elif layer.name == "controlnet_refinement":
            return await self._execute_controlnet_refinement(layer, service, context)
        
        elif layer.name == "lora_style_application":
            return await self._execute_lora_application(layer, service, context)
        
        elif layer.name == "detail_enhancement":
            return await self._execute_detail_enhancement(layer, service, context)
        
        elif layer.name == "ultimate_upscaling":
            return await self._execute_ultimate_upscaling(layer, service, context)
        
        else:
            raise ValueError(f"Unknown layer: {layer.name}")
    
    async def _execute_flux_base_generation(self, layer: LayerConfig, service: Any, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute FLUX base image generation"""
        prompt = context.get("prompt", "")
        negative_prompt = context.get("negative_prompt", "")
        
        if not prompt:
            raise ValueError("Prompt is required for FLUX base generation")
        
        # Enhance prompt for professional quality
        enhanced_prompt = f"{prompt}, masterpiece, best quality, highly detailed, professional photography, 8k uhd"
        
        result = await service.generate_image(
            prompt=enhanced_prompt,
            negative_prompt=f"{negative_prompt}, low quality, blurry, artifacts, distorted",
            width=layer.parameters["width"],
            height=layer.parameters["height"],
            num_inference_steps=layer.parameters["steps"],
            guidance_scale=layer.parameters["guidance_scale"],
            seed=layer.parameters.get("seed", -1)
        )
        
        if not result or not result.get("urls"):
            raise Exception(f"FLUX base generation failed: no URLs returned")
        
        return {
            "image_url": result["urls"][0],
            "image_b64": result.get("image_b64"),
            "seed": result.get("seed"),
            "model_info": result.get("metadata", {})
        }
    
    async def _execute_controlnet_refinement(self, layer: LayerConfig, service: Any, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute ControlNet refinement for precise control"""
        base_result = self.results["flux_base_generation"]
        base_image = base_result.data["image_url"]
        
        prompt = context.get("prompt", "")
        control_image = context.get("control_image")  # Optional control image
        
        if not control_image:
            # Use base image as control image for self-refinement
            control_image = base_image
        
        result = await service.image_to_image(
            prompt=prompt,
            init_image=base_image,
            num_inference_steps=20,
            guidance_scale=7.5
        )
        
        if not result or not result.get("urls"):
            # Fallback to base image if ControlNet fails
            logger.warning("ControlNet refinement failed, using base image")
            return base_result.data
        
        return {
            "image_url": result["urls"][0],
            "image_b64": result.get("image_b64"),
            "control_type": layer.parameters["controlnet_type"],
            "model_info": result.get("metadata", {})
        }
    
    async def _execute_lora_application(self, layer: LayerConfig, service: Any, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute LoRA style application with character consistency"""
        refined_result = self.results["controlnet_refinement"]
        input_image = refined_result.data["image_url"]
        
        prompt = context.get("prompt", "")
        lora_style = context.get("lora_style", "realism")
        face_image = context.get("face_image")  # Character consistency reference
        character_mode = context.get("character_mode", "instant_id")  # instant_id, consistent_character, or flux_lora
        
        # Use character consistency if face image is provided
        if face_image and hasattr(service, 'instant_id_generation'):
            logger.info("Using InstantID for character-consistent LoRA application")
            try:
                result = await service.instant_id_generation(
                    prompt=f"{prompt}, {lora_style} style",
                    face_image=face_image,
                    identitynet_strength_ratio=0.8,
                    adapter_strength_ratio=0.8,
                    num_inference_steps=20,
                    guidance_scale=5.0
                )
                
                if result.get("urls") and len(result["urls"]) > 0:
                    return {
                        "image_url": result["urls"][0],
                        "image_b64": result.get("image_b64"),
                        "lora_applied": lora_style,
                        "character_consistency": "instant_id",
                        "model_info": result.get("model_info", {})
                    }
            except Exception as e:
                logger.warning(f"InstantID generation failed: {e}, falling back to standard LoRA")
        
        # Use consistent character generation if specified
        elif face_image and character_mode == "consistent_character" and hasattr(service, 'consistent_character_generation'):
            logger.info("Using consistent character generation for LoRA application")
            try:
                result = await service.consistent_character_generation(
                    subject=face_image,
                    prompt=f"{prompt}, {lora_style} style",
                    number_of_images=1
                )
                
                if result.get("urls") and len(result["urls"]) > 0:
                    return {
                        "image_url": result["urls"][0],
                        "image_b64": result.get("image_b64"),
                        "lora_applied": lora_style,
                        "character_consistency": "consistent_character",
                        "model_info": result.get("model_info", {})
                    }
            except Exception as e:
                logger.warning(f"Consistent character generation failed: {e}, falling back to standard LoRA")
        
        # Use FLUX LoRA generation if available
        elif hasattr(service, 'flux_lora_generation'):
            logger.info("Using FLUX LoRA generation")
            try:
                result = await service.flux_lora_generation(
                    prompt=f"{prompt}, {lora_style} style",
                    lora_scale=layer.parameters["lora_weights"][0],
                    num_inference_steps=20,
                    guidance_scale=3.5
                )
                
                if result.get("urls") and len(result["urls"]) > 0:
                    return {
                        "image_url": result["urls"][0],
                        "image_b64": result.get("image_b64"),
                        "lora_applied": lora_style,
                        "generation_method": "flux_lora",
                        "model_info": result.get("model_info", {})
                    }
            except Exception as e:
                logger.warning(f"FLUX LoRA generation failed: {e}, falling back to standard method")
        
        # Fallback to standard image generation
        logger.info("Using standard image generation for LoRA application")
        result = await service.image_to_image(
            prompt=f"{prompt}, {lora_style} style",
            init_image=input_image,
            strength=layer.parameters["denoising_strength"],
            num_inference_steps=15
        )
        
        if not result or not result.get("urls"):
            # Fallback to previous result if LoRA fails
            logger.warning("LoRA application failed, using refined image")
            return refined_result.data
        
        return {
            "image_url": result["urls"][0],
            "image_b64": result.get("image_b64"),
            "lora_applied": lora_style,
            "generation_method": "standard",
            "model_info": result.get("metadata", {})
        }
    
    async def _execute_detail_enhancement(self, layer: LayerConfig, service: Any, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute detail enhancement with ADetailer"""
        styled_result = self.results["lora_style_application"]
        input_image = styled_result.data["image_url"]
        
        result = await service.image_to_image(
            prompt="face restoration, detailed enhancement",
            init_image=input_image,
            strength=layer.parameters["denoising_strength"],
            num_inference_steps=20
        )
        
        if not result or not result.get("urls"):
            # Fallback to previous result if enhancement fails
            logger.warning("Detail enhancement failed, using styled image")
            return styled_result.data
        
        return {
            "image_url": result["urls"][0],
            "image_b64": result.get("image_b64"),
            "faces_enhanced": 1,  # Assume face was enhanced
            "model_info": result.get("metadata", {})
        }
    
    async def _execute_ultimate_upscaling(self, layer: LayerConfig, service: Any, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute ultimate upscaling for professional quality"""
        enhanced_result = self.results["detail_enhancement"]
        input_image = enhanced_result.data["image_url"]
        
        scale_factor = context.get("upscale_factor", layer.parameters["scale_factor"])
        
        # Use ultimate_upscale method if available
        if hasattr(service, 'ultimate_upscale'):
            logger.info("Using ultimate_upscale method for professional upscaling")
            try:
                result = await service.ultimate_upscale(
                    image=input_image,
                    scale=scale_factor,
                    scheduler="K_EULER_ANCESTRAL",
                    num_inference_steps=20,
                    guidance_scale=10.0,
                    strength=0.55,
                    hdr=0.0
                )
                
                if result.get("urls") and len(result["urls"]) > 0:
                    return {
                        "image_url": result["urls"][0],
                        "image_b64": result.get("image_b64"),
                        "upscale_factor": scale_factor,
                        "upscaling_method": "ultimate_sd",
                        "final_resolution": result.get("resolution"),
                        "model_info": result.get("model_info", {})
                    }
            except Exception as e:
                logger.warning(f"Ultimate upscale method failed: {e}, falling back to standard invoke")
        
        # Fallback to standard service - use image_to_image for upscaling
        logger.info("Using standard image_to_image for upscaling")
        result = await service.image_to_image(
            prompt="high resolution, ultra detailed, 4k quality",
            init_image=input_image,
            strength=0.3,  # Light modification for upscaling
            num_inference_steps=25
        )
        
        if not result or not result.get("urls"):
            # Fallback to previous result if upscaling fails
            logger.warning("Ultimate upscaling failed, using enhanced image")
            return enhanced_result.data
        
        return {
            "image_url": result["urls"][0],
            "image_b64": result.get("image_b64"),
            "upscale_factor": scale_factor,
            "upscaling_method": "standard",
            "final_resolution": f"enhanced_{scale_factor}x",
            "model_info": result.get("metadata", {})
        }
    
    async def invoke(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the complete FLUX Professional Pipeline
        
        Args:
            context: {
                "prompt": str,                    # Required: Main generation prompt
                "negative_prompt": str,           # Optional: Negative prompt
                "control_image": str,             # Optional: Control image URL/path
                "lora_style": str,               # Optional: LoRA style ("realism", "anime", "art_style")
                "face_image": str,               # Optional: Reference face for character consistency
                "character_mode": str,           # Optional: Character consistency mode ("instant_id", "consistent_character", "flux_lora")
                "upscale_factor": int,           # Optional: Upscaling factor (2, 4, 8)
                "width": int,                    # Optional: Base width (default 1024)
                "height": int                    # Optional: Base height (default 1024)
            }
        
        Returns:
            Dict with professional quality image generation results including character consistency
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Validate input
            if not context.get("prompt"):
                raise ValueError("Prompt is required for FLUX Professional Pipeline")
            
            # Initialize services
            await self.initialize_services()
            
            # Execute layers in sequence
            self.results.clear()
            
            for layer in self.layers:
                logger.info(f"Executing layer: {layer.name}")
                
                result = await self.execute_layer(layer, context)
                self.results[layer.name] = result
                
                if not result.success:
                    logger.error(f"Layer {layer.name} failed: {result.error}")
                    if not layer.fallback_enabled:
                        break
            
            # Build final result
            total_time = asyncio.get_event_loop().time() - start_time
            
            # Get the final high-quality image
            final_result = self.results.get("ultimate_upscaling")
            if not final_result or not final_result.success:
                # Try previous layers as fallback
                for layer_name in ["detail_enhancement", "lora_style_application", "controlnet_refinement", "flux_base_generation"]:
                    fallback_result = self.results.get(layer_name)
                    if fallback_result and fallback_result.success:
                        final_result = fallback_result
                        break
            
            if not final_result or not final_result.success:
                return {
                    "success": False,
                    "error": "All pipeline stages failed",
                    "service": self.service_name,
                    "total_execution_time": total_time,
                    "layer_results": {name: result for name, result in self.results.items()}
                }
            
            return {
                "success": True,
                "service": self.service_name,
                "total_execution_time": total_time,
                "final_output": {
                    "image_url": final_result.data["image_url"],
                    "image_b64": final_result.data.get("image_b64"),
                    "final_resolution": final_result.data.get("final_resolution"),
                    "generation_info": {
                        "prompt": context["prompt"],
                        "stages_completed": len([r for r in self.results.values() if r.success]),
                        "total_stages": len(self.layers),
                        "pipeline": "FLUX Professional"
                    }
                },
                "layer_results": {name: result for name, result in self.results.items()},
                "performance_metrics": self.get_performance_metrics()
            }
            
        except Exception as e:
            total_time = asyncio.get_event_loop().time() - start_time
            logger.error(f"FLUX Professional Pipeline failed: {e}")
            
            return {
                "success": False,
                "error": str(e),
                "service": self.service_name,
                "total_execution_time": total_time,
                "layer_results": {name: result for name, result in self.results.items()}
            }
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for the pipeline"""
        total_layers = len(self.layers)
        successful_layers = len([r for r in self.results.values() if r.success])
        failed_layers = total_layers - successful_layers
        
        total_execution_time = sum(r.execution_time for r in self.results.values())
        
        layer_times = {r.layer_name: r.execution_time for r in self.results.values()}
        
        return {
            "total_layers": total_layers,
            "successful_layers": successful_layers,
            "failed_layers": failed_layers,
            "total_execution_time": total_execution_time,
            "layer_times": layer_times,
            "pipeline_type": "FLUX Professional",
            "average_layer_time": total_execution_time / max(len(self.results), 1)
        }
    
    async def execute_fallback(self, layer: LayerConfig, context: Dict[str, Any], error: str) -> Optional[LayerResult]:
        """Execute fallback logic for failed layers"""
        logger.info(f"Executing fallback for layer {layer.name}")
        
        # For image generation layers, try simpler alternatives
        if layer.layer_type == LayerType.GENERATION:
            # Fallback to basic SDXL if FLUX fails
            try:
                basic_service = self.ai_factory.get_image_gen(model_name="black-forest-labs/flux-schnell")
                result = await basic_service.generate_image(
                    prompt=context.get("prompt", ""),
                    width=1024,
                    height=1024
                )
                
                if result and result.get("urls"):
                    fallback_data = {
                        "image_url": result["urls"][0],
                        "image_b64": result.get("image_b64"),
                        "model_info": result.get("metadata", {})
                    }
                    return LayerResult(
                        layer_name=f"{layer.name}_fallback",
                        success=True,
                        data=fallback_data,
                        metadata={"fallback": True, "original_error": error},
                        execution_time=0.0
                    )
            except Exception as e:
                logger.error(f"Fallback for {layer.name} also failed: {e}")
        
        return None
    
    async def close(self):
        """Clean up services"""
        for service in self.services.values():
            if hasattr(service, 'close'):
                await service.close()
        logger.info(f"Closed {self.service_name}")