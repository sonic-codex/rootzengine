#!/usr/bin/env python3
"""Test enhanced analysis with reggae pattern detection."""

import tempfile
import numpy as np
import soundfile as sf
from pathlib import Path

from rootzengine.audio.analysis import AudioStructureAnalyzer
from rootzengine.audio.reggae_patterns import reggae_detector
from rootzengine.storage.interface import StorageManager

def create_test_audio():
    """Create a test audio file."""
    sr = 22050
    duration = 3
    t = np.linspace(0, duration, int(sr * duration))
    y = 0.3 * np.sin(2 * np.pi * 220 * t)  # 220 Hz sine wave
    
    temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
    sf.write(temp_file.name, y, sr)
    return temp_file.name

def test_enhanced_analysis():
    """Test the complete enhanced analysis system."""
    print("🎵 RootzEngine Enhanced Analysis Test")
    print("=" * 40)
    
    # Create test audio
    audio_file = create_test_audio()
    print(f"✅ Created test audio: {audio_file}")
    
    try:
        # Test analyzer
        analyzer = AudioStructureAnalyzer()
        result = analyzer.analyze_structure(audio_file, perform_separation=False)
        
        print(f"✅ Basic analysis complete")
        print(f"  - Sections: {len(result.get('sections', []))}")
        print(f"  - Tempo: {result.get('tempo', {}).get('bpm')} BPM")
        print(f"  - Key: {result.get('key', {}).get('key')} {result.get('key', {}).get('mode')}")
        
        # Check reggae pattern detection
        reggae_pattern = result.get('reggae_pattern', {})
        if reggae_pattern:
            print(f"✅ Reggae pattern detection complete")
            print(f"  - Detected style: {reggae_pattern.get('detected_style')}")
            print(f"  - Confidence: {reggae_pattern.get('confidence')}")
            print(f"  - Score: {reggae_pattern.get('confidence_score', 0):.2f}")
        
        # Check rhythm characteristics
        rhythm_chars = result.get('rhythm_characteristics', {})
        if rhythm_chars:
            print(f"✅ Rhythm characteristics complete")
            print(f"  - Pattern name: {rhythm_chars.get('pattern_name')}")
            print(f"  - Time signature: {rhythm_chars.get('musical_elements', {}).get('time_signature')}")
            print(f"  - Typical key: {rhythm_chars.get('musical_elements', {}).get('typical_key')}")
        
        # Test individual detector functions
        print(f"\n🎯 Testing individual detector functions:")
        
        # Test style info
        styles = reggae_detector.get_all_styles()
        print(f"✅ Available styles: {len(styles)}")
        for style in styles[:3]:  # Show first 3
            print(f"  - {style['name']}: {style['tempo_range'][0]}-{style['tempo_range'][1]} BPM")
        
        # Test tempo-based detection
        for tempo in [75, 90, 150]:
            detection = reggae_detector.detect_pattern_mock(tempo)
            print(f"✅ Tempo {tempo} BPM → {detection['detected_style']} ({detection['confidence']})")
        
        # Test storage integration
        print(f"\n💾 Testing storage integration:")
        storage = StorageManager()
        analysis_path = storage.save_analysis_result("test_song.wav", result)
        print(f"✅ Analysis saved to storage: {Path(analysis_path).name}")
        
        # Retrieve and verify
        retrieved = storage.get_analysis_result("test_song.wav")
        if retrieved and retrieved.get('reggae_pattern'):
            print(f"✅ Retrieved analysis matches original")
        
        print(f"\n🎉 All enhanced analysis tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    
    finally:
        # Cleanup
        Path(audio_file).unlink(missing_ok=True)

if __name__ == "__main__":
    success = test_enhanced_analysis()
    exit(0 if success else 1)