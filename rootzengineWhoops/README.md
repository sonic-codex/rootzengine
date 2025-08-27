# RootzEngine 🎛️🦁  
*AI-Powered Reggae Analysis & MIDI Generation Toolkit*

> Transform reggae tracks into structured data and generate authentic MIDI patterns with AI-driven analysis.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Development Status](https://img.shields.io/badge/status-active--development-green.svg)]()

---

## 🌟 What is RootzEngine?

RootzEngine is a comprehensive toolkit for analyzing reggae music and generating authentic MIDI patterns. Whether you're a:
- **Producer** building reggae sets and arrangements
- **Researcher** studying reggae musical patterns
- **Developer** building music AI applications
- **Musician** exploring reggae theory and composition

RootzEngine provides the tools to understand and recreate authentic reggae grooves.

## ✨ Key Features

### 🎧 **Advanced Audio Analysis**
- **Tempo & Beat Detection**: Precise BPM detection with reggae-specific rhythm analysis
- **Key & Chord Recognition**: Musical key detection and harmonic analysis
- **Structure Segmentation**: Automatic detection of intro, verse, chorus, bridge sections
- **Reggae Pattern Recognition**: Identifies One Drop, Steppers, Rockers, and other riddim styles

### 🎵 **Intelligent MIDI Generation**
- **Pattern-Aware Generation**: Creates MIDI that matches detected reggae styles
- **Multi-Instrument Arrangements**: Generates bass, drums, organ, and guitar parts
- **Style-Specific Templates**: Authentic patterns for different reggae subgenres
- **Structural Awareness**: MIDI adapts to song sections (verse vs chorus patterns)

### 🔧 **Professional Tools**
- **Stem Separation**: Isolate drums, bass, and other instruments using Demucs
- **API-First Design**: RESTful endpoints for integration with other tools
- **Batch Processing**: Handle multiple files efficiently
- **Cloud Integration**: Azure support for large-scale processing

### 🎛️ **AI Bandmate Capabilities**
- **Real-Time Analysis**: Process audio streams for live performance
- **Contextual Response**: Generate accompaniment that matches the current musical section
- **Pattern Learning**: Improve recommendations based on musical analysis
- **Interactive MIDI**: Generate responsive musical parts for jamming

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/sonic-codex/rootzengine.git
cd rootzengine

# Install dependencies
pip install -e .

# Quick test
python simple_test.py
```

### Basic Usage

```python
from rootzengine.audio.analysis import AudioStructureAnalyzer
from rootzengine.midi.converter import AudioToMidiConverter

# Analyze a reggae track
analyzer = AudioStructureAnalyzer()
analysis = analyzer.analyze_structure("path/to/reggae_song.wav")

print(f"Detected tempo: {analysis['tempo']['bpm']} BPM")
print(f"Reggae style: {analysis['reggae_features']['riddim_type']}")
print(f"Key: {analysis['key']['root']} {analysis['key']['mode']}")

# Generate MIDI from analysis
converter = AudioToMidiConverter()
midi_file = converter.convert_to_midi(
    audio_path="path/to/reggae_song.wav",
    output_path="generated_reggae.mid",
    structure_data=analysis
)

print(f"MIDI saved to: {midi_file}")
```

### API Server

```bash
# Start the development server
uvicorn rootzengine.api.main:app --reload --port 8000

# Test the API
curl -X POST -F "file=@reggae_track.wav" http://localhost:8000/api/v1/analysis/analyze
```

---

## 📁 Project Structure

```
rootzengine/
├── src/rootzengine/           # Core package
│   ├── audio/                 # Audio analysis & processing
│   │   ├── analysis.py        # Main audio structure analyzer
│   │   ├── features.py        # Audio feature extraction
│   │   ├── reggae_patterns.py # Reggae-specific pattern detection
│   │   └── separation.py      # Stem separation (Demucs)
│   ├── midi/                  # MIDI generation & processing
│   │   ├── converter.py       # Audio-to-MIDI conversion
│   │   └── patterns.py        # Reggae MIDI pattern library
│   ├── api/                   # REST API endpoints
│   │   ├── main.py           # FastAPI application
│   │   └── routes/           # API route definitions
│   ├── core/                  # Configuration & utilities
│   └── storage/              # File handling & cloud integration
├── tests/                     # Test suites
├── docker/                    # Containerization
├── docs/                      # Documentation
└── scripts/                   # Utility scripts
```

---

## 🎼 Example Outputs

### Analysis Results
```json
{
  "sections": [
    {"start": 0.0, "end": 16.0, "label": "intro", "confidence": 0.92},
    {"start": 16.0, "end": 48.0, "label": "verse", "confidence": 0.89},
    {"start": 48.0, "end": 80.0, "label": "chorus", "confidence": 0.94}
  ],
  "tempo": {"bpm": 85.2, "confidence": 0.96},
  "key": {"root": "G", "mode": "major", "confidence": 0.87},
  "reggae_features": {
    "riddim_type": "one_drop",
    "skank_pattern": "traditional",
    "bass_line_complexity": 0.73
  }
}
```

### Generated MIDI
- **Authentic reggae drum patterns** (One Drop kick on beat 3)
- **Walking bass lines** with reggae-specific note choices
- **Organ skanks** on off-beats 
- **Guitar chops** with proper timing and voicings

---

## 🛠️ Development Setup

### Prerequisites
- Python 3.8+
- ffmpeg (for audio processing)
- GPU with CUDA (optional, for faster stem separation)

### Development Installation

```bash
# Install development dependencies
pip install -r docker/requirements/dev.txt

# Install pre-commit hooks
pre-commit install

# Run tests
pytest tests/

# Run with GPU acceleration (if available)
export CUDA_VISIBLE_DEVICES=0
python test_enhanced_analysis.py
```

### Docker Development

```bash
# Build development container
docker build -f docker/Dockerfile.dev -t rootzengine:dev .

# Run with volume mounts
docker run -v $(pwd):/workspace -p 8000:8000 rootzengine:dev
```

---

## 🧪 Testing

### Quick Tests
```bash
# Basic functionality test
python simple_test.py

# Enhanced analysis test
python test_enhanced_analysis.py

# API health check
curl http://localhost:8000/health
```

### Test Suite
```bash
# Run all tests
pytest tests/

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
```

---

## 📚 Documentation

- **[Development Setup](DEV_SETUP.md)** - Detailed development environment setup
- **[PC Implementation Guide](PC_IMPLEMENTATION_CHECKLIST.md)** - Moving from mock to real processing
- **[MIDI Analysis Deep Dive](MIDI_CODE_ANALYSIS.md)** - Technical details of MIDI generation
- **[API Documentation](docs/api.md)** - REST API reference
- **[Architecture Overview](docs/architecture.md)** - System design and components

---

## 🎯 Use Cases

### Music Production
```python
# Analyze a reference track and generate similar patterns
analysis = analyzer.analyze_structure("classic_reggae.wav")
midi = converter.generate_similar_pattern(analysis, duration=32)
```

### Research & Analysis
```python
# Batch analyze a reggae collection
for track in reggae_collection:
    analysis = analyzer.analyze_structure(track)
    save_analysis_data(track, analysis)
```

### Live Performance
```python
# Real-time analysis for AI bandmate
stream_analyzer = StreamAnalyzer()
for audio_chunk in live_audio_stream:
    current_analysis = stream_analyzer.process_chunk(audio_chunk)
    accompaniment = generate_live_response(current_analysis)
    play_midi(accompaniment)
```

---

## 🔧 Configuration

### Basic Configuration
```python
# config.py
SAMPLE_RATE = 22050
HOP_LENGTH = 512
TEMPO_RANGE = (60, 120)  # Typical reggae BPM range
DEFAULT_RIDDIM = "one_drop"
```

### Cloud Configuration  
```yaml
# configs/azure.yaml
azure:
  storage_account: "your-storage-account"
  container_name: "rootzengine-audio"
  gpu_enabled: true
  batch_size: 4
```

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Quick Contribution Guide
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and add tests
4. Run the test suite: `pytest tests/`
5. Submit a pull request

### Areas for Contribution
- **Reggae Pattern Database**: Add more authentic riddim patterns
- **Audio Analysis**: Improve chord detection and harmonic analysis  
- **MIDI Generation**: Enhanced arrangement and orchestration features
- **Performance**: Optimization for real-time processing
- **Documentation**: Examples, tutorials, and use cases

---

## 🎵 Roadmap

### Current Features (v0.1.0)
- ✅ Basic audio analysis (tempo, key, structure)
- ✅ Reggae pattern recognition
- ✅ MIDI generation from analysis
- ✅ REST API with file upload
- ✅ Docker containerization

### Next Release (v0.2.0)
- 🔄 Real-time audio processing
- 🔄 Enhanced stem separation
- 🔄 GPU acceleration optimization
- 🔄 Advanced MIDI arrangements
- 🔄 Web interface for analysis visualization

### Future Vision (v1.0.0)
- 🎯 AI Bandmate: Real-time musical accompaniment
- 🎯 Style Transfer: Convert between reggae subgenres
- 🎯 Loop Generation: Create endless reggae variations
- 🎯 Educational Tools: Interactive reggae theory learning

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Bob Marley & The Wailers** - For the inspiration and foundation of reggae
- **Studio One & Treasure Isle** - For the original riddim patterns
- **Facebook Research** - For the Demucs stem separation model
- **librosa team** - For the excellent audio analysis tools
- **The Reggae Community** - For keeping the culture alive

---

## 📞 Support & Community

- **Issues**: [GitHub Issues](https://github.com/sonic-codex/rootzengine/issues)
- **Discussions**: [GitHub Discussions](https://github.com/sonic-codex/rootzengine/discussions)
- **Documentation**: [Project Wiki](https://github.com/sonic-codex/rootzengine/wiki)

---

**Made with dub delay and discipline** 🎛️  
*One Love, One Heart, One Codebase* 🦁