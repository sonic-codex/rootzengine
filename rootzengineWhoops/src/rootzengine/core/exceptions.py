"""Custom exceptions for RootzEngine"""

class RootzEngineError(Exception):
    """Base exception class for RootzEngine"""
    pass

class AudioProcessingError(RootzEngineError):
    """Raised when audio processing fails"""
    pass

class ModelError(RootzEngineError):
    """Raised when ML model operations fail"""
    pass

class StorageError(RootzEngineError):
    """Raised when storage operations fail"""
    pass

class ConfigurationError(RootzEngineError):
    """Raised when configuration is invalid"""
    pass