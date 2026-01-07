"""
Audio structure analysis for reggae music.

This module provides comprehensive analysis of audio structure including
sections, chord progressions, harmonic analysis, and structural boundaries.
"""

from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

import numpy as np

try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False

from .reggae_pattern_detector import detect_reggae_patterns

logger = logging.getLogger(__name__)


class AudioStructureAnalyzer:
    """
    Analyzes the structure of audio files, particularly for reggae music.

    Provides analysis of:
    - Section boundaries (intro, verse, chorus, bridge, outro)
    - Harmonic content and chord progressions
    - Tempo and rhythmic structure
    - Energy levels across sections
    """

    def __init__(
        self,
        sample_rate: int = 22050,
        hop_length: int = 512,
        n_fft: int = 2048,
    ):
        """
        Initialize the structure analyzer.

        Args:
            sample_rate: Audio sample rate
            hop_length: Hop length for STFT
            n_fft: FFT window size
        """
        if not LIBROSA_AVAILABLE:
            raise ImportError(
                "librosa is required for audio analysis. "
                "Install it with: pip install librosa"
            )

        self.sample_rate = sample_rate
        self.hop_length = hop_length
        self.n_fft = n_fft

    def analyze_structure(
        self,
        audio_path: str,
        perform_separation: bool = False,
    ) -> Dict[str, Any]:
        """
        Analyze the structure of an audio file.

        Args:
            audio_path: Path to the audio file
            perform_separation: Whether to perform stem separation (not implemented)

        Returns:
            Dictionary containing structural analysis
        """
        if not LIBROSA_AVAILABLE:
            logger.warning("librosa not available")
            return {"error": "librosa not available"}

        audio_file = Path(audio_path)
        if not audio_file.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        # Load audio
        try:
            y, sr = librosa.load(audio_path, sr=self.sample_rate)
        except Exception as e:
            logger.error(f"Failed to load audio: {e}")
            return {"error": str(e)}

        result = {
            "file_path": str(audio_path),
            "duration": float(len(y) / sr),
            "sample_rate": int(sr),
        }

        # Detect sections
        sections = self._detect_sections(y, sr)
        result["sections"] = sections

        # Analyze harmony
        harmony = self._analyze_harmony(y, sr)
        result["harmony"] = harmony

        # Analyze tempo and rhythm
        rhythm = self._analyze_rhythm(y, sr)
        result["rhythm"] = rhythm

        # Detect patterns
        patterns = detect_reggae_patterns(audio_path, sample_rate=sr)
        result["patterns"] = patterns

        # Analyze energy
        energy = self._analyze_energy(y, sr)
        result["energy"] = energy

        return result

    def _detect_sections(self, y: np.ndarray, sr: int) -> List[Dict[str, Any]]:
        """
        Detect structural sections in the audio.

        Args:
            y: Audio time series
            sr: Sample rate

        Returns:
            List of section dictionaries
        """
        # Compute chroma features for harmonic analysis
        chroma = librosa.feature.chroma_cqt(y=y, sr=sr, hop_length=self.hop_length)

        # Compute MFCC for timbral analysis
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13, hop_length=self.hop_length)

        # Combine features
        features = np.vstack([chroma, mfcc])

        # Compute self-similarity matrix
        rec = librosa.segment.recurrence_matrix(
            features,
            mode='affinity',
            metric='cosine',
            width=9,
        )

        # Detect boundaries
        # Use k to detect section boundaries (typically 8-12 sections in a song)
        boundaries_frames = librosa.segment.agglomerative(
            features,
            k=8,
        )

        # Convert to time
        boundaries = librosa.frames_to_time(
            boundaries_frames,
            sr=sr,
            hop_length=self.hop_length,
        )

        # Create section objects
        sections = []
        section_labels = self._label_sections(len(boundaries))

        for i, (start, label) in enumerate(zip(boundaries, section_labels)):
            end = boundaries[i + 1] if i < len(boundaries) - 1 else len(y) / sr

            sections.append({
                "label": label,
                "start_time": float(start),
                "end_time": float(end),
                "duration": float(end - start),
            })

        return sections

    def _label_sections(self, num_sections: int) -> List[str]:
        """
        Generate labels for detected sections.

        Args:
            num_sections: Number of sections

        Returns:
            List of section labels
        """
        # Simple heuristic for section labeling
        if num_sections <= 1:
            return ["full_track"]
        elif num_sections == 2:
            return ["intro", "main"]
        elif num_sections == 3:
            return ["intro", "main", "outro"]
        elif num_sections == 4:
            return ["intro", "verse", "chorus", "outro"]
        elif num_sections >= 5:
            labels = ["intro"]
            middle_sections = num_sections - 2

            # Alternate verse and chorus
            for i in range(middle_sections):
                if i % 2 == 0:
                    labels.append("verse")
                else:
                    labels.append("chorus")

            labels.append("outro")
            return labels[:num_sections]

        return [f"section_{i}" for i in range(num_sections)]

    def _analyze_harmony(self, y: np.ndarray, sr: int) -> Dict[str, Any]:
        """
        Analyze harmonic content.

        Args:
            y: Audio time series
            sr: Sample rate

        Returns:
            Dictionary of harmonic analysis
        """
        # Extract chroma features
        chroma = librosa.feature.chroma_cqt(y=y, sr=sr, hop_length=self.hop_length)

        # Aggregate over time to get average chroma profile
        chroma_mean = np.mean(chroma, axis=1)

        # Find dominant pitch classes
        pitch_classes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        dominant_pitches = np.argsort(chroma_mean)[-3:][::-1]

        # Estimate key (simplified)
        root = pitch_classes[dominant_pitches[0]]

        # Compute harmonic change rate
        chroma_diff = np.diff(chroma, axis=1)
        harmonic_change_rate = float(np.mean(np.abs(chroma_diff)))

        return {
            "estimated_key": root,
            "dominant_pitch_classes": [pitch_classes[i] for i in dominant_pitches],
            "harmonic_change_rate": harmonic_change_rate,
            "chroma_profile": chroma_mean.tolist(),
        }

    def _analyze_rhythm(self, y: np.ndarray, sr: int) -> Dict[str, Any]:
        """
        Analyze rhythmic content.

        Args:
            y: Audio time series
            sr: Sample rate

        Returns:
            Dictionary of rhythm analysis
        """
        # Detect tempo and beats
        tempo, beat_frames = librosa.beat.beat_track(
            y=y,
            sr=sr,
            hop_length=self.hop_length,
        )

        beat_times = librosa.frames_to_time(beat_frames, sr=sr, hop_length=self.hop_length)

        # Calculate tempo stability
        if len(beat_times) > 1:
            beat_intervals = np.diff(beat_times)
            tempo_stability = 1.0 - (np.std(beat_intervals) / np.mean(beat_intervals))
        else:
            tempo_stability = 0.0

        # Detect onsets
        onset_frames = librosa.onset.onset_detect(
            y=y,
            sr=sr,
            hop_length=self.hop_length,
        )

        onset_times = librosa.frames_to_time(onset_frames, sr=sr, hop_length=self.hop_length)

        return {
            "tempo": float(tempo),
            "tempo_stability": float(np.clip(tempo_stability, 0, 1)),
            "num_beats": int(len(beat_frames)),
            "num_onsets": int(len(onset_frames)),
            "beat_times": beat_times.tolist(),
            "time_signature": "4/4",  # Assume 4/4 for reggae
        }

    def _analyze_energy(self, y: np.ndarray, sr: int) -> Dict[str, Any]:
        """
        Analyze energy levels.

        Args:
            y: Audio time series
            sr: Sample rate

        Returns:
            Dictionary of energy analysis
        """
        # RMS energy
        rms = librosa.feature.rms(y=y, hop_length=self.hop_length)[0]

        # Spectral centroid (brightness)
        spectral_centroid = librosa.feature.spectral_centroid(
            y=y,
            sr=sr,
            hop_length=self.hop_length,
        )[0]

        # Zero crossing rate
        zcr = librosa.feature.zero_crossing_rate(y=y, hop_length=self.hop_length)[0]

        return {
            "mean_energy": float(np.mean(rms)),
            "max_energy": float(np.max(rms)),
            "energy_variance": float(np.var(rms)),
            "mean_spectral_centroid": float(np.mean(spectral_centroid)),
            "mean_zero_crossing_rate": float(np.mean(zcr)),
        }


def analyze_audio_structure(
    audio_path: str,
    sample_rate: int = 22050,
) -> Dict[str, Any]:
    """
    Convenience function to analyze audio structure.

    Args:
        audio_path: Path to audio file
        sample_rate: Sample rate for analysis

    Returns:
        Dictionary of structural analysis
    """
    analyzer = AudioStructureAnalyzer(sample_rate=sample_rate)
    return analyzer.analyze_structure(audio_path)


__all__ = ["AudioStructureAnalyzer", "analyze_audio_structure"]
