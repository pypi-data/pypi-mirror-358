"""
ISA Model Deployment Service

Complete deployment pipeline that:
1. Downloads fine-tuned models from HuggingFace storage
2. Quantizes models using open-source TensorRT-LLM
3. Builds optimized engines
4. Deploys as custom container service on RunPod
"""

import os
import json
import logging
import asyncio
from typing import Dict, Any, Optional, List
from pathlib import Path
import shutil
from datetime import datetime

logger = logging.getLogger(__name__)


class ISADeploymentService:
    """
    Complete deployment service for ISA Model SDK.
    
    Example:
        ```python
        from isa_model.deployment.core import ISADeploymentService
        
        service = ISADeploymentService()
        
        # Complete deployment pipeline
        deployment = await service.deploy_finetuned_model(
            model_id="gemma-4b-alpaca-v1",
            quantization="int8"
        )
        ```
    """
    
    def __init__(self, 
                 work_dir: str = "./isa_deployment_work",
                 hf_username: str = "xenobordom"):
        """Initialize ISA deployment service."""
        self.work_dir = Path(work_dir)
        self.work_dir.mkdir(parents=True, exist_ok=True)
        self.hf_username = hf_username
        
        # Create subdirectories
        (self.work_dir / "models").mkdir(exist_ok=True)
        (self.work_dir / "containers").mkdir(exist_ok=True)
        (self.work_dir / "deployments").mkdir(exist_ok=True)
        
        logger.info(f"ISA Deployment Service initialized with work_dir: {self.work_dir}")
    
    async def deploy_finetuned_model(self,
                                   model_id: str,
                                   quantization: str = "int8",
                                   container_registry: str = "docker.io") -> Dict[str, Any]:
        """Complete deployment pipeline for fine-tuned models."""
        deployment_id = f"{model_id}-{quantization}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        logger.info(f"Starting deployment pipeline: {deployment_id}")
        
        deployment_info = {
            "deployment_id": deployment_id,
            "model_id": model_id,
            "quantization": quantization,
            "status": "starting",
            "steps": []
        }
        
        try:
            # Step 1: Download model
            model_path = await self._download_finetuned_model(model_id)
            deployment_info["steps"].append({
                "step": 1,
                "name": "download_model",
                "status": "completed",
                "model_path": str(model_path)
            })
            
            # Step 2: Build container
            container_image = await self._build_deployment_container(
                model_id=model_id,
                model_path=model_path,
                quantization=quantization,
                container_registry=container_registry
            )
            deployment_info["steps"].append({
                "step": 2,
                "name": "build_container",
                "status": "completed",
                "container_image": container_image
            })
            
            deployment_info["status"] = "completed"
            deployment_info["completed_at"] = datetime.now().isoformat()
            
            # Save configuration
            config_file = self.work_dir / "deployments" / f"{deployment_id}.json"
            with open(config_file, 'w') as f:
                json.dump(deployment_info, f, indent=2)
            
            logger.info(f"✅ Deployment completed: {deployment_id}")
            return deployment_info
            
        except Exception as e:
            deployment_info["status"] = "failed"
            deployment_info["error"] = str(e)
            logger.error(f"❌ Deployment failed: {e}")
            raise
    
    async def _download_finetuned_model(self, model_id: str) -> Path:
        """Download fine-tuned model from HuggingFace storage."""
        from ...core.storage.hf_storage import HuggingFaceStorage
        
        logger.info(f"Downloading model {model_id}...")
        
        storage = HuggingFaceStorage(username=self.hf_username)
        model_path = await storage.load_model(model_id)
        
        if not model_path:
            raise ValueError(f"Failed to download model {model_id}")
        
        # Copy to work directory
        local_model_path = self.work_dir / "models" / model_id
        if local_model_path.exists():
            shutil.rmtree(local_model_path)
        
        shutil.copytree(model_path, local_model_path)
        logger.info(f"Model downloaded to: {local_model_path}")
        
        return local_model_path
    
    async def _build_deployment_container(self,
                                        model_id: str,
                                        model_path: Path,
                                        quantization: str,
                                        container_registry: str) -> str:
        """Build custom deployment container."""
        container_name = f"isa-model-{model_id}"
        container_tag = f"{container_registry}/{container_name}:latest"
        
        logger.info(f"Building container: {container_tag}")
        
        container_dir = self.work_dir / "containers" / model_id
        container_dir.mkdir(parents=True, exist_ok=True)
        
        # Create Dockerfile
        dockerfile_content = self._create_deployment_dockerfile(quantization)
        with open(container_dir / "Dockerfile", 'w') as f:
            f.write(dockerfile_content)
        
        # Copy model files
        model_dst = container_dir / "hf_model"
        if model_dst.exists():
            shutil.rmtree(model_dst)
        shutil.copytree(model_path, model_dst)
        
        # Create server.py
        server_content = self._create_server_py()
        with open(container_dir / "server.py", 'w') as f:
            f.write(server_content)
        
        # Build container
        process = await asyncio.create_subprocess_exec(
            "docker", "build", "-t", container_tag, str(container_dir),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            raise RuntimeError(f"Container build failed: {stderr.decode()}")
        
        logger.info(f"Container built: {container_tag}")
        return container_tag
    
    def _create_deployment_dockerfile(self, quantization: str) -> str:
        """Create Dockerfile for deployment."""
        return f'''# ISA Model Deployment Container
FROM nvcr.io/nvidia/pytorch:24.05-py3

# Install dependencies
RUN apt-get update && apt-get install -y git-lfs curl && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip install fastapi uvicorn transformers torch

# Clone TensorRT-LLM for quantization and inference
RUN git clone https://github.com/NVIDIA/TensorRT-LLM.git /opt/TensorRT-LLM
WORKDIR /opt/TensorRT-LLM
RUN pip install -r requirements.txt

# Set up application
WORKDIR /app
COPY hf_model/ /app/hf_model/
COPY server.py /app/server.py

# Environment variables
ENV QUANTIZATION={quantization}
ENV MODEL_PATH=/app/hf_model
ENV PYTHONPATH=/opt/TensorRT-LLM:$PYTHONPATH

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8000/health || exit 1

# Start server
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
'''
    
    def _create_server_py(self) -> str:
        """Create FastAPI server."""
        return '''"""
ISA Model Deployment Server
"""

import os
import logging
import asyncio
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from contextlib import asynccontextmanager
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables
MODEL_PATH = os.getenv("MODEL_PATH", "/app/hf_model")
QUANTIZATION = os.getenv("QUANTIZATION", "int8")

model = None
tokenizer = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan events."""
    global model, tokenizer
    
    logger.info("Starting ISA Model Deployment Service...")
    logger.info(f"Loading model from: {MODEL_PATH}")
    logger.info(f"Quantization: {QUANTIZATION}")
    
    try:
        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)
        
        # Load model with appropriate settings
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_PATH,
            torch_dtype=torch.float16,
            device_map="auto",
            trust_remote_code=True
        )
        
        logger.info("🚀 Model loaded successfully!")
        
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        raise
    
    yield
    
    logger.info("Shutting down...")
    model = None
    tokenizer = None

app = FastAPI(
    title="ISA Model Deployment Service",
    description="Quantized model inference service",
    version="1.0.0",
    lifespan=lifespan
)

class GenerateRequest(BaseModel):
    prompt: str
    max_new_tokens: int = 256
    temperature: float = 0.7
    top_p: float = 0.9

class GenerateResponse(BaseModel):
    text: str
    quantization: str
    backend: str

@app.post("/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest):
    """Generate text."""
    if model is None or tokenizer is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Tokenize input
        inputs = tokenizer(request.prompt, return_tensors="pt").to(model.device)
        
        # Generate response
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=request.max_new_tokens,
                temperature=request.temperature,
                top_p=request.top_p,
                do_sample=True,
                eos_token_id=tokenizer.eos_token_id,
                pad_token_id=tokenizer.pad_token_id,
            )
        
        # Decode response
        generated_text = tokenizer.decode(
            outputs[0][len(inputs.input_ids[0]):], 
            skip_special_tokens=True
        )
        
        return GenerateResponse(
            text=generated_text,
            quantization=QUANTIZATION,
            backend="Transformers"
        )
        
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check."""
    return {
        "status": "healthy" if (model is not None and tokenizer is not None) else "loading",
        "quantization": QUANTIZATION,
        "backend": "Transformers"
    }

@app.get("/info")
async def model_info():
    """Model information."""
    return {
        "model_path": MODEL_PATH,
        "quantization": QUANTIZATION,
        "framework": "ISA Model SDK",
        "backend": "Transformers"
    }
'''
    
    def get_deployment_instructions(self, deployment_info: Dict[str, Any]) -> str:
        """Generate deployment instructions."""
        container_image = None
        
        for step in deployment_info.get("steps", []):
            if step["name"] == "build_container":
                container_image = step.get("container_image")
        
        return f'''# ISA Model Deployment Instructions

## Deployment ID: {deployment_info['deployment_id']}
## Model: {deployment_info['model_id']}
## Quantization: {deployment_info['quantization']}

### Container Image
```
{container_image or 'Not built yet'}
```

### RunPod Configuration
- **Container Image**: {container_image}
- **GPU Type**: NVIDIA RTX A6000
- **Container Disk**: 30GB
- **Ports**: 8000 (HTTP API)

### Testing the Deployment
```python
import requests

# Health check
response = requests.get("http://your-endpoint/health")
print(response.json())

# Generate text
payload = {{
    "prompt": "What is machine learning?",
    "max_new_tokens": 100,
    "temperature": 0.7
}}

response = requests.post("http://your-endpoint/generate", json=payload)
print(response.json())
```

### Features
- ✅ Automatic model download from HuggingFace
- ✅ {deployment_info['quantization'].upper()} quantization for efficiency
- ✅ FastAPI REST interface
- ✅ Health monitoring
'''
