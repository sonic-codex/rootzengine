"""Stem separation module using Demucs."""

import logging
import os
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Union

import numpy as np
from src.rootzengine.core.config import settings
from src.rootzengine.core.exceptions import StemSeparationError

logger = logging.getLogger(__name__)


class DemucsWrapper:
    """Wrapper for Demucs audio source separation."""
    
    def __init__(self, model_name: Optional[str] = None, device: Optional[str] = None):
        """Initialize the Demucs wrapper.
        
        Args:
            model_name: The Demucs model name to use
            device: The device to run Demucs on ('cpu' or 'cuda')
        """
        self.model_name = model_name or settings.demucs.model_name
        self.device = device or settings.demucs.device
    
    def separate_stems(
        self, 
        input_audio_path: Union[str, Path], 
        output_directory: Optional[Union[str, Path]] = None,
        stems: Optional[List[str]] = None
    ) -> Dict[str, Path]:
        """Separates an audio file into stems.
        
        Args:
            input_audio_path: Path to the input audio file
            output_directory: Directory to save the separated stems
            stems: Specific stems to extract (e.g., ["bass", "drums"])
            
        Returns:
            Dictionary mapping stem names to file paths
            
        Raises:
            StemSeparationError: If stem separation fails
        """
        input_audio_path = Path(input_audio_path)
        
        if not input_audio_path.exists():
            raise StemSeparationError(f"Input file not found: {input_audio_path}")
        
        # Set up output directory
        if output_directory is None:
            output_directory = settings.storage.processed_dir / "stems" / input_audio_path.stem
        else:
            output_directory = Path(output_directory)
        
        os.makedirs(output_directory, exist_ok=True)
        logger.info(f"Stem output directory: {output_directory}")
        
        # Set up stems to extract
        stems_arg = []
        target_stems = stems or ["bass", "drums"]
        
        if stems:
            stems_arg = ["--stems"] + stems
        
        # Build Demucs command
        command = [
            "python", "-m", "demucs",
            "--out", str(output_directory),
            "--filename", "{stem}.{ext}",  # Simple naming
            "-n", self.model_name,
            "--device", self.device
        ]
        
        # Add stems argument if specified
        if stems_arg:
            command.extend(stems_arg)
        
        # Add input file path
        command.append(str(input_audio_path))
        
        logger.info(f"Running Demucs command: {' '.join(command)}")
        
        try:
            # Run Demucs
            process = subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True
            )
            
            logger.info("Demucs processing successful")
            logger.debug(process.stdout)
            
            # Check for expected output files
            result_stems = {}
            for stem in target_stems:
                stem_path = output_directory / f"{stem}.wav"
                if stem_path.exists():
                    result_stems[stem] = stem_path
                    logger.info(f"Found {stem} stem at {stem_path}")
                else:
                    logger.warning(f"Expected {stem} stem not found at {stem_path}")
            
            if not all(stem in result_stems for stem in target_stems):
                missing = [s for s in target_stems if s not in result_stems]
                logger.error(f"Missing stems: {missing}")
                raise StemSeparationError(f"Failed to extract all requested stems: {missing}")
            
            return result_stems
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Demucs process failed: {e}")
            logger.error(f"stderr: {e.stderr}")
            raise StemSeparationError(f"Demucs processing failed: {e.stderr}")
        
        except Exception as e:
            logger.error(f"Error in stem separation: {str(e)}")
            raise StemSeparationError(f"Stem separation failed: {str(e)}")
    
    @staticmethod
    def load_audio_stems(
        stem_paths: Dict[str, Union[str, Path]]
    ) -> Dict[str, np.ndarray]:
        """Load audio stems into memory as numpy arrays.
        
        Args:
            stem_paths: Dictionary of stem names to file paths
            
        Returns:
            Dictionary of stem names to numpy arrays
        """
        import librosa
        
        stem_audio = {}
        for stem_name, stem_path in stem_paths.items():
            try:
                audio, _ = librosa.load(str(stem_path), sr=settings.audio.sample_rate)
                stem_audio[stem_name] = audio
            except Exception as e:
                logger.error(f"Error loading {stem_name} stem: {str(e)}")
                raise StemSeparationError(f"Failed to load {stem_name} stem: {str(e)}")
        
        return stem_audio
