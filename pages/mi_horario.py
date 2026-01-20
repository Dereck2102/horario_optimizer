"""
Modulo Mi Horario (Estudiantes)
Version 3.0 - SQLite Integration
"""

import streamlit as st
import pandas as pd
import json
import os
from core.database import get_all_horarios

# Reusamos la funcion simple de PDF si se necesita
def extract_pdf_tables(pdf_file):
    try:
        import tabula
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            tmp.write(pdf_file.read())
            tmp_path = tmp.name
        tables = tabula.read_pdf(tmp_path, pages='all', multiple_tables=True)
        os.remove(tmp_path)
        return tables
    except:
        return []

def show():
    if st.session_state.get('user_role') != 'Estudiante':
        st.error("Acceso no autorizado")
        return

    st.markdown("## 📅 Mi Horario")
    
    horarios = get_all_horarios()
    
    if not horarios:
        st.info("No hay horarios oficiales publicados aun.")
        return
    
    # Selector de periodo
    periodo = st.selectbox("Seleccionar Periodo Academico", list(horarios.keys()))
    
    if periodo:
        data = horarios[periodo]
        df = pd.DataFrame(data)
        
        st.markdown(f"### Visualización - {periodo}")
        
        # Filtros para que el estudiante encuentre sus materias
        col1, col2 = st.columns(2)
        
        # Filtrar por nivel/paralelo si existen esas columnas
        filtro_nivel = "Todos"
        if 'nivel' in df.columns:
            niveles = ["Todos"] + sorted(list(df['nivel'].astype(str).unique()))
            filtro_nivel = col1.selectbox("Filtrar por Nivel", niveles)
            
        filtro_paralelo = "Todos"
        if 'paralelo' in df.columns:
            paralelos = ["Todos"] + sorted(list(df['paralelo'].astype(str).unique()))
            filtro_paralelo = col2.selectbox("Filtrar por Paralelo", paralelos)
            
        # Filtrar DF
        df_show = df.copy()
        if filtro_nivel != "Todos":
            df_show = df_show[df_show['nivel'].astype(str) == filtro_nivel]
        if filtro_paralelo != "Todos":
            df_show = df_show[df_show['paralelo'].astype(str) == filtro_paralelo]
            
        if not df_show.empty:
            # Mostrar GRID basico similar al dashboard
            dias = ['Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes', 'Sabado']
            horas = list(range(7, 21))
            
            st.markdown("#### Horario Semanal")
            
            # Construir HTML Grid
            html = """
            <style>
                .grid-table { width:100%; border-collapse: collapse; margin-bottom: 1rem; }
                .grid-table th { background:rgba(59,130,246,0.2); border:1px solid #444; padding:5px; color:#ddd; }
                .grid-table td { border:1px solid #444; padding:5px; font-size:0.8em; vertical-align:top; height:50px; }
                .grid-cell { background:rgba(59,130,246,0.3); padding:4px; border-radius:4px; margin-bottom:2px; color:#fff; }
                .grid-hour { background:#222; color:#aaa; text-align:center; }
            </style>
            <table class="grid-table"><thead><tr><th>Hora</th>
            """
            for d in dias: html += f"<th>{d}</th>"
            html += "</tr></thead><tbody>"
            
            for h in horas:
                html += f"<tr><td class='grid-hour'>{h}:00</td>"
                for d in dias:
                    html += "<td>"
                    # Buscar clases
                    if 'dia' in df_show.columns and 'hora_inicio' in df_show.columns:
                        clases_match = df_show[
                            (df_show['dia'] == d) & 
                            (df_show['hora_inicio'].astype(str).str.startswith(str(h)))
                        ]
                        for _, row in clases_match.iterrows():
                            # Asegurarse que materia existe
                            mat = row.get('materia', row.get('Asignatura', 'Clase'))
                            aula = row.get('aula', '')
                            html += f"<div class='grid-cell'><b>{mat}</b><br>{aula}</div>"
                    html += "</td>"
                html += "</tr>"
            html += "</tbody></table>"
            
            st.markdown(html, unsafe_allow_html=True)
            
            # Tabla detallada
            with st.expander("Ver lista detallada"):
                st.dataframe(df_show, use_container_width=True)
        else:
            st.warning("No se encontraron clases con los filtros seleccionados")

    st.markdown("---")
    st.caption("Si necesitas simular un horario personal, usa la opcion de carga en Configuracion (Proximamente)")
