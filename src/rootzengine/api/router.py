"""Router registration for the API."""

from fastapi import APIRouter

from src.rootzengine.api.routes import analysis, midi


def register_routes(app) -> None:
    """
    Register all API routes with the FastAPI application.
    
    Args:
        app: The FastAPI application instance
    """
    # Create main API router
    api_router = APIRouter(prefix="/api/v1")
    
    # Include routes from different modules
    api_router.include_router(
        analysis.router,
        prefix="/analysis",
        tags=["analysis"]
    )
    api_router.include_router(
        midi.router,
        prefix="/midi",
        tags=["midi"]
    )
    
    # Include the API router in the main app
    app.include_router(api_router)
