"""Storage interface for unified local and cloud operations."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
import os

from rootzengine.core.config import settings
from rootzengine.storage.local import LocalStorageManager

try:
    from rootzengine.storage.azure import AzureBlobStorageManager
    AZURE_AVAILABLE = True
except ImportError:
    AzureBlobStorageManager = None
    AZURE_AVAILABLE = False


class StorageInterface(ABC):
    """Abstract interface for storage operations."""
    
    @abstractmethod
    def save_file(self, data: bytes, path: str) -> str:
        """Save binary data to storage."""
        pass
    
    @abstractmethod
    def load_file(self, path: str) -> bytes:
        """Load binary data from storage."""
        pass
    
    @abstractmethod
    def save_json(self, data: Dict[str, Any], path: str) -> str:
        """Save JSON data to storage."""
        pass
    
    @abstractmethod
    def list_files(self, directory: str, pattern: str = "*") -> List[str]:
        """List files in directory."""
        pass
    
    @abstractmethod
    def delete_file(self, path: str) -> bool:
        """Delete a file."""
        pass
    
    @abstractmethod
    def exists(self, path: str) -> bool:
        """Check if file exists."""
        pass


class LocalStorage(StorageInterface):
    """Local filesystem storage implementation."""
    
    def __init__(self, base_dir: Optional[Union[str, Path]] = None):
        self.manager = LocalStorageManager(base_dir)
        self.base_dir = self.manager.base_dir
    
    def save_file(self, data: bytes, path: str) -> str:
        """Save binary data to local filesystem."""
        full_path = self.base_dir / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(full_path, 'wb') as f:
            f.write(data)
        
        return str(full_path)
    
    def load_file(self, path: str) -> bytes:
        """Load binary data from local filesystem."""
        full_path = self.base_dir / path
        with open(full_path, 'rb') as f:
            return f.read()
    
    def save_json(self, data: Dict[str, Any], path: str) -> str:
        """Save JSON data to local filesystem."""
        self.manager.save_json(data, path)
        return str(self.base_dir / path)
    
    def list_files(self, directory: str, pattern: str = "*") -> List[str]:
        """List files in local directory."""
        full_dir = self.base_dir / directory
        if not full_dir.exists():
            return []
        
        files = list(full_dir.glob(pattern))
        return [str(f.relative_to(self.base_dir)) for f in files]
    
    def delete_file(self, path: str) -> bool:
        """Delete a local file."""
        full_path = self.base_dir / path
        if full_path.exists():
            full_path.unlink()
            return True
        return False
    
    def exists(self, path: str) -> bool:
        """Check if local file exists."""
        full_path = self.base_dir / path
        return full_path.exists()


class AzureStorage(StorageInterface):
    """Azure Blob Storage implementation."""
    
    def __init__(self, connection_string: Optional[str] = None, container_name: Optional[str] = None):
        if not AZURE_AVAILABLE:
            raise ImportError("Azure storage dependencies not available. Install with: pip install azure-storage-blob azure-identity")
        self.manager = AzureBlobStorageManager(connection_string, container_name)
    
    def save_file(self, data: bytes, path: str) -> str:
        """Save binary data to Azure Blob Storage."""
        import tempfile
        
        # Save to temp file first, then upload
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(data)
            temp_path = temp_file.name
        
        try:
            self.manager.upload_file(temp_path, path)
            return path
        finally:
            Path(temp_path).unlink()
    
    def load_file(self, path: str) -> bytes:
        """Load binary data from Azure Blob Storage."""
        import tempfile
        
        with tempfile.NamedTemporaryFile() as temp_file:
            self.manager.download_file(path, temp_file.name)
            with open(temp_file.name, 'rb') as f:
                return f.read()
    
    def save_json(self, data: Dict[str, Any], path: str) -> str:
        """Save JSON data to Azure Blob Storage."""
        import json
        json_bytes = json.dumps(data, indent=2, default=str).encode('utf-8')
        return self.save_file(json_bytes, path)
    
    def list_files(self, directory: str, pattern: str = "*") -> List[str]:
        """List files in Azure container."""
        # Azure blob storage doesn't have true directories, so we use prefix
        prefix = directory.rstrip('/') + '/' if directory else ''
        blobs = self.manager.list_blobs(prefix)
        
        # Simple pattern matching (just * wildcard support)
        if pattern != "*":
            import fnmatch
            blobs = [b for b in blobs if fnmatch.fnmatch(Path(b).name, pattern)]
        
        return blobs
    
    def delete_file(self, path: str) -> bool:
        """Delete a file from Azure Blob Storage."""
        try:
            blob_client = self.manager.container_client.get_blob_client(path)
            blob_client.delete_blob()
            return True
        except Exception:
            return False
    
    def exists(self, path: str) -> bool:
        """Check if file exists in Azure Blob Storage."""
        try:
            blob_client = self.manager.container_client.get_blob_client(path)
            blob_client.get_blob_properties()
            return True
        except Exception:
            return False


def get_storage(use_azure: bool = None) -> StorageInterface:
    """Factory function to get appropriate storage backend."""
    if use_azure is None:
        use_azure = bool(AZURE_AVAILABLE and settings.azure and settings.azure.connection_string)
    
    if use_azure and AZURE_AVAILABLE:
        return AzureStorage()
    else:
        return LocalStorage()


class StorageManager:
    """High-level storage manager with automatic backend selection."""
    
    def __init__(self, use_azure: bool = None):
        self.storage = get_storage(use_azure)
        self.use_azure = isinstance(self.storage, AzureStorage)
    
    def save_analysis_result(self, audio_filename: str, analysis_data: Dict[str, Any]) -> str:
        """Save audio analysis result."""
        base_name = Path(audio_filename).stem
        json_path = f"analysis/{base_name}_analysis.json"
        return self.storage.save_json(analysis_data, json_path)
    
    def save_audio_file(self, audio_data: bytes, filename: str) -> str:
        """Save uploaded audio file."""
        audio_path = f"audio/raw/{filename}"
        return self.storage.save_file(audio_data, audio_path)
    
    def save_stem_files(self, stems: Dict[str, bytes], base_filename: str) -> Dict[str, str]:
        """Save separated stem files."""
        base_name = Path(base_filename).stem
        stem_paths = {}
        
        for stem_name, stem_data in stems.items():
            stem_path = f"audio/stems/{base_name}/{stem_name}.wav"
            saved_path = self.storage.save_file(stem_data, stem_path)
            stem_paths[stem_name] = saved_path
        
        return stem_paths
    
    def list_audio_files(self) -> List[str]:
        """List all audio files in storage."""
        return self.storage.list_files("audio/raw", "*.wav") + \
               self.storage.list_files("audio/raw", "*.mp3") + \
               self.storage.list_files("audio/raw", "*.flac")
    
    def list_analysis_results(self) -> List[str]:
        """List all analysis result files."""
        return self.storage.list_files("analysis", "*_analysis.json")
    
    def get_analysis_result(self, audio_filename: str) -> Optional[Dict[str, Any]]:
        """Get analysis result for an audio file."""
        base_name = Path(audio_filename).stem
        json_path = f"analysis/{base_name}_analysis.json"
        
        if self.storage.exists(json_path):
            import json
            json_data = self.storage.load_file(json_path)
            return json.loads(json_data.decode('utf-8'))
        
        return None