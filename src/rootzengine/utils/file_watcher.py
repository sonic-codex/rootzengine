"""File watcher module for processing audio files."""

import os
import time
import logging
from typing import Callable, Dict, List, Optional
from watchdog.observers import Observer
from watchdog.events import (
    FileSystemEventHandler,
    FileCreatedEvent,
    FileModifiedEvent,
)

from rootzengine.core.config import settings

logger = logging.getLogger(__name__)


class AudioFileHandler(FileSystemEventHandler):
    """Handler for audio file events."""
    
    def __init__(
        self,
        extensions: List[str],
        on_created: Optional[Callable[[str], None]] = None,
        on_modified: Optional[Callable[[str], None]] = None
    ):
        """
        Initialize the audio file handler.
        
        Args:
            extensions: List of audio file extensions to monitor
            on_created: Callback for file creation events
            on_modified: Callback for file modification events
        """
        self.extensions = [ext.lower() for ext in extensions]
        self.on_created_callback = on_created
        self.on_modified_callback = on_modified
    
    def on_created(self, event):
        """Handle file creation events."""
        if not isinstance(event, FileCreatedEvent):
            return
        
        file_path = str(event.src_path)
        if not self._is_audio_file(file_path):
            return
            
        logger.info(f"New audio file detected: {file_path}")
        if self.on_created_callback:
            self.on_created_callback(file_path)
    
    def on_modified(self, event):
        """Handle file modification events."""
        if not isinstance(event, FileModifiedEvent):
            return
            
        file_path = str(event.src_path)
        if not self._is_audio_file(file_path):
            return
            
        logger.info(f"Audio file modified: {file_path}")
        if self.on_modified_callback:
            self.on_modified_callback(file_path)
    
    def _is_audio_file(self, file_path: str) -> bool:
        """Check if file has a monitored audio extension."""
        ext = os.path.splitext(file_path)[1].lower()
        return ext in self.extensions


class FileWatcher:
    """Watches directories for new or modified audio files."""
    
    def __init__(
        self,
        directories: List[str],
        extensions: List[str] = ['.mp3', '.wav', '.flac', '.ogg', '.m4a'],
    ):
        """
        Initialize the file watcher.
        
        Args:
            directories: List of directories to monitor
            extensions: List of file extensions to monitor
        """
        self.directories = directories
        self.extensions = extensions
        self.observer = Observer()
        self.handlers: Dict[str, AudioFileHandler] = {}
        
    def add_handler(
        self,
        directory: str,
        on_created: Optional[Callable[[str], None]] = None,
        on_modified: Optional[Callable[[str], None]] = None
    ) -> None:
        """
        Add a handler for a specific directory.
        
        Args:
            directory: Directory to monitor
            on_created: Callback for file creation events
            on_modified: Callback for file modification events
        """
        if not os.path.exists(directory):
            logger.warning(f"Directory does not exist: {directory}")
            os.makedirs(directory, exist_ok=True)
            logger.info(f"Created directory: {directory}")
            
        handler = AudioFileHandler(
            extensions=self.extensions,
            on_created=on_created,
            on_modified=on_modified
        )
        
        self.observer.schedule(handler, directory, recursive=True)
        self.handlers[directory] = handler
        logger.info(f"Added handler for directory: {directory}")
        
    def start(self) -> None:
        """Start watching directories."""
        self.observer.start()
        logger.info("File watcher started")
        
    def stop(self) -> None:
        """Stop watching directories."""
        self.observer.stop()
        self.observer.join()
        logger.info("File watcher stopped")
        
    def run_until_keyboard_interrupt(self) -> None:
        """Run the watcher until keyboard interrupt."""
        try:
            self.start()
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()
        finally:
            logger.info("File watcher terminated")


def process_new_audio_file(file_path: str) -> None:
    """
    Process a new audio file.
    
    Args:
        file_path: Path to the audio file
    """
    from rootzengine.audio.analysis import AudioStructureAnalyzer
    from rootzengine.storage.interface import StorageManager
    
    logger.info(f"Processing new audio file: {file_path}")
    
    # Initialize analyzer and storage
    analyzer = AudioStructureAnalyzer()
    storage = StorageManager()
    
    try:
        # Analyze the file
        results = analyzer.analyze_structure(file_path, perform_separation=False)
        
        # Get filename from path
        filename = os.path.basename(file_path)
        
        # Save to storage
        storage.save_analysis_result(filename, results)
        
        logger.info(f"Analysis results saved for {filename}")
        
    except Exception as e:
        logger.error(f"Failed to process {file_path}: {e}")
