"""API routes for MIDI functionality."""

from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Dict, List, Optional

from fastapi import APIRouter, File, Form, UploadFile, status
from fastapi.responses import JSONResponse, FileResponse

from rootzengine.audio.analysis import AudioStructureAnalyzer
from rootzengine.core.config import settings
from rootzengine.core.exceptions import AudioProcessingError

router = APIRouter()


@router.post("/convert")
async def convert_to_midi(
    audio: UploadFile = File(...),
    analyze: bool = Form(True),
) -> JSONResponse:
    """Convert audio to MIDI with optional structure analysis.
    
    Args:
        audio: Audio file to convert
        analyze: Whether to perform structure analysis
    
    Returns:
        MIDI file response
    """
    # Create a temporary file for the uploaded audio
    with NamedTemporaryFile(suffix=f".{audio.filename.split('.')[-1]}", delete=False) as temp_file:
        # Write uploaded file to disk
        temp_file.write(await audio.read())
        temp_path = Path(temp_file.name)
    
    try:
        # Perform analysis if requested
        structure_data = None
        if analyze:
            analyzer = AudioStructureAnalyzer()
            structure_data = analyzer.analyze_structure(str(temp_path), perform_separation=False)
        
        # Mock MIDI conversion - return analysis data instead
        result = {
            "message": "MIDI conversion ready - requires PC environment",
            "analysis": structure_data,
            "filename": f"{audio.filename.split('.')[0]}.mid"
        }
        
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


@router.post("/generate")
async def generate_pattern(
    pattern_type: str = Form("one_drop"),
    key: str = Form("C"),
    mode: str = Form("major"),
    measures: int = Form(4),
    bass_style: str = Form("simple"),
    skank_style: str = Form("traditional"),
    tempo: float = Form(80.0),
) -> JSONResponse:
    """Generate a reggae MIDI pattern.
    
    Args:
        pattern_type: Type of riddim pattern
        key: Root key
        mode: Mode (major or minor)
        measures: Number of measures
        bass_style: Bass style
        skank_style: Skank style
        tempo: Tempo in BPM
    
    Returns:
        Generated MIDI file
    """
    try:
        # Mock pattern generation - return pattern specification
        filename = f"{pattern_type}_{key}{mode}_{measures}bars.mid"
        
        result = {
            "message": "MIDI pattern generation ready - requires PC environment",
            "pattern_spec": {
                "pattern_type": pattern_type,
                "key": key,
                "mode": mode,
                "measures": measures,
                "bass_style": bass_style,
                "skank_style": skank_style,
                "tempo": tempo
            },
            "filename": filename
        }
        
        return JSONResponse(
            content=result,
            status_code=status.HTTP_200_OK,
        )
        
    except Exception as e:
        return JSONResponse(
            content={"error": str(e)},
            status_code=status.HTTP_400_BAD_REQUEST,
        )
