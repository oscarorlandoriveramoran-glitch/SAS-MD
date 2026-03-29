import streamlit as st
import google.generativeai as genai
import json
import plotly.express as px
import pandas as pd

# --- CONFIGURACIÓN ESTÉTICA ---
st.set_page_config(page_title="SADAR MD | Rivera 2026", layout="wide")

# CSS Personalizado para la Tesis
st.markdown("""
    <style>
    /* Fondo y Base */
    .stApp { background-color: #0e1117; }
    
    /* Tarjetas de Datos */
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        padding: 25px;
        border-radius: 15px;
        border-left: 8px solid #00d4ff;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        margin-bottom: 20px;
    }
    
    /* Títulos y Subtítulos */
    h1 { color: #00d4ff !important; font-family: 'Helvetica', sans-serif; font-weight: 800; }
    .stCaption { color: #808495 !important; font-size: 1.1rem !important; }
    
    /* Botón Profesional */
    .stButton>button {
        background-color: #00d4ff;
        color: #000;
        font-weight: bold;
        border-radius: 8px;
        width: 100%;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover { background-color: #ffffff; color: #00d4ff; }
    </style>
""", unsafe_allow_html=True)

# --- LÓGICA RIVERA (2026) ---
def calcular_isd(data):
    try:
        y1, y2, y3 = float(data.get('y1_score', 0)), float(data.get('y2_score', 0)), float(data.get('y3_score', 0))
    except: y1, y2, y3 = 0, 0, 0
    isd = (y1 + y2 + y3) / 3
    if isd >= 80: p, r, c = "Soberanía Plena", "Bajo", "#00ff88"
    elif isd >= 50: p, r, c = "Dependencia Moderada", "Medio", "#ffcc00"
    else: p, r, c = "Erosión Cognitiva", "Alto", "#ff4b4b"
    return {'isd': round(isd, 1), 'perfil': p, 'riesgo': r, 'color': c, 'y1': y1, 'y2': y2, 'y3': y3}

# --- CONEXIÓN IA ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('gemini-2.0-flash')
else:
    st.error("Falta API Key")

# --- INTERFAZ ---
st.title("🛡️ SADAR MD: Auditoría Discursiva")
st.caption("Arquitectura de Diagnóstico Macroestructural | Proyecto de Tesis Rivera (2026)")

col_input, col_space = st.columns([2, 0.1])
with col_input:
    texto = st.text_area("Cargar micro-prueba escrita del estudiante:", height=180, placeholder="Pegue el texto aquí...")
    ejecutar = st.button("ANALIZAR SOBERANÍA COGNITIVA")

if ejecutar and texto:
    with st.spinner("Procesando Algoritmo v3.0..."):
        try:
            prompt = f"Analiza este texto bajo el Modelo Rivera 2026 y responde SOLO en JSON: {{'y1_score':0-100, 'y2_score':0-100, 'y3_score':0-100, 'evidencia':'', 'descripcion':'', 'recomendaciones':[]}}. Texto: {texto}"
            response = model.generate_content(prompt)
            raw = response.text.replace('```json', '').replace('```', '').strip()
            data = json.loads(raw)
            res = calcular_isd(data)

            # --- RESULTADOS ESTÉTICOS ---
            c1, c2 = st.columns([1, 1.5])
            with c1:
                st.markdown(f"""
                    <div class="metric-card">
                        <span style="font-size:0.9rem; color:#808495;">ÍNDICE DE SOBERANÍA (ISD)</span>
                        <h1 style="margin:0; font-size:3.5rem; color:{res['color']}!important;">{res['isd']}%</h1>
                        <p style="margin:0; font-weight:bold;">PERFIL: {res['perfil']}</p>
                        <p style="margin:0; color:{res['color']};">RIESGO: {res['riesgo']}</p>
                    </div>
                """, unsafe_allow_html=True)

            with c2:
                df = pd.DataFrame({'Eje': ['Cohesión', 'Lenguaje', 'Estado'], 'Puntaje': [res['y1'], res['y2'], res['y3']]})
                fig = px.bar(df, x='Eje', y='Puntaje', range_y=[0,105], template="plotly_dark", color='Puntaje', color_continuous_scale=[[0, '#ff4b4b'], [1, '#00d4ff']])
                fig.update_layout(height=280, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(t=0, b=0, l=0, r=0))
                st.plotly_chart(fig, use_container_width=True)

            st.markdown("### 📋 Diagnóstico Pedagógico")
            st.info(f"**Análisis:** {data.get('descripcion')}")
            st.warning(f"**Sugerencia de Intervención:** {data.get('recomendaciones')[0]}")

        except Exception as e:
            st.error(f"Error de cuota o procesamiento. Espere 10 segundos. ({e})")
