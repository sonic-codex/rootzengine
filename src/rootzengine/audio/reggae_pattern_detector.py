"""
Reggae pattern detection functionality.

This module provides comprehensive pattern detection for reggae music,
including drum patterns (one-drop, steppers, rockers), guitar skank patterns,
and bass patterns.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import logging

import numpy as np

try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False

from .reggae_patterns import (
    ReggaePattern,
    detect_pattern_from_beats,
    detect_skank_pattern,
    get_pattern_characteristics,
)

logger = logging.getLogger(__name__)


class ReggaePatternDetector:
    """
    Main class for reggae pattern detection.

    Detects reggae-specific rhythmic patterns including:
    - Drum patterns (one-drop, steppers, rockers)
    - Guitar skank patterns
    - Bass patterns
    - Overall groove characteristics
    """

    def __init__(
        self,
        sample_rate: int = 22050,
        hop_length: int = 512,
        onset_threshold: float = 0.5,
        beat_threshold: float = 0.3,
    ):
        """
        Initialize the pattern detector.

        Args:
            sample_rate: Audio sample rate
            hop_length: Hop length for STFT analysis
            onset_threshold: Threshold for onset detection
            beat_threshold: Threshold for beat detection
        """
        if not LIBROSA_AVAILABLE:
            raise ImportError(
                "librosa is required for pattern detection. "
                "Install it with: pip install librosa"
            )

        self.sample_rate = sample_rate
        self.hop_length = hop_length
        self.onset_threshold = onset_threshold
        self.beat_threshold = beat_threshold

    def detect(self, audio_path: str) -> List[Dict[str, Any]]:
        """
        Detect patterns in an audio file.

        Args:
            audio_path: Path to the audio file to analyze

        Returns:
            List of detected pattern dictionaries
        """
        return detect_reggae_patterns(
            audio_path,
            sample_rate=self.sample_rate,
            hop_length=self.hop_length,
            onset_threshold=self.onset_threshold,
            beat_threshold=self.beat_threshold,
        )

    def detect_from_audio(self, y: np.ndarray, sr: int) -> List[Dict[str, Any]]:
        """
        Detect patterns from audio data.

        Args:
            y: Audio time series
            sr: Sample rate

        Returns:
            List of detected pattern dictionaries
        """
        results = []

        # Detect tempo and beats
        tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr, hop_length=self.hop_length)
        beat_times = librosa.frames_to_time(beat_frames, sr=sr, hop_length=self.hop_length)

        # Convert to beat positions
        if tempo > 0:
            beat_positions = beat_times * (tempo / 60.0)
        else:
            beat_positions = np.arange(len(beat_times))

        # Detect onsets for different frequency ranges
        # Note: librosa.onset.onset_detect passes kwargs to peak_pick
        # peak_pick uses 'delta' parameter (not 'threshold')
        onsets_all = librosa.onset.onset_detect(
            y=y,
            sr=sr,
            hop_length=self.hop_length,
            delta=self.onset_threshold,
            pre_max=0.03 * sr // self.hop_length,  # 30ms
            post_max=0.03 * sr // self.hop_length,  # 30ms
            pre_avg=0.1 * sr // self.hop_length,  # 100ms
            post_avg=0.1 * sr // self.hop_length,  # 100ms
            wait=0.03 * sr // self.hop_length,  # 30ms between peaks
        )
        onset_times = librosa.frames_to_time(onsets_all, sr=sr, hop_length=self.hop_length)

        # Separate frequency bands for kick, snare, hihat detection
        # Low frequencies for kick (roughly 20-200 Hz)
        y_low = librosa.effects.preemphasis(y, coef=0.0)
        onsets_low = librosa.onset.onset_detect(
            y=y_low,
            sr=sr,
            hop_length=self.hop_length,
            delta=self.onset_threshold,
            pre_max=0.03 * sr // self.hop_length,
            post_max=0.03 * sr // self.hop_length,
            pre_avg=0.1 * sr // self.hop_length,
            post_avg=0.1 * sr // self.hop_length,
            wait=0.03 * sr // self.hop_length,
        )
        kick_times = librosa.frames_to_time(onsets_low, sr=sr, hop_length=self.hop_length)

        # Mid frequencies for snare (roughly 200-5000 Hz)
        S = np.abs(librosa.stft(y, hop_length=self.hop_length))
        snare_band = librosa.feature.spectral_contrast(
            S=S, sr=sr, hop_length=self.hop_length
        )[2:4].mean(axis=0)
        onsets_mid = librosa.onset.onset_detect(
            onset_envelope=snare_band,
            sr=sr,
            hop_length=self.hop_length,
            delta=self.onset_threshold,
            pre_max=0.03 * sr // self.hop_length,
            post_max=0.03 * sr // self.hop_length,
            pre_avg=0.1 * sr // self.hop_length,
            post_avg=0.1 * sr // self.hop_length,
            wait=0.03 * sr // self.hop_length,
        )
        snare_times = librosa.frames_to_time(onsets_mid, sr=sr, hop_length=self.hop_length)

        # Convert to beat positions
        if tempo > 0:
            kick_positions = kick_times * (tempo / 60.0)
            snare_positions = snare_times * (tempo / 60.0)
            onset_positions = onset_times * (tempo / 60.0)
        else:
            kick_positions = kick_times
            snare_positions = snare_times
            onset_positions = onset_times

        # Detect drum pattern
        pattern, confidence = detect_pattern_from_beats(
            kick_positions.tolist(),
            snare_positions.tolist(),
            float(tempo),
        )

        results.append({
            "type": "drum_pattern",
            "pattern": pattern.value,
            "name": pattern.name.replace("_", " ").title(),
            "confidence": float(confidence),
            "tempo": float(tempo),
            "characteristics": get_pattern_characteristics(pattern),
            "kick_times": kick_times.tolist(),
            "snare_times": snare_times.tolist(),
        })

        # Detect guitar skank pattern
        if len(onset_positions) > 0:
            skank_pattern, skank_confidence = detect_skank_pattern(
                onset_positions.tolist(),
                float(tempo),
            )

            results.append({
                "type": "guitar_pattern",
                "pattern": skank_pattern,
                "confidence": float(skank_confidence),
                "tempo": float(tempo),
                "onset_times": onset_times.tolist(),
            })

        # Analyze overall groove
        if len(beat_times) > 1:
            beat_intervals = np.diff(beat_times)
            groove_consistency = 1.0 - (np.std(beat_intervals) / np.mean(beat_intervals))

            results.append({
                "type": "groove_analysis",
                "tempo": float(tempo),
                "consistency": float(np.clip(groove_consistency, 0, 1)),
                "beat_times": beat_times.tolist(),
                "time_signature": "4/4",  # Reggae is typically 4/4
            })

        return results


def detect_reggae_patterns(
    audio_path: str,
    sample_rate: int = 22050,
    hop_length: int = 512,
    onset_threshold: float = 0.5,
    beat_threshold: float = 0.3,
) -> List[Dict[str, Any]]:
    """
    Detect reggae patterns in an audio file.

    Args:
        audio_path: Path to the audio file to analyze
        sample_rate: Audio sample rate for analysis
        hop_length: Hop length for STFT
        onset_threshold: Threshold for onset detection
        beat_threshold: Threshold for beat detection

    Returns:
        List of detected pattern dictionaries

    Raises:
        FileNotFoundError: If audio file doesn't exist
        ImportError: If librosa is not available
    """
    if not LIBROSA_AVAILABLE:
        logger.warning("librosa not available, returning empty pattern list")
        return []

    audio_file = Path(audio_path)
    if not audio_file.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    # Load audio
    try:
        y, sr = librosa.load(audio_path, sr=sample_rate)
    except Exception as e:
        logger.error(f"Failed to load audio file {audio_path}: {e}")
        return []

    # Create detector and analyze
    detector = ReggaePatternDetector(
        sample_rate=sample_rate,
        hop_length=hop_length,
        onset_threshold=onset_threshold,
        beat_threshold=beat_threshold,
    )

    return detector.detect_from_audio(y, sr)


def analyze_riddim_structure(
    audio_path: str,
    sample_rate: int = 22050,
) -> Dict[str, Any]:
    """
    Analyze the riddim (rhythm) structure of a reggae track.

    Args:
        audio_path: Path to the audio file
        sample_rate: Sample rate for analysis

    Returns:
        Dictionary containing riddim analysis
    """
    if not LIBROSA_AVAILABLE:
        return {"error": "librosa not available"}

    audio_file = Path(audio_path)
    if not audio_file.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    try:
        y, sr = librosa.load(audio_path, sr=sample_rate)
    except Exception as e:
        logger.error(f"Failed to load audio file: {e}")
        return {"error": str(e)}

    # Detect tempo and beats
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    beat_times = librosa.frames_to_time(beat_frames, sr=sr)

    # Analyze tempo stability
    if len(beat_frames) > 1:
        beat_intervals = np.diff(beat_times)
        tempo_stability = 1.0 - (np.std(beat_intervals) / np.mean(beat_intervals))
    else:
        tempo_stability = 0.0

    # Detect patterns
    patterns = detect_reggae_patterns(audio_path, sample_rate=sample_rate)

    # Extract primary pattern
    drum_patterns = [p for p in patterns if p.get("type") == "drum_pattern"]
    primary_pattern = drum_patterns[0] if drum_patterns else None

    return {
        "tempo": float(tempo),
        "tempo_stability": float(np.clip(tempo_stability, 0, 1)),
        "duration": float(len(y) / sr),
        "num_beats": int(len(beat_frames)),
        "primary_pattern": primary_pattern["pattern"] if primary_pattern else "unknown",
        "pattern_confidence": primary_pattern["confidence"] if primary_pattern else 0.0,
        "all_patterns": patterns,
    }


__all__ = [
    "ReggaePatternDetector",
    "detect_reggae_patterns",
    "analyze_riddim_structure",
]
