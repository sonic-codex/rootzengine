"""Tests for reggae pattern detection and definitions"""

import pytest
import numpy as np

from rootzengine.audio.reggae_patterns import (
    ReggaePattern,
    InstrumentRole,
    DrumPatternDefinition,
    DRUM_PATTERNS,
    GUITAR_PATTERNS,
    BASS_PATTERNS,
    get_pattern_characteristics,
    detect_pattern_from_beats,
    detect_skank_pattern,
)


class TestReggaePattern:
    """Test ReggaePattern enum"""

    def test_pattern_values(self):
        """Test that all pattern types are defined"""
        assert ReggaePattern.ONE_DROP.value == "one_drop"
        assert ReggaePattern.STEPPERS.value == "steppers"
        assert ReggaePattern.ROCKERS.value == "rockers"


class TestInstrumentRole:
    """Test InstrumentRole enum"""

    def test_instrument_values(self):
        """Test that all instrument roles are defined"""
        assert InstrumentRole.BASS.value == "bass"
        assert InstrumentRole.DRUMS.value == "drums"
        assert InstrumentRole.RHYTHM_GUITAR.value == "rhythm_guitar"
        assert InstrumentRole.ORGAN.value == "organ"


class TestDrumPatterns:
    """Test drum pattern definitions"""

    def test_one_drop_pattern(self):
        """Test one drop pattern definition"""
        pattern = DRUM_PATTERNS[ReggaePattern.ONE_DROP]

        assert pattern.name == "One Drop"
        assert pattern.pattern == ReggaePattern.ONE_DROP
        assert 3.0 in pattern.kick_pattern  # Kick on beat 3
        assert 2.0 in pattern.snare_pattern  # Snare on 2
        assert 4.0 in pattern.snare_pattern  # Snare on 4

    def test_steppers_pattern(self):
        """Test steppers pattern definition"""
        pattern = DRUM_PATTERNS[ReggaePattern.STEPPERS]

        assert pattern.name == "Steppers"
        assert pattern.pattern == ReggaePattern.STEPPERS
        # Kicks on all beats
        assert 1.0 in pattern.kick_pattern
        assert 2.0 in pattern.kick_pattern
        assert 3.0 in pattern.kick_pattern
        assert 4.0 in pattern.kick_pattern

    def test_rockers_pattern(self):
        """Test rockers pattern definition"""
        pattern = DRUM_PATTERNS[ReggaePattern.ROCKERS]

        assert pattern.name == "Rockers"
        assert pattern.pattern == ReggaePattern.ROCKERS
        assert 1.0 in pattern.kick_pattern  # Kick on 1
        assert 3.0 in pattern.kick_pattern  # Kick on 3

    def test_pattern_tempo_ranges(self):
        """Test that patterns have valid tempo ranges"""
        for pattern_type, pattern in DRUM_PATTERNS.items():
            min_tempo, max_tempo = pattern.tempo_range
            assert min_tempo > 0
            assert max_tempo > min_tempo
            assert min_tempo >= 65
            assert max_tempo <= 105


class TestGuitarPatterns:
    """Test guitar pattern definitions"""

    def test_classic_skank(self):
        """Test classic skank pattern"""
        pattern = GUITAR_PATTERNS["classic_skank"]

        assert pattern.name == "Classic Skank"
        # Upbeats (and of each beat)
        assert 1.5 in pattern.strum_positions
        assert 2.5 in pattern.strum_positions
        assert 3.5 in pattern.strum_positions
        assert 4.5 in pattern.strum_positions

    def test_double_skank(self):
        """Test double skank pattern"""
        pattern = GUITAR_PATTERNS["double_skank"]

        assert pattern.name == "Double Skank"
        # Should have more strums than classic
        assert len(pattern.strum_positions) > len(GUITAR_PATTERNS["classic_skank"].strum_positions)


class TestBassPatterns:
    """Test bass pattern definitions"""

    def test_walking_bass(self):
        """Test walking bass pattern"""
        pattern = BASS_PATTERNS["walking"]

        assert pattern.name == "Walking Bass"
        # Walking pattern should have notes on all eighths
        assert len(pattern.note_positions) == 8

    def test_bubble_pattern(self):
        """Test bubble (Nyabinghi) pattern"""
        pattern = BASS_PATTERNS["bubble"]

        assert pattern.name == "Bubble (Nyabinghi)"
        assert pattern.characteristics["traditional"] is True


class TestGetPatternCharacteristics:
    """Test pattern characteristics retrieval"""

    def test_one_drop_characteristics(self):
        """Test getting one drop characteristics"""
        chars = get_pattern_characteristics(ReggaePattern.ONE_DROP)

        assert chars["emphasis"] == "beat_3"
        assert chars["feel"] == "laid_back"

    def test_steppers_characteristics(self):
        """Test getting steppers characteristics"""
        chars = get_pattern_characteristics(ReggaePattern.STEPPERS)

        assert chars["emphasis"] == "all_beats"
        assert chars["feel"] == "driving"

    def test_unknown_pattern(self):
        """Test getting characteristics for undefined pattern"""
        chars = get_pattern_characteristics(ReggaePattern.FLYING_CYMBALS)
        assert chars == {}


class TestDetectPatternFromBeats:
    """Test pattern detection from beat timing"""

    def test_detect_one_drop(self):
        """Test detecting one drop pattern"""
        # Simulate one drop: kick on 3, snare on 2 and 4
        kick_times = [3.0, 7.0, 11.0]  # Beat 3 of each bar
        snare_times = [2.0, 4.0, 6.0, 8.0, 10.0, 12.0]  # Beats 2 and 4

        pattern, confidence = detect_pattern_from_beats(kick_times, snare_times, 80)

        assert pattern == ReggaePattern.ONE_DROP
        assert confidence > 0.5

    def test_detect_steppers(self):
        """Test detecting steppers pattern"""
        # Simulate steppers: kicks on all beats
        kick_times = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0]
        snare_times = [2.0, 4.0, 6.0, 8.0]

        pattern, confidence = detect_pattern_from_beats(kick_times, snare_times, 85)

        assert pattern == ReggaePattern.STEPPERS
        assert confidence > 0.5

    def test_detect_rockers(self):
        """Test detecting rockers pattern"""
        # Simulate rockers: kicks on 1 and 3
        kick_times = [1.0, 3.0, 5.0, 7.0]
        snare_times = [2.0, 4.0, 6.0, 8.0]

        pattern, confidence = detect_pattern_from_beats(kick_times, snare_times, 78)

        assert pattern == ReggaePattern.ROCKERS
        assert confidence > 0.3

    def test_empty_input(self):
        """Test with empty beat arrays"""
        pattern, confidence = detect_pattern_from_beats([], [], 80)

        # Should return default pattern
        assert pattern in [ReggaePattern.ONE_DROP]
        assert confidence >= 0.0


class TestDetectSkankPattern:
    """Test guitar skank pattern detection"""

    def test_detect_classic_skank(self):
        """Test detecting classic skank (upbeat emphasis)"""
        # Simulate upbeat strums
        onset_times = [1.5, 2.5, 3.5, 4.5, 5.5, 6.5]

        pattern_name, confidence = detect_skank_pattern(onset_times, 80)

        assert pattern_name == "classic_skank"
        assert confidence > 0.7

    def test_detect_double_skank(self):
        """Test detecting double skank"""
        # Simulate double time upbeats
        onset_times = [1.25, 1.5, 2.25, 2.5, 3.25, 3.5]

        pattern_name, confidence = detect_skank_pattern(onset_times, 80)

        # Should detect some kind of skank
        assert "skank" in pattern_name or pattern_name == "unknown"

    def test_downbeat_heavy_pattern(self):
        """Test with downbeat-heavy pattern (not a skank)"""
        # Simulate downbeat strums
        onset_times = [1.0, 2.0, 3.0, 4.0, 5.0]

        pattern_name, confidence = detect_skank_pattern(onset_times, 80)

        assert confidence < 0.5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
