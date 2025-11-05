"""Configuration management for RootzEngine using Pydantic settings"""

from pathlib import Path
from typing import Optional
import os
import yaml
from pydantic import BaseModel, Field, ValidationError
from pydantic_settings import BaseSettings


class AudioConfig(BaseModel):
    """Audio processing configuration"""
    sample_rate: int = Field(default=44100, description="Audio sample rate in Hz")
    chunk_size: int = Field(default=1024, description="Processing chunk size")
    hop_length: int = Field(default=512, description="Hop length for STFT")
    n_fft: int = Field(default=2048, description="FFT window size")
    n_mels: int = Field(default=128, description="Number of mel bands")
    n_mfcc: int = Field(default=13, description="Number of MFCC coefficients")

    # Feature extraction
    extract_spectral: bool = Field(default=True, description="Extract spectral features")
    extract_rhythm: bool = Field(default=True, description="Extract rhythm features")
    extract_harmonic: bool = Field(default=True, description="Extract harmonic features")
    extract_energy: bool = Field(default=True, description="Extract energy features")

    # Pattern detection
    onset_threshold: float = Field(default=0.5, description="Onset detection threshold")
    beat_threshold: float = Field(default=0.3, description="Beat detection threshold")


class DemucsConfig(BaseModel):
    """Stem separation configuration using Demucs"""
    model_name: str = Field(default="htdemucs", description="Demucs model to use")
    device: str = Field(default="cpu", description="Device to use (cpu/cuda)")
    shifts: int = Field(default=1, description="Number of random shifts for better quality")
    split: bool = Field(default=True, description="Split audio into chunks to save memory")
    overlap: float = Field(default=0.25, description="Overlap between chunks")

    # Output stems
    output_bass: bool = Field(default=True, description="Output bass stem")
    output_drums: bool = Field(default=True, description="Output drums stem")
    output_vocals: bool = Field(default=True, description="Output vocals stem")
    output_other: bool = Field(default=True, description="Output other instruments stem")


class MIDIConfig(BaseModel):
    """MIDI processing and generation configuration"""
    tempo: int = Field(default=120, description="Default tempo in BPM")
    time_signature_numerator: int = Field(default=4, description="Time signature numerator")
    time_signature_denominator: int = Field(default=4, description="Time signature denominator")

    # Pattern generation
    humanize_timing: bool = Field(default=True, description="Add timing variation")
    humanize_velocity: bool = Field(default=True, description="Add velocity variation")
    timing_variance: float = Field(default=0.02, description="Timing variance (0-1)")
    velocity_variance: float = Field(default=0.15, description="Velocity variance (0-1)")

    # Quantization
    quantize: bool = Field(default=False, description="Quantize MIDI notes")
    quantize_resolution: float = Field(default=0.0625, description="Quantization resolution (16th note = 0.0625)")


class MLConfig(BaseModel):
    """Machine learning configuration"""
    model_path: Optional[str] = Field(default=None, description="Path to trained model")
    training_data_path: str = Field(default="data/training", description="Path to training data")
    checkpoint_dir: str = Field(default="data/checkpoints", description="Model checkpoint directory")

    # Training parameters
    batch_size: int = Field(default=32, description="Training batch size")
    learning_rate: float = Field(default=0.001, description="Learning rate")
    num_epochs: int = Field(default=100, description="Number of training epochs")
    early_stopping_patience: int = Field(default=10, description="Early stopping patience")

    # Model architecture
    hidden_size: int = Field(default=256, description="Hidden layer size")
    num_layers: int = Field(default=3, description="Number of layers")
    dropout: float = Field(default=0.3, description="Dropout rate")

    # Device
    device: str = Field(default="cpu", description="Device to use (cpu/cuda)")
    use_mixed_precision: bool = Field(default=False, description="Use mixed precision training")


class AzureConfig(BaseModel):
    """Azure storage configuration"""
    storage_account: str = Field(default="", description="Azure storage account name")
    container_name: str = Field(default="rootzengine", description="Azure container name")
    connection_string: str = Field(default="", description="Azure connection string")
    use_azure: bool = Field(default=False, description="Enable Azure storage")


class StorageConfig(BaseModel):
    """Storage configuration"""
    local_storage_path: str = Field(default="data/storage", description="Local storage path")
    use_azure: bool = Field(default=False, description="Use Azure storage")
    azure: AzureConfig = Field(default_factory=AzureConfig, description="Azure configuration")

    # Cache settings
    enable_cache: bool = Field(default=True, description="Enable file caching")
    cache_size_mb: int = Field(default=1024, description="Cache size in MB")


class APIConfig(BaseModel):
    """API server configuration"""
    host: str = Field(default="0.0.0.0", description="API host address")
    port: int = Field(default=8000, description="API port")
    debug: bool = Field(default=False, description="Debug mode")
    reload: bool = Field(default=False, description="Auto-reload on code changes")
    workers: int = Field(default=1, description="Number of worker processes")

    # CORS
    allow_origins: list[str] = Field(default=["*"], description="Allowed CORS origins")
    allow_credentials: bool = Field(default=True, description="Allow credentials")
    allow_methods: list[str] = Field(default=["*"], description="Allowed HTTP methods")
    allow_headers: list[str] = Field(default=["*"], description="Allowed HTTP headers")


class LoggingConfig(BaseModel):
    """Logging configuration"""
    level: str = Field(default="INFO", description="Logging level")
    log_file: Optional[str] = Field(default=None, description="Log file path")
    log_to_console: bool = Field(default=True, description="Log to console")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format string"
    )


class ProcessingConfig(BaseModel):
    """Processing pipeline configuration"""
    accuracy_threshold: float = Field(default=0.85, description="Minimum accuracy threshold")
    max_extraction_mode: bool = Field(default=True, description="Maximum extraction mode")
    preserve_intermediates: bool = Field(default=False, description="Keep intermediate files")

    # Pipeline stages
    enable_spectrotone: bool = Field(default=True, description="Enable spectrotone analysis")
    enable_stem_separation: bool = Field(default=True, description="Enable stem separation")
    enable_pattern_detection: bool = Field(default=True, description="Enable pattern detection")
    enable_midi_conversion: bool = Field(default=True, description="Enable MIDI conversion")


class RootzEngineConfig(BaseSettings):
    """Main configuration class for RootzEngine"""

    # Sub-configurations
    audio: AudioConfig = Field(default_factory=AudioConfig, description="Audio processing config")
    demucs: DemucsConfig = Field(default_factory=DemucsConfig, description="Demucs config")
    midi: MIDIConfig = Field(default_factory=MIDIConfig, description="MIDI config")
    ml: MLConfig = Field(default_factory=MLConfig, description="ML config")
    storage: StorageConfig = Field(default_factory=StorageConfig, description="Storage config")
    api: APIConfig = Field(default_factory=APIConfig, description="API config")
    logging: LoggingConfig = Field(default_factory=LoggingConfig, description="Logging config")
    processing: ProcessingConfig = Field(default_factory=ProcessingConfig, description="Processing config")

    # Environment
    environment: str = Field(default="development", description="Environment (development/production/test)")
    debug: bool = Field(default=False, description="Global debug mode")

    class Config:
        env_prefix = "ROOTZENGINE_"
        env_file = ".env"
        env_nested_delimiter = "__"
        case_sensitive = False


class RootzEngineSettings(BaseSettings):
    """Legacy settings class for backwards compatibility"""

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


# Global settings instances
settings = RootzEngineSettings()
config = RootzEngineConfig()


def load_config(config_model, config_path: Path):
    """
    Loads configuration from a YAML file and validates it with a Pydantic model.
    """
    if not config_path.is_file():
        raise FileNotFoundError(f"Configuration file not found at {config_path}")

    with open(config_path, "r") as f:
        config_data = yaml.safe_load(f)

    try:
        return config_model(**config_data.get("azure", {}))
    except (ValidationError, TypeError) as e:
        raise ValueError(f"Azure configuration validation error in {config_path}: {e}") from e