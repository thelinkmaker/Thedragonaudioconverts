import streamlit as st
import edge_tts
import asyncio
import tempfile
import os
import re

st.set_page_config(page_title="The Dragon Audio Converts", page_icon="🐉", layout="centered")

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
.stProgress > div > div > div > div { background: linear-gradient(90deg, #8b0000, #ff4500, #ffd700); }
.stSuccess { background-color: rgba(255, 215, 0, 0.1); color: #ffd700 !important; border: 1px solid #ffd700; }
.stError { background-color: rgba(139, 0, 0, 0.2); color: #ff4500 !important; border: 1px solid #ff4500; }
</style>
""", unsafe_allow_html=True)

st.title("🐉 The Dragon Audio Converts")
st.markdown("<h3 style='text-align: center; color: #ff8c00;'>Forge your text into golden audio. Unleash the fire of AI voices.</h3>", unsafe_allow_html=True)
st.markdown("---")

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

with st.sidebar:
    st.header("🔥 The Forge Settings")
    voice = st.selectbox(
        "Choose the Voice of the Dragon",
        ["en-US-AriaNeural", "en-US-GuyNeural", "en-GB-SoniaNeural", "en-AU-NatashaNeural"],
        format_func=lambda x: x.replace("Neural", "").replace("-", " | ")
    )
    st.info("💡 **Tip:** Split massive novels into chapters under 5,000 words for the fastest forging.")

st.markdown("### 📜 Offer Your Scroll")
uploaded_file = st.file_uploader("Upload your novel (.txt)", type=["txt"], label_visibility="collapsed")

if uploaded_file is not None:
    text_content = uploaded_file.read().decode("utf-8")
    st.success(f"✅ Scroll Accepted: '{uploaded_file.name}' ({len(text_content):,} characters)")
    
    if st.button("🔥 Ignite the Forge (Convert to MP3)", type="primary", use_container_width=True):
        try:
            chunks = chunk_text(text_content)
            all_audio = b""
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, chunk in enumerate(chunks):
                status_text.text(f"🐉 Breathing fire on part {i+1} of {len(chunks)}...")
                
                with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
                    communicate = edge_tts.Communicate(chunk, voice)
                    asyncio.run(communicate.save(tmp.name))
                    
                    with open(tmp.name, "rb") as f:
                        all_audio += f.read()
                    os.unlink(tmp.name)
                
                progress_bar.progress((i + 1) / len(chunks))
            
            progress_bar.empty()
            status_text.empty()
            
            st.balloons()
            st.success("🏆 The Forging is Complete! Your golden audio is ready.")
            
            st.audio(all_audio, format="audio/mp3")
            st.download_button(
                label="⬇️ Claim Your MP3 Treasure",
                data=all_audio,
                file_name=f"{uploaded_file.name.rsplit('.', 1)[0]}_dragon_audio.mp3",
                mime="audio/mpeg",
                use_container_width=True
            )
            
        except Exception as e:
            st.error(f"❌ The fire died out. Error: {str(e)}")
else:
    st.info("👆 Drop your .txt scroll into the hoard above to begin.")
