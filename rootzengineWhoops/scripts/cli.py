#!/usr/bin/env python3
"""
RootzEngine Command Line Interface

Provides easy access to all RootzEngine functionality from the command line.
"""

import sys
import typer
from pathlib import Path
from typing import Optional, List
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import print as rprint

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from rootzengine.audio.analysis import AudioStructureAnalyzer
    from rootzengine.core.config import RootzEngineConfig
    from rootzengine.core.exceptions import RootzEngineError
except ImportError as e:
    rprint(f"[red]Error importing RootzEngine: {e}[/red]")
    rprint("[yellow]Please install dependencies: pip install -r docker/requirements/base.txt[/yellow]")
    sys.exit(1)

app = typer.Typer(
    name="rootzengine",
    help="🎛️ RootzEngine - AI-Powered Reggae Analysis & MIDI Generation",
    add_completion=False
)
console = Console()


@app.command()
def analyze(
    audio_path: Path = typer.Argument(..., help="Path to audio file"),
    output_dir: Optional[Path] = typer.Option(None, "--output-dir", "-o", help="Output directory for results"),
    format: str = typer.Option("json", "--format", "-f", help="Output format (json, yaml)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output")
):
    """
    Analyze a single audio file for reggae patterns and structure.
    
    Example:
        rootzengine analyze song.wav --output-dir results/
    """
    if not audio_path.exists():
        rprint(f"[red]Error: Audio file not found: {audio_path}[/red]")
        raise typer.Exit(1)
    
    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)
    else:
        output_dir = Path("./rootzengine_output")
        output_dir.mkdir(exist_ok=True)
    
    rprint(f"🎵 Analyzing: [bold]{audio_path}[/bold]")
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            
            # Initialize analyzer
            task1 = progress.add_task("Initializing analyzer...", total=None)
            config = RootzEngineConfig()
            analyzer = AudioStructureAnalyzer(config.audio)
            progress.update(task1, description="Loading audio...")
            
            # Perform analysis
            progress.update(task1, description="Analyzing structure...")
            analysis = analyzer.analyze_structure(str(audio_path))
            progress.update(task1, description="Processing results...")
            
            # Save results
            output_file = output_dir / f"{audio_path.stem}_analysis.{format}"
            
            if format.lower() == "json":
                import json
                with open(output_file, 'w') as f:
                    json.dump(analysis, f, indent=2)
            elif format.lower() == "yaml":
                import yaml
                with open(output_file, 'w') as f:
                    yaml.dump(analysis, f, default_flow_style=False)
            
            progress.update(task1, description="Complete!", completed=100)
    
        # Display results
        rprint("\n🎉 Analysis Complete!")
        _display_analysis_summary(analysis)
        rprint(f"\n📁 Full results saved to: [bold]{output_file}[/bold]")
        
    except RootzEngineError as e:
        rprint(f"[red]RootzEngine Error: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        rprint(f"[red]Unexpected error: {e}[/red]")
        if verbose:
            import traceback
            rprint(traceback.format_exc())
        raise typer.Exit(1)


@app.command()
def batch(
    input_dir: Path = typer.Argument(..., help="Directory containing audio files"),
    output_dir: Optional[Path] = typer.Option(None, "--output-dir", "-o", help="Output directory"),
    workers: int = typer.Option(4, "--workers", "-w", help="Number of parallel workers"),
    pattern: str = typer.Option("*.wav", "--pattern", "-p", help="File pattern to match"),
    cloud: bool = typer.Option(False, "--cloud", help="Use cloud processing")
):
    """
    Batch process multiple audio files.
    
    Example:
        rootzengine batch /path/to/songs/ --workers 4 --pattern "*.mp3"
    """
    if not input_dir.exists():
        rprint(f"[red]Error: Input directory not found: {input_dir}[/red]")
        raise typer.Exit(1)
    
    # Find audio files
    audio_files = list(input_dir.glob(pattern))
    if not audio_files:
        rprint(f"[yellow]No audio files found matching pattern: {pattern}[/yellow]")
        return
    
    if output_dir is None:
        output_dir = Path("./rootzengine_batch_output")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    rprint(f"🎵 Found {len(audio_files)} audio files to process")
    rprint(f"📁 Output directory: {output_dir}")
    rprint(f"⚙️  Workers: {workers}")
    
    # Process files
    config = RootzEngineConfig()
    analyzer = AudioStructureAnalyzer(config.audio)
    
    with Progress(console=console) as progress:
        main_task = progress.add_task("Processing files...", total=len(audio_files))
        
        for i, audio_file in enumerate(audio_files):
            try:
                progress.update(main_task, description=f"Processing {audio_file.name}...")
                
                # Analyze file
                analysis = analyzer.analyze_structure(str(audio_file))
                
                # Save result
                output_file = output_dir / f"{audio_file.stem}_analysis.json"
                import json
                with open(output_file, 'w') as f:
                    json.dump(analysis, f, indent=2)
                
                progress.advance(main_task)
                
            except Exception as e:
                rprint(f"[red]Error processing {audio_file}: {e}[/red]")
                continue
    
    rprint(f"\n🎉 Batch processing complete! Results in {output_dir}")


@app.command()
def serve(
    port: int = typer.Option(8000, "--port", "-p", help="Server port"),
    host: str = typer.Option("localhost", "--host", help="Server host"),
    reload: bool = typer.Option(False, "--reload", help="Auto-reload on code changes"),
    log_level: str = typer.Option("info", "--log-level", help="Log level")
):
    """
    Start the RootzEngine API server.
    
    Example:
        rootzengine serve --port 8000 --reload
    """
    try:
        import uvicorn
        from rootzengine.api.main import app as api_app
        
        rprint(f"🚀 Starting RootzEngine API server...")
        rprint(f"🌐 Server will be available at: http://{host}:{port}")
        rprint(f"📚 API documentation: http://{host}:{port}/docs")
        
        uvicorn.run(
            "rootzengine.api.main:app",
            host=host,
            port=port,
            reload=reload,
            log_level=log_level
        )
        
    except ImportError:
        rprint("[red]Error: uvicorn not installed. Install with: pip install uvicorn[/red]")
        raise typer.Exit(1)


@app.command()
def train(
    dataset: Path = typer.Argument(..., help="Path to training dataset"),
    model: str = typer.Option("reggae_structure", "--model", "-m", help="Model type to train"),
    epochs: int = typer.Option(100, "--epochs", "-e", help="Number of training epochs"),
    output_dir: Optional[Path] = typer.Option(None, "--output-dir", "-o", help="Model output directory")
):
    """
    Train machine learning models on reggae data.
    
    Example:
        rootzengine train ./data/training --model reggae_structure --epochs 50
    """
    rprint("🧠 Training functionality coming in v0.2.0!")
    rprint("Stay tuned for ML model training capabilities.")


@app.command()
def config(
    show: bool = typer.Option(False, "--show", help="Show current configuration"),
    reset: bool = typer.Option(False, "--reset", help="Reset to default configuration")
):
    """
    Manage RootzEngine configuration.
    """
    if show:
        config = RootzEngineConfig()
        
        table = Table(title="RootzEngine Configuration")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Sample Rate", str(config.audio.sample_rate))
        table.add_row("Hop Length", str(config.audio.hop_length))
        table.add_row("Debug Mode", str(config.debug))
        table.add_row("Log Level", config.log_level)
        table.add_row("Workers", str(config.workers))
        
        console.print(table)
    
    if reset:
        rprint("🔄 Configuration reset functionality coming soon!")


def _display_analysis_summary(analysis: dict):
    """Display a summary of analysis results."""
    
    # Create summary table
    table = Table(title="🎵 Analysis Summary")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    # Basic info
    table.add_row("Duration", f"{analysis.get('duration', 0):.1f}s")
    
    # Tempo info
    tempo_info = analysis.get('tempo', {})
    table.add_row("Tempo", f"{tempo_info.get('bpm', 0):.1f} BPM")
    table.add_row("Tempo Confidence", f"{tempo_info.get('confidence', 0):.2f}")
    
    # Key info
    key_info = analysis.get('key', {})
    table.add_row("Key", f"{key_info.get('root', 'Unknown')} {key_info.get('mode', '')}")
    
    # Reggae features
    reggae_info = analysis.get('reggae_features', {})
    table.add_row("Riddim Type", reggae_info.get('riddim_type', 'Unknown'))
    table.add_row("Reggae Confidence", f"{reggae_info.get('overall_reggae_confidence', 0):.2f}")
    
    # Sections
    sections = analysis.get('sections', [])
    table.add_row("Sections Found", str(len(sections)))
    
    console.print(table)
    
    # Show sections
    if sections:
        rprint("\n📝 Song Structure:")
        for i, section in enumerate(sections[:5]):  # Show first 5
            start = section.get('start', 0)
            end = section.get('end', 0)
            label = section.get('label', 'unknown')
            confidence = section.get('confidence', 0)
            rprint(f"  {i+1}. {start:.1f}s-{end:.1f}s: [bold]{label}[/bold] ({confidence:.2f})")
        
        if len(sections) > 5:
            rprint(f"  ... and {len(sections) - 5} more sections")


if __name__ == "__main__":
    app()