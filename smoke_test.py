#!/usr/bin/env python3
"""
RootzEngine Smoke Tests - Real File Processing

Tests the complete agentic pipeline with real audio/MIDI files.
Use this to validate the system before moving to production.
"""

import logging
import sys
from pathlib import Path
import json
import time
from typing import List, Tuple, Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from rootzengine.processing.unified_pipeline import create_processing_pipeline
from rootzengine.agents.channel_mapping import get_channel_mapping
from rootzengine.core.config import RootzEngineConfig

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SmokeTestResult:
    """Results from smoke testing."""
    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.errors = []
        self.warnings = []
        self.performance_metrics = {}


def find_test_files() -> Tuple[List[str], List[str]]:
    """Find available test files for smoke testing."""
    test_audio = []
    test_midi = []
    
    # Look in test_dataset first
    test_dataset = Path("test_dataset")
    if test_dataset.exists():
        # Audio files
        for subdir in ["audio/roots_riddim", "audio/digital_dancehall", "audio/live_sessions"]:
            audio_dir = test_dataset / subdir
            if audio_dir.exists():
                test_audio.extend([str(f) for f in audio_dir.glob("*.wav")])
                test_audio.extend([str(f) for f in audio_dir.glob("*.mp3")])
        
        # MIDI files  
        for subdir in ["midi/high_quality", "midi/medium_quality", "midi/reference_patterns"]:
            midi_dir = test_dataset / subdir
            if midi_dir.exists():
                test_midi.extend([str(f) for f in midi_dir.glob("*.mid")])
                test_midi.extend([str(f) for f in midi_dir.glob("*.midi")])
    
    # Also check common locations
    for common_path in ["data", "input", "samples", "test_files"]:
        if Path(common_path).exists():
            test_audio.extend([str(f) for f in Path(common_path).glob("**/*.wav")])
            test_audio.extend([str(f) for f in Path(common_path).glob("**/*.mp3")])
            test_midi.extend([str(f) for f in Path(common_path).glob("**/*.mid")])
    
    return test_audio, test_midi


def smoke_test_audio_processing(audio_file: str, result: SmokeTestResult) -> bool:
    """Test audio file processing through the pipeline."""
    logger.info(f"🎵 Testing audio processing: {Path(audio_file).name}")
    
    try:
        pipeline = create_processing_pipeline()
        start_time = time.time()
        
        processing_result = pipeline.process_file(audio_file)
        
        processing_time = time.time() - start_time
        result.performance_metrics[f"audio_{Path(audio_file).stem}"] = processing_time
        
        # Check critical components
        checks = []
        
        # 1. Basic processing success
        checks.append(("Processing completed", processing_result.success))
        
        # 2. Audio features extracted
        if processing_result.audio_features:
            checks.append(("Audio features extracted", True))
            
            # Check for key features
            has_rhythm = 'rhythm' in processing_result.audio_features
            has_spectral = 'spectral' in processing_result.audio_features
            checks.append(("Rhythm features present", has_rhythm))
            checks.append(("Spectral features present", has_spectral))
        else:
            checks.append(("Audio features extracted", False))
        
        # 3. Metadata created
        metadata_complete = (
            processing_result.metadata.processing_complete and
            len(processing_result.metadata.processing_chain) > 0
        )
        checks.append(("Metadata generated", metadata_complete))
        
        # 4. Channel analysis
        channels_analyzed = len(processing_result.metadata.per_channel_analysis) > 0
        checks.append(("Channel analysis completed", channels_analyzed))
        
        # 5. Performance check (should complete in reasonable time)
        reasonable_time = processing_time < 300  # 5 minutes max
        checks.append(("Processing time reasonable", reasonable_time))
        
        # Report results
        all_passed = True
        for check_name, passed in checks:
            if passed:
                logger.info(f"  ✅ {check_name}")
            else:
                logger.warning(f"  ❌ {check_name}")
                result.warnings.append(f"{audio_file}: {check_name} failed")
                all_passed = False
        
        logger.info(f"  ⏱️ Processing time: {processing_time:.1f}s")
        
        return all_passed
        
    except Exception as e:
        error_msg = f"Audio processing failed for {audio_file}: {str(e)}"
        logger.error(error_msg)
        result.errors.append(error_msg)
        return False


def smoke_test_midi_processing(midi_file: str, result: SmokeTestResult) -> bool:
    """Test MIDI file processing through the pipeline."""
    logger.info(f"🎹 Testing MIDI processing: {Path(midi_file).name}")
    
    try:
        pipeline = create_processing_pipeline()
        start_time = time.time()
        
        processing_result = pipeline.process_file(midi_file)
        
        processing_time = time.time() - start_time
        result.performance_metrics[f"midi_{Path(midi_file).stem}"] = processing_time
        
        # Check critical components
        checks = []
        
        # 1. Basic processing success
        checks.append(("Processing completed", processing_result.success))
        
        # 2. MIDI data loaded
        midi_loaded = processing_result.midi_data is not None
        checks.append(("MIDI data loaded", midi_loaded))
        
        # 3. Channel analysis
        channels_analyzed = len(processing_result.metadata.per_channel_analysis) > 0
        checks.append(("Channel analysis completed", channels_analyzed))
        
        # 4. Quality metrics
        if processing_result.midi_data:
            has_notes = any(len(inst.notes) > 0 for inst in processing_result.midi_data.instruments)
            checks.append(("MIDI contains notes", has_notes))
        
        # 5. Standardization
        standardized_ref = "standardized_midi" in processing_result.metadata.file_references
        checks.append(("MIDI standardization attempted", standardized_ref))
        
        # Report results
        all_passed = True
        for check_name, passed in checks:
            if passed:
                logger.info(f"  ✅ {check_name}")
            else:
                logger.warning(f"  ❌ {check_name}")
                result.warnings.append(f"{midi_file}: {check_name} failed")
                all_passed = False
        
        logger.info(f"  ⏱️ Processing time: {processing_time:.1f}s")
        
        return all_passed
        
    except Exception as e:
        error_msg = f"MIDI processing failed for {midi_file}: {str(e)}"
        logger.error(error_msg)
        result.errors.append(error_msg)
        return False


def smoke_test_agent_profiles(result: SmokeTestResult) -> bool:
    """Test AI agent profile system."""
    logger.info("🤖 Testing AI agent profiles")
    
    try:
        channel_mapping = get_channel_mapping()
        
        checks = []
        
        # 1. All expected agents exist
        expected_channels = [1, 2, 3, 4, 5, 6, 9, 10, 11, 12]
        agents_exist = all(channel_mapping.get_agent(ch) is not None for ch in expected_channels)
        checks.append(("All expected agents exist", agents_exist))
        
        # 2. Agent profiles complete
        complete_profiles = True
        for channel in expected_channels:
            agent = channel_mapping.get_agent(channel)
            if agent:
                has_spectrotone = agent.spectrotone is not None
                has_behaviors = len(agent.behavioral_traits) > 0
                has_interactions = len(agent.interaction_patterns) > 0
                
                if not (has_spectrotone and has_behaviors):
                    complete_profiles = False
                    break
        
        checks.append(("Agent profiles complete", complete_profiles))
        
        # 3. Interaction matrix
        interaction_matrix = channel_mapping.get_interaction_matrix()
        has_interactions = len(interaction_matrix) > 0
        checks.append(("Interaction matrix populated", has_interactions))
        
        # Report results
        all_passed = True
        for check_name, passed in checks:
            if passed:
                logger.info(f"  ✅ {check_name}")
            else:
                logger.warning(f"  ❌ {check_name}")
                result.warnings.append(f"Agent profiles: {check_name} failed")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        error_msg = f"Agent profile testing failed: {str(e)}"
        logger.error(error_msg)
        result.errors.append(error_msg)
        return False


def run_smoke_tests(max_files: int = 3) -> SmokeTestResult:
    """Run comprehensive smoke tests."""
    logger.info("🔥 Starting RootzEngine Smoke Tests")
    
    result = SmokeTestResult()
    
    # Find test files
    audio_files, midi_files = find_test_files()
    
    logger.info(f"Found {len(audio_files)} audio files, {len(midi_files)} MIDI files")
    
    if not audio_files and not midi_files:
        logger.warning("⚠️ No test files found! See file requirements below.")
        result.warnings.append("No test files available")
    
    # Test agent profiles first (no files needed)
    logger.info("\n--- Testing Agent System ---")
    result.tests_run += 1
    if smoke_test_agent_profiles(result):
        result.tests_passed += 1
    else:
        result.tests_failed += 1
    
    # Test audio processing
    if audio_files:
        logger.info("\n--- Testing Audio Processing ---")
        for audio_file in audio_files[:max_files]:
            result.tests_run += 1
            if smoke_test_audio_processing(audio_file, result):
                result.tests_passed += 1
            else:
                result.tests_failed += 1
    
    # Test MIDI processing  
    if midi_files:
        logger.info("\n--- Testing MIDI Processing ---")
        for midi_file in midi_files[:max_files]:
            result.tests_run += 1
            if smoke_test_midi_processing(midi_file, result):
                result.tests_passed += 1
            else:
                result.tests_failed += 1
    
    return result


def show_file_requirements():
    """Show what files are needed for comprehensive testing."""
    print("\n📋 REAL FILES NEEDED FOR TESTING:")
    
    print("\n🎵 AUDIO FILES NEEDED:")
    print("  For test_dataset/audio/roots_riddim/:")
    print("    • 2-3 classic reggae tracks (.wav or .mp3)")
    print("    • Clear bass and drum separation")
    print("    • Traditional riddim patterns (one-drop preferred)")
    print("    • Examples: Bob Marley, Dennis Brown, Augustus Pablo")
    
    print("\n  For test_dataset/audio/digital_dancehall/:")
    print("    • 2-3 digital reggae/dancehall tracks")
    print("    • Programmed drums, digital effects")
    print("    • Examples: Sleng Teng riddim variations")
    
    print("\n🎹 MIDI FILES NEEDED:")
    print("  For test_dataset/midi/high_quality/:")
    print("    • 3-5 professionally created reggae MIDI files")
    print("    • Proper channel separation (bass, drums, guitar, keys)")
    print("    • Realistic velocities (not all 127)")
    print("    • Human-like timing (not perfectly quantized)")
    
    print("\n  For test_dataset/midi/reference_patterns/:")
    print("    • Short 1-4 bar MIDI patterns")
    print("    • One-drop drum patterns, bass lines, skank patterns")
    print("    • Can be created manually or extracted from songs")
    
    print("\n🔗 VALIDATION PAIRS (CRITICAL):")
    print("    • Audio tracks WITH corresponding MIDI versions")
    print("    • Needed for accuracy validation system")
    print("    • Same song in both formats allows cross-modal testing")
    
    print("\n⚡ WHEN FILES ARE NEEDED:")
    print("    • RIGHT NOW: For validating spectrotone analysis")  
    print("    • NEXT: For testing stem separation accuracy")
    print("    • THEN: For validating MIDI conversion accuracy")
    print("    • FINALLY: For training actual AI agent behavior")


if __name__ == "__main__":
    print("🔥 RootzEngine Smoke Test System")
    
    if len(sys.argv) > 1 and sys.argv[1] == "--requirements":
        show_file_requirements()
        sys.exit(0)
    
    # Run smoke tests
    result = run_smoke_tests()
    
    # Report results
    print(f"\n📊 SMOKE TEST RESULTS:")
    print(f"  Tests Run: {result.tests_run}")
    print(f"  Passed: {result.tests_passed} ✅")
    print(f"  Failed: {result.tests_failed} ❌")
    
    if result.performance_metrics:
        print(f"\n⏱️ PERFORMANCE:")
        for test_name, time_taken in result.performance_metrics.items():
            print(f"  {test_name}: {time_taken:.1f}s")
    
    if result.warnings:
        print(f"\n⚠️ WARNINGS ({len(result.warnings)}):")
        for warning in result.warnings[:5]:  # Show first 5
            print(f"  • {warning}")
    
    if result.errors:
        print(f"\n❌ ERRORS ({len(result.errors)}):")
        for error in result.errors[:3]:  # Show first 3
            print(f"  • {error}")
    
    # Recommendations
    if result.tests_failed == 0:
        print(f"\n🎉 ALL TESTS PASSED! System ready for production.")
    else:
        print(f"\n🔧 ISSUES FOUND - see warnings/errors above")
        
    if not any("test files" not in w for w in result.warnings):
        print(f"\n💡 Run with --requirements to see what files you need:")
        print(f"   python smoke_test.py --requirements")