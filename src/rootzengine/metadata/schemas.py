"""
Rich Agentic Metadata Schemas for RootzEngine

This module defines comprehensive metadata schemas for linking audio, MIDI,
and analysis data in the AI bandmate system.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import json
import uuid
from pathlib import Path

import logging

logger = logging.getLogger(__name__)


class ProcessingStatus(Enum):
    """Status of processing pipeline stages."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    VALIDATED = "validated"


class FileType(Enum):
    """Types of files in the processing pipeline."""
    AUDIO = "audio"
    AUDIO_STEM = "audio_stem"
    MIDI = "midi"
    MIDI_CONVERTED = "midi_converted"
    METADATA = "metadata"
    SPECTROTONE = "spectrotone"
    ANALYSIS = "analysis"


@dataclass
class FileReference:
    """Reference to a file in the processing pipeline."""
    file_id: str
    file_type: FileType
    file_path: str
    file_size: Optional[int] = None
    checksum: Optional[str] = None
    created_at: Optional[datetime] = None
    

@dataclass
class ProcessingMetrics:
    """Metrics from processing pipeline stages."""
    stage_name: str
    status: ProcessingStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    accuracy_score: Optional[float] = None
    confidence_score: Optional[float] = None
    error_message: Optional[str] = None
    

@dataclass
class SpectrotoneAnalysis:
    """Spectrotone analysis results for an instrument."""
    instrument: str
    primary_color: str
    secondary_color: str
    timbre: str
    brightness: float  # 0.0-1.0
    weight: float      # 0.0-1.0
    resonance: float   # 0.0-1.0
    harmonic_content: Dict[str, float]  # frequency bands
    temporal_evolution: List[Dict[str, float]]  # how spectrotone changes over time
    

@dataclass
class InstrumentAnalysis:
    """Complete analysis for a single instrument/channel."""
    channel: int
    instrument: str
    note_range: tuple[int, int]
    velocity_curve: List[int]
    timing_variations: Dict[str, float]
    playing_patterns: List[str]
    harmonic_function: str
    interaction_patterns: Dict[int, float]  # channel -> interaction strength
    behavioral_traits: Dict[str, float]
    spectrotone: SpectrotoneAnalysis
    midi_events_count: int
    dominant_rhythmic_pattern: str
    

@dataclass
class CrossChannelRelationships:
    """Analysis of relationships between instruments/channels."""
    bass_drum_lock: float           # How tightly bass follows drums
    harmonic_coherence: float       # Overall harmonic consistency  
    rhythmic_subdivision: str       # Primary rhythmic subdivision
    groove_pocket: float           # How well instruments lock into groove
    dynamic_correlation: Dict[str, float]  # How dynamics correlate between parts
    call_response_patterns: List[Dict[str, Any]]  # Call and response relationships
    

@dataclass
class GrooveTemplate:
    """Template describing the overall groove characteristics."""
    riddim_type: str
    tempo_bpm: float
    tempo_stability: float
    key_signature: str
    mode: str
    time_signature: str
    micro_timing_signature: List[float]  # Timing deviations per beat subdivision
    dynamic_arc: str                     # Overall dynamic shape
    section_structure: List[str]         # Song sections (intro, verse, chorus, etc.)
    harmonic_rhythm: float              # Rate of chord changes
    

@dataclass
class AITrainingFeatures:
    """Features optimized for AI bandmate training."""
    spectrotone_vectors: Dict[str, List[float]]        # Per-instrument spectrotone vectors
    harmonic_progression_vectors: List[List[float]]    # Chord progression as vectors
    rhythmic_pattern_vectors: Dict[int, List[float]]   # Per-channel rhythm vectors
    instrumental_behavior_vectors: Dict[int, List[float]]  # Behavioral characteristic vectors
    interaction_matrices: Dict[str, List[List[float]]]  # Inter-instrument interaction data
    groove_context_vectors: List[float]                # Overall groove characteristics
    

@dataclass
class EnrichmentData:
    """Metadata enrichment from external sources."""
    source: str  # "spotify", "audd", "musicbrainz", etc.
    track_title: Optional[str] = None
    artist: Optional[str] = None
    album: Optional[str] = None
    release_year: Optional[int] = None
    genre: Optional[str] = None
    subgenre: Optional[str] = None
    tempo_detected: Optional[float] = None
    key_detected: Optional[str] = None
    energy: Optional[float] = None
    danceability: Optional[float] = None
    valence: Optional[float] = None
    confidence_score: Optional[float] = None
    

class AgenticMetadata:
    """Complete metadata schema for agentic AI bandmate system."""
    
    def __init__(self, source_file_path: str):
        """Initialize metadata for a source file."""
        self.file_id = str(uuid.uuid4())
        self.created_at = datetime.now()
        self.source_file = source_file_path
        self.source_file_type = self._detect_file_type(source_file_path)
        
        # File references
        self.file_references: Dict[str, FileReference] = {}
        
        # Processing chain
        self.processing_chain: List[ProcessingMetrics] = []
        
        # Analysis results
        self.per_channel_analysis: Dict[int, InstrumentAnalysis] = {}
        self.cross_channel_relationships: Optional[CrossChannelRelationships] = None
        self.groove_template: Optional[GrooveTemplate] = None
        
        # AI training data
        self.ai_training_features: Optional[AITrainingFeatures] = None
        
        # External enrichment
        self.enrichment_data: List[EnrichmentData] = []
        
        # Processing status
        self.processing_complete = False
        self.validation_passed = False
        self.accuracy_score: Optional[float] = None
        
    def _detect_file_type(self, file_path: str) -> FileType:
        """Detect file type from extension."""
        ext = Path(file_path).suffix.lower()
        if ext in ['.mp3', '.wav', '.flac', '.aac']:
            return FileType.AUDIO
        elif ext in ['.mid', '.midi']:
            return FileType.MIDI
        else:
            return FileType.ANALYSIS
    
    def add_file_reference(self, reference_id: str, file_ref: FileReference):
        """Add a file reference to the metadata."""
        self.file_references[reference_id] = file_ref
        logger.info(f"Added file reference: {reference_id} -> {file_ref.file_path}")
    
    def add_processing_stage(self, metrics: ProcessingMetrics):
        """Add processing stage metrics."""
        self.processing_chain.append(metrics)
        logger.info(f"Added processing stage: {metrics.stage_name} - {metrics.status.value}")
    
    def add_channel_analysis(self, channel: int, analysis: InstrumentAnalysis):
        """Add analysis for a specific channel."""
        self.per_channel_analysis[channel] = analysis
        logger.info(f"Added channel analysis: {channel} - {analysis.instrument}")
    
    def add_enrichment_data(self, enrichment: EnrichmentData):
        """Add external enrichment data."""
        self.enrichment_data.append(enrichment)
        logger.info(f"Added enrichment data from: {enrichment.source}")
    
    def set_cross_channel_relationships(self, relationships: CrossChannelRelationships):
        """Set cross-channel relationship analysis."""
        self.cross_channel_relationships = relationships
        
    def set_groove_template(self, template: GrooveTemplate):
        """Set groove template."""
        self.groove_template = template
        
    def set_ai_training_features(self, features: AITrainingFeatures):
        """Set AI training features."""
        self.ai_training_features = features
        
    def mark_processing_complete(self, accuracy_score: float):
        """Mark processing as complete with accuracy score."""
        self.processing_complete = True
        self.accuracy_score = accuracy_score
        self.validation_passed = accuracy_score >= 0.85  # 85% accuracy threshold
        
    def get_linked_files(self) -> Dict[str, str]:
        """Get all linked files as a dictionary."""
        return {ref_id: ref.file_path for ref_id, ref in self.file_references.items()}
    
    def get_processing_summary(self) -> Dict[str, Any]:
        """Get summary of processing pipeline."""
        return {
            "total_stages": len(self.processing_chain),
            "completed_stages": len([s for s in self.processing_chain if s.status == ProcessingStatus.COMPLETED]),
            "failed_stages": len([s for s in self.processing_chain if s.status == ProcessingStatus.FAILED]),
            "overall_accuracy": self.accuracy_score,
            "validation_passed": self.validation_passed,
            "processing_complete": self.processing_complete
        }
    
    def get_channel_summary(self) -> Dict[str, Any]:
        """Get summary of channel analysis."""
        return {
            "channels_analyzed": len(self.per_channel_analysis),
            "instruments": [analysis.instrument for analysis in self.per_channel_analysis.values()],
            "channel_mapping": {ch: analysis.instrument for ch, analysis in self.per_channel_analysis.items()}
        }
    
    def export_for_agent_training(self, agent_channel: int) -> Optional[Dict[str, Any]]:
        """Export data optimized for training a specific agent."""
        if agent_channel not in self.per_channel_analysis:
            return None
            
        channel_analysis = self.per_channel_analysis[agent_channel]
        
        return {
            "agent_config": {
                "channel": agent_channel,
                "instrument": channel_analysis.instrument,
                "note_range": channel_analysis.note_range,
                "primary_patterns": channel_analysis.playing_patterns
            },
            "behavioral_data": channel_analysis.behavioral_traits,
            "interaction_data": channel_analysis.interaction_patterns,
            "spectrotone_profile": asdict(channel_analysis.spectrotone),
            "groove_context": asdict(self.groove_template) if self.groove_template else None,
            "training_vectors": self.ai_training_features.instrumental_behavior_vectors.get(agent_channel) if self.ai_training_features else None
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary for JSON serialization."""
        return {
            "file_id": self.file_id,
            "created_at": self.created_at.isoformat(),
            "source_file": self.source_file,
            "source_file_type": self.source_file_type.value,
            "file_references": {
                ref_id: {
                    "file_id": ref.file_id,
                    "file_type": ref.file_type.value,
                    "file_path": ref.file_path,
                    "file_size": ref.file_size,
                    "checksum": ref.checksum,
                    "created_at": ref.created_at.isoformat() if ref.created_at else None
                }
                for ref_id, ref in self.file_references.items()
            },
            "processing_chain": [
                {
                    "stage_name": stage.stage_name,
                    "status": stage.status.value,
                    "start_time": stage.start_time.isoformat(),
                    "end_time": stage.end_time.isoformat() if stage.end_time else None,
                    "duration_seconds": stage.duration_seconds,
                    "accuracy_score": stage.accuracy_score,
                    "confidence_score": stage.confidence_score,
                    "error_message": stage.error_message
                }
                for stage in self.processing_chain
            ],
            "per_channel_analysis": {
                str(channel): asdict(analysis) if hasattr(analysis, '__dict__') else analysis
                for channel, analysis in self.per_channel_analysis.items()
            },
            "cross_channel_relationships": asdict(self.cross_channel_relationships) if self.cross_channel_relationships else None,
            "groove_template": asdict(self.groove_template) if self.groove_template else None,
            "ai_training_features": asdict(self.ai_training_features) if self.ai_training_features else None,
            "enrichment_data": [asdict(enrichment) for enrichment in self.enrichment_data],
            "processing_summary": self.get_processing_summary(),
            "channel_summary": self.get_channel_summary()
        }
    
    def save_to_file(self, output_path: str):
        """Save metadata to JSON file."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved metadata to: {output_path}")
    
    @classmethod
    def load_from_file(cls, file_path: str) -> 'AgenticMetadata':
        """Load metadata from JSON file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Create instance
        metadata = cls(data['source_file'])
        metadata.file_id = data['file_id']
        metadata.created_at = datetime.fromisoformat(data['created_at'])
        metadata.processing_complete = data.get('processing_summary', {}).get('processing_complete', False)
        metadata.validation_passed = data.get('processing_summary', {}).get('validation_passed', False)
        metadata.accuracy_score = data.get('processing_summary', {}).get('overall_accuracy')
        
        # Load file references
        for ref_id, ref_data in data.get('file_references', {}).items():
            file_ref = FileReference(
                file_id=ref_data['file_id'],
                file_type=FileType(ref_data['file_type']),
                file_path=ref_data['file_path'],
                file_size=ref_data.get('file_size'),
                checksum=ref_data.get('checksum'),
                created_at=datetime.fromisoformat(ref_data['created_at']) if ref_data.get('created_at') else None
            )
            metadata.file_references[ref_id] = file_ref
        
        logger.info(f"Loaded metadata from: {file_path}")
        return metadata


def create_metadata_template(source_file: str) -> AgenticMetadata:
    """Create a new metadata template for a source file."""
    return AgenticMetadata(source_file)


def validate_metadata_schema(metadata_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Validate metadata against the schema."""
    validation_result = {
        "valid": True,
        "errors": [],
        "warnings": []
    }
    
    required_fields = ['file_id', 'created_at', 'source_file', 'source_file_type']
    
    for field in required_fields:
        if field not in metadata_dict:
            validation_result["valid"] = False
            validation_result["errors"].append(f"Missing required field: {field}")
    
    # Validate processing completeness
    if metadata_dict.get('processing_summary', {}).get('processing_complete'):
        if not metadata_dict.get('per_channel_analysis'):
            validation_result["warnings"].append("Processing marked complete but no channel analysis present")
        
        if metadata_dict.get('processing_summary', {}).get('overall_accuracy', 0) < 0.85:
            validation_result["warnings"].append("Overall accuracy below recommended threshold (85%)")
    
    return validation_result