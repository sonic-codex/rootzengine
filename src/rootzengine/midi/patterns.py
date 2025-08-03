"""MIDI pattern generation module."""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import mido
import numpy as np
import pretty_midi

from src.rootzengine.core.config import settings
from src.rootzengine.core.exceptions import MIDIConversionError

logger = logging.getLogger(__name__)


class MIDIPatternGenerator:
    """Generates reggae MIDI patterns based on structure information."""
    
    def __init__(self, tempo: float = 80.0):
        """Initialize the MIDI pattern generator.
        
        Args:
            tempo: Tempo in BPM
        """
        self.tempo = tempo
        
        # Define standard reggae patterns
        self.drum_patterns = {
            "one_drop": self._create_one_drop_pattern,
            "steppers": self._create_steppers_pattern,
            "rockers": self._create_rockers_pattern
        }
        
        self.bass_patterns = {
            "simple": self._create_simple_bass_pattern,
            "walking": self._create_walking_bass_pattern,
            "complex": self._create_complex_bass_pattern
        }
        
        self.skank_patterns = {
            "traditional": self._create_traditional_skank_pattern,
            "bubble": self._create_bubble_skank_pattern,
            "offbeat": self._create_offbeat_skank_pattern
        }
    
    def generate_pattern(
        self,
        output_path: Union[str, Path],
        pattern_type: str = "one_drop",
        key: str = "C",
        mode: str = "major",
        measures: int = 4,
        bass_style: str = "simple",
        skank_style: str = "traditional",
        include_drums: bool = True,
        include_bass: bool = True,
        include_skank: bool = True
    ) -> Path:
        """Generate a reggae MIDI pattern.
        
        Args:
            output_path: Path to save the MIDI file
            pattern_type: Type of riddim pattern ("one_drop", "steppers", "rockers")
            key: Root key (e.g., "C", "D#")
            mode: Mode ("major" or "minor")
            measures: Number of measures to generate
            bass_style: Bass pattern style
            skank_style: Skank (guitar/keys) pattern style
            include_drums: Whether to include drums
            include_bass: Whether to include bass
            include_skank: Whether to include skank
            
        Returns:
            Path to the saved MIDI file
            
        Raises:
            MIDIConversionError: If pattern generation fails
        """
        try:
            # Create MIDI object
            midi_data = pretty_midi.PrettyMIDI(initial_tempo=self.tempo)
            
            # Create instruments
            instruments = {}
            
            if include_drums:
                drums = pretty_midi.Instrument(program=0, is_drum=True, name="Drums")
                instruments["drums"] = drums
                
                # Get the appropriate drum pattern function
                drum_pattern_func = self.drum_patterns.get(
                    pattern_type, self._create_one_drop_pattern
                )
                
                # Generate drum pattern
                drum_pattern_func(drums, measures)
                
                # Add to MIDI
                midi_data.instruments.append(drums)
            
            if include_bass:
                bass_program = pretty_midi.instrument_name_to_program('Electric Bass (finger)')
                bass = pretty_midi.Instrument(program=bass_program, name="Bass")
                instruments["bass"] = bass
                
                # Get the appropriate bass pattern function
                bass_pattern_func = self.bass_patterns.get(
                    bass_style, self._create_simple_bass_pattern
                )
                
                # Generate bass pattern based on key and mode
                bass_pattern_func(bass, key, mode, measures)
                
                # Add to MIDI
                midi_data.instruments.append(bass)
            
            if include_skank:
                # Keys (piano or organ) for skank
                if skank_style == "bubble":
                    # Use organ for bubble pattern
                    organ_program = pretty_midi.instrument_name_to_program('Rock Organ')
                    skank = pretty_midi.Instrument(program=organ_program, name="Organ")
                else:
                    # Use guitar for traditional/offbeat patterns
                    guitar_program = pretty_midi.instrument_name_to_program('Electric Guitar (clean)')
                    skank = pretty_midi.Instrument(program=guitar_program, name="Guitar")
                
                instruments["skank"] = skank
                
                # Get the appropriate skank pattern function
                skank_pattern_func = self.skank_patterns.get(
                    skank_style, self._create_traditional_skank_pattern
                )
                
                # Generate skank pattern based on key and mode
                skank_pattern_func(skank, key, mode, measures)
                
                # Add to MIDI
                midi_data.instruments.append(skank)
            
            # Save the MIDI file
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            midi_data.write(str(output_path))
            
            logger.info(f"Generated {pattern_type} pattern and saved to {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating MIDI pattern: {str(e)}")
            raise MIDIConversionError(f"Failed to generate MIDI pattern: {str(e)}")
    
    def _create_one_drop_pattern(self, drums: pretty_midi.Instrument, measures: int) -> None:
        """Create a one drop drum pattern.
        
        Args:
            drums: Drum instrument to add notes to
            measures: Number of measures to generate
        """
        # One drop typically emphasizes beat 3 (kick) in a 4-beat measure
        beat_duration = 60.0 / self.tempo
        
        for bar in range(measures):
            bar_start = bar * 4 * beat_duration
            
            # Beat 3: Kick drum
            kick_note = pretty_midi.Note(
                velocity=100,
                pitch=36,  # Bass drum
                start=bar_start + (2 * beat_duration),
                end=bar_start + (2 * beat_duration) + 0.1
            )
            drums.notes.append(kick_note)
            
            # Beat 3: Snare with kick
            snare_note = pretty_midi.Note(
                velocity=90,
                pitch=38,  # Snare
                start=bar_start + (2 * beat_duration),
                end=bar_start + (2 * beat_duration) + 0.1
            )
            drums.notes.append(snare_note)
            
            # Hi-hat on every beat
            for beat in range(4):
                hi_hat_note = pretty_midi.Note(
                    velocity=80,
                    pitch=42,  # Closed hi-hat
                    start=bar_start + (beat * beat_duration),
                    end=bar_start + (beat * beat_duration) + 0.05
                )
                drums.notes.append(hi_hat_note)
                
                # Offbeat hi-hats
                if beat < 3:  # Don't add after beat 4
                    offbeat_hi_hat = pretty_midi.Note(
                        velocity=70,
                        pitch=42,  # Closed hi-hat
                        start=bar_start + (beat * beat_duration) + (beat_duration / 2),
                        end=bar_start + (beat * beat_duration) + (beat_duration / 2) + 0.05
                    )
                    drums.notes.append(offbeat_hi_hat)
    
    def _create_steppers_pattern(self, drums: pretty_midi.Instrument, measures: int) -> None:
        """Create a steppers drum pattern.
        
        Args:
            drums: Drum instrument to add notes to
            measures: Number of measures to generate
        """
        # Steppers pattern (four on the floor)
        beat_duration = 60.0 / self.tempo
        
        for bar in range(measures):
            bar_start = bar * 4 * beat_duration
            
            for beat in range(4):
                # Kick on every beat
                kick_note = pretty_midi.Note(
                    velocity=100,
                    pitch=36,  # Bass drum
                    start=bar_start + (beat * beat_duration),
                    end=bar_start + (beat * beat_duration) + 0.1
                )
                drums.notes.append(kick_note)
                
                # Snare on beats 2 and 4
                if beat == 1 or beat == 3:
                    snare_note = pretty_midi.Note(
                        velocity=90,
                        pitch=38,  # Snare
                        start=bar_start + (beat * beat_duration),
                        end=bar_start + (beat * beat_duration) + 0.1
                    )
                    drums.notes.append(snare_note)
                
                # Hi-hat on every beat
                hi_hat_note = pretty_midi.Note(
                    velocity=80,
                    pitch=42,  # Closed hi-hat
                    start=bar_start + (beat * beat_duration),
                    end=bar_start + (beat * beat_duration) + 0.05
                )
                drums.notes.append(hi_hat_note)
    
    def _create_rockers_pattern(self, drums: pretty_midi.Instrument, measures: int) -> None:
        """Create a rockers drum pattern.
        
        Args:
            drums: Drum instrument to add notes to
            measures: Number of measures to generate
        """
        # Rockers pattern (emphasis on 1 and 3)
        beat_duration = 60.0 / self.tempo
        
        for bar in range(measures):
            bar_start = bar * 4 * beat_duration
            
            for beat in range(4):
                if beat == 0 or beat == 2:
                    # Kick on beats 1 and 3
                    kick_note = pretty_midi.Note(
                        velocity=100,
                        pitch=36,  # Bass drum
                        start=bar_start + (beat * beat_duration),
                        end=bar_start + (beat * beat_duration) + 0.1
                    )
                    drums.notes.append(kick_note)
                
                # Snare on beats 2 and 4
                if beat == 1 or beat == 3:
                    snare_note = pretty_midi.Note(
                        velocity=90,
                        pitch=38,  # Snare
                        start=bar_start + (beat * beat_duration),
                        end=bar_start + (beat * beat_duration) + 0.1
                    )
                    drums.notes.append(snare_note)
                
                # Hi-hat on every beat
                hi_hat_note = pretty_midi.Note(
                    velocity=80,
                    pitch=42,  # Closed hi-hat
                    start=bar_start + (beat * beat_duration),
                    end=bar_start + (beat * beat_duration) + 0.05
                )
                drums.notes.append(hi_hat_note)
    
    def _create_simple_bass_pattern(
        self,
        bass: pretty_midi.Instrument,
        key: str,
        mode: str,
        measures: int
    ) -> None:
        """Create a simple bass pattern.
        
        Args:
            bass: Bass instrument to add notes to
            key: Root key
            mode: Mode (major or minor)
            measures: Number of measures to generate
        """
        beat_duration = 60.0 / self.tempo
        duration = beat_duration * 0.8  # Slightly shorter than full beat
        
        # Convert key to MIDI pitch
        root_map = {
            "C": 36, "C#": 37, "D": 38, "D#": 39, "E": 40, "F": 41,
            "F#": 42, "G": 43, "G#": 44, "A": 45, "A#": 46, "B": 47
        }
        root_pitch = root_map.get(key, 36)  # Default to C
        
        # Get scale degrees based on mode
        if mode.lower() == "major":
            scale_steps = [0, 2, 4, 5, 7, 9, 11]  # Major scale
        else:
            scale_steps = [0, 2, 3, 5, 7, 8, 10]  # Natural minor scale
        
        # Generate a simple one drop bass pattern
        for bar in range(measures):
            bar_start = bar * 4 * beat_duration
            
            # Root on beat 1
            note = pretty_midi.Note(
                velocity=80,
                pitch=root_pitch,
                start=bar_start,
                end=bar_start + duration
            )
            bass.notes.append(note)
            
            # Fifth on beat 3
            fifth_pitch = root_pitch + scale_steps[4]
            note = pretty_midi.Note(
                velocity=80,
                pitch=fifth_pitch,
                start=bar_start + (2 * beat_duration),
                end=bar_start + (2 * beat_duration) + duration
            )
            bass.notes.append(note)
    
    def _create_walking_bass_pattern(
        self,
        bass: pretty_midi.Instrument,
        key: str,
        mode: str,
        measures: int
    ) -> None:
        """Create a walking bass pattern.
        
        Args:
            bass: Bass instrument to add notes to
            key: Root key
            mode: Mode (major or minor)
            measures: Number of measures to generate
        """
        beat_duration = 60.0 / self.tempo
        duration = beat_duration * 0.8
        
        # Convert key to MIDI pitch
        root_map = {
            "C": 36, "C#": 37, "D": 38, "D#": 39, "E": 40, "F": 41,
            "F#": 42, "G": 43, "G#": 44, "A": 45, "A#": 46, "B": 47
        }
        root_pitch = root_map.get(key, 36)
        
        # Get scale degrees based on mode
        if mode.lower() == "major":
            scale_steps = [0, 2, 4, 5, 7, 9, 11]  # Major scale
        else:
            scale_steps = [0, 2, 3, 5, 7, 8, 10]  # Natural minor scale
        
        # Walking bass patterns for alternating measures
        pattern_a = [0, 4, 0, 2]  # Root, fifth, root, third
        pattern_b = [0, 2, 4, 5]  # Root, third, fifth, sixth
        
        for bar in range(measures):
            bar_start = bar * 4 * beat_duration
            
            # Alternate between patterns
            pattern = pattern_a if bar % 2 == 0 else pattern_b
            
            # Create notes for each beat
            for beat in range(4):
                scale_idx = pattern[beat]
                note_pitch = root_pitch + scale_steps[scale_idx]
                
                note = pretty_midi.Note(
                    velocity=80,
                    pitch=note_pitch,
                    start=bar_start + (beat * beat_duration),
                    end=bar_start + (beat * beat_duration) + duration
                )
                bass.notes.append(note)
    
    def _create_complex_bass_pattern(
        self,
        bass: pretty_midi.Instrument,
        key: str,
        mode: str,
        measures: int
    ) -> None:
        """Create a more complex bass pattern.
        
        Args:
            bass: Bass instrument to add notes to
            key: Root key
            mode: Mode (major or minor)
            measures: Number of measures to generate
        """
        beat_duration = 60.0 / self.tempo
        
        # Convert key to MIDI pitch
        root_map = {
            "C": 36, "C#": 37, "D": 38, "D#": 39, "E": 40, "F": 41,
            "F#": 42, "G": 43, "G#": 44, "A": 45, "A#": 46, "B": 47
        }
        root_pitch = root_map.get(key, 36)
        
        # Get scale degrees based on mode
        if mode.lower() == "major":
            scale_steps = [0, 2, 4, 5, 7, 9, 11]  # Major scale
        else:
            scale_steps = [0, 2, 3, 5, 7, 8, 10]  # Natural minor scale
        
        # Complex patterns with eighth notes and syncopation
        for bar in range(measures):
            bar_start = bar * 4 * beat_duration
            
            if bar % 4 == 0:  # Pattern 1
                # Beat 1: Root
                note = pretty_midi.Note(
                    velocity=85,
                    pitch=root_pitch,
                    start=bar_start,
                    end=bar_start + (beat_duration * 0.75)
                )
                bass.notes.append(note)
                
                # Beat 1+: Fifth below root
                lower_fifth = root_pitch - scale_steps[4]
                note = pretty_midi.Note(
                    velocity=75,
                    pitch=lower_fifth,
                    start=bar_start + (beat_duration * 0.75),
                    end=bar_start + beat_duration
                )
                bass.notes.append(note)
                
                # Beat 2: Root
                note = pretty_midi.Note(
                    velocity=80,
                    pitch=root_pitch,
                    start=bar_start + beat_duration,
                    end=bar_start + (beat_duration * 1.75)
                )
                bass.notes.append(note)
                
                # Beat 2+: Third
                third_pitch = root_pitch + scale_steps[2]
                note = pretty_midi.Note(
                    velocity=75,
                    pitch=third_pitch,
                    start=bar_start + (beat_duration * 1.75),
                    end=bar_start + (beat_duration * 2)
                )
                bass.notes.append(note)
                
                # Beat 3: Fifth
                fifth_pitch = root_pitch + scale_steps[4]
                note = pretty_midi.Note(
                    velocity=85,
                    pitch=fifth_pitch,
                    start=bar_start + (beat_duration * 2),
                    end=bar_start + (beat_duration * 3)
                )
                bass.notes.append(note)
                
                # Beat 4: Seventh -> Root
                seventh_pitch = root_pitch + scale_steps[6]
                note = pretty_midi.Note(
                    velocity=80,
                    pitch=seventh_pitch,
                    start=bar_start + (beat_duration * 3),
                    end=bar_start + (beat_duration * 3.5)
                )
                bass.notes.append(note)
                
                # Beat 4+: Sixth
                sixth_pitch = root_pitch + scale_steps[5]
                note = pretty_midi.Note(
                    velocity=75,
                    pitch=sixth_pitch,
                    start=bar_start + (beat_duration * 3.5),
                    end=bar_start + (beat_duration * 4)
                )
                bass.notes.append(note)
                
            elif bar % 4 == 1:  # Pattern 2
                # Beat 1: Fourth
                fourth_pitch = root_pitch + scale_steps[3]
                note = pretty_midi.Note(
                    velocity=80,
                    pitch=fourth_pitch,
                    start=bar_start,
                    end=bar_start + (beat_duration * 1.5)
                )
                bass.notes.append(note)
                
                # Beat 2+: Fifth
                fifth_pitch = root_pitch + scale_steps[4]
                note = pretty_midi.Note(
                    velocity=80,
                    pitch=fifth_pitch,
                    start=bar_start + (beat_duration * 1.5),
                    end=bar_start + (beat_duration * 2)
                )
                bass.notes.append(note)
                
                # Beat 3: Root
                note = pretty_midi.Note(
                    velocity=85,
                    pitch=root_pitch,
                    start=bar_start + (beat_duration * 2),
                    end=bar_start + (beat_duration * 3)
                )
                bass.notes.append(note)
                
                # Beat 4: Fifth
                fifth_pitch = root_pitch + scale_steps[4]
                note = pretty_midi.Note(
                    velocity=80,
                    pitch=fifth_pitch,
                    start=bar_start + (beat_duration * 3),
                    end=bar_start + (beat_duration * 4)
                )
                bass.notes.append(note)
                
            else:  # Pattern 3 and 4 (similar with variations)
                # Basic pattern but with variations in timing
                note_pitches = [
                    root_pitch,  # Root
                    root_pitch + scale_steps[4],  # Fifth
                    root_pitch,  # Root
                    root_pitch + (scale_steps[2] if bar % 2 == 0 else scale_steps[3])  # Third or Fourth
                ]
                
                # Add syncopation by shifting some notes slightly
                offsets = [0, 0, 0.25, -0.25] if bar % 2 == 0 else [0, 0.25, 0, 0]
                durations = [0.9, 0.9, 0.7, 0.7] if bar % 2 == 0 else [0.8, 0.7, 0.8, 0.9]
                
                for beat in range(4):
                    start = bar_start + (beat * beat_duration) + (offsets[beat] * beat_duration)
                    dur = durations[beat] * beat_duration
                    
                    note = pretty_midi.Note(
                        velocity=80,
                        pitch=note_pitches[beat],
                        start=start,
                        end=min(start + dur, bar_start + (beat_duration * 4))
                    )
                    bass.notes.append(note)
    
    def _create_traditional_skank_pattern(
        self,
        skank: pretty_midi.Instrument,
        key: str,
        mode: str,
        measures: int
    ) -> None:
        """Create a traditional reggae skank pattern.
        
        Args:
            skank: Instrument to add skank notes to
            key: Root key
            mode: Mode (major or minor)
            measures: Number of measures to generate
        """
        beat_duration = 60.0 / self.tempo
        duration = beat_duration * 0.4  # Short stabs for skanks
        
        # Convert key to MIDI pitch
        root_map = {
            "C": 60, "C#": 61, "D": 62, "D#": 63, "E": 64, "F": 65,
            "F#": 66, "G": 67, "G#": 68, "A": 69, "A#": 70, "B": 71
        }
        root_pitch = root_map.get(key, 60)  # Default to middle C
        
        # Get triad notes based on mode
        if mode.lower() == "major":
            chord_notes = [0, 4, 7]  # Major triad (1-3-5)
        else:
            chord_notes = [0, 3, 7]  # Minor triad (1-b3-5)
        
        # Create traditional skank pattern (offbeats only)
        for bar in range(measures):
            bar_start = bar * 4 * beat_duration
            
            # Generate a chord for each offbeat
            for beat in range(4):
                # Offbeat skank (the "and" of each beat)
                offbeat_time = bar_start + (beat * beat_duration) + (beat_duration / 2)
                
                # Create a triad chord on each offbeat
                for note_offset in chord_notes:
                    note = pretty_midi.Note(
                        velocity=70,
                        pitch=root_pitch + note_offset,
                        start=offbeat_time,
                        end=offbeat_time + duration
                    )
                    skank.notes.append(note)
    
    def _create_bubble_skank_pattern(
        self,
        skank: pretty_midi.Instrument,
        key: str,
        mode: str,
        measures: int
    ) -> None:
        """Create a bubble organ pattern.
        
        Args:
            skank: Instrument to add bubble organ notes to
            key: Root key
            mode: Mode (major or minor)
            measures: Number of measures to generate
        """
        beat_duration = 60.0 / self.tempo
        
        # Convert key to MIDI pitch
        root_map = {
            "C": 60, "C#": 61, "D": 62, "D#": 63, "E": 64, "F": 65,
            "F#": 66, "G": 67, "G#": 68, "A": 69, "A#": 70, "B": 71
        }
        root_pitch = root_map.get(key, 60)
        
        # Get triad notes based on mode
        if mode.lower() == "major":
            chord_notes = [0, 4, 7, 12]  # Major triad with octave
        else:
            chord_notes = [0, 3, 7, 12]  # Minor triad with octave
        
        # Create bubble pattern
        # Bubble pattern typically has alternating chords on beats 2, 2+, 4, 4+
        for bar in range(measures):
            bar_start = bar * 4 * beat_duration
            
            # Beats 2, 2+, 4, 4+
            bubble_times = [
                bar_start + beat_duration,  # Beat 2
                bar_start + beat_duration + (beat_duration / 2),  # Beat 2+
                bar_start + (3 * beat_duration),  # Beat 4
                bar_start + (3 * beat_duration) + (beat_duration / 2)  # Beat 4+
            ]
            
            # Alternate between two chord voicings
            for i, time in enumerate(bubble_times):
                duration = beat_duration * 0.4
                
                # Alternate between different chord inversions for the bubble effect
                if i % 2 == 0:
                    # Root position
                    chord = [root_pitch + note for note in chord_notes]
                else:
                    # First inversion
                    first_inv = [root_pitch + 4, root_pitch + 7, root_pitch + 12, root_pitch + 16]
                    if mode.lower() != "major":
                        first_inv = [root_pitch + 3, root_pitch + 7, root_pitch + 12, root_pitch + 15]
                    chord = first_inv
                
                # Create the chord
                for pitch in chord:
                    note = pretty_midi.Note(
                        velocity=70,
                        pitch=pitch,
                        start=time,
                        end=time + duration
                    )
                    skank.notes.append(note)
    
    def _create_offbeat_skank_pattern(
        self,
        skank: pretty_midi.Instrument,
        key: str,
        mode: str,
        measures: int
    ) -> None:
        """Create an offbeat skank pattern with eighth note variations.
        
        Args:
            skank: Instrument to add skank notes to
            key: Root key
            mode: Mode (major or minor)
            measures: Number of measures to generate
        """
        # Similar to traditional but with some variations
        beat_duration = 60.0 / self.tempo
        duration = beat_duration * 0.3  # Short stabs
        
        # Convert key to MIDI pitch
        root_map = {
            "C": 60, "C#": 61, "D": 62, "D#": 63, "E": 64, "F": 65,
            "F#": 66, "G": 67, "G#": 68, "A": 69, "A#": 70, "B": 71
        }
        root_pitch = root_map.get(key, 60)
        
        # Get chord notes based on mode
        if mode.lower() == "major":
            chord_notes = [0, 4, 7, 12]  # Major triad with octave
        else:
            chord_notes = [0, 3, 7, 12]  # Minor triad with octave
        
        # Create offbeat pattern with variations
        for bar in range(measures):
            bar_start = bar * 4 * beat_duration
            
            # Standard offbeats
            offbeats = [
                bar_start + (beat_duration * 0.5),  # 1+
                bar_start + (beat_duration * 1.5),  # 2+
                bar_start + (beat_duration * 2.5),  # 3+
                bar_start + (beat_duration * 3.5),  # 4+
            ]
            
            # Every other bar, add some additional accents
            additional_accents = []
            if bar % 2 == 1:
                additional_accents = [
                    bar_start + (beat_duration * 2.75),  # 3+ eighth
                    bar_start + (beat_duration * 3.25),  # 4- eighth
                ]
            
            # Combine all skank times
            skank_times = offbeats + additional_accents
            
            # Generate chords at each skank time
            for time in skank_times:
                for note_offset in chord_notes:
                    note = pretty_midi.Note(
                        velocity=70,
                        pitch=root_pitch + note_offset,
                        start=time,
                        end=time + duration
                    )
                    skank.notes.append(note)
