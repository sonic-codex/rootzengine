"""Integration tests for the complete system."""

import pytest
import tempfile
import os
from pathlib import Path

from rootzengine.audio.analysis import AudioStructureAnalyzer
from rootzengine.audio.interfaces import MockAudioProcessor
from rootzengine.core.config import Settings


class TestIntegration:
    """Test the complete system integration."""
    
    def test_end_to_end_mock_analysis(self, tmp_path):
        """Test end-to-end analysis with mock processor."""
        # Create a dummy audio file
        audio_file = tmp_path / "test_song.wav"
        audio_file.touch()
        
        # Create analyzer with mock processor
        processor = MockAudioProcessor()
        analyzer = AudioStructureAnalyzer(processor=processor)
        
        # Run full analysis
        result = analyzer.analyze_structure(str(audio_file), perform_separation=True)
        
        # Verify complete structure
        assert "sections" in result
        assert "tempo" in result
        assert "key" in result
        assert "stems" in result
        
        # Verify sections structure
        sections = result["sections"]
        assert len(sections) == 3
        assert sections[0]["label"] == "intro"
        assert sections[1]["label"] == "verse"
        assert sections[2]["label"] == "chorus"
        
        # Verify tempo detection
        tempo = result["tempo"]
        assert tempo["bpm"] == 85.0
        assert tempo["confidence"] == 0.9
        
        # Verify key detection
        key = result["key"]
        assert key["key"] == "A"
        assert key["mode"] == "minor"
        assert key["confidence"] == 0.85
        
        # Verify stem separation
        stems = result["stems"]
        assert "bass" in stems
        assert "drums" in stems
        assert "vocals" in stems
        assert "other" in stems
        
        # Verify stem files exist
        for stem_type, stem_path in stems.items():
            if stem_path:  # Some stems might be None
                assert Path(stem_path).exists()
    
    def test_environment_switching(self):
        """Test switching between mock and Azure modes."""
        # Test mock mode (default)
        os.environ.pop("ROOTZ_USE_AZURE", None)
        analyzer = AudioStructureAnalyzer()
        assert isinstance(analyzer.processor, MockAudioProcessor)
        
        # Test Azure mode flag
        os.environ["ROOTZ_USE_AZURE"] = "true"
        try:
            analyzer = AudioStructureAnalyzer()
            # Should be Azure processor, but we can't test it fully without Azure setup
            assert analyzer.processor is not None
        finally:
            os.environ.pop("ROOTZ_USE_AZURE", None)
    
    def test_config_integration(self, tmp_path):
        """Test configuration system integration."""
        # Create a test config file
        config_file = tmp_path / "test_config.yaml"
        config_content = """
environment: testing
debug: true
audio:
  sample_rate: 44100
  hop_length: 1024
azure:
  storage_account: testaccount
  container_name: testcontainer
"""
        config_file.write_text(config_content)
        
        # Load settings
        from rootzengine.core.config import load_settings
        settings = load_settings(config_file)
        
        # Verify configuration loaded correctly
        assert settings.environment == "testing"
        assert settings.debug is True
        assert settings.audio.sample_rate == 44100
        assert settings.audio.hop_length == 1024
        assert settings.azure.storage_account == "testaccount"
        assert settings.azure.container_name == "testcontainer"
    
    def test_package_imports(self):
        """Test that all key components can be imported."""
        # Core components
        from rootzengine.audio.analysis import AudioStructureAnalyzer
        from rootzengine.audio.interfaces import MockAudioProcessor, get_audio_processor
        from rootzengine.audio.separation import DemucsWrapper, get_stem_separator
        from rootzengine.core.config import Settings, load_settings
        
        # Verify they can be instantiated
        analyzer = AudioStructureAnalyzer()
        processor = MockAudioProcessor()
        wrapper = DemucsWrapper()
        settings = Settings()
        
        assert analyzer is not None
        assert processor is not None
        assert wrapper is not None
        assert settings is not None
    
    @pytest.mark.parametrize("perform_separation", [True, False])
    def test_analysis_with_separation_flag(self, tmp_path, perform_separation):
        """Test analysis with and without stem separation."""
        # Create dummy audio file
        audio_file = tmp_path / "test.wav"
        audio_file.touch()
        
        # Run analysis
        analyzer = AudioStructureAnalyzer()
        result = analyzer.analyze_structure(str(audio_file), perform_separation=perform_separation)
        
        # Check stem separation results based on flag
        if perform_separation:
            assert "stems" in result
            assert isinstance(result["stems"], dict)
        else:
            assert "stems" not in result
    
    def test_error_handling(self):
        """Test error handling for various scenarios."""
        analyzer = AudioStructureAnalyzer()
        
        # Test file not found
        with pytest.raises(FileNotFoundError):
            analyzer.analyze_structure("nonexistent_file.wav")
        
        # Test extract methods work
        assert analyzer.extract_tempo("dummy.wav") == 85.0
        
        key_info = analyzer.extract_key("dummy.wav")
        assert "key" in key_info
        assert "mode" in key_info