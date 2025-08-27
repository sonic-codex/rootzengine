#!/usr/bin/env python3
"""
Enhanced test script for RootzEngine with MIDI generation.
Demonstrates complete audio analysis and MIDI generation workflow.
"""

import sys
import numpy as np
from pathlib import Path
import tempfile

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from rootzengine.core.config import RootzEngineConfig
    from rootzengine.audio.analysis import AudioStructureAnalyzer
    from rootzengine.midi.converter import AudioToMIDIConverter
    from rootzengine.midi.patterns import ReggaePatternLibrary, RiddimType
    
    print("🎵 RootzEngine Enhanced Analysis Test")
    print("=" * 50)
    
    # Test 1: Configuration and Components
    print("1. Testing configuration and component initialization...")
    config = RootzEngineConfig()
    analyzer = AudioStructureAnalyzer(config.audio)
    converter = AudioToMIDIConverter(config.audio)
    pattern_library = ReggaePatternLibrary()
    
    print(f"   ✅ Sample rate: {config.audio.sample_rate}")
    print(f"   ✅ Hop length: {config.audio.hop_length}")
    print(f"   ✅ Components initialized successfully")
    
    # Test 2: Pattern Library
    print("\n2. Testing reggae pattern library...")
    available_riddims = list(RiddimType)
    print(f"   ✅ Available riddim types: {[r.value for r in available_riddims]}")
    
    # Test One Drop pattern
    one_drop_drums = pattern_library.get_pattern(RiddimType.ONE_DROP, "drums")
    if one_drop_drums:
        print(f"   ✅ One Drop drums: {len(one_drop_drums.notes)} notes, {one_drop_drums.length_beats} beats")
    
    one_drop_bass = pattern_library.get_pattern(RiddimType.ONE_DROP, "bass")
    if one_drop_bass:
        print(f"   ✅ One Drop bass: {len(one_drop_bass.notes)} notes, {one_drop_bass.length_beats} beats")
    
    # Test 3: Mock Audio Analysis
    print("\n3. Testing mock audio analysis...")
    
    # Create realistic reggae-like mock audio (85 BPM One Drop)
    sr = config.audio.sample_rate
    duration = 16  # 16 seconds
    t = np.linspace(0, duration, duration * sr)
    
    # 85 BPM = 1.41667 beats per second
    bpm = 85
    beat_freq = bpm / 60
    
    # Create One Drop pattern: kick on beat 3, snare on 2&4, bass emphasis
    y = np.zeros(len(t))
    
    # Add bass frequency (root note emphasis on beat 3 - the "drop")
    bass_freq = 60  # Low E
    for beat in range(int(duration * beat_freq)):
        beat_time = beat / beat_freq
        beat_pos = beat % 4
        
        if beat_pos == 2:  # Beat 3 (0-indexed) - the "One Drop"
            start_idx = int(beat_time * sr)
            end_idx = min(start_idx + int(0.5 * sr), len(y))
            decay = np.exp(-3 * np.linspace(0, 0.5, end_idx - start_idx))
            y[start_idx:end_idx] += 0.8 * np.sin(2 * np.pi * bass_freq * np.linspace(0, 0.5, end_idx - start_idx)) * decay
        elif beat_pos == 1 or beat_pos == 3:  # Beats 2&4 - snare
            start_idx = int(beat_time * sr)
            end_idx = min(start_idx + int(0.2 * sr), len(y))
            y[start_idx:end_idx] += 0.3 * np.random.normal(0, 0.1, end_idx - start_idx)  # Snare noise
    
    # Add some harmonic content (organ skank on off-beats)
    organ_freq = 220  # A3
    for beat in range(int(duration * beat_freq * 2)):  # Half beats
        beat_time = beat / (beat_freq * 2)
        if beat % 2 == 1:  # Off-beats
            start_idx = int(beat_time * sr)
            end_idx = min(start_idx + int(0.1 * sr), len(y))
            y[start_idx:end_idx] += 0.2 * np.sin(2 * np.pi * organ_freq * np.linspace(0, 0.1, end_idx - start_idx))
    
    # Add some background rhythm
    y += 0.1 * np.sin(2 * np.pi * beat_freq * t)  # Beat frequency
    y += 0.05 * np.random.normal(0, 0.1, len(y))  # Background noise
    
    print(f"   ✅ Created mock reggae audio: {duration}s at {bpm} BPM")
    
    # Test 4: Full Analysis Pipeline
    print("\n4. Testing full analysis pipeline...")
    
    # Create temporary audio file
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
        # Simple WAV header (44-byte header for 16-bit mono)
        sample_rate = sr
        num_samples = len(y)
        num_channels = 1
        bits_per_sample = 16
        
        # Convert float audio to 16-bit int
        y_int16 = (y * 32767).astype(np.int16)
        
        # Write basic WAV file manually
        temp_file.write(b'RIFF')
        temp_file.write((36 + num_samples * 2).to_bytes(4, 'little'))
        temp_file.write(b'WAVE')
        temp_file.write(b'fmt ')
        temp_file.write((16).to_bytes(4, 'little'))
        temp_file.write((1).to_bytes(2, 'little'))  # PCM
        temp_file.write(num_channels.to_bytes(2, 'little'))
        temp_file.write(sample_rate.to_bytes(4, 'little'))
        temp_file.write((sample_rate * num_channels * bits_per_sample // 8).to_bytes(4, 'little'))
        temp_file.write((num_channels * bits_per_sample // 8).to_bytes(2, 'little'))
        temp_file.write(bits_per_sample.to_bytes(2, 'little'))
        temp_file.write(b'data')
        temp_file.write((num_samples * 2).to_bytes(4, 'little'))
        temp_file.write(y_int16.tobytes())
        
        temp_audio_path = temp_file.name
    
    try:
        # Perform analysis
        print("   🔄 Running structure analysis...")
        analysis = analyzer.analyze_structure(temp_audio_path)
        
        print(f"   ✅ Analysis completed!")
        print(f"   📊 Detected tempo: {analysis['tempo']['bpm']:.1f} BPM")
        print(f"   🎵 Detected key: {analysis['key']['root']} {analysis['key']['mode']}")
        print(f"   🎛️ Riddim type: {analysis['reggae_features']['riddim_type']}")
        print(f"   🎯 Reggae confidence: {analysis['reggae_features']['overall_reggae_confidence']:.2f}")
        print(f"   📝 Sections found: {len(analysis['sections'])}")
        
        # Test 5: MIDI Generation
        print("\n5. Testing MIDI generation...")
        
        # Generate MIDI with different riddim types
        for riddim in [RiddimType.ONE_DROP, RiddimType.STEPPERS]:
            print(f"   🎼 Generating {riddim.value} MIDI...")
            
            midi_data = converter.generate_midi_from_analysis(
                analysis,
                instruments=["drums", "bass", "organ"],
                force_riddim=riddim
            )
            
            # Save MIDI file
            output_dir = Path("./test_output")
            output_dir.mkdir(exist_ok=True)
            midi_path = output_dir / f"test_{riddim.value}.mid"
            midi_data.write(str(midi_path))
            
            print(f"   ✅ {riddim.value} MIDI saved: {midi_path}")
            print(f"   🎶 Instruments: {len(midi_data.instruments)}")
            print(f"   🎵 Total notes: {sum(len(inst.notes) for inst in midi_data.instruments)}")
        
        # Test 6: Pattern Information
        print("\n6. Testing pattern information...")
        
        for riddim in [RiddimType.ONE_DROP, RiddimType.STEPPERS, RiddimType.ROCKERS]:
            info = pattern_library.get_riddim_info(riddim)
            available_instruments = pattern_library.get_available_instruments(riddim)
            tempo_range = pattern_library.get_compatible_tempo(riddim)
            
            print(f"   🎛️ {info['name']}:")
            print(f"      📖 {info['description']}")
            print(f"      📅 Era: {info.get('era', 'Unknown')}")
            print(f"      🎼 Instruments: {available_instruments}")
            print(f"      🎵 Tempo: {tempo_range[0]}-{tempo_range[1]} BPM")
        
        # Test 7: Similar Pattern Generation
        print("\n7. Testing similar pattern generation...")
        
        similar_midi = converter.generate_similar_pattern(
            analysis,
            duration=32.0,  # 32 seconds
            instruments=["drums", "bass", "organ", "guitar"]
        )
        
        similar_path = output_dir / "test_similar_pattern.mid"
        similar_midi.write(str(similar_path))
        
        print(f"   ✅ Similar pattern generated: {similar_path}")
        print(f"   ⏱️ Duration: 32 seconds")
        print(f"   🎶 Instruments: {len(similar_midi.instruments)}")
        
    finally:
        # Clean up temporary file
        Path(temp_audio_path).unlink(missing_ok=True)
    
    print("\n" + "=" * 50)
    print("🎉 Enhanced RootzEngine test completed successfully!")
    print("\n📁 Generated files:")
    print("   - test_one_drop.mid")
    print("   - test_steppers.mid") 
    print("   - test_similar_pattern.mid")
    print("\n🎵 Ready for:")
    print("   - Real audio file analysis")
    print("   - API server testing")
    print("   - Integration with existing MIDI pipeline")
    print("\n✨ RootzEngine is fully operational! ✨")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("📝 To fix:")
    print("   1. Install dependencies: pip install -r docker/requirements/base.txt")
    print("   2. Install additional packages: pip install pretty_midi")
    print("   3. For full audio support: pip install librosa soundfile")
    sys.exit(1)
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)