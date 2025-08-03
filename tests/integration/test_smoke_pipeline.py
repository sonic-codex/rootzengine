import numpy as np
import pytest

from rootzengine.audio.analysis import AudioStructureAnalyzer
from rootzengine.midi.converter import AudioToMIDIConverter


def test_smoke_pipeline(tmp_path):
    """End-to-end smoke test: analyze a synthetic audio and convert to MIDI."""
    # Skip test if key dependencies are missing
    pytest.importorskip("soundfile")
    pytest.importorskip("pretty_midi")
    import soundfile as sf
    import pretty_midi
    # Generate a 2-second sine wave at 440 Hz
    sr = 22050
    t = np.linspace(0, 2, int(sr * 2), False)
    y = 0.5 * np.sin(2 * np.pi * 440 * t)

    # Write to temporary WAV file
    audio_path = tmp_path / "test.wav"
    sf.write(str(audio_path), y, sr)

    # Analyze structure
    analyzer = AudioStructureAnalyzer()
    # Analyze structure from synthetic audio
    structure = analyzer.analyze_structure(
        str(audio_path), perform_separation=False
    )
    assert "sections" in structure
    assert "tempo" in structure

    # Convert to MIDI
    midi_path = tmp_path / "test.mid"
    converter = AudioToMIDIConverter()
    # Convert to MIDI using analyzed structure
    out_path = converter.convert_to_midi(
        audio_path,
        midi_path,
        structure_data=structure
    )
    assert out_path.exists(), "MIDI output file was not created"

    # Load and inspect MIDI
    pm = pretty_midi.PrettyMIDI(str(out_path))
    assert len(pm.instruments) >= 1, "No instruments found in generated MIDI"
