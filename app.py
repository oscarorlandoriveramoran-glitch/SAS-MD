import streamlit as st
import google.generativeai as genai
import json
import plotly.express as px
import pandas as pd

# 1. Configuración Visual y de Tesis Profesional
st.set_page_config(page_title="SADAR MD | ECC-UJMD", layout="wide")

st.markdown("""
    <style>
    .report-card { background-color: #1e1e1e; padding: 20px; border-radius: 10px; border-left: 5px solid #00d4ff; color: white; }
    .stTextArea textarea { background-color: #121212; color: #00d4ff; border: 1px solid #333; }
    </style>
""", unsafe_allow_html=True)

# 2. Definición del Algoritmo Matemático Rivera (2026)
def calcular_isd(data):
    try:
        y1 = float(data.get('y1_score', 0))
        y2 = float(data.get('y2_score', 0))
        y3 = float(data.get('y3_score', 0))
    except:
        y1, y2, y3 = 0, 0, 0
    
    isd_final = (y1 + y2 + y3) / 3
    
    if isd_final >= 80:
        perfil, riesgo, color = "Soberanía Plena", "Bajo / Óptimo", "#00ff88"
    elif isd_final >= 50:
        perfil, riesgo, color = "Dependencia Moderada", "Medio / Alerta", "#ffcc00"
    else:
        perfil, riesgo, color = "Erosión Cognitiva", "Alto / Crítico", "#ff4b4b"
        
    return {'isd': round(isd_final, 1), 'perfil': perfil, 'riesgo': riesgo, 'color': color, 'y1_score': y1, 'y2_score': y2, 'y3_score': y3}

# 3. System Prompt
SYSTEM_PROMPT = """
Eres un analizador de macroestructura discursiva académica basado en el Modelo Diagnóstico Rivera (2026).
PRODUCE UN ÚNICO OBJETO JSON con este formato exacto:
{"y1_score": 0-100, "y2_score": 0-100, "y3_score": 0-100, "evidencia": "texto", "descripcion": "texto", "recomendaciones": ["lista"]}
Reglas: Devuelve SOLO el JSON. Sin bloques de código ```.
"""

# 4. Conexión Dual Segura
model = None
try:
    if "GOOGLE_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        # Intentamos con el nombre más básico que acepta la API v1
        model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=SYSTEM_PROMPT)
    else:
        st.error("❌ No se encontró la API Key en Secrets.")
except Exception:
    # Si falla el anterior, intentamos la versión Pro que es más estable en v1beta
    model = genai.GenerativeModel('gemini-1.5-pro', system_instruction=SYSTEM_PROMPT)

# --- INTERFAZ ---
st.title("SADAR MD: Auditoría de Soberanía Cognitiva")
st.caption("Modelo Diagnóstico Macroestructural — Rivera (2026) | ECC-UJMD")

texto_estudiante = st.text_area("Cargar micro-prueba escrita:", height=200)

if st.button("Ejecutar Algoritmo ISD v3"):
    if not texto_estudiante:
        st.warning("Escriba un texto.")
    else:
        with st.spinner("Analizando..."):
            try:
                # Forzamos la respuesta a ser JSON
                response = model.generate_content(texto_estudiante)
                txt_limpio = response.text.replace('```json', '').replace('```', '').strip()
                res_data = json.loads(txt_limpio)
                reporte = calcular_isd(res_data)
                
                # Renderizado
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.markdown(f"<div class='report-card'><h2>ISD: {reporte['isd']}%</h2><p>PERFIL: {reporte['perfil']}</p><p>RIESGO: <span style='color:{reporte['color']}'>{reporte['riesgo']}</span></p></div>", unsafe_allow_html=True)
                with col2:
                    df_plot = pd.DataFrame({'Var': ['Y1', 'Y2', 'Y3'], 'Puntaje': [reporte['y1_score'], reporte['y2_score'], reporte['y3_score']]})
                    fig = px.bar(df_plot, x='Var', y='Puntaje', range_y=[0,105], template="plotly_dark")
                    st.plotly_chart(fig, use_container_width=True)
                
                st.divider()
                st.subheader("📋 Reporte del Asesor")
                st.write(f"**Evidencia:** {res_data.get('evidencia')}")
                st.success(f"**Intervención:** {res_data.get('recomendaciones')[0]}")

            except Exception as e:
                st.error("Error de comunicación con el modelo.")
                st.info("Esto sucede cuando Google satura la API. Reintenta en 10 segundos.")
                with st.expander("Detalle"):
                    st.write(e)
