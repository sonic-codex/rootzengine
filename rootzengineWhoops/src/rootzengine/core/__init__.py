"""Core functionality for RootzEngine"""

from .config import settings
from .exceptions import RootzEngineError, AudioProcessingError

__all__ = ["settings", "RootzEngineError", "AudioProcessingError"]