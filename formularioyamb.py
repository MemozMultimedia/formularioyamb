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

# Improved CSS for Background Image
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;700;900&display=swap');

html, body, [class*=\"st-expander\"] { font-family: 'Inter', sans-serif; }

.stApp {
    background-image: linear-gradient(rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.5)), 
                      url("https://raw.githubusercontent.com/MemozMultimedia/mzmstill/main/hf_20260328_023420_f7d7d2a9-1955-4269-a97a-c444fbbd7a73.png");
    background-size: cover !important;
    background-position: center center !important;
    background-repeat: no-repeat !important;
    background-attachment: fixed !important;
}

.main-card {
    background: rgba(0, 0, 0, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 24px;
    padding: 40px;
    backdrop-filter: blur(15px);
    -webkit-backdrop-filter: blur(15px);
    box-shadow: 0 20px 40px rgba(0,0,0,0.8);
    margin-top: 20px;
}

.yamb-red { color: #ff0000; font-weight: bold; }

.stButton>button {
    background: linear-gradient(90deg, #ff0000, #800000) !important;
    color: white !important;
    border-radius: 12px !important;
    padding: 12px 24px !important;
    font-weight: 700 !important;
}

input {
    background: rgba(255,255,255,0.1) !important;
    color: white !important;
}

@media (max-width: 768px) {
    .main-card { padding: 25px; }
    h1 { font-size: 2rem !important; }
}
</style>
""", unsafe_allow_html=True)

# Navigation
top_l, top_r = st.columns([8, 2])
with top_r:
    admin_mode = st.toggle("🔐 Unlock Admin")

if admin_mode:
    st.markdown("<h2 style='text-align: center; color: white;'>📂 Insight Center</h2>", unsafe_allow_html=True)
    col_a, col_b, col_c = st.columns([1, 1, 1])
    with col_b:
        user = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        if user == "Yamb" and password == "LavueltaesDios1*":
            st.success("Authorized Access")
            df = obtener_datos()
            df.columns = ['Nombre', 'Correo', 'Teléfono', 'Ocupación', 'Fecha']
            st.dataframe(df, use_container_width=True)
        elif user or password: st.error("Invalid Credentials")
else:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: white;'>Regístrate y sé parte de nuestra familia <span class='yamb-red'>YAMB</span></h1>", unsafe_allow_html=True)
    
    _, mid, _ = st.columns([1,2,1])
    with mid:
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        with st.form("modern_form", clear_on_submit=True):
            n = st.text_input("Nombre completo")
            c = st.text_input("Correo electrónico")
            t = st.text_input("Teléfono")
            o = st.text_input("Ocupación")
            sub = st.form_submit_button("✅ Enviar registro", use_container_width=True)
            
        if sub:
            status = guardar(n, c, t, o, datetime.now().strftime('%Y-%m-%d'))
            if status == "success": st.balloons(); st.success("✅ ¡Registro enviado exitosamente!")
            elif status == "duplicate": st.warning("⚠️ Error: Estos datos ya están registrados.")
            else: st.error("⚠️ Por favor, completa los campos correctamente.")
        st.markdown('</div>', unsafe_allow_html=True)
