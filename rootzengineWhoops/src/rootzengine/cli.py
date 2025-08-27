import click
from rootzengine.audio.reggae_pattern_detector import detect_reggae_patterns
from rootzengine.ml.trainer import train_model

@click.group()
def cli():
    """RootzEngine CLI entrypoint."""
    pass

@cli.command()
@click.argument('input_file')
def analyze(input_file):
    """Analyze audio file using new pipeline."""
    click.echo(f'Analyzing {input_file}')

@cli.group()
def ml():
    """Machine learning commands."""
    pass

@ml.command()
@click.option('--config', default=None, help='Path to training config')
def train(config):
    """Train audio analysis models."""
    train_model(config)
    click.echo('Training completed')

@cli.command(name='reggae-detect')
@click.argument('audio_file')
def reggae_detect(audio_file):
    """Detect reggae patterns in audio."""
    patterns = detect_reggae_patterns(audio_file)
    click.echo(f'Detected patterns: {patterns}')
