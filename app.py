import streamlit as st
import edge_tts
import asyncio
import tempfile
import os
import re

# 1. Page Configuration
st.set_page_config(page_title="The Dragon Audio Converts", page_icon="🐉", layout="centered")

# 2. MONETAG VERIFICATION META TAG (Injects into <head>)
st.markdown('<meta name="monetag" content="d80d3c02aee02551207039c9200f3f6a">', unsafe_allow_html=True)

# 3. Custom CSS Styles
st.markdown("""
<style>
.stApp { background: linear-gradient(160deg, #0a0000 0%, #1a0505 40%, #0d0000 100%); color: #ffcc00; }
h1 { color: #ff4500 !important; text-shadow: 0 0 15px #ff0000, 0 0 30px #8b0000; text-align: center; font-family: 'Georgia', serif; letter-spacing: 2px; }
h2, h3 { color: #ff8c00 !important; font-family: 'Georgia', serif; }
p, label { color: #ffd700 !important; }
section[data-testid="stSidebar"] { background: linear-gradient(180deg, #110000 0%, #000000 100%); border-right: 2px solid #8b0000; }
.stButton > button { background: linear-gradient(90deg, #8b0000, #ff4500, #8b0000); color: #ffd700 !important; border: 2px solid #ffd700; font-weight: bold; text-transform: uppercase; letter-spacing: 1px; border-radius: 8px; transition: all 0.3s ease; }
.stButton > button:hover { background: linear-gradient(90deg, #ff4500, #ffd700, #ff4500); color: #000 !important; border-color: #ff4500; box-shadow: 0 0 20px #ff4500; }
.stFileUploader { background: rgba(139, 0, 0, 0.15); border: 2px dashed #ff4500 !important; border-radius: 10px; padding: 20px; }
.stFileUploader label { color: #ffd700 !important; font-weight: bold; } 
.stSelectbox div[data-baseweb="select"] { background-color: #1a0505; border: 1px solid #8b0000; border-radius: 8px; color: #ffd700; }
.stTextArea textarea { background-color: #1a0505 !important; border: 1px solid #8b0000 !important; color: #ffd700 !important; }
.stRadio label { color: #ffd700 !important; }
.stProgress > div > div > div > div { background: linear-gradient(90deg, #8b0000, #ff4500, #ffd700); }
.stSuccess { background-color: rgba(255, 215, 0, 0.1); color: #ffd700 !important; border: 1px solid #ffd700; }
.stError { background-color: rgba(139, 0, 0, 0.2); color: #ff4500 !important; border: 1px solid #ff4500; }
</style>
""", unsafe_allow_html=True)

st.title(" The Dragon Audio Converts")
st.markdown("<h3 style='text-align: center; color: #ff8c00;'>Forge your text into golden audio. Unleash the fire of AI voices.</h3>", unsafe_allow_html=True)
st.markdown("---")

# Language -> list of (display_name, voice_id)
LANGUAGE_VOICES = {
    "English (US)": [
        ("Aria (Female)", "en-US-AriaNeural"),
        ("Guy (Male)", "en-US-GuyNeural"),
        ("Jenny (Female)", "en-US-JennyNeural"),
        ("Christopher (Male)", "en-US-ChristopherNeural"),
    ],
    "English (UK)": [
        ("Sonia (Female)", "en-GB-SoniaNeural"),
        ("Ryan (Male)", "en-GB-RyanNeural"),
    ],
    "English (Australia)": [
        ("Natasha (Female)", "en-AU-NatashaNeural"),
        ("William (Male)", "en-AU-WilliamNeural"),
    ],
    "English (India)": [
        ("Neerja (Female)", "en-IN-NeerjaNeural"),
        ("Prabhat (Male)", "en-IN-PrabhatNeural"),
    ],
    "Hindi": [
        ("Swara (Female)", "hi-IN-SwaraNeural"),
        ("Madhur (Male)", "hi-IN-MadhurNeural"),
    ],
    "Urdu": [
        ("Uzma (Female)", "ur-PK-UzmaNeural"),
        ("Asad (Male)", "ur-PK-AsadNeural"),
    ],
    "Spanish (Spain)": [
        ("Elvira (Female)", "es-ES-ElviraNeural"),
        ("Alvaro (Male)", "es-ES-AlvaroNeural"),
    ],
    "Spanish (Mexico)": [
        ("Dalia (Female)", "es-MX-DaliaNeural"),
        ("Jorge (Male)", "es-MX-JorgeNeural"),
    ],
    "French": [
        ("Denise (Female)", "fr-FR-DeniseNeural"),
        ("Henri (Male)", "fr-FR-HenriNeural"),
    ],
    "German": [
        ("Katja (Female)", "de-DE-KatjaNeural"),
        ("Conrad (Male)", "de-DE-ConradNeural"),
    ],
    "Italian": [
        ("Elsa (Female)", "it-IT-ElsaNeural"),
        ("Diego (Male)", "it-IT-DiegoNeural"),
    ],
    "Portuguese (Brazil)": [
        ("Francisca (Female)", "pt-BR-FranciscaNeural"),
        ("Antonio (Male)", "pt-BR-AntonioNeural"),
    ],
    "Arabic": [
        ("Salma (Female)", "ar-SA-ZariyahNeural"),
        ("Hamed (Male)", "ar-SA-HamedNeural"),
    ],
    "Chinese (Mandarin)": [
        ("Xiaoxiao (Female)", "zh-CN-XiaoxiaoNeural"),
        ("Yunxi (Male)", "zh-CN-YunxiNeural"),
    ],
    "Japanese": [
        ("Nanami (Female)", "ja-JP-NanamiNeural"),
        ("Keita (Male)", "ja-JP-KeitaNeural"),
    ],
    "Russian": [
        ("Svetlana (Female)", "ru-RU-SvetlanaNeural"),
        ("Dmitry (Male)", "ru-RU-DmitryNeural"),
    ],
}

def add_natural_pauses(text):
    """Insert short breathing pauses so the narration doesn't sound rushed/robotic."""
    text = re.sub(r'([.!?])\s+', r'\1  ', text)
    text = re.sub(r'([,;:])\s+', r'\1  ', text)
    text = re.sub(r'\n{2,}', '\n\n... \n\n', text)
    return text

def chunk_text(text, max_chars=4000):
    paragraphs = re.split(r'\n\s*\n', text)
    chunks, current = [], ""
    for p in paragraphs:
        if len(current) + len(p) > max_chars and current:
            chunks.append(current.strip())
            current = p
        else:
            current = f"{current}\n\n{p}" if current else p
    if current.strip():
        chunks.append(current.strip())
    return chunks

def synthesize(text_content, source_name, voice, rate_pct, pitch_pct, volume_pct, natural_pauses):
    processed_text = add_natural_pauses(text_content) if natural_pauses else text_content
    chunks = chunk_text(processed_text)
    all_audio = b""
    rate_str = f"{'+' if rate_pct >= 0 else ''}{rate_pct}%"
    pitch_str = f"{'+' if pitch_pct >= 0 else ''}{pitch_pct}Hz"
    volume_str = f"{'+' if volume_pct >= 0 else ''}{volume_pct}%"
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, chunk in enumerate(chunks):
        status_text.text(f"🐉 Breathing fire on part {i+1} of {len(chunks)}...")
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            communicate = edge_tts.Communicate(
                chunk, voice,
                rate=rate_str, pitch=pitch_str, volume=volume_str
            )
            asyncio.run(communicate.save(tmp.name))
            with open(tmp.name, "rb") as f:
                all_audio += f.read()
            os.unlink(tmp.name)
        progress_bar.progress((i + 1) / len(chunks))
        
    progress_bar.empty()
    status_text.empty()
    return all_audio

def render_result(all_audio, source_name):
    import base64
    st.balloons()
    st.success("🏆 The Forging is Complete! Your golden audio is ready.")
    b64_audio = base64.b64encode(all_audio).decode()
    
    st.markdown("**🎚️ Playback Speed**")
    st.components.v1.html(f"""
        <audio id="dragonAudio" controls style="width:100%;">
            <source src="data:audio/mp3;base64,{b64_audio}" type="audio/mp3">
        </audio>
        <div style="margin-top:8px;">
            <button onclick="document.getElementById('dragonAudio').playbackRate=0.75" style="margin-right:6px;padding:6px 10px;">0.75x</button>
            <button onclick="document.getElementById('dragonAudio').playbackRate=1.0" style="margin-right:6px;padding:6px 10px;">1x</button>
            <button onclick="document.getElementById('dragonAudio').playbackRate=1.25" style="margin-right:6px;padding:6px 10px;">1.25x</button>
            <button onclick="document.getElementById('dragonAudio').playbackRate=1.5" style="margin-right:6px;padding:6px 10px;">1.5x</button>
            <button onclick="document.getElementById('dragonAudio').playbackRate=2.0" style="padding:6px 10px;">2x</button>
        </div>
    """, height=110)
    
    st.download_button(
        label="⬇️ Claim Your MP3 Treasure",
        data=all_audio,
        file_name=f"{source_name}_dragon_audio.mp3",
        mime="audio/mpeg",
        use_container_width=True
    )

with st.sidebar:
    st.header(" The Forge Settings")
    language = st.selectbox("Choose the Dragon's Tongue (Language)", list(LANGUAGE_VOICES.keys()))
    voice_options = LANGUAGE_VOICES[language]
    voice_labels = [label for label, _ in voice_options]
    chosen_label = st.selectbox("Choose the Voice of the Dragon", voice_labels)
    voice = dict(voice_options)[chosen_label]
    
    st.markdown("#### ️ Humanize the Voice")
    rate_pct = st.slider("Speaking Speed", -30, 30, -6, step=2, format="%d%%",
                          help="Slightly slower than default (around -5% to -10%) tends to sound more natural and less rushed.")
    pitch_pct = st.slider("Pitch", -20, 20, 0, step=2, format="%dHz",
                           help="Small shifts (-5 to +5) can add warmth. Large shifts sound robotic.")
    volume_pct = st.slider("Volume", -30, 30, 0, step=5, format="%d%%")
    natural_pauses = st.checkbox("Add natural pauses at punctuation", value=True,
                                  help="Inserts brief breathing pauses after commas and sentence ends, like a real narrator.")
    
    st.info("💡 **Tip:** Split massive novels into chapters under 5,000 words for the fastest forging.")

st.markdown("### 📜 Offer Your Scroll")
input_mode = st.radio("How will you offer your words?", ["Upload a .txt file", "Paste text directly"], horizontal=True)

if input_mode == "Upload a .txt file":
    uploaded_file = st.file_uploader("Upload your novel (.txt)", type=["txt"], label_visibility="collapsed")
    text_content = ""
    source_name = "dragon_audio"
    if uploaded_file is not None:
        text_content = uploaded_file.read().decode("utf-8")
        source_name = uploaded_file.name.rsplit('.', 1)[0]
        st.success(f"✅ Scroll Accepted: '{uploaded_file.name}' ({len(text_content):,} characters)")
    
    if text_content.strip():
        if st.button("🔥 Ignite the Forge (Convert to MP3)", type="primary", use_container_width=True, key="ignite_file"):
            try:
                audio = synthesize(text_content, source_name, voice, rate_pct, pitch_pct, volume_pct, natural_pauses)
                render_result(audio, source_name)
            except Exception as e:
                st.error(f" The fire died out. Error: {str(e)}")
    else:
        st.info(" Upload a scroll to begin.")
else:
    text_content = st.text_area(
        "Paste your text here",
        height=250,
        placeholder="Speak your words into the fire...",
        label_visibility="collapsed",
    )
    source_name = "pasted_text"
    if text_content.strip():
        st.success(f"✅ Words Accepted ({len(text_content):,} characters)")
        if st.button("🔥 Ignite the Forge (Convert to MP3)", type="primary", use_container_width=True, key="ignite_text"):
            try:
                audio = synthesize(text_content, source_name, voice, rate_pct, pitch_pct, volume_pct, natural_pauses)
                render_result(audio, source_name)
            except Exception as e:
                st.error(f"❌ The fire died out. Error: {str(e)}")
    else:
        st.info("👆 Paste your text above to begin.")

# Privacy Policy (Required for Ad Networks)
st.markdown("---")
with st.expander("📜 Privacy Policy & Terms of Use"):
    st.markdown("""
    **Privacy Policy:** This website uses Monetag to display advertisements. 
    Third-party vendors may use cookies to serve ads based on prior visits. 
    Users can opt out of personalized advertising by visiting their browser settings.
    
    **Terms of Use:** This tool is provided as-is for text-to-speech conversion. 
    Generated audio should comply with applicable copyright laws.
    """)
