"""FastAPI application for RootzEngine API."""

import logging
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from ..core.config import RootzEngineConfig
from ..core.exceptions import RootzEngineError
from .routes import analysis, health

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager."""
    # Startup
    logger.info("🎵 Starting RootzEngine API server...")
    
    # Initialize configuration
    config = RootzEngineConfig()
    app.state.config = config
    
    # Create necessary directories
    config.data_dir.mkdir(parents=True, exist_ok=True)
    config.output_dir.mkdir(parents=True, exist_ok=True)
    config.cache_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info("✅ RootzEngine API server started successfully")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down RootzEngine API server...")


# Create FastAPI application
app = FastAPI(
    title="RootzEngine API",
    description="🎛️ AI-Powered Reggae Analysis & MIDI Generation Toolkit",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure appropriately for production
)


@app.middleware("http")
async def add_process_time_header(request, call_next):
    """Add process time header to responses."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.exception_handler(RootzEngineError)
async def rootzengine_exception_handler(request, exc: RootzEngineError):
    """Handle RootzEngine specific exceptions."""
    logger.error(f"RootzEngine error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "RootzEngine Error",
            "message": str(exc),
            "type": exc.__class__.__name__
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """Handle general exceptions."""
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred"
        }
    )


# Include routers
app.include_router(health.router, prefix="/health", tags=["Health"])
app.include_router(analysis.router, prefix="/api/v1/analysis", tags=["Analysis"])


@app.get("/", response_model=Dict[str, Any])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "RootzEngine API",
        "version": "0.1.0",
        "description": "🎛️ AI-Powered Reggae Analysis & MIDI Generation Toolkit",
        "docs_url": "/docs",
        "health_url": "/health",
        "endpoints": {
            "analysis": "/api/v1/analysis",
            "health": "/health"
        },
        "features": [
            "Audio structure analysis",
            "Reggae pattern recognition", 
            "MIDI generation",
            "Batch processing",
            "Real-time analysis"
        ]
    }


@app.get("/info")
async def get_info():
    """Get API information and configuration."""
    config = app.state.config
    
    return {
        "api_version": "0.1.0",
        "audio_config": {
            "sample_rate": config.audio.sample_rate,
            "hop_length": config.audio.hop_length,
            "supported_formats": ["wav", "mp3", "flac", "aac"]
        },
        "processing": {
            "workers": config.workers,
            "batch_processing": True,
            "cloud_processing": bool(config.azure)
        },
        "features": {
            "riddim_types": ["one_drop", "steppers", "rockers", "digital"],
            "instruments": ["drums", "bass", "organ", "guitar"],
            "analysis_types": ["structure", "tempo", "key", "reggae_patterns"]
        }
    }


if __name__ == "__main__":
    uvicorn.run(
        "rootzengine.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )