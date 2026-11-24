"""
MODULE 6: CINEMATIC COLOR PALETTE GENERATOR
===========================================
Generates tailored, aesthetically cohesive color swatches with HEX codes,
color names, and cinematographic color-theory justifications based on scene emotion,
lighting atmosphere, and musical narrative arc.
"""

from typing import Dict, List, Any

# Curated cinematic palettes by emotion / mood
EMOTIONAL_COLOR_SYSTEM = {
    "Sadness": [
        {"name": "Midnight Indigo", "hex": "#0f172a", "role": "Dominant Shadow", "reason": "Evokes deep isolation and nocturnal sorrow."},
        {"name": "Muted Slate Grey", "hex": "#475569", "role": "Midtone Environment", "reason": "Symbolizes emotional numbness and rainy pavement."},
        {"name": "Melancholy Violet", "hex": "#3b0764", "role": "Secondary Tone", "reason": "Adds tragic poetic weight and grief."},
        {"name": "Frosted Mist", "hex": "#94a3b8", "role": "Diffused Highlight", "reason": "Diffused cold overcast illumination on glass."},
        {"name": "Raindrop Charcoal", "hex": "#1e293b", "role": "Accent Contrast", "reason": "Creates oppressive, claustrophobic depth."}
    ],
    "Love": [
        {"name": "Blush Rose", "hex": "#f43f5e", "role": "Hero Accent", "reason": "Embodies tenderness, heartbeat, and vulnerable intimacy."},
        {"name": "Velvet Crimson", "hex": "#be123c", "role": "Passionate Midtone", "reason": "Infuses deep commitment and emotional romance."},
        {"name": "Champagne Gold", "hex": "#fef08a", "role": "Warm Ambient", "reason": "Simulates golden-hour sunlight across skin."},
        {"name": "Candlelight Amber", "hex": "#d97706", "role": "Atmospheric Glow", "reason": "Flickering warm sanctuary lighting."},
        {"name": "Nocturne Plum", "hex": "#4a044e", "role": "Soft Shadow", "reason": "Velvety evening shadow anchoring the warmth."}
    ],
    "Happiness": [
        {"name": "Vibrant Sunflower", "hex": "#eab308", "role": "Primary Sunlight", "reason": "Radiates uninhibited joy, optimism, and warmth."},
        {"name": "Tangerine Glow", "hex": "#f97316", "role": "Dynamic Accent", "reason": "Adds infectious festive warmth and playfulness."},
        {"name": "Spring Mint", "hex": "#22c55e", "role": "Environmental Vitality", "reason": "Represents flourishing nature and youthful freedom."},
        {"name": "Cerulean Blue", "hex": "#38bdf8", "role": "Sky Highlight", "reason": "Unclouded summer expanse overhead."},
        {"name": "Sun-Bleached Cream", "hex": "#fef3c7", "role": "Soft Bounce", "reason": "Gentle airy fill preventing harsh shadows."}
    ],
    "Anger": [
        {"name": "Obsidian Black", "hex": "#09090b", "role": "Absolute Shadow", "reason": "Conveys unyielding oppression and grim defiance."},
        {"name": "Volcanic Crimson", "hex": "#dc2626", "role": "Hero Threat", "reason": "Visualizes blistering adrenaline, fury, and blood."},
        {"name": "Molten Orange", "hex": "#ea580c", "role": "Sparks & Flare", "reason": "Emulates sparks flying from iron, ignition of conflict."},
        {"name": "Gunmetal Grey", "hex": "#71717a", "role": "Industrial Midtone", "reason": "Evokes cold steel, weapons, and harsh urban decay."},
        {"name": "Combustion Ember", "hex": "#b91c1c", "role": "Core Glow", "reason": "Internal smoldering resentment and tension."}
    ],
    "Fear": [
        {"name": "Abyssal Black", "hex": "#020617", "role": "Deep Abyss", "reason": "Total darkness concealing lurking threats."},
        {"name": "Eerie Neon Teal", "hex": "#064e3b", "role": "Cold Ambient", "reason": "Uncanny, sickly fluorescent tint evoking hospital terror."},
        {"name": "Surveillance Cyan", "hex": "#0e7490", "role": "Clinical Edge", "reason": "Piercing laser or CCTV monitors in dark alleys."},
        {"name": "Corridor Slate", "hex": "#334155", "role": "Concrete Walls", "reason": "Damp industrial surfaces closing in on protagonist."},
        {"name": "Blinking Warning Red", "hex": "#991b1b", "role": "Emergency Alarm", "reason": "Subliminal panic trigger in high-stakes escape."}
    ],
    "Hope": [
        {"name": "Dawn Auroral Gold", "hex": "#f59e0b", "role": "Rising Sun", "reason": "Signals triumphant transition from darkness to renewal."},
        {"name": "Ethereal Pearl", "hex": "#fef9c3", "role": "Heavenly Highlight", "reason": "Pure volumetric light shafts breaking through clouds."},
        {"name": "Horizon Sapphire", "hex": "#2563eb", "role": "Boundless Future", "reason": "Expansive sky promising liberation and victory."},
        {"name": "Resilient Jade", "hex": "#10b981", "role": "Life Rebirth", "reason": "Growth, endurance, and healing after trial."},
        {"name": "Twilight Cobalt", "hex": "#1e3a8a", "role": "Fading Past", "reason": "The receding darkness of defeated obstacles."}
    ],
    "Nostalgia": [
        {"name": "Sepia Parchment", "hex": "#78350f", "role": "Vintage Grain", "reason": "Simulates aged 35mm film stock and cherished memory."},
        {"name": "Autumn Wheat", "hex": "#fde68a", "role": "Fading Sunlight", "reason": "Gentle, bittersweet golden memories of childhood."},
        {"name": "Wilted Burgundy", "hex": "#831843", "role": "Emotional Stain", "reason": "The lingering beauty of love that has passed."},
        {"name": "Weathered Linen", "hex": "#f5f5f4", "role": "Antique Canvas", "reason": "Dusty air in an old attic room filled with letters."},
        {"name": "Burnished Bronze", "hex": "#b45309", "role": "Keepsake Polish", "reason": "Patina of vintage watches, lockets, and instruments."}
    ],
    "Loneliness": [
        {"name": "Empty Charcoal", "hex": "#18181b", "role": "Solitary Room", "reason": "Oppressive silence within four bare walls."},
        {"name": "Desolate Steel", "hex": "#334155", "role": "Cold Concrete", "reason": "Distance separating the character from humanity."},
        {"name": "Pale Arctic Cyan", "hex": "#bae6fd", "role": "Hypothermic Glow", "reason": "Chilling blue moonlight falling across empty sheets."},
        {"name": "Frosted Glaze", "hex": "#cbd5e1", "role": "Reflective Pane", "reason": "Looking out at the world without touching it."},
        {"name": "Void Abyss", "hex": "#09090b", "role": "Neglected Corner", "reason": "Unfilled emotional vacuum."}
    ],
    "Excitement": [
        {"name": "Hyper Magenta", "hex": "#d946ef", "role": "Strobe Flash", "reason": "Intense kinetic neon energy bursting on screen."},
        {"name": "Ultraviolet Beam", "hex": "#8b5cf6", "role": "Club Rhythm", "reason": "Pulsing nightclub glow driving the groove."},
        {"name": "Laser Cyan", "hex": "#06b6d4", "role": "Electric Spark", "reason": "High-velocity motion trails and strobe cuts."},
        {"name": "Neon Lime", "hex": "#84cc16", "role": "Adrenaline Rush", "reason": "Unfiltered youthful rebellion and dance energy."},
        {"name": "Deep Rave Navy", "hex": "#1e1b4b", "role": "Bass Depth", "reason": "Subwoofer darkness contrasting neon highlights."}
    ]
}


def get_palette_for_emotion(emotion: str) -> List[Dict[str, str]]:
    """
    Retrieve structured 5-color palette for a given emotion.
    Defaults to Hope/Harmonic if emotion is unrecognized.
    """
    emotion_clean = emotion.strip().title()
    if emotion_clean in EMOTIONAL_COLOR_SYSTEM:
        return EMOTIONAL_COLOR_SYSTEM[emotion_clean]
    
    # Check partial match
    for key in EMOTIONAL_COLOR_SYSTEM.keys():
        if key.lower() in emotion.lower():
            return EMOTIONAL_COLOR_SYSTEM[key]

    # Default balanced cinematic palette
    return EMOTIONAL_COLOR_SYSTEM["Hope"]


def get_hex_codes_for_emotion(emotion: str) -> List[str]:
    """Return bare list of HEX string codes."""
    palette = get_palette_for_emotion(emotion)
    return [c["hex"] for c in palette]
