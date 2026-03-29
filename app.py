import streamlit as st
import google.generativeai as genai
import json
import plotly.express as px
import pandas as pd

# Configuración Visual
st.set_page_config(page_title="SADAR MD | ECC-UJMD", layout="wide")

# Estilos de Tesis Profesional
st.markdown("""
    <style>
    .report-card { background-color: #1e1e1e; padding: 20px; border-radius: 10px; border-left: 5px solid #00d4ff; }
    .metric-box { text-align: center; padding: 10px; background: #262730; border-radius: 5px; }
    </style>
""", unsafe_allow_html=True)

# 1. Configurar el System Prompt de tu archivo
SYSTEM_PROMPT = """
Eres un analizador de macroestructura discursiva académica basado en el Modelo Diagnóstico Rivera (2026).
Recibes un texto y produces UN ÚNICO OBJETO JSON con PARTE A (Valores numéricos) y PARTE B (Texto diagnóstico).
Reglas: Devuelve SOLO el JSON. Sin bloques de código. Máximo 80 líneas.
""" # Aquí pegas el contenido completo de la sección SYSTEM PROMPT de tu TXT

# 2. Conexión con Gemini
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-pro', system_instruction=SYSTEM_PROMPT)
except:
    st.error("Configura la API Key en Streamlit Cloud Secrets.")

st.title("SADAR MD: Auditoría de Soberanía Cognitiva")
st.caption("Modelo Diagnóstico Macroestructural — Versión Asesor v3.0 | Rivera (2026)")

# Interfaz de Usuario
texto_estudiante = st.text_area("Cargar micro-prueba escrita:", height=250, placeholder="Escriba o pegue el texto aquí...")

if st.button("Ejecutar Algoritmo ISD v3"):
    if texto_estudiante:
        with st.spinner("Analizando macroestructura..."):
            # Llamada a la IA
            response = model.generate_content(texto_estudiante)
            
            try:
                # Limpiamos la respuesta para asegurar que sea JSON puro
                raw_json = response.text.replace('```json', '').replace('```', '').strip()
                res_data = json.loads(raw_json)
                
                # Ejecutamos tu Algoritmo en Python
                reporte = calcular_isd(res_data) # Usando la función del paso anterior
                
                # --- RENDERIZADO DEL REPORTE ---
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    st.markdown(f"""
                    <div class='report-card'>
                        <h3>ISD: {reporte['isd']}/100</h3>
                        <p>PERFIL: <b>{reporte['perfil']}</b></p>
                        <p>RIESGO: <span style='color:{reporte['color']}'>{reporte['riesgo']}</span></p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    # Gráfico de la Matriz
                    df_plot = pd.DataFrame({
                        'Variable': ['Cohesión (Y1)', 'Lenguaje (Y2)', 'Estado (Y3)'],
                        'Puntaje': [reporte['y1_score'], reporte['y2_score'], reporte['y3_score']]
                    })
                    fig = px.bar(df_plot, x='Variable', y='Puntaje', range_y=[0,100], template="plotly_dark")
                    st.plotly_chart(fig, use_container_width=True)

                st.divider()
                st.subheader("Reporte para el Asesor")
                st.write(f"**Evidencia:** {res_data['evidencia']}")
                st.write(f"**Descripción:** {res_data['descripcion']}")
                
                st.info(f"**Intervención Sugerida:** {res_data['recomendaciones'][0]}")

            except Exception as e:
                st.error(f"Error al procesar el JSON: {e}")
                st.text(response.text)
