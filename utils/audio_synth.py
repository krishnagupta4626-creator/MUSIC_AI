"""
Audio Synthesizer Utility
=========================
Generates synthetic WAV audio files matching different moods and musical characteristics
(Tempo, frequency content, harmonics, and energy curves) using NumPy and SciPy.
Useful for testing and offline college demonstrations without requiring external MP3 files.
"""

import os
import numpy as np
from scipy.io import wavfile


def generate_mood_audio(mood: str, duration_sec: float = 12.0, sample_rate: int = 22050) -> tuple[np.ndarray, int, str]:
    """
    Generate synthetic audio matching a designated mood.
    
    Returns:
        (audio_data, sample_rate, description)
    """
    t = np.linspace(0, duration_sec, int(sample_rate * duration_sec), endpoint=False)
    mood = mood.lower().strip()
    
    if "sad" in mood or "melanchol" in mood:
        # Slow tempo (~64 BPM), low-frequency minor chord (C minor: C3 130.81Hz, Eb3 155.56Hz, G3 196.0Hz), soft dynamics
        bpm = 64
        beat_interval = 60.0 / bpm
        envelope = 0.5 + 0.3 * np.sin(2 * np.pi * (1 / beat_interval) * t)
        tone = (
            0.50 * np.sin(2 * np.pi * 130.81 * t) +
            0.35 * np.sin(2 * np.pi * 155.56 * t) +
            0.25 * np.sin(2 * np.pi * 196.00 * t) +
            0.10 * np.sin(2 * np.pi * 65.41 * t)
        )
        # Gentle rain-like high frequency pink/white noise
        noise = 0.05 * np.random.normal(0, 1, len(t))
        signal = (tone * envelope + noise) * 0.4
        desc = "C Minor Adagio Piano/Cello Emulation (64 BPM, soft dynamics, low spectral energy)"

    elif "romantic" in mood or "love" in mood:
        # Warm, intimate tempo (~74 BPM), D Major chord (D3 146.83Hz, F#3 185.0Hz, A3 220.0Hz), smooth swell
        bpm = 74
        beat_interval = 60.0 / bpm
        envelope = 0.6 + 0.35 * np.sin(2 * np.pi * (1 / beat_interval) * t)
        tone = (
            0.45 * np.sin(2 * np.pi * 146.83 * t) +
            0.35 * np.sin(2 * np.pi * 185.00 * t) +
            0.30 * np.sin(2 * np.pi * 220.00 * t) +
            0.15 * np.sin(2 * np.pi * 293.66 * t)  # D4 overtone
        )
        signal = (tone * envelope) * 0.5
        desc = "D Major Acoustic Guitar/Warm String Emulation (74 BPM, resonant harmonics)"

    elif "happy" in mood or "joy" in mood:
        # Bright upbeat tempo (~124 BPM), G Major chord (G3 196.0Hz, B3 246.94Hz, D4 293.66Hz), punchy rhythmic envelope
        bpm = 124
        beat_interval = 60.0 / bpm
        rhythm = (np.sin(2 * np.pi * (bpm / 60.0) * t) > 0).astype(float)
        tone = (
            0.40 * np.sin(2 * np.pi * 196.00 * t) +
            0.30 * np.sin(2 * np.pi * 246.94 * t) +
            0.25 * np.sin(2 * np.pi * 293.66 * t) +
            0.20 * np.sin(2 * np.pi * 392.00 * t)
        )
        # Snare/hi-hat burst at beats
        burst = 0.15 * np.random.normal(0, 1, len(t)) * (np.sin(2 * np.pi * (bpm / 60.0) * t * 2) > 0.8).astype(float)
        signal = (tone * 0.6 + burst) * (0.6 + 0.4 * rhythm)
        desc = "G Major Upbeat Brass/Funk Groove (124 BPM, high spectral centroid, rhythmic envelope)"

    elif "motivational" in mood or "power" in mood or "triumph" in mood:
        # Driving tempo (~138 BPM), Power 5th chords (D3 146.83Hz, A3 220Hz, D4 293.66Hz), aggressive distorted wave
        bpm = 138
        beat_interval = 60.0 / bpm
        sub_kick = np.sin(2 * np.pi * 55.0 * t) * (np.sin(2 * np.pi * (bpm / 60.0) * t) > 0.3).astype(float)
        lead = (
            0.4 * np.sign(np.sin(2 * np.pi * 146.83 * t)) +  # Square wave for rock drive
            0.3 * np.sin(2 * np.pi * 220.00 * t) +
            0.2 * np.sin(2 * np.pi * 293.66 * t)
        )
        signal = (lead * 0.5 + sub_kick * 0.4)
        desc = "D Power Chord Anthem Drive (138 BPM, high RMS energy, rich harmonic overtones)"

    elif "suspense" in mood or "mystery" in mood or "fear" in mood:
        # Moderate tense tempo (~96 BPM), Tritone dissonance / dark minor (F#3 185.0Hz, C4 261.63Hz - devil's interval), pulse
        bpm = 96
        beat_interval = 60.0 / bpm
        lfo = 0.4 + 0.3 * np.sin(2 * np.pi * 0.25 * t)  # Slow 4-second sweep
        tone = (
            0.45 * np.sin(2 * np.pi * 92.50 * t) +   # Deep sub F#2
            0.35 * np.sin(2 * np.pi * 185.00 * t) +  # F#3
            0.35 * np.sin(2 * np.pi * 261.63 * t) +  # C4 Tritone
            0.15 * np.sin(2 * np.pi * 370.00 * t)
        )
        heartbeat = 0.3 * (np.sin(2 * np.pi * (bpm / 60.0) * t) > 0.85).astype(float)
        signal = (tone * lfo + heartbeat * 0.35) * 0.6
        desc = "Dark Ambient Tritone Drone with Heartbeat Pulse (96 BPM, eerie sub-bass)"

    else:
        # Balanced neutral audio
        bpm = 100
        t_envelope = 0.5 + 0.25 * np.sin(2 * np.pi * (bpm / 60.0) * t)
        tone = 0.5 * np.sin(2 * np.pi * 220.0 * t) + 0.3 * np.sin(2 * np.pi * 330.0 * t)
        signal = tone * t_envelope * 0.5
        desc = "Neutral Acoustic Test Harmonic Tone (100 BPM)"

    # Normalize to -1.0 to 1.0 to prevent clipping
    max_val = np.max(np.abs(signal))
    if max_val > 0:
        signal = signal / max_val * 0.85

    return signal, sample_rate, desc


def save_mood_audio_file(mood: str, output_path: str, duration_sec: float = 12.0) -> str:
    """Save synthesized mood audio to a 16-bit PCM WAV file."""
    audio_data, sample_rate, _ = generate_mood_audio(mood, duration_sec=duration_sec)
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    # Convert float32 to int16 PCM
    int_audio = (audio_data * 32767).astype(np.int16)
    wavfile.write(output_path, sample_rate, int_audio)
    return output_path
