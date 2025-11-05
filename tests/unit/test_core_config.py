"""Tests for configuration module"""

import pytest
from pathlib import Path

from rootzengine.core.config import (
    RootzEngineConfig,
    RootzEngineSettings,
    AudioConfig,
    MIDIConfig,
    MLConfig,
    AzureConfig,
    settings,
    config,
)


class TestAudioConfig:
    """Test AudioConfig"""

    def test_default_values(self):
        """Test default configuration values"""
        audio_config = AudioConfig()

        assert audio_config.sample_rate == 44100
        assert audio_config.chunk_size == 1024
        assert audio_config.hop_length == 512
        assert audio_config.n_fft == 2048
        assert audio_config.n_mels == 128
        assert audio_config.n_mfcc == 13

    def test_custom_values(self):
        """Test custom configuration values"""
        audio_config = AudioConfig(
            sample_rate=22050,
            chunk_size=2048,
            n_mels=256,
        )

        assert audio_config.sample_rate == 22050
        assert audio_config.chunk_size == 2048
        assert audio_config.n_mels == 256


class TestMIDIConfig:
    """Test MIDIConfig"""

    def test_default_values(self):
        """Test default MIDI configuration"""
        midi_config = MIDIConfig()

        assert midi_config.tempo == 120
        assert midi_config.time_signature_numerator == 4
        assert midi_config.time_signature_denominator == 4
        assert midi_config.humanize_timing is True
        assert midi_config.humanize_velocity is True

    def test_humanization_settings(self):
        """Test humanization settings"""
        midi_config = MIDIConfig(
            timing_variance=0.03,
            velocity_variance=0.20,
        )

        assert midi_config.timing_variance == 0.03
        assert midi_config.velocity_variance == 0.20


class TestMLConfig:
    """Test MLConfig"""

    def test_default_values(self):
        """Test default ML configuration"""
        ml_config = MLConfig()

        assert ml_config.batch_size == 32
        assert ml_config.learning_rate == 0.001
        assert ml_config.num_epochs == 100
        assert ml_config.device == "cpu"

    def test_training_parameters(self):
        """Test training parameter configuration"""
        ml_config = MLConfig(
            batch_size=64,
            learning_rate=0.0001,
            num_epochs=50,
        )

        assert ml_config.batch_size == 64
        assert ml_config.learning_rate == 0.0001
        assert ml_config.num_epochs == 50


class TestAzureConfig:
    """Test AzureConfig"""

    def test_default_values(self):
        """Test default Azure configuration"""
        azure_config = AzureConfig()

        assert azure_config.storage_account == ""
        assert azure_config.container_name == "rootzengine"
        assert azure_config.use_azure is False

    def test_custom_values(self):
        """Test custom Azure configuration"""
        azure_config = AzureConfig(
            storage_account="teststorage",
            container_name="testcontainer",
            use_azure=True,
        )

        assert azure_config.storage_account == "teststorage"
        assert azure_config.container_name == "testcontainer"
        assert azure_config.use_azure is True


class TestRootzEngineConfig:
    """Test main RootzEngineConfig"""

    def test_initialization(self):
        """Test config initialization"""
        config = RootzEngineConfig()

        # Check that all sub-configs are initialized
        assert config.audio is not None
        assert config.midi is not None
        assert config.ml is not None
        assert config.storage is not None
        assert config.api is not None
        assert config.logging is not None
        assert config.processing is not None

    def test_nested_config_access(self):
        """Test accessing nested configuration"""
        config = RootzEngineConfig()

        # Access nested config values
        assert config.audio.sample_rate == 44100
        assert config.midi.tempo == 120
        assert config.ml.batch_size == 32

    def test_environment_setting(self):
        """Test environment configuration"""
        config = RootzEngineConfig(environment="production")

        assert config.environment == "production"


class TestGlobalSettings:
    """Test global settings instances"""

    def test_settings_instance(self):
        """Test that global settings instance is accessible"""
        assert settings is not None
        assert isinstance(settings, RootzEngineSettings)

    def test_config_instance(self):
        """Test that global config instance is accessible"""
        assert config is not None
        assert isinstance(config, RootzEngineConfig)
