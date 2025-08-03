"""Audio feature extraction utilities."""

import logging
from typing import Dict, Tuple

import librosa
import numpy as np

from src.rootzengine.core.config import settings

logger = logging.getLogger(__name__)


def extract_features(
    y: np.ndarray, 
    sr: int, 
    hop_length: int = None, 
    n_fft: int = None
) -> Dict:
    """Extract audio features from a time series.
    
    Args:
        y: Audio time series
        sr: Sample rate
        hop_length: Hop length for FFT
        n_fft: FFT window size
        
    Returns:
        Dictionary of extracted features
    """
    hop_length = hop_length or settings.audio.hop_length
    n_fft = n_fft or settings.audio.n_fft
    
    # Compute MFCCs
    mfccs = librosa.feature.mfcc(
        y=y, sr=sr, n_mfcc=13, hop_length=hop_length, n_fft=n_fft
    )
    mfcc_delta = librosa.feature.delta(mfccs)
    mfcc_delta2 = librosa.feature.delta(mfccs, order=2)
    
    # Compute chroma features
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr, hop_length=hop_length)
    
    # Compute spectral features
    spectral_centroid = librosa.feature.spectral_centroid(
        y=y, sr=sr, hop_length=hop_length, n_fft=n_fft
    )
    spectral_bandwidth = librosa.feature.spectral_bandwidth(
        y=y, sr=sr, hop_length=hop_length, n_fft=n_fft
    )
    spectral_contrast = librosa.feature.spectral_contrast(
        y=y, sr=sr, hop_length=hop_length, n_fft=n_fft
    )
    spectral_flatness = librosa.feature.spectral_flatness(
        y=y, hop_length=hop_length, n_fft=n_fft
    )
    
    # Compute temporal features
    rms = librosa.feature.rms(y=y, hop_length=hop_length)
    zcr = librosa.feature.zero_crossing_rate(y=y, hop_length=hop_length)
    
    # Onset features
    onset_env = librosa.onset.onset_strength(
        y=y, sr=sr, hop_length=hop_length
    )
    
    # Return features as dictionary
    features = {
        "mfccs": mfccs,
        "mfcc_delta": mfcc_delta,
        "mfcc_delta2": mfcc_delta2,
        "chroma": chroma,
        "spectral_centroid": spectral_centroid,
        "spectral_bandwidth": spectral_bandwidth,
        "spectral_contrast": spectral_contrast,
        "spectral_flatness": spectral_flatness,
        "rms": rms,
        "zero_crossing_rate": zcr,
        "onset_env": onset_env
    }
    
    return features


def detect_onsets(
    y: np.ndarray, 
    sr: int, 
    hop_length: int = None
) -> Tuple[np.ndarray, np.ndarray]:
    """Detect onsets in audio time series.
    
    Args:
        y: Audio time series
        sr: Sample rate
        hop_length: Hop length for analysis
        
    Returns:
        Tuple containing:
        - onset_times: Array of onset times in seconds
        - onset_strengths: Array of onset strengths
    """
    hop_length = hop_length or settings.audio.hop_length
    
    # Compute onset strength
    onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop_length)
    
    # Detect onsets
    onset_frames = librosa.onset.onset_detect(
        onset_envelope=onset_env, sr=sr, hop_length=hop_length
    )
    
    # Convert frames to time
    onset_times = librosa.frames_to_time(onset_frames, sr=sr, hop_length=hop_length)
    
    # Get onset strengths
    onset_strengths = onset_env[onset_frames] if len(onset_frames) > 0 else np.array([])
    
    return onset_times, onset_strengths


def detect_reggae_rhythm_pattern(
    y: np.ndarray, 
    sr: int, 
    hop_length: int = None
) -> str:
    """Detect common reggae rhythm patterns.
    
    Args:
        y: Audio time series
        sr: Sample rate
        hop_length: Hop length for analysis
        
    Returns:
        String indicating the detected pattern: 'one_drop', 'steppers', etc.
    """
    hop_length = hop_length or settings.audio.hop_length
    
    # This is a placeholder for more sophisticated reggae pattern detection
    # In a real implementation, this would analyze onset patterns in the low-frequency
    # range to identify characteristic reggae rhythm patterns
    
    # Extract onset envelope focused on drum frequencies
    onset_env = librosa.onset.onset_strength(
        y=y, sr=sr, hop_length=hop_length, 
        fmin=50, fmax=200  # Focus on bass drum frequencies
    )
    
    # Detect beats
    tempo, beats = librosa.beat.beat_track(
        onset_envelope=onset_env, sr=sr, hop_length=hop_length
    )
    
    # Analyze onset pattern within beats
    # This is simplified; a real implementation would be more sophisticated
    if 60 <= tempo <= 80:
        return "one_drop"
    elif 80 < tempo <= 95:
        return "rockers"
    else:
        return "steppers"
