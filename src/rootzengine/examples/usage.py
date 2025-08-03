"""
RootzEngine Usage Examples

This file demonstrates how to use the RootzEngine library and CLI.
"""

import os
import json
from pathlib import Path

from src.rootzengine.audio.analysis import AudioStructureAnalyzer
from src.rootzengine.midi.converter import AudioToMIDIConverter
from src.rootzengine.core.config import settings


def analyze_audio_file(file_path: str) -> dict:
    """
    Analyze an audio file and print the results.
    
    Args:
        file_path: Path to the audio file
        
    Returns:
        Analysis results as a dictionary
    """
    print(f"Analyzing {file_path}...")
    analyzer = AudioStructureAnalyzer(file_path)
    results = analyzer.analyze()
    
    # Print key results
    print(f"Tempo: {results['tempo']} BPM")
    print(f"Key: {results['key']}")
    print(f"Sections: {len(results['sections'])}")
    
    for i, section in enumerate(results['sections']):
        print(f"  Section {i+1}: {section['start']:.2f}s - {section['end']:.2f}s")
        print(f"    Type: {section['type']}")
    
    return results


def generate_midi(file_path: str, output_path: str = None) -> str:
    """
    Generate a MIDI file from audio analysis.
    
    Args:
        file_path: Path to the audio file
        output_path: Optional path for output MIDI file
        
    Returns:
        Path to the generated MIDI file
    """
    if not output_path:
        output_path = os.path.splitext(file_path)[0] + ".mid"
    
    print(f"Generating MIDI from {file_path}...")
    analyzer = AudioStructureAnalyzer(file_path)
    analysis = analyzer.analyze()
    
    converter = AudioToMIDIConverter(analysis)
    midi_data = converter.generate()
    converter.save(midi_data, output_path)
    
    print(f"MIDI file saved to {output_path}")
    return output_path


def run_batch_processing(input_dir: str, output_dir: str) -> None:
    """
    Process all audio files in a directory.
    
    Args:
        input_dir: Directory containing audio files
        output_dir: Directory for output files
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    audio_files = []
    for ext in ['.mp3', '.wav', '.flac', '.ogg', '.m4a']:
        audio_files.extend(input_path.glob(f"*{ext}"))
    
    print(f"Found {len(audio_files)} audio files in {input_dir}")
    
    for audio_file in audio_files:
        try:
            print(f"\nProcessing {audio_file.name}...")
            
            # Analyze audio
            analysis = analyze_audio_file(str(audio_file))
            
            # Save analysis results
            analysis_file = output_path / f"{audio_file.stem}_analysis.json"
            with open(analysis_file, 'w') as f:
                json.dump(analysis, f, indent=2)
                
            # Generate MIDI
            midi_file = output_path / f"{audio_file.stem}.mid"
            generate_midi(str(audio_file), str(midi_file))
            
        except Exception as e:
            print(f"Error processing {audio_file.name}: {e}")


if __name__ == "__main__":
    # Example usage
    # Replace with an actual audio file path
    example_file = "path/to/your/audio/file.mp3"
    
    # Make sure the file exists before trying to process it
    if os.path.exists(example_file):
        # Single file analysis
        results = analyze_audio_file(example_file)
        
        # MIDI generation
        midi_path = generate_midi(example_file)
        
        print(f"\nAnalysis and MIDI generation complete!")
        print(f"Check the output files for results.")
    else:
        print(f"Please edit this file to specify a valid audio file path.")
        print(f"Then run: python -m src.rootzengine.examples.usage")
