"""MIDI pattern generation for reggae styles."""

import logging
from typing import Dict, Optional

import numpy as np
import pretty_midi

logger = logging.getLogger(__name__)


class MIDIPatternGenerator:
    """Generates MIDI patterns for different reggae styles."""

    def __init__(self, tempo: float = 120.0):
        """Initialize the MIDI pattern generator.

        Args:
            tempo: The tempo in BPM for the generated patterns.
        """
        self.tempo = tempo
        self.tick_rate = 480  # Ticks per quarter note, standard for MIDI

    def generate_pattern(
        self,
        pattern_type: str,
        key: str,
        mode: str,
        measures: int,
        bass_style: str,
        skank_style: str,
    ) -> pretty_midi.PrettyMIDI:
        """Generate a complete MIDI pattern for a section.

        Args:
            pattern_type: The riddim type (e.g., 'one_drop', 'steppers').
            key: The root key of the section.
            mode: The mode ('major' or 'minor').
            measures: The number of measures to generate.
            bass_style: The style of the bassline.
            skank_style: The style of the skank pattern.

        Returns:
            A PrettyMIDI object containing the generated pattern.
        """
        midi_data = pretty_midi.PrettyMIDI(initial_tempo=self.tempo)
        drums = pretty_midi.Instrument(program=0, is_drum=True, name="Drums")
        bass = pretty_midi.Instrument(program=33, name="Electric Bass")  # 33: Electric Bass (finger)

        # This is a placeholder for a more sophisticated pattern generation logic.
        # In a real implementation, this would generate varied and musical patterns.
        
        # Simple drum pattern based on riddim type
        self._add_drum_pattern(drums, pattern_type, measures)

        # Simple bassline
        self._add_bassline(bass, key, mode, measures, bass_style)

        midi_data.instruments.append(drums)
        midi_data.instruments.append(bass)

        return midi_data

    def _add_drum_pattern(self, instrument: pretty_midi.Instrument, pattern_type: str, measures: int):
        """Adds a drum pattern to a MIDI instrument."""
        # Note numbers for General MIDI drums
        kick = 36
        snare = 38
        hi_hat_closed = 42

        seconds_per_beat = 60.0 / self.tempo

        for measure in range(measures):
            measure_start_time = measure * 4 * seconds_per_beat

            # Hi-hat on every 8th note
            for i in range(8):
                hat_time = measure_start_time + i * (seconds_per_beat / 2)
                instrument.notes.append(pretty_midi.Note(
                    velocity=80, pitch=hi_hat_closed, start=hat_time, end=hat_time + 0.1
                ))

            # Riddim-specific kick/snare
            if pattern_type == "one_drop":
                # Snare on beat 3
                snare_time = measure_start_time + 2 * seconds_per_beat
                instrument.notes.append(pretty_midi.Note(
                    velocity=100, pitch=snare, start=snare_time, end=snare_time + 0.1
                ))
            elif pattern_type == "steppers":
                # Kick on every beat
                for i in range(4):
                    kick_time = measure_start_time + i * seconds_per_beat
                    instrument.notes.append(pretty_midi.Note(
                        velocity=110, pitch=kick, start=kick_time, end=kick_time + 0.1
                    ))
            else:  # Default to a simple rockers beat
                # Kick on 1, snare on 3
                kick_time = measure_start_time
                snare_time = measure_start_time + 2 * seconds_per_beat
                instrument.notes.append(pretty_midi.Note(
                    velocity=110, pitch=kick, start=kick_time, end=kick_time + 0.1
                ))
                instrument.notes.append(pretty_midi.Note(
                    velocity=100, pitch=snare, start=snare_time, end=snare_time + 0.1
                ))

    def _add_bassline(self, instrument: pretty_midi.Instrument, key: str, mode: str, measures: int, style: str):
        """Adds a bassline to a MIDI instrument."""
        # This is a highly simplified placeholder.
        # A real implementation would use music theory to generate compelling basslines.
        key_map = {"C": 60, "C#": 61, "D": 62, "D#": 63, "E": 64, "F": 65, "F#": 66, "G": 67, "G#": 68, "A": 69, "A#": 70, "B": 71}
        root_note = key_map.get(key.upper(), 60) - 24  # Go down two octaves for bass

        seconds_per_beat = 60.0 / self.tempo

        for measure in range(measures):
            measure_start_time = measure * 4 * seconds_per_beat
            if style == "simple":
                # Play root note on beat 1
                note_time = measure_start_time
                instrument.notes.append(pretty_midi.Note(
                    velocity=90, pitch=root_note, start=note_time, end=note_time + seconds_per_beat
                ))
            else: # complex/walking
                # Play root on 1, fifth on 3
                fifth_note = root_note + 7
                instrument.notes.append(pretty_midi.Note(
                    velocity=90, pitch=root_note, start=measure_start_time, end=measure_start_time + seconds_per_beat
                ))
                instrument.notes.append(pretty_midi.Note(
                    velocity=90, pitch=fifth_note, start=measure_start_time + 2 * seconds_per_beat, end=measure_start_time + 3 * seconds_per_beat
                ))