#!/usr/bin/env python3
"""Simple API test script."""

import tempfile
import requests
from pathlib import Path
import numpy as np
import soundfile as sf

# Create a test audio file
def create_test_audio():
    """Create a simple test audio file."""
    sr = 22050
    duration = 2
    t = np.linspace(0, duration, int(sr * duration))
    y = 0.3 * np.sin(2 * np.pi * 220 * t)  # 220 Hz sine wave
    
    temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
    sf.write(temp_file.name, y, sr)
    return temp_file.name

def test_api():
    """Test the API endpoints."""
    import uvicorn
    from rootzengine.api.main import app
    import threading
    import time
    
    # Start the server in a separate thread
    def run_server():
        uvicorn.run(app, host="127.0.0.1", port=8000, log_level="error")
    
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    time.sleep(2)  # Wait for server to start
    
    try:
        # Test health endpoint
        response = requests.get("http://127.0.0.1:8000/health")
        print(f"Health check: {response.status_code} - {response.json()}")
        
        # Test structure analysis endpoint
        audio_file = create_test_audio()
        with open(audio_file, 'rb') as f:
            files = {'audio': f}
            response = requests.post("http://127.0.0.1:8000/api/v1/analysis/structure", files=files)
            print(f"Structure analysis: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"  Sections: {len(result.get('sections', []))}")
                print(f"  Tempo: {result.get('tempo', {}).get('bpm')} BPM")
            else:
                print(f"  Error: {response.text}")
        
        # Clean up
        Path(audio_file).unlink()
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API server")
    except Exception as e:
        print(f"❌ API test failed: {e}")

if __name__ == "__main__":
    test_api()