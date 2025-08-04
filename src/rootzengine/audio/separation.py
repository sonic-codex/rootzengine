"""Audio stem separation with configurable backend."""

from typing import Dict, List, Optional
from pathlib import Path
import os

from .interfaces import StemSeparatorInterface


class MockStemSeparator(StemSeparatorInterface):
    """Mock stem separator for development."""
    
    def separate(self, audio_path: str, output_dir: str, model: str = "demucs") -> Dict[str, str]:
        """Mock stem separation - creates empty files."""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True, parents=True)
        
        stems = ["bass", "drums", "vocals", "other"]
        stem_paths = {}
        
        for stem in stems:
            stem_file = output_path / f"{stem}.wav"
            stem_file.touch()  # Create empty file
            stem_paths[stem] = str(stem_file)
        
        return stem_paths


class AzureStemSeparator(StemSeparatorInterface):
    """Azure-based stem separator for production."""
    
    def __init__(self, azure_config: Optional[Dict] = None):
        self.azure_config = azure_config or {}
    
    def separate(self, audio_path: str, output_dir: str, model: str = "demucs") -> Dict[str, str]:
        """Delegate to Azure function for stem separation."""
        # TODO: Implement Azure Function call
        raise NotImplementedError("Azure stem separation not yet implemented")


def get_stem_separator(use_azure: bool = False, config: Optional[Dict] = None) -> StemSeparatorInterface:
    """Factory function to get appropriate stem separator."""
    if use_azure:
        return AzureStemSeparator(config)
    else:
        return MockStemSeparator()


# Legacy wrapper for backward compatibility
class DemucsWrapper:
    """Legacy wrapper for existing code compatibility."""
    
    def __init__(self):
        self.separator = get_stem_separator()
    
    def separate_stems(self, audio_path: str, output_dir: str) -> List[str]:
        """Separate stems and return list of paths."""
        stem_dict = self.separator.separate(audio_path, output_dir)
        return list(stem_dict.values())