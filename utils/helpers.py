"""
Utility Helpers
===============
Contains utility functions for JSON serialization, input validation,
formatting, and error handling.
"""

import json
from typing import Dict, Any, Tuple, Optional


def validate_inputs(lyrics: str, has_audio: bool) -> Tuple[bool, str]:
    """
    Validates user input.
    Ensures at least lyrics or audio is provided, and warns if lyrics are omitted.
    """
    lyrics_clean = lyrics.strip() if lyrics else ""
    if not lyrics_clean and not has_audio:
        return False, "Please provide song lyrics or upload an audio file to begin analysis."
    
    if not lyrics_clean and has_audio:
        # User uploaded audio without lyrics
        return True, "Audio uploaded. Note: Without lyrics, mood and storyboard will be estimated from acoustic features alone. Enter lyrics separately for full story generation."
    
    if len(lyrics_clean) < 15 and not has_audio:
        return False, "Lyrics are too short for meaningful NLP sentiment and emotion analysis. Please enter more complete lyrics."

    return True, "Valid inputs provided."


def serialize_project_state(
    song_title: str,
    artist_name: str,
    lyrics_analysis: Optional[Dict[str, Any]],
    emotion_analysis: Optional[Dict[str, Any]],
    audio_analysis: Optional[Dict[str, Any]],
    mood_analysis: Optional[Dict[str, Any]],
    storyboard: Optional[list],
    generator_mode: str
) -> str:
    """
    Serialize entire project analysis and storyboard into structured, pretty-printed JSON.
    """
    state = {
        "project_metadata": {
            "title": song_title or "Untitled Concept",
            "artist": artist_name or "Unknown Artist",
            "system": "Music-to-Visual Narrative Generator",
            "generator_engine": generator_mode,
            "version": "1.0.0"
        },
        "lyrics_nlp_analysis": lyrics_analysis or {},
        "emotion_classification": emotion_analysis or {},
        "audio_dsp_features": audio_analysis or {},
        "multimodal_mood_detection": mood_analysis or {},
        "cinematic_storyboard": storyboard or []
    }

    # Custom cleaner to ensure numpy types and floats serialize cleanly
    def default_converter(o):
        if hasattr(o, "item"):
            return o.item()
        if hasattr(o, "__dict__"):
            return o.__dict__
        return str(o)

    return json.dumps(state, indent=2, default=default_converter)
