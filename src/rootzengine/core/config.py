"""Core configuration management for RootzEngine."""

import os
from pathlib import Path
from typing import Dict, List, Optional, Union

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Base directory for the project
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent


class AudioConfig(BaseSettings):
    """Audio processing configuration."""
    
    sample_rate: int = 22050
    hop_length: int = 512
    n_fft: int = 2048
    
    model_config = SettingsConfigDict(env_prefix="AUDIO_")


class DemucsConfig(BaseSettings):
    """Configuration for Demucs stem separation."""
    
    model_name: str = "htdemucs_ft"
    device: str = "cpu"  # or "cuda"
    stems: List[str] = ["bass", "drums", "other", "vocals"]
    
    model_config = SettingsConfigDict(env_prefix="DEMUCS_")


class StorageConfig(BaseSettings):
    """Local storage configuration."""
    
    project_root: Path = BASE_DIR
    raw_dir: Path = Field(default_factory=lambda: BASE_DIR / "data" / "raw")
    processed_dir: Path = Field(default_factory=lambda: BASE_DIR / "data" / "processed")
    midi_dir: Path = Field(default_factory=lambda: BASE_DIR / "data" / "midi")
    models_dir: Path = Field(default_factory=lambda: BASE_DIR / "data" / "models")
    
    model_config = SettingsConfigDict(env_prefix="STORAGE_")


class AzureConfig(BaseSettings):
    """Azure cloud storage configuration."""
    
    storage_account: str = ""
    container_name: str = ""
    connection_string: str = ""
    
    model_config = SettingsConfigDict(env_prefix="AZURE_")


class Settings(BaseSettings):
    """Main application settings combining all config sections."""
    
    environment: str = "development"
    debug: bool = False
    
    audio: AudioConfig = Field(default_factory=AudioConfig)
    demucs: DemucsConfig = Field(default_factory=DemucsConfig)
    storage: StorageConfig = Field(default_factory=StorageConfig)
    azure: Optional[AzureConfig] = Field(default_factory=AzureConfig)
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="allow",
    )
    
    @classmethod
    def from_yaml(cls, config_path: Union[str, Path]) -> "Settings":
        """Load settings from a YAML file."""
        with open(config_path, "r") as f:
            config_data = yaml.safe_load(f)
        
        # Convert loaded YAML into flat dictionary with nested delimiters
        flat_dict = {}
        
        def flatten_dict(d: Dict, prefix: str = ""):
            for key, value in d.items():
                new_key = f"{prefix}{key}" if prefix else key
                if isinstance(value, dict):
                    flatten_dict(value, f"{new_key}__")
                else:
                    flat_dict[new_key] = value
        
        flatten_dict(config_data)
        return cls(**flat_dict)


# Create default settings instance
settings = Settings()


def load_settings(config_path: Optional[Union[str, Path]] = None) -> Settings:
    """Load settings from environment variables and optionally from a YAML file."""
    if config_path and os.path.exists(config_path):
        return Settings.from_yaml(config_path)
    return Settings()
