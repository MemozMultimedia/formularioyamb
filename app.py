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
st.set_page_config(page_title="YAMB Pro | Experience", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;700;900&display=swap');

html, body, [class*=\"st-expander\"] { font-family: 'Inter', sans-serif; }

.stApp {
    background: radial-gradient(circle at center, #1a1a1a 0%, #000000 100%);
    color: white;
}

/* Animated Mesh Background Overlay */
.stApp::before {
    content: '';
    position: fixed;
    top: 0; left: 0; width: 100%; height: 100%;
    background: url('https://raw.githubusercontent.com/MemozMultimedia/mzmstill/main/hf_20260328_023420_f7d7d2a9-1955-4269-a97a-c444fbbd7a73.png');
    background-size: cover; opacity: 0.15; filter: blur(5px);
    z-index: -1;
}

.main-card {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 24px;
    padding: 40px;
    backdrop-filter: blur(20px);
    box-shadow: 0 20px 40px rgba(0,0,0,0.4);
    transition: all 0.3s ease;
}

.yamb-red { 
    background: linear-gradient(90deg, #ff0000, #b30000);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 900; 
}

.stButton>button {
    background: linear-gradient(90deg, #ff0000, #800000) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 12px 24px !important;
    font-weight: 700 !important;
    letter-spacing: 1px;
    transition: 0.4s !important;
}

.stButton>button:hover {
    box-shadow: 0 0 20px rgba(255,0,0,0.6) !important;
    transform: translateY(-2px);
}

input {
    background: rgba(255,255,255,0.05) !important;
    border-color: rgba(255,255,255,0.1) !important;
    color: white !important;
    border-radius: 10px !important;
}
</style>
""", unsafe_allow_html=True)

# Navigation
admin_mode = st.sidebar.toggle("🔒 Admin Access")

if admin_mode:
    st.markdown("<h1 style='text-align: center;'>📂 Insight Center</h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1,1.5,1])
    with c2:
        with st.container(border=True):
            u = st.text_input("User ID")
            p = st.text_input("Key Token", type="password")
            if u == "Yamb" and p == "LavueltaesDios1*":
                st.success("Authorized Access")
                df = obtener_datos()
                df.columns = ['Nombre', 'Email', 'Teléfono', 'Ocupación', 'Fecha']
                st.dataframe(df, use_container_width=True)
            elif u or p: st.error("Invalid Credentials")
else:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; font-size: 4rem; letter-spacing: -2px;'>Welcome to <span class='yamb-red'>YAMB</span></h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; opacity: 0.7;'>La próxima generación de nuestra familia comienza contigo.</p>", unsafe_allow_html=True)
    
    _, mid, _ = st.columns([1,2,1])
    with mid:
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        with st.form("modern_form", clear_on_submit=True):
            n = st.text_input("Nombre Completo", placeholder="Ej: Juan Pérez")
            c = st.text_input("Correo Electrónico", placeholder="ejemplo@yamb.com")
            t = st.text_input("Número de Contacto")
            o = st.text_input("Tu Ocupación")
            sub = st.form_submit_button("UNIRSE AHORA", use_container_width=True)
            
        if sub:
            status = guardar(n, c, t, o, datetime.now().strftime('%Y-%m-%d'))
            if status == "success": st.balloons(); st.success("Bienvenido a la familia YAMB.")
            elif status == "duplicate": st.warning("⚠️ Estos datos ya están en nuestro registro.")
            else: st.error("Por favor revisa la información.")
        st.markdown('</div>', unsafe_allow_html=True)
