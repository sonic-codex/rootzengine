# RootzEngine 🎛️🦁  
*AI-Powered Reggae Metadata + Groove Generation Toolkit*

RootzEngine is a modular, cloud-native pipeline for analyzing, enriching, and generating authentic reggae grooves. From MP3s to MIDI, it extracts metadata, splits stems, detects riddims, and outputs fully structured training files for music AI, live performance, or riddim production.

---

## 🌀 Features

### 🎧 Metadata Enrichment
- Fuzzy matching with Spotify + Audd APIs
- Auto-fills: Title, Artist, Album, Tempo, Key, Mode, Duration
- Outputs rich `.json` metadata per track
- Designed for AI training, sync licensing, sample curation

### 🎚 Groove Analysis + Generation
- Demucs-based 2-stem separation (bass + drums)
- BPM + key detection with Librosa
- One Drop / Steppers / Ska / Rocksteady style selector
- Groove encoded as structured JSON + MIDI
- Modular instrument logic (bass, organ, clav, skank guitar)

### ☁️ Cloud Native
- Google Cloud Storage integration
- Colab notebooks for instant web-based processing
- Batch file handling and smart trash sorting

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

Coming soon:  
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/)

---

## 🛣 Roadmap

- [x] Spotify/Audd enrichment
- [x] Groove detection + MIDI export
- [x] JSON training output
- [ ] Multi-instrument MIDI generator
- [ ] Genre/style classifier
- [ ] Web dashboard for groove preview + batch tagging
- [ ] Auto DJ/riddim builder (loop-based)

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
