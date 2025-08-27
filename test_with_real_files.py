#!/usr/bin/env python3
"""
Test RootzEngine with REAL Bob Marley MIDI + Burning Spear MP3 files!
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_with_real_files():
    """Test the system with actual reggae files."""
    print("Testing RootzEngine with REAL REGGAE FILES!")
    print("=" * 50)
    
    # Test files we just copied
    test_files = [
        "test_dataset/midi/high_quality/bob_marley-no_woman_no_cry.mid",
        "test_dataset/midi/high_quality/bob_marley-one_love.mid", 
        "test_dataset/audio/roots_riddim/01 - Marcus Garvey.mp3",
        "test_dataset/audio/roots_riddim/07 - Tradition.mp3"
    ]
    
    print("Available test files:")
    for file_path in test_files:
        if Path(file_path).exists():
            size_kb = Path(file_path).stat().st_size / 1024
            print(f"  ✓ {Path(file_path).name} ({size_kb:.1f} KB)")
        else:
            print(f"  ✗ {file_path} - Missing")
    
    # Test agent system with real files
    try:
        from rootzengine.agents.channel_mapping import get_channel_mapping
        
        mapping = get_channel_mapping()
        print(f"\nAI Agent System Ready: {len(mapping.agents)} agents")
        
        # Show key agents for reggae
        key_agents = [1, 2, 4, 10]  # Bass, Guitar, Organ, Drums
        for channel in key_agents:
            agent = mapping.get_agent(channel)
            if agent:
                print(f"  Ch{channel}: {agent.instrument} - {agent.spectrotone.primary_color} {agent.spectrotone.timbre}")
        
    except Exception as e:
        print(f"Agent system test failed: {e}")
    
    # Test metadata system
    try:
        from rootzengine.metadata.schemas import create_metadata_template
        
        metadata = create_metadata_template("test_dataset/midi/high_quality/bob_marley-no_woman_no_cry.mid")
        print(f"\nMetadata System Ready: File ID {metadata.file_id[:8]}...")
        
    except Exception as e:
        print(f"Metadata system test failed: {e}")
    
    print("\nNEXT STEPS:")
    print("1. Install dependencies: pip install librosa pretty_midi numpy")
    print("2. Run: python demo_agentic_pipeline.py test_dataset/midi/high_quality/bob_marley-no_woman_no_cry.mid")
    print("3. Watch AI agents analyze Bob Marley's patterns!")

if __name__ == "__main__":
    test_with_real_files()