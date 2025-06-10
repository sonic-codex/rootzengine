# Testing Strategy for RootzEngine

This document outlines the testing approach for the project.

## Test Types
- **Unit tests:** For all major modules (see `utils/`, `pipeline.py`).
- **Integration tests:** For workflows spanning multiple modules.

## Structure
- All tests are in `/tests`, mirroring the main codebase structure.
- Test files are named `test_*.py`.

## Running Tests
- Use `pytest` for running tests: `pytest tests/`
- Tests are run automatically in CI (see `.github/workflows/ci.yml`).

## Guidelines
- Write clear, isolated tests.
- Use fixtures for setup/teardown.
- Mock external dependencies.

See also: `docs/04-Code_Style_And_Linting.md` and `CONTRIBUTING.md`.
