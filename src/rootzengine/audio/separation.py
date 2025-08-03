"""
Stem separation module using Demucs.

This module provides functionality to separate an audio file into its
constituent stems (e.g., bass, drums, vocals, other). It uses the
Demucs library and is designed to be integrated into the RootzEngine
analysis pipeline.
"""

import logging
import os
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

from src.rootzengine.core.config import settings
from src.rootzengine.core.exceptions import AudioProcessingError

logger = logging.getLogger(__name__)


def separate_stems(
    input_audio_path: str,
    output_dir: str,
    stems_to_separate: List[str] = ["bass", "drums"],
) -> Optional[Dict[str, str]]:
    """
    Separates stems from an audio file using Demucs.

    Args:
        input_audio_path: Absolute path to the input audio file.
        output_dir: Directory to save the separated stem files.
        stems_to_separate: A list of stems to separate (e.g., ['bass', 'drums']).

    Returns:
        A dictionary where keys are stem names and values are the paths
        to the separated stem files. Returns None if separation fails.
    """
    input_path = Path(input_audio_path)
    if not input_path.exists():
        logger.error(f"Input audio file not found: {input_audio_path}")
        raise FileNotFoundError(f"Input audio file not found: {input_audio_path}")

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    model = settings.demucs.model_name
    device = settings.demucs.device

    # Demucs command structure
    # We use --two-stems for bass/drums if that's all we need.
    # Otherwise, we use the full model and select the stems later.
    command = [
        "python3",
        "-m",
        "demucs",
        "--out",
        str(output_path),
        "--filename",
        "{stem}.{ext}",
        "-n",
        model,
        "-d",
        device,
        str(input_path),
    ]

    if set(stems_to_separate) == {"bass", "drums"}:
        command.append("--two-stems=bass") # Demucs convention for bass/not-bass

    logger.info(f"Running Demucs command: {' '.join(command)}")

    try:
        process = subprocess.run(
            command, check=True, capture_output=True, text=True, encoding="utf-8"
        )
        logger.info("Demucs processing successful.")
        logger.debug(process.stdout)

        # Verify that the expected stem files were created
        extracted_paths = {}
        for stem in stems_to_separate:
            # Assuming .wav output, which is common for high-quality separation
            stem_file = output_path / f"{stem}.wav"
            if stem_file.exists():
                extracted_paths[stem] = str(stem_file)
                logger.info(f"Found separated stem: {stem_file}")
            else:
                logger.warning(f"Expected stem file not found: {stem_file}")

        if len(extracted_paths) != len(stems_to_separate):
            raise AudioProcessingError("Demucs did not produce all expected stems.")

        return extracted_paths

    except subprocess.CalledProcessError as e:
        logger.error(f"Error during Demucs processing: {e.stderr}")
        raise AudioProcessingError(f"Demucs failed: {e.stderr}") from e
    except FileNotFoundError:
        logger.error("Demucs command not found. Is it installed and in PATH?")
        raise EnvironmentError("Demucs command not found. Is it installed and in PATH?")