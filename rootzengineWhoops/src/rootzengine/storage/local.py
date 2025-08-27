"""Local filesystem storage backend"""

from pathlib import Path
from typing import Optional, BinaryIO
import shutil

class LocalStorage:
    """Local filesystem storage implementation"""
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def save_file(self, file_data: BinaryIO, filename: str) -> str:
        """Save file to local storage"""
        file_path = self.base_path / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'wb') as f:
            shutil.copyfileobj(file_data, f)
        
        return str(file_path)
    
    def load_file(self, filename: str) -> Optional[BinaryIO]:
        """Load file from local storage"""
        file_path = self.base_path / filename
        if file_path.exists():
            return open(file_path, 'rb')
        return None
    
    def delete_file(self, filename: str) -> bool:
        """Delete file from local storage"""
        file_path = self.base_path / filename
        if file_path.exists():
            file_path.unlink()
            return True
        return False
