import pytest
from rootzengine.core.config import RootzEngineSettings

def test_settings_load_yaml(tmp_path):
    yaml = tmp_path / "test.yaml"
    yaml.write_text("audio:\n  sample_rate: 44100\n")
    settings = RootzEngineSettings.model_validate_yaml(yaml)
    assert settings.audio.sample_rate == 44100

def test_azure_config_defaults():
    settings = RootzEngineSettings()
    assert hasattr(settings, "azure")
