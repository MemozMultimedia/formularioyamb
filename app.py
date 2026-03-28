import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd
import re
import os

# =====================
# DB SETUP
# =====================
conn = sqlite3.connect("datos_app.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS registros (
    id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT UNIQUE, correo TEXT UNIQUE,
    telefono TEXT UNIQUE, ocupacion TEXT, fecha TEXT)""")
conn.commit()

def validar_email(email):
    return re.match(r'^\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', email)

def guardar(nombre, correo, telefono, ocupacion, fecha):
    if nombre and correo and validar_email(correo):
        try:
            cursor.execute("SELECT * FROM registros WHERE nombre=? OR correo=? OR telefono=?", (nombre, correo, telefono))
            if cursor.fetchone(): return "duplicate"
            cursor.execute("INSERT INTO registros (nombre, correo, telefono, ocupacion, fecha) VALUES (?, ?, ?, ?, ?)",
                           (nombre, correo, telefono, ocupacion, fecha))
            conn.commit()
            return "success"
        except sqlite3.IntegrityError: return "duplicate"
    return "error"

def obtener_datos():
    return pd.read_sql_query("SELECT nombre, correo, telefono, ocupacion, fecha FROM registros ORDER BY fecha DESC", conn)

# =====================
# DYNAMIC ARTISTIC UI & METADATA
# =====================
st.set_page_config(
    page_title="YAMB | Viviendo la experiencia del barrio",
    page_icon="🔥",
    layout="wide"
)

# METADATOS PARA EL LINK (Social Media Preview)
st.markdown("""
    <head>
        <meta property="og:title" content="YAMB | Únete a nuestra familia" />
        <meta property="og:description" content="Vive la experiencia del barrio. Regístrate y apoya a jóvenes talentos en la música y el arte. Compra con propósito, apoya el talento." />
        <meta property="og:image" content="https://raw.githubusercontent.com/MemozMultimedia/mzmstill/main/hf_20260328_023420_f7d7d2a9-1955-4269-a97a-c444fbbd7a73.png" />
        <meta property="og:type" content="website" />
        <meta name="description" content="Registro oficial de la familia YAMB. Apoyando el arte y la música del barrio." />
    </head>
""", unsafe_allow_html=True)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;700;900&display=swap');

html, body, [class*=\"st-expander\"] { font-family: 'Inter', sans-serif; }

.stApp {
    background: radial-gradient(circle at 50% 50%, #1a0000 0%, #000000 100%) !important;
    overflow: hidden;
}

.stApp::before {
    content: '';
    position: fixed;
    top: 0; left: 0; width: 100%; height: 100%;
    background: url("https://raw.githubusercontent.com/MemozMultimedia/mzmstill/main/hf_20260328_023420_f7d7d2a9-1955-4269-a97a-c444fbbd7a73.png");
    background-size: cover; opacity: 0.12; filter: contrast(1.2) brightness(0.8);
    z-index: -1;
}

.stApp::after {
    content: '';
    position: fixed;
    top: -50%; left: -50%; width: 200%; height: 200%;
    background: radial-gradient(circle, rgba(255,0,0,0.08) 0%, transparent 40%);
    animation: pulse 10s infinite alternate ease-in-out;
    z-index: -1;
}

@keyframes pulse {
    0% { transform: translate(-10%, -10%); }
    100% { transform: translate(10%, 10%); }
}

.main-card {
    background: rgba(20, 20, 20, 0.4);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 40px;
    padding: 0px;
    backdrop-filter: blur(25px);
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
    margin-top: 10px;
    overflow: hidden;
}

.unified-header {
    background: linear-gradient(135deg, rgba(255,0,0,0.8) 0%, rgba(100,0,0,0.9) 100%);
    padding: 40px 20px;
    text-align: center;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.header-text {
    font-weight: 900; font-size: 1.6rem; color: white;
    text-shadow: 0 2px 10px rgba(0,0,0,0.3);
    letter-spacing: -1px;
}

.yt-pill {
    background: white; color: black !important;
    padding: 10px 25px; border-radius: 50px;
    font-weight: 900; font-size: 0.85rem;
    box-shadow: 0 10px 20px rgba(0,0,0,0.2);
    transition: 0.3s;
}

.yt-pill:hover { transform: scale(1.1); box-shadow: 0 0 30px rgba(255,255,255,0.4); }

.form-body { padding: 45px; }

.stButton>button {
    background: white !important; color: black !important;
    border-radius: 15px !important; padding: 18px !important;
    font-weight: 900 !important; border: none !important;
    transition: 0.4s !important;
}

.stButton>button:hover {
    background: #ff0000 !important; color: white !important;
    transform: translateY(-3px); box-shadow: 0 10px 20px rgba(255,0,0,0.4) !important;
}

input { background: rgba(255,255,255,0.05) !important; color: white !important; border: 1px solid rgba(255,255,255,0.1) !important; border-radius: 12px !important; }

.footer-message {
    margin-top: 40px;
    padding: 40px;
    text-align: center;
    background: rgba(255, 0, 0, 0.05);
    border-radius: 30px;
    border: 1px solid rgba(255, 0, 0, 0.2);
    backdrop-filter: blur(10px);
}

.footer-title { font-weight: 900; font-size: 1.4rem; color: #ff0000; margin-bottom: 15px; }
.footer-text { font-size: 1rem; color: #cccccc; line-height: 1.6; }
.footer-highlight { font-weight: 700; color: white; margin-top: 15px; }
</style>
""", unsafe_allow_html=True)

top_l, top_r = st.columns([9, 1])
with top_r: admin_mode = st.toggle("🔐")

if admin_mode:
    st.markdown("<h1 style='text-align: center; color: white;'>📂 Insight Center</h1>", unsafe_allow_html=True)
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        u, p = st.text_input("Key"), st.text_input("Pass", type="password")
        if u == "Yamb" and p == "LavueltaesDios1*":
            df = obtener_datos()
            st.dataframe(df, use_container_width=True)
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 EXPORTAR DB", csv, "yamb_pro.csv", "text/csv", use_container_width=True)
else:
    st.markdown("<h1 style='text-align: center; color: white; font-weight:900; font-size: 3.5rem; letter-spacing: -3px;'>ÚNETE A NUESTRA FAMILIA <span style='color:#ff0000;'>YAMB</span></h1>", unsafe_allow_html=True)

    _, mid, _ = st.columns([1, 1.6, 1])
    with mid:
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        st.markdown('''
            <div class="unified-header">
                <div class="header-text">VIVIENDO LA EXPERIENCIA DEL BARRIO</div><br>
                <a href="https://www.youtube.com/@YoAmoMiBarrioOFICIAL" target="_blank" class="yt-pill">CANAL OFICIAL YAMB TV ▶️</a>
            </div>
        ''', unsafe_allow_html=True)
        
        st.markdown('<div class="form-body">', unsafe_allow_html=True)
        with st.form("compact_form", clear_on_submit=True):
            n = st.text_input("Nombre completo", placeholder="Tu nombre")
            c = st.text_input("Email", placeholder="tucorreo@ejemplo.com")
            t = st.text_input("WhatsApp", placeholder="+57...")
            o = st.text_input("¿Qué haces? (Ocupación)", placeholder="Ej: Artista, Diseñador")
            sub = st.form_submit_button("✅ UNIRME AHORA", use_container_width=True)

        if sub:
            status = guardar(n, c, t, o, datetime.now().strftime('%Y-%m-%d'))
            if status == "success": st.balloons(); st.success("¡Bienvenido a la verdadera vuelta!")
            elif status == "duplicate": st.warning("Tus datos ya están registrados.")
            else: st.error("Completa los campos correctamente.")
        st.markdown('</div></div>', unsafe_allow_html=True)

        st.markdown('''
            <div class="footer-message">
                <div class="footer-title">GRACIAS POR TU COMPRA</div>
                <div class="footer-text">
                    CADA PRODUCTO DE YAMB TIENE UN PROPÓSITO.<br>
                    CON TU COMPRA, APOYAS A JÓVENES TALENTOS EN LA MÚSICA Y EL ARTE, AYUDÁNDOLOS A CRECER, CREAR Y COMPARTIR SU PASIÓN CON EL MUNDO.
                </div>
                <div class="footer-highlight">
                    COMPRASTE CON PROPÓSITO. APOYASTE EL TALENTO.
                </div>
            </div>
        ''', unsafe_allow_html=True)
