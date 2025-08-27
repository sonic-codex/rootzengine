import pytest
import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from rootzengine.audio.reggae_pattern_detector import detect_reggae_patterns

def test_detect_reggae_empty(tmp_path):
    audio_file = tmp_path / "silence.wav"
    # ... create silent WAV ...
    patterns = detect_reggae_patterns(str(audio_file))
    assert isinstance(patterns, list)
    assert patterns == []
