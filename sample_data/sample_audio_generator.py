"""
Generate 5 sample audio files matching the 5 test moods.
"""
import os
import sys

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.audio_synth import save_mood_audio_file

def main():
    audio_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio")
    os.makedirs(audio_dir, exist_ok=True)
    
    moods = {
        "romantic": "romantic_sample.wav",
        "sad": "sad_sample.wav",
        "happy": "happy_sample.wav",
        "motivational": "motivational_sample.wav",
        "suspenseful": "suspenseful_sample.wav",
    }
    
    print("Generating synthetic demo audio files...")
    for mood, filename in moods.items():
        filepath = os.path.join(audio_dir, filename)
        save_mood_audio_file(mood, filepath, duration_sec=10.0)
        print(f"Created: {filepath}")
    print("All sample audio files generated successfully!")

if __name__ == "__main__":
    main()
