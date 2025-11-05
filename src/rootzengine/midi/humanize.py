"""
MIDI humanization for realistic musical feel.

This module provides timing and velocity humanization to make
generated MIDI patterns sound more natural and less mechanical.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
import random
import numpy as np

from .patterns import MIDINote


@dataclass
class HumanizeConfig:
    """Configuration for MIDI humanization"""
    timing_variance: float = 0.02  # Max timing deviation (0-1, as fraction of beat)
    velocity_variance: float = 0.15  # Max velocity deviation (0-1)
    swing_amount: float = 0.0  # Swing feel (0-1)
    groove_template: Optional[Dict[float, float]] = None  # Beat position -> timing offset


class MIDIHumanizer:
    """
    Humanizes MIDI patterns for more natural feel.

    Applies:
    - Timing variations (drift, jitter)
    - Velocity variations (dynamics, accents)
    - Swing and groove quantization
    - Playing style characteristics
    """

    def __init__(self, config: Optional[HumanizeConfig] = None):
        """
        Initialize humanizer.

        Args:
            config: Humanization configuration
        """
        self.config = config or HumanizeConfig()
        self._random = random.Random(42)  # Seeded for reproducibility

    def humanize_notes(
        self,
        notes: List[MIDINote],
        preserve_grid: bool = False,
    ) -> List[MIDINote]:
        """
        Humanize a list of MIDI notes.

        Args:
            notes: List of MIDI notes to humanize
            preserve_grid: Whether to keep notes close to grid positions

        Returns:
            List of humanized MIDI notes
        """
        humanized = []

        for note in notes:
            humanized_note = MIDINote(
                note=note.note,
                velocity=self._humanize_velocity(note.velocity),
                start_beat=self._humanize_timing(
                    note.start_beat,
                    preserve_grid=preserve_grid,
                ),
                duration=note.duration * self._random.uniform(0.95, 1.05),
                channel=note.channel,
            )
            humanized.append(humanized_note)

        return humanized

    def _humanize_timing(
        self,
        beat_position: float,
        preserve_grid: bool = False,
    ) -> float:
        """
        Add timing humanization to a beat position.

        Args:
            beat_position: Original beat position
            preserve_grid: Keep close to grid

        Returns:
            Humanized beat position
        """
        # Apply groove template if provided
        if self.config.groove_template:
            beat_in_bar = beat_position % 4
            if beat_in_bar in self.config.groove_template:
                beat_position += self.config.groove_template[beat_in_bar]

        # Apply swing
        if self.config.swing_amount > 0:
            beat_fraction = beat_position % 1.0
            # Apply swing to eighth notes (0.5 position)
            if 0.4 < beat_fraction < 0.6:
                swing_offset = self.config.swing_amount * 0.1
                beat_position += swing_offset

        # Add random timing variation
        if not preserve_grid:
            max_deviation = self.config.timing_variance
            deviation = self._random.uniform(-max_deviation, max_deviation)
            beat_position += deviation
        else:
            # Smaller variation for grid-preserved notes
            max_deviation = self.config.timing_variance * 0.3
            deviation = self._random.uniform(-max_deviation, max_deviation)
            beat_position += deviation

        return max(0.0, beat_position)  # Don't go negative

    def _humanize_velocity(self, velocity: int) -> int:
        """
        Add velocity humanization.

        Args:
            velocity: Original velocity (0-127)

        Returns:
            Humanized velocity
        """
        # Calculate variation amount
        max_variation = int(velocity * self.config.velocity_variance)
        variation = self._random.randint(-max_variation, max_variation)

        # Apply variation
        new_velocity = velocity + variation

        # Clamp to valid MIDI range
        return max(1, min(127, new_velocity))

    def apply_reggae_feel(
        self,
        notes: List[MIDINote],
        style: str = "laid_back",
    ) -> List[MIDINote]:
        """
        Apply reggae-specific timing feel.

        Args:
            notes: List of notes to process
            style: Reggae style ('laid_back', 'steppers', 'rockers')

        Returns:
            Notes with reggae feel applied
        """
        if style == "laid_back":
            # Laid back feel: slightly behind the beat
            groove = {
                0.0: -0.01,  # Beat 1 slightly late
                1.0: -0.015,  # Beat 2 more late
                2.0: -0.02,  # Beat 3 (the drop) most laid back
                3.0: -0.01,  # Beat 4 slightly late
                0.5: 0.01,   # Upbeats slightly early
                1.5: 0.01,
                2.5: 0.01,
                3.5: 0.01,
            }
        elif style == "steppers":
            # Steppers: more on the beat, driving
            groove = {
                0.0: 0.0,    # On the beat
                1.0: 0.0,
                2.0: 0.0,
                3.0: 0.0,
                0.5: 0.005,  # Slight emphasis on upbeats
                1.5: 0.005,
                2.5: 0.005,
                3.5: 0.005,
            }
        elif style == "rockers":
            # Rockers: syncopated, rocking feel
            groove = {
                0.0: 0.01,   # Beat 1 slightly early
                1.0: -0.01,  # Beat 2 slightly late
                2.0: 0.015,  # Beat 3 slightly early
                3.0: -0.005, # Beat 4 on time
                3.5: 0.02,   # 4+ early (the rocker)
            }
        else:
            groove = {}

        # Apply groove
        result = []
        for note in notes:
            beat_in_bar = note.start_beat % 4
            offset = groove.get(beat_in_bar, 0.0)

            humanized_note = MIDINote(
                note=note.note,
                velocity=note.velocity,
                start_beat=note.start_beat + offset,
                duration=note.duration,
                channel=note.channel,
            )
            result.append(humanized_note)

        return result

    def add_dynamics(
        self,
        notes: List[MIDINote],
        curve: str = "crescendo",
    ) -> List[MIDINote]:
        """
        Apply dynamic curve to notes.

        Args:
            notes: List of notes
            curve: Type of dynamic curve ('crescendo', 'diminuendo', 'wave')

        Returns:
            Notes with dynamics applied
        """
        if not notes:
            return notes

        result = []
        num_notes = len(notes)

        for i, note in enumerate(notes):
            # Calculate position in sequence (0.0 to 1.0)
            position = i / max(1, num_notes - 1)

            # Calculate dynamic multiplier
            if curve == "crescendo":
                multiplier = 0.7 + (position * 0.3)  # 0.7 to 1.0
            elif curve == "diminuendo":
                multiplier = 1.0 - (position * 0.3)  # 1.0 to 0.7
            elif curve == "wave":
                multiplier = 0.85 + (0.15 * np.sin(position * np.pi * 2))
            else:
                multiplier = 1.0

            # Apply multiplier to velocity
            new_velocity = int(note.velocity * multiplier)
            new_velocity = max(1, min(127, new_velocity))

            humanized_note = MIDINote(
                note=note.note,
                velocity=new_velocity,
                start_beat=note.start_beat,
                duration=note.duration,
                channel=note.channel,
            )
            result.append(humanized_note)

        return result

    def apply_accent_pattern(
        self,
        notes: List[MIDINote],
        accent_beats: List[float],
        accent_boost: int = 15,
    ) -> List[MIDINote]:
        """
        Apply accents to specific beat positions.

        Args:
            notes: List of notes
            accent_beats: Beat positions to accent (e.g., [0.0, 2.0] for beats 1 and 3)
            accent_boost: Velocity increase for accents

        Returns:
            Notes with accents applied
        """
        result = []

        for note in notes:
            beat_in_bar = note.start_beat % 4

            # Check if this beat should be accented
            is_accent = any(
                abs(beat_in_bar - accent_beat) < 0.1
                for accent_beat in accent_beats
            )

            velocity = note.velocity
            if is_accent:
                velocity = min(127, velocity + accent_boost)

            humanized_note = MIDINote(
                note=note.note,
                velocity=velocity,
                start_beat=note.start_beat,
                duration=note.duration,
                channel=note.channel,
            )
            result.append(humanized_note)

        return result


def create_reggae_humanizer(style: str = "one_drop") -> MIDIHumanizer:
    """
    Create a humanizer with reggae-appropriate settings.

    Args:
        style: Reggae style (one_drop, steppers, rockers, etc.)

    Returns:
        Configured MIDIHumanizer
    """
    if style == "one_drop":
        config = HumanizeConfig(
            timing_variance=0.015,  # Moderate timing variation
            velocity_variance=0.12,  # Moderate velocity variation
            swing_amount=0.0,        # No swing in reggae
        )
    elif style == "steppers":
        config = HumanizeConfig(
            timing_variance=0.008,   # Tighter timing
            velocity_variance=0.10,  # Less velocity variation
            swing_amount=0.0,
        )
    elif style == "rockers":
        config = HumanizeConfig(
            timing_variance=0.020,   # More loose timing
            velocity_variance=0.15,  # More velocity variation
            swing_amount=0.0,
        )
    else:
        config = HumanizeConfig()

    return MIDIHumanizer(config)


__all__ = [
    "HumanizeConfig",
    "MIDIHumanizer",
    "create_reggae_humanizer",
]
