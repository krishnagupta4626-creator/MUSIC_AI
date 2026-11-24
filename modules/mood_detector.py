"""
MODULE 4: MULTI-MODAL MOOD DETECTION ENGINE
===========================================
Fuses NLP lyrics features (emotions, sentiment polarity, themes) and
audio DSP characteristics (tempo, RMS energy, spectral centroid, ZCR)
into an overall musical mood prediction with confidence metrics and explanation.
"""

from typing import Dict, List, Any, Optional

# Core mood definitions with corresponding multimodal signatures
MOOD_DEFINITIONS = {
    "Romantic & Tender": {
        "description": "Warm, heartfelt, intimate, and affectionate atmosphere centered around connection and devotion.",
        "dominant_emotions": ["Love"],
        "supporting_emotions": ["Happiness", "Hope", "Nostalgia"],
        "acoustic_ideal": {"tempo_range": (65, 95), "energy_range": (0.02, 0.12), "valence": "positive"},
        "colors": ["#f43f5e", "#be123c", "#fef08a", "#d97706", "#4a044e"]
    },
    "Sad & Melancholic": {
        "description": "Somber, grieving, heart-rending, and deeply reflective atmosphere filled with sorrow and loss.",
        "dominant_emotions": ["Sadness", "Loneliness"],
        "supporting_emotions": ["Nostalgia", "Fear"],
        "acoustic_ideal": {"tempo_range": (50, 80), "energy_range": (0.01, 0.08), "valence": "negative"},
        "colors": ["#0f172a", "#475569", "#3b0764", "#94a3b8", "#1e293b"]
    },
    "Joyful & Euphoric": {
        "description": "Radiant, upbeat, festive, and exhilarating energy brimming with pure happiness and celebration.",
        "dominant_emotions": ["Happiness", "Excitement"],
        "supporting_emotions": ["Hope", "Love"],
        "acoustic_ideal": {"tempo_range": (115, 145), "energy_range": (0.09, 0.25), "valence": "positive"},
        "colors": ["#eab308", "#f97316", "#22c55e", "#38bdf8", "#fef3c7"]
    },
    "Fierce & Motivational": {
        "description": "Powerful, resilient, triumphant, and electrifying drive designed to inspire victory and defiance.",
        "dominant_emotions": ["Hope", "Anger"],
        "supporting_emotions": ["Excitement"],
        "acoustic_ideal": {"tempo_range": (120, 155), "energy_range": (0.10, 0.30), "valence": "positive_mixed"},
        "colors": ["#09090b", "#dc2626", "#ea580c", "#71717a", "#f59e0b"]
    },
    "Tense & Suspenseful": {
        "description": "Ominous, shadowy, enigmatic, and edge-of-seat thriller atmosphere filled with mystery and vigilance.",
        "dominant_emotions": ["Fear"],
        "supporting_emotions": ["Anger", "Loneliness"],
        "acoustic_ideal": {"tempo_range": (85, 115), "energy_range": (0.04, 0.16), "valence": "negative_tense"},
        "colors": ["#020617", "#064e3b", "#0e7490", "#334155", "#1e293b"]
    },
    "Nostalgic & Reflective": {
        "description": "Bittersweet, introspective journey evoking cherished memories, passage of time, and gentle longing.",
        "dominant_emotions": ["Nostalgia"],
        "supporting_emotions": ["Loneliness", "Love", "Sadness"],
        "acoustic_ideal": {"tempo_range": (70, 100), "energy_range": (0.03, 0.10), "valence": "neutral_mixed"},
        "colors": ["#78350f", "#fde68a", "#831843", "#f5f5f4", "#b45309"]
    }
}


def detect_mood(
    lyrics_analysis: Optional[Dict[str, Any]] = None,
    emotion_analysis: Optional[Dict[str, Any]] = None,
    audio_analysis: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Combines text NLP and audio DSP into an overall mood classification.
    Supports multimodal, text-only, and audio-only scenarios with tailored explanations.
    """
    has_lyrics = lyrics_analysis is not None and "error" not in lyrics_analysis
    has_emotions = emotion_analysis is not None and "error" not in emotion_analysis
    has_audio = audio_analysis is not None and "error" not in audio_analysis

    if not has_lyrics and not has_audio:
        return {
            "dominant_mood": "Neutral / Undefined",
            "confidence": 0.0,
            "secondary_emotions": [],
            "explanation": "No valid lyrics or audio data provided for mood analysis.",
            "fusion_mode": "None"
        }

    # Initialize candidate scores for each mood
    mood_scores: Dict[str, float] = {m: 0.1 for m in MOOD_DEFINITIONS.keys()}

    explanation_parts = []
    secondary_emotions: List[str] = []

    # --- 1. LYRICS & EMOTION CONTRIBUTION ---
    if has_emotions and emotion_analysis:
        dominant_e = emotion_analysis.get("dominant_emotion", "Happiness")
        dominant_p = emotion_analysis.get("dominant_percentage", 30.0)
        secondary_e = emotion_analysis.get("secondary_emotion", "Hope")
        secondary_p = emotion_analysis.get("secondary_percentage", 20.0)
        probs = emotion_analysis.get("probabilities", {})

        secondary_emotions = [f"{secondary_e} ({secondary_p}%)", f"{dominant_e} ({dominant_p}%)"]

        # Score matching based on emotion distributions
        for mood_name, mood_meta in MOOD_DEFINITIONS.items():
            # Dominant emotion matches get strong weight
            for target_e in mood_meta["dominant_emotions"]:
                weight = probs.get(target_e, 0.0) / 100.0
                mood_scores[mood_name] += weight * 4.0
            # Supporting emotion matches get moderate weight
            for target_e in mood_meta.get("supporting_emotions", []):
                weight = probs.get(target_e, 0.0) / 100.0
                mood_scores[mood_name] += weight * 1.0

        explanation_parts.append(
            f"Lyrical emotion classification identified '{dominant_e}' ({dominant_p}%) "
            f"and '{secondary_e}' ({secondary_p}%) as primary affective vectors."
        )

    if has_lyrics and lyrics_analysis:
        sentiment = lyrics_analysis.get("sentiment", {})
        compound = sentiment.get("compound", 0.0)
        themes = [t["theme"] for t in lyrics_analysis.get("themes", [])[:2]]
        
        if themes:
            explanation_parts.append(f"Recurring themes detected: {', '.join(themes)}.")

        # Modulate scores with thematic cues
        theme_names = [t.lower() for t in themes]
        if any("romance" in t for t in theme_names):
            mood_scores["Romantic & Tender"] += 1.5
        if any("grief" in t or "separation" in t for t in theme_names):
            mood_scores["Sad & Melancholic"] += 1.5
        if any("joy" in t or "celebration" in t for t in theme_names):
            mood_scores["Joyful & Euphoric"] += 1.5
        if any("triumph" in t or "ambition" in t for t in theme_names):
            mood_scores["Fierce & Motivational"] += 1.8
        if any("mystery" in t or "suspense" in t for t in theme_names):
            mood_scores["Tense & Suspenseful"] += 1.8

    # --- 2. AUDIO DSP CONTRIBUTION ---
    if has_audio and audio_analysis:
        tempo = audio_analysis.get("tempo", 100.0)
        rms = audio_analysis.get("rms_mean", 0.08)
        centroid = audio_analysis.get("spectral_centroid_mean", 2000.0)

        # Tempo & Energy heuristic alignments
        if tempo < 75 and rms < 0.07:
            mood_scores["Sad & Melancholic"] += 1.5
            mood_scores["Nostalgic & Reflective"] += 1.1
            acoustic_note = f"Slow tempo ({tempo} BPM) and delicate dynamics (RMS {rms:.3f})"
        elif tempo > 125 and rms > 0.09:
            mood_scores["Joyful & Euphoric"] += 1.2
            mood_scores["Fierce & Motivational"] += 1.5
            acoustic_note = f"Driving tempo ({tempo} BPM) and high energy (RMS {rms:.3f})"
        elif 80 <= tempo <= 115 and centroid < 1800:
            mood_scores["Tense & Suspenseful"] += 1.2
            acoustic_note = f"Moderate tempo ({tempo} BPM) with dark/tense spectral timbre ({centroid:.0f} Hz)"
        elif 65 <= tempo <= 100:
            mood_scores["Romantic & Tender"] += 1.1
            acoustic_note = f"Flowing tempo ({tempo} BPM) with warm acoustic contour"
        else:
            acoustic_note = f"Tempo of {tempo} BPM and RMS energy of {rms:.3f}"

        explanation_parts.append(f"Acoustic signal processing confirms {acoustic_note}.")

    # --- 3. FUSION & PROBABILITY CALCULATION ---
    sorted_moods = sorted(mood_scores.items(), key=lambda x: x[1], reverse=True)
    dominant_mood, top_score = sorted_moods[0]
    second_mood, second_score = sorted_moods[1]

    total_score = sum(s for _, s in sorted_moods)
    margin = (top_score - second_score) / max(0.001, total_score)
    
    if has_lyrics and has_audio:
        fusion_mode = "Multimodal Fusion (Lyrics NLP + Audio DSP)"
        confidence = min(0.96, max(0.55, 0.60 + margin * 0.8))
    elif has_lyrics:
        fusion_mode = "Unimodal (Lyrics NLP Only)"
        confidence = min(0.88, max(0.50, 0.52 + margin * 0.7))
        explanation_parts.append("(Audio file was not provided; mood estimation derived exclusively from lyrical semantics).")
    else:
        fusion_mode = "Unimodal (Audio DSP Only)"
        confidence = min(0.75, max(0.40, 0.45 + margin * 0.6))
        explanation_parts.append("(Lyrics were not provided; mood estimation derived from acoustic timbre and tempo signals).")

    confidence = round(confidence, 2)
    meta = MOOD_DEFINITIONS.get(dominant_mood, {})
    full_explanation = " ".join(explanation_parts)

    return {
        "dominant_mood": dominant_mood,
        "mood_description": meta.get("description", ""),
        "confidence": confidence,
        "confidence_percentage": round(confidence * 100, 1),
        "secondary_emotions": secondary_emotions,
        "runner_up_mood": second_mood,
        "fusion_mode": fusion_mode,
        "explanation": full_explanation,
        "color_palette": meta.get("colors", ["#6366f1", "#8b5cf6", "#ec4899", "#3b82f6", "#10b981"])
    }
