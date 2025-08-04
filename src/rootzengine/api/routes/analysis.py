"""API routes for audio analysis functionality."""

import json
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Dict, List, Optional

from fastapi import APIRouter, File, Form, UploadFile, status
from fastapi.responses import JSONResponse

from rootzengine.audio.analysis import AudioStructureAnalyzer
from rootzengine.audio.separation import DemucsWrapper
from rootzengine.core.config import settings
from rootzengine.core.exceptions import AudioProcessingError
from rootzengine.storage.interface import StorageManager

router = APIRouter()


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
    # Read audio data once
    audio_data = await audio.read()
    
    # Create a temporary file for analysis
    with NamedTemporaryFile(suffix=f".{audio.filename.split('.')[-1]}", delete=False) as temp_file:
        temp_file.write(audio_data)
        temp_path = Path(temp_file.name)
    
    try:
        # Initialize storage and analyzer
        storage = StorageManager()
        analyzer = AudioStructureAnalyzer()
        
        # Save uploaded file to storage
        storage.save_audio_file(audio_data, audio.filename)
        
        # Analyze the file
        result = analyzer.analyze_structure(str(temp_path), perform_separation=False)
        
        # Save analysis result
        storage.save_analysis_result(audio.filename, result)
        
        # Add metadata to result
        result["storage_info"] = {
            "filename": audio.filename,
            "storage_backend": "azure" if storage.use_azure else "local",
            "analysis_saved": True
        }
        
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


@router.get("/files")
async def list_audio_files() -> JSONResponse:
    """List all audio files in storage."""
    try:
        storage = StorageManager()
        audio_files = storage.list_audio_files()
        
        return JSONResponse(
            content={
                "files": audio_files,
                "count": len(audio_files),
                "storage_backend": "azure" if storage.use_azure else "local"
            },
            status_code=status.HTTP_200_OK,
        )
    except Exception as e:
        return JSONResponse(
            content={"error": str(e)},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.get("/results")
async def list_analysis_results() -> JSONResponse:
    """List all analysis results in storage."""
    try:
        storage = StorageManager()
        results = storage.list_analysis_results()
        
        return JSONResponse(
            content={
                "results": results,
                "count": len(results),
                "storage_backend": "azure" if storage.use_azure else "local"
            },
            status_code=status.HTTP_200_OK,
        )
    except Exception as e:
        return JSONResponse(
            content={"error": str(e)},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.get("/results/{filename}")
async def get_analysis_result(filename: str) -> JSONResponse:
    """Get analysis result for a specific file."""
    try:
        storage = StorageManager()
        result = storage.get_analysis_result(filename)
        
        if result is None:
            return JSONResponse(
                content={"error": f"No analysis result found for {filename}"},
                status_code=status.HTTP_404_NOT_FOUND,
            )
        
        return JSONResponse(
            content={
                "filename": filename,
                "result": result,
                "storage_backend": "azure" if storage.use_azure else "local"
            },
            status_code=status.HTTP_200_OK,
        )
    except Exception as e:
        return JSONResponse(
            content={"error": str(e)},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


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
        
        # Process file - create output directory
        output_dir = settings.storage.processed_dir / "stems" / audio.filename.split('.')[0]
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Separate stems
        stem_paths = demucs.separate_stems(str(temp_path), str(output_dir))
        
        # Convert to dictionary format expected by response
        result = {}
        for stem_path in stem_paths:
            stem_name = Path(stem_path).stem
            result[stem_name] = str(Path(stem_path).relative_to(settings.storage.project_root))
        
        relative_paths = result
        
        return JSONResponse(
            content={"stems": relative_paths},
            status_code=status.HTTP_200_OK,
        )
        
    except Exception as e:
        return JSONResponse(
            content={"error": str(e)},
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    finally:
        # Clean up temporary file
        if temp_path.exists():
            temp_path.unlink()


@router.get("/files")
async def list_audio_files() -> JSONResponse:
    """List all audio files in storage."""
    try:
        storage = StorageManager()
        audio_files = storage.list_audio_files()
        
        return JSONResponse(
            content={
                "files": audio_files,
                "count": len(audio_files),
                "storage_backend": "azure" if storage.use_azure else "local"
            },
            status_code=status.HTTP_200_OK,
        )
    except Exception as e:
        return JSONResponse(
            content={"error": str(e)},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.get("/results")
async def list_analysis_results() -> JSONResponse:
    """List all analysis results in storage."""
    try:
        storage = StorageManager()
        results = storage.list_analysis_results()
        
        return JSONResponse(
            content={
                "results": results,
                "count": len(results),
                "storage_backend": "azure" if storage.use_azure else "local"
            },
            status_code=status.HTTP_200_OK,
        )
    except Exception as e:
        return JSONResponse(
            content={"error": str(e)},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.get("/results/{filename}")
async def get_analysis_result(filename: str) -> JSONResponse:
    """Get analysis result for a specific file."""
    try:
        storage = StorageManager()
        result = storage.get_analysis_result(filename)
        
        if result is None:
            return JSONResponse(
                content={"error": f"No analysis result found for {filename}"},
                status_code=status.HTTP_404_NOT_FOUND,
            )
        
        return JSONResponse(
            content={
                "filename": filename,
                "result": result,
                "storage_backend": "azure" if storage.use_azure else "local"
            },
            status_code=status.HTTP_200_OK,
        )
    except Exception as e:
        return JSONResponse(
            content={"error": str(e)},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
