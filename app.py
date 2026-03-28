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
    if not nombre or not correo or not validar_email(correo):
        return "error"
    try:
        cursor.execute("SELECT * FROM registros WHERE nombre=? OR correo=? OR telefono=?", (nombre, correo, telefono))
        if cursor.fetchone(): return "duplicate"
        cursor.execute("INSERT INTO registros (nombre, correo, telefono, ocupacion, fecha) VALUES (?, ?, ?, ?, ?)",
                       (nombre, correo, telefono, ocupacion, fecha))
        conn.commit()
        return "success"
    except sqlite3.IntegrityError: return "duplicate"

def obtener_datos():
    return pd.read_sql_query("SELECT nombre, correo, telefono, ocupacion, fecha FROM registros ORDER BY fecha DESC", conn)

# =====================
# UI MASTER BRANDING
# =====================
st.set_page_config(page_title="YAMB | Experience", page_icon="❌", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;700;800;900&family=Source+Sans+3:wght@400;700;900&display=swap');
html, body { font-family: 'Inter', sans-serif; background-color: #000; }

.admin-font { font-family: 'Source Sans 3', sans-serif !important; }
.block-container { padding-top: 1rem !important; }
header { visibility: hidden; }

.stApp {
    background: radial-gradient(circle at 50% 50%, #1a0000 0%, #000000 100%) !important;
}

.main-card {
    background: rgba(10, 10, 10, 0.6);
    border: 1px solid rgba(255, 0, 0, 0.2);
    border-radius: 40px;
    backdrop-filter: blur(35px);
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.8);
    padding: 0px; overflow: hidden;
}

.unified-header {
    background: linear-gradient(135deg, #220000 0%, #000000 100%);
    padding: 35px 20px; text-align: center; border-bottom: 2px solid #ff0000;
}

.header-text { font-weight: 900; font-size: 1.8rem; color: white; letter-spacing: 4px; }

.yt-pill {
    background: #ff0000; padding: 12px 30px; border-radius: 5px;
    font-weight: 900; color: white !important; text-decoration: none !important;
    display: inline-block; transition: 0.4s; box-shadow: 0 0 15px rgba(255,0,0,0.5);
}

.stButton>button {
    background: white !important; color: black !important;
    border-radius: 12px !important; font-weight: 900 !important;
    animation: pulseGlow 2s infinite ease-in-out !important;
}

@keyframes pulseGlow {
    0% { box-shadow: 0 0 5px rgba(255,255,255,0.2); }
    50% { box-shadow: 0 0 25px rgba(255,0,0,0.8); }
    100% { box-shadow: 0 0 5px rgba(255,255,255,0.2); }
}

.social-footer { text-align: center; margin-top: 50px; padding: 20px; border-top: 1px solid rgba(255,255,255,0.1); }
.social-icon { color: white; font-size: 1.5rem; margin: 0 15px; text-decoration: none; opacity: 0.6; transition: 0.3s; }
.social-icon:hover { opacity: 1; color: #ff0000; text-shadow: 0 0 10px #ff0000; }
</style>
""", unsafe_allow_html=True)

col_t1, col_t2 = st.columns([9, 1])
with col_t2: admin_trigger = st.toggle("🔐")

if admin_trigger:
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, mid_admin, _ = st.columns([1, 1.2, 1])
    with mid_admin:
        st.markdown("<div class='admin-font' style='text-align: center; color: white; font-weight: 900; margin-bottom: 40px; font-size: 1.8rem;'>🔐 INSIGHT CENTER</div>", unsafe_allow_html=True)
        with st.form("admin_auth"):
            u, p = st.text_input("MASTER IDENTIFICATION"), st.text_input("SECURITY TOKEN", type="password")
            login = st.form_submit_button("🚀 INITIALIZE ACCESS", use_container_width=True)
        if login and u == "Yamb" and p == "LavueltaesDios1*":
            st.session_state["auth"] = True
        if st.session_state.get("auth"):
            df_export = obtener_datos()
            st.dataframe(df_export, use_container_width=True)
            csv = df_export.to_csv(index=False).encode('utf-8')
            st.download_button("📥 DESCARGAR BASE DE DATOS (CSV)", data=csv, file_name='yamb_data.csv', mime='text/csv', use_container_width=True)
else:
    st.markdown("<div style='text-align: center; color: white; font-weight:900; font-size: 3rem; margin-bottom: 30px;'>Únete a nuestra familia <span style='color:#ff0000;'>YAMB</span></div>", unsafe_allow_html=True)
    _, mid, _ = st.columns([1, 1.5, 1])
    with mid:
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        st.markdown('<div class="unified-header"><div class="header-text">EXPERIENCIA DEL BARRIO</div><br><a href="https://www.youtube.com/@YoAmoMiBarrioOFICIAL" class="yt-pill">YAMB TV ▶️</a></div>', unsafe_allow_html=True)
        with st.form("reg_form", clear_on_submit=True):
            n = st.text_input("Nombre completo")
            c = st.text_input("Email")
            t = st.text_input("WhatsApp")
            o = st.text_input("Ocupación")
            sub = st.form_submit_button("UNIRME AHORA", use_container_width=True)
        if sub:
            status = guardar(n, c, t, o, datetime.now().strftime('%Y-%m-%d'))
            if status == "success": st.balloons(); st.success(f"¡Bienvenido a la verdadera vuelta, {n}!")
            elif status == "duplicate": st.warning("Ya eres parte de la familia.")
            else: st.error("Revisa tus datos.")
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown("""
<div class="social-footer">
    <a href="#" class="social-icon">INSTAGRAM</a>
    <a href="#" class="social-icon">TIKTOK</a>
    <a href="https://www.youtube.com/@YoAmoMiBarrioOFICIAL" class="social-icon">YOUTUBE</a>
</div>
""", unsafe_allow_html=True)
