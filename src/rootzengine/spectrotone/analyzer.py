"""
Spectrotone Analysis for Realistic AI Behavior

This module provides comprehensive spectrotone analysis that maps audio characteristics
to colors, timbres, and behavioral patterns for AI bandmate agents.
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
import librosa
from dataclasses import dataclass
from enum import Enum

from ..metadata.schemas import SpectrotoneAnalysis
from ..core.config import AudioConfig

logger = logging.getLogger(__name__)


class SpectralCharacteristic(Enum):
    """Spectral characteristics for instrument classification."""
    BRIGHT = "bright"
    DARK = "dark"
    WARM = "warm"
    COLD = "cold"
    HOLLOW = "hollow"
    FULL = "full"
    SHARP = "sharp"
    SOFT = "soft"


@dataclass
class SpectrotoneProfile:
    """Enhanced spectrotone profile with behavioral implications."""
    primary_color: str
    secondary_color: str
    timbre: str
    brightness: float      # 0.0-1.0, affects high-frequency content
    weight: float          # 0.0-1.0, affects presence in mix
    resonance: float       # 0.0-1.0, affects sustain characteristics
    attack_sharpness: float # 0.0-1.0, affects note onset characteristics
    decay_rate: float      # 0.0-1.0, affects note release characteristics
    harmonic_richness: float # 0.0-1.0, affects harmonic content complexity
    dynamic_range: float   # 0.0-1.0, affects volume variation capability


class SpectrotoneMapping:
    """Spectrotone mapping system for instruments."""
    
    # Enhanced spectrotone table with behavioral characteristics
    INSTRUMENT_PROFILES = {
        # Reggae Core Instruments
        "bass_guitar": SpectrotoneProfile(
            primary_color="blue",
            secondary_color="grey",
            timbre="dark",
            brightness=0.2,
            weight=0.85,
            resonance=0.8,
            attack_sharpness=0.3,
            decay_rate=0.4,
            harmonic_richness=0.6,
            dynamic_range=0.7
        ),
        "rhythm_guitar": SpectrotoneProfile(
            primary_color="tan",
            secondary_color="brown", 
            timbre="warm",
            brightness=0.4,
            weight=0.6,
            resonance=0.6,
            attack_sharpness=0.8,  # Sharp attack for skank
            decay_rate=0.9,        # Quick decay
            harmonic_richness=0.5,
            dynamic_range=0.6
        ),
        "lead_guitar": SpectrotoneProfile(
            primary_color="grey",
            secondary_color="yellow",
            timbre="bright",
            brightness=0.7,
            weight=0.5,
            resonance=0.5,
            attack_sharpness=0.6,
            decay_rate=0.5,
            harmonic_richness=0.8,
            dynamic_range=0.9
        ),
        "organ": SpectrotoneProfile(
            primary_color="ivory",
            secondary_color="yellow",
            timbre="hollow",
            brightness=0.5,
            weight=0.7,
            resonance=0.9,   # High sustain
            attack_sharpness=0.2,  # Soft attack
            decay_rate=0.1,  # Very slow decay
            harmonic_richness=0.7,
            dynamic_range=0.4  # Limited dynamics
        ),
        "piano": SpectrotoneProfile(
            primary_color="white",
            secondary_color="grey",
            timbre="neutral",
            brightness=0.6,
            weight=0.4,
            resonance=0.7,
            attack_sharpness=0.5,
            decay_rate=0.6,
            harmonic_richness=0.8,
            dynamic_range=0.9
        ),
        "drums": SpectrotoneProfile(
            primary_color="white",
            secondary_color="black",
            timbre="percussive",
            brightness=0.5,
            weight=0.8,
            resonance=0.3,   # Short sustain
            attack_sharpness=1.0,  # Very sharp attack
            decay_rate=0.8,  # Quick decay
            harmonic_richness=0.3,  # Minimal harmonics
            dynamic_range=1.0  # Full dynamic range
        ),
        "synth_bass": SpectrotoneProfile(
            primary_color="purple",
            secondary_color="blue",
            timbre="synthetic",
            brightness=0.3,
            weight=0.9,
            resonance=0.8,
            attack_sharpness=0.4,
            decay_rate=0.3,
            harmonic_richness=0.9,  # Rich harmonics
            dynamic_range=0.8
        )
    }


class SpectrotoneAnalyzer:
    """Analyzer for extracting spectrotone characteristics from audio."""
    
    def __init__(self, config: Optional[AudioConfig] = None):
        """Initialize spectrotone analyzer."""
        self.config = config or AudioConfig()
        self.mapping = SpectrotoneMapping()
        
        # Frequency bands for analysis (Hz)
        self.frequency_bands = {
            "sub_bass": (20, 60),
            "bass": (60, 250),
            "low_mid": (250, 500),
            "mid": (500, 2000),
            "high_mid": (2000, 4000),
            "presence": (4000, 8000),
            "brilliance": (8000, 20000)
        }
        
    def analyze_audio_spectrotone(
        self, 
        audio_path: str, 
        instrument_hint: Optional[str] = None
    ) -> SpectrotoneAnalysis:
        """
        Analyze audio file and extract spectrotone characteristics.
        
        Args:
            audio_path: Path to audio file
            instrument_hint: Optional hint about the instrument type
            
        Returns:
            SpectrotoneAnalysis with comprehensive spectrotone data
        """
        try:
            # Load audio
            y, sr = librosa.load(audio_path, sr=self.config.sample_rate)
            
            # Extract spectral features
            spectral_features = self._extract_spectral_features(y, sr)
            
            # Classify instrument if not provided
            if instrument_hint is None:
                instrument_hint = self._classify_instrument(spectral_features)
            
            # Get base profile
            base_profile = self.mapping.INSTRUMENT_PROFILES.get(
                instrument_hint, 
                self._create_default_profile()
            )
            
            # Adapt profile based on actual audio characteristics
            adapted_profile = self._adapt_profile_to_audio(base_profile, spectral_features)
            
            # Create analysis
            analysis = SpectrotoneAnalysis(
                instrument=instrument_hint,
                primary_color=adapted_profile.primary_color,
                secondary_color=adapted_profile.secondary_color,
                timbre=adapted_profile.timbre,
                brightness=adapted_profile.brightness,
                weight=adapted_profile.weight,
                resonance=adapted_profile.resonance,
                harmonic_content=self._analyze_harmonic_content(y, sr),
                temporal_evolution=self._analyze_temporal_evolution(y, sr)
            )
            
            logger.info(f"Analyzed spectrotone for {instrument_hint}: {adapted_profile.primary_color} {adapted_profile.timbre}")
            return analysis
            
        except Exception as e:
            logger.error(f"Spectrotone analysis failed for {audio_path}: {str(e)}")
            # Return default analysis
            return self._create_default_analysis(instrument_hint or "unknown")
    
    def _extract_spectral_features(self, y: np.ndarray, sr: int) -> Dict[str, float]:
        """Extract comprehensive spectral features from audio."""
        features = {}
        
        # Spectral centroid (brightness indicator)
        spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
        features['brightness'] = np.mean(spectral_centroid) / (sr / 2)  # Normalize
        
        # Spectral rolloff (high-frequency content)
        spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
        features['rolloff'] = np.mean(spectral_rolloff) / (sr / 2)
        
        # Spectral bandwidth (spectral spread)
        spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)[0]
        features['bandwidth'] = np.mean(spectral_bandwidth) / (sr / 2)
        
        # Zero crossing rate (noisiness indicator)
        zcr = librosa.feature.zero_crossing_rate(y)[0]
        features['noisiness'] = np.mean(zcr)
        
        # RMS energy (overall loudness/weight)
        rms = librosa.feature.rms(y=y)[0]
        features['energy'] = np.mean(rms)
        
        # Spectral flatness (tonality vs noise)
        spectral_flatness = librosa.feature.spectral_flatness(y=y)[0]
        features['flatness'] = np.mean(spectral_flatness)
        
        # Frequency band analysis
        stft = librosa.stft(y, hop_length=self.config.hop_length)
        magnitude = np.abs(stft)
        freqs = librosa.fft_frequencies(sr=sr, n_fft=self.config.n_fft)
        
        for band_name, (low_freq, high_freq) in self.frequency_bands.items():
            band_mask = (freqs >= low_freq) & (freqs <= high_freq)
            band_energy = np.mean(magnitude[band_mask, :])
            features[f'energy_{band_name}'] = band_energy
        
        # Attack and decay characteristics
        onset_envelope = librosa.onset.onset_strength(y=y, sr=sr)
        features['attack_sharpness'] = np.mean(np.gradient(onset_envelope))
        
        # Harmonic vs percussive content
        y_harmonic, y_percussive = librosa.effects.hpss(y)
        total_energy = np.sum(y**2)
        features['harmonic_ratio'] = np.sum(y_harmonic**2) / total_energy if total_energy > 0 else 0
        features['percussive_ratio'] = np.sum(y_percussive**2) / total_energy if total_energy > 0 else 0
        
        return features
    
    def _classify_instrument(self, features: Dict[str, float]) -> str:
        """Classify instrument based on spectral features."""
        # Simple rule-based classification
        # In production, this would use a trained ML model
        
        if features.get('energy_sub_bass', 0) > 0.5 and features.get('brightness', 0) < 0.3:
            return "bass_guitar"
        elif features.get('percussive_ratio', 0) > 0.7:
            return "drums"
        elif features.get('harmonic_ratio', 0) > 0.8 and features.get('brightness', 0) > 0.6:
            return "lead_guitar"
        elif features.get('energy_mid', 0) > 0.6 and features.get('attack_sharpness', 0) > 0.5:
            return "rhythm_guitar"
        elif features.get('flatness', 0) < 0.1 and features.get('energy_mid', 0) > 0.5:
            return "organ"
        else:
            return "unknown"
    
    def _adapt_profile_to_audio(
        self, 
        base_profile: SpectrotoneProfile, 
        features: Dict[str, float]
    ) -> SpectrotoneProfile:
        """Adapt base instrument profile based on actual audio characteristics."""
        # Create adapted profile by blending base with measured characteristics
        adapted = SpectrotoneProfile(
            primary_color=base_profile.primary_color,
            secondary_color=base_profile.secondary_color,
            timbre=base_profile.timbre,
            brightness=self._blend_values(base_profile.brightness, features.get('brightness', 0.5), 0.3),
            weight=self._blend_values(base_profile.weight, features.get('energy', 0.5), 0.2),
            resonance=self._blend_values(base_profile.resonance, 1.0 - features.get('flatness', 0.5), 0.2),
            attack_sharpness=self._blend_values(base_profile.attack_sharpness, features.get('attack_sharpness', 0.5), 0.4),
            decay_rate=base_profile.decay_rate,  # Harder to measure, keep base
            harmonic_richness=self._blend_values(base_profile.harmonic_richness, features.get('harmonic_ratio', 0.5), 0.3),
            dynamic_range=base_profile.dynamic_range  # Keep base for now
        )
        
        return adapted
    
    def _blend_values(self, base: float, measured: float, blend_factor: float) -> float:
        """Blend base profile value with measured value."""
        return base * (1 - blend_factor) + measured * blend_factor
    
    def _analyze_harmonic_content(self, y: np.ndarray, sr: int) -> Dict[str, float]:
        """Analyze harmonic content in frequency domain."""
        # Extract fundamental frequency and harmonics
        pitches, magnitudes = librosa.piptrack(y=y, sr=sr, threshold=0.1)
        
        harmonic_content = {}
        
        # Find fundamental frequency
        fundamental_indices = np.where(magnitudes > 0)
        if len(fundamental_indices[0]) > 0:
            fundamental_freq = np.median(pitches[fundamental_indices])
            
            if fundamental_freq > 0:
                # Analyze harmonic series
                for harmonic in range(1, 6):  # First 5 harmonics
                    harmonic_freq = fundamental_freq * harmonic
                    # Find energy at harmonic frequency
                    freq_bin = int(harmonic_freq * self.config.n_fft / sr)
                    if freq_bin < len(pitches):
                        harmonic_content[f'harmonic_{harmonic}'] = float(
                            np.mean(magnitudes[freq_bin-2:freq_bin+3]) if freq_bin > 2 else 0
                        )
        
        # Default harmonic content if analysis fails
        if not harmonic_content:
            harmonic_content = {
                'harmonic_1': 0.8,  # Fundamental
                'harmonic_2': 0.4,  # Octave
                'harmonic_3': 0.2,  # Fifth
                'harmonic_4': 0.1,  # Second octave
                'harmonic_5': 0.05  # Major third above second octave
            }
        
        return harmonic_content
    
    def _analyze_temporal_evolution(self, y: np.ndarray, sr: int) -> List[Dict[str, float]]:
        """Analyze how spectrotone characteristics evolve over time."""
        # Divide audio into segments for temporal analysis
        segment_length = sr * 2  # 2-second segments
        segments = []
        
        for i in range(0, len(y), segment_length):
            segment = y[i:i+segment_length]
            if len(segment) < segment_length // 2:  # Skip very short segments
                continue
            
            # Extract features for this segment
            segment_features = self._extract_spectral_features(segment, sr)
            
            segment_data = {
                'time_start': i / sr,
                'time_end': (i + len(segment)) / sr,
                'brightness': segment_features.get('brightness', 0.5),
                'energy': segment_features.get('energy', 0.5),
                'harmonic_ratio': segment_features.get('harmonic_ratio', 0.5),
                'noisiness': segment_features.get('noisiness', 0.5)
            }
            
            segments.append(segment_data)
        
        return segments
    
    def _create_default_profile(self) -> SpectrotoneProfile:
        """Create default spectrotone profile for unknown instruments."""
        return SpectrotoneProfile(
            primary_color="grey",
            secondary_color="white",
            timbre="neutral",
            brightness=0.5,
            weight=0.5,
            resonance=0.5,
            attack_sharpness=0.5,
            decay_rate=0.5,
            harmonic_richness=0.5,
            dynamic_range=0.5
        )
    
    def _create_default_analysis(self, instrument: str) -> SpectrotoneAnalysis:
        """Create default spectrotone analysis when analysis fails."""
        return SpectrotoneAnalysis(
            instrument=instrument,
            primary_color="grey",
            secondary_color="white",
            timbre="neutral",
            brightness=0.5,
            weight=0.5,
            resonance=0.5,
            harmonic_content={
                'harmonic_1': 0.5,
                'harmonic_2': 0.3,
                'harmonic_3': 0.2
            },
            temporal_evolution=[]
        )
    
    def get_behavioral_implications(self, analysis: SpectrotoneAnalysis) -> Dict[str, Any]:
        """
        Get behavioral implications for AI agents based on spectrotone analysis.
        
        Returns:
            Dictionary with behavioral parameters for AI agent
        """
        implications = {
            # Playing style based on spectrotone
            "preferred_velocity_range": self._velocity_from_spectrotone(analysis),
            "timing_humanization": self._timing_from_spectrotone(analysis),
            "note_length_preference": self._note_length_from_spectrotone(analysis),
            "dynamic_sensitivity": analysis.weight,
            
            # Mix behavior
            "mix_presence": analysis.weight,
            "frequency_emphasis": self._frequency_emphasis_from_spectrotone(analysis),
            
            # Interaction behavior
            "leadership_tendency": analysis.brightness,  # Bright instruments tend to lead
            "supportive_tendency": 1.0 - analysis.brightness,  # Dark instruments support
            "rhythmic_precision": 1.0 - analysis.resonance,  # High sustain = less rhythmic precision
        }
        
        return implications
    
    def _velocity_from_spectrotone(self, analysis: SpectrotoneAnalysis) -> Tuple[int, int]:
        """Determine velocity range from spectrotone characteristics."""
        base_min = 40
        base_max = 100
        
        # Bright instruments can play louder
        brightness_factor = analysis.brightness
        weight_factor = analysis.weight
        
        min_vel = int(base_min + (1 - weight_factor) * 20)
        max_vel = int(base_max + brightness_factor * 27)
        
        return (min_vel, max_vel)
    
    def _timing_from_spectrotone(self, analysis: SpectrotoneAnalysis) -> float:
        """Determine timing humanization from spectrotone."""
        # Percussive instruments (low resonance) have tighter timing
        return 0.02 * analysis.resonance  # 0-0.02 seconds variation
    
    def _note_length_from_spectrotone(self, analysis: SpectrotoneAnalysis) -> str:
        """Determine note length preference from spectrotone."""
        if analysis.resonance > 0.7:
            return "long"
        elif analysis.resonance < 0.3:
            return "short"
        else:
            return "medium"
    
    def _frequency_emphasis_from_spectrotone(self, analysis: SpectrotoneAnalysis) -> Dict[str, float]:
        """Determine frequency emphasis from spectrotone."""
        return {
            "low": 1.0 - analysis.brightness,
            "mid": 0.5 + analysis.weight * 0.5,
            "high": analysis.brightness
        }


def create_spectrotone_analyzer(config: Optional[AudioConfig] = None) -> SpectrotoneAnalyzer:
    """Factory function to create spectrotone analyzer."""
    return SpectrotoneAnalyzer(config)