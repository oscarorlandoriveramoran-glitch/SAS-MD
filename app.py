import streamlit as st
import google.generativeai as genai
import json
import plotly.express as px
import pandas as pd

# 1. Configuración de la Página
st.set_page_config(page_title="SADAR MD | ECC-UJMD", layout="wide")

# 2. Algoritmo Matemático Rivera
def calcular_isd(data):
    try:
        y1, y2, y3 = float(data.get('y1_score', 0)), float(data.get('y2_score', 0)), float(data.get('y3_score', 0))
    except:
        y1, y2, y3 = 0, 0, 0
    isd = (y1 + y2 + y3) / 3
    if isd >= 80: p, r, c = "Soberanía Plena", "Bajo", "#00ff88"
    elif isd >= 50: p, r, c = "Dependencia Moderada", "Medio", "#ffcc00"
    else: p, r, c = "Erosión Cognitiva", "Alto", "#ff4b4b"
    return {'isd': round(isd, 1), 'perfil': p, 'riesgo': r, 'color': c, 'y1': y1, 'y2': y2, 'y3': y3}

# 3. Configuración de API (Sin parámetros extra para evitar el 404)
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    # USAMOS SOLO EL NOMBRE DEL MODELO SIN NADA MÁS
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.error("Falta la API Key en Secrets.")

st.title("SADAR MD: Auditoría de Soberanía Cognitiva")
st.caption("Modelo Rivera (2026) | ECC-UJMD")

texto_estudiante = st.text_area("Cargar texto para análisis:", height=200)

if st.button("Ejecutar Algoritmo ISD v3"):
    if texto_estudiante:
        with st.spinner("Conectando con el motor de IA..."):
            try:
                # METEMOS EL SYSTEM PROMPT DIRECTO EN EL MENSAJE
                instruccion = "Eres un analizador de macroestructura discursiva (Modelo Rivera 2026). Responde SOLO en JSON con campos: y1_score, y2_score, y3_score, evidencia, descripcion, recomendaciones. Texto a analizar: "
                
                response = model.generate_content(instruccion + texto_estudiante)
                
                # Limpieza y Procesamiento
                raw = response.text.replace('```json', '').replace('```', '').strip()
                res_data = json.loads(raw)
                reporte = calcular_isd(res_data)
                
                # Visualización
                c1, c2 = st.columns([1, 2])
                with c1:
                    st.markdown(f"<div style='background:#1e1e1e; p:20px; border-radius:10px; border-left:5px solid {reporte['color']}; color:white;'><h2>ISD: {reporte['isd']}%</h2><p>{reporte['perfil']}</p></div>", unsafe_allow_html=True)
                with c2:
                    fig = px.bar(x=['Y1', 'Y2', 'Y3'], y=[reporte['y1'], reporte['y2'], reporte['y3']], range_y=[0,105], template="plotly_dark")
                    st.plotly_chart(fig, use_container_width=True)
                
                st.success(f"**Recomendación:** {res_data.get('recomendaciones')[0]}")
            
            except Exception as e:
                st.error(f"Error técnico: {e}")
                st.info("Si el error persiste, probá cambiando el nombre del modelo a 'gemini-pro' en el código.")
