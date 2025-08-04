"""API initialization."""

# These imports are used to ensure the routes are registered
# when the API is initialized and included in the FastAPI app
from rootzengine.api.routes import analysis, midi, batch, reggae  # noqa
