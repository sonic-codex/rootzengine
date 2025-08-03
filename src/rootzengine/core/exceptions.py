"""Custom exceptions for the RootzEngine application."""

class RootzEngineError(Exception):
    """Base exception for RootzEngine errors."""
    pass


class ConfigurationError(RootzEngineError):
    """Raised when there's an issue with configuration."""
    pass


class AudioProcessingError(RootzEngineError):
    """Raised when audio processing fails."""
    pass


class StemSeparationError(RootzEngineError):
    """Raised when stem separation fails."""
    pass


class MIDIConversionError(RootzEngineError):
    """Raised when MIDI conversion fails."""
    pass


class StorageError(RootzEngineError):
    """Raised for storage-related errors."""
    pass


class AzureError(StorageError):
    """Raised for Azure-specific errors."""
    pass


class ModelError(RootzEngineError):
    """Raised for ML model-related errors."""
    pass
