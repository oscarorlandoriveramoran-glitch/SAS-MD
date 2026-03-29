import streamlit as st
import google.generativeai as genai
import json
import plotly.express as px
import pandas as pd

# 1. Configuración de la Página
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

# 3. DIRECCIÓN EXACTA DEL MODELO (Solución al error 404 persistente)
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    # Usamos la dirección absoluta del modelo para evitar el error de versión v1beta
    model = genai.GenerativeModel('models/gemini-1.5-flash-latest')
else:
    st.error("⚠️ Configura la 'GOOGLE_API_KEY' en los Secrets.")

st.title("SADAR MD: Auditoría de Soberanía Cognitiva")
st.caption("Modelo Rivera (2026) — Versión de Máxima Compatibilidad | ECC-UJMD")

texto_estudiante = st.text_area("Cargar texto para análisis:", height=200)

if st.button("Ejecutar Algoritmo ISD v3"):
    if texto_estudiante:
        with st.spinner("Analizando macroestructura..."):
            try:
                # Instrucción directa en el prompt
                prompt_completo = (
                    "Actúa como el Algoritmo ISD v3. Analiza el siguiente texto y responde UNICAMENTE con un objeto JSON. "
                    "Campos: y1_score, y2_score, y3_score, evidencia (string), descripcion (string), recomendaciones (lista). "
                    f"Texto: {texto_estudiante}"
                )
                
                response = model.generate_content(prompt_completo)
                
                # Limpieza manual del JSON por si la IA agrega basura
                res_text = response.text.strip()
                if "```json" in res_text:
                    res_text = res_text.split("```json")[1].split("```")[0].strip()
                elif "```" in res_text:
                    res_text = res_text.split("```")[1].split("```")[0].strip()
                
                res_data = json.loads(res_text)
                reporte = calcular_isd(res_data)
                
                # --- VISUALIZACIÓN ---
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.markdown(f"""
                        <div style='background:#1e1e1e; padding:20px; border-radius:10px; border-left:5px solid {reporte['color']}; color:white;'>
                            <h2 style='margin:0;'>ISD: {reporte['isd']}%</h2>
                            <p style='margin:5px 0;'>PERFIL: <b>{reporte['perfil']}</b></p>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    fig = px.bar(x=['Y1', 'Y2', 'Y3'], y=[reporte['y1'], reporte['y2'], reporte['y3']], range_y=[0,105], template="plotly_dark")
                    st.plotly_chart(fig, use_container_width=True)
                
                st.success(f"**Intervención:** {res_data.get('recomendaciones', ['Analizar caso'])[0]}")
            
            except Exception as e:
                st.error(f"Error en el motor: {e}")
                # Si falla, imprimimos los modelos que tu API realmente ve
                try:
                    models = [m.name for m in genai.list_models()]
                    st.info(f"Modelos disponibles en tu llave: {models}")
                except:
                    pass
    else:
        st.warning("Ingrese un texto.")
