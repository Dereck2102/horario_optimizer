"""
Modulo Dashboard
Version 4.0 - Clean UI & Plotly
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from core.database import get_stats, get_all_horarios

def show():
    st.markdown("## 📊 Dashboard General")
    st.markdown("Resumen de actividad y estadísticas del sistema.")
    
    # 1. Metricas Principales
    stats = get_stats()
    horarios = get_all_horarios()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="app-card" style="text-align: center;">
            <div style="font-size: 0.9rem; opacity: 0.7;">Periodos</div>
            <div style="font-size: 2rem; font-weight: 700; color: var(--primary-color);">{stats['horarios']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        total_clases = sum(len(h) for h in horarios.values())
        st.markdown(f"""
        <div class="app-card" style="text-align: center;">
            <div style="font-size: 0.9rem; opacity: 0.7;">Total Clases</div>
            <div style="font-size: 2rem; font-weight: 700; color: #3b82f6;">{total_clases}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown(f"""
        <div class="app-card" style="text-align: center;">
            <div style="font-size: 0.9rem; opacity: 0.7;">Profesores</div>
            <div style="font-size: 2rem; font-weight: 700; color: #10b981;">{stats['professors']}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col4:
        st.markdown(f"""
        <div class="app-card" style="text-align: center;">
            <div style="font-size: 0.9rem; opacity: 0.7;">Estudiantes</div>
            <div style="font-size: 2rem; font-weight: 700; color: #8b5cf6;">{stats['students']}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 2. Graficos y Detalles
    col_chart, col_list = st.columns([2, 1])
    
    if horarios:
        with col_chart:
            st.markdown("#### Clases por Periodo")
            data_chart = [{"Periodo": k, "Clases": len(v)} for k, v in horarios.items()]
            df_chart = pd.DataFrame(data_chart)
            
            fig = px.bar(
                df_chart, x="Periodo", y="Clases",
                text="Clases",
                color="Clases",
                color_continuous_scale="Blues"
            )
            fig.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font_color="gray",
                showlegend=False
            )
            fig.update_traces(textposition='outside')
            st.plotly_chart(fig, use_container_width=True)
            
        with col_list:
            st.markdown("#### Últimos Horarios")
            for p in list(horarios.keys())[:5]:
                st.markdown(f"""
                <div style="padding: 0.75rem; border-bottom: 1px solid var(--border-color);">
                    <strong>{p}</strong> <br>
                    <span style="font-size: 0.8rem; opacity: 0.7;">{len(horarios[p])} clases registradas</span>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No hay datos suficientes para mostrar estadísticas.")

    # 3. Vista de Horario (Grid)
    if horarios:
        st.markdown("---")
        st.markdown("### 📅 Vista de Horario Oficial")
        
        periodo = st.selectbox("Seleccionar Periodo", list(horarios.keys()))
        
        if periodo:
            from app import show_schedule_grid # Importar helper visual de app
            show_schedule_grid(horarios[periodo])
