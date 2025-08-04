"""Tests for storage system."""

import pytest
import tempfile
import json
from pathlib import Path

from rootzengine.storage.interface import LocalStorage, StorageManager, get_storage


class TestLocalStorage:
    """Test local storage implementation."""
    
    def test_save_and_load_file(self, tmp_path):
        """Test saving and loading binary files."""
        storage = LocalStorage(tmp_path)
        
        test_data = b"Hello, World!"
        saved_path = storage.save_file(test_data, "test/file.bin")
        
        assert Path(saved_path).exists()
        loaded_data = storage.load_file("test/file.bin")
        assert loaded_data == test_data
    
    def test_save_and_load_json(self, tmp_path):
        """Test saving and loading JSON files."""
        storage = LocalStorage(tmp_path)
        
        test_data = {"key": "value", "number": 42}
        saved_path = storage.save_json(test_data, "test/data.json")
        
        assert Path(saved_path).exists()
        
        # Load back as JSON
        with open(saved_path, 'r') as f:
            loaded_data = json.load(f)
        
        assert loaded_data == test_data
    
    def test_list_files(self, tmp_path):
        """Test listing files."""
        storage = LocalStorage(tmp_path)
        
        # Create some test files
        storage.save_file(b"data1", "test/file1.txt")
        storage.save_file(b"data2", "test/file2.txt")
        storage.save_file(b"data3", "test/file3.log")
        
        # List all files
        all_files = storage.list_files("test")
        assert len(all_files) == 3
        
        # List with pattern
        txt_files = storage.list_files("test", "*.txt")
        assert len(txt_files) == 2
        assert all("file" in f and f.endswith(".txt") for f in txt_files)
    
    def test_delete_file(self, tmp_path):
        """Test deleting files."""
        storage = LocalStorage(tmp_path)
        
        storage.save_file(b"test data", "test/deleteme.txt")
        assert storage.exists("test/deleteme.txt")
        
        success = storage.delete_file("test/deleteme.txt")
        assert success
        assert not storage.exists("test/deleteme.txt")
        
        # Try to delete non-existent file
        success = storage.delete_file("test/nonexistent.txt")
        assert not success
    
    def test_exists(self, tmp_path):
        """Test file existence check."""
        storage = LocalStorage(tmp_path)
        
        assert not storage.exists("test/nonexistent.txt")
        
        storage.save_file(b"test data", "test/exists.txt")
        assert storage.exists("test/exists.txt")


class TestStorageManager:
    """Test high-level storage manager."""
    
    def test_initialization(self, tmp_path):
        """Test storage manager initialization."""
        # Force local storage for testing
        manager = StorageManager(use_azure=False)
        assert not manager.use_azure
        assert isinstance(manager.storage, LocalStorage)
    
    def test_save_analysis_result(self, tmp_path):
        """Test saving analysis results."""
        manager = StorageManager(use_azure=False)
        # Override the storage with test directory
        manager.storage = LocalStorage(tmp_path)
        
        analysis_data = {
            "tempo": {"bpm": 85.0, "confidence": 0.9},
            "key": {"key": "A", "mode": "minor"},
            "sections": [{"start": 0, "end": 30, "label": "intro"}]
        }
        
        saved_path = manager.save_analysis_result("test_song.wav", analysis_data)
        assert "analysis" in saved_path
        assert "test_song_analysis.json" in saved_path
        
        # Verify we can retrieve it
        retrieved = manager.get_analysis_result("test_song.wav")
        assert retrieved == analysis_data
    
    def test_save_audio_file(self, tmp_path):
        """Test saving audio files."""
        manager = StorageManager(use_azure=False)
        manager.storage = LocalStorage(tmp_path)
        
        audio_data = b"fake audio data"
        saved_path = manager.save_audio_file(audio_data, "test_song.wav")
        
        assert "audio/raw" in saved_path
        assert manager.storage.exists("audio/raw/test_song.wav")
    
    def test_save_stem_files(self, tmp_path):
        """Test saving stem files."""
        manager = StorageManager(use_azure=False)
        manager.storage = LocalStorage(tmp_path)
        
        stems = {
            "bass": b"fake bass data",
            "drums": b"fake drums data",
            "vocals": b"fake vocals data"
        }
        
        stem_paths = manager.save_stem_files(stems, "test_song.wav")
        
        assert len(stem_paths) == 3
        assert all("stems/test_song" in path for path in stem_paths.values())
        
        # Verify files exist
        for stem_name in stems.keys():
            assert manager.storage.exists(f"audio/stems/test_song/{stem_name}.wav")
    
    def test_list_operations(self, tmp_path):
        """Test listing operations."""
        manager = StorageManager(use_azure=False)
        manager.storage = LocalStorage(tmp_path)
        
        # Add some test files
        manager.save_audio_file(b"audio1", "song1.wav")
        manager.save_audio_file(b"audio2", "song2.mp3")
        manager.save_analysis_result("song1.wav", {"test": "data"})
        
        # Test listing
        audio_files = manager.list_audio_files()
        assert len(audio_files) >= 2
        
        analysis_files = manager.list_analysis_results()
        assert len(analysis_files) >= 1
        assert "song1_analysis.json" in str(analysis_files[0])


class TestStorageFactory:
    """Test storage factory function."""
    
    def test_get_storage_local(self):
        """Test getting local storage."""
        storage = get_storage(use_azure=False)
        assert isinstance(storage, LocalStorage)
    
    def test_get_storage_auto_detect(self):
        """Test auto-detection of storage backend."""
        # Without Azure config, should default to local
        storage = get_storage()
        assert isinstance(storage, LocalStorage)