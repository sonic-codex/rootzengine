"""Implementation of reggae-specific pattern detection."""

import logging
from typing import Dict, List, Optional, Tuple

import librosa
import numpy as np

from src.rootzengine.core.config import settings
from src.rootzengine.core.exceptions import AudioProcessingError

logger = logging.getLogger(__name__)


class ReggaePatternDetector:
    """Detector for reggae-specific musical patterns."""
    
    def __init__(
        self,
        sample_rate: Optional[int] = None,
        hop_length: Optional[int] = None,
    ):
        """Initialize the reggae pattern detector.
        
        Args:
            sample_rate: The sample rate to use for analysis
            hop_length: The hop length for FFT
        """
        self.sample_rate = sample_rate or settings.audio.sample_rate
        self.hop_length = hop_length or settings.audio.hop_length
        
        # Pattern definitions
        self.patterns = {
            "one_drop": {
                "description": "Emphasis on beat 3, silence on beat 1",
                "beats": [0, 0, 1, 0]  # Simplified pattern representation
            },
            "steppers": {
                "description": "Four-to-the-floor kick pattern",
                "beats": [1, 0, 1, 0]  # Simplified pattern representation
            },
            "rockers": {
                "description": "Emphasis on beats 1 and 3",
                "beats": [1, 0, 1, 0]  # Simplified pattern representation
            },
            "heartbeat": {
                "description": "Emphasis on beats 1 and 2+",
                "beats": [1, 0.5, 0, 0]  # Simplified pattern representation
            }
        }
    
    def detect_patterns(self, audio_path: str) -> Dict:
        """Detect reggae patterns in an audio file.
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            Dictionary containing detected patterns and confidence scores
        """
        try:
            # Load audio
            y, sr = librosa.load(audio_path, sr=self.sample_rate)
            
            # Low-pass filter to focus on bass frequencies
            y_bass = librosa.effects.preemphasis(y, coef=0.95, zi=None)
            
            # Detect overall tempo and beats
            tempo, beat_frames = librosa.beat.beat_track(
                y=y, sr=sr, hop_length=self.hop_length
            )
            
            # Detect downbeats (first beat of each measure)
            # In a real implementation, this would use more sophisticated algorithms
            # Here we'll simulate by taking every 4th beat
            downbeats = beat_frames[::4]
            
            # Calculate onset envelope focused on drum frequencies
            onset_env = librosa.onset.onset_strength(
                y=y, sr=sr, hop_length=self.hop_length
            )
            
            # Analyze onset patterns relative to beats
            riddim_type = self._analyze_riddim_pattern(
                y, sr, beat_frames, onset_env
            )
            
            # Detect skank pattern (guitar/keys offbeat pattern)
            skank_pattern = self._detect_skank_pattern(
                y, sr, beat_frames, onset_env
            )
            
            # Analyze bass complexity
            bass_complexity = self._analyze_bass_complexity(y_bass, sr)
            
            return {
                "riddim_type": riddim_type,
                "skank_pattern": skank_pattern,
                "bass_line_complexity": float(bass_complexity)
            }
            
        except Exception as e:
            logger.error(f"Error detecting reggae patterns: {str(e)}")
            raise AudioProcessingError(
                f"Failed to detect reggae patterns: {str(e)}"
            ) from e
    
    def _analyze_riddim_pattern(
        self,
        y: np.ndarray,
        sr: int,
        beat_frames: np.ndarray,
        onset_env: np.ndarray
    ) -> str:
        """Analyze the drum pattern to determine riddim type.
        
        Args:
            y: Audio time series
            sr: Sample rate
            beat_frames: Beat frames
            onset_env: Onset strength envelope
            
        Returns:
            The detected riddim type
        """
        # Extract low frequency content for kick drum detection
        y_harmonic, y_percussive = librosa.effects.hpss(y)
        
        # Focus on low-frequency percussive content (kick drum)
        spec = np.abs(librosa.stft(y_percussive, hop_length=self.hop_length))
        spec_low = spec[:10, :]  # Focus on low frequencies
        
        # Analyze kick drum pattern relative to beats
        beat_onset_strengths = []
        for beat in beat_frames:
            if beat < onset_env.shape[0]:
                # Get onset strength in window around beat
                window_size = 2  # +/- frames around beat
                start = max(0, beat - window_size)
                end = min(onset_env.shape[0], beat + window_size + 1)
                beat_onset_strengths.append(np.max(onset_env[start:end]))
            else:
                beat_onset_strengths.append(0)
        
        # Group beats into measures (assuming 4/4 time signature)
        measure_patterns = []
        for i in range(0, len(beat_onset_strengths) - 3, 4):
            measure = beat_onset_strengths[i:i+4]
            if len(measure) == 4:
                measure_patterns.append(measure)
        
        # Analyze patterns
        pattern_scores = {}
        
        if len(measure_patterns) > 0:
            # Average across measures
            avg_pattern = np.mean(measure_patterns, axis=0)
            
            # Normalize pattern
            if np.sum(avg_pattern) > 0:
                avg_pattern = avg_pattern / np.max(avg_pattern)
            
            # Compare with known patterns
            for pattern_name, pattern_info in self.patterns.items():
                # Calculate correlation with ideal pattern
                ideal_pattern = np.array(pattern_info["beats"])
                correlation = np.corrcoef(avg_pattern, ideal_pattern)[0, 1]
                pattern_scores[pattern_name] = max(0, correlation)  # Ensure non-negative
        
        # Return the highest scoring pattern
        if pattern_scores:
            return max(pattern_scores.items(), key=lambda x: x[1])[0]
        else:
            return "unknown"
    
    def _detect_skank_pattern(
        self,
        y: np.ndarray,
        sr: int,
        beat_frames: np.ndarray,
        onset_env: np.ndarray
    ) -> str:
        """Detect the guitar/keys skank pattern.
        
        Args:
            y: Audio time series
            sr: Sample rate
            beat_frames: Beat frames
            onset_env: Onset strength envelope
            
        Returns:
            The detected skank pattern type
        """
        # In reggae, skanks typically occur on the offbeats (the "and" of each beat)
        # We'll detect activity between beats
        
        # Create frames for offbeats (halfway between beats)
        offbeat_frames = []
        for i in range(len(beat_frames) - 1):
            offbeat = (beat_frames[i] + beat_frames[i + 1]) // 2
            offbeat_frames.append(offbeat)
        
        offbeat_frames = np.array(offbeat_frames)
        
        # Analyze onset strengths at offbeats
        offbeat_strengths = []
        for offbeat in offbeat_frames:
            if offbeat < onset_env.shape[0]:
                window_size = 2  # +/- frames around offbeat
                start = max(0, offbeat - window_size)
                end = min(onset_env.shape[0], offbeat + window_size + 1)
                offbeat_strengths.append(np.max(onset_env[start:end]))
            else:
                offbeat_strengths.append(0)
        
        # Analyze pattern of offbeats
        if len(offbeat_strengths) > 8:
            # Calculate mean and std of offbeat strengths
            mean_strength = np.mean(offbeat_strengths)
            std_strength = np.std(offbeat_strengths)
            
            # Simple pattern classification
            if mean_strength > 0.5 and std_strength < 0.2:
                return "traditional"  # Consistent offbeat skanks
            elif mean_strength > 0.3:
                return "complex"  # Some offbeat activity but varied
            else:
                return "minimal"  # Little offbeat activity
        else:
            return "unknown"  # Not enough data
    
    def _analyze_bass_complexity(self, y_bass: np.ndarray, sr: int) -> float:
        """Analyze the complexity of the bass line.
        
        Args:
            y_bass: Bass-filtered audio time series
            sr: Sample rate
            
        Returns:
            A float indicating bass line complexity (0-1)
        """
        # Extract pitch content
        chroma = librosa.feature.chroma_cqt(y=y_bass, sr=sr)
        
        # Calculate pitch variability
        pitch_variety = np.mean(np.std(chroma, axis=1))
        
        # Calculate note density using onset detection on bass
        onset_env = librosa.onset.onset_strength(
            y=y_bass, sr=sr, hop_length=self.hop_length
        )
        onsets = librosa.onset.onset_detect(
            onset_envelope=onset_env, sr=sr, hop_length=self.hop_length
        )
        note_density = len(onsets) / (len(y_bass) / sr)  # Notes per second
        
        # Normalize and combine factors
        pitch_score = min(1.0, pitch_variety * 5)  # Scale up, cap at 1.0
        density_score = min(1.0, note_density / 4.0)  # Assuming 4 notes/sec is complex
        
        complexity = 0.6 * pitch_score + 0.4 * density_score
        return complexity
