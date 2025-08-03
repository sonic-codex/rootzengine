"""Smoke test script for end-to-end pipeline testing."""

import os
import sys
import numpy as np
import tempfile
from pathlib import Path

# Add project root to path
root_dir = Path(__file__).parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

# Try to import required packages
try:
    import soundfile as sf
    import pretty_midi
except ImportError:
    print("Missing dependencies. Install with: pip install soundfile pretty_midi")
    sys.exit(1)

# Import project modules
try:
    from src.rootzengine.audio.analysis import AudioStructureAnalyzer
    from src.rootzengine.midi.converter import AudioToMIDIConverter
except ImportError:
    print("Could not import rootzengine modules. Check your installation.")
    sys.exit(1)

def run_smoke_test():
    """Run an end-to-end smoke test on the pipeline."""
    # Create a temp directory for test files
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Generate a 2-second sine wave at 440 Hz
        sr = 22050
        t = np.linspace(0, 2, int(sr * 2), False)
        y = 0.5 * np.sin(2 * np.pi * 440 * t)
        
        # Write to temporary WAV file
        audio_path = os.path.join(tmp_dir, "test.wav")
        sf.write(audio_path, y, sr)
        
        # Analyze structure
        print("Running audio structure analysis...")
        analyzer = AudioStructureAnalyzer()
        structure = analyzer.analyze_structure(audio_path, perform_separation=False)
        
        if "sections" not in structure or "tempo" not in structure:
            print("ERROR: Missing expected fields in structure analysis")
            return False
        
        print(f"Analysis complete. Found {len(structure.get('sections', []))} sections.")
        print(f"Detected tempo: {structure.get('tempo', {}).get('bpm', 'unknown')} BPM")
        
        # Convert to MIDI
        print("Converting to MIDI...")
        midi_path = os.path.join(tmp_dir, "test.mid")
        converter = AudioToMIDIConverter()
        
        try:
            out_path = converter.convert_to_midi(audio_path, midi_path, structure_data=structure)
            
            if not os.path.exists(out_path):
                print("ERROR: MIDI file was not created")
                return False
                
            # Load and inspect MIDI
            pm = pretty_midi.PrettyMIDI(str(out_path))
            if len(pm.instruments) == 0:
                print("ERROR: No instruments found in generated MIDI")
                return False
                
            print(f"MIDI conversion successful. Generated {len(pm.instruments)} instruments.")
            print(f"Total MIDI duration: {pm.get_end_time():.2f} seconds")
            
            return True
            
        except Exception as e:
            print(f"ERROR in MIDI conversion: {str(e)}")
            return False

if __name__ == "__main__":
    print("Starting RootzEngine smoke test...")
    success = run_smoke_test()
    
    if success:
        print("✅ Smoke test PASSED!")
        sys.exit(0)
    else:
        print("❌ Smoke test FAILED!")
        sys.exit(1)
