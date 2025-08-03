"""CLI module for RootzEngine."""

import os
import typer
from typing import Optional
import uvicorn

from src.rootzengine.core.config import settings

app = typer.Typer(
    help="RootzEngine CLI - Audio analysis and MIDI generation toolkit"
)


@app.command()
def analyze(
    input_file: str = typer.Argument(
        ..., help="Path to the input audio file to analyze"
    ),
    output_dir: str = typer.Option(
        None, help="Directory to save analysis results (default: current dir)"
    ),
    save_json: bool = typer.Option(
        True, help="Save analysis results as JSON"
    ),
    detect_sections: bool = typer.Option(
        True, help="Detect structural sections in audio"
    ),
    detect_reggae_patterns: bool = typer.Option(
        True, help="Detect reggae-specific patterns"
    ),
):
    """
    Analyze audio file and extract musical information.
    
    This command performs comprehensive audio analysis including:
    - Tempo and beat detection
    - Key and scale detection
    - Section/structure detection
    - Reggae pattern detection
    """
    from src.rootzengine.audio.analysis import AudioStructureAnalyzer
    
    if not os.path.exists(input_file):
        typer.echo(f"Error: Input file '{input_file}' not found")
        raise typer.Exit(code=1)
    
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    output_path = output_dir if output_dir else os.getcwd()
    typer.echo(f"Analyzing {input_file}...")
    
    analyzer = AudioStructureAnalyzer(input_file)
    
    # Perform analysis
    results = analyzer.analyze(
        detect_sections=detect_sections,
        detect_reggae_patterns=detect_reggae_patterns,
    )
    
    if save_json:
        base_name = os.path.basename(input_file)
        file_name = os.path.splitext(base_name)[0]
        output_file = os.path.join(
            output_path,
            f"{file_name}_analysis.json"
        )
        analyzer.save_results(results, output_file)
        typer.echo(f"Analysis saved to {output_file}")
    
    typer.echo("Analysis complete!")
    return results


@app.command()
def generate_midi(
    input_file: str = typer.Argument(
        ..., help="Path to the input audio file"
    ),
    output_file: Optional[str] = typer.Option(
        None, help="Path for the output MIDI file"
    ),
    pattern_type: str = typer.Option(
        "auto", help="MIDI pattern type (auto, one_drop, steppers, rockers)"
    ),
    include_sections: bool = typer.Option(
        True, help="Generate patterns for different song sections"
    ),
):
    """
    Generate MIDI from audio with reggae patterns.
    
    This command creates MIDI files based on the audio analysis:
    - Extracts tempo and key from audio
    - Identifies structural sections
    - Generates appropriate patterns for each section
    - Creates a complete MIDI file with reggae groove patterns
    """
    from src.rootzengine.audio.analysis import AudioStructureAnalyzer
    from src.rootzengine.midi.converter import AudioToMIDIConverter
    
    if not os.path.exists(input_file):
        typer.echo(f"Error: Input file '{input_file}' not found")
        raise typer.Exit(code=1)
    
    # Create default output filename if none provided
    if not output_file:
        output_file = os.path.splitext(input_file)[0] + ".mid"
    
    typer.echo(f"Analyzing {input_file}...")
    analyzer = AudioStructureAnalyzer(input_file)
    analysis = analyzer.analyze()
    
    typer.echo(f"Generating MIDI with {pattern_type} pattern...")
    converter = AudioToMIDIConverter(analysis)
    midi_data = converter.generate(
        pattern_type=pattern_type,
        include_sections=include_sections,
    )
    
    # Save the generated MIDI file
    converter.save(midi_data, output_file)
    typer.echo(f"MIDI file saved to {output_file}")


@app.command()
def serve(
    host: str = typer.Option("0.0.0.0", help="Host to bind the API server"),
    port: int = typer.Option(8000, help="Port to bind the API server"),
    reload: bool = typer.Option(
        False, help="Enable auto-reload for development"
    ),
    workers: int = typer.Option(1, help="Number of worker processes"),
):
    """
    Start the RootzEngine API server.
    
    This command launches the FastAPI application with uvicorn.
    """
    typer.echo(f"Starting RootzEngine API on {host}:{port}")
    typer.echo(f"Environment: {settings.environment}")
    
    uvicorn.run(
        "src.rootzengine.api.main:app",
        host=host,
        port=port,
        reload=reload,
        workers=workers,
    )


if __name__ == "__main__":
    app()
