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

# 3. Configuración de API (Cambiado a gemini-pro para evitar el Error 404)
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    # gemini-pro es el motor más estable para evitar el error NotFound
    model = genai.GenerativeModel('gemini-pro')
else:
    st.error("⚠️ Configura la 'GOOGLE_API_KEY' en los Secrets de Streamlit.")

st.title("SADAR MD: Auditoría de Soberanía Cognitiva")
st.caption("Modelo Rivera (2026) — Versión de Alta Compatibilidad | ECC-UJMD")

# Interfaz de Usuario
texto_estudiante = st.text_area("Cargar texto para análisis:", height=200, placeholder="Pegue el texto aquí...")

if st.button("Ejecutar Algoritmo ISD v3"):
    if texto_estudiante:
        with st.spinner("Procesando Matriz 3.0 con Gemini Pro..."):
            try:
                # Instrucción embebida para forzar formato JSON
                instruccion = (
                    "Eres un experto en macroestructura discursiva. Analiza el texto bajo el Modelo Rivera 2026. "
                    "Responde ESTRICTAMENTE con un objeto JSON (sin texto extra ni comillas de bloque) que contenga: "
                    "y1_score (0-100), y2_score (0-100), y3_score (0-100), evidencia (string), descripcion (string), recomendaciones (lista de strings). "
                    "Texto: "
                )
                
                response = model.generate_content(instruccion + texto_estudiante)
                
                # Limpieza de respuesta para asegurar JSON puro
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
                            <p style='margin:0;'>RIESGO: <span style='color:{reporte['color']}'>{reporte['riesgo']}</span></p>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    df_plot = pd.DataFrame({
                        'Variable': ['Cohesión (Y1)', 'Lenguaje (Y2)', 'Estado (Y3)'],
                        'Puntaje': [reporte['y1'], reporte['y2'], reporte['y3']]
                    })
                    fig = px.bar(df_plot, x='Variable', y='Puntaje', range_y=[0,105], 
                                 template="plotly_dark", color='Puntaje',
                                 color_continuous_scale=[[0, '#ff4b4b'], [0.5, '#ffcc00'], [1, '#00ff88']])
                    fig.update_layout(height=250, margin=dict(l=20, r=20, t=20, b=20))
                    st.plotly_chart(fig, use_container_width=True)
                
                st.divider()
                st.subheader("📋 Reporte del Asesor")
                st.write(f"**Evidencia:** {res_data.get('evidencia', 'No disponible')}")
                st.write(f"**Análisis:** {res_data.get('descripcion', 'No disponible')}")
                
                recs = res_data.get('recomendaciones', ['Sin recomendaciones'])
                st.success(f"**Intervención Sugerida:** {recs[0]}")
            
            except Exception as e:
                st.error("Error al procesar la respuesta de la IA.")
                with st.expander("Detalle técnico"):
                    st.write(e)
                    if 'response' in locals():
                        st.text(response.text)
    else:
        st.warning("Ingrese un texto para analizar.")
