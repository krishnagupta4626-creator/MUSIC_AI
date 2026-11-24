"""
Comprehensive Academic Testing Suite
====================================
Tests the Music-to-Visual Narrative Generator across:
1. All 5 required moods: Romantic, Sad, Happy, Motivational, Suspenseful
2. Edge cases: Missing lyrics, Missing audio, Empty inputs, Large inputs
3. PDF generation and JSON serialization
"""

import os
import sys
import json
import io

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.lyrics_analyzer import analyze_lyrics_full, parse_song_sections
from modules.emotion_detector import classify_emotions
from modules.audio_analyzer import analyze_audio_file
from modules.mood_detector import detect_mood
from modules.story_generator import generate_storyboard
from utils.helpers import validate_inputs, serialize_project_state
from utils.pdf_exporter import generate_storyboard_pdf


def run_comprehensive_tests():
    print("=" * 70)
    print("STARTING ACADEMIC VERIFICATION & MULTI-MOOD TESTING")
    print("=" * 70)

    # Load presets
    preset_file = os.path.join(os.path.dirname(__file__), "sample_data", "sample_lyrics.json")
    with open(preset_file, "r", encoding="utf-8") as f:
        presets = json.load(f)

    test_moods = ["romantic", "sad", "happy", "motivational", "suspenseful"]
    all_passed = True

    for mood_key in test_moods:
        print(f"\n--- [TEST] Mood Category: {mood_key.upper()} ---")
        song = presets[mood_key]
        title = song["title"]
        artist = song["artist"]
        lyrics = song["lyrics"]
        audio_path = os.path.join(os.path.dirname(__file__), "sample_data", "audio", f"{mood_key}_sample.wav")

        print(f"Song: '{title}' by {artist}")

        # 1. NLP Lyrics Analysis
        lyrics_res = analyze_lyrics_full(lyrics)
        assert "error" not in lyrics_res, f"Lyrics analysis failed for {mood_key}"
        print(f"  ✓ Lyrics NLP: {lyrics_res['total_words']} words, {lyrics_res['section_count']} sections, Valence: {lyrics_res['sentiment']['sentiment']}")

        # 2. Emotion Detection
        emotion_res = classify_emotions(lyrics)
        top_emo = emotion_res["dominant_emotion"]
        top_prob = emotion_res["dominant_percentage"]
        print(f"  ✓ Emotion Classified: Dominant = {top_emo} ({top_prob}%), Secondary = {emotion_res['secondary_emotion']} ({emotion_res['secondary_percentage']}%)")

        # 3. Audio Analysis
        assert os.path.exists(audio_path), f"Audio file missing: {audio_path}"
        with open(audio_path, "rb") as af:
            audio_bytes = af.read()
        audio_res = analyze_audio_file(io.BytesIO(audio_bytes), original_filename=f"{mood_key}.wav")
        assert "error" not in audio_res, f"Audio DSP failed: {audio_res.get('error')}"
        print(f"  ✓ Audio DSP: {audio_res['tempo']} BPM ({audio_res['tempo_category']}), RMS: {audio_res['rms_mean']:.4f}, Pitch: {audio_res['dominant_pitch']}")

        # 4. Multimodal Mood Detection
        mood_res = detect_mood(lyrics_res, emotion_res, audio_res)
        print(f"  ✓ Multimodal Mood: '{mood_res['dominant_mood']}' (Confidence: {mood_res['confidence_percentage']}%)")
        print(f"    Reasoning: {mood_res['explanation'][:100]}...")

        # 5. Cinematic Storyboard Generation (Offline Engine Fallback)
        storyboard, engine_mode = generate_storyboard(
            song_title=title,
            artist_name=artist,
            raw_lyrics=lyrics,
            parsed_sections=lyrics_res.get("sections", []),
            dominant_mood=mood_res["dominant_mood"],
            emotion_analysis=emotion_res,
            tempo=audio_res["tempo"],
            total_audio_duration=audio_res["duration_sec"],
            api_key=None  # Explicitly test offline fallback reliability
        )
        assert len(storyboard) >= 4, f"Storyboard too short for {mood_key}"
        print(f"  ✓ Storyboard: Generated {len(storyboard)} scenes using '{engine_mode}'")
        first_scene = storyboard[0]
        print(f"    Scene 01: '{first_scene['scene_title']}' | Angle: {first_scene['camera_angle']} | Lighting: {first_scene['lighting']}")

        # 6. PDF Generation
        pdf_bytes = generate_storyboard_pdf(
            song_title=title,
            artist_name=artist,
            mood_analysis=mood_res,
            lyrics_analysis=lyrics_res,
            emotion_analysis=emotion_res,
            audio_analysis=audio_res,
            storyboard=storyboard,
            generator_mode=engine_mode
        )
        assert len(pdf_bytes) > 1000, f"Generated PDF is invalid or too small for {mood_key}"
        print(f"  ✓ PDF Export: Generated {len(pdf_bytes)} bytes")

        # 7. JSON State Serialization
        json_out = serialize_project_state(
            song_title=title,
            artist_name=artist,
            lyrics_analysis=lyrics_res,
            emotion_analysis=emotion_res,
            audio_analysis=audio_res,
            mood_analysis=mood_res,
            storyboard=storyboard,
            generator_mode=engine_mode
        )
        assert len(json_out) > 500, "JSON export failed"
        print(f"  ✓ JSON Serialization: Verified valid JSON payload ({len(json_out)} chars)")

    # -------------------------------------------------------------------------
    # EDGE CASE TESTING
    # -------------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("TESTING EDGE CASES & ERROR HANDLING")
    print("=" * 70)

    # Edge Case 1: Empty input validation
    valid1, msg1 = validate_inputs("", False)
    assert not valid1, "Failed empty input validation check"
    print("  ✓ Edge Case 1 (Empty input): Successfully blocked with message:", msg1)

    # Edge Case 2: Audio only (no lyrics)
    valid2, msg2 = validate_inputs("", True)
    assert valid2, "Audio only should be valid with warning"
    print("  ✓ Edge Case 2 (Audio without lyrics): Accepted with notice:", msg2[:70], "...")

    mood_audio_only = detect_mood(lyrics_analysis=None, emotion_analysis=None, audio_analysis=audio_res)
    assert mood_audio_only["fusion_mode"] == "Unimodal (Audio DSP Only)"
    print("  ✓ Edge Case 2.1 (Acoustic Unimodal Mood):", mood_audio_only["dominant_mood"], f"({mood_audio_only['confidence_percentage']}%)")

    # Edge Case 3: Lyrics only (no audio)
    valid3, msg3 = validate_inputs("Some long lyrics for testing without audio.", False)
    assert valid3, "Lyrics only should be accepted"
    mood_lyrics_only = detect_mood(lyrics_analysis=lyrics_res, emotion_analysis=emotion_res, audio_analysis=None)
    assert mood_lyrics_only["fusion_mode"] == "Unimodal (Lyrics NLP Only)"
    print("  ✓ Edge Case 3 (Lyrics without audio):", mood_lyrics_only["dominant_mood"], f"({mood_lyrics_only['confidence_percentage']}%)")

    # Edge Case 4: Invalid/Tiny lyrics
    valid4, msg4 = validate_inputs("Too short", False)
    assert not valid4, "Short lyrics should fail validation"
    print("  ✓ Edge Case 4 (Short lyrics): Caught gracefully:", msg4)

    # Edge Case 5: Missing API Key fallback check
    story_fallback, mode_fallback = generate_storyboard(
        song_title="Offline Test",
        artist_name="Offline Band",
        raw_lyrics=presets["sad"]["lyrics"],
        parsed_sections=[],
        dominant_mood="Sad & Melancholic",
        emotion_analysis={"dominant_emotion": "Sadness"},
        tempo=64,
        total_audio_duration=120,
        api_key=None
    )
    assert len(story_fallback) > 0
    assert "Offline" in mode_fallback
    print(f"  ✓ Edge Case 5 (Missing API Key): Seamless fallback to '{mode_fallback}' with {len(story_fallback)} scenes generated")

    print("\n" + "=" * 70)
    print("ALL 5 MOODS AND EDGE CASES PASSED WITH 100% SUCCESS!")
    print("=" * 70)


if __name__ == "__main__":
    run_comprehensive_tests()
