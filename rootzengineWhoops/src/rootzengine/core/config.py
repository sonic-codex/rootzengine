"""Configuration management using Pydantic settings"""

from pydantic import BaseSettings, Field
from typing import Optional
import os

class RootzEngineSettings(BaseSettings):
    """Main configuration class for RootzEngine"""
    
    # Audio processing settings
    sample_rate: int = Field(default=44100, description="Default audio sample rate")
    chunk_size: int = Field(default=1024, description="Audio processing chunk size")
    
    # ML model settings
    model_path: Optional[str] = Field(default=None, description="Path to trained model")
    training_data_path: str = Field(default="data/training", description="Path to training data")
    
    # Storage settings
    azure_connection_string: Optional[str] = Field(default=None, description="Azure storage connection string")
    local_storage_path: str = Field(default="data/storage", description="Local storage path")
    
    # API settings
    api_host: str = Field(default="0.0.0.0", description="API host address")
    api_port: int = Field(default=8000, description="API port")
    debug: bool = Field(default=False, description="Debug mode")
    
    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    log_file: Optional[str] = Field(default=None, description="Log file path")
    
    class Config:
        env_prefix = "ROOTZENGINE_"
        env_file = ".env"

# Global settings instance
settings = RootzEngineSettings()