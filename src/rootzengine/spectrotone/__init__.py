"""
Spectrotone Analysis Module for RootzEngine

This module provides comprehensive spectrotone analysis for mapping audio
characteristics to colors, timbres, and behavioral patterns for AI agents.
"""

from .analyzer import (
    SpectrotoneAnalyzer,
    SpectrotoneMapping,
    SpectrotoneProfile,
    SpectralCharacteristic,
    create_spectrotone_analyzer
)

__all__ = [
    "SpectrotoneAnalyzer",
    "SpectrotoneMapping",
    "SpectrotoneProfile", 
    "SpectralCharacteristic",
    "create_spectrotone_analyzer"
]