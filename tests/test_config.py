"""Tests for configuration system."""

import pytest
import os
import tempfile
from pathlib import Path

from rootzengine.core.config import Settings, AudioConfig, AzureConfig, load_settings


class TestAudioConfig:
    """Test audio configuration."""
    
    def test_default_values(self):
        """Test default audio configuration values."""
        config = AudioConfig()
        
        assert config.sample_rate == 22050
        assert config.hop_length == 512
        assert config.n_fft == 2048
    
    def test_environment_override(self):
        """Test environment variable override."""
        os.environ["AUDIO_SAMPLE_RATE"] = "44100"
        
        try:
            config = AudioConfig()
            assert config.sample_rate == 44100
        finally:
            os.environ.pop("AUDIO_SAMPLE_RATE", None)


class TestAzureConfig:
    """Test Azure configuration."""
    
    def test_default_values(self):
        """Test default Azure configuration values."""
        config = AzureConfig()
        
        assert config.storage_account == ""
        assert config.container_name == ""
        assert config.connection_string == ""
    
    def test_environment_override(self):
        """Test environment variable override."""
        os.environ["AZURE_STORAGE_ACCOUNT"] = "teststorage"
        os.environ["AZURE_CONTAINER_NAME"] = "testcontainer"
        
        try:
            config = AzureConfig()
            assert config.storage_account == "teststorage"
            assert config.container_name == "testcontainer"
        finally:
            os.environ.pop("AZURE_STORAGE_ACCOUNT", None)
            os.environ.pop("AZURE_CONTAINER_NAME", None)


class TestSettings:
    """Test main settings class."""
    
    def test_default_initialization(self):
        """Test default settings initialization."""
        settings = Settings()
        
        assert settings.environment == "development"
        assert settings.debug is False
        assert isinstance(settings.audio, AudioConfig)
        assert isinstance(settings.azure, AzureConfig)
    
    def test_nested_environment_variables(self):
        """Test nested environment variable parsing."""
        os.environ["AUDIO__SAMPLE_RATE"] = "44100"
        os.environ["AZURE__STORAGE_ACCOUNT"] = "testaccount"
        
        try:
            settings = Settings()
            assert settings.audio.sample_rate == 44100
            assert settings.azure.storage_account == "testaccount"
        finally:
            os.environ.pop("AUDIO__SAMPLE_RATE", None)
            os.environ.pop("AZURE__STORAGE_ACCOUNT", None)
    
    def test_from_yaml(self, tmp_path):
        """Test loading settings from YAML file."""
        config_file = tmp_path / "test_config.yaml"
        config_content = """
environment: production
debug: true
audio:
  sample_rate: 44100
  hop_length: 1024
azure:
  storage_account: testaccount
  container_name: testcontainer
"""
        config_file.write_text(config_content)
        
        settings = Settings.from_yaml(config_file)
        
        assert settings.environment == "production"
        assert settings.debug is True
        assert settings.audio.sample_rate == 44100
        assert settings.audio.hop_length == 1024
        assert settings.azure.storage_account == "testaccount"
        assert settings.azure.container_name == "testcontainer"


class TestLoadSettings:
    """Test settings loading function."""
    
    def test_load_settings_no_config(self):
        """Test loading settings without config file."""
        settings = load_settings()
        assert isinstance(settings, Settings)
        assert settings.environment == "development"
    
    def test_load_settings_with_config(self, tmp_path):
        """Test loading settings with config file."""
        config_file = tmp_path / "test_config.yaml"
        config_content = """
environment: testing
debug: true
"""
        config_file.write_text(config_content)
        
        settings = load_settings(config_file)
        
        assert settings.environment == "testing"
        assert settings.debug is True
    
    def test_load_settings_nonexistent_file(self):
        """Test loading settings with nonexistent config file."""
        settings = load_settings("nonexistent_config.yaml")
        assert isinstance(settings, Settings)
        assert settings.environment == "development"