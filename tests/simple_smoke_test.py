"""Simple standalone smoke test that works outside the pytest framework."""

import numpy as np
import sys
import os
from pathlib import Path

# Add proper paths for imports
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root))

try:
    import soundfile as sf
    import pretty_midi
except ImportError:
    print("ERROR: Required packages missing. Install with:")
    print("pip install soundfile pretty_midi")
    sys.exit(1)

# Try direct imports from src
try:
    from src.rootzengine.audio.analysis import AudioStructureAnalyzer
    from src.rootzengine.midi.converter import AudioToMIDIConverter
    print("✓ Successfully imported rootzengine modules")
except ImportError as e:
    print(f"ERROR: Could not import rootzengine modules: {e}")
    sys.exit(1)

# Create test directory
test_dir = os.path.join(current_dir, "smoke_test_output")
os.makedirs(test_dir, exist_ok=True)
print(f"✓ Created test directory: {test_dir}")

# Generate simple audio (a sine wave)
print("Generating test audio...")
sr = 22050
duration = 2  # seconds
t = np.linspace(0, duration, int(sr * duration), False)
y = 0.5 * np.sin(2 * np.pi * 440 * t)  # 440 Hz sine wave

# Save audio to file
audio_path = os.path.join(test_dir, "test_audio.wav")
sf.write(audio_path, y, sr)
print(f"✓ Saved test audio to: {audio_path}")

# Run the audio analysis
print("Running audio structure analysis...")
analyzer = AudioStructureAnalyzer()
structure = analyzer.analyze_structure(audio_path, perform_separation=False)

# Check results
if not structure or "sections" not in structure:
    print("ERROR: Audio analysis did not return valid structure data")
    sys.exit(1)

print(f"✓ Analysis complete with {len(structure['sections'])} sections")
print(f"✓ Detected tempo: {structure['tempo']['bpm']:.1f} BPM")

# Generate MIDI
print("Converting to MIDI...")
midi_path = os.path.join(test_dir, "test_output.mid")
converter = AudioToMIDIConverter()
output_path = converter.convert_to_midi(audio_path, midi_path, structure_data=structure)

# Verify MIDI
if not os.path.exists(output_path):
    print(f"ERROR: Expected MIDI file not created at {output_path}")
    sys.exit(1)

print(f"✓ MIDI file created at: {output_path}")

# Verify MIDI content
midi = pretty_midi.PrettyMIDI(str(output_path))
print(f"✓ MIDI file contains {len(midi.instruments)} instruments")
print(f"✓ MIDI duration: {midi.get_end_time():.2f} seconds")

print("\n✅ SMOKE TEST PASSED - Pipeline is working correctly!")
