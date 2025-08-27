#!/usr/bin/env python3
"""
Comprehensive Demo of RootzEngine Agentic AI-Bandmate Pipeline

This script demonstrates the complete pipeline for processing audio and MIDI files
with maximum extraction efficiency for AI bandmate training.
"""

import logging
import sys
from pathlib import Path
import json

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from rootzengine.processing.unified_pipeline import create_processing_pipeline
from rootzengine.agents.channel_mapping import get_channel_mapping
from rootzengine.spectrotone.analyzer import create_spectrotone_analyzer
from rootzengine.metadata.schemas import create_metadata_template
from rootzengine.core.config import RootzEngineConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def demo_complete_pipeline():
    """Demonstrate the complete agentic processing pipeline."""
    logger.info("🎯 Starting RootzEngine Agentic AI-Bandmate Pipeline Demo")
    
    # Initialize components
    config = RootzEngineConfig()
    pipeline = create_processing_pipeline(config)
    channel_mapping = get_channel_mapping()
    spectrotone_analyzer = create_spectrotone_analyzer(config.audio)
    
    print("\n📋 Pipeline Configuration:")
    print(f"  • Sample Rate: {config.audio.sample_rate} Hz")
    print(f"  • Hop Length: {config.audio.hop_length}")
    print(f"  • Channel Mapping: {len(channel_mapping.agents)} AI agents")
    print(f"  • Accuracy Threshold: {pipeline.ACCURACY_THRESHOLD * 100}%")
    
    # Show channel mapping
    print("\n🎛️ Standardized Channel Mapping for AI Agents:")
    mapping_info = channel_mapping.get_standardized_mapping_info()
    
    for channel, info in mapping_info['channels'].items():
        print(f"  Ch {channel:2d}: {info['instrument']:<20} ({info['role']}) - {info['primary_color']} {info['timbre']}")
    
    # Demonstrate test dataset structure
    print("\n📁 Test Dataset Structure:")
    test_dataset_path = Path("test_dataset")
    if test_dataset_path.exists():
        for category in ["audio", "midi", "processed"]:
            category_path = test_dataset_path / category
            if category_path.exists():
                subdirs = [d.name for d in category_path.iterdir() if d.is_dir()]
                print(f"  • {category}/: {len(subdirs)} categories - {', '.join(subdirs)}")
    else:
        print("  • Test dataset not found - run setup first")
    
    # Demonstrate processing workflow
    print("\n🔄 Processing Workflow:")
    print("  1. File Input (Audio/MIDI) → Polymorphic Detection")
    print("  2. Maximum Extraction Phase:")
    print("     • Audio: Features → Spectrotone → Stems → Per-Stem Analysis")
    print("     • MIDI: Quality → Channels → Standardization")
    print("  3. Cross-Modal Validation (if both available)")
    print("  4. MIDI Conversion with Accuracy Validation")
    print("  5. AI Training Feature Generation")
    print("  6. Cleanup (stems deleted if validation passes)")
    
    # Demonstrate spectrotone analysis
    print("\n🎨 Spectrotone Analysis for AI Behavior:")
    reggae_instruments = ["bass_guitar", "rhythm_guitar", "organ", "drums"]
    
    for instrument in reggae_instruments:
        agent = channel_mapping.get_agent(channel_mapping.agents[
            next(ch for ch, ag in channel_mapping.agents.items() 
                 if ag.instrument == instrument)
        ].channel)
        
        if agent:
            print(f"  • {instrument}:")
            print(f"    - Color: {agent.spectrotone.primary_color} {agent.spectrotone.timbre}")
            print(f"    - Weight: {agent.spectrotone.weight:.1f}, Brightness: {agent.spectrotone.brightness:.1f}")
            print(f"    - Behavioral Traits: {', '.join(list(agent.behavioral_traits.keys())[:3])}")
    
    # Demonstrate metadata schema
    print("\n📊 Rich Agentic Metadata Schema:")
    sample_metadata = create_metadata_template("demo_audio.wav")
    
    print("  Key Metadata Components:")
    print("    • File References: Links all related files (audio → stems → MIDI → metadata)")
    print("    • Processing Chain: Tracks each stage with accuracy/timing metrics")  
    print("    • Per-Channel Analysis: Deep dive into each instrument's characteristics")
    print("    • Cross-Channel Relationships: How instruments interact")
    print("    • Groove Template: Overall song structure and feel")
    print("    • AI Training Features: Vectors optimized for agent training")
    print("    • Enrichment Data: External metadata from Spotify/AudD APIs")
    
    # Demonstrate efficiency optimizations
    print("\n⚡ Efficiency Optimizations:")
    print("  • Single-Pass Analysis: Extract everything before any deletions")
    print("  • Accuracy Validation: Only keep MIDI conversions ≥85% accurate")
    print("  • Smart Cleanup: Delete expensive stems after successful validation")
    print("  • Linked Metadata: All related files tracked in single JSON")
    print("  • Polymorphic Processing: Same pipeline handles audio and MIDI")
    
    # Show agent training data export
    print("\n🤖 AI Agent Training Data Export:")
    print("  Each processed file generates:")
    print("    • Per-channel behavior patterns and characteristics")
    print("    • Cross-instrument interaction matrices")
    print("    • Spectrotone-driven behavioral parameters")
    print("    • Timing/groove humanization data")
    print("    • Harmonic relationship patterns")
    
    # Interaction patterns
    print("\n🔗 Agent Interaction Patterns:")
    interaction_matrix = channel_mapping.get_interaction_matrix()
    
    print("  Key Relationships:")
    bass_ch = channel_mapping.BASS_CHANNEL
    drums_ch = channel_mapping.DRUMS_FULL_KIT_CHANNEL
    guitar_ch = channel_mapping.RHYTHM_GUITAR_CHANNEL
    
    if (bass_ch, drums_ch) in interaction_matrix:
        print(f"    • Bass (Ch{bass_ch}) ↔ Drums (Ch{drums_ch}): {interaction_matrix[(bass_ch, drums_ch)].value}")
    if (guitar_ch, bass_ch) in interaction_matrix:
        print(f"    • Guitar (Ch{guitar_ch}) ↔ Bass (Ch{bass_ch}): {interaction_matrix[(guitar_ch, bass_ch)].value}")
    
    print("\n✅ Demo Complete! The pipeline is ready for:")
    print("  • Processing curated test files")
    print("  • Training AI bandmate agents")  
    print("  • Real-time agentic music generation")
    

def demo_file_processing(sample_file: str):
    """
    Demonstrate processing a single file through the pipeline.
    
    Args:
        sample_file: Path to sample audio or MIDI file
    """
    if not Path(sample_file).exists():
        logger.warning(f"Sample file not found: {sample_file}")
        return
    
    logger.info(f"🎵 Processing sample file: {sample_file}")
    
    # Initialize pipeline
    pipeline = create_processing_pipeline()
    
    # Process the file
    result = pipeline.process_file(sample_file)
    
    if result.success:
        logger.info("✅ Processing completed successfully!")
        
        # Show results
        print(f"\n📊 Processing Results for {Path(sample_file).name}:")
        print(f"  • MIDI Accuracy: {result.midi_accuracy_score:.1%}" if result.midi_accuracy_score else "  • No MIDI conversion")
        print(f"  • Validation Passed: {'✅' if result.validation_passed else '❌'}")
        print(f"  • Stems Generated: {len(result.stems)}")
        print(f"  • Stems Deleted: {'✅' if result.stems_deleted else '❌'}")
        
        # Show metadata summary
        processing_summary = result.metadata.get_processing_summary()
        channel_summary = result.metadata.get_channel_summary()
        
        print(f"  • Processing Stages: {processing_summary['completed_stages']}/{processing_summary['total_stages']} completed")
        print(f"  • Channels Analyzed: {channel_summary['channels_analyzed']}")
        print(f"  • Instruments: {', '.join(channel_summary['instruments'])}")
        
        # Save metadata
        metadata_path = Path("test_dataset/processed/metadata") / f"{Path(sample_file).stem}_metadata.json"
        metadata_path.parent.mkdir(parents=True, exist_ok=True)
        result.metadata.save_to_file(str(metadata_path))
        print(f"  • Metadata saved: {metadata_path}")
        
    else:
        logger.error(f"❌ Processing failed: {result.error_message}")


def show_agent_training_example():
    """Show how to export data for training a specific AI agent."""
    print("\n🎯 AI Agent Training Data Example:")
    
    channel_mapping = get_channel_mapping()
    bass_agent = channel_mapping.get_agent(channel_mapping.BASS_CHANNEL)
    
    if bass_agent:
        print(f"\n🎸 Bass Agent (Channel {bass_agent.channel}) Training Profile:")
        print(f"  • Instrument: {bass_agent.instrument}")
        print(f"  • Role: {bass_agent.role.value}")
        print(f"  • Note Range: {bass_agent.midi_note_range[0]}-{bass_agent.midi_note_range[1]}")
        print(f"  • Velocity Range: {bass_agent.playing_chars.velocity_range}")
        print(f"  • Timing Variation: ±{bass_agent.playing_chars.timing_variation * 1000:.1f}ms")
        
        print(f"\n  Behavioral Traits:")
        for trait, strength in bass_agent.behavioral_traits.items():
            print(f"    • {trait}: {strength:.1%}")
        
        print(f"\n  Spectrotone Profile:")
        print(f"    • Color: {bass_agent.spectrotone.primary_color} {bass_agent.spectrotone.timbre}")
        print(f"    • Weight in Mix: {bass_agent.spectrotone.weight:.1%}")
        print(f"    • Brightness: {bass_agent.spectrotone.brightness:.1%}")
        
        print(f"\n  Interaction Patterns:")
        for target_ch, interaction in bass_agent.interaction_patterns.items():
            target_agent = channel_mapping.get_agent(target_ch)
            if target_agent:
                print(f"    • {interaction.value} with {target_agent.instrument} (Ch{target_ch})")


if __name__ == "__main__":
    # Run complete demo
    demo_complete_pipeline()
    
    # Show agent training example
    show_agent_training_example()
    
    # If sample file provided, demonstrate processing
    if len(sys.argv) > 1:
        sample_file = sys.argv[1]
        demo_file_processing(sample_file)
    else:
        print("\n💡 To see file processing in action:")
        print("   python demo_agentic_pipeline.py path/to/your/audio_or_midi_file")
        
    print("\n🚀 Ready to build AI bandmates that understand reggae!")