"""Audio structure analysis module."""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Union

import librosa
import librosa.display
import numpy as np
import msaf
from madmom.features import beats
from madmom.features.downbeats import DBNDownBeatTrackingProcessor, RNNDownBeatProcessor

from src.rootzengine.audio.features import extract_features
from src.rootzengine.audio.reggae_patterns import ReggaePatternDetector
from src.rootzengine.audio.separation import separate_stems
from src.rootzengine.core.config import settings
from src.rootzengine.core.exceptions import AudioProcessingError, StemSeparationError

logger = logging.getLogger(__name__)


class AudioStructureAnalyzer:
    """Analyzes the structure of audio files, identifying musical sections and features."""
    
    def __init__(
        self,
        sample_rate: Optional[int] = None,
        hop_length: Optional[int] = None,
        n_fft: Optional[int] = None,
    ):
        """Initialize the audio structure analyzer.
        
        Args:
            sample_rate: The sample rate to use for analysis, defaults to settings.audio.sample_rate
            hop_length: The hop length for FFT, defaults to settings.audio.hop_length
            n_fft: The FFT window size, defaults to settings.audio.n_fft
        """
        self.sample_rate = sample_rate or settings.audio.sample_rate
        self.hop_length = hop_length or settings.audio.hop_length
        self.n_fft = n_fft or settings.audio.n_fft
        
        # Initialize specialized detectors
        self.reggae_detector = ReggaePatternDetector(sample_rate=self.sample_rate, hop_length=self.hop_length)
    
    def analyze_structure(self, audio_path: Union[str, Path], perform_separation: bool = False) -> Dict:
        """Analyze the structure of an audio file.
        
        Args:
            audio_path: Path to the audio file
            perform_separation: If True, separates audio into stems before analysis

        Returns:
            Dictionary containing structured analysis results including:
            - sections: List of detected sections with start/end times and labels
            - tempo: Detected tempo information
            - key: Musical key information
            - energy_profile: Energy analysis data
            - reggae_features: Reggae-specific features
            - stem_paths: Paths to the separated audio stems (if performed)
            
        Raises:
            AudioProcessingError: If audio processing fails
        """
        try:
            # Load audio file
            y, sr = librosa.load(audio_path, sr=self.sample_rate)
            
            # Stem separation (optional)
            separated_stems: Dict[str, np.ndarray] = {}
            stem_paths: Dict[str, str] = {}
            if perform_separation:
                try:
                    logger.info(f"Performing stem separation on {audio_path}...")
                    # Create a dedicated output directory for stems for this audio file
                    stems_output_dir = settings.storage.processed_dir / Path(audio_path).stem / "stems"
                    
                    stem_paths = separate_stems(
                        input_audio_path=str(audio_path),
                        output_dir=str(stems_output_dir)
                    )
                    
                    # Load the audio data from the separated stem files
                    for stem_name, stem_path in stem_paths.items():
                        y_stem, _ = librosa.load(stem_path, sr=self.sample_rate)
                        separated_stems[stem_name] = y_stem
                        
                    logger.info("Stem separation and loading successful.")
                except (StemSeparationError, AudioProcessingError, FileNotFoundError) as e:
                    logger.warning(f"Could not separate stems for {audio_path}: {e}. Continuing analysis on full mix.")


            # Get basic features
            features = extract_features(y, sr, self.hop_length, self.n_fft)
            
            # Detect tempo and beat information
            tempo_data = self._detect_tempo_and_beats(y, sr, audio_path)
            
            # Detect key
            key_data = self._detect_key(y, sr)
            
            # Segment the audio into structural sections
            sections = self._segment_structure(y, sr, features, audio_path)
            
            # Analyze energy profile
            energy_profile = self._analyze_energy(y, sr)
            
            # Detect reggae-specific patterns
            reggae_features = self.reggae_detector.detect_patterns(y, sr, tempo_data, stems=separated_stems)
            
            # Compile results
            result = {
                "sections": sections,
                "tempo": tempo_data,
                "key": key_data,
                "energy_profile": energy_profile,
                "reggae_features": reggae_features,
                "stem_paths": {k: str(v) for k, v in stem_paths.items()}
            }
            
            logger.info(f"Successfully analyzed structure of {audio_path}")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing structure of {audio_path}: {str(e)}")
            raise AudioProcessingError(f"Failed to analyze audio structure: {str(e)}") from e
    
    def _detect_tempo_and_beats(self, y: np.ndarray, sr: int, audio_path: Union[str, Path]) -> Dict:
        """Detect tempo and beat information.
        
        Uses madmom and librosa for robust beat tracking.
        
        Args:
            y: Audio time series
            sr: Sample rate
            audio_path: Path to the audio file for madmom processing
            
        Returns:
            Dictionary with tempo and beat information
        """
        # Use librosa for initial tempo estimate
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr, hop_length=self.hop_length)
        
        # Use madmom for more accurate beat and downbeat detection
        # This is especially important for reggae with its distinctive rhythmic patterns
        proc = beats.BeatTrackingProcessor(fps=100)
        act = beats.RNNBeatProcessor()(audio_path)
        beat_times = proc(act)
        
        # For downbeats (important in reggae for one drop patterns)
        downbeat_proc = DBNDownBeatTrackingProcessor(beats_per_bar=[3, 4], fps=100)
        downbeat_act = RNNDownBeatProcessor()(audio_path)
        downbeats = downbeat_proc(downbeat_act)
        
        # Calculate beat confidence
        beat_confidence = np.mean(act[np.array(beat_times * 100, dtype=int)])
        
        return {
            "bpm": float(tempo),
            "confidence": float(beat_confidence),
            "beat_times": beat_times.tolist(),
            "downbeats": downbeats.tolist()
        }
    
    def _detect_key(self, y: np.ndarray, sr: int) -> Dict:
        """Detect the musical key of the audio.
        
        Args:
            y: Audio time series
            sr: Sample rate
            
        Returns:
            Dictionary with key information
        """
        # Extract chroma features
        chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
        
        # Key detection using chord recognition
        # Typically this would use a dedicated key detection algorithm
        # For now we'll use a simplified approach with chroma profiles
        
        # Map indices to key names (C, C#, D, etc.)
        key_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        mode_names = ['major', 'minor']
        
        # Simple key detection using chroma profile correlation
        key_idx = np.argmax(np.mean(chroma, axis=1))
        
        # Simple mode detection (major/minor)
        # This is simplified; real implementation would use more sophisticated analysis
        major_profile = np.array([1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1])  # Major scale profile
        minor_profile = np.array([1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0])  # Natural minor scale profile
        
        # Rotate profiles to match detected key
        rolled_major = np.roll(major_profile, key_idx)
        rolled_minor = np.roll(minor_profile, key_idx)
        
        # Correlate with chroma
        mean_chroma = np.mean(chroma, axis=1)
        major_corr = np.corrcoef(mean_chroma, rolled_major)[0, 1]
        minor_corr = np.corrcoef(mean_chroma, rolled_minor)[0, 1]
        
        mode_idx = 0 if major_corr > minor_corr else 1
        confidence = max(major_corr, minor_corr)
        
        return {
            "root": key_names[key_idx],
            "mode": mode_names[mode_idx],
            "confidence": float(confidence)
        }
    
    def _segment_structure(
        self, y: np.ndarray, sr: int, features: Dict, audio_path: Union[str, Path]
    ) -> List[Dict]:
        """Segment the audio into structural sections using MSAF with a librosa fallback.
        
        Args:
            y: Audio time series (for fallback)
            sr: Sample rate (for fallback)
            features: Pre-extracted audio features (unused, but kept for signature consistency)
            audio_path: Path to the audio file for MSAF processing
            
        Returns:
            List of section dictionaries with start/end times and labels
        """
        try:
            logger.info(f"Running MSAF segmentation on {audio_path}...")
            # Use MSAF for robust segmentation and labeling.
            boundaries, labels = msaf.process(str(audio_path), boundaries_id="foote", labels_id="sf")
            
            sections = []
            for i, label in enumerate(labels):
                sections.append({
                    "start": float(boundaries[i, 0]),
                    "end": float(boundaries[i, 1]),
                    "label": label,
                    "confidence": 1.0  # MSAF doesn't provide confidence directly
                })
            
            logger.info(f"MSAF found {len(sections)} sections.")
            return sections

        except Exception as e:
            logger.warning(f"MSAF segmentation failed: {e}. Falling back to librosa-based segmentation.")
            # Fallback to librosa's simple segmentation
            # This is a basic approach using a self-similarity matrix
            chroma = librosa.feature.chroma_cqt(y=y, sr=sr, hop_length=self.hop_length)
            # Use 'affinity' for better structural grouping
            sim_matrix = librosa.segment.recurrence_matrix(chroma, mode='affinity', sparse=True)
            
            # Find segment boundaries using a target number of segments (e.g., 10)
            # This is a simple heuristic; more advanced methods could be used.
            boundaries_frames = librosa.segment.agglomerative(sim_matrix, k=10)
            boundary_times = librosa.frames_to_time(boundaries_frames, sr=sr, hop_length=self.hop_length)
            
            # Create sections from boundaries
            sections = []
            start_time = 0.0
            # Ensure boundaries are sorted and unique
            full_boundaries = np.unique(np.concatenate(([start_time], boundary_times, [librosa.get_duration(y=y, sr=sr)])))
            
            for i in range(len(full_boundaries) - 1):
                sections.append({
                    "start": full_boundaries[i],
                    "end": full_boundaries[i+1],
                    "label": f"segment_{i+1}", # Librosa doesn't label
                    "confidence": 0.5 # Lower confidence for fallback method
                })
            
            return sections
    
    def _analyze_energy(self, y: np.ndarray, sr: int) -> Dict:
        """Analyze the energy profile of the audio.
        
        Args:
            y: Audio time series
            sr: Sample rate
            
        Returns:
            Dictionary with energy analysis results
        """
        # RMS energy
        rms = librosa.feature.rms(y=y, hop_length=self.hop_length)[0]
        
        # Spectral centroid - brightness
        cent = librosa.feature.spectral_centroid(y=y, sr=sr, hop_length=self.hop_length)[0]
        
        # Zero crossing rate - noisiness/percussiveness
        zcr = librosa.feature.zero_crossing_rate(y, hop_length=self.hop_length)[0]
        
        # Convert to time domain
        times = librosa.times_like(rms, sr=sr, hop_length=self.hop_length)
        
        # Compute statistics
        return {
            "rms_mean": float(np.mean(rms)),
            "rms_std": float(np.std(rms)),
            "spectral_centroid_mean": float(np.mean(cent)),
            "zero_crossing_rate_mean": float(np.mean(zcr)),
            "dynamic_range": float(np.max(rms) - np.min(rms)),
            "profile": {
                "times": times.tolist(),
                "rms": rms.tolist(),
                "spectral_centroid": cent.tolist(),
                "zero_crossing_rate": zcr.tolist()
            }
        }
