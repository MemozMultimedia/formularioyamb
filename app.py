
import streamlit as st
import cv2
import numpy as np
import tempfile
import zipfile
import os
from PIL import Image

st.set_page_config(page_title="MZM Stillz Pro", layout="wide")

# 🎨 DISEÑO CORPORATIVO CENTRALIZADO
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;700;800&display=swap');

.stApp {
    background: linear-gradient(135deg, #020205 0%, #08081a 100%) !important;
    color: #f0f0f0;
    font-family: 'Inter', sans-serif;
}

.stApp::before {
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background-image: url('https://raw.githubusercontent.com/MemozMultimedia/mzmstill/main/MZM.PNG');
    background-size: 250px;
    background-repeat: repeat;
    opacity: 0.02;
    filter: blur(2px) grayscale(1);
    z-index: -1;
}

/* CENTRALIZACIÓN TOTAL DEL HEADER */
.main-header {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    width: 100%;
    margin-bottom: 40px;
}

.steam-effect {
    display: flex;
    justify-content: center;
    filter: drop-shadow(0 0 15px rgba(255,255,255,0.1));
    margin-bottom: 20px;
}

.steam-effect::after {
    content: '';
    position: absolute;
    width: 200px; height: 200px;
    background-image: url('https://raw.githubusercontent.com/MemozMultimedia/mzmstill/main/MZM.PNG');
    background-size: contain;
    background-repeat: no-repeat;
    opacity: 0;
    filter: blur(15px) brightness(2);
    animation: steam 4s infinite ease-in-out;
    z-index: -1;
}

@keyframes steam {
    0% { transform: translateY(0) scale(1); opacity: 0; }
    50% { transform: translateY(-10px) scale(1.05); opacity: 0.3; }
    100% { transform: translateY(-20px) scale(1.1); opacity: 0; }
}

h1 {
    background: linear-gradient(180deg, #ffffff 0%, #888888 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800 !important;
    font-size: 4.5rem !important;
    letter-spacing: -3px;
    margin: 0 !important;
}

.card {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.07);
    border-radius: 24px;
    padding: 40px;
    backdrop-filter: blur(20px);
    margin: 0 auto 30px auto;
    max-width: 800px;
    box-shadow: 0 20px 50px rgba(0,0,0,0.5);
}
</style>
""", unsafe_allow_html=True)

# HEADER CENTRALIZADO
st.markdown('<div class="main-header">', unsafe_allow_html=True)
st.markdown('<div class="steam-effect">', unsafe_allow_html=True)
if os.path.exists("MZM.PNG"):
    st.image("MZM.PNG", width=220)
st.markdown('</div>', unsafe_allow_html=True)
st.markdown('<h1>MZM Stillz</h1>', unsafe_allow_html=True)
st.markdown("<p style='color: #666; font-size: 1.1rem; letter-spacing: 8px; text-transform: uppercase;'>High Fidelity Extraction</p>", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# CONTENIDO
st.markdown('<div class="card">', unsafe_allow_html=True)
uploaded_file = st.file_uploader("", type=["mov","mp4","avi"], label_visibility="collapsed")
st.markdown('</div>', unsafe_allow_html=True)

def score(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return cv2.Laplacian(gray, cv2.CV_64F).var()

if uploaded_file:
    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(uploaded_file.read())
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.video(tfile.name)
    num = st.slider("Selection Density", 4, 30, 12)
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("Process Master Stills"):
        with st.status("Neural Engine Processing...", expanded=True):
            cap = cv2.VideoCapture(tfile.name)
            frames, scores = [], []
            count = 0
            while True:
                ret, frame = cap.read()
                if not ret: break
                if count % 10 == 0:
                    frames.append(frame)
                    scores.append(score(frame))
                count += 1
            cap.release()
            idx = np.argsort(scores)[-num:]
            best = [frames[i] for i in idx]
            os.makedirs("output", exist_ok=True)
            paths = []
            for i, f in enumerate(best):
                p = f"output/frame_{i}.png"
                cv2.imwrite(p, f)
                paths.append(p)
            st.success("Neural Extraction Complete.")
            cols = st.columns(4)
            for i, p in enumerate(paths):
                cols[i % 4].image(Image.open(p), use_column_width=True)
            zip_path = f"{os.path.splitext(uploaded_file.name)[0]}_mzm_master.zip"
            with zipfile.ZipFile(zip_path, "w") as z:
                for p in paths: z.write(p)
            st.download_button("Download Master Package", open(zip_path, "rb"), file_name=zip_path)
