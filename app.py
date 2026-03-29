import streamlit as st
import google.generativeai as genai
import json
import plotly.express as px
import pandas as pd

# 1. Configuración Visual
st.set_page_config(page_title="SADAR MD | ECC-UJMD", layout="wide")

# 2. Algoritmo Matemático Rivera (2026)
def calcular_isd(data):
    try:
        y1 = float(data.get('y1_score', 0))
        y2 = float(data.get('y2_score', 0))
        y3 = float(data.get('y3_score', 0))
    except:
        y1, y2, y3 = 0, 0, 0
    isd = (y1 + y2 + y3) / 3
    if isd >= 80: p, r, c = "Soberanía Plena", "Bajo", "#00ff88"
    elif isd >= 50: p, r, c = "Dependencia Moderada", "Medio", "#ffcc00"
    else: p, r, c = "Erosión Cognitiva", "Alto", "#ff4b4b"
    return {'isd': round(isd, 1), 'perfil': p, 'riesgo': r, 'color': c, 'y1': y1, 'y2': y2, 'y3': y3}

# 3. Conexión con el Modelo Detectado (Gemini 2.0 Flash)
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    # USAMOS EL NOMBRE EXACTO DE TU LISTA
    model = genai.GenerativeModel('gemini-2.0-flash')
else:
    st.error("⚠️ Configura la API Key en los Secrets.")

st.title("SADAR MD: Auditoría de Soberanía Cognitiva")
st.caption("Modelo Rivera (2026) — Impulsado por Gemini 2.0 | ECC-UJMD")

texto_estudiante = st.text_area("Cargar texto para análisis:", height=200)

if st.button("Ejecutar Algoritmo ISD v3"):
    if texto_estudiante:
        with st.spinner("Analizando con tecnología 2.0..."):
            try:
                # Instrucción directa
                prompt = (
                    "Eres el Algoritmo ISD v3. Analiza este texto y responde ÚNICAMENTE en JSON. "
                    "Campos: y1_score, y2_score, y3_score, evidencia, descripcion, recomendaciones. "
                    f"Texto: {texto_estudiante}"
                )
                
                response = model.generate_content(prompt)
                
                # Limpieza de JSON
                res_text = response.text.strip()
                if "```json" in res_text:
                    res_text = res_text.split("```json")[1].split("```")[0].strip()
                elif "```" in res_text:
                    res_text = res_text.split("```")[1].split("```")[0].strip()
                
                res_data = json.loads(res_text)
                reporte = calcular_isd(res_data)
                
                # --- RENDERIZADO ---
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.markdown(f"""
                        <div style='background:#1e1e1e; padding:20px; border-radius:10px; border-left:5px solid {reporte['color']}; color:white;'>
                            <h2 style='margin:0;'>ISD: {reporte['isd']}%</h2>
                            <p>PERFIL: <b>{reporte['perfil']}</b></p>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    fig = px.bar(x=['Y1', 'Y2', 'Y3'], y=[reporte['y1'], reporte['y2'], reporte['y3']], range_y=[0,105], template="plotly_dark")
                    st.plotly_chart(fig, use_container_width=True)
                
                st.success(f"**Intervención:** {res_data.get('recomendaciones')[0]}")
            
            except Exception as e:
                st.error(f"Error: {e}")
