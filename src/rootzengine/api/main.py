"""Main FastAPI application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.rootzengine.api.router import register_routes
from src.rootzengine.core.config import settings

# Create FastAPI app
app = FastAPI(
    title="RootzEngine API",
    description="API for RootzEngine: AI-Powered Reggae Metadata + Groove Generation Toolkit",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all API routes
register_routes(app)


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint returning basic API info."""
    return {
        "app": "RootzEngine API",
        "version": app.version,
        "status": "online",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return JSONResponse(
        content={"status": "healthy", "environment": settings.environment},
        status_code=200,
    )
