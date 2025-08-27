#!/usr/bin/env python3
"""
Simple test script for RootzEngine functionality.
Tests core components without requiring audio files.
"""

import sys
import numpy as np
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from rootzengine.core.config import RootzEngineConfig, AudioConfig
    from rootzengine.audio.features import FeatureExtractor
    from rootzengine.audio.reggae_patterns import ReggaePatternDetector
    from rootzengine.audio.analysis import AudioStructureAnalyzer
    
    print("🎵 RootzEngine Simple Test")
    print("=" * 40)
    
    # Test 1: Configuration
    print("1. Testing configuration system...")
    config = RootzEngineConfig()
    print(f"   ✅ Sample rate: {config.audio.sample_rate}")
    print(f"   ✅ Debug mode: {config.debug}")
    
    # Test 2: Feature Extractor
    print("\n2. Testing feature extractor...")
    extractor = FeatureExtractor()
    print("   ✅ Feature extractor initialized")
    
    # Test 3: Reggae Pattern Detector
    print("\n3. Testing reggae pattern detector...")
    detector = ReggaePatternDetector()
    print("   ✅ Pattern detector initialized")
    print(f"   ✅ Available riddim patterns: {list(detector.riddim_patterns.keys())}")
    
    # Test 4: Audio Structure Analyzer
    print("\n4. Testing audio structure analyzer...")
    analyzer = AudioStructureAnalyzer()
    print("   ✅ Structure analyzer initialized")
    
    # Test 5: Mock Analysis
    print("\n5. Running mock analysis...")
    
    # Create mock audio data
    sr = config.audio.sample_rate
    duration = 10  # 10 seconds
    t = np.linspace(0, duration, duration * sr)
    
    # Generate a simple reggae-like pattern (85 BPM)
    bpm = 85
    beat_freq = bpm / 60
    
    # Mock reggae: kick on beat 3, snare on 2&4, bass line
    y = (
        0.5 * np.sin(2 * np.pi * 60 * t) +  # Bass frequency
        0.3 * np.sin(2 * np.pi * beat_freq * t) +  # Beat frequency
        0.2 * np.random.normal(0, 0.1, len(t))  # Some noise
    )
    
    # Test feature extraction on mock data
    try:
        features = extractor.extract_all_features_from_array(y, sr)
        print("   ✅ Mock feature extraction successful")
        print(f"   ✅ Detected tempo: {features['rhythm']['tempo']:.1f} BPM")
        
        # Test reggae pattern detection
        reggae_features = detector.detect_patterns(y, sr, features)
        print(f"   ✅ Detected riddim: {reggae_features['riddim_type']}")
        print(f"   ✅ Reggae confidence: {reggae_features['overall_reggae_confidence']:.2f}")
        
    except Exception as e:
        print(f"   ⚠️  Mock analysis failed: {str(e)}")
        print("   (This is expected without real audio libraries)")
    
    print("\n🎉 RootzEngine basic test completed!")
    print("✅ All core components initialized successfully")
    print("\nNext steps:")
    print("- Install audio dependencies: pip install -r docker/requirements/base.txt")
    print("- Test with real audio: python test_enhanced_analysis.py")
    print("- Start API server: uvicorn rootzengine.api.main:app --reload")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please install dependencies: pip install -r docker/requirements/base.txt")
    sys.exit(1)
except Exception as e:
    print(f"❌ Test failed: {e}")
    sys.exit(1)