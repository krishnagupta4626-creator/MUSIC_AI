"""
MODULE 5: AI STORYBOARD & CINEMATIC NARRATIVE GENERATOR
=======================================================
Transforms musical and lyrical analysis into an interconnected, continuous,
scene-by-scene cinematic music-video storyboard.

Features:
- Adapts to actual song sections (Intro, Verse, Chorus, Bridge, Outro)
- Continuous narrative character and setting arcs
- Multi-field scene specifications (Title, Timestamp, Location, Characters, Description)
- Integrated Camera, Lighting, Color Palette, and AI Image Generation Prompts
- Dual-mode architecture:
  1. Generative AI Engine via Google Gemini API (when GEMINI_API_KEY is available)
  2. High-Fidelity Offline Intelligent Cinematic Script Engine (offline fallback)
"""

import os
import json
import re
from typing import Dict, List, Any, Optional

from modules.color_generator import get_palette_for_emotion, get_hex_codes_for_emotion
from modules.camera_generator import recommend_cinematography


def format_timestamp(start_sec: float, end_sec: float) -> str:
    """Format seconds into 'mm:ss - mm:ss (XXs)' format."""
    s_m, s_s = int(start_sec // 60), int(start_sec % 60)
    e_m, e_s = int(end_sec // 60), int(end_sec % 60)
    duration = int(end_sec - start_sec)
    return f"{s_m:02d}:{s_s:02d} - {e_m:02d}:{e_s:02d} ({duration}s)"


def build_image_prompt(
    scene_title: str,
    visual_description: str,
    location: str,
    lighting: str,
    shot_type: str,
    dominant_emotion: str,
    palette_hexes: List[str]
) -> str:
    """
    Construct a prompt optimized for Midjourney v6 / Flux / Stable Diffusion XL.
    """
    color_hint = ", ".join(palette_hexes[:3])
    prompt = (
        f"Cinematic 35mm film still of {scene_title}. {visual_description}. "
        f"Location: {location}. Shot on {shot_type}, anamorphic lens, {lighting}. "
        f"Color grading palette inspired by {color_hint}. Mood: {dominant_emotion}. "
        f"Photorealistic, 8k resolution, volumetric atmosphere, masterpiece, cinematic color grade --ar 16:9 --style raw"
    )
    return prompt


# ---------------------------------------------------------------------------
# OFFLINE INTELLIGENT CINEMATIC SCRIPT ENGINE (ROBUST RULE-BASED STORYTELLER)
# ---------------------------------------------------------------------------

OFFLINE_NARRATIVE_TEMPLATES = {
    "Romantic": {
        "protagonists": "Elena (a thoughtful ceramic artisan) and Mateo (a vintage book conservator)",
        "world": "A sun-bleached coastal Mediterranean town, terracotta rooftops, and a quiet seaside pottery workshop",
        "story_arc": [
            {
                "title": "Amber Tides of Memory",
                "desc": "Wide view of the rugged coastline at sunset. Elena sits on a weathered wooden dock with clay on her hands, watching the tide roll in while clutching an unsent parchment letter. A gentle sea breeze catches her scarf.",
                "action": "A lone silhouette walks along the distant sandbar, holding a brass pocket watch.",
                "emotion": "Nostalgia",
                "env": "Weathered coastal dock overlooking sea at golden hour"
            },
            {
                "title": "Unspoken Recognition",
                "desc": "Inside Mateo's seaside bookshop, warm light filters through dust motes. Mateo looks up as a wind chime sounds. Elena enters out of the sudden evening breeze. Their eyes lock in quiet, breath-catching recognition.",
                "action": "Mateo gently sets down his magnifying glass and steps around the antique oak counter.",
                "emotion": "Love",
                "env": "Antique seaside bookstore filled with leather-bound volumes and amber lanterns"
            },
            {
                "title": "The Golden Shelter",
                "desc": "They walk together along the surf under an enormous rose-gold horizon. Elena points out constellations appearing in the twilight sky. Mateo smiles, draping his woolen jacket over her shoulders as waves lap softly at their boots.",
                "action": "Their hands brush against each other and clasp tightly, banishing the cold.",
                "emotion": "Love",
                "env": "Secluded silver beach beneath a sprawling sunset canopy"
            },
            {
                "title": "Shadows of Uncertainty",
                "desc": "Later that evening, dark storm clouds billow on the maritime horizon. Elena sits by a flickering fireplace in her studio, hesitating before an unfinished sculpture of intertwined hands. Mateo watches from the open arched doorway, steady and present.",
                "action": "Mateo reaches out, his palm resting over hers on the damp clay, sharing the creative burden.",
                "emotion": "Hope",
                "env": "Artisan pottery studio with kiln embers and rainwater running down stained-glass windows"
            },
            {
                "title": "The Tempest and the Beacon",
                "desc": "A sudden coastal squall batters the shoreline cliffs. Elena and Mateo climb the winding stone steps of the town's old decommissioned lighthouse to secure the iron storm shutters together amidst swirling wind and sea spray.",
                "action": "Surrounded by wind, Mateo pulls Elena close into a protective, fiercely devoted embrace.",
                "emotion": "Love",
                "env": "Vintage lighthouse balcony amidst driving rain and flashing maritime lightning"
            },
            {
                "title": "Eternal Horizon",
                "desc": "The storm clears instantly into an ethereal dawn. Pristine turquoise water glistens under breaking sunbeams. Elena and Mateo stand together on the wet cliff-top overlook, smiling as fishing dories set sail into the gleaming new day.",
                "action": "Elena rests her head on Mateo's shoulder as the camera sweeps out across the boundless ocean.",
                "emotion": "Happiness",
                "env": "Lush emerald coastal headland overlooking an expanse of radiant sunrise ocean"
            },
            {
                "title": "Whispers in the Amber Light",
                "desc": "Elena and Mateo sit on the stone porch of the studio, laughing together over two steaming cups of coffee as the morning sun casts long golden stripes across their intertwined fingers.",
                "action": "The frame slowly dissolves as the gentle tide recedes into the distance.",
                "emotion": "Love",
                "env": "Sunny stone terrace surrounded by blooming bougainvillea overlooking calm bay"
            }
        ]
    },
    "Sad": {
        "protagonists": "Julian (a solitary violinist) and the lingering phantom memory of Sophia",
        "world": "A rainy, neo-gothic metropolis in late autumn; cobblestone streets, foggy bridges, and an abandoned concert hall",
        "story_arc": [
            {
                "title": "The Phantom on the Windowpane",
                "desc": "Rain lashes against a high arched studio window in a quiet apartment. Julian stands motionless with his back to the camera, his hand resting on the icy glass. Outside, blurred city streetlights bleed into the grey overcast sky.",
                "action": "He traces a solitary droplet slowly cascading down the cold pane.",
                "emotion": "Sadness",
                "env": "Dimly lit Victorian apartment with rain streaks on tall windows"
            },
            {
                "title": "Echoes in the Empty Hallway",
                "desc": "Julian walks down a long, dimly lit corridor where dust motes drift like snow. On a side table rests an untouched violin case and two porcelain teacups, one filled with cold, black tea.",
                "action": "He pauses, staring at a coat hook still bearing an empty winter scarf.",
                "emotion": "Loneliness",
                "env": "Shadowed apartment corridor with faded floral wallpaper and ticking wall clock"
            },
            {
                "title": "Lost in the Falling Rain",
                "desc": "Julian wanders onto a desolate iron suspension bridge. Rain pours mercilessly over his dark overcoat. In the passing headlights of distant cars, the translucent, ethereal memory of Sophia appears across the bridge before vanishing into mist.",
                "action": "Julian reaches out into the empty air, clenching his fist as the vision dissolves.",
                "emotion": "Sadness",
                "env": "Gothic suspension bridge over a dark, churning river shrouded in heavy fog"
            },
            {
                "title": "The Faded Gallery",
                "desc": "Inside an abandoned greenhouse conservatory where vines climb shattered glass panes. Julian uncovers a wooden chest filled with sepia photographs and old concert programs from performances they played together.",
                "action": "He picks up a single photograph; a single tear falls, staining the dry paper.",
                "emotion": "Nostalgia",
                "env": "Overgrown conservatory with rain falling through broken glass roof"
            },
            {
                "title": "The Unheard Crescendo",
                "desc": "Julian stands on the empty stage of a decayed theater. He lifts his violin to his chin and draws the bow across the strings with agonizing emotional intensity. Phantom spotlights flicker on, illuminating rows of velvet seats occupied only by dust.",
                "action": "His playing reaches a passionate, weeping crescendo as his eyes shut tightly in grief.",
                "emotion": "Sadness",
                "env": "Grand abandoned concert hall with peeling gold leaf and broken chandeliers"
            },
            {
                "title": "The Silent River",
                "desc": "Julian walks slowly down stone river steps in the pouring dusk. He gently places a small bouquet of white lilies onto the dark, reflective river current and watches them drift away under the iron bridge.",
                "action": "He lets out a long breath, releasing the knot of anguish in his chest.",
                "emotion": "Sadness",
                "env": "Stone embankment beside swollen urban river at twilight"
            },
            {
                "title": "Solitude in the Mist",
                "desc": "The rain subsides into a quiet, cold mist. Julian walks away down an endless cobblestone avenue, his dark figure fading gradually into the blue-grey fog as the streetlamps flicker softly.",
                "action": "The screen slowly darkens to black as the final violin resonance decays.",
                "emotion": "Loneliness",
                "env": "Empty winding European alleyway cloaked in dense blue twilight fog"
            }
        ]
    },
    "Happy": {
        "protagonists": "Leo and Maya (two free-spirited mural artists)",
        "world": "A bustling, vibrant summer city filled with open-air bazaars, colorful streetcars, rooftop gardens, and carnival lights",
        "story_arc": [
            {
                "title": "Morning Burst",
                "desc": "Maya throws open oversized wooden shutters on a sun-drenched second-story loft. Warm morning sunlight floods the room. On the street below, bicycle bells chime and fruit vendors arrange vibrant oranges and watermelons.",
                "action": "Maya tosses a paint roller down to Leo, who catches it with a triumphant grin.",
                "emotion": "Happiness",
                "env": "Bohemian loft window overlooking a bustling, cobblestone sunlit avenue"
            },
            {
                "title": "The Avenue in Motion",
                "desc": "Leo and Maya skate through a bustling open-air street bazaar. Children run beside them with colorful pinwheels. A brass street band bursts into a punchy brass groove on a street corner as locals begin clapping along.",
                "action": "Maya grabs a bouquet of sunflowers and spins Leo around in an impromptu street waltz.",
                "emotion": "Excitement",
                "env": "Vibrant market plaza with hanging paper lanterns and festive crowds"
            },
            {
                "title": "The Sunburst Canvas",
                "desc": "They arrive at a colossal grey concrete wall in the town square. With ecstatic energy, they launch buckets of yellow, cyan, and magenta paint across the wall, transforming the drab masonry into a glorious soaring phoenix mural.",
                "action": "A crowd of passersby joins in, leaving colorful handprints across the base.",
                "emotion": "Happiness",
                "env": "Sunlit public plaza with a monumental public wall mural in progress"
            },
            {
                "title": "Lemonade and Confetti",
                "desc": "Maya and Leo take a break on the curb, sipping chilled sparkling lemonade from mason jars with paint smudges on their cheeks. Maya blows a handful of golden confetti toward the camera with a joyful burst of laughter.",
                "action": "Leo takes a vintage Polaroid photo of her mid-laugh as the paper flutter catches the sun.",
                "emotion": "Happiness",
                "env": "Curb beside vibrant fruit stalls shaded by broad yellow canvas umbrellas"
            },
            {
                "title": "Rooftop Fiesta",
                "desc": "Late afternoon on a sprawling rooftop garden strung with fairy lights. Dozens of friends and neighbors have gathered, dancing to infectious indie-funk music while enjoying watermelon slices and dancing in the golden breeze.",
                "action": "Maya and Leo climb atop a bench, leading the whole rooftop in synchronized rhythm.",
                "emotion": "Excitement",
                "env": "Lush rooftop oasis overlooking a sparkling city skyline at sunset"
            },
            {
                "title": "Carnival under the Stars",
                "desc": "Night falls and a giant vintage Ferris wheel in the adjoining carnival park illuminates in electric neon teal and amber. Maya and Leo ride in a swinging cabin high above the glowing festival, looking down at the dancing crowds.",
                "action": "They high-five in celebration as fireworks explode in radiant pink bursts in the sky.",
                "emotion": "Happiness",
                "env": "High ferris wheel carriage surrounded by festival fireworks and neon lights"
            },
            {
                "title": "Dancing into Dawn",
                "desc": "Maya and Leo run hand-in-hand down an empty boulevard showered in colorful leftover confetti under starry skies, their laughter echoing cheerfully between the buildings as street sweepers smile in the dawn.",
                "action": "They leap into the air together as the freeze-frame catches their euphoric silhouettes.",
                "emotion": "Happiness",
                "env": "Wide metropolitan avenue at blue hour illuminated by vintage streetlamps"
            }
        ]
    },
    "Motivational": {
        "protagonists": "Kael (an injured marathon runner and ironworker)",
        "world": "A gritty industrial city of ironworks, steel bridges, steep uphill mountain roads, and stormy training grounds",
        "story_arc": [
            {
                "title": "Sparks in the Ruin",
                "desc": "Inside a massive iron foundry. Showers of orange molten sparks spray across Kael's soot-streaked face. He looks down at his scarred knee, remembering a brutal track collapse from the past season.",
                "action": "He tightens his grip on the heavy steel tongs, jaw set with steely determination.",
                "emotion": "Anger",
                "env": "Industrial steel mill glowing with molten furnace heat and dark shadows"
            },
            {
                "title": "The Solitary Grind",
                "desc": "Pre-dawn rain at 4:30 AM. Kael laces his weathered running shoes in a bare brick locker room. The fluorescent bulb overhead hums. Through the barred window, cold rain beats against the asphalt.",
                "action": "He slaps his legs, takes a deep breath of frosty air, and sprints out into the storm.",
                "emotion": "Hope",
                "env": "Underground concrete athletic facility and rain-slicked stadium tunnel"
            },
            {
                "title": "Rise Above the Ashes",
                "desc": "Kael runs up a punishing industrial incline beneath colossal steel suspension bridges. His breath fogs in the freezing morning air. Pain flares in his legs, but his stride accelerates with ferocious rhythm.",
                "action": "He passes a billboard showing his previous defeat and surges past it without looking back.",
                "emotion": "Hope",
                "env": "Steep urban incline alongside roaring freight trains and iron bridges"
            },
            {
                "title": "Breaking the Threshold",
                "desc": "Kael trains on an abandoned gravel quarry track under driving rain. His trainer flashes a stopwatch showing record pace. Kael pushes through the wall of fatigue, his eyes burning with raw, unbroken resolve.",
                "action": "He throws off his soaked hoodie, muscles glistening with rain and sweat.",
                "emotion": "Anger",
                "env": "Muddy industrial quarry track surrounded by towering gravel heaps"
            },
            {
                "title": "The Mountain Ascent",
                "desc": "Thunder roars as Kael reaches the base of a legendary winding mountain trail known as Devil's Spine. As lightning branches across the iron-grey sky, he charges up the jagged rock steps, leaping across chasms.",
                "action": "A camera tracking at foot level captures his shoes tearing into the gravel with power.",
                "emotion": "Excitement",
                "env": "Rugged alpine crag with stormy clouds swirling around steep rocky switchbacks"
            },
            {
                "title": "The Champion Reborn",
                "desc": "Kael bursts onto the summit plateau just as the storm clouds shatter and blinding morning sun breaks across the world below. Thousands of feet below, the vast valley and shimmering city spread out before him.",
                "action": "He lets out a triumphant roar of victory, arms raised high against the radiant sun.",
                "emotion": "Hope",
                "env": "Breathtaking mountain summit overlooking endless sea of clouds pierced by gold rays"
            },
            {
                "title": "Unstoppable Horizon",
                "desc": "Kael stands at the start line of the international championship marathon. As the starter pistol fires, he surges forward into the leading pack with a calm, unstoppable smile on his face.",
                "action": "The camera cranes up into the blue sky as the thunderous cheer of the stadium echoes.",
                "emotion": "Hope",
                "env": "Packed Olympic stadium with banners waving and thousands of roaring spectators"
            }
        ]
    },
    "Suspenseful": {
        "protagonists": "Agent Cole (a rogue cryptographer) and The Handler",
        "world": "A rainy cyberpunk metropolis of neon alleyways, glass skyscrapers, server farms, and surveillance drones",
        "story_arc": [
            {
                "title": "The Glitch on the Wire",
                "desc": "In a crowded underground subway terminal bathed in sickly cyan fluorescent light, Agent Cole stands near a vending machine wearing a dark trench coat. His smartwatch flashes an encrypted crimson prompt: 'CIPHER 09 COMPROMISED'.",
                "action": "Cole spots two figures in earpieces stepping onto the platform and quickly ducks into a service passage.",
                "emotion": "Fear",
                "env": "Subterranean subway corridor with flickering fluorescent tubes and steam vents"
            },
            {
                "title": "Footsteps on Wet Asphalt",
                "desc": "Cole emerges into a pouring rain-slicked alleyway surrounded by buzzing magenta and green neon signs. Overhead, a black surveillance drone pivots its searchlight across fire escapes.",
                "action": "Cole presses his back flat against an iron blast door as the searchlight beam passes an inch away.",
                "emotion": "Fear",
                "env": "Narrow neon-lit cyberpunk alleyway with overflowing dumpster bins and rain puddles"
            },
            {
                "title": "The Midnight Labyrinth",
                "desc": "Cole enters an abandoned brutalist power substation. Rows of humming server racks flash with amber LED arrays. He connects a portable decrypter device to a main terminal, watching the percentage bar tick up.",
                "action": "Footsteps crunch on broken glass behind him; he unholsters an electromagnetic dart emitter.",
                "emotion": "Fear",
                "env": "Decommissioned server vault with humming cooling fans and cobwebs over blinking consoles"
            },
            {
                "title": "The Classification Breach",
                "desc": "The terminal screen flashes: 'PROJECT CHIMERA UNLOCKED'. Blueprints of a city-wide mind-control satellite array download to Cole's drive. In the reflection of the glass monitor, a red laser sight centers on his shoulder.",
                "action": "Cole drops instantly as a silenced round shatters the computer screen into sparks.",
                "emotion": "Fear",
                "env": "Dark command console room bathed in green phosphor screen glow"
            },
            {
                "title": "Vertical Escape",
                "desc": "Cole sprints up an external metal fire escape amidst torrential rain and flashing sirens. Pursuers in tactical armor scale the opposite stairwell, muzzle flashes illuminating the foggy rain.",
                "action": "Cole leaps across an 8-foot alley chasm, catching a rusted ladder with one hand and pulling himself up.",
                "emotion": "Anger",
                "env": "Dizzying rooftop fire escape thirty stories above misty neon traffic"
            },
            {
                "title": "The Rooftop Confrontation",
                "desc": "On the skyscraper helipad during a thunderstorm. The lead operative corners Cole near the edge. Instead of surrendering, Cole reveals the flash drive has already broadcasted the encrypted files worldwide.",
                "action": "Sirens wail as news helicopter searchlights flood the roof, exposing the conspiracy live on air.",
                "emotion": "Hope",
                "env": "Wind-swept skyscraper helipad overlooking a sprawling metropolis in heavy rain"
            },
            {
                "title": "Vanished into the Neon Mist",
                "desc": "In the chaos of searchlights and sirens, Cole deploys a thermal smoke grenade. When the smoke clears, only an empty trench coat and a glowing cipher key remain on the helipad.",
                "action": "A camera pans over the city skyline as a hooded figure blends into the anonymous crowd below.",
                "emotion": "Fear",
                "env": "Crowded neon crosswalk under towering digital billboards in midnight drizzle"
            }
        ]
    }
}


def generate_offline_storyboard(
    song_title: str,
    artist_name: str,
    parsed_sections: List[Dict[str, Any]],
    dominant_mood: str,
    emotion_analysis: Dict[str, Any],
    tempo: float = 100.0,
    total_audio_duration: float = 180.0
) -> List[Dict[str, Any]]:
    """
    Intelligently generates a complete, coherent music video storyboard using
    offline cinematic screenplay templates, custom-fitted to the exact song structure.
    """
    # Select template family based on mood
    dm = dominant_mood.lower()
    if "joy" in dm or "happy" in dm or "euphor" in dm:
        mood_key = "Happy"
    elif "sad" in dm or "melanchol" in dm:
        mood_key = "Sad"
    elif "romanc" in dm or "tender" in dm or "love" in dm:
        mood_key = "Romantic"
    elif "motivat" in dm or "fierce" in dm or "triumph" in dm or "power" in dm:
        mood_key = "Motivational"
    elif "suspens" in dm or "tense" in dm or "fear" in dm or "myster" in dm:
        mood_key = "Suspenseful"
    else:
        mood_key = "Romantic"

    template_data = OFFLINE_NARRATIVE_TEMPLATES[mood_key]
    characters = template_data["protagonists"]
    story_beats = template_data["story_arc"]

    # Adapt scenes to actual parsed sections if available
    num_scenes = max(4, min(8, len(parsed_sections) if parsed_sections else 6))
    
    # Calculate scene timestamps based on total duration
    scene_duration = total_audio_duration / num_scenes
    storyboard: List[Dict[str, Any]] = []

    for i in range(num_scenes):
        start_t = i * scene_duration
        end_t = (i + 1) * scene_duration
        timestamp = format_timestamp(start_t, end_t)

        # Determine section name
        if parsed_sections and i < len(parsed_sections):
            sec_name = parsed_sections[i]["section_name"]
            lyric_snippet = parsed_sections[i]["text"][:120] + "..." if len(parsed_sections[i]["text"]) > 120 else parsed_sections[i]["text"]
        else:
            default_labels = ["Introduction", "Verse 1", "Chorus", "Verse 2", "Bridge", "Final Chorus", "Outro"]
            sec_name = default_labels[i] if i < len(default_labels) else f"Scene {i+1}"
            lyric_snippet = f"Lyrics corresponding to {sec_name}"

        # Pick beat from template, cycling smoothly
        beat = story_beats[i % len(story_beats)]
        scene_emotion = beat["emotion"]
        scene_palette = get_palette_for_emotion(scene_emotion)
        scene_hexes = [c["hex"] for c in scene_palette]

        # Get cinematography
        cinema = recommend_cinematography(
            section_name=sec_name,
            scene_emotion=scene_emotion,
            scene_index=i,
            total_scenes=num_scenes,
            tempo=tempo
        )

        # Image generation prompt
        img_prompt = build_image_prompt(
            scene_title=beat["title"],
            visual_description=beat["desc"],
            location=beat["env"],
            lighting=cinema["lighting_style"],
            shot_type=cinema["shot_type"],
            dominant_emotion=scene_emotion,
            palette_hexes=scene_hexes
        )

        scene_card = {
            "scene_number": i + 1,
            "scene_id": f"SCENE-{i+1:02d}",
            "section_name": sec_name,
            "scene_title": beat["title"],
            "timestamp": timestamp,
            "duration_seconds": round(scene_duration, 1),
            "characters": characters,
            "location": beat["env"],
            "emotional_atmosphere": f"{scene_emotion} - {beat['emotion']}",
            "visual_description": beat["desc"],
            "character_action": beat["action"],
            "lyric_excerpt": lyric_snippet,
            "color_palette": scene_palette,
            "color_hexes": scene_hexes,
            "camera_angle": cinema["shot_type"],
            "camera_movement": cinema["camera_movement"],
            "lens": cinema["lens"],
            "lighting": cinema["lighting_style"],
            "transition": cinema["transition"],
            "cinematography_rationale": cinema["cinematography_rationale"],
            "image_prompt": img_prompt
        }
        storyboard.append(scene_card)

    return storyboard


# ---------------------------------------------------------------------------
# GEMINI API INTEGRATION ENGINE
# ---------------------------------------------------------------------------

def generate_storyboard_with_gemini(
    song_title: str,
    artist_name: str,
    raw_lyrics: str,
    parsed_sections: List[Dict[str, Any]],
    dominant_mood: str,
    emotion_analysis: Dict[str, Any],
    tempo: float = 100.0,
    api_key: Optional[str] = None
) -> Optional[List[Dict[str, Any]]]:
    """
    Invokes Google Gemini API using google-genai SDK to generate custom screenplay scenes.
    Returns parsed storyboard or None if API fails/unavailable.
    """
    key = api_key or os.getenv("GEMINI_API_KEY")
    if not key or not key.strip() or key == "your_gemini_api_key_here":
        return None

    try:
        from google import genai
        client = genai.Client(api_key=key.strip())

        sections_summary = "\n".join([f"- {s['section_name']}: {s['text'][:90]}..." for s in parsed_sections[:7]])
        if not sections_summary:
            sections_summary = "Intro, Verse 1, Chorus, Verse 2, Bridge, Final Chorus, Outro"

        prompt = f"""You are an award-winning cinematic music video director and screenwriter.
Create a scene-by-scene storyboard for the song:
Title: "{song_title}"
Artist: "{artist_name or 'Independent Artist'}"
Dominant Mood: {dominant_mood}
Primary Emotion: {emotion_analysis.get('dominant_emotion', 'Poetic')}
Tempo: {tempo} BPM

Song Sections:
{sections_summary}

Full Lyrics:
{raw_lyrics[:1200]}

Generate a continuous, emotionally coherent narrative music-video storyboard containing exactly 5 to 7 scenes matching the song's actual sections.
Ensure each scene connects logically to form one continuous visual film.

Return ONLY a valid, raw JSON array of objects with the exact following keys for every scene (do not wrap in markdown or backticks):
[
  {{
    "scene_number": 1,
    "section_name": "Intro",
    "scene_title": "Descriptive Scene Title",
    "timestamp": "0:00 - 0:30 (30s)",
    "characters": "Names and descriptions of recurring characters",
    "location": "Detailed cinematic setting and weather",
    "emotional_atmosphere": "Nuanced emotional feeling",
    "visual_description": "Detailed visual action, staging, and cinematography description",
    "character_action": "Specific key action the character performs in this scene",
    "dominant_emotion": "Love | Sadness | Happiness | Anger | Fear | Hope | Nostalgia | Loneliness | Excitement",
    "camera_angle": "Wide-Angle Shot | Close-Up Shot | Extreme Close-Up | Medium Shot | Over-the-Shoulder | Aerial / Drone Shot | Dutch Angle | Low-Angle Hero Shot",
    "camera_movement": "Slow Push-In Dolly | Lateral Tracking Shot | 360-Degree Steadicam Orbit | Crane / Jib Ascending Rise | Handheld Kinetic Tremor | Static Locked-Off Frame | Whip Pan",
    "lighting": "Chiaroscuro / Low-Key Noir | Golden Hour Volumetric | Neon Noir Cyberpunk | Overcast Diffused Cool | Hard Volumetric Strobe | Intimate Candlelight Amber",
    "transition": "Match Cut | Slow Dissolve | Smash Cut | Whip Pan Blur | Light Leak / Lens Flare | Fade to Black"
  }}
]
"""
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        raw_text = response.text.strip()
        # Clean json codeblocks if wrapped
        raw_text = re.sub(r'^```json\s*|^```\s*|```$', '', raw_text, flags=re.MULTILINE).strip()
        parsed_json = json.loads(raw_text)

        if not isinstance(parsed_json, list) or len(parsed_json) == 0:
            return None

        # Enrich scenes with color palettes and prompts
        storyboard = []
        for idx, item in enumerate(parsed_json):
            emo = item.get("dominant_emotion", "Hope")
            palette = get_palette_for_emotion(emo)
            hexes = [c["hex"] for c in palette]
            shot = item.get("camera_angle", "Medium Shot")
            movement = item.get("camera_movement", "Slow Push-In Dolly")
            lighting = item.get("lighting", "Golden Hour Volumetric")
            loc = item.get("location", "Urban Landscape")
            title = item.get("scene_title", f"Scene {idx+1}")
            desc = item.get("visual_description", "")

            img_prompt = build_image_prompt(
                scene_title=title,
                visual_description=desc,
                location=loc,
                lighting=lighting,
                shot_type=shot,
                dominant_emotion=emo,
                palette_hexes=hexes
            )

            cinema_rationale = (
                f"The {shot} combined with {movement} emphasizes the {emo.lower()} emotional beat, "
                f"reinforcing character isolation and relational focus under {lighting}."
            )

            card = {
                "scene_number": idx + 1,
                "scene_id": f"SCENE-{idx+1:02d}",
                "section_name": item.get("section_name", f"Part {idx+1}"),
                "scene_title": title,
                "timestamp": item.get("timestamp", f"Scene {idx+1}"),
                "duration_seconds": 30.0,
                "characters": item.get("characters", "Protagonist"),
                "location": loc,
                "emotional_atmosphere": item.get("emotional_atmosphere", emo),
                "visual_description": desc,
                "character_action": item.get("character_action", "Steps forward into the frame."),
                "lyric_excerpt": f"Musical progression for {item.get('section_name', 'Scene')}",
                "color_palette": palette,
                "color_hexes": hexes,
                "camera_angle": shot,
                "camera_movement": movement,
                "lens": "35mm Cine Prime",
                "lighting": lighting,
                "transition": item.get("transition", "Slow Dissolve"),
                "cinematography_rationale": cinema_rationale,
                "image_prompt": img_prompt
            }
            storyboard.append(card)

        return storyboard

    except Exception:
        # Fallback to rule-based engine on any API error/rate-limit
        return None


def generate_storyboard(
    song_title: str,
    artist_name: str,
    raw_lyrics: str,
    parsed_sections: List[Dict[str, Any]],
    dominant_mood: str,
    emotion_analysis: Dict[str, Any],
    tempo: float = 100.0,
    total_audio_duration: float = 180.0,
    api_key: Optional[str] = None
) -> Tuple[List[Dict[str, Any]], str]:
    """
    Master storyboard generator function.
    Attempts Gemini API first (if key provided).
    Falls back cleanly to offline intelligent screenplay generator if API is unavailable or fails.
    
    Returns:
        (storyboard_list, generator_mode_used)
    """
    # 1. Try Gemini API
    if api_key or os.getenv("GEMINI_API_KEY"):
        ai_storyboard = generate_storyboard_with_gemini(
            song_title=song_title,
            artist_name=artist_name,
            raw_lyrics=raw_lyrics,
            parsed_sections=parsed_sections,
            dominant_mood=dominant_mood,
            emotion_analysis=emotion_analysis,
            tempo=tempo,
            api_key=api_key
        )
        if ai_storyboard and len(ai_storyboard) > 0:
            return ai_storyboard, "Gemini Generative AI Engine"

    # 2. Fallback to Offline Intelligent Narrative Engine
    offline_storyboard = generate_offline_storyboard(
        song_title=song_title,
        artist_name=artist_name,
        parsed_sections=parsed_sections,
        dominant_mood=dominant_mood,
        emotion_analysis=emotion_analysis,
        tempo=tempo,
        total_audio_duration=total_audio_duration
    )
    return offline_storyboard, "Intelligent Screenplay Narrative Engine (Offline Fallback)"
