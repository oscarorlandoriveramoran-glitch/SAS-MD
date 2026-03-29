import streamlit as st
import google.generativeai as genai
import json
import plotly.express as px
import pandas as pd

# 1. Configuración Visual y de Tesis
st.set_page_config(page_title="SADAR MD | ECC-UJMD", layout="wide")

st.markdown("""
    <style>
    .report-card { background-color: #1e1e1e; padding: 20px; border-radius: 10px; border-left: 5px solid #00d4ff; color: white; }
    .stTextArea textarea { background-color: #121212; color: #00d4ff; border: 1px solid #333; }
    </style>
""", unsafe_allow_html=True)

# 2. Definición del Algoritmo Matemático Rivera (2026)
def calcular_isd(data):
    # Extraemos variables de la Matriz 3.0
    y1 = data.get('y1_score', 0)
    y2 = data.get('y2_score', 0)
    y3 = data.get('y3_score', 0)
    
    # Cálculo del Índice de Soberanía Discursiva (Promedio ponderado)
    isd_final = (y1 + y2 + y3) / 3
    
    # Lógica de Riesgo
    if isd_final >= 80:
        perfil, riesgo, color = "Soberanía Plena", "Bajo / Óptimo", "#00ff88"
    elif isd_final >= 50:
        perfil, riesgo, color = "Dependencia Moderada", "Medio / Alerta", "#ffcc00"
    else:
        perfil, riesgo, color = "Erosión Cognitiva", "Alto / Crítico", "#ff4b4b"
        
    return {
        'isd': round(isd_final, 1),
        'perfil': perfil,
        'riesgo': riesgo,
        'color': color,
        'y1_score': y1,
        'y2_score': y2,
        'y3_score': y3
    }

# 3. System Prompt y Conexión IA
SYSTEM_PROMPT = """
Eres un analizador de macroestructura discursiva académica basado en el Modelo Diagnóstico Rivera (2026).
Tu objetivo es detectar la 'Economía de la Dopamina' y erosión cognitiva en textos estudiantiles.
PRODUCE UN ÚNICO OBJETO JSON con este formato exacto:
{
  "y1_score": valor 0-100,
  "y2_score": valor 0-100,
  "y3_score": valor 0-100,
  "evidencia": "frase corta del texto",
  "descripcion": "diagnóstico breve",
  "recomendaciones": ["acción 1", "acción 2"]
}
Reglas: Devuelve SOLO el JSON. Sin bloques de código ```. Máximo 80 líneas.
"""

# Inicialización segura de la API
try:
    if "GOOGLE_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        # Usamos 1.5-flash por velocidad y compatibilidad
        model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=SYSTEM_PROMPT)
    else:
        st.warning("⚠️ Esperando configuración de API Key en Secrets...")
except Exception as e:
    st.error(f"Error de configuración: {e}")

# --- INTERFAZ ---
st.title("SADAR MD: Auditoría de Soberanía Cognitiva")
st.caption("Modelo Diagnóstico Macroestructural — Versión Asesor v3.0 | Rivera (2026) | ECC-UJMD")

texto_estudiante = st.text_area("Cargar micro-prueba escrita:", height=200, placeholder="Pegue el ensayo o respuesta del alumno aquí...")

if st.button("Ejecutar Algoritmo ISD v3"):
    if not texto_estudiante:
        st.warning("Por favor, ingrese un texto para analizar.")
    else:
        with st.spinner("Procesando Matriz 3.0..."):
            try:
                # Llamada a la IA
                response = model.generate_content(texto_estudiante)
                
                # Limpiar y parsear JSON
                raw_json = response.text.replace('```json', '').replace('```', '').strip()
                res_data = json.loads(raw_json)
                
                # Ejecutar Algoritmo
                reporte = calcular_isd(res_data)
                
                # --- VISUALIZACIÓN ---
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    st.markdown(f"""
                    <div class='report-card'>
                        <h2 style='margin:0;'>ISD: {reporte['isd']}%</h2>
                        <p style='margin:5px 0;'>PERFIL: <b>{reporte['perfil']}</b></p>
                        <p style='margin:0;'>RIESGO: <span style='color:{reporte['color']}'>{reporte['riesgo']}</span></p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    df_plot = pd.DataFrame({
                        'Variable': ['Cohesión (Y1)', 'Lenguaje (Y2)', 'Estado (Y3)'],
                        'Puntaje': [reporte['y1_score'], reporte['y2_score'], reporte['y3_score']]
                    })
                    fig = px.bar(df_plot, x='Variable', y='Puntaje', range_y=[0,105], 
                                 template="plotly_dark", color='Puntaje', 
                                 color_continuous_scale=[[0, '#ff4b4b'], [0.5, '#ffcc00'], [1, '#00ff88']])
                    fig.update_layout(height=250, margin=dict(l=20, r=20, t=20, b=20))
                    st.plotly_chart(fig, use_container_width=True)

                st.divider()
                
                # Reporte Detallado
                with st.expander("Ver Diagnóstico Detallado del Asesor"):
                    st.write(f"**Evidencia Detectada:** {res_data.get('evidencia', 'N/A')}")
                    st.write(f"**Análisis de Macroestructura:** {res_data.get('descripcion', 'N/A')}")
                    st.success(f"**Intervención Pedagógica Sugerida:** {res_data.get('recomendaciones', ['Sin datos'])[0]}")

            except Exception as e:
                st.error("Error crítico en el motor de análisis.")
                st.info("Revisa que la API Key sea válida y que el texto no sea demasiado corto.")
                with st.expander("Ver detalle técnico del error"):
                    st.write(e)
