"""Command-line interface for RootzEngine."""

import logging
import os
from pathlib import Path
from typing import List, Optional

import typer
import uvicorn

from src.rootzengine.audio import AudioStructureAnalyzer, DemucsWrapper
from src.rootzengine.core.config import load_settings, settings
from src.rootzengine.midi import AudioToMIDIConverter, MIDIPatternGenerator

# Set up logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("rootzengine")

# Create Typer app
app = typer.Typer(help="RootzEngine: AI-Powered Reggae Metadata + Groove Generation Toolkit")

# Create sub-commands
analyze_app = typer.Typer(help="Audio analysis commands")
app.add_typer(analyze_app, name="analyze")

midi_app = typer.Typer(help="MIDI generation commands")
app.add_typer(midi_app, name="midi")

batch_app = typer.Typer(help="Batch processing commands")
app.add_typer(batch_app, name="batch")


@app.callback()
def main(
    config: Optional[Path] = typer.Option(
        None, "--config", "-c", help="Path to config file"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging"
    ),
):
    """RootzEngine: AI-Powered Reggae Metadata + Groove Generation Toolkit."""
    # Load configuration
    if config:
        load_settings(config)
    
    # Set log level
    if verbose:
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")
    
    # Ensure data directories exist
    os.makedirs(settings.storage.raw_dir, exist_ok=True)
    os.makedirs(settings.storage.processed_dir, exist_ok=True)
    os.makedirs(settings.storage.midi_dir, exist_ok=True)
    os.makedirs(settings.storage.models_dir, exist_ok=True)


@analyze_app.command("audio")
def analyze_audio(
    input_path: Path = typer.Argument(..., help="Path to audio file to analyze"),
    output_dir: Optional[Path] = typer.Option(
        None, "--output-dir", "-o", help="Output directory for analysis results"
    ),
):
    """Analyze the structure of an audio file."""
    logger.info(f"Analyzing audio file: {input_path}")
    
    # Create analyzer
    analyzer = AudioStructureAnalyzer()
    
    # Run analysis
    result = analyzer.analyze_structure(input_path)
    
    # Determine output path
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        output_path = output_dir / f"{input_path.stem}_analysis.json"
    else:
        output_path = settings.storage.processed_dir / f"{input_path.stem}_analysis.json"
        os.makedirs(output_path.parent, exist_ok=True)
    
    # Save results
    import json
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)
    
    logger.info(f"Analysis saved to: {output_path}")
    
    return result


@analyze_app.command("stems")
def separate_stems(
    input_path: Path = typer.Argument(..., help="Path to audio file to separate"),
    output_dir: Optional[Path] = typer.Option(
        None, "--output-dir", "-o", help="Output directory for stems"
    ),
    stems: List[str] = typer.Option(
        ["bass", "drums"], "--stem", "-s", help="Stems to extract"
    ),
):
    """Separate audio into stems using Demucs."""
    logger.info(f"Separating stems for: {input_path}")
    
    # Create Demucs wrapper
    demucs = DemucsWrapper()
    
    # Run separation
    result = demucs.separate_stems(
        input_path,
        output_directory=output_dir,
        stems=stems
    )
    
    logger.info(f"Stems extracted: {', '.join(result.keys())}")
    
    return result


@midi_app.command("convert")
def convert_to_midi(
    input_path: Path = typer.Argument(..., help="Path to audio file to convert"),
    output_path: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Output MIDI file path"
    ),
    analyze: bool = typer.Option(
        True, "--analyze/--no-analyze", help="Perform structure analysis first"
    ),
):
    """Convert audio to MIDI with optional structure-awareness."""
    logger.info(f"Converting {input_path} to MIDI")
    
    # Create converter
    converter = AudioToMIDIConverter()
    
    # Perform analysis if requested
    structure_data = None
    if analyze:
        logger.info("Performing structure analysis...")
        analyzer = AudioStructureAnalyzer()
        structure_data = analyzer.analyze_structure(input_path)
    
    # Convert to MIDI
    midi_path = converter.convert_to_midi(
        input_path,
        output_path=output_path,
        structure_data=structure_data
    )
    
    logger.info(f"MIDI saved to: {midi_path}")
    
    return midi_path


@midi_app.command("generate")
def generate_pattern(
    output_path: Path = typer.Argument(..., help="Output MIDI file path"),
    pattern_type: str = typer.Option(
        "one_drop", "--pattern", "-p", 
        help="Riddim pattern type (one_drop, steppers, rockers)"
    ),
    key: str = typer.Option("C", "--key", "-k", help="Root key"),
    mode: str = typer.Option(
        "major", "--mode", "-m", help="Mode (major or minor)"
    ),
    measures: int = typer.Option(4, "--measures", "-n", help="Number of measures"),
    bass_style: str = typer.Option(
        "simple", "--bass", "-b", 
        help="Bass style (simple, walking, complex)"
    ),
    skank_style: str = typer.Option(
        "traditional", "--skank", "-s",
        help="Skank style (traditional, bubble, offbeat)"
    ),
):
    """Generate a reggae MIDI pattern."""
    logger.info(f"Generating {pattern_type} pattern in {key} {mode}")
    
    # Create generator
    generator = MIDIPatternGenerator(tempo=80.0)
    
    # Generate pattern
    midi_path = generator.generate_pattern(
        output_path,
        pattern_type=pattern_type,
        key=key,
        mode=mode,
        measures=measures,
        bass_style=bass_style,
        skank_style=skank_style
    )
    
    logger.info(f"Pattern saved to: {midi_path}")
    
    return midi_path


@batch_app.command("process")
def batch_process(
    input_dir: Path = typer.Argument(..., help="Directory with audio files to process"),
    output_dir: Optional[Path] = typer.Option(
        None, "--output-dir", "-o", help="Output directory"
    ),
    workers: int = typer.Option(1, "--workers", "-w", help="Number of worker processes"),
    cloud: bool = typer.Option(False, "--cloud", help="Use cloud storage")
):
    """Process multiple audio files in batch mode."""
    logger.info(f"Batch processing audio in: {input_dir}")
    logger.info(f"Using {workers} worker{'s' if workers > 1 else ''}")
    
    # Implementation details would depend on specific batch processing approach
    # This is a placeholder
    
    typer.echo(f"Batch processing with {workers} workers")
    typer.echo(f"Using {'cloud' if cloud else 'local'} storage")
    
    # In a real implementation, this would:
    # 1. Scan the input directory
    # 2. Create a work queue
    # 3. Start worker processes
    # 4. Process files and collect results
    
    typer.echo("Batch processing not yet implemented")


@app.command("serve")
def serve_api(
    host: str = typer.Option("127.0.0.1", "--host", "-h", help="API host"),
    port: int = typer.Option(8000, "--port", "-p", help="API port"),
    reload: bool = typer.Option(False, "--reload", help="Enable auto-reload")
):
    """Start the API server."""
    logger.info(f"Starting API server on {host}:{port}")
    
    # This would start a FastAPI server in a real implementation
    uvicorn.run(
        "src.rootzengine.api.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )


if __name__ == "__main__":
    app()
