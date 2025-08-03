"""Audio to MIDI conversion module."""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Union

import librosa
import mido
import numpy as np
import pretty_midi

from src.rootzengine.core.config import settings
from src.rootzengine.core.exceptions import MIDIConversionError

logger = logging.getLogger(__name__)


class AudioToMIDIConverter:
    """Converts audio to MIDI with structural awareness."""
    
    def __init__(
        self,
        sample_rate: Optional[int] = None,
        hop_length: Optional[int] = None,
    ):
        """Initialize the audio to MIDI converter.
        
        Args:
            sample_rate: Sample rate for audio processing
            hop_length: Hop length for FFT
        """
        self.sample_rate = sample_rate or settings.audio.sample_rate
        self.hop_length = hop_length or settings.audio.hop_length
    
    def convert_to_midi(
        self,
        audio_path: Union[str, Path],
        output_path: Optional[Union[str, Path]] = None,
        structure_data: Optional[Dict] = None
    ) -> Path:
        """Convert audio to MIDI.
        
        Args:
            audio_path: Path to the audio file
            output_path: Path to save the MIDI file
            structure_data: Optional structure analysis data
            
        Returns:
            Path to the saved MIDI file
            
        Raises:
            MIDIConversionError: If conversion fails
        """
        try:
            # Load audio
            y, sr = librosa.load(str(audio_path), sr=self.sample_rate)
            
            # Determine output path if not provided
            if output_path is None:
                audio_path = Path(audio_path)
                output_path = settings.storage.midi_dir / f"{audio_path.stem}.mid"
            else:
                output_path = Path(output_path)
            
            # Create parent directory if it doesn't exist
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create MIDI object
            midi_data = pretty_midi.PrettyMIDI()
            
            # Extract MIDI data based on audio
            if structure_data:
                # Use structure-aware processing if available
                self._convert_with_structure(y, sr, midi_data, structure_data)
            else:
                # Basic conversion without structure awareness
                self._convert_basic(y, sr, midi_data)
            
            # Save MIDI file
            midi_data.write(str(output_path))
            logger.info(f"Saved MIDI file to {output_path}")
            
            return output_path
            
        except Exception as e:
            logger.error(f"Error in MIDI conversion: {str(e)}")
            raise MIDIConversionError(f"Failed to convert audio to MIDI: {str(e)}")
    
    def _convert_with_structure(
        self,
        y: np.ndarray,
        sr: int,
        midi_data: pretty_midi.PrettyMIDI,
        structure_data: Dict
    ) -> None:
        """Convert audio to MIDI with structural awareness.
        
        Args:
            y: Audio time series
            sr: Sample rate
            midi_data: MIDI data object to populate
            structure_data: Structure analysis data
        """
        # Get basic musical info
        tempo = structure_data.get("tempo", {}).get("bpm", 120.0)
        midi_data.initial_tempo = float(tempo)
        
        # Get sections
        sections = structure_data.get("sections", [])
        
        # Create instruments
        bass_program = pretty_midi.instrument_name_to_program('Electric Bass (finger)')
        bass = pretty_midi.Instrument(program=bass_program)
        
        drums = pretty_midi.Instrument(program=0, is_drum=True)
        
        # Process each section
        for section in sections:
            section_start = section["start"]
            section_end = section["end"]
            section_label = section["label"]
            
            # Extract audio for this section
            start_idx = int(section_start * sr)
            end_idx = int(section_end * sr)
            y_section = y[start_idx:end_idx]
            
            # Generate notes based on section type
            self._generate_section_notes(
                y_section, sr, bass, drums, 
                section_start, section_label, structure_data
            )
        
        # Add instruments to MIDI
        midi_data.instruments.append(bass)
        midi_data.instruments.append(drums)
    
    def _generate_section_notes(
        self,
        y_section: np.ndarray,
        sr: int,
        bass: pretty_midi.Instrument,
        drums: pretty_midi.Instrument,
        section_start: float,
        section_label: str,
        structure_data: Dict
    ) -> None:
        """Generate notes for a specific section based on its type.
        
        Args:
            y_section: Audio for this section
            sr: Sample rate
            bass: Bass instrument
            drums: Drum instrument
            section_start: Start time of section in seconds
            section_label: Type of section (intro, verse, etc.)
            structure_data: Overall structure data
        """
        # Extract timing information
        tempo = structure_data.get("tempo", {}).get("bpm", 120.0)
        beat_duration = 60.0 / tempo
        
        # Get key information (default to C if not available)
        key_data = structure_data.get("key", {"root": "C", "mode": "major"})
        root_note = key_data.get("root", "C")
        mode = key_data.get("mode", "major")
        
        # Map root note to MIDI pitch
        root_map = {
            "C": 60, "C#": 61, "D": 62, "D#": 63, "E": 64, "F": 65,
            "F#": 66, "G": 67, "G#": 68, "A": 69, "A#": 70, "B": 71
        }
        root_pitch = root_map.get(root_note, 60)
        
        # Scale patterns based on mode
        if mode == "major":
            scale_steps = [0, 2, 4, 5, 7, 9, 11]  # Major scale
        else:
            scale_steps = [0, 2, 3, 5, 7, 8, 10]  # Natural minor scale
        
        # Get reggae features
        reggae_features = structure_data.get("reggae_features", {})
        riddim_type = reggae_features.get("riddim_type", "one_drop")
        
        # Generate patterns based on section type and riddim type
        if section_label == "intro":
            self._generate_intro_pattern(
                bass, drums, section_start, beat_duration, 
                root_pitch, scale_steps, riddim_type
            )
        elif section_label == "verse":
            self._generate_verse_pattern(
                bass, drums, section_start, beat_duration,
                root_pitch, scale_steps, riddim_type
            )
        elif section_label == "chorus":
            self._generate_chorus_pattern(
                bass, drums, section_start, beat_duration,
                root_pitch, scale_steps, riddim_type
            )
        elif section_label == "bridge":
            self._generate_bridge_pattern(
                bass, drums, section_start, beat_duration,
                root_pitch, scale_steps, riddim_type
            )
        else:  # outro or other
            self._generate_outro_pattern(
                bass, drums, section_start, beat_duration,
                root_pitch, scale_steps, riddim_type
            )
    
    def _generate_intro_pattern(
        self,
        bass: pretty_midi.Instrument,
        drums: pretty_midi.Instrument,
        start_time: float,
        beat_duration: float,
        root_pitch: int,
        scale_steps: List[int],
        riddim_type: str
    ) -> None:
        """Generate an intro pattern.
        
        Args:
            bass: Bass instrument
            drums: Drum instrument
            start_time: Start time in seconds
            beat_duration: Duration of one beat
            root_pitch: Root pitch (MIDI note number)
            scale_steps: Scale steps for the key
            riddim_type: Type of riddim pattern
        """
        # Simple 4-bar intro pattern
        duration = beat_duration * 0.8  # Slightly shorter than full beat
        
        # Basic one-drop drum pattern (simplified)
        if riddim_type == "one_drop":
            # One drop typically emphasizes beat 3 (kick) in a 4-beat measure
            for bar in range(4):  # 4-bar intro
                bar_start = start_time + (bar * 4 * beat_duration)
                
                # Beat 3: Kick drum
                kick_note = pretty_midi.Note(
                    velocity=100,
                    pitch=36,  # Bass drum
                    start=bar_start + (2 * beat_duration),
                    end=bar_start + (2 * beat_duration) + 0.1
                )
                drums.notes.append(kick_note)
                
                # Hi-hat on every beat
                for beat in range(4):
                    hi_hat_note = pretty_midi.Note(
                        velocity=80,
                        pitch=42,  # Closed hi-hat
                        start=bar_start + (beat * beat_duration),
                        end=bar_start + (beat * beat_duration) + 0.05
                    )
                    drums.notes.append(hi_hat_note)
        
        # Simple bass line
        for bar in range(4):
            bar_start = start_time + (bar * 4 * beat_duration)
            
            # Root note on beat 1
            note = pretty_midi.Note(
                velocity=80,
                pitch=root_pitch - 12,  # An octave lower
                start=bar_start,
                end=bar_start + duration
            )
            bass.notes.append(note)
            
            # Fifth on beat 3
            fifth_pitch = root_pitch - 12 + scale_steps[4]  # Fifth in scale
            note = pretty_midi.Note(
                velocity=80,
                pitch=fifth_pitch,
                start=bar_start + (2 * beat_duration),
                end=bar_start + (2 * beat_duration) + duration
            )
            bass.notes.append(note)
    
    def _generate_verse_pattern(
        self,
        bass: pretty_midi.Instrument,
        drums: pretty_midi.Instrument,
        start_time: float,
        beat_duration: float,
        root_pitch: int,
        scale_steps: List[int],
        riddim_type: str
    ) -> None:
        """Generate a verse pattern.
        
        Args:
            bass: Bass instrument
            drums: Drum instrument
            start_time: Start time in seconds
            beat_duration: Duration of one beat
            root_pitch: Root pitch (MIDI note number)
            scale_steps: Scale steps for the key
            riddim_type: Type of riddim pattern
        """
        # More detailed 8-bar pattern
        duration = beat_duration * 0.8
        
        # Generate drum pattern based on riddim type
        for bar in range(8):  # 8-bar verse
            bar_start = start_time + (bar * 4 * beat_duration)
            
            if riddim_type == "one_drop":
                # One drop pattern
                for beat in range(4):
                    if beat == 2:  # Beat 3 (0-indexed)
                        # Kick on beat 3
                        kick_note = pretty_midi.Note(
                            velocity=100,
                            pitch=36,  # Bass drum
                            start=bar_start + (beat * beat_duration),
                            end=bar_start + (beat * beat_duration) + 0.1
                        )
                        drums.notes.append(kick_note)
                        
                        # Snare with kick
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
                    
                    # Offbeat hi-hats
                    if beat < 3:  # Don't add after beat 4
                        offbeat_hi_hat = pretty_midi.Note(
                            velocity=70,
                            pitch=42,  # Closed hi-hat
                            start=bar_start + (beat * beat_duration) + (beat_duration / 2),
                            end=bar_start + (beat * beat_duration) + (beat_duration / 2) + 0.05
                        )
                        drums.notes.append(offbeat_hi_hat)
                
            elif riddim_type == "steppers":
                # Steppers pattern (four on the floor)
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
            
            else:  # Default or "rockers" pattern
                # Rockers pattern (emphasis on 1 and 3)
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
            
            # Bass line for this bar - simple pattern based on root and fifth
            if bar % 2 == 0:  # Alternating pattern every other bar
                # Root on beat 1
                note = pretty_midi.Note(
                    velocity=80,
                    pitch=root_pitch - 12,
                    start=bar_start,
                    end=bar_start + duration
                )
                bass.notes.append(note)
                
                # Fifth on beat 2
                fifth_pitch = root_pitch - 12 + scale_steps[4]
                note = pretty_midi.Note(
                    velocity=75,
                    pitch=fifth_pitch,
                    start=bar_start + beat_duration,
                    end=bar_start + beat_duration + duration
                )
                bass.notes.append(note)
                
                # Root on beat 3
                note = pretty_midi.Note(
                    velocity=80,
                    pitch=root_pitch - 12,
                    start=bar_start + (2 * beat_duration),
                    end=bar_start + (2 * beat_duration) + duration
                )
                bass.notes.append(note)
                
                # Third on beat 4
                third_pitch = root_pitch - 12 + scale_steps[2]
                note = pretty_midi.Note(
                    velocity=75,
                    pitch=third_pitch,
                    start=bar_start + (3 * beat_duration),
                    end=bar_start + (3 * beat_duration) + duration
                )
                bass.notes.append(note)
            else:
                # Variation for odd bars
                # Fifth on beat 1
                fifth_pitch = root_pitch - 12 + scale_steps[4]
                note = pretty_midi.Note(
                    velocity=80,
                    pitch=fifth_pitch,
                    start=bar_start,
                    end=bar_start + duration
                )
                bass.notes.append(note)
                
                # Root on beat 2
                note = pretty_midi.Note(
                    velocity=75,
                    pitch=root_pitch - 12,
                    start=bar_start + beat_duration,
                    end=bar_start + beat_duration + duration
                )
                bass.notes.append(note)
                
                # Fourth on beat 3
                fourth_pitch = root_pitch - 12 + scale_steps[3]
                note = pretty_midi.Note(
                    velocity=80,
                    pitch=fourth_pitch,
                    start=bar_start + (2 * beat_duration),
                    end=bar_start + (2 * beat_duration) + duration
                )
                bass.notes.append(note)
                
                # Fifth on beat 4
                note = pretty_midi.Note(
                    velocity=75,
                    pitch=fifth_pitch,
                    start=bar_start + (3 * beat_duration),
                    end=bar_start + (3 * beat_duration) + duration
                )
                bass.notes.append(note)
    
    def _generate_chorus_pattern(
        self,
        bass: pretty_midi.Instrument,
        drums: pretty_midi.Instrument,
        start_time: float,
        beat_duration: float,
        root_pitch: int,
        scale_steps: List[int],
        riddim_type: str
    ) -> None:
        """Generate a chorus pattern (more energetic).
        
        Args:
            bass: Bass instrument
            drums: Drum instrument
            start_time: Start time in seconds
            beat_duration: Duration of one beat
            root_pitch: Root pitch (MIDI note number)
            scale_steps: Scale steps for the key
            riddim_type: Type of riddim pattern
        """
        # Similar to verse but with variations and more intensity
        self._generate_verse_pattern(
            bass, drums, start_time, beat_duration,
            root_pitch, scale_steps, riddim_type
        )
        
        # Add extra percussion for chorus energy
        for bar in range(8):
            bar_start = start_time + (bar * 4 * beat_duration)
            
            # Add open hi-hat accents on offbeats
            for beat in range(4):
                if beat % 2 == 0:  # Beats 1 and 3
                    open_hi_hat = pretty_midi.Note(
                        velocity=90,
                        pitch=46,  # Open hi-hat
                        start=bar_start + (beat * beat_duration) + (beat_duration / 2),
                        end=bar_start + (beat * beat_duration) + (beat_duration / 2) + 0.1
                    )
                    drums.notes.append(open_hi_hat)
    
    def _generate_bridge_pattern(
        self,
        bass: pretty_midi.Instrument,
        drums: pretty_midi.Instrument,
        start_time: float,
        beat_duration: float,
        root_pitch: int,
        scale_steps: List[int],
        riddim_type: str
    ) -> None:
        """Generate a bridge pattern (variation from verse/chorus).
        
        Args:
            bass: Bass instrument
            drums: Drum instrument
            start_time: Start time in seconds
            beat_duration: Duration of one beat
            root_pitch: Root pitch (MIDI note number)
            scale_steps: Scale steps for the key
            riddim_type: Type of riddim pattern
        """
        duration = beat_duration * 0.8
        
        # Create a different pattern for the bridge
        # Often a bridge uses a different chord progression or feel
        
        # For simplicity, we'll do a 4-bar pattern that changes the bass line
        # and reduces the drums
        
        for bar in range(4):
            bar_start = start_time + (bar * 4 * beat_duration)
            
            # Simplified drum pattern
            for beat in range(4):
                if beat == 2:  # Just kick on beat 3 for a one drop feel
                    kick_note = pretty_midi.Note(
                        velocity=90,
                        pitch=36,  # Bass drum
                        start=bar_start + (beat * beat_duration),
                        end=bar_start + (beat * beat_duration) + 0.1
                    )
                    drums.notes.append(kick_note)
                
                # Sparse hi-hat
                if beat % 2 == 0:  # Beats 1 and 3
                    hi_hat_note = pretty_midi.Note(
                        velocity=70,
                        pitch=42,  # Closed hi-hat
                        start=bar_start + (beat * beat_duration),
                        end=bar_start + (beat * beat_duration) + 0.05
                    )
                    drums.notes.append(hi_hat_note)
            
            # Walking bass line for bridge - using different scale positions
            scale_pos = [0, 2, 4, 5]  # Root, third, fifth, sixth
            for beat in range(4):
                note_pitch = root_pitch - 12 + scale_steps[scale_pos[beat]]
                note = pretty_midi.Note(
                    velocity=75,
                    pitch=note_pitch,
                    start=bar_start + (beat * beat_duration),
                    end=bar_start + (beat * beat_duration) + duration
                )
                bass.notes.append(note)
    
    def _generate_outro_pattern(
        self,
        bass: pretty_midi.Instrument,
        drums: pretty_midi.Instrument,
        start_time: float,
        beat_duration: float,
        root_pitch: int,
        scale_steps: List[int],
        riddim_type: str
    ) -> None:
        """Generate an outro pattern.
        
        Args:
            bass: Bass instrument
            drums: Drum instrument
            start_time: Start time in seconds
            beat_duration: Duration of one beat
            root_pitch: Root pitch (MIDI note number)
            scale_steps: Scale steps for the key
            riddim_type: Type of riddim pattern
        """
        # Simple 2-bar outro that resolves back to the root
        duration = beat_duration * 0.8
        
        # Simple drum pattern
        for bar in range(2):
            bar_start = start_time + (bar * 4 * beat_duration)
            
            for beat in range(4):
                # Last beat of the outro gets a final accent
                if bar == 1 and beat == 3:
                    # Final kick
                    kick_note = pretty_midi.Note(
                        velocity=110,  # Stronger for final accent
                        pitch=36,  # Bass drum
                        start=bar_start + (beat * beat_duration),
                        end=bar_start + (beat * beat_duration) + 0.1
                    )
                    drums.notes.append(kick_note)
                    
                    # Final snare
                    snare_note = pretty_midi.Note(
                        velocity=110,
                        pitch=38,  # Snare
                        start=bar_start + (beat * beat_duration),
                        end=bar_start + (beat * beat_duration) + 0.1
                    )
                    drums.notes.append(snare_note)
                elif beat == 2:  # One drop on beat 3 for other beats
                    kick_note = pretty_midi.Note(
                        velocity=95,
                        pitch=36,
                        start=bar_start + (beat * beat_duration),
                        end=bar_start + (beat * beat_duration) + 0.1
                    )
                    drums.notes.append(kick_note)
                
                # Hi-hat on every beat
                hi_hat_note = pretty_midi.Note(
                    velocity=80,
                    pitch=42,  # Closed hi-hat
                    start=bar_start + (beat * beat_duration),
                    end=bar_start + (beat * beat_duration) + 0.05
                )
                drums.notes.append(hi_hat_note)
        
        # Simple resolving bass line
        for bar in range(2):
            bar_start = start_time + (bar * 4 * beat_duration)
            
            if bar == 0:
                # First bar: fifth to fourth to root pattern
                fifth_pitch = root_pitch - 12 + scale_steps[4]
                note = pretty_midi.Note(
                    velocity=80,
                    pitch=fifth_pitch,
                    start=bar_start,
                    end=bar_start + (2 * beat_duration)
                )
                bass.notes.append(note)
                
                fourth_pitch = root_pitch - 12 + scale_steps[3]
                note = pretty_midi.Note(
                    velocity=80,
                    pitch=fourth_pitch,
                    start=bar_start + (2 * beat_duration),
                    end=bar_start + (4 * beat_duration)
                )
                bass.notes.append(note)
            else:
                # Second bar: sustained root note to end
                note = pretty_midi.Note(
                    velocity=85,
                    pitch=root_pitch - 12,
                    start=bar_start,
                    end=bar_start + (4 * beat_duration)
                )
                bass.notes.append(note)
    
    def _convert_basic(self, y: np.ndarray, sr: int, midi_data: pretty_midi.PrettyMIDI) -> None:
        """Basic conversion without structure awareness.
        
        Args:
            y: Audio time series
            sr: Sample rate
            midi_data: MIDI data object to populate
        """
        # Estimate tempo
        tempo, beats = librosa.beat.beat_track(y=y, sr=sr, hop_length=self.hop_length)
        midi_data.initial_tempo = float(tempo)
        
        # Create instruments
        bass_program = pretty_midi.instrument_name_to_program('Electric Bass (finger)')
        bass = pretty_midi.Instrument(program=bass_program)
        
        # Extract pitch content
        # For bass, focus on low frequencies
        y_harmonic = librosa.effects.harmonic(y)
        chroma = librosa.feature.chroma_cqt(
            y=y_harmonic, sr=sr, hop_length=self.hop_length
        )
        
        # Convert beat frames to times
        beat_times = librosa.frames_to_time(beats, sr=sr, hop_length=self.hop_length)
        
        # For each beat, find the most prominent pitch and create a note
        for i in range(len(beat_times) - 1):
            start_time = beat_times[i]
            end_time = beat_times[i + 1]
            duration = end_time - start_time
            
            # Find frame indices for this beat
            start_frame = beats[i]
            end_frame = beats[i + 1] if i < len(beats) - 1 else chroma.shape[1]
            
            if start_frame < chroma.shape[1] and end_frame <= chroma.shape[1]:
                # Get the most prominent pitch in this beat segment
                beat_chroma = np.mean(chroma[:, start_frame:end_frame], axis=1)
                pitch_class = np.argmax(beat_chroma)
                
                # Map to bass range (around MIDI note 36-48)
                midi_note = pitch_class + 36
                
                # Create note (only if there's significant energy)
                if np.max(beat_chroma) > 0.1:
                    note = pretty_midi.Note(
                        velocity=80,
                        pitch=midi_note,
                        start=start_time,
                        end=min(start_time + duration * 0.8, end_time)
                    )
                    bass.notes.append(note)
        
        # Add instrument to MIDI
        midi_data.instruments.append(bass)
