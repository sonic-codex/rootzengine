"""Basic audio feature extraction."""

import librosa
import numpy as np

def extract_features(y, sr, hop_length=512, n_fft=2048):
    """Extract basic audio features."""
    return {
        "mfcc": librosa.feature.mfcc(y=y, sr=sr, hop_length=hop_length),
        "chroma": librosa.feature.chroma_stft(y=y, sr=sr, hop_length=hop_length),
        "spectral_centroid": librosa.feature.spectral_centroid(y=y, sr=sr, hop_length=hop_length)
    }


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
