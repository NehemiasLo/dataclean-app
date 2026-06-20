import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import io
import os

# 1. Configuración de la página con tema oscuro nativo básico
st.set_page_config(
    page_title="Limpiador de Datos Inteligente v2.0",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados para imitar el look oscuro y las tarjetas de la captura
st.markdown("""
    <style>
    /* Fondo general oscuro y tipografía */
    .stApp {
        background-color: #0b111e;
        color: #e2e8f0;
    }
    /* Estilo de las tarjetas de reglas */
    .rule-card {
        background-color: #111a2e;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #1e293b;
        height: 100%;
    }
    .rule-title {
        color: #38bdf8;
        font-weight: bold;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .highlight-blue {
        color: #38bdf8;
        font-weight: 500;
    }
    .highlight-green {
        color: #34d399;
        font-weight: 500;
    }
    </style>
""", unsafe_allow_html=True)

# --- BARRA LATERAL: Flujo de Trabajo ---
with st.sidebar:
    st.markdown("### 📋 FLUJO DE TRABAJO")
    
    # Simulamos los pasos de la captura usando un radio button estilizado
    paso_actual = st.radio(
        "Progreso del pipeline:",
        ["1️⃣ Cargar Archivo", "2️⃣ Análisis de Calidad", "3️⃣ Consola de Limpieza", "4️⃣ Resultados & Exportar"],
        label_visibility="collapsed"
    )
    
    st.write("---")
    st.caption("⚙️ Ingeniería de Datos Avanzada para CSV / Excel")

# --- CONTENIDO PRINCIPAL ---
# Encabezado idéntico a la captura
col_header_1, col_header_2 = st.columns([3, 1])
with col_header_1:
    st.title("🧪 Limpiador de Datos Inteligente `v2.0`")
    st.caption("Ingeniería de Datos Avanzada para CSV / Excel")
with col_header_2:
    # Botón superior de prueba por si el usuario quiere testear la app
    st.button("📥 Cargar Dataset Sucio de Prueba", use_container_width=True)

st.write("---")

# Lógica basada en el flujo seleccionado en la barra lateral
if "1️⃣ Cargar Archivo" in paso_actual:
    
    st.markdown("## Cargar Dataset Sucio")
    st.markdown("Sube tu archivo .csv o Excel (.xlsx/.xls) para identificar y resolver de forma automática nulos en campos de texto o fechas de acuerdo al pipeline establecido.")
    
    # Caja de carga de archivos (Streamlit por defecto ya la centra y estiliza muy bien)
    uploaded_file = st.file_uploader(
        "Selecciona o arrastra tu archivo. Formatos soportados: Microsoft Excel (.xlsx, .xls) o Texto Delimitado (.csv)",
        type=["csv", "xlsx", "xls"],
        label_visibility="collapsed"
    )
    
    if uploaded_file is not None:
        st.success(f"✔️ Archivo '{uploaded_file.name}' detectado en memoria. Pasa al paso '2️⃣ Análisis de Calidad' en la barra lateral para continuar.")
        # Guardar archivo en el estado de la sesión para mantenerlo entre pestañas
        st.session_state['archivo_crudo'] = uploaded_file
    
    st.write("###")
    
    # --- BLOQUE INFERIOR: Reglas del Pipeline (Mapeadas de la captura) ---
    col_rule1, col_rule2 = st.columns(2)
    
    with col_rule1:
        st.markdown(f"""
        <div class="rule-card">
            <div class="rule-title">📄 REGLA 1: COLUMNAS DE TEXTO</div>
            <p>Se eliminan los espacios en blanco extremos y cualquier nulo o cadena vacía 
            (<code style="color:#f43f5e;">'nan'</code>, <code style="color:#f43f5e;">'None'</code>, <code style="color:#f43f5e;">'null'</code>) 
            se reemplaza por <span class="highlight-blue">"No registra información"</span>.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col_rule2:
        st.markdown(f"""
        <div class="rule-card">
            <div class="rule-title">📅 REGLA 2: COLUMNAS DE FECHA</div>
            <p>Toda columna interpretada con más de un un 70% de fechas se normaliza 
            y los registros faltantes o corruptos se rellenan con la <span class="highlight-green">Fecha Actual ({datetime.now().strftime('%Y-%m-%d')})</span>.</p>
        </div>
        """, unsafe_allow_html=True)

elif "2️⃣ Análisis de Calidad" in paso_actual:
    st.markdown("## Análisis de Calidad")
    if 'archivo_crudo' in st.session_state:
        # Aquí puedes renderizar los gráficos de nulos, dimensiones y dataframes que teníamos antes
        st.info("Lectura de datos exitosa. Aquí se computa el reporte analítico inicial.")
    else:
        st.warning("⚠️ Primero debes cargar un archivo en el paso 1.")

elif "3️⃣ Consola de Limpieza" in paso_actual:
    st.markdown("## Consola de Limpieza")
    st.info("Aplicando las reglas automáticas sobre el dataset...")
    # Aquí va el bucle for de Pandas que limpia nulos, textos y fechas basados en las Reglas 1 y 2

elif "4️⃣ Resultados & Exportar" in paso_actual:
    st.markdown("## Resultados & Exportar")
    st.info("Aquí el usuario descarga el archivo procesado.")

# --- PIE DE PÁGINA ---
st.write("###")
st.write("---")
col_foot1, col_foot2 = st.columns(2)
with col_foot1:
    st.caption("© 2026 Limpiador de Datos Inteligente. Todos los derechos reservados.")
with col_foot2:
    st.markdown("<p style='text-align: right; font-size: 0.8rem; opacity: 0.7;'>Desarrollado con pasión de Ingeniería de Datos ❤️</p>", unsafe_allow_html=True)
