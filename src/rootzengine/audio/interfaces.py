"""Audio processing interfaces for local development and Azure delegation."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from pathlib import Path


class AudioProcessorInterface(ABC):
    """Abstract interface for audio processing operations."""
    
    @abstractmethod
    def analyze_structure(self, audio_path: str, **kwargs) -> Dict[str, Any]:
        """Analyze audio structure and return metadata."""
        pass
    
    @abstractmethod
    def extract_tempo(self, audio_path: str) -> float:
        """Extract tempo from audio file."""
        pass
    
    @abstractmethod
    def extract_key(self, audio_path: str) -> Dict[str, Any]:
        """Extract key and mode from audio file."""
        pass
    
    @abstractmethod
    def separate_stems(self, audio_path: str, output_dir: str) -> List[str]:
        """Separate audio into stems and return paths."""
        pass


class StemSeparatorInterface(ABC):
    """Abstract interface for stem separation."""
    
    @abstractmethod
    def separate(self, audio_path: str, output_dir: str, model: str = "demucs") -> Dict[str, str]:
        """Separate audio into stems."""
        pass


class FeatureExtractorInterface(ABC):
    """Abstract interface for audio feature extraction."""
    
    @abstractmethod
    def extract_features(self, audio_path: str) -> Dict[str, Any]:
        """Extract audio features for analysis."""
        pass
    
    @abstractmethod
    def extract_rhythm_features(self, audio_path: str) -> Dict[str, Any]:
        """Extract rhythm-specific features."""
        pass


class MockAudioProcessor(AudioProcessorInterface):
    """Mock audio processor for development without heavy dependencies."""
    
    def analyze_structure(self, audio_path: str, **kwargs) -> Dict[str, Any]:
        """Return mock structure analysis."""
        return {
            "sections": [
                {"start": 0.0, "end": 30.0, "label": "intro"},
                {"start": 30.0, "end": 120.0, "label": "verse"},
                {"start": 120.0, "end": 180.0, "label": "chorus"}
            ],
            "tempo": {"bpm": 85.0, "confidence": 0.9},
            "key": {"key": "A", "mode": "minor", "confidence": 0.85},
            "duration": 180.0,
            "sample_rate": 22050,
            "channels": 2
        }
    
    def extract_tempo(self, audio_path: str) -> float:
        """Return mock tempo."""
        return 85.0
    
    def extract_key(self, audio_path: str) -> Dict[str, Any]:
        """Return mock key detection."""
        return {"key": "A", "mode": "minor", "confidence": 0.85}
    
    def separate_stems(self, audio_path: str, output_dir: str) -> List[str]:
        """Return mock stem separation paths."""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Create mock stem files (empty for now)
        stems = ["bass.wav", "drums.wav", "vocals.wav", "other.wav"]
        stem_paths = []
        
        for stem in stems:
            stem_path = output_path / stem
            stem_path.touch()  # Create empty file
            stem_paths.append(str(stem_path))
        
        return stem_paths


class AzureAudioProcessor(AudioProcessorInterface):
    """Azure-based audio processor for production workloads."""
    
    def __init__(self, azure_config: Optional[Dict[str, Any]] = None):
        self.azure_config = azure_config or {}
        # This will be implemented to call Azure functions
    
    def analyze_structure(self, audio_path: str, **kwargs) -> Dict[str, Any]:
        """Delegate to Azure function for structure analysis."""
        # TODO: Implement Azure Function call
        raise NotImplementedError("Azure processing not yet implemented")
    
    def extract_tempo(self, audio_path: str) -> float:
        """Delegate to Azure function for tempo extraction."""
        # TODO: Implement Azure Function call
        raise NotImplementedError("Azure processing not yet implemented")
    
    def extract_key(self, audio_path: str) -> Dict[str, Any]:
        """Delegate to Azure function for key detection."""
        # TODO: Implement Azure Function call
        raise NotImplementedError("Azure processing not yet implemented")
    
    def separate_stems(self, audio_path: str, output_dir: str) -> List[str]:
        """Delegate to Azure function for stem separation."""
        # TODO: Implement Azure Function call
        raise NotImplementedError("Azure processing not yet implemented")


def get_audio_processor(use_azure: bool = False, config: Optional[Dict[str, Any]] = None) -> AudioProcessorInterface:
    """Factory function to get appropriate audio processor."""
    if use_azure:
        return AzureAudioProcessor(config)
    else:
        return MockAudioProcessor()