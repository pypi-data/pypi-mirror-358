"""
Health Check Routes

System health and status endpoints
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import time
import psutil
import torch
from typing import Dict, Any

router = APIRouter()

class HealthResponse(BaseModel):
    status: str
    timestamp: float
    version: str
    uptime: float
    system: Dict[str, Any]

@router.get("/", response_model=HealthResponse)
async def health_check():
    """
    Basic health check endpoint
    """
    return HealthResponse(
        status="healthy",
        timestamp=time.time(),
        version="1.0.0",
        uptime=time.time(),  # Simplified uptime
        system={
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "gpu_available": torch.cuda.is_available(),
            "gpu_count": torch.cuda.device_count() if torch.cuda.is_available() else 0
        }
    )

@router.get("/detailed")
async def detailed_health():
    """
    Detailed health check with system information
    """
    gpu_info = []
    if torch.cuda.is_available():
        for i in range(torch.cuda.device_count()):
            gpu_info.append({
                "device": i,
                "name": torch.cuda.get_device_name(i),
                "memory_allocated": torch.cuda.memory_allocated(i),
                "memory_cached": torch.cuda.memory_reserved(i)
            })
    
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "system": {
            "cpu": {
                "percent": psutil.cpu_percent(),
                "count": psutil.cpu_count()
            },
            "memory": {
                "percent": psutil.virtual_memory().percent,
                "available": psutil.virtual_memory().available,
                "total": psutil.virtual_memory().total
            },
            "gpu": {
                "available": torch.cuda.is_available(),
                "devices": gpu_info
            }
        }
    }

@router.get("/ready")
async def readiness_probe():
    """
    Kubernetes readiness probe endpoint
    """
    # Add model loading checks here
    return {"status": "ready", "timestamp": time.time()}