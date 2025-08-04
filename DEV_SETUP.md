# RootzEngine Development Setup

## Overview

RootzEngine is now configured for cross-platform development with Pi-friendly local development and Azure-based audio processing. This setup allows you to develop on Pi while delegating heavy audio processing to Azure.

## Quick Start

### 1. Environment Setup

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install development dependencies (Pi-friendly)
pip install -r requirements-dev.txt

# Install package in development mode
pip install --no-deps -e .

# Install core dependencies manually (due to Pi ARM issues)
pip install PyYAML fastapi uvicorn pytest pytest-mock pydantic-settings
```

### 2. Configuration

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` to configure your environment:
- Set `ROOTZ_USE_AZURE=false` for local development with mocks
- Set `ROOTZ_USE_AZURE=true` for Azure-based processing (production)

### 3. Testing

Run tests to verify setup:
```bash
# Quick verification
python simple_test.py

# Full test suite
python -m pytest tests/test_mock_interfaces.py tests/test_config.py tests/test_integration.py -v
```

## Architecture

### Mock vs Azure Processing

The system uses a plugin architecture that switches between mock and Azure processing:

**Mock Mode (Pi Development):**
- `MockAudioProcessor`: Returns realistic fake data for development
- `MockStemSeparator`: Creates empty stem files for testing
- No heavy audio dependencies required

**Azure Mode (Production):**
- `AzureAudioProcessor`: Delegates to Azure Functions (TODO: implement)
- `AzureStemSeparator`: Uses cloud-based Demucs processing
- Requires full audio processing dependencies

### Key Components

1. **Audio Processing Interfaces** (`src/rootzengine/audio/interfaces.py`)
   - Abstract interfaces for audio processing
   - Factory functions for getting appropriate processors

2. **Audio Structure Analyzer** (`src/rootzengine/audio/analysis.py`)
   - Main entry point for audio analysis
   - Auto-detects processing backend based on environment

3. **Configuration System** (`src/rootzengine/core/config.py`)
   - Environment-based configuration
   - YAML file support for different environments
   - Nested settings with Pydantic validation

## File Structure

```
rootzengine/
├── requirements-dev.txt          # Pi-friendly dependencies
├── requirements-azure.txt        # Full Azure dependencies
├── .env.example                  # Environment template
├── configs/
│   ├── development.yaml          # Development configuration
│   └── production.yaml           # Production configuration
├── src/rootzengine/
│   ├── audio/
│   │   ├── interfaces.py         # Audio processing interfaces
│   │   ├── analysis.py           # Main analyzer
│   │   └── separation.py         # Stem separation
│   └── core/
│       ├── config.py             # Configuration system
│       └── exceptions.py         # Custom exceptions
└── tests/
    ├── test_mock_interfaces.py   # Interface tests
    ├── test_config.py            # Configuration tests
    └── test_integration.py       # End-to-end tests
```

## Development Workflow

### On Pi (Local Development)
1. Edit business logic, API endpoints, configuration
2. Write and run tests with mock audio processing
3. Develop MIDI processing, storage logic, web interfaces
4. Test with synthetic audio data

### On Azure (Production Processing)
1. Deploy audio processing functions
2. Implement real Demucs stem separation
3. Process actual audio files
4. Run performance tests

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ROOTZ_USE_AZURE` | Use Azure processing vs mocks | `false` |
| `ENVIRONMENT` | Environment name | `development` |
| `DEBUG` | Enable debug mode | `true` |
| `AZURE_STORAGE_ACCOUNT` | Azure storage account | `""` |
| `AZURE_CONTAINER_NAME` | Azure container name | `""` |
| `AZURE_CONNECTION_STRING` | Azure connection string | `""` |

## What Works on Pi

✅ **Fully Functional:**
- Package installation and imports
- Configuration system
- Mock audio processing
- API development (FastAPI)
- MIDI processing
- Azure storage integration
- Unit and integration testing

✅ **Limited but Workable:**
- Basic audio I/O with soundfile
- Simple audio generation for testing

❌ **Not Recommended on Pi:**
- Real audio processing (librosa, essentia)
- ML model training/inference
- Heavy stem separation (Demucs)

## Next Steps

1. **Implement Azure Functions** for real audio processing
2. **Create API endpoints** for audio analysis requests
3. **Set up CI/CD pipeline** for automated testing
4. **Add MIDI generation** based on reggae patterns
5. **Implement storage backends** for processed data

## Testing

The system includes comprehensive tests:
- **Mock Interface Tests**: Verify mock processors work correctly
- **Configuration Tests**: Test environment and YAML configuration
- **Integration Tests**: End-to-end system testing

All tests pass on Pi and verify the development setup is working correctly.