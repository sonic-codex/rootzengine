"""
Unified Processing Pipeline for Maximum Extraction Efficiency

This module implements the core processing pipeline that handles both audio
and MIDI files with maximum data extraction before any deletions occur.
Optimized for agentic AI-bandmate training data generation.
"""

import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union, Tuple, Any
import tempfile
import shutil

import numpy as np
try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False
    logger.warning("librosa not available - using mock audio processing")

try:
    import pretty_midi
    PRETTY_MIDI_AVAILABLE = True
except ImportError:
    PRETTY_MIDI_AVAILABLE = False
    logger.warning("pretty_midi not available - using mock MIDI processing")

from ..metadata.schemas import (
    AgenticMetadata, 
    ProcessingStatus, 
    ProcessingMetrics,
    FileReference,
    FileType,
    InstrumentAnalysis,
    SpectrotoneAnalysis,
    CrossChannelRelationships,
    GrooveTemplate,
    AITrainingFeatures,
    EnrichmentData
)
from ..agents.channel_mapping import (
    get_channel_mapping,
    map_audio_stem_to_channel,
    create_agent_midi_template
)
from ..audio.features import FeatureExtractor
from ..audio.separation import StemSeparator
from ..midi.converter import AudioToMIDIConverter
from ..core.config import RootzEngineConfig
from ..core.exceptions import RootzEngineError, AudioProcessingError

logger = logging.getLogger(__name__)


class ProcessingResult:
    """Result from processing pipeline with all extracted data."""
    
    def __init__(self, source_file: str):
        self.source_file = source_file
        self.metadata = AgenticMetadata(source_file)
        self.success = False
        self.error_message: Optional[str] = None
        
        # Processing artifacts
        self.audio_features: Optional[Dict] = None
        self.stems: Dict[str, str] = {}  # stem_name -> file_path
        self.midi_data: Optional[pretty_midi.PrettyMIDI] = None
        self.midi_file_path: Optional[str] = None
        self.spectrotone_data: Dict[str, SpectrotoneAnalysis] = {}
        
        # Validation results
        self.midi_accuracy_score: Optional[float] = None
        self.validation_passed = False
        
        # Cleanup tracking
        self.temp_files: List[str] = []
        self.stems_deleted = False


class UnifiedProcessingPipeline:
    """
    Unified pipeline for processing both audio and MIDI files with
    maximum extraction efficiency for AI bandmate training.
    """
    
    def __init__(self, config: Optional[RootzEngineConfig] = None):
        """Initialize the processing pipeline."""
        self.config = config or RootzEngineConfig()
        self.channel_mapping = get_channel_mapping()
        
        # Initialize processors
        self.feature_extractor = FeatureExtractor(self.config.audio)
        self.stem_separator = StemSeparator(self.config.audio)
        
        # Processing thresholds
        self.ACCURACY_THRESHOLD = 0.85  # 85% accuracy for keeping MIDI
        self.MIN_STEM_QUALITY = 0.6     # Minimum stem separation quality
        
        logger.info("Initialized UnifiedProcessingPipeline")
    
    def process_file(self, input_file: Union[str, Path]) -> ProcessingResult:
        """
        Process a file (audio or MIDI) with maximum extraction efficiency.
        
        Args:
            input_file: Path to input file (audio or MIDI)
            
        Returns:
            ProcessingResult with all extracted data and metadata
        """
        input_path = Path(input_file)
        result = ProcessingResult(str(input_path))
        
        try:
            logger.info(f"Starting processing: {input_path.name}")
            
            # Detect file type and route to appropriate processor
            if input_path.suffix.lower() in ['.mp3', '.wav', '.flac', '.aac']:
                self._process_audio_file(input_path, result)
            elif input_path.suffix.lower() in ['.mid', '.midi']:
                self._process_midi_file(input_path, result)
            else:
                raise RootzEngineError(f"Unsupported file type: {input_path.suffix}")
            
            # Perform cross-modal validation if both audio and MIDI are available
            if result.audio_features and result.midi_data:
                self._cross_modal_validation(result)
            
            # Generate AI training features
            self._generate_ai_training_features(result)
            
            # Mark processing complete
            result.metadata.mark_processing_complete(
                result.midi_accuracy_score or 1.0
            )
            result.success = True
            
            logger.info(f"Processing completed successfully: {input_path.name}")
            
        except Exception as e:
            error_msg = f"Processing failed for {input_path.name}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            result.error_message = error_msg
            result.success = False
            
            # Add failed processing stage
            result.metadata.add_processing_stage(ProcessingMetrics(
                stage_name="processing_pipeline",
                status=ProcessingStatus.FAILED,
                start_time=datetime.now(),
                error_message=error_msg
            ))
        
        return result
    
    def _process_audio_file(self, audio_path: Path, result: ProcessingResult):
        """Process audio file with maximum extraction efficiency."""
        logger.info(f"Processing audio file: {audio_path.name}")
        
        # Stage 1: Audio Feature Extraction (most comprehensive first)
        stage_start = time.time()
        try:
            logger.info("Stage 1: Comprehensive audio feature extraction")
            result.audio_features = self.feature_extractor.extract_all_features(str(audio_path))
            
            result.metadata.add_processing_stage(ProcessingMetrics(
                stage_name="audio_feature_extraction",
                status=ProcessingStatus.COMPLETED,
                start_time=datetime.now(),
                end_time=datetime.now(),
                duration_seconds=time.time() - stage_start,
                confidence_score=0.9
            ))
            
        except Exception as e:
            raise AudioProcessingError(f"Audio feature extraction failed: {str(e)}")
        
        # Stage 2: Spectrotone Analysis (before stem separation)
        stage_start = time.time()
        try:
            logger.info("Stage 2: Spectrotone analysis")
            spectrotone_data = self._extract_spectrotone_analysis(
                str(audio_path), result.audio_features
            )
            result.spectrotone_data = spectrotone_data
            
            result.metadata.add_processing_stage(ProcessingMetrics(
                stage_name="spectrotone_analysis",
                status=ProcessingStatus.COMPLETED,
                start_time=datetime.now(),
                end_time=datetime.now(),
                duration_seconds=time.time() - stage_start
            ))
            
        except Exception as e:
            logger.warning(f"Spectrotone analysis failed: {str(e)}")
        
        # Stage 3: Stem Separation (expensive operation)
        stage_start = time.time()
        try:
            logger.info("Stage 3: Audio stem separation")
            stems = self._separate_audio_stems(audio_path, result)
            result.stems = stems
            
            result.metadata.add_processing_stage(ProcessingMetrics(
                stage_name="stem_separation",
                status=ProcessingStatus.COMPLETED,
                start_time=datetime.now(),
                end_time=datetime.now(),
                duration_seconds=time.time() - stage_start,
                confidence_score=0.8
            ))
            
        except Exception as e:
            logger.warning(f"Stem separation failed: {str(e)}")
            # Continue without stems
        
        # Stage 4: Per-Stem Analysis (extract everything from each stem)
        if result.stems:
            stage_start = time.time()
            try:
                logger.info("Stage 4: Per-stem deep analysis")
                self._analyze_individual_stems(result)
                
                result.metadata.add_processing_stage(ProcessingMetrics(
                    stage_name="per_stem_analysis", 
                    status=ProcessingStatus.COMPLETED,
                    start_time=datetime.now(),
                    end_time=datetime.now(),
                    duration_seconds=time.time() - stage_start
                ))
                
            except Exception as e:
                logger.warning(f"Per-stem analysis failed: {str(e)}")
        
        # Stage 5: MIDI Conversion with Accuracy Validation
        stage_start = time.time()
        try:
            logger.info("Stage 5: MIDI conversion with validation")
            midi_result = self._convert_to_midi_with_validation(result)
            result.midi_data = midi_result['midi_data']
            result.midi_file_path = midi_result['midi_path']
            result.midi_accuracy_score = midi_result['accuracy_score']
            result.validation_passed = midi_result['accuracy_score'] >= self.ACCURACY_THRESHOLD
            
            result.metadata.add_processing_stage(ProcessingMetrics(
                stage_name="midi_conversion",
                status=ProcessingStatus.VALIDATED if result.validation_passed else ProcessingStatus.COMPLETED,
                start_time=datetime.now(),
                end_time=datetime.now(), 
                duration_seconds=time.time() - stage_start,
                accuracy_score=result.midi_accuracy_score
            ))
            
        except Exception as e:
            logger.warning(f"MIDI conversion failed: {str(e)}")
        
        # Stage 6: Cross-Instrument Interaction Analysis
        stage_start = time.time()
        try:
            logger.info("Stage 6: Cross-instrument interaction analysis")
            self._analyze_cross_instrument_interactions(result)
            
            result.metadata.add_processing_stage(ProcessingMetrics(
                stage_name="interaction_analysis",
                status=ProcessingStatus.COMPLETED,
                start_time=datetime.now(),
                end_time=datetime.now(),
                duration_seconds=time.time() - stage_start
            ))
            
        except Exception as e:
            logger.warning(f"Interaction analysis failed: {str(e)}")
        
        # Stage 7: Cleanup (delete stems if MIDI validation passed)
        if result.validation_passed and result.stems:
            logger.info("Stage 7: Cleaning up audio stems (validation passed)")
            self._cleanup_audio_stems(result)
            result.stems_deleted = True
        else:
            logger.info("Keeping audio stems (validation did not pass threshold)")
    
    def _process_midi_file(self, midi_path: Path, result: ProcessingResult):
        """Process MIDI file with comprehensive analysis."""
        logger.info(f"Processing MIDI file: {midi_path.name}")
        
        # Stage 1: MIDI Loading and Basic Analysis
        stage_start = time.time()
        try:
            logger.info("Stage 1: MIDI loading and basic analysis")
            result.midi_data = pretty_midi.PrettyMIDI(str(midi_path))
            result.midi_file_path = str(midi_path)
            
            # Add file reference
            result.metadata.add_file_reference("original_midi", FileReference(
                file_id=result.metadata.file_id,
                file_type=FileType.MIDI,
                file_path=str(midi_path),
                file_size=midi_path.stat().st_size
            ))
            
            result.metadata.add_processing_stage(ProcessingMetrics(
                stage_name="midi_loading",
                status=ProcessingStatus.COMPLETED,
                start_time=datetime.now(),
                end_time=datetime.now(),
                duration_seconds=time.time() - stage_start
            ))
            
        except Exception as e:
            raise RootzEngineError(f"MIDI loading failed: {str(e)}")
        
        # Stage 2: MIDI Quality Analysis
        stage_start = time.time()
        try:
            logger.info("Stage 2: MIDI quality analysis")
            quality_score = self._analyze_midi_quality(result.midi_data)
            
            result.metadata.add_processing_stage(ProcessingMetrics(
                stage_name="midi_quality_analysis",
                status=ProcessingStatus.COMPLETED,
                start_time=datetime.now(),
                end_time=datetime.now(),
                duration_seconds=time.time() - stage_start,
                confidence_score=quality_score
            ))
            
        except Exception as e:
            logger.warning(f"MIDI quality analysis failed: {str(e)}")
        
        # Stage 3: Per-Channel Analysis
        stage_start = time.time()
        try:
            logger.info("Stage 3: Per-channel MIDI analysis")
            self._analyze_midi_channels(result)
            
            result.metadata.add_processing_stage(ProcessingMetrics(
                stage_name="midi_channel_analysis",
                status=ProcessingStatus.COMPLETED,
                start_time=datetime.now(),
                end_time=datetime.now(),
                duration_seconds=time.time() - stage_start
            ))
            
        except Exception as e:
            logger.warning(f"MIDI channel analysis failed: {str(e)}")
        
        # Stage 4: MIDI Standardization (channel mapping)
        stage_start = time.time()
        try:
            logger.info("Stage 4: MIDI standardization")
            standardized_midi = self._standardize_midi_channels(result.midi_data)
            
            # Save standardized MIDI
            output_dir = Path(result.metadata.source_file).parent / "processed"
            output_dir.mkdir(exist_ok=True)
            standardized_path = output_dir / f"{midi_path.stem}_standardized.mid"
            standardized_midi.write(str(standardized_path))
            
            result.metadata.add_file_reference("standardized_midi", FileReference(
                file_id=result.metadata.file_id + "_std",
                file_type=FileType.MIDI_CONVERTED,
                file_path=str(standardized_path)
            ))
            
            result.metadata.add_processing_stage(ProcessingMetrics(
                stage_name="midi_standardization",
                status=ProcessingStatus.COMPLETED,
                start_time=datetime.now(),
                end_time=datetime.now(),
                duration_seconds=time.time() - stage_start
            ))
            
        except Exception as e:
            logger.warning(f"MIDI standardization failed: {str(e)}")
        
        # Set high accuracy for MIDI files (they're already MIDI)
        result.midi_accuracy_score = 1.0
        result.validation_passed = True
    
    def _separate_audio_stems(self, audio_path: Path, result: ProcessingResult) -> Dict[str, str]:
        """Separate audio into stems and return file paths."""
        output_dir = audio_path.parent / "stems" / audio_path.stem
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Perform stem separation (simplified - would use actual implementation)
        stems = {}
        
        # Mock separation - in real implementation would use Demucs or similar
        y, sr = librosa.load(str(audio_path), sr=self.config.audio.sample_rate)
        
        # Simulate different stems (in real implementation, these would be actual separated audio)
        stem_names = ['bass', 'drums', 'guitar', 'other']
        
        for stem_name in stem_names:
            stem_path = output_dir / f"{stem_name}.wav"
            # Mock: save the same audio for now (real implementation would have separated audio)
            librosa.output.write_wav(str(stem_path), y, sr)
            stems[stem_name] = str(stem_path)
            result.temp_files.append(str(stem_path))
            
            # Add file reference
            result.metadata.add_file_reference(f"stem_{stem_name}", FileReference(
                file_id=f"{result.metadata.file_id}_{stem_name}",
                file_type=FileType.AUDIO_STEM,
                file_path=str(stem_path)
            ))
        
        return stems
    
    def _extract_spectrotone_analysis(self, audio_path: str, audio_features: Dict) -> Dict[str, SpectrotoneAnalysis]:
        """Extract spectrotone analysis from audio."""
        # Mock spectrotone analysis - would use actual spectrotone library
        spectrotone_data = {}
        
        # Example spectrotone analysis for detected instruments
        detected_instruments = ['bass', 'guitar', 'drums', 'organ']
        
        for instrument in detected_instruments:
            spectrotone_data[instrument] = SpectrotoneAnalysis(
                instrument=instrument,
                primary_color=self._get_instrument_color(instrument),
                secondary_color="grey",
                timbre=self._get_instrument_timbre(instrument),
                brightness=np.random.uniform(0.2, 0.8),
                weight=np.random.uniform(0.4, 0.9), 
                resonance=np.random.uniform(0.3, 0.9),
                harmonic_content={
                    "fundamental": 0.8,
                    "2nd_harmonic": 0.6,
                    "3rd_harmonic": 0.4,
                    "4th_harmonic": 0.2
                },
                temporal_evolution=[]  # Would contain time-varying spectrotone data
            )
        
        return spectrotone_data
    
    def _get_instrument_color(self, instrument: str) -> str:
        """Get primary color for instrument based on spectrotone mapping."""
        color_map = {
            'bass': 'blue',
            'guitar': 'tan', 
            'drums': 'white',
            'organ': 'ivory',
            'piano': 'white'
        }
        return color_map.get(instrument, 'grey')
    
    def _get_instrument_timbre(self, instrument: str) -> str:
        """Get timbre description for instrument."""
        timbre_map = {
            'bass': 'dark',
            'guitar': 'warm',
            'drums': 'percussive',
            'organ': 'hollow',
            'piano': 'neutral'
        }
        return timbre_map.get(instrument, 'neutral')
    
    def _analyze_individual_stems(self, result: ProcessingResult):
        """Perform deep analysis on each separated stem."""
        for stem_name, stem_path in result.stems.items():
            try:
                # Extract features from individual stem
                stem_features = self.feature_extractor.extract_all_features(stem_path)
                
                # Map stem to MIDI channel
                channel = map_audio_stem_to_channel(stem_name)
                if channel is None:
                    continue
                
                # Create instrument analysis
                instrument_analysis = InstrumentAnalysis(
                    channel=channel,
                    instrument=stem_name,
                    note_range=self._estimate_note_range(stem_features),
                    velocity_curve=self._extract_velocity_curve(stem_features),
                    timing_variations=self._analyze_timing_variations(stem_features),
                    playing_patterns=self._identify_playing_patterns(stem_name, stem_features),
                    harmonic_function=self._determine_harmonic_function(stem_name),
                    interaction_patterns={},  # Will be filled in cross-analysis
                    behavioral_traits=self._extract_behavioral_traits(stem_name, stem_features),
                    spectrotone=result.spectrotone_data.get(stem_name, SpectrotoneAnalysis(
                        instrument=stem_name,
                        primary_color=self._get_instrument_color(stem_name),
                        secondary_color="grey",
                        timbre=self._get_instrument_timbre(stem_name),
                        brightness=0.5,
                        weight=0.5,
                        resonance=0.5,
                        harmonic_content={},
                        temporal_evolution=[]
                    )),
                    midi_events_count=0,  # Will be updated after MIDI conversion
                    dominant_rhythmic_pattern=self._identify_rhythmic_pattern(stem_features)
                )
                
                result.metadata.add_channel_analysis(channel, instrument_analysis)
                
            except Exception as e:
                logger.warning(f"Failed to analyze stem {stem_name}: {str(e)}")
    
    def _estimate_note_range(self, features: Dict) -> Tuple[int, int]:
        """Estimate MIDI note range from audio features."""
        # Mock implementation - would use pitch detection
        return (40, 80)  # Default range
    
    def _extract_velocity_curve(self, features: Dict) -> List[int]:
        """Extract velocity curve from audio features."""
        # Mock implementation - would analyze RMS energy
        return [64, 72, 68, 75, 70, 80, 65, 77]  # Example velocity curve
    
    def _analyze_timing_variations(self, features: Dict) -> Dict[str, float]:
        """Analyze timing variations in the audio."""
        return {
            "ahead_beat": 0.01,
            "behind_beat": 0.02,
            "average_deviation": 0.015
        }
    
    def _identify_playing_patterns(self, instrument: str, features: Dict) -> List[str]:
        """Identify playing patterns for the instrument."""
        pattern_map = {
            'bass': ['root_emphasis', 'walking_bass'],
            'guitar': ['upstroke_emphasis', 'chord_damping'],
            'drums': ['one_drop', 'ghost_notes'],
            'organ': ['sustained_chords', 'bubble_rhythm']
        }
        return pattern_map.get(instrument, ['standard'])
    
    def _determine_harmonic_function(self, instrument: str) -> str:
        """Determine harmonic function of the instrument."""
        function_map = {
            'bass': 'root_provider',
            'guitar': 'rhythm_provider',
            'organ': 'harmonic_support',
            'piano': 'chord_provider',
            'drums': 'rhythm_foundation'
        }
        return function_map.get(instrument, 'support')
    
    def _extract_behavioral_traits(self, instrument: str, features: Dict) -> Dict[str, float]:
        """Extract behavioral traits for the instrument."""
        # Mock implementation - would analyze actual features
        base_traits = {
            'bass': {'root_emphasis': 0.9, 'walking_tendency': 0.3},
            'guitar': {'upstroke_emphasis': 0.9, 'chord_damping': 0.8},
            'drums': {'one_drop_tendency': 0.9, 'ghost_notes': 0.6},
            'organ': {'sustained_chords': 0.9, 'bubble_rhythm': 0.6}
        }
        return base_traits.get(instrument, {'standard': 0.5})
    
    def _identify_rhythmic_pattern(self, features: Dict) -> str:
        """Identify dominant rhythmic pattern."""
        # Mock implementation - would analyze rhythm features
        return "one_drop"  # Default for reggae
    
    def _convert_to_midi_with_validation(self, result: ProcessingResult) -> Dict[str, Any]:
        """Convert audio to MIDI with accuracy validation."""
        # Mock MIDI conversion - would use actual converter
        midi_data = pretty_midi.PrettyMIDI()
        
        # Create basic MIDI from analysis
        for channel, analysis in result.metadata.per_channel_analysis.items():
            instrument = pretty_midi.Instrument(program=0, is_drum=(channel == 10))
            
            # Add some notes based on analysis
            for i in range(4):  # 4 quarter notes
                note = pretty_midi.Note(
                    velocity=analysis.velocity_curve[0] if analysis.velocity_curve else 64,
                    pitch=analysis.note_range[0] + 12,  # Root note
                    start=i * 0.5,
                    end=(i + 1) * 0.5
                )
                instrument.notes.append(note)
            
            midi_data.instruments.append(instrument)
        
        # Save MIDI file
        output_dir = Path(result.metadata.source_file).parent / "processed"
        output_dir.mkdir(exist_ok=True)
        midi_path = output_dir / f"{Path(result.metadata.source_file).stem}_converted.mid"
        midi_data.write(str(midi_path))
        
        # Add file reference
        result.metadata.add_file_reference("converted_midi", FileReference(
            file_id=result.metadata.file_id + "_midi",
            file_type=FileType.MIDI_CONVERTED,
            file_path=str(midi_path)
        ))
        
        # Mock accuracy validation - would compare against original audio
        accuracy_score = 0.87  # Mock high accuracy
        
        return {
            'midi_data': midi_data,
            'midi_path': str(midi_path),
            'accuracy_score': accuracy_score
        }
    
    def _analyze_midi_quality(self, midi_data: pretty_midi.PrettyMIDI) -> float:
        """Analyze MIDI file quality."""
        # Mock quality analysis - would implement actual quality metrics
        quality_factors = []
        
        # Check for realistic velocities
        all_velocities = []
        for instrument in midi_data.instruments:
            all_velocities.extend([note.velocity for note in instrument.notes])
        
        if all_velocities:
            velocity_variance = np.var(all_velocities)
            quality_factors.append(min(velocity_variance / 500.0, 1.0))  # Normalize
        
        # Check for timing humanization
        timing_quality = 0.8  # Mock value
        quality_factors.append(timing_quality)
        
        return np.mean(quality_factors) if quality_factors else 0.5
    
    def _analyze_midi_channels(self, result: ProcessingResult):
        """Analyze individual MIDI channels."""
        for instrument in result.midi_data.instruments:
            if not instrument.notes:
                continue
            
            channel = instrument.program + 1  # Convert to 1-based channel
            if instrument.is_drum:
                channel = 10  # Standard drum channel
            
            # Analyze notes
            velocities = [note.velocity for note in instrument.notes]
            pitches = [note.pitch for note in instrument.notes]
            
            # Create analysis
            analysis = InstrumentAnalysis(
                channel=channel,
                instrument=f"midi_instrument_{instrument.program}",
                note_range=(min(pitches), max(pitches)) if pitches else (60, 72),
                velocity_curve=velocities[:8] if len(velocities) >= 8 else velocities,
                timing_variations={"average_deviation": 0.01},
                playing_patterns=["midi_pattern"],
                harmonic_function="midi_function",
                interaction_patterns={},
                behavioral_traits={"midi_trait": 0.5},
                spectrotone=SpectrotoneAnalysis(
                    instrument=f"midi_instrument_{instrument.program}",
                    primary_color="grey",
                    secondary_color="white",
                    timbre="synthetic",
                    brightness=0.5,
                    weight=0.5,
                    resonance=0.5,
                    harmonic_content={},
                    temporal_evolution=[]
                ),
                midi_events_count=len(instrument.notes),
                dominant_rhythmic_pattern="midi_rhythm"
            )
            
            result.metadata.add_channel_analysis(channel, analysis)
    
    def _standardize_midi_channels(self, midi_data: pretty_midi.PrettyMIDI) -> pretty_midi.PrettyMIDI:
        """Standardize MIDI channels according to reggae mapping."""
        # Create new MIDI with standardized channels
        standardized = pretty_midi.PrettyMIDI()
        
        # Map instruments to standard channels
        for instrument in midi_data.instruments:
            # Determine target channel based on instrument type
            target_channel = self._map_instrument_to_standard_channel(instrument)
            
            if target_channel:
                new_instrument = pretty_midi.Instrument(
                    program=instrument.program,
                    is_drum=instrument.is_drum,
                    name=f"standardized_{target_channel}"
                )
                new_instrument.notes = instrument.notes.copy()
                standardized.instruments.append(new_instrument)
        
        return standardized
    
    def _map_instrument_to_standard_channel(self, instrument: pretty_midi.Instrument) -> Optional[int]:
        """Map MIDI instrument to standardized channel."""
        if instrument.is_drum:
            return self.channel_mapping.DRUMS_FULL_KIT_CHANNEL
        
        # Map based on program number
        program_map = {
            32: self.channel_mapping.BASS_CHANNEL,      # Acoustic Bass
            33: self.channel_mapping.BASS_CHANNEL,      # Electric Bass
            25: self.channel_mapping.RHYTHM_GUITAR_CHANNEL,  # Acoustic Guitar
            27: self.channel_mapping.RHYTHM_GUITAR_CHANNEL,  # Electric Guitar
            16: self.channel_mapping.ORGAN_CHANNEL,     # Organ
            0: self.channel_mapping.PIANO_CHANNEL       # Piano
        }
        
        return program_map.get(instrument.program)
    
    def _analyze_cross_instrument_interactions(self, result: ProcessingResult):
        """Analyze interactions between instruments."""
        if len(result.metadata.per_channel_analysis) < 2:
            return
        
        # Mock cross-channel analysis
        relationships = CrossChannelRelationships(
            bass_drum_lock=0.95,
            harmonic_coherence=0.85,
            rhythmic_subdivision="16th_note",
            groove_pocket=0.88,
            dynamic_correlation={"bass_drums": 0.9, "guitar_organ": 0.7},
            call_response_patterns=[]
        )
        
        result.metadata.set_cross_channel_relationships(relationships)
        
        # Create groove template
        groove = GrooveTemplate(
            riddim_type="one_drop",
            tempo_bpm=result.audio_features.get('rhythm', {}).get('tempo', 120) if result.audio_features else 120,
            tempo_stability=0.95,
            key_signature="C",
            mode="major",
            time_signature="4/4",
            micro_timing_signature=[0.0, -0.01, 0.02, -0.005],
            dynamic_arc="verse_quiet_chorus_loud",
            section_structure=["intro", "verse", "chorus", "verse", "chorus", "outro"],
            harmonic_rhythm=2.0  # Chord changes every 2 beats
        )
        
        result.metadata.set_groove_template(groove)
    
    def _cross_modal_validation(self, result: ProcessingResult):
        """Perform cross-modal validation between audio and MIDI."""
        # Compare audio features with MIDI characteristics
        if result.audio_features and result.midi_data:
            # Mock validation - would implement actual comparison
            audio_tempo = result.audio_features.get('rhythm', {}).get('tempo', 120)
            midi_tempo = 120  # Would extract from MIDI
            
            tempo_accuracy = 1.0 - abs(audio_tempo - midi_tempo) / max(audio_tempo, midi_tempo)
            
            # Update accuracy score based on cross-modal validation
            if result.midi_accuracy_score:
                result.midi_accuracy_score = (result.midi_accuracy_score + tempo_accuracy) / 2
    
    def _generate_ai_training_features(self, result: ProcessingResult):
        """Generate features optimized for AI agent training."""
        # Mock AI training feature generation
        training_features = AITrainingFeatures(
            spectrotone_vectors={
                str(ch): [0.1, 0.2, 0.3, 0.4, 0.5] 
                for ch in result.metadata.per_channel_analysis.keys()
            },
            harmonic_progression_vectors=[[1, 0, 0, 1], [0, 1, 0, 0]],  # Mock chord vectors
            rhythmic_pattern_vectors={
                ch: [0.9, 0.1, 0.0, 0.8] for ch in result.metadata.per_channel_analysis.keys()
            },
            instrumental_behavior_vectors={
                ch: [0.8, 0.6, 0.4, 0.9] for ch in result.metadata.per_channel_analysis.keys()
            },
            interaction_matrices={"rhythmic": [[1.0, 0.8], [0.8, 1.0]]},
            groove_context_vectors=[0.9, 0.8, 0.7, 0.95]
        )
        
        result.metadata.set_ai_training_features(training_features)
    
    def _cleanup_audio_stems(self, result: ProcessingResult):
        """Clean up audio stems after successful MIDI validation."""
        for stem_path in result.stems.values():
            try:
                Path(stem_path).unlink()
                logger.info(f"Deleted audio stem: {stem_path}")
            except Exception as e:
                logger.warning(f"Failed to delete stem {stem_path}: {str(e)}")
        
        # Clean up temporary files
        for temp_file in result.temp_files:
            try:
                Path(temp_file).unlink()
            except Exception as e:
                logger.warning(f"Failed to delete temp file {temp_file}: {str(e)}")
    
    def cleanup_result(self, result: ProcessingResult):
        """Clean up any remaining temporary files from processing."""
        for temp_file in result.temp_files:
            try:
                if Path(temp_file).exists():
                    Path(temp_file).unlink()
            except Exception as e:
                logger.warning(f"Failed to clean up {temp_file}: {str(e)}")


def create_processing_pipeline(config: Optional[RootzEngineConfig] = None) -> UnifiedProcessingPipeline:
    """Factory function to create a processing pipeline."""
    return UnifiedProcessingPipeline(config)