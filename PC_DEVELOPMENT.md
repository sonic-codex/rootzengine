# RootzEngine PC Development Guide

## 🎯 Overview

This guide covers transitioning RootzEngine from Pi-based mock development to full PC audio processing with real librosa audio analysis and pretty_midi generation.

## 🏁 Current Pi Implementation Status

### ✅ **Fully Implemented & Tested**

**Core Architecture:**
- ✅ Mock audio processing interfaces with pluggable backends
- ✅ Unified storage system (local/Azure) with automatic selection
- ✅ Complete FastAPI system with 20+ endpoints across 4 modules
- ✅ Batch processing pipeline with parallel job execution
- ✅ File watcher system with automatic processing triggers
- ✅ Configuration management with environment/YAML support

**Reggae-Specific Features:**
- ✅ Complete reggae pattern detection system (5 styles: One Drop, Steppers, Rockers, Ska, Rocksteady)
- ✅ Tempo-based style classification with confidence scoring
- ✅ Rhythm characteristic analysis with musical theory integration
- ✅ Mock audio structure analysis integrated with reggae detection

**API Endpoints Working:**
```
/api/v1/analysis/*     - Audio analysis, file management, storage operations
/api/v1/batch/*        - Batch processing, job tracking, directory scanning  
/api/v1/reggae/*       - Pattern detection, style info, tempo classification
/api/v1/midi/*         - Mock MIDI operations (ready for PC implementation)
```

**Testing & Quality:**
- ✅ 29 comprehensive tests passing (mock interfaces, config, storage, integration)
- ✅ Package installation working (`pip install -e .`)
- ✅ All imports and dependencies resolved for Pi environment
- ✅ Enhanced analysis with reggae patterns fully functional

## 🚀 PC Enhancement Roadmap

### Phase 1: Real Audio Processing (Priority: HIGH)

#### 1.1 Replace Mock Audio Processor
**File:** `src/rootzengine/audio/interfaces.py`

Create `LibrosaAudioProcessor` class:
```python
class LibrosaAudioProcessor(AudioProcessorInterface):
    def analyze_structure(self, audio_path: str, **kwargs) -> Dict[str, Any]:
        # Real librosa implementation
        y, sr = librosa.load(audio_path)
        tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
        # ... rest of real implementation
```

**Current Mock Returns:**
```python
{
    "sections": [{"start": 0.0, "end": 30.0, "label": "intro"}, ...],
    "tempo": {"bpm": 85.0, "confidence": 0.9},
    "key": {"key": "A", "mode": "minor", "confidence": 0.85},
    "duration": 180.0,
    "sample_rate": 22050,
    "channels": 2
}
```

#### 1.2 Implement Real Audio Features
**File:** `src/rootzengine/audio/features.py` (ALREADY EXISTS - needs enhancement)

**Current State:** Basic librosa functions already written
**Enhancement Needed:**
- Fix missing imports (`from typing import Tuple`)
- Add real tempo detection replacing mock 85.0 BPM
- Implement actual key detection using chroma features
- Add beat tracking and onset detection

#### 1.3 Enhanced Reggae Pattern Detection
**File:** `src/rootzengine/audio/reggae_patterns.py`

**Current:** Mock detection based only on tempo
**Enhancement:** Add real onset pattern analysis
```python
def detect_pattern_real(self, y: np.ndarray, sr: int, tempo: float) -> Dict[str, any]:
    # Analyze actual kick/snare patterns from audio
    # Use onset detection in frequency ranges
    # Compare against known reggae rhythm templates
```

### Phase 2: MIDI Generation Integration (Priority: MEDIUM)

#### 2.1 Existing MIDI Code Status
**Files:** `src/rootzengine/midi/converter.py`, `src/rootzengine/midi/patterns.py`

**✅ Already Implemented:**
- Complete `MIDIPatternGenerator` with reggae-specific patterns
- `AudioToMIDIConverter` that maps analysis sections to MIDI
- Drum patterns for One Drop, Steppers, Rockers
- Bass line generation with walking bass
- Pretty_midi integration complete

**🔧 Fixes Needed:**
```python
# Fix imports in converter.py line 7:
from src.rootzengine.midi.patterns import MIDIPatternGenerator
# Change to:
from rootzengine.midi.patterns import MIDIPatternGenerator
```

#### 2.2 Integration with New Pattern Detection
**Current Flow:** Mock analysis → MIDI generation
**Enhanced Flow:** Real analysis → Enhanced pattern detection → Smarter MIDI generation

Enhance `AudioToMIDIConverter.__init__()`:
```python
def __init__(self, analysis_data: Dict):
    self.analysis = analysis_data
    # Use real detected tempo and key
    self.tempo = analysis_data.get("tempo", {}).get("bpm", 120.0)
    self.key = analysis_data.get("key", {}).get("key", "C")
    # Use detected reggae style for pattern selection
    self.reggae_style = analysis_data.get("reggae_pattern", {}).get("detected_style", "rockers")
```

#### 2.3 Enhanced API Integration
**File:** `src/rootzengine/api/routes/midi.py`

**Current:** Returns mock JSON responses
**Enhancement:** Generate and return actual MIDI files

Replace mock responses with:
```python
# Real MIDI generation
converter = AudioToMIDIConverter(structure_data)
midi_data = converter.generate()
# Save and return file
midi_path = output_dir / f"{filename}.mid" 
converter.save(midi_data, str(midi_path))
return FileResponse(midi_path, media_type="audio/midi")
```

### Phase 3: Stem Separation (Priority: LOW)

#### 3.1 Real Demucs Integration
**File:** `src/rootzengine/audio/separation.py`

**Current:** Mock separation creating empty files
**Enhancement:** Real Demucs processing

```python
import demucs.separate
class DemucsRealSeparator(StemSeparatorInterface):
    def separate(self, audio_path: str, output_dir: str, model: str = "htdemucs") -> Dict[str, str]:
        # Real Demucs separation
        # GPU acceleration support
        # Progress tracking
```

### Phase 4: Performance & Production

#### 4.1 Heavy Processing Optimization
- GPU acceleration for Demucs
- Batch processing optimization
- Memory management for large files
- Progress tracking for long operations

#### 4.2 Enhanced Testing
- Real audio file test cases
- Performance benchmarks
- Memory usage monitoring
- API load testing

## 🔧 PC Setup Instructions

### 1. Dependencies Installation
```bash
# Create fresh environment
python3 -m venv venv_pc
source venv_pc/bin/activate

# Install full requirements
pip install -r requirements-azure.txt

# Key packages for PC:
pip install librosa>=0.10.0 pretty_midi>=0.2.10 demucs>=4.0.0
```

### 2. Environment Configuration
```bash
# Copy and configure for PC
cp .env.example .env

# Edit .env:
ROOTZ_USE_AZURE=false  # or true for cloud processing
ENVIRONMENT=pc_development
```

### 3. Test Real Processing
```bash
# Test with real audio file
python -c "
import librosa
from rootzengine.audio.analysis import AudioStructureAnalyzer
analyzer = AudioStructureAnalyzer()
# When implemented: result = analyzer.analyze_structure('test.wav')
"
```

## 🎵 Implementation Strategy

### Quick Wins (1-2 hours)
1. **Fix MIDI imports** - Change `src.rootzengine` to `rootzengine` in MIDI files
2. **Test existing MIDI generation** - Verify patterns work with real audio structure
3. **Add librosa to mock processor** - Replace tempo=85.0 with real detection

### Medium Tasks (Half day)
1. **Implement LibrosaAudioProcessor** - Real audio analysis
2. **Enhance reggae pattern detection** - Use real onset analysis  
3. **Update API to return real MIDI files** - File downloads instead of JSON

### Complex Tasks (1-2 days)
1. **Real stem separation** - Demucs integration with GPU support
2. **Performance optimization** - Memory management, progress tracking
3. **Comprehensive testing** - Real audio files, performance benchmarks

## 🧪 Testing Strategy

### Test Audio Files Needed
```
test_files/
├── reggae_one_drop_85bpm.wav    # Classic one drop example
├── ska_upstroke_150bpm.wav      # Fast ska pattern
├── steppers_4on4_90bpm.wav      # Four-on-the-floor
├── complex_song_structure.wav   # Multiple sections
└── stem_separation_test.wav     # Good for separation testing
```

### Validation Tests
1. **Tempo Detection Accuracy** - Compare librosa vs known BPM
2. **Pattern Classification** - Verify reggae style detection
3. **MIDI Quality** - Generated patterns match audio characteristics
4. **API Performance** - Response times with real processing

## 🎯 Success Metrics

### Phase 1 Complete When:
- [ ] Real audio analysis working (tempo, key, structure)
- [ ] Reggae pattern detection using actual audio features
- [ ] API returns real analysis data instead of mocks
- [ ] All existing tests still pass

### Phase 2 Complete When:
- [ ] MIDI files generated from real audio analysis
- [ ] API serves downloadable MIDI files
- [ ] Pattern quality matches detected reggae style
- [ ] Integration with enhanced pattern detection

### Full PC Implementation Complete When:
- [ ] Stem separation working with real audio
- [ ] Performance optimized for large files
- [ ] Comprehensive test suite with real audio
- [ ] Ready for production deployment

## 🚨 Migration Notes from Pi

### What Changes
- Audio processing: Mock → Real librosa analysis
- MIDI generation: JSON responses → Real file downloads  
- Performance: Lightweight → Heavy processing optimized
- Dependencies: Pi-friendly → Full audio processing stack

### What Stays the Same
- API structure and endpoints
- Storage system and database schemas
- Configuration management
- Batch processing architecture
- Core business logic and reggae knowledge

The Pi development provides the perfect foundation - now we add the real audio power! 🎸🦁