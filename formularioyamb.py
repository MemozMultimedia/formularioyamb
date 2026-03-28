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
    if not nombre or not correo or not validar_email(correo):
        return "error"
    try:
        cursor.execute("SELECT id FROM registros WHERE nombre=? OR correo=? OR telefono=?", (nombre, correo, telefono))
        if cursor.fetchone():
            return "duplicate"
        
        cursor.execute("INSERT INTO registros (nombre, correo, telefono, ocupacion, fecha) VALUES (?, ?, ?, ?, ?)",
                       (nombre, correo, telefono, ocupacion, fecha))
        conn.commit()
        return "success"
    except Exception as e:
        return "error"

def obtener_datos():
    return pd.read_sql_query("SELECT nombre, correo, telefono, ocupacion, fecha FROM registros ORDER BY fecha DESC", conn)

# =====================
# UI MASTER BRANDING
# =====================
# Browser Tab Title (INCLUDES YAMB)
st.set_page_config(page_title="YAMB VIVIENDO LA EXPERIENCIA DEL BARRIO", page_icon="❌", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;700;800;900&family=Source+Sans+3:wght@400;700;900&display=swap');
html, body { font-family: 'Inter', sans-serif; }
.admin-font { font-family: 'Source Sans 3', sans-serif !important; }
.block-container { padding-top: 1rem !important; animation: fadeIn 1.2s ease-out; }
header { visibility: hidden; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
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
    background: rgba(10, 10, 10, 0.4);
    border: 1px solid rgba(255, 0, 0, 0.2);
    border-radius: 40px;
    backdrop-filter: blur(35px);
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.8);
    padding: 0px; overflow: hidden;
    animation: float 6s infinite ease-in-out;
}
@keyframes float { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-5px); } }
.unified-header {
    background: linear-gradient(135deg, #220000 0%, #000000 100%);
    padding: 35px 20px; text-align: center; border-bottom: 2px solid #ff0000;
}
.header-text {
    font-weight: 900; font-size: 1.8rem; letter-spacing: 4px; 
    background: linear-gradient(to bottom, #ffffff 40%, #aaaaaa 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    filter: drop-shadow(0 0 8px rgba(255,0,0,0.4));
}
.yt-pill {
    background: #ff0000; padding: 12px 30px; border-radius: 5px;
    font-weight: 900; color: white !important; text-decoration: none !important;
    display: inline-block; transition: 0.4s; box-shadow: 0 0 15px rgba(255,0,0,0.5);
    text-transform: uppercase;
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
.social-icon { color: white; font-size: 1.2rem; margin: 0 15px; text-decoration: none; opacity: 0.6; transition: 0.3s; font-weight: 800; }
.social-icon:hover { opacity: 1; color: #ff0000; text-shadow: 0 0 10px #ff0000; }
.purpose-card {
    margin-top: 25px; padding: 30px; text-align: center;
    background: rgba(20, 20, 20, 0.3); border-radius: 35px;
    border: 1px solid rgba(255, 255, 255, 0.05); backdrop-filter: blur(15px);
}
.purpose-title { font-weight: 800; font-size: 1.5rem; color: #ff0000; margin-bottom: 10px; }
.purpose-text { font-size: 1rem; color: rgba(255,255,255,0.7); line-height: 1.6; }
</style>
""", unsafe_allow_html=True)

col_t1, col_t2 = st.columns([9, 1])
with col_t2: admin_trigger = st.toggle("🔐")

if admin_trigger:
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, mid_admin, _ = st.columns([1, 1.2, 1])
    with mid_admin:
        st.markdown("""
            <div class='admin-font' style='text-align: center; background: linear-gradient(to bottom, #ffffff 40%, #aaaaaa 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: 4px; font-weight: 900; margin-bottom: 40px; font-size: 1.8rem; filter: drop-shadow(0 0 5px rgba(255,0,0,0.4));'>
                🔐 INSIGHT CENTER
            </div>
        """, unsafe_allow_html=True)
        with st.form("admin_auth"):
            u = st.text_input("MASTER IDENTIFICATION", placeholder="User")
            p = st.text_input("SECURITY TOKEN", type="password", placeholder="••••••••")
            login = st.form_submit_button("🚀 INITIALIZE ACCESS", use_container_width=True)
        if login and u == "Yamb" and p == "LavueltaesDios1*":
            st.session_state["auth"] = True
        if st.session_state.get("auth"):
            df_export = obtener_datos()
            st.dataframe(df_export, use_container_width=True)
            csv = df_export.to_csv(index=False).encode('utf-8')
            st.download_button("📥 DESCARGAR BASE DE DATOS (CSV)", data=csv, file_name='yamb_registros.csv', mime='text/csv', use_container_width=True)
        elif login: st.error("Credenciales inválidas.")
else:
    st.markdown("<div style='text-align: center; color: white; font-weight:900; font-size: 3rem; margin-bottom: 30px; letter-spacing: -2px;'>Únete a nuestra familia <span style='color:#ff0000;'>YAMB</span></div>", unsafe_allow_html=True)
    _, mid, _ = st.columns([1, 1.5, 1])
    with mid:
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        # Visible Page Header (WITHOUT YAMB)
        st.markdown('<div class="unified-header"><div class="header-text">VIVIENDO LA EXPERIENCIA DEL BARRIO</div><br><a href="https://www.youtube.com/@YoAmoMiBarrioOFICIAL" target="_blank" class="yt-pill">YAMB TV ▶️</a></div>', unsafe_allow_html=True)
        st.markdown('<div style="padding: 40px;">', unsafe_allow_html=True)
        with st.form("reg_form", clear_on_submit=True):
            n = st.text_input("Nombre completo", placeholder="Ej: Juan Pérez")
            c = st.text_input("Email", placeholder="ejemplo@yamb.com")
            t = st.text_input("WhatsApp", placeholder="+57")
            o = st.text_input("Ocupación", placeholder="Artista, Diseñador, etc.")
            sub = st.form_submit_button("UNIRME AHORA", use_container_width=True)
        if sub:
            status = guardar(n, c, t, o, datetime.now().strftime('%Y-%m-%d'))
            if status == "success": st.balloons(); st.success(f"¡Bienvenido a la verdadera vuelta, {n}!")
            elif status == "duplicate": st.warning("Ya eres parte de la familia.")
            else: st.error("Revisa tus datos.")
        st.markdown('</div></div>', unsafe_allow_html=True)
        st.markdown('''
            <div class="purpose-card">
                <div class="purpose-title">GRACIAS POR TU COMPRA</div>
                <div class="purpose-text">
                    CADA PRODUCTO DE YAMB TIENE UN PROPÓSITO.<br>
                    CON TU COMPRA, APOYAS A JÓVENES TALENTOS EN LA MÚSICA Y EL ARTE, AYUDÁNDOLOS A CRECER, CREAR Y COMPARTIR SU PASIÓN CON EL MUNDO.
                </div>
            </div>
        ''', unsafe_allow_html=True)

st.markdown("""
<div class="social-footer">
    <a href=\"https://www.instagram.com/yoamomibarrioyamb/\" target=\"_blank\" class="social-icon">INSTAGRAM</a>
    <a href=\"https://www.tiktok.com/@yambshop\" target=\"_blank\" class="social-icon">TIKTOK</a>
    <a href="https://www.youtube.com/@YoAmoMiBarrioOFICIAL" target="_blank" class="social-icon">YOUTUBE</a>
</div>
""", unsafe_allow_html=True)
