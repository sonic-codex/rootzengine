"""
Reggae pattern definitions and detection library.

This module defines common reggae drum patterns and rhythm characteristics
used for pattern detection and generation.
"""

from typing import Dict, List, Tuple
from enum import Enum
from dataclasses import dataclass


class ReggaePattern(Enum):
    """Common reggae drum patterns"""
    ONE_DROP = "one_drop"  # Kick on 3, snare on 2 and 4
    STEPPERS = "steppers"  # Kick on every beat
    ROCKERS = "rockers"  # Kick on 1 and 3, emphasis on 3
    FLYING_CYMBALS = "flying_cymbals"  # Open hi-hat on upbeats
    FOUR_ON_FLOOR = "four_on_floor"  # Steady kick pattern
    RUBADUB = "rubadub"  # Traditional pattern with emphasis


class InstrumentRole(Enum):
    """Instrument roles in reggae"""
    BASS = "bass"
    DRUMS = "drums"
    RHYTHM_GUITAR = "rhythm_guitar"  # Skank
    LEAD_GUITAR = "lead_guitar"
    ORGAN = "organ"
    PIANO = "piano"
    PERCUSSION = "percussion"
    HORNS = "horns"
    VOCALS = "vocals"


@dataclass
class DrumPatternDefinition:
    """Definition of a drum pattern"""
    name: str
    pattern: ReggaePattern
    kick_pattern: List[float]  # Beat positions (1.0 = beat 1, 1.5 = and of 1)
    snare_pattern: List[float]
    hihat_pattern: List[float]
    characteristics: Dict[str, any]
    tempo_range: Tuple[float, float]  # BPM range


# Define standard reggae drum patterns
DRUM_PATTERNS = {
    ReggaePattern.ONE_DROP: DrumPatternDefinition(
        name="One Drop",
        pattern=ReggaePattern.ONE_DROP,
        kick_pattern=[3.0],  # Emphasize beat 3
        snare_pattern=[2.0, 4.0],  # Backbeat on 2 and 4
        hihat_pattern=[1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5],  # Steady eighths
        characteristics={
            "emphasis": "beat_3",
            "feel": "laid_back",
            "rimshot": True,
            "cross_stick": False,
        },
        tempo_range=(65, 95),
    ),
    ReggaePattern.STEPPERS: DrumPatternDefinition(
        name="Steppers",
        pattern=ReggaePattern.STEPPERS,
        kick_pattern=[1.0, 2.0, 3.0, 4.0],  # Four on the floor
        snare_pattern=[2.0, 4.0],
        hihat_pattern=[1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5],
        characteristics={
            "emphasis": "all_beats",
            "feel": "driving",
            "energy": "high",
        },
        tempo_range=(70, 100),
    ),
    ReggaePattern.ROCKERS: DrumPatternDefinition(
        name="Rockers",
        pattern=ReggaePattern.ROCKERS,
        kick_pattern=[1.0, 3.0],  # Emphasize 1 and 3, especially 3
        snare_pattern=[2.0, 4.0],
        hihat_pattern=[1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5],
        characteristics={
            "emphasis": "beat_1_and_3",
            "feel": "rocking",
            "open_hihat": "upbeats",
        },
        tempo_range=(75, 105),
    ),
}


@dataclass
class GuitarPatternDefinition:
    """Definition of guitar skank pattern"""
    name: str
    strum_positions: List[float]  # Beat positions for strums
    muted_strums: List[float]  # Positions for muted/chucked strums
    characteristics: Dict[str, any]


# Guitar skank patterns
GUITAR_PATTERNS = {
    "classic_skank": GuitarPatternDefinition(
        name="Classic Skank",
        strum_positions=[1.5, 2.5, 3.5, 4.5],  # Upbeats (and of each beat)
        muted_strums=[1.0, 2.0, 3.0, 4.0],  # Muted on downbeats
        characteristics={
            "muting": "heavy",
            "rhythm": "upbeat_emphasis",
            "voicing": "rootless_chords",
        },
    ),
    "double_skank": GuitarPatternDefinition(
        name="Double Skank",
        strum_positions=[1.25, 1.5, 2.25, 2.5, 3.25, 3.5, 4.25, 4.5],  # 16th note upbeats
        muted_strums=[1.0, 2.0, 3.0, 4.0],
        characteristics={
            "muting": "moderate",
            "rhythm": "double_time_feel",
            "density": "high",
        },
    ),
}


@dataclass
class BassPatternDefinition:
    """Definition of bass line pattern"""
    name: str
    note_positions: List[float]
    emphasis_positions: List[float]  # Where to emphasize notes
    characteristics: Dict[str, any]


# Bass patterns
BASS_PATTERNS = {
    "walking": BassPatternDefinition(
        name="Walking Bass",
        note_positions=[1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5],
        emphasis_positions=[1.0, 3.0],
        characteristics={
            "movement": "stepwise",
            "rhythm": "walking",
            "syncopation": "moderate",
        },
    ),
    "bubble": BassPatternDefinition(
        name="Bubble (Nyabinghi)",
        note_positions=[1.0, 1.25, 2.0, 2.25, 3.0, 3.25, 4.0, 4.25],
        emphasis_positions=[1.0, 3.0],
        characteristics={
            "movement": "alternating_notes",
            "rhythm": "bubble",
            "traditional": True,
        },
    ),
    "steppers_bass": BassPatternDefinition(
        name="Steppers Bass",
        note_positions=[1.0, 2.0, 3.0, 4.0],
        emphasis_positions=[1.0, 3.0],
        characteristics={
            "movement": "steady",
            "rhythm": "four_on_floor",
            "emphasis": "downbeats",
        },
    ),
}


def get_pattern_characteristics(pattern: ReggaePattern) -> Dict[str, any]:
    """
    Get characteristics for a specific reggae pattern.

    Args:
        pattern: The reggae pattern to get characteristics for

    Returns:
        Dictionary of pattern characteristics
    """
    if pattern in DRUM_PATTERNS:
        return DRUM_PATTERNS[pattern].characteristics
    return {}


def detect_pattern_from_beats(
    kick_times: List[float],
    snare_times: List[float],
    tempo: float,
) -> Tuple[ReggaePattern, float]:
    """
    Detect reggae pattern from drum hit timings.

    Args:
        kick_times: List of kick drum hit times in beats
        snare_times: List of snare drum hit times in beats
        tempo: Tempo in BPM

    Returns:
        Tuple of (detected pattern, confidence score)
    """
    # Normalize times to beat positions within a bar (1-4)
    def normalize_to_bar(times: List[float]) -> List[float]:
        if not times:
            return []
        return [(t % 4) + 1 for t in times]

    kick_positions = normalize_to_bar(kick_times)
    snare_positions = normalize_to_bar(snare_times)

    scores = {}

    for pattern_type, pattern_def in DRUM_PATTERNS.items():
        score = 0.0

        # Check if tempo is in range
        if pattern_def.tempo_range[0] <= tempo <= pattern_def.tempo_range[1]:
            score += 0.3

        # Check kick pattern similarity
        kick_match = sum(
            1 for expected in pattern_def.kick_pattern
            if any(abs(actual - expected) < 0.25 for actual in kick_positions)
        )
        if pattern_def.kick_pattern:
            score += 0.4 * (kick_match / len(pattern_def.kick_pattern))

        # Check snare pattern similarity
        snare_match = sum(
            1 for expected in pattern_def.snare_pattern
            if any(abs(actual - expected) < 0.25 for actual in snare_positions)
        )
        if pattern_def.snare_pattern:
            score += 0.3 * (snare_match / len(pattern_def.snare_pattern))

        scores[pattern_type] = score

    if not scores:
        return ReggaePattern.ONE_DROP, 0.0

    best_pattern = max(scores.items(), key=lambda x: x[1])
    return best_pattern[0], best_pattern[1]


def detect_skank_pattern(onset_times: List[float], tempo: float) -> Tuple[str, float]:
    """
    Detect guitar skank pattern from onset timings.

    Args:
        onset_times: List of guitar onset times in beats
        tempo: Tempo in BPM

    Returns:
        Tuple of (pattern name, confidence score)
    """
    # Normalize to beat positions
    positions = [(t % 4) + 1 for t in onset_times]

    # Count upbeat vs downbeat onsets
    upbeat_count = sum(1 for p in positions if (p % 1) > 0.3 and (p % 1) < 0.7)
    downbeat_count = sum(1 for p in positions if (p % 1) < 0.2 or (p % 1) > 0.8)

    if upbeat_count > downbeat_count * 1.5:
        return "classic_skank", 0.8
    elif upbeat_count > downbeat_count:
        return "double_skank", 0.6

    return "unknown", 0.3


__all__ = [
    "ReggaePattern",
    "InstrumentRole",
    "DrumPatternDefinition",
    "GuitarPatternDefinition",
    "BassPatternDefinition",
    "DRUM_PATTERNS",
    "GUITAR_PATTERNS",
    "BASS_PATTERNS",
    "get_pattern_characteristics",
    "detect_pattern_from_beats",
    "detect_skank_pattern",
]
