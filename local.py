"""Local file storage management."""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Union

from src.rootzengine.core.config import settings
from src.rootzengine.core.exceptions import StorageError

logger = logging.getLogger(__name__)


class LocalStorageManager:
    """Manages file operations on the local filesystem."""

    def __init__(self, base_dir: Union[str, Path] = None):
        """Initialize the local storage manager.

        Args:
            base_dir: The base directory for all operations. Defaults to project root.
        """
        self.base_dir = Path(base_dir) if base_dir else settings.storage.project_root
        logger.info(f"LocalStorageManager initialized with base directory: {self.base_dir}")

    def save_json(self, data: Dict[str, Any], file_path: Union[str, Path]):
        """Saves a dictionary to a JSON file.

        Args:
            data: The dictionary to save.
            file_path: The relative path to the output file.
        """
        full_path = self.base_dir / file_path
        try:
            full_path.parent.mkdir(parents=True, exist_ok=True)
            with open(full_path, "w") as f:
                json.dump(data, f, indent=2, default=str)
            logger.info(f"Successfully saved JSON to {full_path}")
        except Exception as e:
            logger.error(f"Failed to save JSON to {full_path}: {e}")
            raise StorageError(f"Could not save JSON file: {e}") from e

    def list_files(self, directory: Union[str, Path], pattern: str = "*") -> List[Path]:
        """Lists files in a directory.

        Args:
            directory: The directory to search.
            pattern: The glob pattern to match files.
        """
        full_dir = Path(directory)
        if not full_dir.is_dir():
            logger.warning(f"Directory not found for listing: {full_dir}")
            return []
        return list(full_dir.glob(pattern))