import streamlit as st
import edge_tts
import asyncio
import tempfile
import os
import re
import streamlit.components.v1 as components

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="The Dragon Audio Converts",
    page_icon="🐉",
    layout="centered"
)

# ============================================================
# GOOGLE ADSENSE
# ============================================================

ADSENSE_PUBLISHER_ID = "ca-pub-9856228284451388"

# Load Google AdSense
st.markdown(
    f"""
    <script async
        src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADSENSE_PUBLISHER_ID}"
        crossorigin="anonymous">
    </script>
    """,
    unsafe_allow_html=True
)

# Your AdSense ad-unit slot ID.
# Replace this after creating an AdSense ad unit.
ADSENSE_AD_SLOT = "YOUR_REAL_AD_SLOT_ID"

# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .stApp {
        background:
            radial-gradient(
                circle at top,
                rgba(75, 0, 130, 0.25),
                transparent 35%
            ),
            linear-gradient(
                180deg,
                #080016 0%,
                #120025 45%,
                #050008 100%
            );
        color: white;
    }

    .dragon-title {
        text-align: center;
        font-size: 42px;
        font-weight: 800;
        margin-top: 10px;
        margin-bottom: 5px;
        color: #ffffff;
    }

    .dragon-subtitle {
        text-align: center;
        color: #cfc5df;
        font-size: 16px;
        margin-bottom: 25px;
    }

    .dragon-card {
        background: rgba(255,255,255,0.055);
        border: 1px solid rgba(255,255,255,0.10);
        border-radius: 18px;
        padding: 22px;
        margin: 15px 0;
        backdrop-filter: blur(10px);
    }

    .dragon-ad-space {
        min-height: 90px;
        margin: 18px 0;
    }

    .result-title {
        font-size: 24px;
        font-weight: 700;
        margin-bottom: 10px;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="dragon-title">🐉 The Dragon Audio Converts</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="dragon-subtitle">Convert your text and novels into natural-sounding MP3 audio.</div>',
    unsafe_allow_html=True
)

# ============================================================
# LANGUAGE / VOICE DATA
# ============================================================

LANGUAGE_VOICES = {
    "English (US)": {
        "en-US-AriaNeural": "Aria",
        "en-US-GuyNeural": "Guy",
        "en-US-JennyNeural": "Jenny",
    },

    "English (UK)": {
        "en-GB-SoniaNeural": "Sonia",
        "en-GB-RyanNeural": "Ryan",
    },

    "English (Australia)": {
        "en-AU-NatashaNeural": "Natasha",
        "en-AU-WilliamNeural": "William",
    },

    "English (India)": {
        "en-IN-NeerjaNeural": "Neerja",
        "en-IN-PrabhatNeural": "Prabhat",
    },

    "Hindi": {
        "hi-IN-SwaraNeural": "Swara",
        "hi-IN-MadhurNeural": "Madhur",
    },

    "Urdu": {
        "ur-PK-AsadNeural": "Asad",
        "ur-PK-UzmaNeural": "Uzma",
    },

    "Spanish (Spain)": {
        "es-ES-ElviraNeural": "Elvira",
        "es-ES-AlvaroNeural": "Alvaro",
    },

    "Spanish (Mexico)": {
        "es-MX-DaliaNeural": "Dalia",
        "es-MX-JorgeNeural": "Jorge",
    },

    "French": {
        "fr-FR-DeniseNeural": "Denise",
        "fr-FR-HenriNeural": "Henri",
    },

    "German": {
        "de-DE-KatjaNeural": "Katja",
        "de-DE-ConradNeural": "Conrad",
    },

    "Italian": {
        "it-IT-ElsaNeural": "Elsa",
        "it-IT-DiegoNeural": "Diego",
    },

    "Portuguese (Brazil)": {
        "pt-BR-FranciscaNeural": "Francisca",
        "pt-BR-AntonioNeural": "Antonio",
    },

    "Arabic": {
        "ar-SA-ZariyahNeural": "Zariyah",
        "ar-SA-HamedNeural": "Hamed",
    },

    "Chinese (Mandarin)": {
        "zh-CN-XiaoxiaoNeural": "Xiaoxiao",
        "zh-CN-YunxiNeural": "Yunxi",
    },

    "Japanese": {
        "ja-JP-NanamiNeural": "Nanami",
        "ja-JP-KeitaNeural": "Keita",
    },

    "Russian": {
        "ru-RU-SvetlanaNeural": "Svetlana",
        "ru-RU-DmitryNeural": "Dmitry",
    }
}

# ============================================================
# TEXT PROCESSING
# ============================================================

def add_natural_pauses(text):
    text = re.sub(r'([.!?])\s+', r'\1\n', text)
    text = re.sub(r'([,:;])\s+', r'\1 ', text)
    return text


def chunk_text(text, max_chars=3500):
    text = text.strip()

    if len(text) <= max_chars:
        return [text]

    chunks = []
    current = ""

    paragraphs = text.split("\n")

    for paragraph in paragraphs:

        if len(current) + len(paragraph) + 1 <= max_chars:
            current += paragraph + "\n"

        else:
            if current.strip():
                chunks.append(current.strip())

            current = paragraph + "\n"

    if current.strip():
        chunks.append(current.strip())

    return chunks


# ============================================================
# TEXT TO SPEECH
# ============================================================

async def generate_audio(
    text,
    voice,
    rate,
    pitch,
    volume,
    output_file
):

    communicate = edge_tts.Communicate(
        text,
        voice=voice,
        rate=rate,
        pitch=pitch,
        volume=volume
    )

    await communicate.save(output_file)


def synthesize(
    text,
    source_name,
    voice,
    speed,
    pitch,
    volume,
    natural_pauses
):

    if natural_pauses:
        text = add_natural_pauses(text)

    chunks = chunk_text(text)

    progress = st.progress(0)
    status = st.empty()

    temp_files = []

    try:

        for index, chunk in enumerate(chunks):

            status.info(
                f"🐉 Creating audio... {index + 1}/{len(chunks)}"
            )

            temp_file = tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".mp3"
            )

            temp_file.close()

            rate_value = f"{speed:+d}%"
            pitch_value = f"{pitch:+d}Hz"
            volume_value = f"{volume:+d}%"

            asyncio.run(
                generate_audio(
                    chunk,
                    voice,
                    rate_value,
                    pitch_value,
                    volume_value,
                    temp_file.name
                )
            )

            temp_files.append(temp_file.name)

            progress.progress(
                int(((index + 1) / len(chunks)) * 100)
            )

        # Combine files if there is more than one chunk.
        final_file = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".mp3"
        )

        final_file.close()

        with open(final_file.name, "wb") as output:

            for file_path in temp_files:

                with open(file_path, "rb") as source:
                    output.write(source.read())

        status.success("✅ Audio conversion completed!")

        return final_file.name

    except Exception as e:

        status.error(
            f"❌ Audio generation failed: {str(e)}"
        )

        return None

    finally:

        for file_path in temp_files:

            try:
                os.remove(file_path)

            except Exception:
                pass


# ============================================================
# ADSENSE AD
# ============================================================

def render_adsense_ad():

    # Don't render a fake/invalid ad unit.
    if ADSENSE_AD_SLOT == "YOUR_REAL_AD_SLOT_ID":
        return

    components.html(
        f"""
        <!DOCTYPE html>

        <html>

        <head>

            <script async
                src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADSENSE_PUBLISHER_ID}"
                crossorigin="anonymous">
            </script>

        </head>

        <body style="margin:0; padding:0;">

            <ins class="adsbygoogle"
                style="display:block"
                data-ad-client="{ADSENSE_PUBLISHER_ID}"
                data-ad-slot="{ADSENSE_AD_SLOT}"
                data-ad-format="auto"
                data-full-width-responsive="true">
            </ins>

            <script>
                (adsbygoogle = window.adsbygoogle || []).push({{}});
            </script>

        </body>

        </html>
        """,
        height=120
    )


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("⚙️ Audio Settings")

    language = st.selectbox(
        "🌎 Language",
        list(LANGUAGE_VOICES.keys())
    )

    voices = LANGUAGE_VOICES[language]

    voice = st.selectbox(
        "🎙️ Voice",
        list(voices.keys()),
        format_func=lambda x: voices[x]
    )

    speed = st.slider(
        "⚡ Speed",
        min_value=-30,
        max_value=30,
        value=-6,
        step=1
    )

    pitch = st.slider(
        "🎵 Pitch",
        min_value=-20,
        max_value=20,
        value=0,
        step=1
    )

    volume = st.slider(
        "🔊 Volume",
        min_value=-30,
        max_value=30,
        value=0,
        step=1
    )

    natural_pauses = st.checkbox(
        "⏸️ Natural pauses",
        value=True
    )


# ============================================================
# INPUT
# ============================================================

st.markdown(
    '<div class="dragon-card">',
    unsafe_allow_html=True
)

input_mode = st.radio(
    "Choose input method",
    ["📄 Upload TXT", "✍️ Paste Text"],
    horizontal=True
)

text_content = ""
source_name = "Dragon Audio"

if input_mode == "📄 Upload TXT":

    uploaded_file = st.file_uploader(
        "Upload your TXT file",
        type=["txt"]
    )

    if uploaded_file:

        try:

            text_content = uploaded_file.read().decode(
                "utf-8",
                errors="ignore"
            )

            source_name = os.path.splitext(
                uploaded_file.name
            )[0]

            st.success(
                f"📖 Loaded: {uploaded_file.name}"
            )

        except Exception as e:

            st.error(
                f"Could not read file: {e}"
            )

else:

    text_content = st.text_area(
        "Paste your text here",
        height=300,
        placeholder="Paste your novel, story, article or any text here..."
    )

st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# CONVERT BUTTON
# ============================================================

if st.button(
    "🐉 Convert to MP3",
    type="primary",
    use_container_width=True
):

    if not text_content.strip():

        st.warning(
            "⚠️ Please upload a TXT file or paste some text first."
        )

    else:

        audio_file = synthesize(
            text_content,
            source_name,
            voice,
            speed,
            pitch,
            volume,
            natural_pauses
        )

        if audio_file:

            # =================================================
            # RESULT
            # =================================================

            st.markdown(
                '<div class="dragon-card">',
                unsafe_allow_html=True
            )

            st.markdown(
                '<div class="result-title">🎧 Your Dragon Audio</div>',
                unsafe_allow_html=True
            )

            # Audio player
            with open(audio_file, "rb") as audio:

                audio_bytes = audio.read()

            st.audio(
                audio_bytes,
                format="audio/mp3"
            )

            # Download
            download_name = re.sub(
                r'[\\/:*?"<>|]+',
                "_",
                source_name
            )

            st.download_button(
                "⬇️ Download MP3",
                data=audio_bytes,
                file_name=f"{download_name}.mp3",
                mime="audio/mpeg",
                use_container_width=True
            )

            st.markdown(
                "</div>",
                unsafe_allow_html=True
            )

            # =================================================
            # ADSENSE
            # =================================================

            render_adsense_ad()

            # =================================================
            # CLEANUP
            # =================================================

            try:
                os.remove(audio_file)

            except Exception:
                pass


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div style="
        text-align:center;
        color:#8f849e;
        font-size:13px;
        padding:25px 0;
    ">
        🐉 The Dragon Audio Converts
        <br>
        Turn your words into sound.
    </div>
    """,
    unsafe_allow_html=True
)
