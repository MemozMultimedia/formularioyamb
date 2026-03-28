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

cursor.execute("""
CREATE TABLE IF NOT EXISTS registros (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT,
    correo TEXT UNIQUE,
    telefono TEXT,
    fecha TEXT
)
""")
conn.commit()

def validar_email(email):
    patron = r'^\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.match(patron, email)

def guardar_en_txt(df):
    df.to_string('reporte_registros.txt', index=False)

def guardar(nombre, correo, telefono, fecha):
    if nombre and correo and validar_email(correo):
        try:
            cursor.execute("""
            INSERT INTO registros (nombre, correo, telefono, fecha)
            VALUES (?, ?, ?, ?)
            """, (nombre, correo, telefono, fecha))
            conn.commit()
            df = obtener_datos()
            guardar_en_txt(df)
            return "success"
        except sqlite3.IntegrityError:
            return "duplicate"
    return "error"

def obtener_datos():
    return pd.read_sql_query("SELECT * FROM registros ORDER BY fecha DESC", conn)

# =====================
# UI STREAMLIT
# =====================
st.set_page_config(page_title="YAMB Pro", layout="wide")

st.markdown("""
<style>
.stApp {
    background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)),
                url('https://raw.githubusercontent.com/MemozMultimedia/mzmstill/main/hf_20260328_023420_f7d7d2a9-1955-4269-a97a-c444fbbd7a73.png');
    background-size: cover; background-position: center; background-attachment: fixed;
    color: white !important;
}
.main-card { background: rgba(0,0,0,0.5); padding: 30px; border-radius: 20px; backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.1); }
.yamb-red { color: #ff0000; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# Top Admin Button
col_left, col_right = st.columns([8, 2])
with col_right:
    admin_mode = st.toggle("🔐 Acceso Administrador")

if admin_mode:
    st.markdown("<h2 style='text-align: center;'>📂 Panel de Control Privado</h2>", unsafe_allow_html=True)
    col_a, col_b, col_c = st.columns([1, 1, 1])
    with col_b:
        user = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")

        if user == "Yamb" and password == "LavueltaesDios1*":
            st.success("✅ Acceso Concedido")
            df = obtener_datos()
            st.dataframe(df.drop(columns=['id']), use_container_width=True)
            if os.path.exists('reporte_registros.txt'):
                with open('reporte_registros.txt', 'rb') as f:
                    st.download_button("⏬ Descargar (.txt)", f, file_name='reporte_registros.txt')
        elif user or password:
            st.error("❌ Credenciales incorrectas")

else:
    st.markdown("<h1 style='text-align: center;'>Registrate y se parte de nuestra familia <span class='yamb-red'>YAMB</span></h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        with st.form("public_form", clear_on_submit=True):
            nombre = st.text_input("Nombre completo")
            correo = st.text_input("Email")
            telefono = st.text_input("Teléfono")
            submit = st.form_submit_button("✅ Enviar Registro", use_container_width=True)

        if submit:
            res = guardar(nombre, correo, telefono, datetime.now().strftime('%Y-%m-%d'))
            if res == "success": st.success("✅ ¡Registro enviado!")
            elif res == "duplicate": st.error("⚠️ El correo ya existe.")
            else: st.error("⚠️ Completa los campos.")
        st.markdown('</div>', unsafe_allow_html=True)
