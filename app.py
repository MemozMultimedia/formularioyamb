import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd
import re
import os

# =====================
# DB SETUP (PROTECTED)
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
# MASTER URBAN BRANDING
# =====================
st.set_page_config(
    page_title="YAMB | Viviendo la experiencia del barrio",
    page_icon="❌",
    layout="wide"
)

st.markdown("""
    <head>
        <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22 fill=%22red%22 font-weight=%22bold%22>Y</text></svg>">
    </head>
""", unsafe_allow_html=True)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;700;800;900&display=swap');
html, body, [class*=\"st-expander\"] { font-family: 'Inter', sans-serif; }

.block-container { padding-top: 1rem !important; }
header { visibility: hidden; }

.stApp {
    background: radial-gradient(circle at 50% 50%, #1a0000 0%, #000000 100%) !important;
}
.stApp::before {
    content: '';
    position: fixed;
    top: 0; left: 0; width: 100%; height: 100%;
    background: url(\"https://raw.githubusercontent.com/MemozMultimedia/mzmstill/main/hf_20260328_023420_f7d7d2a9-1955-4269-a97a-c444fbbd7a73.png\");
    background-size: cover; opacity: 0.12; filter: brightness(0.7);
    z-index: -1;
}

.main-card {
    background: rgba(20, 20, 20, 0.4);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 40px;
    backdrop-filter: blur(25px);
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
    overflow: hidden;
}

/* MASTER URBAN HEADER */
.unified-header {
    background: linear-gradient(135deg, #220000 0%, #000000 100%);
    padding: 35px 20px;
    text-align: center;
    border-bottom: 2px solid #ff0000;
    position: relative;
}
.unified-header::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0; width: 100%; height: 2px;
    background: #ff0000; box-shadow: 0 0 15px #ff0000;
}
.header-text {
    font-weight: 900; 
    font-size: 1.8rem; 
    background: linear-gradient(to bottom, #ffffff 40%, #888888 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: 4px;
    margin-bottom: 15px;
    text-transform: uppercase;
    font-style: italic;
    filter: drop-shadow(0 0 5px rgba(255,255,255,0.2));
}
.yt-pill {
    background: #ff0000; color: white !important;
    padding: 12px 25px; border-radius: 4px;
    font-weight: 900; font-size: 0.85rem;
    text-decoration: none;
    display: inline-block;
    transition: 0.3s;
    border: 1px solid rgba(255,255,255,0.1);
}
.yt-pill:hover { background: white; color: black !important; box-shadow: 0 0 20px white; }

.form-body { padding: 40px; }

.stButton>button {
    background: white !important; color: black !important;
    border-radius: 12px !important; padding: 15px !important;
    font-weight: 900 !important; border: none !important;
    transition: 0.4s !important;
    text-transform: uppercase;
}
.stButton>button:hover {
    background: #ff0000 !important; color: white !important;
    transform: translateY(-2px);
}
input { background: rgba(255,255,255,0.05) !important; color: white !important; border: 1px solid rgba(255,255,255,0.1) !important; border-radius: 10px !important; }
</style>
""", unsafe_allow_html=True)

# Admin Sidebar
admin_mode = st.sidebar.toggle("🔐 Admin Access")
if admin_mode:
    u = st.text_input("Master Key")
    p = st.text_input("Token", type="password")
    if u == "Yamb" and p == "LavueltaesDios1*":
        st.dataframe(obtener_datos(), use_container_width=True)
else:
    st.markdown("<h1 style='text-align: center; color: white; font-weight:900; font-size: 3rem; letter-spacing: -3px;'>Únete a nuestra familia <span style='color:#ff0000;'>YAMB</span></h1>", unsafe_allow_html=True)
    _, mid, _ = st.columns([1, 1.5, 1])
    with mid:
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        st.markdown('''
            <div class="unified-header">
                <div class="header-text">VIVIENDO LA EXPERIENCIA DEL BARRIO</div>
                <a href="https://www.youtube.com/@YoAmoMiBarrioOFICIAL" target="_blank" class="yt-pill">CANAL OFICIAL YAMB TV ▶️</a>
            </div>
        ''', unsafe_allow_html=True)
        st.markdown('<div class="form-body">', unsafe_allow_html=True)
        with st.form("master_form", clear_on_submit=True):
            n = st.text_input("Nombre completo")
            c = st.text_input("Email")
            t = st.text_input("WhatsApp")
            o = st.text_input("Ocupación")
            sub = st.form_submit_button("UNIRME AHORA", use_container_width=True)
        if sub:
            status = guardar(n, c, t, o, datetime.now().strftime('%Y-%m-%d'))
            if status == "success": st.balloons(); st.success("¡Bienvenido a la verdadera vuelta!")
            else: st.error("Error en el registro.")
        st.markdown('</div></div>', unsafe_allow_html=True)
