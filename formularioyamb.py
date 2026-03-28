import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd
import re

# =====================
# DB SETUP
# =====================
conn = sqlite3.connect("datos_app.db", check_same_thread=False)
cursor = conn.cursor()

# Re-create table with description field
cursor.execute("""
CREATE TABLE IF NOT EXISTS registros (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT,
    correo TEXT,
    telefono TEXT,
    descripcion TEXT,
    fecha TEXT
)
""")
conn.commit()

def validar_email(email):
    patron = r'^\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.match(patron, email)

def guardar(nombre, correo, telefono, descripcion, fecha):
    if nombre and correo and validar_email(correo):
        cursor.execute("""
        INSERT INTO registros (nombre, correo, telefono, descripcion, fecha)
        VALUES (?, ?, ?, ?, ?)
        """, (nombre, correo, telefono, descripcion, fecha))
        conn.commit()
        return True
    return False

def obtener_datos():
    return pd.read_sql_query("SELECT * FROM registros ORDER BY fecha DESC", conn)

# =====================
# UI STREAMLIT
# =====================
st.set_page_config(page_title="Formulario YAMB", layout="wide")

st.title("📋 Formulario YAMB Pro")

# Collapsible Registration Tab
with st.expander("🔐 Abrir Registro YAMB (Maximizar/Minimizar)", expanded=False):
    st.markdown("### Complete los datos de contacto")
    with st.form("registro_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre completo")
            correo = st.text_input("Email")
        with col2:
            telefono = st.text_input("Teléfono")
            fecha = st.date_input("Fecha", datetime.today())
        
        descripcion = st.text_area("Descripción / Notas")
        submit = st.form_submit_button("✅ Guardar Registro")

    if submit:
        if not validar_email(correo):
            st.error("⚠️ Formato de correo inválido")
        elif guardar(nombre, correo, telefono, descripcion, str(fecha)):
            st.success("✅ Registro guardado exitosamente")
            st.rerun()
        else:
            st.error("⚠️ Por favor, complete Nombre y Email válido")

st.markdown("--- ")
st.subheader("📊 Base de Datos de Contactos")

df = obtener_datos()
if not df.empty:
    st.dataframe(df.drop(columns=['id']), use_container_width=True)
else:
    st.info("No hay contactos registrados todavía.")
