"""Convert audio structure analysis to a MIDI file."""

import logging
from typing import Dict

import pretty_midi
from rootzengine.midi.patterns import MIDIPatternGenerator

logger = logging.getLogger(__name__)


class AudioToMIDIConverter:
    """Converts a structured audio analysis into a coherent MIDI file."""

    def __init__(self, analysis_data: Dict):
        """Initialize the converter with audio analysis results.

        Args:
            analysis_data: The dictionary output from AudioStructureAnalyzer.
        """
        self.analysis = analysis_data
        self.tempo = analysis_data.get("tempo", {}).get("bpm", 120.0)
        self.key = analysis_data.get("key", {}).get("root", "C")
        self.mode = analysis_data.get("key", {}).get("mode", "major")
        self.generator = MIDIPatternGenerator(tempo=self.tempo)

    def _map_section_to_params(self, section_label: str) -> Dict:
        """Maps a section label to MIDI generation parameters.

        This is where the "intelligence" of the conversion happens, deciding
        how each section should sound.

        Args:
            section_label: The label of the song section (e.g., 'intro', 'chorus').

        Returns:
            A dictionary of parameters for the MIDIPatternGenerator.
        """
        # Default parameters
        params = {
            "pattern_type": "rockers",
            "bass_style": "simple",
            "skank_style": "traditional",
        }

        label_lower = section_label.lower()

        if "chorus" in label_lower:
            params["pattern_type"] = "steppers"
            params["bass_style"] = "complex"
        elif "verse" in label_lower:
            params["pattern_type"] = "one_drop"
            params["bass_style"] = "simple"
        elif "intro" in label_lower or "outro" in label_lower:
            params["pattern_type"] = "heartbeat"
            params["bass_style"] = "minimal"
        
        return params

    def generate(self) -> pretty_midi.PrettyMIDI:
        """Generates a full MIDI file from the analysis data.

        Returns:
            A PrettyMIDI object representing the entire song.
        """
        final_midi = pretty_midi.PrettyMIDI(initial_tempo=self.tempo)
        
        # Ensure instruments are created once and shared
        final_midi.instruments.append(pretty_midi.Instrument(program=0, is_drum=True, name="Drums"))
        final_midi.instruments.append(pretty_midi.Instrument(program=33, name="Electric Bass"))

        for section in self.analysis.get("sections", []):
            start_time = section["start"]
            end_time = section["end"]
            duration = end_time - start_time
            measures = int(round(duration / (60.0 / self.tempo * 4)))

            if measures == 0:
                continue

            params = self._map_section_to_params(section["label"])
            section_midi = self.generator.generate_pattern(measures=measures, key=self.key, mode=self.mode, **params)

            # Append notes from the generated section, offsetting by start time
            for instrument in section_midi.instruments:
                target_instrument = final_midi.instruments[0] if instrument.is_drum else final_midi.instruments[1]
                for note in instrument.notes:
                    note.start += start_time
                    note.end += start_time
                    target_instrument.notes.append(note)
        
        return final_midi

    def save(self, midi_data: pretty_midi.PrettyMIDI, output_path: str):
        """Saves the PrettyMIDI object to a file.

        Args:
            midi_data: The MIDI object to save.
            output_path: The path to save the .mid file.
        """
        midi_data.write(output_path)
        logger.info(f"MIDI file saved to {output_path}")