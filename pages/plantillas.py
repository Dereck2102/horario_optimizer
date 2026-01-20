"""
Modulo Plantillas
Version 4.0 - Clean UI & Permissions
"""
import streamlit as st
import pandas as pd
import io

def show():
    role = st.session_state.get('user_role')
    
    if role == 'Estudiante':
        st.error("🔒 No tienes permiso para acceder a esta sección.")
        return
        
    st.markdown("## 📄 Plantillas de Datos")
    st.markdown("Descarga los formatos Excel requeridos para la carga de información.")
    
    col1, col2 = st.columns(2)
    
    # 1. Plantilla de Disponibilidad (Comun para Admin y Profe)
    with col1:
        st.markdown("### 📝 Disponibilidad Docente")
        st.info("Formato para que los profesores registren sus horas disponibles.")
        
        df_disp = pd.DataFrame({
            'Dia': ['Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes'],
            'Hora_Inicio': [7, 7, 7, 7, 7],
            'Hora_Fin': [13, 13, 13, 13, 13]
        })
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_disp.to_excel(writer, index=False)
            
        st.download_button(
            label="⬇️ Descargar Plantilla Disponibilidad",
            data=output.getvalue(),
            file_name="plantilla_disponibilidad.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

    # 2. Plantillas Administrativas (Solo Admin)
    if role == 'Admin':
        st.markdown("---")
        st.markdown("### 🛠️ Plantillas Administrativas")
        
        c1, c2, c3 = st.columns(3)
        
        # Clases
        with c1:
            st.markdown("**📚 Clases / Materias**")
            df_clases = pd.DataFrame({
                'Paralelo': ['SI1-001'], 'Asignatura': ['Programación I'], 
                'Nivel': ['1'], 'Estudiantes_registrados': [30], 
                'Duracion_bloques': [2], 'Tipo_espacio': ['Laboratorio']
            })
            out1 = io.BytesIO()
            with pd.ExcelWriter(out1, engine='openpyxl') as w: df_clases.to_excel(w, index=False)
            st.download_button("⬇️ Excel Clases", out1.getvalue(), "plantilla_clases.xlsx", use_container_width=True)
            
        # Aulas
        with c2:
            st.markdown("**🏛️ Aulas / Espacios**")
            df_aulas = pd.DataFrame({
                'Nombre': ['LAB-01'], 'Tipo': ['Laboratorio'], 
                'Capacidad': [30], 'Edificio': ['A']
            })
            out2 = io.BytesIO()
            with pd.ExcelWriter(out2, engine='openpyxl') as w: df_aulas.to_excel(w, index=False)
            st.download_button("⬇️ Excel Aulas", out2.getvalue(), "plantilla_aulas.xlsx", use_container_width=True)
            
        # Docentes
        with c3:
            st.markdown("**👨‍🏫 Docentes**")
            df_doc = pd.DataFrame({
                'Nombre': ['Juan Perez'], 'Materias': ['Programación I'], 
                'Email': ['jperez@uce.edu.ec']
            })
            out3 = io.BytesIO()
            with pd.ExcelWriter(out3, engine='openpyxl') as w: df_doc.to_excel(w, index=False)
            st.download_button("⬇️ Excel Docentes", out3.getvalue(), "plantilla_docentes.xlsx", use_container_width=True)
