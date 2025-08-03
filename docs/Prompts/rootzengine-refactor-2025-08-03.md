# RootzEngine Phase 2.5: Emergency Cleanup & Simple Testing

## Current Situation
The project has good core functionality but the file organization has become scattered, making testing impossible. The agent needs to focus on cleanup and getting ONE simple test working.

## 🎯 **PRIORITY 1: File Organization Fix**

### Critical Cleanup Tasks
1. **Move scattered files to proper locations:**
   ```bash
   # These files are currently in root and need to be moved:
   mv analysis.py src/rootzengine/audio/
   mv azure.py src/rootzengine/storage/
   mv converter.py src/rootzengine/midi/
   mv patterns.py src/rootzengine/midi/
   mv local.py src/rootzengine/storage/
   mv demucs_wrapper.py src/rootzengine/audio/separation.py  # rename appropriately
   ```

2. **Remove duplicate/empty files:**
   ```bash
   # Remove empty files in root:
   rm 50803.py analysis.py config_loader.py demucs_wrapper.py midi-analysis.py
   rm pipeline.py router.py schemas.py model-config.yaml
   ```

3. **Fix import statements throughout codebase:**
   - Change all `from src.rootzengine` to `from rootzengine`
   - Ensure proper relative imports

## 🎯 **PRIORITY 2: Minimal Working Test**

### Create ONE Simple Test That Works
Create `simple_test.py` in root directory:

```python
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
```

## 🎯 **PRIORITY 3: Fix Core Dependencies**

### Essential Missing Implementations
Create these MINIMAL working versions:

**1. `src/rootzengine/core/config.py`:**
```python
"""Simple configuration with fallbacks."""

class AudioConfig:
    sample_rate: int = 22050
    hop_length: int = 512
    n_fft: int = 2048

class Settings:
    def __init__(self):
        self.audio = AudioConfig()

# Global settings instance
settings = Settings()
```

**2. `src/rootzengine/core/exceptions.py`:**
```python
"""Custom exceptions."""

class AudioProcessingError(Exception):
    """Raised when audio processing fails."""
    pass

class StemSeparationError(Exception):
    """Raised when stem separation fails."""
    pass
```

**3. Fix `src/rootzengine/audio/features.py`:**
```python
"""Basic audio feature extraction."""

import librosa
import numpy as np

def extract_features(y, sr, hop_length=512, n_fft=2048):
    """Extract basic audio features."""
    return {
        "mfcc": librosa.feature.mfcc(y=y, sr=sr, hop_length=hop_length),
        "chroma": librosa.feature.chroma_stft(y=y, sr=sr, hop_length=hop_length),
        "spectral_centroid": librosa.feature.spectral_centroid(y=y, sr=sr, hop_length=hop_length)
    }
```

## 🎯 **PRIORITY 4: Package Installation**

### Test Installation Process
```bash
# 1. Install in development mode
pip install -e .

# 2. Test basic import
python -c "from rootzengine.audio.analysis import AudioStructureAnalyzer; print('Success')"

# 3. Run simple test
python simple_test.py
```

## 🛑 **STOP CONDITIONS**

**Do NOT proceed with advanced features until:**
- [ ] ✅ Package installs without errors: `pip install -e .`
- [ ] ✅ Basic import works: `from rootzengine.audio.analysis import AudioStructureAnalyzer`
- [ ] ✅ Simple test passes: `python simple_test.py`

## 🚫 **What NOT to Do**

1. **Don't add new features** - focus only on making what exists work
2. **Don't work on Docker** - local testing first
3. **Don't create complex tests** - one simple test is enough
4. **Don't worry about Azure/cloud** - local only for now
5. **Don't refactor architecture** - just organize existing files

## ✅ **Success Criteria**

1. **File organization is clean** - no scattered files in root
2. **Package installs** - `pip install -e .` works
3. **One test passes** - synthetic audio analysis works
4. **Import paths work** - no import errors

## 💬 **Communication Strategy**

If testing in Codespace is too complex:
- Get the basic test working locally first
- Use `python simple_test.py` to verify core functionality
- Once stable, then worry about Codespace deployment

## 🎵 **Remember the Goal**

We're building an AI bandmate that understands reggae music structure. The current implementation has the right architecture - it just needs to be organized and tested. One working test is worth more than 100 features that don't run.

Focus on making the audio structure analysis work with synthetic audio first. Once that's solid, we can add real reggae tracks and move toward the AI bandmate functionality.