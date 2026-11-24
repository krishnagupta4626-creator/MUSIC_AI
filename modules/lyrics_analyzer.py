"""
MODULE 2: LYRICS ANALYSIS ENGINE
================================
Performs natural language processing, text preprocessing, tokenization,
TF-IDF keyword extraction, thematic detection, and sentiment analysis on song lyrics.
"""

import re
import string
from collections import Counter
from typing import Dict, List, Any, Tuple

import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Ensure NLTK resources are available
try:
    _vader = SentimentIntensityAnalyzer()
except Exception:
    try:
        nltk.download('vader_lexicon', quiet=True)
        _vader = SentimentIntensityAnalyzer()
    except Exception:
        _vader = None

try:
    _stop_words = set(stopwords.words('english'))
except Exception:
    try:
        nltk.download('stopwords', quiet=True)
        _stop_words = set(stopwords.words('english'))
    except Exception:
        _stop_words = {
            'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your',
            'he', 'him', 'his', 'she', 'her', 'it', 'its', 'they', 'them', 'their',
            'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is',
            'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having',
            'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or',
            'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about',
            'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above',
            'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under',
            'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why',
            'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some',
            'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very',
            's', 't', 'can', 'will', 'just', 'don', 'should', 'now', 'd', 'll', 'm', 'o',
            're', 've', 'y', 'ain', 'aren', 'couldn', 'didn', 'doesn', 'hadn', 'hasn',
            'haven', 'isn', 'ma', 'mightn', 'mustn', 'needn', 'shan', 'shouldn', 'wasn',
            'weren', 'won', 'wouldn'
        }

# Pre-defined semantic thematic lexicons for thematic detection
THEME_LEXICON = {
    "Love & Romance": [
        "love", "heart", "darling", "kiss", "forever", "embrace", "touch", "tender",
        "sweet", "passion", "flame", "adore", "beloved", "romance", "whisper", "vow"
    ],
    "Grief & Separation": [
        "rain", "tears", "goodbye", "broken", "empty", "shadow", "hollow", "lost",
        "fade", "cry", "pain", "sorrow", "regret", "vanished", "ache", "funeral"
    ],
    "Triumph & Ambition": [
        "rise", "champion", "storm", "thunder", "destiny", "unbroken", "power", "glory",
        "conquer", "fight", "warrior", "fire", "crown", "strong", "wings", "soar"
    ],
    "Joy & Celebration": [
        "sun", "sunburst", "dance", "carnival", "laughter", "smile", "festival", "bright",
        "celebrate", "rhythm", "groove", "colors", "gold", "alive", "joy", "sing"
    ],
    "Mystery & Suspense": [
        "cipher", "labyrinth", "neon", "shadow", "secrets", "classified", "danger",
        "siren", "clock", "whisper", "wire", "mist", "asphalt", "dark", "hunter", "prey"
    ],
    "Solitude & Introspection": [
        "solitude", "hallway", "mirror", "room", "silence", "echo", "lonely", "wander",
        "night", "isolate", "ponder", "memory", "photograph", "whisper", "ghost"
    ],
    "Nature & Transcendence": [
        "ocean", "tide", "sky", "horizon", "stars", "river", "mountain", "wind",
        "breeze", "earth", "clouds", "sunlight", "seashore", "waves", "beacon"
    ]
}


def clean_lyrics(raw_lyrics: str) -> str:
    """
    Clean and preprocess lyrics text.
    Removes bracketed cues, normalizes whitespace and punctuation.
    """
    if not raw_lyrics:
        return ""
    # Remove stage/structure tags like [Chorus], (Verse 1), etc.
    cleaned = re.sub(r'\[.*?\]|\(.*?\)', ' ', raw_lyrics)
    # Normalize punctuation and line breaks
    cleaned = re.sub(r'[^\w\s\']', ' ', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned.lower()


def tokenize_words(text: str) -> List[str]:
    """Tokenize text into lowercase words, excluding punctuation and stopwords."""
    clean = clean_lyrics(text)
    tokens = [w for w in clean.split() if w not in _stop_words and len(w) > 2]
    return tokens


def parse_song_sections(raw_lyrics: str) -> List[Dict[str, str]]:
    """
    Parse lyrics into distinct song sections (e.g. Intro, Verse 1, Chorus, Bridge, Outro).
    If no explicit section headers [Section] exist, splits into stanzas based on double line breaks.
    """
    if not raw_lyrics or not raw_lyrics.strip():
        return []

    lines = [line.strip() for line in raw_lyrics.split('\n')]
    sections: List[Dict[str, str]] = []
    current_label = "Section 1"
    current_lines: List[str] = []

    header_regex = re.compile(r'^\[\s*([a-zA-Z0-9\s\-]+)\s*\]$|^\(\s*([a-zA-Z0-9\s\-]+)\s*\)$')

    for line in lines:
        if not line:
            # Empty line could separate stanzas
            if current_lines and not any(header_regex.match(l) for l in current_lines):
                # We reached stanza break in headerless lyrics
                pass
            continue

        match = header_regex.match(line)
        if match:
            # We hit a new section header
            if current_lines:
                text_block = "\n".join(current_lines).strip()
                if text_block:
                    sections.append({
                        "section_name": current_label,
                        "text": text_block,
                        "line_count": len(current_lines)
                    })
            current_label = (match.group(1) or match.group(2)).title().strip()
            current_lines = []
        else:
            current_lines.append(line)

    if current_lines:
        text_block = "\n".join(current_lines).strip()
        if text_block:
            sections.append({
                "section_name": current_label,
                "text": text_block,
                "line_count": len(current_lines)
            })

    # If no headers were detected and only 1 big section exists, partition by stanzas
    if len(sections) <= 1 and "\n\n" in raw_lyrics:
        raw_stanzas = [s.strip() for s in raw_lyrics.split("\n\n") if s.strip()]
        if len(raw_stanzas) > 1:
            sections = []
            labels = ["Intro", "Verse 1", "Chorus", "Verse 2", "Bridge", "Final Chorus", "Outro"]
            for idx, stanza in enumerate(raw_stanzas):
                label = labels[idx] if idx < len(labels) else f"Scene {idx+1}"
                sections.append({
                    "section_name": label,
                    "text": stanza,
                    "line_count": len(stanza.split('\n'))
                })

    return sections


def extract_keywords(lyrics: str, top_n: int = 12) -> List[Tuple[str, int]]:
    """
    Extract key content words using frequency and TF-IDF style importance heuristics.
    """
    tokens = tokenize_words(lyrics)
    if not tokens:
        return []
    counter = Counter(tokens)
    return counter.most_common(top_n)


def detect_themes(lyrics: str) -> List[Dict[str, Any]]:
    """
    Identify recurring themes by matching semantic keyword vectors against lyrics tokens.
    Returns ranked theme scores.
    """
    tokens = tokenize_words(lyrics)
    token_counter = Counter(tokens)
    total_tokens = max(1, len(tokens))

    theme_scores = []
    for theme, keywords in THEME_LEXICON.items():
        matched_words = []
        score = 0
        for kw in keywords:
            count = token_counter.get(kw, 0)
            if count > 0:
                matched_words.append(f"{kw} ({count})")
                score += count * 2.0  # Weight matches

        # Also search for partial stem/lemmatized stems
        for token in tokens:
            for kw in keywords:
                if len(kw) > 4 and kw in token and kw not in matched_words:
                    score += 0.5

        normalized_score = min(1.0, score / (total_tokens * 0.15 + 1.0))
        if score > 0:
            theme_scores.append({
                "theme": theme,
                "score": round(normalized_score * 100, 1),
                "matches": matched_words[:5]
            })

    # Sort descending by score
    theme_scores.sort(key=lambda x: x["score"], reverse=True)
    return theme_scores[:5]


def analyze_sentiment(lyrics: str) -> Dict[str, Any]:
    """
    Perform VADER sentiment analysis on the song lyrics.
    Returns polarity metrics, compound score, and sentiment label.
    """
    clean_text = clean_lyrics(lyrics)
    if not clean_text:
        return {
            "compound": 0.0,
            "pos": 0.0,
            "neu": 1.0,
            "neg": 0.0,
            "sentiment": "Neutral",
            "valence_description": "Neutral lyrical content"
        }

    if _vader is not None:
        scores = _vader.polarity_scores(lyrics)
    else:
        # Fallback simple rule-based polarity counter
        pos_words = {"love", "good", "happy", "sun", "smile", "joy", "peace", "light", "bright", "soar", "champion"}
        neg_words = {"sad", "rain", "tears", "dark", "lonely", "broken", "pain", "hollow", "grief", "die", "storm"}
        tokens = tokenize_words(lyrics)
        p_c = sum(1 for w in tokens if w in pos_words)
        n_c = sum(1 for w in tokens if w in neg_words)
        total = max(1, p_c + n_c)
        comp = (p_c - n_c) / total
        scores = {
            "compound": round(comp, 3),
            "pos": round(p_c / total, 3),
            "neu": 0.5,
            "neg": round(n_c / total, 3)
        }

    compound = scores["compound"]
    if compound >= 0.35:
        sentiment = "Positive"
        desc = "High positive valence with optimistic and uplifting emotional tones."
    elif compound <= -0.35:
        sentiment = "Negative"
        desc = "Strong negative valence with melancholic, conflicted, or sorrowful tones."
    else:
        sentiment = "Neutral / Mixed"
        desc = "Balanced or nuanced emotional polarity with contrasting emotional layers."

    return {
        "compound": round(compound, 3),
        "pos": round(scores["pos"], 3),
        "neu": round(scores["neu"], 3),
        "neg": round(scores["neg"], 3),
        "sentiment": sentiment,
        "valence_description": desc
    }


def analyze_lyrics_full(raw_lyrics: str) -> Dict[str, Any]:
    """
    Orchestrates complete lyrics analysis pipeline:
    - Preprocessing and tokenization
    - Structural section parsing
    - Keyword frequency
    - Theme detection
    - VADER sentiment metrics
    - Lexical statistics
    """
    if not raw_lyrics or not raw_lyrics.strip():
        return {"error": "Empty lyrics provided"}

    tokens = tokenize_words(raw_lyrics)
    total_words = len(raw_lyrics.split())
    unique_words = len(set(tokens))
    lexical_diversity = round(unique_words / max(1, len(tokens)), 3)

    sections = parse_song_sections(raw_lyrics)
    keywords = extract_keywords(raw_lyrics, top_n=12)
    themes = detect_themes(raw_lyrics)
    sentiment = analyze_sentiment(raw_lyrics)

    return {
        "raw_lyrics": raw_lyrics,
        "total_words": total_words,
        "token_count": len(tokens),
        "unique_words": unique_words,
        "lexical_diversity": lexical_diversity,
        "sections": sections,
        "section_count": len(sections),
        "keywords": keywords,
        "themes": themes,
        "sentiment": sentiment
    }
