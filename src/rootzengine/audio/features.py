"""Audio feature extraction functionality"""

from typing import Dict, Any, Optional
import numpy as np
import librosa
import librosa.feature
from pathlib import Path
import logging

from ..core.config import AudioConfig
from ..core.exceptions import AudioProcessingError

logger = logging.getLogger(__name__)


def extract_audio_features(audio_file_path: str) -> Dict[str, Any]:
    """
    Extract comprehensive audio features from an audio file.
    
    Args:
        audio_file_path: Path to the audio file
        
    Returns:
        Dictionary containing extracted features
    """
    # TODO: Implement feature extraction
    return {
        'mfcc': np.array([]),
        'spectral_centroid': np.array([]),
        'chroma': np.array([]),
        'tempo': 120.0
    }


class FeatureExtractor:
    """Extract comprehensive audio features for structure analysis."""
    
    def __init__(self, config: Optional[AudioConfig] = None):
        self.config = config or AudioConfig()
        
    def extract_all_features(self, audio_path: str) -> Dict:
        """Extract comprehensive feature set from audio file."""
        try:
            y, sr = librosa.load(audio_path, sr=self.config.sample_rate)
            
            features = {
                "spectral": self._extract_spectral_features(y, sr),
                "rhythm": self._extract_rhythm_features(y, sr),
                "harmonic": self._extract_harmonic_features(y, sr),
                "energy": self._extract_energy_features(y, sr),
                "temporal": self._extract_temporal_features(y, sr),
            }
            
            logger.info(f"Extracted features from {audio_path}")
            return features
            
        except Exception as e:
            raise AudioProcessingError(f"Feature extraction failed: {str(e)}")
    
    def _extract_spectral_features(self, y: np.ndarray, sr: int) -> Dict:
        """Extract spectral features (MFCC, chroma, spectral characteristics)."""
        
        # MFCC features
        mfcc = librosa.feature.mfcc(
            y=y, sr=sr, 
            n_mfcc=self.config.n_mfcc,
            hop_length=self.config.hop_length
        )
        
        # Chroma features  
        chroma = librosa.feature.chroma_stft(
            y=y, sr=sr,
            hop_length=self.config.hop_length,
            n_chroma=self.config.n_chroma
        )
        
        # Spectral features
        spectral_centroids = librosa.feature.spectral_centroid(
            y=y, sr=sr, hop_length=self.config.hop_length
        )[0]
        
        spectral_rolloff = librosa.feature.spectral_rolloff(
            y=y, sr=sr, hop_length=self.config.hop_length
        )[0]
        
        spectral_bandwidth = librosa.feature.spectral_bandwidth(
            y=y, sr=sr, hop_length=self.config.hop_length
        )[0]
        
        zero_crossing_rate = librosa.feature.zero_crossing_rate(
            y, hop_length=self.config.hop_length
        )[0]
        
        return {
            "mfcc": mfcc.tolist(),
            "mfcc_mean": np.mean(mfcc, axis=1).tolist(),
            "mfcc_std": np.std(mfcc, axis=1).tolist(),
            "chroma": chroma.tolist(),
            "chroma_mean": np.mean(chroma, axis=1).tolist(),
            "spectral_centroid": spectral_centroids.tolist(),
            "spectral_rolloff": spectral_rolloff.tolist(), 
            "spectral_bandwidth": spectral_bandwidth.tolist(),
            "zero_crossing_rate": zero_crossing_rate.tolist(),
        }
    
    def _extract_rhythm_features(self, y: np.ndarray, sr: int) -> Dict:
        """Extract rhythm and tempo features."""
        
        # Tempo and beat tracking
        tempo, beats = librosa.beat.beat_track(
            y=y, sr=sr, hop_length=self.config.hop_length
        )
        
        # Onset detection
        onset_frames = librosa.onset.onset_detect(
            y=y, sr=sr, hop_length=self.config.hop_length
        )
        onset_times = librosa.frames_to_time(
            onset_frames, sr=sr, hop_length=self.config.hop_length
        )
        
        # Rhythm patterns
        tempogram = librosa.feature.tempogram(
            y=y, sr=sr, hop_length=self.config.hop_length
        )
        
        return {
            "tempo": float(tempo),
            "beats": beats.tolist(),
            "beat_times": librosa.frames_to_time(
                beats, sr=sr, hop_length=self.config.hop_length
            ).tolist(),
            "onsets": onset_times.tolist(),
            "onset_strength": librosa.onset.onset_strength(
                y=y, sr=sr, hop_length=self.config.hop_length
            ).tolist(),
            "tempogram_mean": np.mean(tempogram, axis=1).tolist(),
        }
    
    def _extract_harmonic_features(self, y: np.ndarray, sr: int) -> Dict:
        """Extract harmonic and tonal features."""
        
        # Harmonic-percussive separation
        y_harmonic, y_percussive = librosa.effects.hpss(y)
        
        # Tonnetz (tonal centroid features)
        tonnetz = librosa.feature.tonnetz(
            y=y_harmonic, sr=sr, hop_length=self.config.hop_length
        )
        
        # Constant-Q transform for better harmonic analysis
        cqt = librosa.cqt(y=y_harmonic, sr=sr, hop_length=self.config.hop_length)
        
        # Key estimation
        chroma = librosa.feature.chroma_cqt(
            C=cqt, sr=sr, hop_length=self.config.hop_length
        )
        
        return {
            "tonnetz": tonnetz.tolist(),
            "tonnetz_mean": np.mean(tonnetz, axis=1).tolist(),
            "harmonic_energy": float(np.sum(y_harmonic**2)),
            "percussive_energy": float(np.sum(y_percussive**2)),
            "harmonic_percussive_ratio": float(
                np.sum(y_harmonic**2) / (np.sum(y_percussive**2) + 1e-8)
            ),
            "chroma_cqt": chroma.tolist(),
            "chroma_cqt_mean": np.mean(chroma, axis=1).tolist(),
        }
    
    def _extract_energy_features(self, y: np.ndarray, sr: int) -> Dict:
        """Extract energy and dynamics features."""
        
        # RMS energy
        rms = librosa.feature.rms(
            y=y, hop_length=self.config.hop_length
        )[0]
        
        # Mel-frequency features
        mel_spectrogram = librosa.feature.melspectrogram(
            y=y, sr=sr, 
            n_mels=self.config.n_mel,
            hop_length=self.config.hop_length
        )
        
        # Convert to dB
        mel_db = librosa.power_to_db(mel_spectrogram, ref=np.max)
        
        return {
            "rms": rms.tolist(),
            "rms_mean": float(np.mean(rms)),
            "rms_std": float(np.std(rms)),
            "dynamic_range": float(np.max(rms) - np.min(rms)),
            "mel_spectrogram": mel_db.tolist(),
            "mel_mean": np.mean(mel_db, axis=1).tolist(),
            "overall_loudness": float(np.mean(librosa.amplitude_to_db(rms))),
        }
    
    def _extract_temporal_features(self, y: np.ndarray, sr: int) -> Dict:
        """Extract temporal structure features."""
        
        # Segment the audio for local analysis
        segment_length = int(self.config.segment_length * sr)
        n_segments = len(y) // segment_length
        
        segment_features = []
        for i in range(n_segments):
            start = i * segment_length
            end = start + segment_length
            segment = y[start:end]
            
            if len(segment) > 0:
                segment_rms = np.sqrt(np.mean(segment**2))
                segment_zcr = np.mean(librosa.feature.zero_crossing_rate(segment))
                
                segment_features.append({
                    "rms": float(segment_rms),
                    "zcr": float(segment_zcr),
                    "start_time": float(start / sr),
                    "end_time": float(end / sr),
                })
        
        return {
            "segments": segment_features,
            "total_duration": float(len(y) / sr),
            "n_segments": n_segments,
        }
    
    def extract_features_for_time_range(
        self, 
        audio_path: str, 
        start_time: float, 
        end_time: float
    ) -> Dict:
        """Extract features for a specific time range."""
        try:
            y, sr = librosa.load(
                audio_path, 
                sr=self.config.sample_rate,
                offset=start_time,
                duration=end_time - start_time
            )
            
            return self.extract_all_features_from_array(y, sr)
            
        except Exception as e:
            raise AudioProcessingError(f"Time range feature extraction failed: {str(e)}")
    
    def extract_all_features_from_array(self, y: np.ndarray, sr: int) -> Dict:
        """Extract features from audio array instead of file."""
        features = {
            "spectral": self._extract_spectral_features(y, sr),
            "rhythm": self._extract_rhythm_features(y, sr),
            "harmonic": self._extract_harmonic_features(y, sr),
            "energy": self._extract_energy_features(y, sr),
            "temporal": self._extract_temporal_features(y, sr),
        }
        
        return features


def extract_features(audio_path: str):
    """Legacy function for backward compatibility."""
    extractor = FeatureExtractor()
    return extractor.extract_all_features(audio_path)


__all__ = ["extract_features", "extract_audio_features", "FeatureExtractor"]
