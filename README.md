# RootzEngine 🎛️🦁  
*AI-Powered Reggae Riddim Generator and Groove Analysis Toolkit*

RootzEngine is an intelligent pipeline for analyzing and generating authentic reggae grooves. Designed for musicians, producers, and researchers, it combines classic riddim styles with modern machine learning tools to extract, visualize, and generate basslines, drum patterns, and skank rhythms from real tracks.

---

## 🌀 Features

- 🎚️ **Bassline Extraction** from MP3s using Demucs (2-stem separation)
- 🥁 **Drum Groove Detection** and High-Pass Filtering for clean rhythm
- 🧠 **Groove JSON + MIDI Output** for use in DAWs, AUM, or AI training
- 🎛️ **Riddim Style Selector** (One Drop, Steppers, Ska, Rocksteady, etc.)
- 🌐 **Google Cloud Integration** for high-speed cloud processing
- 🧩 **Modular Instrument Scripts** (bass, guitar, organ, clavinet)
- 📦 Generates ready-to-use MIDI + JSON grooves from real music

---

## 🛠️ Folder Structure

```bash
CloudServices/
├── pipeline.py                # Main processing script
├── utils/
│   ├── demucs_wrapper.py      # 2-stem separation logic
│   ├── bpm_key_detection.py   # Librosa-based BPM + key finder
│   ├── midi_generator.py      # Converts grooves to MIDI
│   ├── groove_json.py         # Encodes patterns as groove JSON
├── assets/
│   ├── logo.png               # Logo for splash screens / builds
├── output/                    # Generated grooves + logs
├── requirements.txt
└── README.md
# rootzengine
A riddim analysis and generation toolkit for reggae, dub, and ska.
