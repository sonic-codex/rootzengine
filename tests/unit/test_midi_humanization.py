"""Tests for MIDI humanization"""

import pytest
import numpy as np

from rootzengine.midi.humanize import (
    HumanizeConfig,
    MIDIHumanizer,
    create_reggae_humanizer,
)
from rootzengine.midi.patterns import MIDINote


class TestHumanizeConfig:
    """Test HumanizeConfig"""

    def test_default_config(self):
        """Test default humanization configuration"""
        config = HumanizeConfig()

        assert config.timing_variance == 0.02
        assert config.velocity_variance == 0.15
        assert config.swing_amount == 0.0

    def test_custom_config(self):
        """Test custom humanization configuration"""
        config = HumanizeConfig(
            timing_variance=0.03,
            velocity_variance=0.20,
            swing_amount=0.1,
        )

        assert config.timing_variance == 0.03
        assert config.velocity_variance == 0.20
        assert config.swing_amount == 0.1


class TestMIDIHumanizer:
    """Test MIDIHumanizer"""

    @pytest.fixture
    def humanizer(self):
        """Create a humanizer instance"""
        return MIDIHumanizer()

    @pytest.fixture
    def test_notes(self):
        """Create test MIDI notes"""
        return [
            MIDINote(note=60, velocity=80, start_beat=0.0, duration=0.5, channel=1),
            MIDINote(note=64, velocity=85, start_beat=1.0, duration=0.5, channel=1),
            MIDINote(note=67, velocity=90, start_beat=2.0, duration=0.5, channel=1),
            MIDINote(note=72, velocity=95, start_beat=3.0, duration=0.5, channel=1),
        ]

    def test_humanize_notes_changes_values(self, humanizer, test_notes):
        """Test that humanization changes note values"""
        original_velocities = [n.velocity for n in test_notes]
        original_timings = [n.start_beat for n in test_notes]

        humanized = humanizer.humanize_notes(test_notes)

        # Check that values have changed (with high probability)
        humanized_velocities = [n.velocity for n in humanized]
        humanized_timings = [n.start_beat for n in humanized]

        # At least some notes should have different velocities
        assert humanized_velocities != original_velocities

    def test_humanize_notes_preserves_count(self, humanizer, test_notes):
        """Test that humanization preserves note count"""
        humanized = humanizer.humanize_notes(test_notes)

        assert len(humanized) == len(test_notes)

    def test_humanize_notes_preserves_pitches(self, humanizer, test_notes):
        """Test that humanization preserves note pitches"""
        humanized = humanizer.humanize_notes(test_notes)

        original_pitches = [n.note for n in test_notes]
        humanized_pitches = [n.note for n in humanized]

        assert humanized_pitches == original_pitches

    def test_humanize_velocity_range(self, humanizer):
        """Test that humanized velocities stay in valid range"""
        notes = [
            MIDINote(note=60, velocity=v, start_beat=0.0, duration=0.5, channel=1)
            for v in [10, 50, 100, 127]
        ]

        humanized = humanizer.humanize_notes(notes)

        for note in humanized:
            assert 1 <= note.velocity <= 127

    def test_humanize_timing_non_negative(self, humanizer):
        """Test that humanized timings don't go negative"""
        notes = [
            MIDINote(note=60, velocity=80, start_beat=t, duration=0.5, channel=1)
            for t in [0.0, 0.1, 0.5, 1.0]
        ]

        humanized = humanizer.humanize_notes(notes)

        for note in humanized:
            assert note.start_beat >= 0.0

    def test_preserve_grid(self, humanizer, test_notes):
        """Test grid preservation mode"""
        humanized_grid = humanizer.humanize_notes(test_notes, preserve_grid=True)
        humanized_free = humanizer.humanize_notes(test_notes, preserve_grid=False)

        # Grid-preserved notes should be closer to original positions
        # This is probabilistic, but should hold generally
        original_timings = [n.start_beat for n in test_notes]
        grid_timings = [n.start_beat for n in humanized_grid]
        free_timings = [n.start_beat for n in humanized_free]

        # Calculate average deviation
        grid_deviation = np.mean([abs(g - o) for g, o in zip(grid_timings, original_timings)])
        free_deviation = np.mean([abs(f - o) for f, o in zip(free_timings, original_timings)])

        # Grid should generally have smaller deviation
        # (This may occasionally fail due to randomness, but very unlikely)
        assert grid_deviation <= free_deviation * 1.5


class TestReggaeFeel:
    """Test reggae-specific feel application"""

    @pytest.fixture
    def humanizer(self):
        """Create a humanizer instance"""
        return MIDIHumanizer()

    @pytest.fixture
    def test_notes(self):
        """Create test MIDI notes on beats"""
        return [
            MIDINote(note=60, velocity=80, start_beat=0.0, duration=0.5, channel=1),  # Beat 1
            MIDINote(note=64, velocity=80, start_beat=1.0, duration=0.5, channel=1),  # Beat 2
            MIDINote(note=67, velocity=80, start_beat=2.0, duration=0.5, channel=1),  # Beat 3
            MIDINote(note=72, velocity=80, start_beat=3.0, duration=0.5, channel=1),  # Beat 4
        ]

    def test_laid_back_feel(self, humanizer, test_notes):
        """Test laid back reggae feel"""
        felt_notes = humanizer.apply_reggae_feel(test_notes, style="laid_back")

        assert len(felt_notes) == len(test_notes)

        # Beat 3 should be most laid back (behind the beat)
        beat_3_note = felt_notes[2]
        assert beat_3_note.start_beat >= 2.0  # Should be at or behind beat

    def test_steppers_feel(self, humanizer, test_notes):
        """Test steppers feel (more on the beat)"""
        felt_notes = humanizer.apply_reggae_feel(test_notes, style="steppers")

        assert len(felt_notes) == len(test_notes)
        # Timings should be close to original beats

    def test_rockers_feel(self, humanizer, test_notes):
        """Test rockers feel"""
        felt_notes = humanizer.apply_reggae_feel(test_notes, style="rockers")

        assert len(felt_notes) == len(test_notes)


class TestDynamics:
    """Test dynamic curve application"""

    @pytest.fixture
    def humanizer(self):
        return MIDIHumanizer()

    @pytest.fixture
    def test_notes(self):
        """Create uniform velocity notes"""
        return [
            MIDINote(note=60+i, velocity=80, start_beat=float(i), duration=0.5, channel=1)
            for i in range(8)
        ]

    def test_crescendo(self, humanizer, test_notes):
        """Test crescendo (getting louder)"""
        crescendo_notes = humanizer.add_dynamics(test_notes, curve="crescendo")

        velocities = [n.velocity for n in crescendo_notes]

        # Velocities should generally increase
        assert velocities[-1] >= velocities[0]

    def test_diminuendo(self, humanizer, test_notes):
        """Test diminuendo (getting quieter)"""
        diminuendo_notes = humanizer.add_dynamics(test_notes, curve="diminuendo")

        velocities = [n.velocity for n in diminuendo_notes]

        # Velocities should generally decrease
        assert velocities[0] >= velocities[-1]

    def test_wave_dynamics(self, humanizer, test_notes):
        """Test wave dynamics"""
        wave_notes = humanizer.add_dynamics(test_notes, curve="wave")

        # Should have some variation
        velocities = [n.velocity for n in wave_notes]
        assert len(set(velocities)) > 1  # Not all the same


class TestAccentPattern:
    """Test accent pattern application"""

    @pytest.fixture
    def humanizer(self):
        return MIDIHumanizer()

    @pytest.fixture
    def test_notes(self):
        """Create notes on all beats"""
        return [
            MIDINote(note=60, velocity=80, start_beat=float(i), duration=0.5, channel=1)
            for i in range(4)
        ]

    def test_accent_beats_1_and_3(self, humanizer, test_notes):
        """Test accenting beats 1 and 3"""
        accented = humanizer.apply_accent_pattern(
            test_notes,
            accent_beats=[0.0, 2.0],
            accent_boost=20,
        )

        # Beats 1 and 3 should be louder
        assert accented[0].velocity > test_notes[1].velocity
        assert accented[2].velocity > test_notes[1].velocity

    def test_accent_boost_amount(self, humanizer, test_notes):
        """Test accent boost amount"""
        boost = 30
        accented = humanizer.apply_accent_pattern(
            test_notes,
            accent_beats=[0.0],
            accent_boost=boost,
        )

        # First note should be boosted
        expected_velocity = min(127, test_notes[0].velocity + boost)
        assert accented[0].velocity == expected_velocity


class TestCreateReggaeHumanizer:
    """Test reggae humanizer factory"""

    def test_one_drop_humanizer(self):
        """Test creating one drop humanizer"""
        humanizer = create_reggae_humanizer(style="one_drop")

        assert humanizer is not None
        assert isinstance(humanizer, MIDIHumanizer)
        assert humanizer.config.timing_variance == 0.015

    def test_steppers_humanizer(self):
        """Test creating steppers humanizer"""
        humanizer = create_reggae_humanizer(style="steppers")

        assert humanizer is not None
        assert humanizer.config.timing_variance == 0.008  # Tighter timing

    def test_rockers_humanizer(self):
        """Test creating rockers humanizer"""
        humanizer = create_reggae_humanizer(style="rockers")

        assert humanizer is not None
        assert humanizer.config.timing_variance == 0.020  # Looser timing


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
