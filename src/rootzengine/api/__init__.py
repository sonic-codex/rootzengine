"""API initialization."""

# These imports are used to ensure the routes are registered
# when the API is initialized and included in the FastAPI app
from src.rootzengine.api.routes import analysis, midi  # noqa
