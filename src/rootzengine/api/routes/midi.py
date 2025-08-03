"""API routes for MIDI functionality."""

from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Dict, List, Optional

from fastapi import APIRouter, File, Form, UploadFile, status
from fastapi.responses import JSONResponse, FileResponse

from src.rootzengine.audio import AudioStructureAnalyzer
from src.rootzengine.core.config import settings
from src.rootzengine.core.exceptions import AudioProcessingError, MIDIConversionError
from src.rootzengine.midi import AudioToMIDIConverter, MIDIPatternGenerator

router = APIRouter(prefix="/midi", tags=["MIDI"])


@router.post("/convert")
async def convert_to_midi(
    audio: UploadFile = File(...),
    analyze: bool = Form(True),
) -> FileResponse:
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
        # Initialize converter
        converter = AudioToMIDIConverter()
        
        # Perform analysis if requested
        structure_data = None
        if analyze:
            analyzer = AudioStructureAnalyzer()
            structure_data = analyzer.analyze_structure(temp_path)
        
        # Output path for the MIDI file
        output_path = settings.storage.midi_dir / f"{audio.filename.split('.')[0]}.mid"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert to MIDI
        midi_path = converter.convert_to_midi(
            temp_path,
            output_path=output_path,
            structure_data=structure_data,
        )
        
        # Return the MIDI file
        return FileResponse(
            midi_path,
            filename=midi_path.name,
            media_type="audio/midi",
        )
        
    except (AudioProcessingError, MIDIConversionError) as e:
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
) -> FileResponse:
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
        # Initialize generator
        generator = MIDIPatternGenerator(tempo=tempo)
        
        # Create output path
        filename = f"{pattern_type}_{key}{mode}_{measures}bars.mid"
        output_path = settings.storage.midi_dir / "patterns" / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Generate pattern
        midi_path = generator.generate_pattern(
            output_path,
            pattern_type=pattern_type,
            key=key,
            mode=mode,
            measures=measures,
            bass_style=bass_style,
            skank_style=skank_style,
        )
        
        # Return the MIDI file
        return FileResponse(
            midi_path,
            filename=midi_path.name,
            media_type="audio/midi",
        )
        
    except MIDIConversionError as e:
        return JSONResponse(
            content={"error": str(e)},
            status_code=status.HTTP_400_BAD_REQUEST,
        )
