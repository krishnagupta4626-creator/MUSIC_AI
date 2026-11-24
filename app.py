"""
MUSIC-TO-VISUAL NARRATIVE GENERATOR
====================================
Academic Mini-Project | B.Tech Computer Science (AI & ML)
An AI-powered web application that analyzes a song's lyrics, emotions, musical characteristics,
and mood to generate a cinematic music-video concept in the form of a scene-by-scene storyboard.

Technologies: Streamlit, Librosa, NLTK, Plotly, SciPy, FPDF2, Google Gemini API
"""

import os
import sys
import io
import json
import tempfile
from typing import Dict, Any, Optional

import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv

# Ensure local modules are in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.lyrics_analyzer import analyze_lyrics_full
from modules.emotion_detector import classify_emotions
from modules.audio_analyzer import analyze_audio_file
from modules.mood_detector import detect_mood
from modules.story_generator import generate_storyboard
from utils.helpers import validate_inputs, serialize_project_state
from utils.pdf_exporter import generate_storyboard_pdf
from utils.audio_synth import generate_mood_audio, save_mood_audio_file

# Load environment variables
load_dotenv()

# Streamlit Page Config
st.set_page_config(
    page_title="Music-to-Visual Narrative Generator",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load Custom CSS
def load_css():
    css_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "style.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# Load Sample Lyrics Data
@st.cache_data
def load_sample_presets() -> Dict[str, Any]:
    json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_data", "sample_lyrics.json")
    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

presets = load_sample_presets()

# Initialize Session State
if "analysis_complete" not in st.session_state:
    st.session_state.analysis_complete = False
if "lyrics_data" not in st.session_state:
    st.session_state.lyrics_data = None
if "emotion_data" not in st.session_state:
    st.session_state.emotion_data = None
if "audio_data" not in st.session_state:
    st.session_state.audio_data = None
if "mood_data" not in st.session_state:
    st.session_state.mood_data = None
if "storyboard" not in st.session_state:
    st.session_state.storyboard = None
if "generator_mode" not in st.session_state:
    st.session_state.generator_mode = "Offline Intelligent Screenplay Engine"
if "song_title" not in st.session_state:
    st.session_state.song_title = ""
if "artist_name" not in st.session_state:
    st.session_state.artist_name = ""
if "raw_lyrics" not in st.session_state:
    st.session_state.raw_lyrics = ""
if "audio_bytes" not in st.session_state:
    st.session_state.audio_bytes = None
if "audio_filename" not in st.session_state:
    st.session_state.audio_filename = None


# -----------------------------------------------------------------------------
# SIDEBAR CONTROLS & DEMO PRESETS
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🎬 Control Deck")
    st.markdown("---")

    # API Configuration
    st.markdown("#### 🔑 AI Engine Configuration")
    user_api_key = st.text_input(
        "Google Gemini API Key (Optional)",
        type="password",
        value=os.getenv("GEMINI_API_KEY", ""),
        help="Optional: Leave blank to use the built-in Intelligent Screenplay Engine (offline rule-based system)."
    )
    if user_api_key and user_api_key.strip():
        st.caption("🟢 Gemini API mode enabled")
    else:
        st.caption("🔵 Offline Intelligent Story Engine active (No key needed)")

    st.markdown("---")

    # Quick Demo Presets for Academic Evaluation
    st.markdown("#### ⚡ 1-Click Evaluation Presets")
    st.markdown("Instantly test 5 distinct musical moods with pre-loaded lyrics and matching synthetic audio:")

    preset_choice = st.selectbox(
        "Select Test Mood Preset:",
        ["None (Custom Input)", "Romantic ('Golden Horizons')", "Sad ('Echoes of Rain')", "Happy ('Sunburst Carnival')", "Motivational ('Rise Above the Ashes')", "Suspenseful ('Midnight Labyrinth')"]
    )

    if st.button("Load Selected Preset", use_container_width=True):
        preset_key_map = {
            "Romantic ('Golden Horizons')": "romantic",
            "Sad ('Echoes of Rain')": "sad",
            "Happy ('Sunburst Carnival')": "happy",
            "Motivational ('Rise Above the Ashes')": "motivational",
            "Suspenseful ('Midnight Labyrinth')": "suspenseful"
        }
        selected_key = preset_key_map.get(preset_choice)
        if selected_key and selected_key in presets:
            item = presets[selected_key]
            st.session_state.song_title = item["title"]
            st.session_state.artist_name = item["artist"]
            st.session_state.raw_lyrics = item["lyrics"]

            # Load corresponding sample audio file
            audio_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_data", "audio", f"{selected_key}_sample.wav")
            if os.path.exists(audio_path):
                with open(audio_path, "rb") as af:
                    st.session_state.audio_bytes = af.read()
                st.session_state.audio_filename = f"{selected_key}_sample.wav"

            st.session_state.analysis_complete = False
            st.success(f"Loaded '{item['title']}' ({item['mood_category']})!")
            st.rerun()

    st.markdown("---")
    if st.button("🔄 Reset Project / Clear All", use_container_width=True):
        st.session_state.analysis_complete = False
        st.session_state.lyrics_data = None
        st.session_state.emotion_data = None
        st.session_state.audio_data = None
        st.session_state.mood_data = None
        st.session_state.storyboard = None
        st.session_state.song_title = ""
        st.session_state.artist_name = ""
        st.session_state.raw_lyrics = ""
        st.session_state.audio_bytes = None
        st.session_state.audio_filename = None
        st.rerun()

    st.markdown("---")
    st.caption("🎓 **Academic Mini-Project** | B.Tech CSE (AI & ML)\nTeam of 5 Students | 2nd Year")


# -----------------------------------------------------------------------------
# MAIN DASHBOARD TABS
# -----------------------------------------------------------------------------

# Hero Banner
st.markdown("""
<div class="hero-container">
    <div class="hero-title">MUSIC-TO-VISUAL NARRATIVE GENERATOR</div>
    <div class="hero-subtitle">
        An AI-powered multimodal platform transforming song lyrics, acoustic signals, and emotional arcs 
        into cinematic, scene-by-scene music video storyboards with professional cinematography and color direction.
    </div>
    <div class="hero-badge-container">
        <span class="hero-badge">NLP Lyrics Engine</span>
        <span class="hero-badge">Librosa Audio DSP</span>
        <span class="hero-badge">Multimodal Affective Fusion</span>
        <span class="hero-badge">Cinematic Storyboard</span>
        <span class="hero-badge">AI Image Prompts</span>
        <span class="hero-badge">PDF Export</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Main Navigation Tabs
tab_home, tab_input, tab_lyrics, tab_audio, tab_mood, tab_story, tab_export, tab_about = st.tabs([
    "🏠 Overview",
    "📝 Song Input",
    "📊 Lyrics Analysis",
    "🎵 Audio Analysis",
    "🎭 Mood Detection",
    "🎬 AI Storyboard",
    "📥 Export & Report",
    "ℹ️ About Project"
])


# -----------------------------------------------------------------------------
# TAB 1: OVERVIEW & HOME DASHBOARD
# -----------------------------------------------------------------------------
with tab_home:
    st.markdown('<div class="section-title">System Workflow & Architecture</div>', unsafe_allow_html=True)
    
    col_w1, col_w2, col_w3, col_w4 = st.columns(4)
    with col_w1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Phase 01</div>
            <div class="metric-value">Input & Ingestion</div>
            <div class="metric-sub">Accepts lyrics text & MP3/WAV audio files</div>
        </div>
        """, unsafe_allow_html=True)
    with col_w2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Phase 02</div>
            <div class="metric-value">Dual Analytics</div>
            <div class="metric-sub">NLP Sentiment/Emotions + Librosa DSP Features</div>
        </div>
        """, unsafe_allow_html=True)
    with col_w3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Phase 03</div>
            <div class="metric-value">Affective Fusion</div>
            <div class="metric-sub">Softmax multimodal mood & confidence estimation</div>
        </div>
        """, unsafe_allow_html=True)
    with col_w4:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Phase 04</div>
            <div class="metric-value">Cinematic Story</div>
            <div class="metric-sub">Scene-by-scene cinematography & prompt generation</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if st.session_state.analysis_complete and st.session_state.mood_data:
        st.markdown('<div class="section-title">Active Project Snapshot</div>', unsafe_allow_html=True)
        m = st.session_state.mood_data
        e = st.session_state.emotion_data
        a = st.session_state.audio_data
        s = st.session_state.lyrics_data

        c_snap1, c_snap2, c_snap3, c_snap4 = st.columns(4)
        with c_snap1:
            st.metric("Dominant Mood", m.get("dominant_mood", "N/A"), f"{m.get('confidence_percentage', 0)}% Conf.")
        with c_snap2:
            st.metric("Top Emotion", e.get("dominant_emotion", "N/A"), f"{e.get('dominant_percentage', 0)}% of lyrics")
        with c_snap3:
            tempo_disp = f"{a.get('tempo', 0)} BPM" if a else "No Audio"
            st.metric("Detected Tempo", tempo_disp, a.get("tempo_category", "N/A") if a else "N/A")
        with c_snap4:
            scene_cnt = len(st.session_state.storyboard) if st.session_state.storyboard else 0
            st.metric("Generated Scenes", f"{scene_cnt} Cinematic Scenes", st.session_state.generator_mode.split()[0])
        
        st.info(f"**Multimodal Explanation:** {m.get('explanation', '')}")
    else:
        st.info("💡 **Ready to Start:** Navigate to **'📝 Song Input'** tab or click one of the **1-Click Evaluation Presets** in the sidebar to load a demo song immediately.")


# -----------------------------------------------------------------------------
# TAB 2: SONG INPUT SYSTEM (MODULE 1)
# -----------------------------------------------------------------------------
with tab_input:
    st.markdown('<div class="section-title">Module 1: User Input System</div>', unsafe_allow_html=True)
    st.markdown("Enter song metadata, paste full lyrics, and optionally upload an audio file (MP3/WAV) to drive the multimodal analysis.")

    col_in1, col_in2 = st.columns([1.2, 1])

    with col_in1:
        st.markdown("##### 🎵 Song Metadata")
        title_in = st.text_input("Song Title *", value=st.session_state.song_title, placeholder="e.g. Golden Horizons")
        artist_in = st.text_input("Artist Name (Optional)", value=st.session_state.artist_name, placeholder="e.g. Aria & The Sunset Strings")

        st.markdown("##### 📜 Song Lyrics *")
        lyrics_in = st.text_area(
            "Paste full lyrics with optional structural tags like [Verse 1], [Chorus], [Bridge], [Outro]:",
            value=st.session_state.raw_lyrics,
            height=280,
            placeholder="[Intro]\nGentle breeze upon the tide...\n\n[Verse 1]\nAmber shadows paint the quiet shore...\n\n[Chorus]\nUnder golden horizons, my heart finds home..."
        )

    with col_in2:
        st.markdown("##### 🎧 Audio File Upload (MP3 or WAV)")
        uploaded_audio = st.file_uploader(
            "Upload audio file (Optional, but enables deep acoustic feature extraction):",
            type=["wav", "mp3", "ogg", "flac"]
        )

        # Handle uploaded audio or preset audio
        active_audio_bytes = None
        if uploaded_audio is not None:
            active_audio_bytes = uploaded_audio.read()
            st.session_state.audio_bytes = active_audio_bytes
            st.session_state.audio_filename = uploaded_audio.name
            st.success(f"Uploaded audio: {uploaded_audio.name}")
        elif st.session_state.audio_bytes is not None:
            active_audio_bytes = st.session_state.audio_bytes
            st.info(f"Preset audio loaded: {st.session_state.audio_filename or 'Synthetic Demo WAV'}")

        if active_audio_bytes is not None:
            st.audio(active_audio_bytes, format="audio/wav")

        st.markdown("""
        > [!NOTE]
        > **Acoustic Speech-to-Text Disclaimer:**
        > If lyrics are not provided, the system does not hallucinate speech-to-text transcription.
        > Lyrics must be pasted separately into the lyrics text area for natural language sentiment, thematic, and story analysis.
        """)

    st.markdown("---")

    # Run Analysis Button
    col_btn1, col_btn2, _ = st.columns([1.2, 1, 2])
    with col_btn1:
        run_analysis = st.button("🚀 Analyze Song & Generate Storyboard", type="primary", use_container_width=True)

    if run_analysis:
        # Validate inputs
        has_audio = (st.session_state.audio_bytes is not None)
        valid, msg = validate_inputs(lyrics_in, has_audio)
        
        if not valid:
            st.error(msg)
        else:
            with st.spinner("Processing lyrics NLP, audio DSP signals, and synthesizing cinematic storyboard..."):
                st.session_state.song_title = title_in or "Untitled Song"
                st.session_state.artist_name = artist_in or "Independent Artist"
                st.session_state.raw_lyrics = lyrics_in

                # 1. Lyrics Analysis
                lyrics_res = None
                emotions_res = None
                if lyrics_in and lyrics_in.strip():
                    lyrics_res = analyze_lyrics_full(lyrics_in)
                    emotions_res = classify_emotions(lyrics_in)
                    st.session_state.lyrics_data = lyrics_res
                    st.session_state.emotion_data = emotions_res

                # 2. Audio Analysis
                audio_res = None
                if st.session_state.audio_bytes:
                    audio_res = analyze_audio_file(
                        io.BytesIO(st.session_state.audio_bytes),
                        original_filename=st.session_state.audio_filename or "track.wav"
                    )
                    st.session_state.audio_data = audio_res

                # 3. Multimodal Mood Detection
                mood_res = detect_mood(
                    lyrics_analysis=lyrics_res,
                    emotion_analysis=emotions_res,
                    audio_analysis=audio_res
                )
                st.session_state.mood_data = mood_res

                # 4. AI Storyboard Generation
                tempo = audio_res.get("tempo", 100.0) if audio_res else 100.0
                duration = audio_res.get("duration_sec", 180.0) if audio_res else 180.0
                sections = lyrics_res.get("sections", []) if lyrics_res else []

                storyboard, mode_used = generate_storyboard(
                    song_title=st.session_state.song_title,
                    artist_name=st.session_state.artist_name,
                    raw_lyrics=lyrics_in,
                    parsed_sections=sections,
                    dominant_mood=mood_res.get("dominant_mood", "Cinematic"),
                    emotion_analysis=emotions_res or {},
                    tempo=tempo,
                    total_audio_duration=duration,
                    api_key=user_api_key
                )

                st.session_state.storyboard = storyboard
                st.session_state.generator_mode = mode_used
                st.session_state.analysis_complete = True

            st.success("Analysis complete! Explore the results across the tabs above.")
            st.rerun()


# -----------------------------------------------------------------------------
# TAB 3: LYRICS ANALYSIS (MODULE 2)
# -----------------------------------------------------------------------------
with tab_lyrics:
    st.markdown('<div class="section-title">Module 2: Lyrics Natural Language Processing</div>', unsafe_allow_html=True)
    
    if not st.session_state.lyrics_data:
        st.warning("Please enter song lyrics and run the analysis in the 'Song Input' tab.")
    else:
        ld = st.session_state.lyrics_data
        ed = st.session_state.emotion_data
        sentiment = ld.get("sentiment", {})

        # Top Lexical Metrics Row
        l_col1, l_col2, l_col3, l_col4 = st.columns(4)
        with l_col1:
            st.metric("Total Words", ld.get("total_words", 0))
        with l_col2:
            st.metric("Unique Vocabulary", ld.get("unique_words", 0))
        with l_col3:
            st.metric("Lexical Diversity (TTR)", ld.get("lexical_diversity", 0.0))
        with l_col4:
            st.metric("Detected Sections", ld.get("section_count", 0))

        st.markdown("<br>", unsafe_allow_html=True)

        col_ly1, col_ly2 = st.columns([1, 1])

        with col_ly1:
            st.markdown("##### 🎭 Emotional Probability Distribution (9 Classes)")
            probs = ed.get("probabilities", {})
            df_emotions = pd.DataFrame(list(probs.items()), columns=["Emotion", "Probability (%)"])
            
            # Interactive Radar Chart
            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(
                r=list(probs.values()),
                theta=list(probs.keys()),
                fill='toself',
                fillcolor='rgba(139, 92, 246, 0.35)',
                line=dict(color='#8b5cf6', width=2),
                name='Emotion %'
            ))
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, max(probs.values(), default=30) + 10], color="#94a3b8"),
                    angularaxis=dict(color="#f8fafc")
                ),
                showlegend=False,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=35, r=35, t=25, b=25),
                height=340
            )
            st.plotly_chart(fig_radar, use_container_width=True)

            st.caption(f"**Classification Methodology:** {ed.get('method', 'Multi-Layer NLP')}")

        with col_ly2:
            st.markdown("##### ⚖️ Sentiment Polarity & Valence (VADER)")
            c_score = sentiment.get("compound", 0.0)
            
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=c_score,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': f"Compound Valence: {sentiment.get('sentiment', 'Neutral')}", 'font': {'color': '#f8fafc', 'size': 14}},
                number={'font': {'color': '#c084fc'}},
                gauge={
                    'axis': {'range': [-1.0, 1.0], 'tickcolor': "#94a3b8"},
                    'bar': {'color': "#8b5cf6"},
                    'steps': [
                        {'range': [-1.0, -0.35], 'color': "rgba(220, 38, 38, 0.25)"},
                        {'range': [-0.35, 0.35], 'color': "rgba(100, 116, 139, 0.25)"},
                        {'range': [0.35, 1.0], 'color': "rgba(34, 197, 94, 0.25)"}
                    ]
                }
            ))
            fig_gauge.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color="#f8fafc"),
                margin=dict(l=30, r=30, t=30, b=20),
                height=220
            )
            st.plotly_chart(fig_gauge, use_container_width=True)
            st.caption(sentiment.get("valence_description", ""))

            # Sentiment components breakdown
            st.markdown(f"**Positive:** `{sentiment.get('pos', 0)*100:.1f}%` | **Neutral:** `{sentiment.get('neu', 0)*100:.1f}%` | **Negative:** `{sentiment.get('neg', 0)*100:.1f}%`")

        st.markdown("---")

        # Keywords and Themes
        col_th1, col_th2 = st.columns([1, 1])
        with col_th1:
            st.markdown("##### 🏷️ Salient Keywords (TF-IDF / Frequency)")
            keywords = ld.get("keywords", [])
            if keywords:
                df_kw = pd.DataFrame(keywords, columns=["Keyword", "Frequency"])
                fig_kw = px.bar(
                    df_kw.head(8),
                    x="Frequency",
                    y="Keyword",
                    orientation="h",
                    color="Frequency",
                    color_continuous_scale="Purples",
                    title="Top Distinctive Lyric Tokens"
                )
                fig_kw.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color="#f8fafc"),
                    yaxis=dict(autorange="reversed"),
                    margin=dict(l=20, r=20, t=30, b=20),
                    height=280
                )
                st.plotly_chart(fig_kw, use_container_width=True)
        
        with col_th2:
            st.markdown("##### 📖 Recurring Thematic Signatures")
            themes = ld.get("themes", [])
            if themes:
                for th in themes:
                    st.markdown(f"""
                    <div style="background: rgba(255,255,255,0.04); border-left: 3px solid #8b5cf6; padding: 0.6rem 0.8rem; border-radius: 4px; margin-bottom: 0.5rem;">
                        <strong style="color: #c084fc;">{th['theme']}</strong> ({th['score']}% match)
                        <div style="font-size: 0.78rem; color: #94a3b8; margin-top: 2px;">Key matches: {', '.join(th['matches'])}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No dominant thematic clusters detected.")


# -----------------------------------------------------------------------------
# TAB 4: AUDIO ANALYSIS ENGINE (MODULE 3)
# -----------------------------------------------------------------------------
with tab_audio:
    st.markdown('<div class="section-title">Module 3: Audio Signal Processing (Librosa DSP)</div>', unsafe_allow_html=True)

    if not st.session_state.audio_data:
        st.info("💡 No audio file was provided. To view audio signal processing features (Tempo, RMS Energy, Spectral Centroid, Chroma Pitches), upload an audio file or select a preset in the sidebar.")
    elif "error" in st.session_state.audio_data:
        st.error(st.session_state.audio_data["error"])
    else:
        ad = st.session_state.audio_data

        # Top Audio Metrics Row
        a_col1, a_col2, a_col3, a_col4 = st.columns(4)
        with a_col1:
            st.metric("Tempo (BPM)", f"{ad.get('tempo', 0)} BPM", ad.get("tempo_category", ""))
        with a_col2:
            st.metric("Duration", ad.get("duration_formatted", "00:00"), f"{ad.get('duration_sec', 0)}s")
        with a_col3:
            st.metric("RMS Energy", f"{ad.get('rms_mean', 0):.4f}", f"Peak: {ad.get('rms_max', 0):.3f}")
        with a_col4:
            st.metric("Spectral Centroid", f"{ad.get('spectral_centroid_mean', 0):.0f} Hz", "Timbral Brightness")

        st.markdown("<br>", unsafe_allow_html=True)

        col_au1, col_au2 = st.columns([1.2, 1])

        with col_au1:
            st.markdown("##### 📈 Dynamic RMS Energy Progression Over Time")
            timeseries = ad.get("energy_timeseries", [])
            if timeseries:
                df_energy = pd.DataFrame(timeseries)
                fig_energy = px.area(
                    df_energy,
                    x="time",
                    y="energy",
                    title="Acoustic Energy Variations (Loudness Envelope)",
                    labels={"time": "Time (seconds)", "energy": "RMS Energy"}
                )
                fig_energy.update_traces(line_color="#8b5cf6", fillcolor="rgba(139, 92, 246, 0.25)")
                fig_energy.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color="#f8fafc"),
                    margin=dict(l=20, r=20, t=35, b=20),
                    height=280
                )
                st.plotly_chart(fig_energy, use_container_width=True)

        with col_au2:
            st.markdown("##### 🎹 Chroma Pitch Class Profile (12 Semitones)")
            chroma = ad.get("chroma_profile", {})
            if chroma:
                df_chroma = pd.DataFrame(list(chroma.items()), columns=["Pitch Class", "Energy %"])
                fig_chroma = px.bar(
                    df_chroma,
                    x="Pitch Class",
                    y="Energy %",
                    color="Energy %",
                    color_continuous_scale="Purples",
                    title=f"Harmonic Distribution (Dominant: {ad.get('dominant_pitch', 'C')})"
                )
                fig_chroma.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color="#f8fafc"),
                    margin=dict(l=20, r=20, t=35, b=20),
                    height=280
                )
                st.plotly_chart(fig_chroma, use_container_width=True)

        st.markdown("---")
        st.markdown("##### 🔍 Acoustic Profile Scientific Interpretation")
        st.markdown(f"> {ad.get('acoustic_profile_summary', '')}")
        st.caption("Note: In accordance with academic MIR (Music Information Retrieval) standards, audio acoustic signals serve as supporting indicators for mood estimation rather than definitive determinants.")


# -----------------------------------------------------------------------------
# TAB 5: MOOD DETECTION (MODULE 4)
# -----------------------------------------------------------------------------
with tab_mood:
    st.markdown('<div class="section-title">Module 4: Multimodal Mood Detection Engine</div>', unsafe_allow_html=True)

    if not st.session_state.mood_data:
        st.info("Run the analysis from the 'Song Input' tab to generate multimodal mood predictions.")
    else:
        md = st.session_state.mood_data

        # Prominent Mood Banner Card
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, rgba(30, 27, 75, 0.8) 0%, rgba(15, 23, 42, 0.9) 100%); border: 1px solid #8b5cf6; border-radius: 14px; padding: 1.8rem; margin-bottom: 1.5rem;">
            <div style="font-size: 0.82rem; text-transform: uppercase; letter-spacing: 0.08em; color: #a78bfa; font-weight: 700;">PREDICTED DOMINANT MOOD</div>
            <div style="font-size: 2.2rem; font-weight: 800; color: #f8fafc; font-family: var(--font-heading); margin: 0.3rem 0;">{md.get('dominant_mood', 'Cinematic')}</div>
            <div style="font-size: 1rem; color: #cbd5e1; max-width: 850px; line-height: 1.6;">{md.get('mood_description', '')}</div>
            <div style="display: flex; gap: 1rem; margin-top: 1.2rem; flex-wrap: wrap;">
                <span class="hero-badge">Confidence: {md.get('confidence_percentage', 0)}%</span>
                <span class="hero-badge">Mode: {md.get('fusion_mode', 'Multimodal')}</span>
                <span class="hero-badge">Runner-up: {md.get('runner_up_mood', 'Reflective')}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col_m1, col_m2 = st.columns([1.2, 1])

        with col_m1:
            st.markdown("##### 🧠 Multimodal Reasoning & Cross-Modal Evidence")
            st.markdown(f"""
            <div class="metric-card" style="font-size: 0.94rem; line-height: 1.65; color: #e2e8f0;">
                {md.get('explanation', '')}
            </div>
            """, unsafe_allow_html=True)

        with col_m2:
            st.markdown("##### 🎨 Recommended Core Color Archetype")
            palette = md.get("color_palette", [])
            st.markdown('<div class="color-bar-container">', unsafe_allow_html=True)
            for hex_c in palette:
                st.markdown(f"""
                <div class="color-swatch-box">
                    <div class="color-swatch" style="background-color: {hex_c};"></div>
                    <div class="color-swatch-hex">{hex_c}</div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            st.caption("Harmonious color grading archetype reflecting the dominant psychological resonance.")


# -----------------------------------------------------------------------------
# TAB 6: AI STORYBOARD (MODULES 5, 6, 7, 8)
# -----------------------------------------------------------------------------
with tab_story:
    st.markdown('<div class="section-title">Module 8: Cinematic Storyboard Dashboard</div>', unsafe_allow_html=True)

    if not st.session_state.storyboard:
        st.info("Run the analysis from the 'Song Input' tab to generate your scene-by-scene storyboard.")
    else:
        st.markdown(f"**Concept:** *{st.session_state.song_title}* by *{st.session_state.artist_name}* &nbsp;|&nbsp; **Engine:** `{st.session_state.generator_mode}`")
        st.markdown("Each scene forms a continuous narrative arc complete with cinematography, camera movements, lighting, transitions, and AI visual prompts.")
        st.markdown("<br>", unsafe_allow_html=True)

        storyboard = st.session_state.storyboard

        for scene in storyboard:
            # Build scene card HTML
            palette_html = "".join([
                f'<div class="color-swatch-box"><div class="color-swatch" style="background-color: {c["hex"]};" title="{c["name"]}: {c["reason"]}"></div><div class="color-swatch-hex">{c["hex"]}</div></div>'
                for c in scene.get("color_palette", [])[:5]
            ])

            st.markdown(f"""
            <div class="scene-card">
                <div class="scene-header">
                    <div>
                        <span class="scene-num-badge">{scene['scene_id']}</span>
                        <span class="scene-title-text">{scene['scene_title']}</span>
                        <span style="color: #94a3b8; font-size: 0.82rem; margin-left: 0.6rem;">({scene['section_name']})</span>
                    </div>
                    <span class="scene-time-badge">⏱ {scene['timestamp']}</span>
                </div>
                
                <div class="scene-meta-row">
                    <span class="meta-pill">📍 <strong>Location:</strong> {scene.get('location', 'Urban')}</span>
                    <span class="meta-pill">👥 <strong>Cast:</strong> {scene.get('characters', 'Protagonists')}</span>
                    <span class="meta-pill">✨ <strong>Atmosphere:</strong> {scene.get('emotional_atmosphere', 'Reflective')}</span>
                </div>
                
                <div class="scene-description-box">
                    <strong>Visual Description:</strong><br>
                    {scene.get('visual_description', '')}
                </div>
                
                <div class="scene-action-box">
                    🎬 <strong>Key Character Action:</strong> {scene.get('character_action', '')}
                </div>
                
                <div class="scene-meta-row" style="margin-top: 0.6rem;">
                    <span class="meta-pill">🎥 <strong>Camera:</strong> {scene.get('camera_angle', 'Medium Shot')}</span>
                    <span class="meta-pill">🔄 <strong>Movement:</strong> {scene.get('camera_movement', 'Dolly')}</span>
                    <span class="meta-pill">💡 <strong>Lighting:</strong> {scene.get('lighting', 'Chiaroscuro')}</span>
                    <span class="meta-pill">🎞️ <strong>Transition:</strong> {scene.get('transition', 'Dissolve')}</span>
                </div>
                
                <div style="font-size: 0.78rem; color: #a78bfa; margin-top: 0.4rem; font-style: italic;">
                    📐 <strong>Cinematography Rationale:</strong> {scene.get('cinematography_rationale', '')}
                </div>
                
                <div style="margin-top: 1rem;">
                    <div style="font-size: 0.75rem; text-transform: uppercase; color: #94a3b8; font-weight: 700; letter-spacing: 0.05em;">SCENE COLOR PALETTE</div>
                    <div class="color-bar-container">
                        {palette_html}
                    </div>
                </div>
                
                <div class="prompt-box">
                    <strong>🎨 AI Generation Prompt (Midjourney / Flux / SDXL):</strong><br>
                    {scene.get('image_prompt', '')}
                </div>
            </div>
            """, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# TAB 7: EXPORT & DOWNLOAD (MODULE 9)
# -----------------------------------------------------------------------------
with tab_export:
    st.markdown('<div class="section-title">Module 9: Export & Download Suite</div>', unsafe_allow_html=True)

    if not st.session_state.storyboard:
        st.info("Run the analysis from the 'Song Input' tab to enable exporting.")
    else:
        st.markdown("Download your complete music-video concept, academic analysis report, and structured storyboard in multiple standard formats.")
        st.markdown("<br>", unsafe_allow_html=True)

        col_ex1, col_ex2, col_ex3 = st.columns(3)

        # 1. PDF Storyboard Export
        with col_ex1:
            st.markdown("""
            <div class="metric-card" style="text-align: center;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">📄</div>
                <div class="metric-value" style="font-size: 1.1rem;">Storyboard PDF</div>
                <div class="metric-sub" style="margin-bottom: 1rem;">Professional multi-page concept deck with swatches & cinematography</div>
            </div>
            """, unsafe_allow_html=True)
            
            try:
                pdf_bytes = generate_storyboard_pdf(
                    song_title=st.session_state.song_title,
                    artist_name=st.session_state.artist_name,
                    mood_analysis=st.session_state.mood_data or {},
                    lyrics_analysis=st.session_state.lyrics_data,
                    emotion_analysis=st.session_state.emotion_data,
                    audio_analysis=st.session_state.audio_data,
                    storyboard=st.session_state.storyboard,
                    generator_mode=st.session_state.generator_mode
                )
                st.download_button(
                    label="📥 Download Storyboard (PDF)",
                    data=pdf_bytes,
                    file_name=f"{st.session_state.song_title.lower().replace(' ', '_')}_storyboard.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Error compiling PDF: {str(e)}")

        # 2. JSON Project State Export
        with col_ex2:
            st.markdown("""
            <div class="metric-card" style="text-align: center;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">📦</div>
                <div class="metric-value" style="font-size: 1.1rem;">Full State (JSON)</div>
                <div class="metric-sub" style="margin-bottom: 1rem;">Raw JSON containing all NLP, DSP, and scene metadata</div>
            </div>
            """, unsafe_allow_html=True)
            
            json_str = serialize_project_state(
                song_title=st.session_state.song_title,
                artist_name=st.session_state.artist_name,
                lyrics_analysis=st.session_state.lyrics_data,
                emotion_analysis=st.session_state.emotion_data,
                audio_analysis=st.session_state.audio_data,
                mood_analysis=st.session_state.mood_data,
                storyboard=st.session_state.storyboard,
                generator_mode=st.session_state.generator_mode
            )
            st.download_button(
                label="📥 Download State (JSON)",
                data=json_str,
                file_name=f"{st.session_state.song_title.lower().replace(' ', '_')}_data.json",
                mime="application/json",
                use_container_width=True
            )

        # 3. Markdown / Text Analysis Report
        with col_ex3:
            st.markdown("""
            <div class="metric-card" style="text-align: center;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">📝</div>
                <div class="metric-value" style="font-size: 1.1rem;">Analysis Report</div>
                <div class="metric-sub" style="margin-bottom: 1rem;">Academic markdown report with methodology and metrics</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Construct markdown report text
            md_text = f"""# MUSIC-TO-VISUAL NARRATIVE GENERATOR
## Comprehensive Academic Mini-Project Report
**Song Title:** {st.session_state.song_title}
**Artist:** {st.session_state.artist_name}
**Engine:** {st.session_state.generator_mode}

---
### 1. Multimodal Mood & Emotion Summary
- **Predicted Dominant Mood:** {st.session_state.mood_data.get('dominant_mood', 'N/A')}
- **Classification Confidence:** {st.session_state.mood_data.get('confidence_percentage', 0)}%
- **Top Lyrical Emotion:** {st.session_state.emotion_data.get('dominant_emotion', 'N/A') if st.session_state.emotion_data else 'N/A'}
- **Scientific Rationale:** {st.session_state.mood_data.get('explanation', '')}

### 2. Audio Signal Processing (Librosa DSP)
- **Tempo:** {st.session_state.audio_data.get('tempo', 'N/A') if st.session_state.audio_data else 'N/A'} BPM
- **Duration:** {st.session_state.audio_data.get('duration_formatted', 'N/A') if st.session_state.audio_data else 'N/A'}
- **Mean RMS Energy:** {st.session_state.audio_data.get('rms_mean', 'N/A') if st.session_state.audio_data else 'N/A'}
- **Spectral Centroid:** {st.session_state.audio_data.get('spectral_centroid_mean', 'N/A') if st.session_state.audio_data else 'N/A'} Hz

### 3. Scene Breakdown
"""
            for sc in st.session_state.storyboard:
                md_text += f"\n#### {sc['scene_id']}: {sc['scene_title']} ({sc['section_name']})\n"
                md_text += f"- **Timestamp:** {sc['timestamp']}\n"
                md_text += f"- **Location:** {sc.get('location', '')}\n"
                md_text += f"- **Visual Description:** {sc.get('visual_description', '')}\n"
                md_text += f"- **Camera:** {sc.get('camera_angle', '')} | {sc.get('camera_movement', '')}\n"
                md_text += f"- **Lighting:** {sc.get('lighting', '')}\n"
                md_text += f"- **AI Prompt:** `{sc.get('image_prompt', '')}`\n"

            st.download_button(
                label="📥 Download Report (Markdown)",
                data=md_text,
                file_name=f"{st.session_state.song_title.lower().replace(' ', '_')}_report.md",
                mime="text/markdown",
                use_container_width=True
            )


# -----------------------------------------------------------------------------
# TAB 8: ABOUT PROJECT & ACADEMIC DOCUMENTATION
# -----------------------------------------------------------------------------
with tab_about:
    st.markdown('<div class="section-title">Academic Mini-Project Documentation</div>', unsafe_allow_html=True)
    
    st.markdown(r"""
    ### Project Background
    This project was conceived and developed as a **B.Tech Computer Science 2nd-Year Mini-Project** 
    specializing in **Artificial Intelligence and Machine Learning** by a collaborative team of five students.

    ### Core Engineering Contributions:
    1. **Natural Language Processing:** Implemented tokenization, stopword filtering, TF-IDF style keyword salience, semantic theme extraction, and a 9-class affective emotion classifier combining VADER valence anchoring with NRC-style emotion category lexicons and softmax normalization.
    2. **Digital Audio Signal Processing (DSP):** Integrated Librosa to analyze acoustic audio features, including Tempo (BPM) beat tracking, Root Mean Square (RMS) loudness contours, Spectral Centroid timbral brightness, Zero-Crossing Rate (ZCR), and 12-semitone harmonic Chroma STFT profiles.
    3. **Multimodal Affective Fusion:** Engineered a weighted cross-modal fusion engine combining lyrical sentiment ($70\%$) with acoustic indicators ($30\%$) to deduce the dominant musical mood and confidence margin.
    4. **Cinematic Story Generation:** Built an interconnected screenplay generation architecture that structures visual narratives into cinematic scenes complete with professional camera directions, lighting styles, color palettes, and Midjourney/Flux image prompts.
    5. **Industry-Grade Export Suite:** Integrated FPDF2 for generating high-definition multi-page PDF storyboards, alongside JSON and Markdown exports.

    ### Technology Stack
    - **Frontend:** Streamlit 1.67+, Custom CSS3 Glassmorphism, Responsive Component Architecture
    - **Audio DSP:** Librosa 1.0.1, SoundFile, SciPy, NumPy
    - **NLP & Sentiment:** NLTK (VADER, Stopwords, Punkt), Scikit-Learn
    - **Visualization:** Plotly Express & Plotly Graph Objects (Polar Radars, Area Envelopes, Gauge Meters)
    - **Generative AI:** Google Gemini API (`gemini-2.5-flash`) via `google-genai` SDK with built-in Intelligent Offline Fallback
    - **Document Generation:** FPDF2

    ### Academic Transparency & Disclaimer
    - **No Fake Generated Images:** The application does not claim to generate real-time video frames; it generates rigorous scene specifications and copy-pasteable prompts engineered for modern image models (Midjourney v6, Flux, Stable Diffusion XL).
    - **No Artificial Speech-to-Text:** Audio upload extracts acoustic musical characteristics; lyrics must be provided separately unless a dedicated STT pipeline is hooked up.
    - **Achievable & Explainable:** All machine learning and rule-based fallback components are grounded in explainable statistical heuristics, making it suitable for viva defense and college mini-project demonstrations.
    """)
