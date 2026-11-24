# 🎬 MUSIC-TO-VISUAL NARRATIVE GENERATOR
### AI-Powered Multimodal Music Video Storyboard Synthesis
**Academic Mini-Project | B.Tech Computer Science (Artificial Intelligence & Machine Learning) - 2nd Year**

---

## 📌 1. Project Overview
The **Music-to-Visual Narrative Generator** is an AI-powered web application that bridges natural language processing, audio digital signal processing (DSP), and generative storytelling. It ingests song lyrics and musical audio (MP3/WAV), extracts lyrical sentiments, thematic structures, and acoustic characteristics (tempo, loudness, timbre, harmonic pitch profile), and synthesizes a coherent, scene-by-scene cinematic music-video storyboard complete with professional camera directions, lighting schemes, harmonious color palettes, and Midjourney/Flux-ready image generation prompts.

---

## 🚀 2. Key Features

- **Multimodal Sentiment & Mood Fusion:** Merges textual emotion probabilities ($70\%$) with acoustic signal heuristics ($30\%$) to predict dominant moods with statistical confidence.
- **9-Class Affective NLP Classifier:** Classifies lyrics across *Happiness, Sadness, Love, Anger, Fear, Hope, Nostalgia, Loneliness,* and *Excitement* using VADER valence anchoring and expanded NRC lexicons.
- **Librosa Audio DSP Engine:** Extracts dynamic tempo (BPM), duration, RMS energy profiles, spectral centroid (timbral brightness), and 12-semitone Chroma pitch distributions.
- **Intelligent Storyboard Synthesis (Dual-Engine):**
  - **Generative AI Engine:** Leverages Google Gemini (`gemini-2.5-flash`) via `google-genai` SDK for original script synthesis.
  - **Offline Cinematic Screenplay Engine:** Built-in high-fidelity rule-based narrative engine that works 100% offline without requiring an API key.
- **Cinematography & Color Direction:** Automatically prescribes shot types (Wide, Medium, Close-Up, Dutch, Hero Shot), camera movements (Dolly, Steadicam, Crane), lighting, transitions, and 5-swatch HEX palettes.
- **Multi-Format Export Suite:** 1-click download of high-definition Storyboard PDF decks, raw JSON state data, and academic Markdown reports.
- **Pre-Loaded Evaluation Presets:** Instant 1-click testing of 5 distinct moods: *Romantic, Sad, Happy, Motivational, and Suspenseful*.

---

## 🛠️ 3. Technology Stack

| Layer | Technology / Library | Purpose |
| :--- | :--- | :--- |
| **Frontend UI** | Streamlit 1.67+, Custom CSS3 | Cinematic glassmorphic UI, responsive controls, interactive tabs |
| **Audio Processing** | Librosa 1.0.1, SoundFile, SciPy | Tempo tracking, RMS envelope, spectral features, chroma profiles |
| **NLP & Semantics** | NLTK 3.10+, VADER, Scikit-Learn | Tokenization, TF-IDF salience, sentiment polarity, emotion vectors |
| **Data & Visuals** | Plotly Express, Plotly Graph Objects, Pandas, NumPy | Interactive radar charts, energy area plots, chroma histograms |
| **Generative AI** | Google Gemini API (`google-genai`) | High-level generative scriptwriting (with offline fallback) |
| **Document Export** | FPDF2 | Automated multi-page PDF storyboard compilation with swatches |

---

## 📁 4. Project Folder Structure

```text
MUSIC_AI/
│
├── app.py                         # Main Streamlit web application & UI dashboard
├── requirements.txt               # Python package dependencies
├── README.md                      # Project setup & execution guide
├── PROJECT_REPORT.md              # 17-Section academic report & presentation deck
├── .env.example                   # Environment configuration template
├── test_pipeline.py               # Automated test suite covering all 5 moods & edge cases
│
├── modules/                       # Core functional backend engines
│   ├── __init__.py
│   ├── lyrics_analyzer.py         # NLP: Tokenization, TF-IDF keywords, themes, VADER sentiment
│   ├── audio_analyzer.py          # Librosa DSP: Tempo, RMS, spectral centroid, chroma profiles
│   ├── emotion_detector.py        # 9-class affective emotion classifier with softmax normalization
│   ├── mood_detector.py           # Multimodal fusion of lyrics & acoustic features with confidence
│   ├── story_generator.py         # Gemini API + Offline Intelligent screenplay synthesis
│   ├── color_generator.py         # Emotional color palette mapper with HEX swatches & justifications
│   └── camera_generator.py        # Cinematography direction engine (angles, movements, lighting)
│
├── utils/                         # Helper utilities
│   ├── __init__.py
│   ├── helpers.py                 # Input validation, JSON serializers, error handling
│   ├── pdf_exporter.py            # Multi-page PDF storyboard compiler (FPDF2)
│   └── audio_synth.py             # SciPy/NumPy acoustic synthesizer for test audio generation
│
├── assets/
│   └── style.css                  # Custom dark cinematic UI CSS styling
│
└── sample_data/                   # Pre-loaded evaluation datasets
    ├── sample_lyrics.json         # 5 song presets (Romantic, Sad, Happy, Motivational, Suspense)
    ├── sample_lyrics.txt          # Human-readable sample lyrics documentation
    ├── sample_audio_generator.py  # Script to generate synthetic test WAV files
    └── audio/                     # Pre-generated 16-bit PCM WAV demo audio files
        ├── romantic_sample.wav
        ├── sad_sample.wav
        ├── happy_sample.wav
        ├── motivational_sample.wav
        └── suspenseful_sample.wav
```

---

## ⚡ 5. Installation & Execution Guide

### Prerequisites
- Python 3.10+ (Tested and verified up to Python 3.14 on Windows)
- Modern Web Browser (Chrome, Firefox, Edge, Safari)

### Step 1: Clone or Navigate to Project Directory
```powershell
cd c:\Users\tannu\Downloads\MUSIC_AI
```

### Step 2: Install Required Dependencies
```powershell
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables (Optional)
If you wish to use the Google Gemini API for generative AI scripting, copy `.env.example` to `.env`:
```powershell
cp .env.example .env
```
Add your Gemini API key in `.env`:
```ini
GEMINI_API_KEY=your_gemini_api_key_here
```
*(Note: If omitted, the application runs seamlessly using the built-in Intelligent Screenplay Narrative Engine!)*

### Step 4: Run the Application
Launch the Streamlit dashboard:
```powershell
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 🧪 6. Running Automated Verification Tests
To run the automated multi-mood verification suite covering all 5 test moods (*Romantic, Sad, Happy, Motivational, Suspenseful*) and all edge cases (missing lyrics, missing audio, short text, offline fallback):
```powershell
python test_pipeline.py
```

Expected output:
```text
======================================================================
ALL 5 MOODS AND EDGE CASES PASSED WITH 100% SUCCESS!
======================================================================
```

---

## 👥 7. Academic Mini-Project Attribution
- **Degree:** B.Tech Computer Science & Engineering (Specialization in AI & ML)
- **Year of Study:** 2nd Year
- **Team Size:** 5 Members
- **Project Title:** Music-to-Visual Narrative Generator
- **Academic Year:** 2026-2027
