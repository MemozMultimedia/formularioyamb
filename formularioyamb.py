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
    background: linear-gradient(rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.5)), 
                url("https://raw.githubusercontent.com/MemozMultimedia/mzmstill/main/hf_20260328_023420_f7d7d2a9-1955-4269-a97a-c444fbbd7a73.png") no-repeat center center fixed !important;
    background-size: cover !important;
}

.block-container { padding-top: 1rem !important; }
header { visibility: hidden; }

.main-card {
    background: rgba(10, 10, 10, 0.8);
    border: 1px solid rgba(255, 0, 0, 0.3);
    border-radius: 28px;
    padding: 35px;
    backdrop-filter: blur(25px);
    -webkit-backdrop-filter: blur(25px);
    box-shadow: 0 0 50px rgba(255, 0, 0, 0.15);
    margin-top: -10px;
    display: flex;
    flex-direction: column;
    gap: 15px;
}

.yamb-red { color: #ff0000; font-weight: 900; text-shadow: 0 0 10px rgba(255,0,0,0.3); }

.stButton>button {
    background: linear-gradient(90deg, #ff0000, #800000) !important;
    color: white !important;
    border-radius: 14px !important;
    padding: 12px 28px !important;
    font-weight: 800 !important;
    border: none !important;
}

.experience-link {
    background: rgba(255, 0, 0, 0.2);
    color: #ff0000 !important;
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 800;
    text-decoration: none !important;
    display: inline-block;
    width: fit-content;
    transition: 0.3s;
    border: 1px solid rgba(255, 0, 0, 0.3);
}
.experience-link:hover { background: rgba(255, 0, 0, 0.4); transform: scale(1.05); }

input {
    background: rgba(255,255,255,0.08) !important;
    color: white !important;
    border-radius: 10px !important;
}
</style>
""", unsafe_allow_html=True)

top_l, top_r = st.columns([9, 1])
with top_r: admin_mode = st.toggle("🔐", help="Acceso Admin")

if admin_mode:
    st.markdown("<h2 style='text-align: center; color: white;'>📂 Insight Center</h2>", unsafe_allow_html=True)
    _, col_b, _ = st.columns([1, 1, 1])
    with col_b:
        user = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        if user == "Yamb" and password == "LavueltaesDios1*":
            st.success("Authorized Access")
            df = obtener_datos()
            st.dataframe(df, use_container_width=True)
        elif user or password: st.error("Invalid Credentials")
else:
    st.markdown("<h1 style='text-align: center; color: white;'>Sé parte de la familia <span class='yamb-red'>YAMB</span></h1>", unsafe_allow_html=True)
    
    _, mid, _ = st.columns([1,1.8,1])
    with mid:
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        st.markdown('<a href="https://www.youtube.com/@YoAmoMiBarrioOFICIAL" target="_blank" class="experience-link">BARRIO EXPERIENCE ▶️</a>', unsafe_allow_html=True)
        st.markdown("<h3 style='margin:0;'>Únete al movimiento</h3>", unsafe_allow_html=True)
        st.markdown("<p style='opacity:0.7; font-size:0.9rem; margin-bottom: 5px;'>Completa tus datos para vivir la verdadera experiencia del barrio.</p>", unsafe_allow_html=True)
        
        with st.form("modern_form", clear_on_submit=True):
            n = st.text_input("Nombre completo", placeholder="Ej: Juan Pérez")
            c = st.text_input("Correo electrónico", placeholder="ejemplo@yamb.com")
            t = st.text_input("Teléfono", placeholder="Ej: +57 300 123 4567")
            o = st.text_input("Ocupación", placeholder="Ej: Productor, Artista")
            sub = st.form_submit_button("✅ ENVIAR REGISTRO", use_container_width=True)
            
        if sub:
            status = guardar(n, c, t, o, datetime.now().strftime('%Y-%m-%d'))
            if status == "success": st.balloons(); st.success("✅ ¡Registro enviado exitosamente!")
            elif status == "duplicate": st.warning("⚠️ Error: Datos registrados.")
            else: st.error("⚠️ Completa los campos correctamente.")
        st.markdown('</div>', unsafe_allow_html=True)
