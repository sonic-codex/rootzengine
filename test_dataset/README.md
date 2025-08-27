# 🎯 RootzEngine Curated Test Dataset

This dataset is specifically curated for testing the agentic AI-bandmate pipeline with maximum extraction efficiency.

## 📁 Directory Structure

### Audio Files (`/audio/`)
Organize by reggae subgenre and complexity for comprehensive testing:

#### `roots_riddim/`
- **Purpose**: Classic one-drop patterns with traditional instrumentation
- **Target Files**: 5-10 high-quality recordings with clear bass/drum separation
- **Characteristics**: Live feel, organic timing, traditional riddim patterns
- **Examples**: Bob Marley, Dennis Brown, Augustus Pablo riddims

#### `digital_dancehall/`
- **Purpose**: 80s-90s digital production with programmed elements
- **Target Files**: 5-10 tracks with digital drums and synthesized bass
- **Characteristics**: Quantized timing, digital effects, samplers
- **Examples**: Sleng Teng riddim, Bam Bam, digital era productions

#### `live_sessions/`
- **Purpose**: Multi-instrument recordings for cross-modal validation
- **Target Files**: 3-5 full band recordings with all instruments present
- **Characteristics**: Multiple instruments, live interaction, natural dynamics
- **Use**: Validate AI agent interaction patterns

#### `stem_separated/`
- **Purpose**: Pre-separated stems for validation testing
- **Target Files**: Individual instrument tracks from professional mixing
- **Characteristics**: Clean isolation, professional quality
- **Use**: Accuracy validation baseline for stem separation

### MIDI Files (`/midi/`)
Organize by quality and purpose for agent training:

#### `high_quality/` (Score ≥80)
- **Purpose**: Excellent MIDI files for training reference patterns
- **Target Files**: 10-15 professionally created MIDI files
- **Characteristics**: Accurate timing, proper channel mapping, realistic velocities
- **Use**: Gold standard for agent behavior training

#### `medium_quality/` (Score 60-79)
- **Purpose**: Good quality files that may need cleaning
- **Target Files**: 15-20 files with minor issues
- **Characteristics**: Mostly accurate but may have timing/velocity issues
- **Use**: Test cleaning algorithms and improvement metrics

#### `reference_patterns/`
- **Purpose**: Hand-curated riddim templates and patterns
- **Target Files**: 20-30 short MIDI patterns (1-4 bars each)
- **Characteristics**: Perfect accuracy, instrument-specific patterns
- **Use**: Training templates for individual AI agents

### Processed Output (`/processed/`)

#### `metadata/`
- **Purpose**: Rich JSON metadata files linking all related data
- **Format**: One JSON per source file with complete agentic analysis
- **Links**: Original → stems → MIDI → enrichment → agent data

#### `validated_midi/`
- **Purpose**: MIDI files that passed ≥85% accuracy validation
- **Format**: Standardized channel mapping for AI agents
- **Quality**: Only high-accuracy conversions retained

#### `agent_training_data/`
- **Purpose**: Per-channel agent training datasets
- **Format**: Instrument-specific behavior patterns and characteristics
- **Structure**: Organized by MIDI channel/instrument type

## 🎛️ Curation Guidelines

### Audio File Selection Criteria:
1. **Diverse riddim types** - Cover main reggae subgenres
2. **Clear instrumentation** - Identifiable bass, drums, guitar, keys
3. **Quality recordings** - Good signal-to-noise ratio
4. **Moderate complexity** - Not too simple or overly complex
5. **Standard song structure** - Intro/verse/chorus sections identifiable

### MIDI File Selection Criteria:
1. **Instrument separation** - Each instrument on separate channel
2. **Realistic velocities** - Human-like dynamics, not all velocity 127
3. **Proper timing** - Not perfectly quantized unless digital riddim
4. **Complete arrangements** - Multiple instruments, not just melody
5. **Standard MIDI compliance** - Proper channel 10 drums, etc.

### Processing Efficiency Rules:
1. **Single-pass analysis** - Extract everything possible before deletion
2. **Cross-validation** - Use both audio and MIDI to validate each other
3. **Accuracy thresholds** - Only keep MIDI conversions ≥85% accurate
4. **Linked metadata** - Every file links to all related processing outputs
5. **Agent-ready output** - Standardized format for AI bandmate training

## 🤖 AI-Bandmate Integration

### Channel Mapping Standard:
- **Ch 1**: Bass Guitar (Foundation Agent)
- **Ch 2**: Rhythm Guitar/Skank (Rhythm Agent)
- **Ch 3**: Lead Guitar (Lead Agent)
- **Ch 4**: Organ/Keys Comping (Harmonic Agent)
- **Ch 5**: Piano Chords (Chord Agent)
- **Ch 6**: Additional Percussion (Percussion Agent)
- **Ch 9**: Drums Kick/Snare (Drum Agent)
- **Ch 10**: Full Drum Kit (Kit Agent)
- **Ch 11**: Bass Synth (Sub-bass Agent)
- **Ch 12**: FX/Delays/Reverb (FX Agent)

### Agent Training Data:
Each processed file generates:
- Per-channel playing patterns
- Cross-instrument interaction patterns
- Spectrotone characteristics
- Timing/groove variations
- Dynamic response patterns
- Harmonic relationship patterns

## 📊 Success Metrics

### Processing Efficiency:
- **Extraction Completeness**: 100% of available features extracted per pass
- **MIDI Accuracy**: ≥85% conversion accuracy before stem deletion
- **Processing Speed**: Full analysis in <5 minutes per audio file
- **Storage Optimization**: Audio stems deleted after successful MIDI validation

### AI Training Quality:
- **Agent Behavior Diversity**: Each channel agent has unique characteristics
- **Cross-modal Validation**: Audio and MIDI features correlate ≥80%
- **Spectrotone Integration**: Color/timbre data enhances realism
- **Interaction Patterns**: Agent-to-agent relationships accurately captured

## 🔄 Workflow Integration

1. **Curate** → Select files meeting criteria above
2. **Process** → Run through unified pipeline with maximum extraction
3. **Validate** → Check accuracy metrics before audio deletion
4. **Enrich** → Single API call for metadata enrichment
5. **Train** → Generate agent-specific training data
6. **Deploy** → Use in agentic AI-bandmate system

This dataset serves as the foundation for training realistic, responsive AI bandmates that understand reggae music structure and can interact intelligently with human musicians.