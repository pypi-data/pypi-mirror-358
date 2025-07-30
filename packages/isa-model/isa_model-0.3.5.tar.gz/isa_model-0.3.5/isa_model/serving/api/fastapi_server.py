"""
FastAPI Server for ISA Model Serving

Main FastAPI application that serves model inference endpoints
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
import logging
from typing import Dict, Any

from .routes import ui_analysis, vision, llm, health
from .middleware.request_logger import RequestLoggerMiddleware

logger = logging.getLogger(__name__)

def create_app(config: Dict[str, Any] = None) -> FastAPI:
    """
    Create and configure FastAPI application
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        Configured FastAPI application
    """
    app = FastAPI(
        title="ISA Model Serving API",
        description="High-performance model inference API",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add custom middleware
    app.add_middleware(RequestLoggerMiddleware)
    
    # Exception handlers
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Global exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "detail": str(exc) if config and config.get("debug") else "An error occurred"
            }
        )
    
    # Include routers
    app.include_router(health.router, prefix="/health", tags=["health"])
    app.include_router(ui_analysis.router, prefix="/ui-analysis", tags=["ui-analysis"])
    app.include_router(vision.router, prefix="/vision", tags=["vision"])
    app.include_router(llm.router, prefix="/llm", tags=["llm"])
    
    # Root endpoint
    @app.get("/")
    async def root():
        return {
            "service": "isa-model-serving",
            "version": "1.0.0",
            "status": "running",
            "timestamp": time.time()
        }
    
    return app

# Create default app instance
app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)