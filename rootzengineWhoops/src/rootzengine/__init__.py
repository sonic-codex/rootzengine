"""
RootzEngine - Advanced Audio Analysis and Pattern Detection Library
"""

__version__ = "0.1.0"
__author__ = "RootzEngine Team"

from .core.config import settings
from .audio.analysis import AudioStructureAnalyzer
from .ml.training import train_model

__all__ = [
    "settings",
    "AudioStructureAnalyzer", 
    "train_model"
]