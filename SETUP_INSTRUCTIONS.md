# RootzEngine Setup Instructions

## What You Need to Get Started

### IMMEDIATE SETUP (5 minutes):

**1. Install Core Dependencies:**
```bash
pip install librosa pretty_midi numpy soundfile
```

**2. Test Without API Keys:**
```bash
# Test with just your Bob Marley MIDI files
python demo_agentic_pipeline.py "input/raw-midi/bob_marley-no_woman_no_cry.mid"

# Test with Burning Spear audio
python demo_agentic_pipeline.py "input/raw-mp3/01 - Marcus Garvey.mp3"
```

**This will work immediately!** The system will:
- Analyze MIDI patterns and audio features
- Generate AI agent behavioral profiles
- Create rich metadata
- Skip external enrichment (no APIs needed for core functionality)

---

## OPTIONAL API ENRICHMENT (for metadata enhancement):

### Spotify API (Optional):
**What it adds:** Track titles, artists, tempo, key, energy scores
**Cost:** Free (1000 requests/month)
**Setup:**
1. Go to https://developer.spotify.com/dashboard
2. Create an app, get Client ID and Client Secret
3. Add to environment:
   ```bash
   export SPOTIFY_CLIENT_ID="your_client_id"
   export SPOTIFY_CLIENT_SECRET="your_client_secret"
   ```

### AudD API (Optional):
**What it adds:** Song identification from audio fingerprints
**Cost:** 500 free requests/month, then $5/1000 requests
**Setup:**
1. Sign up at https://audd.io
2. Get API key
3. Add to environment:
   ```bash
   export AUDD_API_KEY="your_api_key"
   ```

---

## WHAT WORKS WITHOUT API KEYS:

### Core AI Bandmate System:
- **10 AI agents** with behavioral profiles
- **Spectrotone analysis** (colors, timbres, playing styles)
- **MIDI pattern recognition** (one-drop, steppers, etc.)
- **Audio feature extraction** (tempo, key, harmonics, rhythm)
- **Cross-modal validation** (audio vs MIDI accuracy)
- **Rich metadata generation** with all analysis results

### Processing Pipeline:
- **Audio stem separation** (mock mode works for testing)
- **MIDI conversion** with accuracy validation
- **Maximum extraction efficiency**
- **Smart cleanup** (delete stems after successful validation)

---

## RECOMMENDED STARTUP SEQUENCE:

### Phase 1: Core Testing (Now):
```bash
pip install librosa pretty_midi numpy soundfile
python demo_agentic_pipeline.py "input/raw-midi/bob_marley-jammin.mid"
```

### Phase 2: Audio Processing:
```bash
python demo_agentic_pipeline.py "input/raw-mp3/07 - Tradition.mp3"
```

### Phase 3: API Enhancement (Later):
- Set up Spotify API for track metadata
- Add AudD for audio fingerprinting
- Enable full enrichment pipeline

---

## WHAT THE SYSTEM GENERATES:

### From Bob Marley MIDI:
- **Channel analysis**: Which instruments play what patterns
- **Behavioral extraction**: How bass follows drums, guitar skank patterns
- **Interaction mapping**: Cross-instrument relationships
- **Agent training data**: Per-channel behavioral characteristics

### From Burning Spear Audio:
- **Spectrotone profiles**: Color-coded instrument characteristics
- **Feature extraction**: Comprehensive audio analysis
- **MIDI conversion**: Audio to standardized MIDI channels
- **Validation scoring**: Accuracy metrics for keeping/discarding

### Result:
**AI bandmates that understand authentic reggae patterns and can play with humans!**

---

## BOTTOM LINE:

**START NOW with just pip install** - the core system works beautifully with your Bob Marley and Burning Spear collection. API keys are optional enhancements you can add later for even richer metadata.

Your reggae collection + our AI system = Intelligent musical bandmates!