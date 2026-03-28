
import streamlit as st
import cv2
import numpy as np
import tempfile
import zipfile
import os
from PIL import Image

st.set_page_config(page_title="MZM Stillz Pro", layout="wide")

# 🔱 MINIMALIST FUTURISTIC CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;700;800&display=swap');

.stApp {
    background: #050508 !important;
    color: #f0f0f0;
    font-family: 'Inter', sans-serif;
}

/* Subtle Background Detail */
.stApp::before {
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background-image: url('https://raw.githubusercontent.com/MemozMultimedia/mzmstill/main/MZM.PNG');
    background-size: 180px;
    background-repeat: repeat;
    opacity: 0.015;
    z-index: -1;
}

/* Compact Layout */
.block-container { padding-top: 1rem !important; padding-bottom: 0rem !important; }
.main-header { display: flex; flex-direction: column; align-items: center; margin-bottom: 20px; }

.logo-img { 
    filter: drop-shadow(0 0 10px rgba(255,255,255,0.2));
    margin-bottom: 10px;
}

h1 {
    background: linear-gradient(180deg, #fff 30%, #555 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800 !important;
    font-size: 3rem !important;
    letter-spacing: -2px;
    margin: 0 !important;
}

.card {
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 15px;
    padding: 20px;
    backdrop-filter: blur(10px);
    margin-bottom: 15px;
}

/* Modern Minimalist UI Elements */
.stSlider [data-baseweb="slider"] { margin-top: 10px; }
.stButton>button {
    width: 100%;
    background: linear-gradient(90deg, #fff, #888) !important;
    color: #000 !important;
    border: none !important;
    font-weight: 700 !important;
    border-radius: 10px !important;
    padding: 0.5rem !important;
}
</style>
""", unsafe_allow_html=True)

# HEADER
st.markdown('<div class="main-header">', unsafe_allow_html=True)
if os.path.exists("MZM.PNG"):
    st.image("MZM.PNG", width=140)
st.markdown('<h1>MZM Stillz</h1>', unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# INPUT SECTION
uploaded_file = st.file_uploader("", type=["mov","mp4","avi"], label_visibility="collapsed")

def get_sharpness(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return cv2.Laplacian(gray, cv2.CV_64F).var()

if uploaded_file:
    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(uploaded_file.read())
    
    col_v, col_s = st.columns([1.5, 1])
    
    with col_v:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.video(tfile.name)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_s:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        num = st.slider("Density", 4, 24, 8)
        process = st.button("EXTRACT HIGH FIDELITY")
        st.markdown('</div>', unsafe_allow_html=True)

    if process:
        with st.status("Neural Focus Scanning...", expanded=False):
            cap = cv2.VideoCapture(tfile.name)
            frames, scores = [], []
            count = 0
            while True:
                ret, frame = cap.read()
                if not ret: break
                if count % 8 == 0: # Check more frequently for better selection
                    frames.append(frame)
                    scores.append(get_sharpness(frame))
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
            
            st.success(f"Generated {num} Ultra-Sharp Stills")
            cols = st.columns(4)
            for i, p in enumerate(paths):
                cols[i % 4].image(Image.open(p), use_column_width=True)
            
            zip_path = f"{os.path.splitext(uploaded_file.name)[0]}_mzm.zip"
            with zipfile.ZipFile(zip_path, "w") as z:
                for p in paths: z.write(p)
            st.download_button("DOWNLOAD PACKAGE", open(zip_path, "rb"), file_name=zip_path)
