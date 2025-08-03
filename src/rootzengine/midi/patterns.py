"""
Module for generating reggae-specific MIDI patterns.
"""
import logging
from pathlib import Path
from typing import Dict, List, Union

import pretty_midi

logger = logging.getLogger(__name__)


class MIDIPatternGenerator:
    """Generates MIDI patterns for different reggae styles."""

    def __init__(self, tempo: float = 120.0):
        """
        Initializes the pattern generator.

        Args:
            tempo: The tempo in BPM for the generated patterns.
        """
        self.tempo = tempo
        self.beat_duration = 60.0 / self.tempo

    def generate_pattern(
        self,
        output_path: Union[str, Path],
        pattern_type: str,
        key: str,
        mode: str,
        measures: int,
        bass_style: str,
        skank_style: str,
    ) -> Path:
        """
        Generates a complete MIDI file with a specified reggae pattern.

        Args:
            output_path: Path to save the generated MIDI file.
            pattern_type: The riddim type (e.g., 'one_drop', 'steppers').
            key: The root key (e.g., 'C', 'G#').
            mode: The mode ('major' or 'minor').
            measures: The number of measures to generate.
            bass_style: The style of the bassline.
            skank_style: The style of the skank pattern.

        Returns:
            The path to the saved MIDI file.
        """
        midi_data = pretty_midi.PrettyMIDI(initial_tempo=self.tempo)
        drums = pretty_midi.Instrument(program=0, is_drum=True, name="Drums")
        bass = pretty_midi.Instrument(
            program=pretty_midi.instrument_name_to_program("Electric Bass (finger)"),
            name="Bass",
        )

        # Key and scale setup
        root_pitch = pretty_midi.note_name_to_number(f"{key}4")
        scale_steps = (
            [0, 2, 4, 5, 7, 9, 11]
            if mode == "major"
            else [0, 2, 3, 5, 7, 8, 10]
        )

        for bar in range(measures):
            bar_start_time = bar * 4 * self.beat_duration
            self._create_drum_pattern(drums, bar_start_time, pattern_type)
            self._create_bassline(bass, bar_start_time, root_pitch, scale_steps, bass_style)

        midi_data.instruments.append(drums)
        midi_data.instruments.append(bass)

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        midi_data.write(str(output_path))
        logger.info(f"Generated MIDI pattern saved to {output_path}")
        return output_path

    def _create_drum_pattern(
        self, drums: pretty_midi.Instrument, bar_start_time: float, pattern_type: str
    ):
        """Creates a single bar of a drum pattern."""
        # Hi-hat on every 8th note
        for i in range(8):
            time = bar_start_time + i * (self.beat_duration / 2)
            velocity = 80 if i % 2 == 0 else 60
            drums.notes.append(
                pretty_midi.Note(
                    velocity=velocity, pitch=42, start=time, end=time + 0.1
                )  # Closed Hi-hat
            )

        if pattern_type == "one_drop":
            # Kick and snare on beat 3
            time = bar_start_time + 2 * self.beat_duration
            drums.notes.append(
                pretty_midi.Note(
                    velocity=100, pitch=36, start=time, end=time + 0.1
                )  # Kick
            )
            drums.notes.append(
                pretty_midi.Note(
                    velocity=90, pitch=38, start=time, end=time + 0.1
                )  # Snare
            )
        elif pattern_type == "steppers":
            # Kick on every beat, snare on 2 and 4
            for beat in range(4):
                time = bar_start_time + beat * self.beat_duration
                drums.notes.append(
                    pretty_midi.Note(
                        velocity=100, pitch=36, start=time, end=time + 0.1
                    )  # Kick
                )
                if beat in [1, 3]:
                    drums.notes.append(
                        pretty_midi.Note(
                            velocity=90, pitch=38, start=time, end=time + 0.1
                        )  # Snare
                    )
        else:  # Default to rockers
            # Kick on 1 and 3, snare on 2 and 4
            for beat in range(4):
                time = bar_start_time + beat * self.beat_duration
                if beat in [0, 2]:
                    drums.notes.append(
                        pretty_midi.Note(
                            velocity=100, pitch=36, start=time, end=time + 0.1
                        )  # Kick
                    )
                if beat in [1, 3]:
                    drums.notes.append(
                        pretty_midi.Note(
                            velocity=90, pitch=38, start=time, end=time + 0.1
                        )  # Snare
                    )

    def _create_bassline(
        self,
        bass: pretty_midi.Instrument,
        bar_start_time: float,
        root_pitch: int,
        scale_steps: List[int],
        bass_style: str,
    ):
        """Creates a single bar of a bassline."""
        bass_octave = -12  # Drop the bassline by one octave

        if bass_style == "simple":
            # Root on beat 1, fifth on beat 3
            p1 = root_pitch + bass_octave
            t1 = bar_start_time
            bass.notes.append(
                pretty_midi.Note(velocity=90, pitch=p1, start=t1, end=t1 + self.beat_duration)
            )

            p2 = root_pitch + scale_steps[4] + bass_octave
            t2 = bar_start_time + 2 * self.beat_duration
            bass.notes.append(
                pretty_midi.Note(velocity=85, pitch=p2, start=t2, end=t2 + self.beat_duration)
            )
        else:  # Default to a walking-style pattern
            # Walk through root, third, fifth, sixth
            note_indices = [0, 2, 4, 5]
            for beat in range(4):
                pitch = root_pitch + scale_steps[note_indices[beat]] + bass_octave
                time = bar_start_time + beat * self.beat_duration
                bass.notes.append(
                    pretty_midi.Note(
                        velocity=80, pitch=pitch, start=time, end=time + self.beat_duration * 0.9
                    )
                )