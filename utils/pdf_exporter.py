"""
PDF Storyboard Exporter
=======================
Generates an academic and industry-grade PDF storyboard document from the
analysis results and scene concepts using FPDF2.
"""

import io
from typing import Dict, List, Any, Optional
from fpdf import FPDF


class StoryboardPDF(FPDF):
    """Custom styled FPDF canvas for cinematic storyboard output."""
    
    def __init__(self, song_title: str, artist_name: str, dominant_mood: str):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.song_title = song_title or "Untitled Song"
        self.artist_name = artist_name or "Unknown Artist"
        self.dominant_mood = dominant_mood or "Undefined Mood"
        self.set_auto_page_break(auto=True, margin=15)
        
    def header(self):
        # Header banner on every page except page 1 if desired, but we keep a subtle line
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(140, 140, 150)
        self.cell(0, 8, f"Music-to-Visual Narrative Generator | {self.song_title} - {self.artist_name}", border=0, align="L")
        self.cell(0, 8, f"Mood: {self.dominant_mood}", border=0, align="R", new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(50, 50, 70)
        self.set_line_width(0.3)
        self.line(10, 16, 200, 16)
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(140, 140, 150)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}} | Academic Mini-Project (B.Tech AI & ML)", border=0, align="C")


def hex_to_rgb(hex_code: str) -> tuple[int, int, int]:
    """Convert HEX string like '#f43f5e' to RGB tuple (244, 63, 94)."""
    hex_clean = hex_code.lstrip("#")
    if len(hex_clean) == 6:
        return int(hex_clean[0:2], 16), int(hex_clean[2:4], 16), int(hex_clean[4:6], 16)
    return (100, 100, 120)


def generate_storyboard_pdf(
    song_title: str,
    artist_name: str,
    mood_analysis: Dict[str, Any],
    lyrics_analysis: Optional[Dict[str, Any]],
    emotion_analysis: Optional[Dict[str, Any]],
    audio_analysis: Optional[Dict[str, Any]],
    storyboard: List[Dict[str, Any]],
    generator_mode: str
) -> bytes:
    """
    Compile full storyboard and multimodal analytics into a professional PDF.
    Returns bytes buffer for Streamlit download button.
    """
    dominant_mood = mood_analysis.get("dominant_mood", "Cinematic")
    pdf = StoryboardPDF(song_title, artist_name, dominant_mood)
    pdf.alias_nb_pages()
    pdf.add_page()

    # --- TITLE SECTION ---
    pdf.set_fill_color(18, 18, 28)
    pdf.rect(10, 20, 190, 42, style="F")

    pdf.set_xy(14, 23)
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(240, 240, 255)
    pdf.cell(0, 9, f"STORYBOARD: {song_title.upper()}", new_x="LMARGIN", new_y="NEXT")

    pdf.set_x(14)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(180, 180, 210)
    pdf.cell(0, 6, f"Artist: {artist_name or 'Independent Artist'}   |   Engine: {generator_mode}", new_x="LMARGIN", new_y="NEXT")

    pdf.set_x(14)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(140, 200, 255)
    conf_pct = mood_analysis.get("confidence_percentage", 80)
    pdf.cell(0, 7, f"Dominant Mood: {dominant_mood} (Confidence: {conf_pct}%)", new_x="LMARGIN", new_y="NEXT")

    # --- EXECUTIVE SUMMARY & FUSION Math ---
    pdf.ln(8)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(40, 40, 80)
    pdf.cell(0, 7, "1. MULTIMODAL MOOD & ACOUSTIC PROFILE", new_x="LMARGIN", new_y="NEXT")
    pdf.set_draw_color(100, 100, 150)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(3)

    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(50, 50, 60)
    explanation = mood_analysis.get("explanation", "Multimodal affective inference.")
    pdf.multi_cell(0, 5, f"Analysis Summary: {explanation}")
    pdf.ln(2)

    # Key metrics row
    tempo_val = audio_analysis.get("tempo", "N/A") if audio_analysis else "N/A"
    duration_val = audio_analysis.get("duration_formatted", "N/A") if audio_analysis else "N/A"
    dominant_emo = emotion_analysis.get("dominant_emotion", "N/A") if emotion_analysis else "N/A"
    dominant_pct = emotion_analysis.get("dominant_percentage", 0) if emotion_analysis else 0
    secondary_emo = emotion_analysis.get("secondary_emotion", "N/A") if emotion_analysis else "N/A"
    sentiment_val = lyrics_analysis.get("sentiment", {}).get("sentiment", "N/A") if lyrics_analysis else "N/A"

    pdf.set_font("Helvetica", "B", 8)
    pdf.set_fill_color(240, 242, 248)
    pdf.cell(45, 6, f"Tempo: {tempo_val} BPM", border=1, fill=True)
    pdf.cell(45, 6, f"Duration: {duration_val}", border=1, fill=True)
    pdf.cell(50, 6, f"Top Emotion: {dominant_emo} ({dominant_pct}%)", border=1, fill=True)
    pdf.cell(50, 6, f"Sentiment: {sentiment_val}", border=1, fill=True, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)

    # --- SCENE-BY-SCENE STORYBOARD ---
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(40, 40, 80)
    pdf.cell(0, 7, "2. CINEMATIC SCENE-BY-SCENE STORYBOARD", new_x="LMARGIN", new_y="NEXT")
    pdf.set_draw_color(100, 100, 150)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(4)

    for scene in storyboard:
        # Check remaining space on page, add page if tight
        if pdf.get_y() > 220:
            pdf.add_page()

        # Scene Card Header Banner
        pdf.set_fill_color(30, 32, 45)
        pdf.rect(10, pdf.get_y(), 190, 8, style="F")
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(255, 255, 255)
        pdf.set_x(12)
        pdf.cell(100, 8, f"{scene['scene_id']}: {scene['scene_title'].upper()} ({scene['section_name']})")
        pdf.cell(85, 8, f"Timestamp: {scene['timestamp']}", align="R", new_x="LMARGIN", new_y="NEXT")

        pdf.set_draw_color(210, 215, 225)
        pdf.set_line_width(0.2)
        y_start = pdf.get_y()

        # Visual description
        pdf.ln(2)
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_text_color(70, 70, 90)
        pdf.cell(25, 5, "Environment:")
        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(30, 30, 40)
        pdf.cell(0, 5, f"{scene.get('location', 'Urban Studio')}", new_x="LMARGIN", new_y="NEXT")

        pdf.set_font("Helvetica", "B", 8)
        pdf.set_text_color(70, 70, 90)
        pdf.cell(25, 5, "Characters:")
        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(30, 30, 40)
        pdf.cell(0, 5, f"{scene.get('characters', 'Protagonists')}", new_x="LMARGIN", new_y="NEXT")

        pdf.set_font("Helvetica", "B", 8)
        pdf.set_text_color(70, 70, 90)
        pdf.cell(25, 5, "Atmosphere:")
        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(30, 30, 40)
        pdf.cell(0, 5, f"{scene.get('emotional_atmosphere', 'Reflective')}", new_x="LMARGIN", new_y="NEXT")

        pdf.set_font("Helvetica", "B", 8)
        pdf.set_text_color(70, 70, 90)
        pdf.cell(0, 5, "Visual Action & Narrative Staging:", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(30, 30, 40)
        pdf.multi_cell(0, 4.2, f"{scene.get('visual_description', '')} {scene.get('character_action', '')}")

        # Cinematography Details
        pdf.ln(1)
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_text_color(100, 40, 120)
        angle = scene.get("camera_angle", "Medium Shot")
        movement = scene.get("camera_movement", "Slow Push-In Dolly")
        lighting = scene.get("lighting", "Golden Hour")
        transition = scene.get("transition", "Slow Dissolve")
        pdf.cell(0, 5, f"Camera: {angle} | Move: {movement} | Lighting: {lighting}", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "I", 7.5)
        pdf.set_text_color(80, 80, 100)
        pdf.cell(0, 4, f"Transition: {transition}", new_x="LMARGIN", new_y="NEXT")

        # Color Palette Swatches
        pdf.ln(1)
        pdf.set_font("Helvetica", "B", 7.5)
        pdf.set_text_color(70, 70, 90)
        pdf.cell(24, 6, "Color Palette:")
        
        # Render colored square swatches
        palette = scene.get("color_palette", [])
        swatch_x = pdf.get_x()
        swatch_y = pdf.get_y() + 1
        for c_idx, c_info in enumerate(palette[:5]):
            r, g, b = hex_to_rgb(c_info.get("hex", "#6366f1"))
            pdf.set_fill_color(r, g, b)
            pdf.rect(swatch_x + (c_idx * 16), swatch_y, 7, 4.5, style="F")
            pdf.set_xy(swatch_x + (c_idx * 16) + 7.5, swatch_y)
            pdf.set_font("Helvetica", "", 6)
            pdf.set_text_color(60, 60, 70)
            pdf.cell(8.5, 4.5, c_info.get("hex", "#000"))

        pdf.set_xy(10, swatch_y + 6)

        # AI Prompt Block
        pdf.set_fill_color(245, 246, 250)
        pdf.set_font("Courier", "", 6.5)
        pdf.set_text_color(60, 60, 80)
        prompt_text = f"Prompt: {scene.get('image_prompt', '')}"
        pdf.multi_cell(190, 3.5, prompt_text, border=1, fill=True)

        pdf.ln(4)

    # Return raw PDF bytes
    output_bytes = pdf.output()
    return bytes(output_bytes)
