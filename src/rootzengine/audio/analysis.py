"""Audio structure analysis with configurable backend."""

from typing import Dict, Any, Optional
from pathlib import Path
import os

from .interfaces import get_audio_processor, AudioProcessorInterface
from .reggae_patterns import reggae_detector
from ..core.config import settings


class AudioStructureAnalyzer:
    """Main audio structure analyzer with pluggable backends."""
    
    def __init__(self, processor: Optional[AudioProcessorInterface] = None):
        if processor is None:
            # Auto-detect based on environment or config
            use_azure = os.getenv("ROOTZ_USE_AZURE", "false").lower() == "true"
            self.processor = get_audio_processor(use_azure=use_azure, config=settings.azure)
        else:
            self.processor = processor
    
    def analyze_structure(self, audio_path: str, perform_separation: bool = True) -> Dict[str, Any]:
        """
        Analyze audio structure using configured processor.
        
        Args:
            audio_path: Path to audio file
            perform_separation: Whether to perform stem separation
            
        Returns:
            Dictionary containing structure analysis results
        """
        if not Path(audio_path).exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        # Get basic structure analysis
        structure = self.processor.analyze_structure(audio_path)
        
        # Add reggae pattern detection
        tempo = structure.get("tempo", {}).get("bpm", 85.0)
        reggae_analysis = reggae_detector.detect_pattern_mock(tempo, audio_path)
        structure["reggae_pattern"] = reggae_analysis
        
        # Add detailed rhythm characteristics
        if reggae_analysis.get("detected_style"):
            rhythm_chars = reggae_detector.analyze_rhythm_characteristics(
                tempo, reggae_analysis["detected_style"]
            )
            structure["rhythm_characteristics"] = rhythm_chars
        
        # Add stem separation if requested
        if perform_separation:
            try:
                stems_dir = Path(audio_path).parent / "stems"
                stems = self.processor.separate_stems(audio_path, str(stems_dir))
                structure["stems"] = {
                    "bass": next((s for s in stems if "bass" in Path(s).name), None),
                    "drums": next((s for s in stems if "drums" in Path(s).name), None),
                    "vocals": next((s for s in stems if "vocals" in Path(s).name), None),
                    "other": next((s for s in stems if "other" in Path(s).name), None)
                }
            except Exception as e:
                structure["stems"] = {"error": str(e)}
        
        return structure
    
    def extract_tempo(self, audio_path: str) -> float:
        """Extract tempo from audio file."""
        return self.processor.extract_tempo(audio_path)
    
    def extract_key(self, audio_path: str) -> Dict[str, Any]:
        """Extract key and mode from audio file."""
        return self.processor.extract_key(audio_path)