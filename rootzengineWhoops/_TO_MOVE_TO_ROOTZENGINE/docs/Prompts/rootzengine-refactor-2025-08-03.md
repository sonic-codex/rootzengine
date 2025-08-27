# RootzEngine Refactor Instructions for Coding Agent

## Project Overview

Refactor the existing RootzEngine reggae AI analysis pipeline into a modern, containerized architecture with advanced audio structure analysis. The goal is to build an AI bandmate that can understand song structure and respond musically in real-time.

## Core Requirements

### 1. Audio Structure Analysis Pipeline

Create a comprehensive audio analysis system that identifies musical sections:

**Required Analysis Features:**

* **Structural Segmentation** : Detect intro, verse, chorus, bridge, outro, instrumental breaks
* **Tempo/Beat Tracking** : BPM detection with beat grid alignment
* **Key/Chord Analysis** : Root key detection and chord progression analysis
* **Energy/Dynamics** : RMS energy levels, spectral centroid, zero-crossing rate
* **Reggae-Specific Features** : One Drop detection, skank pattern recognition, riddim classification
* **Onset Detection** : Note onsets for MIDI conversion timing

**Implementation Stack:**

* `librosa` for core audio analysis
* `madmom` for beat tracking and onset detection
* `essentia` for advanced music analysis features
* `chord-recognition` or `chroma-chord` for harmonic analysis
* Custom reggae pattern detection algorithms

### 2. Modern Project Architecture

**Directory Structure:**

```
rootzengine/
├── docker/
│   ├── Dockerfile.dev           # Development container
│   ├── Dockerfile.prod          # Production container  
│   ├── docker-compose.yml       # Multi-service setup
│   └── requirements/
│       ├── base.txt
│       ├── dev.txt
│       └── prod.txt
├── src/rootzengine/
│   ├── __init__.py
│   ├── core/
│   │   ├── config.py            # Configuration management
│   │   └── exceptions.py        # Custom exceptions
│   ├── audio/
│   │   ├── __init__.py
│   │   ├── separation.py        # Demucs stem separation
│   │   ├── analysis.py          # Audio structure analysis
│   │   ├── features.py          # Feature extraction
│   │   └── reggae_patterns.py   # Reggae-specific detection
│   ├── midi/
│   │   ├── __init__.py
│   │   ├── converter.py         # Audio to MIDI conversion
│   │   └── patterns.py          # MIDI pattern generation
│   ├── ml/
│   │   ├── __init__.py
│   │   ├── dataset.py           # Training data preparation
│   │   ├── models.py            # ML model definitions
│   │   └── training.py          # Training pipeline
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── local.py             # Local file operations
│   │   └── azure.py             # Azure Storage integration
│   └── api/
│       ├── __init__.py
│       ├── main.py              # FastAPI application
│       └── routes/              # API endpoints
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── scripts/
│   ├── cli.py                   # Command-line interface
│   ├── process_batch.py         # Batch processing
│   └── setup_dev.py            # Development setup
├── configs/
│   ├── development.yaml
│   ├── production.yaml
│   └── azure.yaml
├── data/
│   ├── raw/                     # Input audio files
│   ├── processed/               # Processed stems and analysis
│   ├── midi/                    # Generated MIDI files
│   └── models/                  # Trained ML models
└── docs/
    ├── api.md
    ├── setup.md
    └── architecture.md
```

### 3. Audio Analysis Implementation Details

**Structure Analysis Class:**

```python
class AudioStructureAnalyzer:
    def analyze_structure(self, audio_path: str) -> Dict:
        """
        Returns:
        {
            "sections": [
                {"start": 0.0, "end": 16.0, "label": "intro", "confidence": 0.95},
                {"start": 16.0, "end": 48.0, "label": "verse", "confidence": 0.87},
                {"start": 48.0, "end": 80.0, "label": "chorus", "confidence": 0.92}
            ],
            "tempo": {"bpm": 75.2, "confidence": 0.94},
            "key": {"root": "C", "mode": "major", "confidence": 0.81},
            "energy_profile": [...],
            "reggae_features": {
                "riddim_type": "one_drop",
                "skank_pattern": "traditional",
                "bass_line_complexity": 0.67
            }
        }
        """
```

**Processing Pipeline:**

1. **Load audio** with librosa at consistent sample rate
2. **Extract features** : MFCC, chroma, spectral features, tempo
3. **Segment structure** using similarity matrices and novelty detection
4. **Classify sections** with trained models or rule-based heuristics
5. **Detect reggae patterns** with custom algorithms
6. **Generate metadata** in structured JSON format

### 4. Docker Configuration

**Development Container Features:**

* Ubuntu 22.04 base with audio libraries
* GPU support for future ML training
* Volume mounts for development files
* Hot-reload for code changes
* Jupyter lab for experimentation

**Required System Dependencies:**

```dockerfile
# Audio processing
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    libasound2-dev \
    portaudio19-dev \
    libportaudiocpp0 \
    && rm -rf /var/lib/apt/lists/*
```

**Python Dependencies:**

```
# Core audio processing
librosa>=0.10.0
soundfile>=0.12.0
demucs>=4.0.0
madmom>=0.16.1
essentia>=2.1b6

# MIDI processing  
pretty_midi>=0.2.10
mido>=1.3.0

# ML and data science
numpy>=1.24.0
scipy>=1.10.0
scikit-learn>=1.3.0
pandas>=2.0.0

# Structure analysis
msaf>=0.1.91
chord_recognition>=0.1.0

# Configuration and storage
pydantic>=2.0.0
pydantic-settings>=2.0.0
azure-storage-blob>=12.0.0
PyYAML>=6.0

# API and CLI
fastapi>=0.104.0
uvicorn>=0.24.0
typer>=0.9.0

# Development tools
pytest>=7.4.0
black>=23.0.0
isort>=5.12.0
mypy>=1.6.0
```

### 5. Configuration Management

**Environment-based config with Pydantic:**

```python
class AudioConfig(BaseSettings):
    sample_rate: int = 22050
    hop_length: int = 512
    n_fft: int = 2048
  
class DemucsConfig(BaseSettings):
    model_name: str = "htdemucs_ft"
    device: str = "cpu"  # or "cuda"
  
class AzureConfig(BaseSettings):
    storage_account: str
    container_name: str
    connection_string: str
```

### 6. CLI Interface

**Command Structure:**

```bash
# Single file processing
python -m rootzengine analyze /path/to/song.mp3 --output-dir ./results

# Batch processing
python -m rootzengine batch /path/to/songs/ --workers 4 --cloud

# Start API server
python -m rootzengine serve --port 8000 --reload

# Train models
python -m rootzengine train --dataset ./data/training --model reggae_structure
```

### 7. Integration Points

**Stem Separation Integration:**

* Preserve existing Demucs functionality
* Add pre-analysis step before separation
* Use structure info to improve stem quality
* Generate metadata that links stems to song sections

**MIDI Generation Enhancement:**

* Use structure analysis to inform MIDI timing
* Apply different generation strategies per section type
* Maintain consistency within sections
* Add section transition handling

**ML Training Data:**

* Structure analysis creates rich training labels
* Pair audio features with musical context
* Enable section-aware model training
* Support transfer learning from pre-trained models

### 8. Testing Strategy

**Test Coverage Requirements:**

* Unit tests for all audio analysis functions
* Integration tests for full pipeline
* Regression tests for audio processing quality
* Performance benchmarks for processing speed
* Docker container functionality tests

**Test Data:**

* Include diverse reggae samples in tests
* Create synthetic test cases for edge cases
* Mock Azure services for local testing
* Provide golden reference outputs

### 9. Documentation Requirements

**Technical Documentation:**

* API reference with OpenAPI specs
* Architecture decision records (ADRs)
* Performance optimization guide
* Deployment instructions for Azure

**User Documentation:**

* Quick start guide with examples
* Configuration reference
* Troubleshooting guide
* Contributing guidelines

### 10. Azure Cloud Integration

**Storage Strategy:**

* Azure Blob Storage for audio files and results
* Hierarchical namespace for organization
* Lifecycle policies for cost optimization
* CDN integration for fast access

**Compute Strategy:**

* Azure Container Instances for batch processing
* Azure ML for model training and inference
* Azure Functions for lightweight processing
* Auto-scaling based on queue depth

**Security:**

* Managed identity for Azure services
* Key Vault for sensitive configuration
* Network security groups for isolation
* Audit logging for compliance

## Success Criteria

1. **Functional Pipeline** : Complete audio → structure analysis → MIDI generation
2. **Containerized** : Runs consistently in Docker across environments
3. **Scalable** : Handles single files locally, batches in cloud
4. **Extensible** : Clear interfaces for adding new analysis features
5. **Production Ready** : Proper logging, error handling, monitoring
6. **Well Tested** : Comprehensive test suite with good coverage
7. **Documented** : Clear setup and usage instructions

## Implementation Priority

1. **Core refactoring** : Project structure and Docker setup
2. **Audio structure analysis** : Implement segmentation and feature extraction
3. **Integration** : Connect with existing stem separation
4. **MIDI enhancement** : Use structure info in MIDI generation
5. **Azure integration** : Cloud storage and compute setup
6. **API development** : RESTful endpoints for processing
7. **ML pipeline** : Training data preparation and model development

## Notes for Agent

* Preserve all existing functionality from current codebase
* Focus on modularity and testability
* Use type hints throughout Python code
* Follow PEP 8 and include linting configuration
* Add comprehensive error handling and logging
* Design for both local development and cloud deployment
* Consider memory usage for large audio files
* Plan for real-time processing requirements
