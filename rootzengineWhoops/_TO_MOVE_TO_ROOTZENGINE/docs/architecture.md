# Architecture

- All config in `rootzengine/core/config.py` (Pydantic, YAML).
- Storage backend: Azure or Local, auto-selected.
- ML worker runs as a separate service (see `docker-compose.yml`).
- Audio modules: `audio/analysis.py`, `audio/separation.py`, etc.
