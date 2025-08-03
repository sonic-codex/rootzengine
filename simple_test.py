#!/usr/bin/env python3
"""Ultra-simple test to verify basic functionality."""

import sys
import numpy as np
import soundfile as sf
from pathlib import Path

def test_basic_imports():
    """Test that we can import core modules."""
    try:
        from rootzengine.audio.analysis import AudioStructureAnalyzer
        print("✅ AudioStructureAnalyzer import successful")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_synthetic_audio_analysis():
    """Test analysis with synthetic audio."""
    try:
        from rootzengine.audio.analysis import AudioStructureAnalyzer
        # Create 5 seconds of test audio (sine wave)
        sr = 22050
        duration = 5
        t = np.linspace(0, duration, int(sr * duration))
        y = 0.3 * np.sin(2 * np.pi * 220 * t)  # 220 Hz
        # Save to temporary file
        test_file = "temp_test.wav"
        sf.write(test_file, y, sr)
        # Run analysis
        analyzer = AudioStructureAnalyzer()
        result = analyzer.analyze_structure(test_file, perform_separation=False)
        # Cleanup
        Path(test_file).unlink(missing_ok=True)
        # Check results
        if result and 'sections' in result:
            print(f"✅ Analysis successful: {len(result['sections'])} sections detected")
            print(f"✅ Tempo: {result['tempo']['bpm']:.1f} BPM")
            return True
        else:
            print("❌ Analysis returned invalid results")
            return False
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        return False

def main():
    """Run basic tests."""
    print("🎵 RootzEngine Basic Test")
    print("=" * 30)
    # Test 1: Imports
    if not test_basic_imports():
        print("Import test failed - fix package structure first")
        return False
    # Test 2: Basic analysis
    if not test_synthetic_audio_analysis():
        print("Analysis test failed - check audio processing")
        return False
    print("\n🎉 All basic tests passed!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
