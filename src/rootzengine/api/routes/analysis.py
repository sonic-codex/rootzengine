"""API routes for audio analysis functionality."""

import json
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Dict, List, Optional

from fastapi import APIRouter, File, Form, UploadFile, status
from fastapi.responses import JSONResponse

from src.rootzengine.audio import AudioStructureAnalyzer, DemucsWrapper
from src.rootzengine.core.config import settings
from src.rootzengine.core.exceptions import AudioProcessingError, StemSeparationError

router = APIRouter(prefix="/analysis", tags=["Analysis"])


@router.post("/structure")
async def analyze_structure(
    audio: UploadFile = File(...),
    sample_rate: Optional[int] = Form(None),
) -> JSONResponse:
    """Analyze the structure of an audio file.
    
    Args:
        audio: Audio file to analyze
        sample_rate: Optional sample rate to use for analysis
    
    Returns:
        JSON response with analysis results
    """
    # Create a temporary file for the uploaded audio
    with NamedTemporaryFile(suffix=f".{audio.filename.split('.')[-1]}", delete=False) as temp_file:
        # Write uploaded file to disk
        temp_file.write(await audio.read())
        temp_path = Path(temp_file.name)
    
    try:
        # Initialize analyzer with optional parameters
        analyzer = AudioStructureAnalyzer(
            sample_rate=sample_rate or settings.audio.sample_rate,
        )
        
        # Analyze the file
        result = analyzer.analyze_structure(temp_path)
        
        # Return the result
        return JSONResponse(
            content=result,
            status_code=status.HTTP_200_OK,
        )
        
    except AudioProcessingError as e:
        return JSONResponse(
            content={"error": str(e)},
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    finally:
        # Clean up temporary file
        if temp_path.exists():
            temp_path.unlink()


@router.post("/stems")
async def separate_stems(
    audio: UploadFile = File(...),
    stems: List[str] = Form(["bass", "drums"]),
) -> JSONResponse:
    """Separate audio into stems using Demucs.
    
    Args:
        audio: Audio file to separate
        stems: List of stems to extract
    
    Returns:
        JSON response with stem paths
    """
    # Create a temporary file for the uploaded audio
    with NamedTemporaryFile(suffix=f".{audio.filename.split('.')[-1]}", delete=False) as temp_file:
        # Write uploaded file to disk
        temp_file.write(await audio.read())
        temp_path = Path(temp_file.name)
    
    try:
        # Initialize Demucs wrapper
        demucs = DemucsWrapper()
        
        # Process file
        output_dir = settings.storage.processed_dir / "stems" / audio.filename
        output_dir.mkdir(parents=True, exist_ok=True)
        
        result = demucs.separate_stems(
            temp_path,
            output_directory=output_dir,
            stems=stems,
        )
        
        # Convert paths to relative paths for the response
        relative_paths = {k: str(v.relative_to(settings.storage.project_root)) for k, v in result.items()}
        
        return JSONResponse(
            content={"stems": relative_paths},
            status_code=status.HTTP_200_OK,
        )
        
    except StemSeparationError as e:
        return JSONResponse(
            content={"error": str(e)},
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    finally:
        # Clean up temporary file
        if temp_path.exists():
            temp_path.unlink()
