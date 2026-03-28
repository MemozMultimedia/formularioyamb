
import streamlit as st
import cv2
import numpy as np
import tempfile
import zipfile
import os
from PIL import Image

st.set_page_config(page_title="Video Stills AI", layout="wide")

# 🎨 ESTILO PREMIUM
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0f0f14, #1c1c26);
    color: white;
}
h1 {
    font-size: 2.5rem;
    font-weight: 800;
}
.card {
    background: rgba(255,255,255,0.05);
    padding: 20px;
    border-radius: 20px;
    margin-bottom: 20px;
    backdrop-filter: blur(10px);
}
button[kind="primary"] {
    background: linear-gradient(90deg, #ff4da6, #ff0066);
    border-radius: 12px;
    border: none;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# HEADER
# Display the logo
st.image("MZM.PNG", width=200) # Adjust width as needed
st.title("MZM Stillz") # Updated title
st.caption("Genera capturas automáticamente")

# UPLOAD
st.markdown('<div class="card">', unsafe_allow_html=True)
uploaded_file = st.file_uploader("Arrastra tu video (.mov, .mp4, .avi)", type=["mov","mp4","avi"])
st.markdown('</div>', unsafe_allow_html=True)

def score(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    sharp = cv2.Laplacian(gray, cv2.CV_64F).var()
    bright = np.mean(gray)
    return sharp * 0.7 + bright * 0.3

if uploaded_file:
    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(uploaded_file.read())

    col1, col2 = st.columns([1,1])

    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("🎥 Preview")
        st.video(tfile.name)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        num = st.slider("Cantidad de imágenes", 5, 20, 10)
        st.markdown('</div>', unsafe_allow_html=True)

    if st.button("🚀 Generar Capturas PRO"):

        with st.status("Iniciando la generación de capturas...", expanded=True) as status:
            cap = cv2.VideoCapture(tfile.name)
            frames, scores = [], []
            count = 0

            status.update(label="Extrayendo frames del video...", state="running", expanded=True)
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                if count % 10 == 0:
                    frames.append(frame)
                    scores.append(score(frame))

                count += 1

            cap.release()

            status.update(label="Calculando nitidez y seleccionando las mejores capturas...", state="running", expanded=True)
            if not frames:
                st.error("No se pudieron extraer frames del video. Asegúrate de que el archivo no esté corrupto.")
                status.update(label="Error en la generación de capturas.", state="error")
            else:
                idx = np.argsort(scores)[-num:]
                best = [frames[i] for i in idx]

                status.update(label="Guardando capturas y preparando descarga...", state="running", expanded=True)
                os.makedirs("output", exist_ok=True)
                paths = []

                for i, f in enumerate(best):
                    p = f"output/frame_{i}.png"
                    cv2.imwrite(p, f)
                    paths.append(p)

                st.success("✅ Proceso Completado!")
                status.update(label="Proceso de generación de capturas completado.", state="complete", expanded=False)

                st.subheader("🖼️ Resultados")

                cols = st.columns(4)
                for i, p in enumerate(paths):
                    cols[i % 4].image(Image.open(p), width="stretch")

                # Dynamic zip filename
                original_filename_base = os.path.splitext(uploaded_file.name)[0]
                zip_path = f"{original_filename_base}_stills.zip"

                with zipfile.ZipFile(zip_path, "w") as z:
                    for p in paths:
                        z.write(p)

                with open(zip_path, "rb") as f:
                    st.download_button("📥 Descargar ZIP", f, file_name=zip_path)
