import pytest
import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from rootzengine.ml.training import train_model

def test_train_model_with_none():
    """Test that train_model handles None input gracefully"""
    result = train_model(None)
    assert isinstance(result, dict)
    assert result['status'] == 'skipped'
    assert result['reason'] == 'no_data'
    assert result['model_path'] is None

def test_train_model_with_data():
    """Test that train_model handles actual data"""
    mock_data = {"samples": [1, 2, 3], "labels": [0, 1, 0]}
    result = train_model(mock_data)
    assert isinstance(result, dict)
    assert result['status'] == 'completed'
    assert 'accuracy' in result
    assert 'model_path' in result
