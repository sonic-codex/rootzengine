"""Tests for mock audio processing interfaces."""

import pytest
from pathlib import Path
import tempfile
import os

from rootzengine.audio.interfaces import MockAudioProcessor, get_audio_processor
from rootzengine.audio.analysis import AudioStructureAnalyzer
from rootzengine.audio.separation import MockStemSeparator


class TestMockAudioProcessor:
    """Test the mock audio processor."""
    
    def test_analyze_structure(self):
        """Test structure analysis returns expected format."""
        processor = MockAudioProcessor()
        result = processor.analyze_structure("dummy_path.wav")
        
        assert "sections" in result
        assert "tempo" in result
        assert "key" in result
        assert isinstance(result["sections"], list)
        assert len(result["sections"]) > 0
        assert result["tempo"]["bpm"] == 85.0
    
    def test_extract_tempo(self):
        """Test tempo extraction returns float."""
        processor = MockAudioProcessor()
        tempo = processor.extract_tempo("dummy_path.wav")
        
        assert isinstance(tempo, float)
        assert tempo > 0
    
    def test_extract_key(self):
        """Test key extraction returns expected format."""
        processor = MockAudioProcessor()
        key_info = processor.extract_key("dummy_path.wav")
        
        assert "key" in key_info
        assert "mode" in key_info
        assert "confidence" in key_info
    
    def test_separate_stems(self):
        """Test stem separation creates files."""
        processor = MockAudioProcessor()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            stems = processor.separate_stems("dummy_path.wav", temp_dir)
            
            assert len(stems) == 4  # bass, drums, vocals, other
            for stem_path in stems:
                assert Path(stem_path).exists()


class TestMockStemSeparator:
    """Test the mock stem separator."""
    
    def test_separate(self):
        """Test stem separation creates expected files."""
        separator = MockStemSeparator()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = separator.separate("dummy_path.wav", temp_dir)
            
            expected_stems = ["bass", "drums", "vocals", "other"]
            assert set(result.keys()) == set(expected_stems)
            
            for stem_name, stem_path in result.items():
                assert Path(stem_path).exists()
                assert stem_name in Path(stem_path).name


class TestAudioStructureAnalyzer:
    """Test the main audio structure analyzer."""
    
    def test_initialization_with_mock(self):
        """Test analyzer initializes with mock processor."""
        mock_processor = MockAudioProcessor()
        analyzer = AudioStructureAnalyzer(processor=mock_processor)
        
        assert analyzer.processor is mock_processor
    
    def test_initialization_auto_detect(self):
        """Test analyzer auto-detects processor based on environment."""
        # Ensure we get mock processor when not using Azure
        os.environ.pop("ROOTZ_USE_AZURE", None)
        analyzer = AudioStructureAnalyzer()
        
        assert isinstance(analyzer.processor, MockAudioProcessor)
    
    def test_analyze_structure_no_separation(self, tmp_path):
        """Test structure analysis without stem separation."""
        # Create a dummy audio file
        dummy_audio = tmp_path / "test.wav"
        dummy_audio.touch()
        
        analyzer = AudioStructureAnalyzer()
        result = analyzer.analyze_structure(str(dummy_audio), perform_separation=False)
        
        assert "sections" in result
        assert "tempo" in result
        assert "key" in result
        assert "stems" not in result
    
    def test_analyze_structure_with_separation(self, tmp_path):
        """Test structure analysis with stem separation."""
        # Create a dummy audio file
        dummy_audio = tmp_path / "test.wav"
        dummy_audio.touch()
        
        analyzer = AudioStructureAnalyzer()
        result = analyzer.analyze_structure(str(dummy_audio), perform_separation=True)
        
        assert "sections" in result
        assert "tempo" in result
        assert "key" in result
        assert "stems" in result
        assert isinstance(result["stems"], dict)
    
    def test_file_not_found(self):
        """Test error handling for missing file."""
        analyzer = AudioStructureAnalyzer()
        
        with pytest.raises(FileNotFoundError):
            analyzer.analyze_structure("nonexistent_file.wav")


class TestFactoryFunctions:
    """Test factory functions for getting processors."""
    
    def test_get_audio_processor_default(self):
        """Test getting default (mock) audio processor."""
        processor = get_audio_processor(use_azure=False)
        assert isinstance(processor, MockAudioProcessor)
    
    def test_get_audio_processor_azure_not_implemented(self):
        """Test getting Azure processor (should raise NotImplementedError when used)."""
        from rootzengine.audio.interfaces import AzureAudioProcessor
        
        processor = get_audio_processor(use_azure=True)
        assert isinstance(processor, AzureAudioProcessor)
        
        # Should raise NotImplementedError when trying to use
        with pytest.raises(NotImplementedError):
            processor.analyze_structure("dummy.wav")