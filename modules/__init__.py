"""
Modules package for Music-to-Visual Narrative Generator.
"""
from modules.lyrics_analyzer import analyze_lyrics_full, parse_song_sections, tokenize_words
from modules.audio_analyzer import analyze_audio_file
from modules.emotion_detector import classify_emotions
from modules.mood_detector import detect_mood
from modules.color_generator import get_palette_for_emotion, get_hex_codes_for_emotion
from modules.camera_generator import recommend_cinematography
from modules.story_generator import generate_storyboard
