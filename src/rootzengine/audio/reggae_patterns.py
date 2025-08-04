"""Reggae pattern detection and classification."""

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from rootzengine.core.config import settings


class ReggaeStyle(Enum):
    """Reggae style classifications."""
    ONE_DROP = "one_drop"
    STEPPERS = "steppers"
    ROCKERS = "rockers"
    SKA = "ska"
    ROCKSTEADY = "rocksteady"
    ROOTS = "roots"
    DANCEHALL = "dancehall"
    DUB = "dub"
    UNKNOWN = "unknown"


@dataclass
class RhythmPattern:
    """Represents a rhythm pattern."""
    name: str
    style: ReggaeStyle
    tempo_range: Tuple[int, int]  # BPM range
    emphasis_pattern: List[float]  # Beat emphasis pattern (0-1)
    kick_pattern: List[bool]  # Kick drum pattern
    snare_pattern: List[bool]  # Snare drum pattern
    hi_hat_pattern: List[bool]  # Hi-hat pattern
    skank_pattern: List[bool]  # Guitar skank pattern
    bass_pattern: List[bool]  # Bass pattern
    confidence_factors: Dict[str, float]  # Factors for pattern matching


# Define standard reggae patterns
REGGAE_PATTERNS = {
    ReggaeStyle.ONE_DROP: RhythmPattern(
        name="One Drop",
        style=ReggaeStyle.ONE_DROP,
        tempo_range=(60, 90),
        emphasis_pattern=[0.3, 1.0, 0.5, 0.8],  # Emphasis on 2 and 4
        kick_pattern=[False, False, False, True],  # Kick on 3
        snare_pattern=[False, True, False, True],  # Snare on 2 and 4
        hi_hat_pattern=[False, True, True, True],  # Hi-hat on off-beats
        skank_pattern=[False, True, False, True],  # Skank on off-beats
        bass_pattern=[True, False, False, True],  # Bass on 1 and 3
        confidence_factors={
            "tempo_weight": 0.2,
            "rhythm_weight": 0.4,
            "emphasis_weight": 0.3,
            "harmonic_weight": 0.1
        }
    ),
    
    ReggaeStyle.STEPPERS: RhythmPattern(
        name="Steppers",
        style=ReggaeStyle.STEPPERS,
        tempo_range=(70, 100),
        emphasis_pattern=[0.8, 0.6, 0.8, 0.6],  # More even emphasis
        kick_pattern=[True, False, True, False],  # Kick on 1 and 3
        snare_pattern=[False, True, False, True],  # Snare on 2 and 4
        hi_hat_pattern=[True, True, True, True],  # Steady hi-hat
        skank_pattern=[False, True, False, True],  # Skank on off-beats
        bass_pattern=[True, False, True, False],  # Bass on 1 and 3
        confidence_factors={
            "tempo_weight": 0.25,
            "rhythm_weight": 0.4,
            "emphasis_weight": 0.25,
            "harmonic_weight": 0.1
        }
    ),
    
    ReggaeStyle.ROCKERS: RhythmPattern(
        name="Rockers",
        style=ReggaeStyle.ROCKERS,
        tempo_range=(80, 110),
        emphasis_pattern=[0.9, 0.7, 0.9, 0.7],  # Strong on 1 and 3
        kick_pattern=[True, False, True, False],  # Kick on 1 and 3
        snare_pattern=[False, True, False, True],  # Snare on 2 and 4
        hi_hat_pattern=[True, True, True, True],  # Steady hi-hat
        skank_pattern=[False, True, False, True],  # Skank on off-beats
        bass_pattern=[True, True, True, True],  # More active bass
        confidence_factors={
            "tempo_weight": 0.2,
            "rhythm_weight": 0.35,
            "emphasis_weight": 0.3,
            "harmonic_weight": 0.15
        }
    ),
    
    ReggaeStyle.SKA: RhythmPattern(
        name="Ska",
        style=ReggaeStyle.SKA,
        tempo_range=(120, 180),
        emphasis_pattern=[0.6, 0.9, 0.6, 0.9],  # Emphasis on off-beats
        kick_pattern=[True, False, True, False],  # Kick on 1 and 3
        snare_pattern=[False, True, False, True],  # Snare on 2 and 4
        hi_hat_pattern=[True, True, True, True],  # Fast hi-hat
        skank_pattern=[False, True, False, True],  # Heavy skank emphasis
        bass_pattern=[True, True, True, True],  # Walking bass feel
        confidence_factors={
            "tempo_weight": 0.4,  # Tempo is crucial for ska
            "rhythm_weight": 0.3,
            "emphasis_weight": 0.2,
            "harmonic_weight": 0.1
        }
    ),
    
    ReggaeStyle.ROCKSTEADY: RhythmPattern(
        name="Rocksteady",
        style=ReggaeStyle.ROCKSTEADY,
        tempo_range=(90, 120),
        emphasis_pattern=[0.7, 0.8, 0.7, 0.8],  # Moderate emphasis
        kick_pattern=[True, False, True, False],  # Kick on 1 and 3
        snare_pattern=[False, True, False, True],  # Snare on 2 and 4
        hi_hat_pattern=[True, True, True, True],  # Steady rhythm
        skank_pattern=[False, True, False, True],  # Moderate skank
        bass_pattern=[True, False, True, False],  # Walking bass
        confidence_factors={
            "tempo_weight": 0.25,
            "rhythm_weight": 0.35,
            "emphasis_weight": 0.25,
            "harmonic_weight": 0.15
        }
    )
}


class ReggaePatternDetector:
    """Detects and classifies reggae patterns in audio."""
    
    def __init__(self):
        self.patterns = REGGAE_PATTERNS
    
    def detect_pattern_mock(self, tempo: float, audio_path: str = None) -> Dict[str, any]:
        """
        Mock pattern detection based on tempo and synthetic analysis.
        
        Args:
            tempo: Detected tempo in BPM
            audio_path: Path to audio file (for future real implementation)
            
        Returns:
            Pattern detection results
        """
        # Calculate pattern scores based on tempo
        pattern_scores = {}
        
        for style, pattern in self.patterns.items():
            tempo_min, tempo_max = pattern.tempo_range
            
            # Tempo score (1.0 if within range, decreases outside)
            if tempo_min <= tempo <= tempo_max:
                tempo_score = 1.0
            else:
                # Penalize being outside range
                distance = min(abs(tempo - tempo_min), abs(tempo - tempo_max))
                tempo_score = max(0.0, 1.0 - distance / 50.0)
            
            # Simulate rhythm analysis (mock values)
            rhythm_score = np.random.uniform(0.4, 0.9)  # Random but realistic
            emphasis_score = np.random.uniform(0.3, 0.8)
            harmonic_score = np.random.uniform(0.2, 0.7)
            
            # Calculate weighted score
            weights = pattern.confidence_factors
            total_score = (
                tempo_score * weights["tempo_weight"] +
                rhythm_score * weights["rhythm_weight"] +
                emphasis_score * weights["emphasis_weight"] +
                harmonic_score * weights["harmonic_weight"]
            )
            
            pattern_scores[style.value] = {
                "total_score": total_score,
                "tempo_score": tempo_score,
                "rhythm_score": rhythm_score,
                "emphasis_score": emphasis_score,
                "harmonic_score": harmonic_score,
                "pattern_name": pattern.name
            }
        
        # Find best match
        best_style = max(pattern_scores.keys(), key=lambda k: pattern_scores[k]["total_score"])
        best_score = pattern_scores[best_style]["total_score"]
        
        # Classification confidence
        if best_score > 0.7:
            confidence = "high"
        elif best_score > 0.5:
            confidence = "medium"
        else:
            confidence = "low"
        
        return {
            "detected_style": best_style,
            "confidence": confidence,
            "confidence_score": best_score,
            "all_scores": pattern_scores,
            "tempo": tempo,
            "analysis_type": "mock"
        }
    
    def get_pattern_info(self, style: ReggaeStyle) -> Optional[RhythmPattern]:
        """Get detailed information about a specific pattern."""
        return self.patterns.get(style)
    
    def analyze_rhythm_characteristics(self, tempo: float, detected_style: str) -> Dict[str, any]:
        """Analyze rhythm characteristics for the detected style."""
        style_enum = ReggaeStyle(detected_style)
        pattern = self.patterns.get(style_enum)
        
        if not pattern:
            return {"error": f"Unknown style: {detected_style}"}
        
        # Mock rhythm analysis
        characteristics = {
            "style": detected_style,
            "pattern_name": pattern.name,
            "tempo": tempo,
            "tempo_range": pattern.tempo_range,
            "rhythm_analysis": {
                "kick_emphasis": np.mean(pattern.kick_pattern),
                "snare_emphasis": np.mean(pattern.snare_pattern),
                "off_beat_emphasis": np.mean(pattern.skank_pattern),
                "bass_activity": np.mean(pattern.bass_pattern),
                "overall_syncopation": np.std(pattern.emphasis_pattern)
            },
            "musical_elements": {
                "time_signature": "4/4",
                "typical_key": "A minor" if style_enum in [ReggaeStyle.ROOTS, ReggaeStyle.DUB] else "C major",
                "chord_progression": self._get_typical_progression(style_enum),
                "instrumentation": self._get_typical_instruments(style_enum)
            }
        }
        
        return characteristics
    
    def _get_typical_progression(self, style: ReggaeStyle) -> List[str]:
        """Get typical chord progression for a style."""
        progressions = {
            ReggaeStyle.ONE_DROP: ["i", "♭VII", "♭VI", "♭VII"],
            ReggaeStyle.STEPPERS: ["I", "vi", "IV", "V"],
            ReggaeStyle.ROCKERS: ["i", "♭VII", "i", "♭VII"],
            ReggaeStyle.SKA: ["I", "V", "vi", "IV"],
            ReggaeStyle.ROCKSTEADY: ["I", "vi", "ii", "V"]
        }
        return progressions.get(style, ["I", "V", "vi", "IV"])
    
    def _get_typical_instruments(self, style: ReggaeStyle) -> List[str]:
        """Get typical instruments for a style."""
        base_instruments = ["bass", "drums", "guitar", "keyboard"]
        
        style_specific = {
            ReggaeStyle.ONE_DROP: base_instruments + ["organ"],
            ReggaeStyle.STEPPERS: base_instruments + ["horn section"],
            ReggaeStyle.ROCKERS: base_instruments + ["lead guitar"],
            ReggaeStyle.SKA: base_instruments + ["horn section", "trombone", "trumpet"],
            ReggaeStyle.ROCKSTEADY: base_instruments + ["piano"]
        }
        
        return style_specific.get(style, base_instruments)
    
    def get_all_styles(self) -> List[Dict[str, any]]:
        """Get information about all available reggae styles."""
        return [
            {
                "style": style.value,
                "name": pattern.name,
                "tempo_range": pattern.tempo_range,
                "description": self._get_style_description(style)
            }
            for style, pattern in self.patterns.items()
        ]
    
    def _get_style_description(self, style: ReggaeStyle) -> str:
        """Get description for a reggae style."""
        descriptions = {
            ReggaeStyle.ONE_DROP: "Classic reggae rhythm with emphasis on the third beat",
            ReggaeStyle.STEPPERS: "Four-on-the-floor drum pattern with steady kick",
            ReggaeStyle.ROCKERS: "Driving rhythm with strong emphasis on one and three",
            ReggaeStyle.SKA: "Fast-paced predecessor to reggae with upstroke emphasis",
            ReggaeStyle.ROCKSTEADY: "Mid-tempo style between ska and reggae"
        }
        return descriptions.get(style, "Reggae sub-genre")


# Global detector instance
reggae_detector = ReggaePatternDetector()