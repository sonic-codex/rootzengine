#!/usr/bin/env python3
"""
Simple Smoke Test - No External Dependencies

Tests core system functionality without requiring librosa, pretty_midi, etc.
This validates the architectural design and imports.
"""

import logging
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_imports():
    """Test that core modules can be imported."""
    print("Testing Core Imports...")
    
    try:
        # Test agents system
        from src.rootzengine.agents.channel_mapping import get_channel_mapping
        channel_mapping = get_channel_mapping()
        assert len(channel_mapping.agents) > 0
        print("  [OK] Agent system imports and initializes")
        
        # Test metadata system
        from src.rootzengine.metadata.schemas import create_metadata_template
        metadata = create_metadata_template("test.wav")
        assert metadata.file_id is not None
        print("  [OK] Metadata system works")
        
        # Test spectrotone system
        from src.rootzengine.spectrotone.analyzer import SpectrotoneMapping
        mapping = SpectrotoneMapping()
        assert len(mapping.INSTRUMENT_PROFILES) > 0
        print("  [OK] Spectrotone system works")
        
        # Test configuration
        from src.rootzengine.core.config import RootzEngineConfig
        config = RootzEngineConfig()
        assert config.audio.sample_rate == 44100
        print("  [OK] Configuration system works")
        
        return True
        
    except Exception as e:
        print(f"  [FAIL] Import test failed: {e}")
        return False

def test_agent_profiles():
    """Test AI agent profile system."""
    print("\nTesting Agent Profiles...")
    
    try:
        from src.rootzengine.agents.channel_mapping import get_channel_mapping
        
        channel_mapping = get_channel_mapping()
        
        # Test expected agents exist
        expected_channels = [1, 2, 3, 4, 5, 6, 9, 10, 11, 12]
        for channel in expected_channels:
            agent = channel_mapping.get_agent(channel)
            assert agent is not None, f"Agent for channel {channel} missing"
            assert agent.spectrotone is not None, f"Agent {channel} missing spectrotone"
            assert len(agent.behavioral_traits) > 0, f"Agent {channel} missing behavioral traits"
        
        print(f"  [OK] All {len(expected_channels)} agents configured correctly")
        
        # Test interaction matrix
        interactions = channel_mapping.get_interaction_matrix()
        assert len(interactions) > 0, "No interaction patterns defined"
        print(f"  [OK] {len(interactions)} interaction patterns defined")
        
        return True
        
    except Exception as e:
        print(f"  [FAIL] Agent profile test failed: {e}")
        return False

def test_metadata_schema():
    """Test metadata schema functionality."""
    print("\n📊 Testing Metadata Schema...")
    
    try:
        from src.rootzengine.metadata.schemas import (
            create_metadata_template,
            FileReference,
            FileType,
            ProcessingStatus,
            ProcessingMetrics
        )
        from datetime import datetime
        
        # Create metadata
        metadata = create_metadata_template("test_audio.wav")
        assert metadata.file_id is not None
        
        # Add file reference
        file_ref = FileReference(
            file_id="test123",
            file_type=FileType.AUDIO,
            file_path="test.wav"
        )
        metadata.add_file_reference("original", file_ref)
        
        # Add processing stage
        stage = ProcessingMetrics(
            stage_name="test_stage",
            status=ProcessingStatus.COMPLETED,
            start_time=datetime.now(),
            accuracy_score=0.95
        )
        metadata.add_processing_stage(stage)
        
        # Test export
        metadata_dict = metadata.to_dict()
        assert "file_id" in metadata_dict
        assert "processing_chain" in metadata_dict
        
        print("  ✅ Metadata schema works correctly")
        return True
        
    except Exception as e:
        print(f"  ❌ Metadata schema test failed: {e}")
        return False

def test_spectrotone_mapping():
    """Test spectrotone mapping system."""
    print("\n🎨 Testing Spectrotone System...")
    
    try:
        from src.rootzengine.spectrotone.analyzer import SpectrotoneMapping
        
        mapping = SpectrotoneMapping()
        
        # Test instrument profiles
        reggae_instruments = ["bass_guitar", "rhythm_guitar", "organ", "drums"]
        for instrument in reggae_instruments:
            profile = mapping.INSTRUMENT_PROFILES.get(instrument)
            assert profile is not None, f"Missing profile for {instrument}"
            assert profile.primary_color is not None
            assert 0 <= profile.brightness <= 1
            assert 0 <= profile.weight <= 1
        
        print(f"  ✅ {len(mapping.INSTRUMENT_PROFILES)} instrument profiles defined")
        
        # Test behavioral implications would go here if we had audio
        return True
        
    except Exception as e:
        print(f"  ❌ Spectrotone test failed: {e}")
        return False

def test_file_structure():
    """Test that file structure is correct."""
    print("\n📁 Testing File Structure...")
    
    required_dirs = [
        "src/rootzengine/agents",
        "src/rootzengine/metadata", 
        "src/rootzengine/spectrotone",
        "src/rootzengine/core",
        "test_dataset"
    ]
    
    missing_dirs = []
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            missing_dirs.append(dir_path)
    
    if missing_dirs:
        print(f"  ❌ Missing directories: {missing_dirs}")
        return False
    else:
        print(f"  ✅ All {len(required_dirs)} required directories exist")
        return True

def run_simple_smoke_tests():
    """Run all simple smoke tests."""
    print("RootzEngine Simple Smoke Tests (No External Dependencies)")
    print("=" * 60)
    
    tests = [
        ("Core Imports", test_imports),
        ("Agent Profiles", test_agent_profiles), 
        ("Metadata Schema", test_metadata_schema),
        ("Spectrotone System", test_spectrotone_mapping),
        ("File Structure", test_file_structure)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"  ⚠️ {test_name} had issues")
        except Exception as e:
            print(f"  ❌ {test_name} crashed: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL BASIC TESTS PASSED!")
        print("\n💡 Next Steps:")
        print("  1. Install dependencies: pip install librosa pretty_midi numpy")
        print("  2. Add test files to test_dataset/")
        print("  3. Run full smoke test: python smoke_test.py")
    else:
        print("🔧 ISSUES FOUND - fix architecture before adding dependencies")
    
    return passed == total

if __name__ == "__main__":
    success = run_simple_smoke_tests()
    sys.exit(0 if success else 1)