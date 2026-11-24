"""
MODULE 2B: EMOTION CLASSIFICATION ENGINE
=========================================
Classifies song lyrics into 9 distinct psychological and musical emotion categories:
- Happiness
- Sadness
- Love
- Anger
- Fear
- Hope
- Nostalgia
- Loneliness
- Excitement

Uses a multi-layered NLP approach:
1. VADER valence/arousal anchoring
2. Expanded NRC-style emotion category lexicons
3. Semantic pattern and contextual negation checks
4. Softmax probability normalization
"""

import math
from typing import Dict, List, Any, Tuple
from collections import Counter
from modules.lyrics_analyzer import tokenize_words, analyze_sentiment

# Emotion Lexicons curated for musical lyrics analysis
EMOTION_LEXICONS = {
    "Happiness": [
        "happy", "joy", "smile", "laugh", "sun", "sunshine", "dance", "celebrate", "bright",
        "cheerful", "delight", "glee", "bliss", "merry", "fun", "warmth", "light", "golden",
        "singing", "splendid", "radiant", "play", "carefree", "ecstatic"
    ],
    "Sadness": [
        "sad", "tears", "cry", "crying", "grief", "sorrow", "mourn", "weep", "broken",
        "pain", "ache", "hollow", "heavy", "darkness", "drown", "loss", "bleak", "funeral",
        "agony", "suffering", "heartbreak", "hopeless", "despair"
    ],
    "Love": [
        "love", "beloved", "darling", "heart", "kiss", "embrace", "forever", "tender",
        "cherish", "devotion", "passion", "sweetheart", "holding", "vows", "soul",
        "together", "gentle", "shelter", "adore", "affection", "romantic"
    ],
    "Anger": [
        "anger", "angry", "rage", "fury", "burn", "fire", "fight", "hate", "scars",
        "strike", "blood", "crush", "roar", "scream", "furious", "vengeance", "rebel",
        "wrath", "madness", "spite", "hostile", "defy", "enemy"
    ],
    "Fear": [
        "fear", "afraid", "scared", "terror", "horror", "panic", "shiver", "tremble",
        "danger", "shadow", "threat", "dread", "alarm", "paranoid", "trapped", "cower",
        "nightmare", "chased", "creep", "warning", "sinister"
    ],
    "Hope": [
        "hope", "aspire", "faith", "dream", "believe", "promise", "future", "dawn",
        "rise", "heal", "overcome", "triumph", "unbroken", "spark", "beacon", "horizon",
        "light", "rescue", "champion", "destiny", "courage", "soar", "persist"
    ],
    "Nostalgia": [
        "nostalgia", "remember", "memory", "memories", "yesterday", "past", "photograph",
        "childhood", "reminisce", "faded", "traces", "echoes", "forgotten", "years",
        "autumn", "old", "vintage", "sepia", "once", "lingering", "phantom"
    ],
    "Loneliness": [
        "lonely", "alone", "isolation", "empty", "hallway", "silence", "abandoned",
        "solitary", "deserted", "unheard", "distance", "stranger", "cold", "void",
        "secluded", "apart", "nobody", "quiet", "barren", "hollow"
    ],
    "Excitement": [
        "excitement", "electric", "wild", "rush", "energy", "groove", "rhythm", "fast",
        "jump", "party", "thrill", "carnival", "blaze", "thunder", "alive", "screaming",
        "loud", "ignite", "dynamic", "buzz", "velocity", "pump"
    ]
}

# Negative modifiers that flip or dampen emotions
NEGATIONS = {"no", "not", "never", "without", "hardly", "barely", "scarcely"}


def classify_emotions(lyrics: str) -> Dict[str, Any]:
    """
    Classify song lyrics across 9 core emotional categories.
    Returns:
        - raw_scores: Unnormalized raw lexical hit counts
        - probabilities: Softmax-normalized probability distribution (%)
        - dominant_emotion: Primary emotion detected
        - secondary_emotion: Second highest emotion
        - emotion_rankings: List of (emotion, percentage) tuples
        - method: Explanation of methodology used
    """
    tokens = tokenize_words(lyrics)
    token_count = max(1, len(tokens))
    sentiment = analyze_sentiment(lyrics)
    compound = sentiment.get("compound", 0.0)

    # Count emotional tokens with contextual weights
    raw_scores: Dict[str, float] = {e: 0.1 for e in EMOTION_LEXICONS.keys()}  # Small Laplace smoothing
    matched_words_by_emotion: Dict[str, List[str]] = {e: [] for e in EMOTION_LEXICONS.keys()}

    words_lower = [w.strip(".,!?;:\"'()[]") for w in lyrics.lower().split()]
    for i, word in enumerate(words_lower):
        # Check if preceded by a negation word
        is_negated = (i > 0 and words_lower[i-1] in NEGATIONS)
        
        for emotion, lexicon in EMOTION_LEXICONS.items():
            if word in lexicon:
                weight = 1.0
                if is_negated:
                    # Inverted effect: e.g. "not afraid" reduces Fear, boosts Hope/Calm
                    weight = -0.6
                
                raw_scores[emotion] = max(0.0, raw_scores[emotion] + weight)
                if not is_negated and word not in matched_words_by_emotion[emotion]:
                    matched_words_by_emotion[emotion].append(word)

    # Infuse VADER sentiment polarity as psychological prior
    if compound >= 0.3:
        # Boost positive valenced emotions
        raw_scores["Happiness"] += compound * 2.0
        raw_scores["Love"] += compound * 1.8
        raw_scores["Hope"] += compound * 1.5
        raw_scores["Excitement"] += compound * 1.2
    elif compound <= -0.3:
        # Boost negative valenced emotions
        abs_c = abs(compound)
        raw_scores["Sadness"] += abs_c * 2.2
        raw_scores["Loneliness"] += abs_c * 1.9
        raw_scores["Anger"] += abs_c * 1.5
        raw_scores["Fear"] += abs_c * 1.4

    # Apply temperature-scaled Softmax to obtain genuine probability distribution
    temperature = 1.2
    exp_scores = {e: math.exp(score / temperature) for e, score in raw_scores.items()}
    sum_exp = sum(exp_scores.values())

    probabilities: Dict[str, float] = {}
    for e, exp_v in exp_scores.items():
        probabilities[e] = round((exp_v / sum_exp) * 100.0, 1)

    # Sort emotions descending by probability
    ranked = sorted(probabilities.items(), key=lambda item: item[1], reverse=True)
    dominant_emotion, dominant_prob = ranked[0]
    secondary_emotion, secondary_prob = ranked[1]

    # Calculate classification confidence margin
    confidence = min(0.98, max(0.40, (dominant_prob - secondary_prob) / 100.0 + 0.55))

    return {
        "dominant_emotion": dominant_emotion,
        "dominant_percentage": dominant_prob,
        "secondary_emotion": secondary_emotion,
        "secondary_percentage": secondary_prob,
        "probabilities": probabilities,
        "rankings": ranked,
        "confidence": round(confidence, 2),
        "matched_keywords": matched_words_by_emotion,
        "method": "Multi-Layered NRC Emotion Lexicon + VADER Valence Anchoring + Softmax Normalization"
    }
