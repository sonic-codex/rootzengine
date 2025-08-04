"""Router registration for the API."""

from fastapi import APIRouter

from rootzengine.api.routes import analysis, midi, batch, reggae


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
    api_router.include_router(
        batch.router,
        prefix="/batch",
        tags=["batch"]
    )
    api_router.include_router(
        reggae.router,
        prefix="/reggae",
        tags=["reggae"]
    )
    
    # Include the API router in the main app
    app.include_router(api_router)
