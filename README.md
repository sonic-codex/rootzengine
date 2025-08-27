# RootzEngine 🎛️🤖  
*Agentic AI-Bandmate System for Reggae Music*

RootzEngine is an advanced agentic AI system that creates intelligent musical bandmates specializing in reggae. Using maximum extraction efficiency, it processes audio/MIDI files into rich training data for AI agents that understand reggae structure, interact realistically, and respond to human musicians with authentic reggae feel.

---

## 🌀 Core Features

### 🤖 Agentic AI Bandmates
- **10 specialized AI agents** with unique behavioral profiles
- **Spectrotone-driven behavior** (colors influence playing style)  
- **Cross-agent interactions** (bass locks with drums, guitar harmonizes with organ)
- **Reggae-optimized patterns** (one-drop, steppers, rockers, digital)
- **Real-time musical intelligence** and human-responsive playing

### ⚡ Maximum Extraction Pipeline
- **Single-pass analysis** - extract everything before any deletions
- **Cross-modal validation** - audio and MIDI validate each other
- **85% accuracy threshold** - only keep high-quality MIDI conversions
- **Smart cleanup** - delete expensive stems after validation
- **Polymorphic processing** - same pipeline handles audio and MIDI

### 🎨 Spectrotone Intelligence  
- **Color-coded instruments** (blue bass, tan guitar, ivory organ)
- **Behavioral implications** from spectral characteristics
- **Temporal evolution** tracking for dynamic response
- **Realistic AI behavior** based on actual audio analysis

---

## 🛠 Folder Structure

```bash
rootzengine/
├── pipeline.py                  # Full processing pipeline
├── utils/
│   ├── demucs_wrapper.py        # Stem separation logic
│   ├── bpm_key_detection.py     # Audio feature extraction
│   ├── midi_generator.py        # Groove-to-MIDI conversion
│   ├── groove_json.py           # Groove JSON encoder
│   ├── config_loader.py         # Auto-loader for settings
├── assets/
│   └── logo.png                 # For splash + app builds
├── data/
│   ├── mp3_raw/                 # Input bucket (GCS)
│   ├── mp3_enriched/            # Enriched files + JSON
│   ├── mp3_trash/               # Rejected or failed files
├── output/                      # Logs + generated content
├── notebooks/                   # Colab + demo notebooks
├── requirements.txt
└── README.md
```

---

## 🔄 Example Output: Enriched `.json`

```json
{
  "filename": "03-macklemore-b_boy-ftd.mp3",
  "source": "spotify",
  "metadata": {
    "title": "B-Boy",
    "artist": "Macklemore",
    "album": "The Language of My World",
    "year": 2005,
    "duration_sec": 215
  },
  "audio_features": {
    "tempo": 92.3,
    "key": 5,
    "mode": "minor"
  },
  "training_tags": ["roots", "one drop"],
  "midi": {
    "bass": "...",
    "drums": "...",
    "groove_json": "..."
  },
  "history": {
    "processed": "2025-03-30T...",
    "match_confidence": 0.91
  }
}
```

---

## 🚀 Quick Start

```python
# Initialize agentic pipeline
from rootzengine.processing.unified_pipeline import create_processing_pipeline
from rootzengine.agents.channel_mapping import get_channel_mapping

# Process audio/MIDI with maximum extraction
pipeline = create_processing_pipeline()
result = pipeline.process_file("your_reggae_track.wav")

# Get AI agent training data  
bass_agent = result.metadata.export_for_agent_training(1)  # Channel 1 = Bass
```

**Demo the complete pipeline:**
```bash
python demo_agentic_pipeline.py path/to/your/audio_file.wav
```

---

## 🛣 Implementation Status

- [✅] **Agentic AI System** - 10 specialized bandmate agents
- [✅] **Maximum Extraction Pipeline** - single-pass processing
- [✅] **Spectrotone Analysis** - color-driven behavior
- [✅] **Rich Metadata Schema** - comprehensive training data
- [✅] **Channel Standardization** - consistent AI interfaces
- [🔄] **MIDI-Tools Integration** - unified enrichment system
- [🔄] **Validation System** - accuracy-based cleanup
- [📋] **Live Performance API** - real-time agent interaction

---

## ⚡️ Built For

- Producers & DJs building reggae sets
- Sample pack creators tagging large libraries
- AI researchers training groove-aware music models
- Sync teams prepping audio for licensing
- Fans of riddim science and low-end frequency worship

---

## 🪙 License

MIT — fork it, flip it, rootify it.

---

> Made with dub delay and discipline by [@lt-blmr](https://github.com/lt-blmr)
