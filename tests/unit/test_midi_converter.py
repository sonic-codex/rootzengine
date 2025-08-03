"""Basic unit tests for MIDI converter module."""

import numpy as np
import pytest

# Import directly from src path
from src.rootzengine.midi.converter import AudioToMIDIConverter


def test_converter_initialization():
    """Test that the MIDI converter initializes correctly."""
    converter = AudioToMIDIConverter()
    assert converter is not None
    assert hasattr(converter, 'sample_rate')
    assert hasattr(converter, 'hop_length')


def test_convert_with_structure_basic():
    """Test that the structure-aware conversion method handles basic inputs."""
    converter = AudioToMIDIConverter()
    
    # Create minimal audio mock
    y = np.zeros(22050)  # 1 second of silence at 22050Hz
    sr = 22050
    
    # Create a simple MIDI container
    mock_midi = type('MockMIDI', (), {
        'initial_tempo': 0,
        'instruments': []
    })()
    
    # Create minimal structure data
    structure_data = {
        'tempo': {'bpm': 120.0},
        'sections': [
            {'start': 0.0, 'end': 1.0, 'label': 'intro'}
        ],
        'key': {'root': 'C', 'mode': 'major'},
        'reggae_features': {'riddim_type': 'one_drop'}
    }
    
    # This should run without error
    converter._convert_with_structure(y, sr, mock_midi, structure_data)
    
    # Basic assertions on the output MIDI
    assert mock_midi.initial_tempo == 120.0
    assert len(mock_midi.instruments) == 2  # Bass and drums
