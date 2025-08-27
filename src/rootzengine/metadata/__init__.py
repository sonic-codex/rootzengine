"""
Metadata Management Module for RootzEngine

This module provides comprehensive metadata schemas and management
for the agentic AI bandmate system.
"""

from .schemas import (
    AgenticMetadata,
    FileReference,
    ProcessingMetrics,
    InstrumentAnalysis,
    SpectrotoneAnalysis,
    CrossChannelRelationships,
    GrooveTemplate,
    AITrainingFeatures,
    EnrichmentData,
    ProcessingStatus,
    FileType,
    create_metadata_template,
    validate_metadata_schema
)

__all__ = [
    "AgenticMetadata",
    "FileReference", 
    "ProcessingMetrics",
    "InstrumentAnalysis",
    "SpectrotoneAnalysis",
    "CrossChannelRelationships",
    "GrooveTemplate",
    "AITrainingFeatures",
    "EnrichmentData",
    "ProcessingStatus",
    "FileType",
    "create_metadata_template",
    "validate_metadata_schema"
]