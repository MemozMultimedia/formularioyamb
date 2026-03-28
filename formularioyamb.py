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
# UI MODERN LOOK & FEEL
# =====================
st.set_page_config(page_title="YAMB | Viviendo la experiencia del barrio", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;700;900&display=swap');

html, body, [class*=\"st-expander\"] { font-family: 'Inter', sans-serif; }

.stApp {
    background: linear-gradient(rgba(0, 0, 0, 0.6), rgba(0, 0, 0, 0.6)),
                url("https://raw.githubusercontent.com/MemozMultimedia/mzmstill/main/hf_20260328_023420_f7d7d2a9-1955-4269-a97a-c444fbbd7a73.png") no-repeat center center fixed !important;
    background-size: cover !important;
}

.block-container { padding-top: 1rem !important; }
header { visibility: hidden; }

.main-card {
    background: rgba(10, 10, 10, 0.9);
    border: 1px solid rgba(255, 0, 0, 0.4);
    border-radius: 32px;
    padding: 0px;
    backdrop-filter: blur(30px);
    box-shadow: 0 0 70px rgba(255, 0, 0, 0.25);
    margin-top: 10px;
    overflow: hidden;
}

.unified-header {
    background: linear-gradient(135deg, #ff0000 0%, #600000 100%);
    padding: 35px 25px;
    text-align: center;
    border-bottom: 2px solid rgba(255, 255, 255, 0.1);
}

.header-text {
    font-weight: 900;
    font-size: 1.5rem;
    color: white;
    letter-spacing: -1px;
    margin-bottom: 15px;
    text-transform: uppercase;
}

.yt-pill {
    background: rgba(255, 255, 255, 1);
    color: #ff0000 !important;
    text-decoration: none !important;
    padding: 12px 24px;
    border-radius: 50px;
    font-weight: 900;
    font-size: 0.9rem;
    box-shadow: 0 4px 15px rgba(255, 255, 255, 0.3);
    transition: 0.3s ease-in-out;
}

.yt-pill:hover { transform: scale(1.1); box-shadow: 0 0 25px rgba(255, 255, 255, 0.5); }

/* Insight Center Styling */
.stat-card {
    background: rgba(255, 255, 255, 0.05);
    border-left: 4px solid #ff0000;
    padding: 20px;
    border-radius: 12px;
    margin-bottom: 10px;
}

.stDataFrame { border-radius: 16px; overflow: hidden; border: 1px solid rgba(255,0,0,0.2); }

.form-body { padding: 40px; }

.stButton>button {
    background: linear-gradient(90deg, #ff0000, #b30000) !important;
    color: white !important;
    border-radius: 12px !important;
    padding: 15px !important;
    font-weight: 900 !important;
    border: none !important;
    font-size: 1.1rem !important;
}

input {
    background: rgba(255,255,255,0.07) !important;
    color: white !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 10px !important;
    padding: 12px !important;
}
</style>
""", unsafe_allow_html=True)

top_l, top_r = st.columns([9, 1])
with top_r: admin_mode = st.toggle("🔐", help="Insight Center Access")

if admin_mode:
    st.markdown("<h1 style='text-align: center; color: white; margin-bottom: 30px;'>📂 Insight <span style='color:#ff0000;'>Center</span></h1>", unsafe_allow_html=True)
    _, col_b, _ = st.columns([1, 1.5, 1])
    with col_b:
        u, p = st.text_input("Master Key"), st.text_input("Token", type="password")
        if u == "Yamb" and p == "LavueltaesDios1*":
            data = obtener_datos()
            c1, c2 = st.columns(2)
            with c1: st.markdown(f'<div class="stat-card"><h3>{len(data)}</h3><p>Miembros Totales</p></div>', unsafe_allow_html=True)
            with c2: st.markdown(f'<div class="stat-card"><h3>{datetime.now().strftime("%d/%m")}</h3><p>Última Sincronización</p></div>', unsafe_allow_html=True)
            st.dataframe(data, use_container_width=True)
        elif u or p: st.error("Acceso Denegado")
else:
    st.markdown("<h1 style='text-align: center; color: white; margin-bottom: 30px; font-weight:900;'>LA FAMILIA <span style='color:#ff0000;'>YAMB</span></h1>", unsafe_allow_html=True)

    _, mid, _ = st.columns([1, 1.8, 1])
    with mid:
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        st.markdown('''
            <div class="unified-header">
                <div class="header-text">VIVIENDO LA EXPERIENCIA DEL BARRIO</div>
                <a href="https://www.youtube.com/@YoAmoMiBarrioOFICIAL" target="_blank" class="yt-pill">CANAL OFICIAL YAMB TV ▶️</a>
            </div>
        ''', unsafe_allow_html=True)

        st.markdown('<div class="form-body">', unsafe_allow_html=True)
        with st.form("compact_form", clear_on_submit=True):
            n = st.text_input("Nombre completo", placeholder="Tu nombre aquí")
            c = st.text_input("Correo electrónico", placeholder="tucorreo@ejemplo.com")
            t = st.text_input("Teléfono", placeholder="WhatsApp")
            o = st.text_input("¿Qué haces? (Ocupación)", placeholder="Ej: Músico, Diseñador...")
            sub = st.form_submit_button("✅ UNIRME AHORA", use_container_width=True)

        if sub:
            status = guardar(n, c, t, o, datetime.now().strftime('%Y-%m-%d'))
            if status == "success": st.balloons(); st.success("¡Bienvenido a la verdadera vuelta!")
            elif status == "duplicate": st.warning("Tus datos ya están en la base.")
            else: st.error("Completa los campos para entrar.")
        st.markdown('</div></div>', unsafe_allow_html=True)
