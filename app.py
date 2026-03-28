
import streamlit as st
import cv2
import numpy as np
import tempfile
import zipfile
import os
import base64
from PIL import Image
from io import BytesIO

st.set_page_config(page_title="MZM Stillz Pro", layout="wide")

# ✨ DYNAMIC FUTURISTIC UI WITH ANIMATED BACKGROUND
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');

/* Dynamic Background */
.stApp {
    background: radial-gradient(circle at 50% 50%, #0a0a12 0%, #050508 100%) !important;
    color: #f0f0f0;
    font-family: 'Inter', sans-serif;
    overflow: hidden;
}

.stApp::before {
    content: '';
    position: fixed;
    top: 0; left: 0; width: 100%; height: 100%;
    background: 
        radial-gradient(circle at 20% 30%, rgba(100, 100, 255, 0.05) 0%, transparent 50%),
        radial-gradient(circle at 80% 70%, rgba(255, 100, 255, 0.05) 0%, transparent 50%);
    animation: bgMove 15s infinite alternate ease-in-out;
    z-index: -1;
}

@keyframes bgMove {
    0% { transform: scale(1); opacity: 0.5; }
    100% { transform: scale(1.2); opacity: 0.8; }
}

/* Fix Logo Space */
.main-header { 
    display: flex; 
    flex-direction: column; 
    align-items: center; 
    padding-top: 50px;
    margin-bottom: 30px; 
    text-shadow: 0 0 20px rgba(255,255,255,0.1);
}

.block-container { padding-top: 0rem !important; }

/* Glassmorphism Cards */
.card { 
    background: rgba(255, 255, 255, 0.03); 
    border: 1px solid rgba(255, 255, 255, 0.08); 
    border-radius: 16px; 
    padding: 20px; 
    margin-bottom: 20px; 
    backdrop-filter: blur(12px);
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
}

.img-container { 
    border-radius: 10px; 
    overflow: hidden; 
    border: 1px solid rgba(255,255,255,0.08); 
    background: #000; 
    margin-bottom: 12px; 
    transition: transform 0.3s ease;
}
.img-container:hover { transform: scale(1.02); }

/* GLOSSY GLOW BUTTONS */
.download-btn { 
    display: inline-block; 
    padding: 10px 15px; 
    background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%); 
    color: #fff !important; 
    text-decoration: none !important; 
    border-radius: 10px; 
    font-size: 0.85rem; 
    font-weight: 600;
    text-align: center; 
    width: 100%; 
    border: 1px solid rgba(255,255,255,0.15);
    transition: 0.3s all ease; 
    position: relative;
    overflow: hidden;
}

.download-btn:hover { 
    background: rgba(255,255,255,0.15); 
    border-color: rgba(255,255,255,0.6);
    box-shadow: 0 0 25px rgba(255,255,255,0.2); 
}

.download-btn::after {
    content: '';
    position: absolute;
    top: -50%; left: -50%;
    width: 200%; height: 200%;
    background: linear-gradient(45deg, transparent, rgba(255,255,255,0.15), transparent);
    transform: rotate(45deg);
    transition: 0.6s;
}

.download-btn:hover::after { left: 100%; }

.stButton>button {
    background: #ffffff !important;
    color: #000000 !important;
    font-weight: 800 !important;
    border-radius: 12px !important;
    border: none !important;
    padding: 0.7rem !important;
    transition: 0.3s ease;
}
.stButton>button:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(255,255,255,0.3); }

/* Custom Sidebar & Sliders */
.stSlider [data-baseweb="slider"] { padding: 10px 0; }
</style>
""", unsafe_allow_html=True)

# FUNCTIONS
def get_sharpness(img):
    return cv2.Laplacian(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), cv2.CV_64F).var()

def get_image_download_link(img, filename, text):
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    href = f'<a href="data:file/png;base64,{img_str}" download="{filename}" class="download-btn">{text}</a>'
    return href

# HEADER
st.markdown('<div class="main-header">', unsafe_allow_html=True)
if os.path.exists("MZM.PNG"): st.image("MZM.PNG", width=150)
st.markdown('<h1 style="font-size: 3.5rem; margin:0; letter-spacing:-2px; font-weight:800; background: linear-gradient(white, #aaa); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">MZM Stillz</h1>', unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# UI
uploaded_file = st.file_uploader("", type=["mov","mp4","avi"], label_visibility="collapsed")

if uploaded_file:
    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(uploaded_file.read())
    
    c1, c2 = st.columns([1.3, 1])
    with c1: 
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.video(tfile.name)
        st.caption("Tip: 📺 Use control bar for Full Screen.")
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("⚙️ Extraction Settings")
        num = st.slider("Density of Stills", 4, 48, 12)
        if st.button("⚡ START NEURAL SCAN", use_container_width=True):
            with st.status("Processing High Fidelity Frames...", expanded=False):
                cap = cv2.VideoCapture(tfile.name)
                frames, scores = [], []
                count = 0
                while True:
                    ret, frame = cap.read()
                    if not ret: break
                    if count % 8 == 0:
                        frames.append(frame)
                        scores.append(get_sharpness(frame))
                    count += 1
                cap.release()
                idx = np.argsort(scores)[-num:]
                st.session_state['stills'] = [frames[i] for i in idx]
                st.session_state['file_name'] = os.path.splitext(uploaded_file.name)[0]
        st.markdown('</div>', unsafe_allow_html=True)

if 'stills' in st.session_state:
    st.markdown("--- ")
    zip_path = f"{st.session_state['file_name']}_mzm_package.zip"
    with zipfile.ZipFile(zip_path, "w") as z:
        for i, f in enumerate(st.session_state['stills']):
            p = f"frame_{i}.png"; cv2.imwrite(p, f); z.write(p); os.remove(p)
    
    with open(zip_path, "rb") as f:
        st.download_button("📦 DOWNLOAD COMPLETE MASTER PACKAGE", f, file_name=zip_path, type="primary", use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    cols = st.columns(4)
    for i, frame in enumerate(st.session_state['stills']):
        with cols[i % 4]:
            st.markdown('<div class="img-container">', unsafe_allow_html=True)
            pil_img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            st.image(pil_img, use_column_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown(get_image_download_link(pil_img, f"still_{i}.png", f"⤓ Download Still {i+1}"), unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
