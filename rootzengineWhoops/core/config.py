"""
Configuration management for RootzEngine using Pydantic.

This module defines the settings for the application, allowing for environment-based
configuration and type validation. Settings can be loaded from environment variables
or a .env file.
"""

from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class AudioConfig(BaseSettings):
    """Configuration for audio processing parameters."""
    sample_rate: int = 44100
    hop_length: int = 512
    n_fft: int = 2048


class DemucsConfig(BaseSettings):
    """Configuration for Demucs stem separation."""
    model_name: str = "htdemucs_ft"
    device: str = "cpu"  # Can be overridden to "cuda" if a GPU is available


class AzureConfig(BaseSettings):
    """Configuration for Azure cloud services."""
    storage_account: Optional[str] = None
    container_name: Optional[str] = None
    connection_string: Optional[str] = None


class Settings(BaseSettings):
    """
    Main application settings class.

    Aggregates all configuration components and allows loading from a .env file.
    Prefixes for environment variables are inferred from the class structure
    (e.g., ROOTZENGINE_AUDIO__SAMPLE_RATE).
    """
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', env_nested_delimiter='__', env_prefix='ROOTZENGINE_')

    audio: AudioConfig = AudioConfig()
    demucs: DemucsConfig = DemucsConfig()
    azure: AzureConfig = AzureConfig()


# Create a single, global instance of the settings to be used throughout the application.
settings = Settings()