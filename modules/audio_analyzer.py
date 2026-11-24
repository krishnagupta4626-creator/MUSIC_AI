"""
MODULE 3: AUDIO ANALYSIS ENGINE
===============================
Extracts acoustic, spectral, temporal, and harmonic features from uploaded MP3/WAV files
using Librosa, SoundFile, and SciPy.
Features extracted:
- Tempo (BPM) and onset envelope
- Duration (seconds & formatted mm:ss)
- Root Mean Square (RMS) Energy (Mean, Peak, Time series)
- Spectral Centroid (Timbre Brightness in Hz)
- Spectral Rolloff (High-frequency distribution in Hz)
- Zero-Crossing Rate (Perceived noisiness and percussiveness)
- Chroma STFT (12 semitone musical pitch distribution)
- Approximate energy variations over time for visualization
"""

import os
import io
import math
import tempfile
from typing import Dict, List, Any, Tuple, Optional

import numpy as np

# Set matplotlib cache dir to temp to avoid permission warnings on Windows
os.environ["MPLCONFIGDIR"] = tempfile.gettempdir()

try:
    import librosa
    import soundfile as sf
    _LIBROSA_AVAILABLE = True
except Exception:
    _LIBROSA_AVAILABLE = False


def format_duration(seconds: float) -> str:
    """Format duration in seconds into mm:ss format."""
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins:02d}:{secs:02d}"


def analyze_audio_file(audio_input: Any, original_filename: str = "uploaded_audio.wav") -> Dict[str, Any]:
    """
    Extract comprehensive acoustic and musical features from audio.
    Accepts file path (str), BytesIO buffer, or Streamlit UploadedFile.
    
    Returns structured dictionary with:
    - tempo: Beats Per Minute (float)
    - duration_sec: Duration in seconds (float)
    - duration_formatted: mm:ss (str)
    - rms_mean: Average RMS energy (float)
    - rms_max: Peak RMS energy (float)
    - spectral_centroid_mean: Timbral brightness in Hz (float)
    - spectral_rolloff_mean: High-frequency cutoff in Hz (float)
    - zcr_mean: Zero-crossing rate (float)
    - chroma_profile: 12-pitch distribution (Dict[str, float])
    - energy_timeseries: Sampled points of energy across time for plotting
    - waveform_downsampled: Sampled waveform amplitudes for waveform visualization
    - acoustic_profile_summary: Interpretive text summary
    """
    if not _LIBROSA_AVAILABLE:
        return {"error": "Librosa/Soundfile is not available in the current environment."}

    temp_path = None
    try:
        # If input is a file-like object from Streamlit upload, write to temporary file
        if hasattr(audio_input, "read"):
            suffix = os.path.splitext(original_filename)[1].lower()
            if suffix not in [".wav", ".mp3", ".ogg", ".flac"]:
                suffix = ".wav"
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(audio_input.read())
                temp_path = tmp.name
            load_target = temp_path
        elif isinstance(audio_input, str) and os.path.isfile(audio_input):
            load_target = audio_input
        else:
            return {"error": "Invalid audio input format. Expected file path or file-like stream."}

        # Load audio using librosa (downsampled to 22050 Hz mono for fast, robust processing)
        y, sr = librosa.load(load_target, sr=22050, mono=True)
        duration_sec = float(librosa.get_duration(y=y, sr=sr))

        if duration_sec < 0.5:
            return {"error": "Audio duration is too short for meaningful analysis (minimum 0.5s required)."}

        # 1. TEMPO (BPM) DETECTION
        try:
            onset_env = librosa.onset.onset_strength(y=y, sr=sr)
            tempo_result = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)
            # Handle librosa return signature variations across versions
            if isinstance(tempo_result, tuple):
                tempo = float(tempo_result[0])
            elif isinstance(tempo_result, (np.ndarray, list)):
                tempo = float(tempo_result[0])
            else:
                tempo = float(tempo_result)
        except Exception:
            tempo = 100.0

        # Round and normalize tempo
        tempo = round(tempo, 1)

        # 2. RMS ENERGY (Loudness & Dynamics)
        rms = librosa.feature.rms(y=y)[0]
        rms_mean = float(np.mean(rms))
        rms_max = float(np.max(rms))
        rms_std = float(np.std(rms))

        # Downsample RMS energy curve to ~60 points for responsive web visualization
        n_points = min(60, len(rms))
        indices = np.linspace(0, len(rms) - 1, n_points, dtype=int)
        time_points = [round(float(idx * 512 / sr), 2) for idx in indices]
        energy_values = [round(float(rms[idx]), 4) for idx in indices]
        energy_timeseries = [{"time": t, "energy": e} for t, e in zip(time_points, energy_values)]

        # 3. SPECTRAL CENTROID (Brightness/Timbre)
        spec_cent = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
        spectral_centroid_mean = round(float(np.mean(spec_cent)), 1)

        # 4. SPECTRAL ROLLOFF (Frequency Ceiling)
        spec_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
        spectral_rolloff_mean = round(float(np.mean(spec_rolloff)), 1)

        # 5. ZERO-CROSSING RATE (Percussiveness / Noisiness)
        zcr = librosa.feature.zero_crossing_rate(y=y)[0]
        zcr_mean = round(float(np.mean(zcr)), 4)

        # 6. CHROMA PITCH PROFILE (Harmonic Content - 12 pitch classes)
        chroma = librosa.feature.chroma_stft(y=y, sr=sr)
        chroma_mean = np.mean(chroma, axis=1)
        # Normalize sum to 1.0
        chroma_sum = np.sum(chroma_mean)
        if chroma_sum > 0:
            chroma_norm = chroma_mean / chroma_sum
        else:
            chroma_norm = chroma_mean

        pitch_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        chroma_profile = {pitch_names[i]: round(float(chroma_norm[i]) * 100, 1) for i in range(12)}
        # Identify dominant musical pitch class
        dominant_pitch = pitch_names[int(np.argmax(chroma_mean))]

        # 7. DOWNSAMPLED WAVEFORM FOR VISUALIZATION
        # Downsample raw waveform to 120 points for interactive SVG / Plotly display
        wf_step = max(1, len(y) // 120)
        downsampled_wf = [round(float(val), 3) for val in y[::wf_step][:120]]

        # 8. ACOUSTIC PROFILE INTERPRETATION
        # Assess tempo category
        if tempo < 75:
            tempo_cat = "Largo / Adagio (Slow, Contemplative)"
        elif tempo < 108:
            tempo_cat = "Andante / Moderato (Moderate, Flowing)"
        elif tempo < 130:
            tempo_cat = "Allegro (Upbeat, Driving)"
        else:
            tempo_cat = "Vivace / Presto (High-Speed, Energetic)"

        # Assess energy category
        if rms_mean < 0.05:
            energy_cat = "Subdued, intimate acoustic density"
        elif rms_mean < 0.12:
            energy_cat = "Moderate dynamic intensity"
        else:
            energy_cat = "High dynamic impact and power"

        # Assess brightness category
        if spectral_centroid_mean < 1500:
            timbre_cat = "Warm, dark, mellow acoustic color"
        elif spectral_centroid_mean < 2800:
            timbre_cat = "Balanced, natural presence"
        else:
            timbre_cat = "Bright, crisp, piercing high-frequency presence"

        summary = (
            f"The track features a tempo of {tempo} BPM ({tempo_cat}), "
            f"exhibiting {energy_cat} (mean RMS {rms_mean:.3f}) with {timbre_cat} "
            f"(spectral centroid {spectral_centroid_mean:.0f} Hz). "
            f"Dominant pitch class is centered around '{dominant_pitch}'."
        )

        return {
            "tempo": tempo,
            "tempo_category": tempo_cat,
            "duration_sec": round(duration_sec, 2),
            "duration_formatted": format_duration(duration_sec),
            "rms_mean": round(rms_mean, 4),
            "rms_max": round(rms_max, 4),
            "rms_std": round(rms_std, 4),
            "spectral_centroid_mean": spectral_centroid_mean,
            "spectral_rolloff_mean": spectral_rolloff_mean,
            "zcr_mean": zcr_mean,
            "chroma_profile": chroma_profile,
            "dominant_pitch": dominant_pitch,
            "energy_timeseries": energy_timeseries,
            "waveform_downsampled": downsampled_wf,
            "acoustic_profile_summary": summary,
            "original_filename": original_filename
        }

    except Exception as e:
        return {"error": f"Failed to analyze audio: {str(e)}"}
    finally:
        # Clean up temporary file if created
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass
