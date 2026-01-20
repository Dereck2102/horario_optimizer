"""
Modulo Profesional (Generacion de Horarios - Admin)
Version 3.0 - SQLite Integration
"""

import streamlit as st
import pandas as pd
import json
import uuid
from core.optimizer import HorarioOptimizer
from core.database import save_horario, get_all_horarios, delete_horario

def show():
    if st.session_state.get('user_role') != 'Admin':
        st.error("Solo administradores pueden generar horarios")
        return

    st.markdown("## 📅 Generador de Horarios")
    
    # 1. Carga de Datos
    with st.expander("1. Cargar Datos (Excel)", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        clases_file = col1.file_uploader("Clases", type=['xlsx'], key='f_clases')
        aulas_file = col2.file_uploader("Aulas", type=['xlsx'], key='f_aulas')
        docentes_file = col3.file_uploader("Docentes", type=['xlsx'], key='f_docentes')
        
        if clases_file and aulas_file and docentes_file:
            try:
                clases_df = pd.read_excel(clases_file)
                aulas_df = pd.read_excel(aulas_file)
                docentes_df = pd.read_excel(docentes_file)
                
                # Preprocesamiento basico
                if 'id' not in clases_df.columns:
                    clases_df['id'] = range(1, len(clases_df) + 1)
                
                st.session_state.clases_df = clases_df
                st.session_state.aulas_df = aulas_df
                st.session_state.docentes_df = docentes_df
                
                st.success(f"Datos cargados: {len(clases_df)} clases, {len(aulas_df)} aulas, {len(docentes_df)} docentes")
            except Exception as e:
                st.error(f"Error cargando archivos: {e}")

    # 2. Configuracion de Ejecucion
    if 'clases_df' in st.session_state:
        with st.expander("2. Configuración y Ejecución", expanded=True):
            time_limit = st.slider("Tiempo limite (segundos)", 10, 300, 60)
            
            if st.button("🚀 Iniciar Optimizacion", type="primary"):
                with st.spinner("Optimizando horarios... esto puede tardar un momento"):
                    optimizer = HorarioOptimizer()
                    
                    # Ejecutar optimizacion
                    result = optimizer.optimize(
                        st.session_state.clases_df,
                        st.session_state.aulas_df,
                        st.session_state.docentes_df
                    )
                    
                    st.session_state.last_result = result
                    
                    if result['status'] == 'success':
                        st.success("¡Horario optimo encontrado!")
                    else:
                        st.error(f"No se pudo encontrar solucion: {result.get('reason')}")

    # 3. Resultados y Publicacion
    if 'last_result' in st.session_state and st.session_state.last_result['status'] == 'success':
        result = st.session_state.last_result
        schedule = result['schedule']
        
        st.markdown("### 3. Resultados")
        st.dataframe(pd.DataFrame(schedule), use_container_width=True)
        
        st.markdown(f"**Metricas:** Conflictos: {result['solver_stats']['conflicts']}")
        
        with st.form("publish_form"):
            periodo = st.text_input("Nombre del Periodo (Ej: 2024-2025)", value="2024-2025")
            
            if st.form_submit_button("📢 Publicar Horario Oficial"):
                if periodo:
                    if save_horario(periodo, schedule, created_by=st.session_state.username):
                        st.balloons()
                        st.success(f"Horario del periodo {periodo} publicado exitosamente")
                    else:
                        st.error("Error al guardar (quizas el nombre del periodo ya existe)")
                else:
                    st.warning("Ingrese un nombre para el periodo")

    # 4. Gestion de Publicados
    st.markdown("---")
    st.markdown("### Horarios Publicados")
    horarios = get_all_horarios()
    if horarios:
        for p, data in horarios.items():
            col1, col2 = st.columns([3, 1])
            col1.markdown(f"**{p}** ({len(data)} clases)")
            if col2.button("🗑️ Eliminar", key=f"del_{p}"):
                if delete_horario(p):
                    st.success("Eliminado")
                    st.rerun()
    else:
        st.info("No hay horarios publicados")
