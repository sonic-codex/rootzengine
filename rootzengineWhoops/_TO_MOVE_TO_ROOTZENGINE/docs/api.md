# API Reference

## Configuration

Edit YAML files in `configs/` and load via `RootzEngineSettings`.

## CLI

- `python scripts/cli.py analyze <audio_path>`
- `python scripts/cli.py batch <directory>`
- `python scripts/cli.py serve`
- `python scripts/cli.py train <data_dir>`

## FastAPI

- Startup/shutdown events handled in `rootzengine/api/main.py`
- Storage backend auto-selects Local or Azure
