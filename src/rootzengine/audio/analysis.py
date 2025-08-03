"""Audio structure analysis module."""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Union

import librosa
import librosa.display
import numpy as np
from madmom.features import beats
from madmom.features.downbeats import DBNDownBeatTrackingProcessor, RNNDownBeatProcessor

from src.rootzengine.audio.features import extract_features
from src.rootzengine.core.config import settings
from src.rootzengine.core.exceptions import AudioProcessingError

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
        
        # Initialize section detection models
        # Typically this would load or create models for section classification
    
    def analyze_structure(self, audio_path: Union[str, Path]) -> Dict:
        """Analyze the structure of an audio file.
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            Dictionary containing structured analysis results including:
            - sections: List of detected sections with start/end times and labels
            - tempo: Detected tempo information
            - key: Musical key information
            - energy_profile: Energy analysis data
            - reggae_features: Reggae-specific features
            
        Raises:
            AudioProcessingError: If audio processing fails
        """
        try:
            # Load audio file
            y, sr = librosa.load(audio_path, sr=self.sample_rate)
            
            # Get basic features
            features = extract_features(y, sr, self.hop_length, self.n_fft)
            
            # Detect tempo and beat information
            tempo_data = self._detect_tempo_and_beats(y, sr)
            
            # Detect key
            key_data = self._detect_key(y, sr)
            
            # Segment the audio into structural sections
            sections = self._segment_structure(y, sr, features)
            
            # Analyze energy profile
            energy_profile = self._analyze_energy(y, sr)
            
            # Detect reggae-specific patterns
            reggae_features = self._detect_reggae_patterns(y, sr, tempo_data)
            
            # Compile results
            result = {
                "sections": sections,
                "tempo": tempo_data,
                "key": key_data,
                "energy_profile": energy_profile,
                "reggae_features": reggae_features
            }
            
            logger.info(f"Successfully analyzed structure of {audio_path}")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing structure of {audio_path}: {str(e)}")
            raise AudioProcessingError(f"Failed to analyze audio structure: {str(e)}") from e
    
    def _detect_tempo_and_beats(self, y: np.ndarray, sr: int) -> Dict:
        """Detect tempo and beat information.
        
        Uses madmom and librosa for robust beat tracking.
        
        Args:
            y: Audio time series
            sr: Sample rate
            
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
        self, y: np.ndarray, sr: int, features: Dict
    ) -> List[Dict]:
        """Segment the audio into structural sections.
        
        Args:
            y: Audio time series
            sr: Sample rate
            features: Pre-extracted audio features
            
        Returns:
            List of section dictionaries with start/end times and labels
        """
        # Calculate self-similarity matrix
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13, hop_length=self.hop_length)
        S = librosa.segment.recurrence_matrix(mfccs, mode='affinity')
        
        # Detect segment boundaries
        boundaries = librosa.segment.agglomerative(S, 10)
        boundary_times = librosa.frames_to_time(boundaries, sr=sr, hop_length=self.hop_length)
        
        # For a real implementation, we'd have a trained model to classify these sections
        # For now, use a simplified approach that assigns generic labels
        section_labels = ["intro", "verse", "chorus", "bridge", "outro"]
        
        sections = []
        for i in range(len(boundary_times) - 1):
            start_time = boundary_times[i]
            end_time = boundary_times[i + 1]
            
            # Simplified section labeling - in reality would use a classifier
            # This assigns labels in a repeating pattern with some confidence scores
            label_idx = i % len(section_labels)
            
            # Fake confidence score - decreases as we go further in the song
            # In a real model, this would be the classifier's confidence
            confidence = 0.95 - (i * 0.02)
            confidence = max(0.6, confidence)  # Keep it above 0.6
            
            sections.append({
                "start": float(start_time),
                "end": float(end_time),
                "label": section_labels[label_idx],
                "confidence": float(confidence)
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
    
    def _detect_reggae_patterns(self, y: np.ndarray, sr: int, tempo_data: Dict) -> Dict:
        """Detect reggae-specific musical patterns.
        
        Args:
            y: Audio time series
            sr: Sample rate
            tempo_data: Tempo and beat information
            
        Returns:
            Dictionary with reggae pattern analysis
        """
        # For a real implementation, this would contain specialized detection algorithms
        # for reggae patterns like one drop, steppers, rockers, etc.
        
        # Here's a simplified placeholder that would be replaced with actual detection logic
        # In reality, this would analyze beat patterns in the bass and drum stems
        
        # Placeholder detection logic:
        # 1. For now, assume one-drop if tempo is between 60-80 bpm
        # 2. Assume steppers for faster tempos
        # 3. Add some placeholder complexity scores
        
        tempo = tempo_data["bpm"]
        
        if 60 <= tempo <= 80:
            riddim_type = "one_drop"
            skank_pattern = "traditional"
        elif 80 < tempo <= 100:
            riddim_type = "steppers"
            skank_pattern = "modern"
        else:
            riddim_type = "rockers"
            skank_pattern = "complex"
            
        # Placeholder complexity scores
        bass_complexity = 0.5 + (tempo / 200)  # Simple formula that increases with tempo
        
        return {
            "riddim_type": riddim_type,
            "skank_pattern": skank_pattern,
            "bass_line_complexity": float(bass_complexity)
        }
