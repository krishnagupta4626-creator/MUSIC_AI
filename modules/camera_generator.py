"""
MODULE 7: CINEMATOGRAPHY & CAMERA DIRECTION GENERATOR
=====================================================
Generates professional cinematography directions for music-video storyboards:
- Camera shot types (ELS, Wide, Medium, Close-up, ECU, Dutch, Over-the-Shoulder)
- Camera movement (Dolly, Tracking, Steadicam, Crane, Pan, Orbit, Handheld)
- Lens focal length & Depth of Field (24mm, 50mm, 85mm anamorphic, shallow bokeh)
- Lighting schemes (Chiaroscuro, Golden hour, Neon noir, Volumetric haze)
- Shot transitions (Match cut, Whip pan, Slow dissolve, Smash cut, Fade)
- Aesthetic justification linking visual grammar to the emotional narrative arc
"""

from typing import Dict, List, Any

# Cinematographic vocabulary with film grammar rules
CAMERA_SHOT_TYPES = {
    "Wide-Angle Shot": {
        "lens": "24mm or 28mm wide prime lens",
        "dof": "Deep depth-of-field, capturing extensive environmental context",
        "effect": "Establishes geographical scale, character vulnerability, or environmental grandeur."
    },
    "Close-Up Shot": {
        "lens": "85mm portrait telephoto prime",
        "dof": "Shallow depth-of-field with creamy circular background bokeh",
        "effect": "Draws audience intimately into the character's facial emotion, micro-expressions, and unspoken thoughts."
    },
    "Extreme Close-Up": {
        "lens": "100mm macro anamorphic lens",
        "dof": "Razor-thin depth-of-field focusing solely on iris, tear, or trembling hands",
        "effect": "Creates visceral, claustrophobic intensity, magnifying psychological stakes."
    },
    "Medium Shot": {
        "lens": "50mm normal lens (human eye perspective)",
        "dof": "Moderate depth-of-field balancing character posture and immediate surroundings",
        "effect": "Grounds the action, allowing natural body language, performance, and interaction to breathe."
    },
    "Over-the-Shoulder Shot": {
        "lens": "50mm or 85mm lens with character shoulder softly blurred in foreground",
        "dof": "Soft foreground bokeh, crisp focus on counterpart or focal horizon",
        "effect": "Establishes relational distance, tension, or confrontation between two entities."
    },
    "Aerial / Drone Shot": {
        "lens": "Ultra-wide 16mm cine lens on gyroscopic gimbal",
        "dof": "Infinite focus across vast landscape or sprawling city grid",
        "effect": "Provides god's-eye perspective, symbolizing existential isolation, destiny, or boundless freedom."
    },
    "Dutch Angle": {
        "lens": "35mm cine lens tilted 15 to 25 degrees off horizontal axis",
        "dof": "Moderate depth with diagonal horizon lines",
        "effect": "Subconsciously signals psychological disorientation, unease, danger, or unraveling reality."
    },
    "Low-Angle Hero Shot": {
        "lens": "28mm wide lens positioned near floor looking upward",
        "dof": "Deep focus framing subject towering against sky or ceiling lights",
        "effect": "Endows the protagonist with overwhelming power, triumph, resilience, and monumental authority."
    }
}

CAMERA_MOVEMENTS = {
    "Slow Push-In Dolly": {
        "description": "Camera glides forward on precision track directly toward the subject",
        "effect": "Gradually intensifies dramatic focus, signaling an internal realization or rising emotional intimacy."
    },
    "Lateral Tracking Shot": {
        "description": "Camera moves parallel alongside the character as they walk or run",
        "effect": "Imparts dynamic forward momentum, emphasizing an ongoing physical or emotional journey."
    },
    "360-Degree Steadicam Orbit": {
        "description": "Camera continuously circles around the character in a smooth fluid revolution",
        "effect": "Conveys feeling lost in time, overwhelming romance, or sudden revelation as the world spins around."
    },
    "Crane / Jib Ascending Rise": {
        "description": "Camera swoops upward vertically from character level into the high rafters or open sky",
        "effect": "Signals dramatic climax, liberation, spiritual release, or the concluding catharsis of an era."
    },
    "Handheld Kinetic Tremor": {
        "description": "Camera operator holds rig with organic slight shake and spontaneous adjustments",
        "effect": "Injects raw documentary realism, chaotic urgency, panic, or adrenaline-fueled kinetic grit."
    },
    "Static Locked-Off Frame": {
        "description": "Camera mounted immovably on heavy tripod with zero pan or tilt",
        "effect": "Emphasizes oppressive stillness, clinical detachment, or patient emotional observation of sorrow."
    },
    "Whip Pan": {
        "description": "Extremely fast blurred rotation of the camera from one point of interest to another",
        "effect": "Creates energetic, disorienting shock transitions matching sudden musical drop or percussive accents."
    }
}

LIGHTING_STYLES = {
    "Chiaroscuro / Low-Key Noir": "High-contrast lighting with deep, impenetrable shadows, sharp single key light, and rim separation.",
    "Golden Hour Volumetric": "Warm low-angle sun casting long amber shadows, dust motes floating in visible golden light shafts.",
    "Neon Noir Cyberpunk": "Vibrant contrasting practicals (cyan, magenta, amber) reflecting on wet asphalt under dark murky skies.",
    "Overcast Diffused Cool": "Soft shadowless silver daylight filtered through heavy cloud cover, creating a melancholic flat palette.",
    "Hard Volumetric Strobe": "Pulsing beams of concert-grade spotlights cutting through dense atmospheric stage haze.",
    "Intimate Candlelight Amber": "Soft flickering point sources illuminating warm skin tones against deep velvety room shadows."
}

TRANSITIONS = [
    "Match Cut (linking visual shape or motion between outgoing and incoming scene)",
    "Slow Dissolve (gentle 2-second cross-fade blending memories together)",
    "Smash Cut (instantaneous hard cut on loud beat drop for sudden shock)",
    "Whip Pan Blur (kinetic horizontal swish into the subsequent environment)",
    "Light Leak / Lens Flare (golden anamorphic flare obscuring frame to reveal new dawn)",
    "Fade to Black (gradual darkening leaving lingering emotional resonance)"
]


def recommend_cinematography(
    section_name: str,
    scene_emotion: str,
    scene_index: int,
    total_scenes: int,
    tempo: float = 100.0
) -> Dict[str, Any]:
    """
    Synthesize complete cinematography recommendations tailored to the emotional beat
    and structural position in the music video.
    """
    sec_lower = section_name.lower()
    emo_lower = scene_emotion.lower()

    # Determine Shot Type
    if scene_index == 0 or "intro" in sec_lower:
        shot_type = "Wide-Angle Shot" if "love" not in emo_lower else "Aerial / Drone Shot"
    elif "chorus" in sec_lower:
        if "anger" in emo_lower or "motivat" in emo_lower:
            shot_type = "Low-Angle Hero Shot"
        elif "happy" in emo_lower or "excite" in emo_lower:
            shot_type = "Wide-Angle Shot"
        elif "sad" in emo_lower or "lonel" in emo_lower:
            shot_type = "Close-Up Shot"
        else:
            shot_type = "Medium Shot"
    elif "bridge" in sec_lower:
        if "suspense" in emo_lower or "fear" in emo_lower:
            shot_type = "Dutch Angle"
        elif "sad" in emo_lower:
            shot_type = "Extreme Close-Up"
        else:
            shot_type = "Close-Up Shot"
    elif scene_index == total_scenes - 1 or "outro" in sec_lower:
        shot_type = "Aerial / Drone Shot" if "hope" in emo_lower or "happy" in emo_lower else "Wide-Angle Shot"
    elif "verse 2" in sec_lower:
        shot_type = "Over-the-Shoulder Shot"
    else:
        shot_type = "Medium Shot"

    # Determine Camera Movement
    if tempo > 125:
        movement = "Handheld Kinetic Tremor" if "anger" in emo_lower else "Lateral Tracking Shot"
    elif tempo < 75:
        movement = "Slow Push-In Dolly" if "love" in emo_lower else "Static Locked-Off Frame"
    elif "bridge" in sec_lower:
        movement = "360-Degree Steadicam Orbit"
    elif "outro" in sec_lower:
        movement = "Crane / Jib Ascending Rise"
    else:
        movement = "Slow Push-In Dolly"

    # Determine Lighting Style
    if "love" in emo_lower or "romanc" in emo_lower:
        lighting = "Golden Hour Volumetric" if scene_index % 2 == 0 else "Intimate Candlelight Amber"
    elif "sad" in emo_lower or "lonel" in emo_lower:
        lighting = "Overcast Diffused Cool" if scene_index % 2 == 0 else "Chiaroscuro / Low-Key Noir"
    elif "fear" in emo_lower or "suspense" in emo_lower:
        lighting = "Neon Noir Cyberpunk"
    elif "anger" in emo_lower or "motivat" in emo_lower:
        lighting = "Chiaroscuro / Low-Key Noir"
    elif "excite" in emo_lower:
        lighting = "Hard Volumetric Strobe"
    else:
        lighting = "Golden Hour Volumetric"

    # Determine Transition
    if scene_index == total_scenes - 1:
        transition = "Fade to Black (lingering into complete silence)"
    elif "chorus" in sec_lower or tempo > 130:
        transition = "Smash Cut (aligned with snare/drum impact)"
    elif "sad" in emo_lower or "nostalg" in emo_lower:
        transition = "Slow Dissolve (fluidly merging emotional memories)"
    elif "suspense" in emo_lower:
        transition = "Whip Pan Blur (kinetic swish into hidden alleyway)"
    else:
        transition = "Match Cut (connecting character eye-line to next location)"

    shot_meta = CAMERA_SHOT_TYPES.get(shot_type, CAMERA_SHOT_TYPES["Medium Shot"])
    movement_meta = CAMERA_MOVEMENTS.get(movement, CAMERA_MOVEMENTS["Slow Push-In Dolly"])

    rationale = (
        f"The {shot_type} ({shot_meta['lens']}) coupled with a {movement} "
        f"amplifies the scene's emotional beat of '{scene_emotion}'. "
        f"{shot_meta['effect']} {movement_meta['effect']}"
    )

    return {
        "shot_type": shot_type,
        "lens": shot_meta["lens"],
        "depth_of_field": shot_meta["dof"],
        "camera_movement": movement,
        "movement_description": movement_meta["description"],
        "lighting_style": lighting,
        "transition": transition,
        "cinematography_rationale": rationale
    }
