import streamlit as st
import pandas as pd
import sys
import os
import io

# Asegurar que el directorio raiz este en el path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.data_loader import DataLoader

st.set_page_config(page_title="Configuracion", page_icon="gear", layout="wide")

# Verificar autenticacion
if not st.session_state.get('authenticated'):
    st.error("Acceso denegado. Inicie sesion primero.")
    st.stop()

# Verificar rol de admin para algunas funciones
is_admin = st.session_state.get('user_role') == 'Admin'

# Logout en sidebar
st.sidebar.markdown(f"**Sesion:** {st.session_state.get('user_role')}")
if st.sidebar.button("Cerrar Sesion", use_container_width=True):
    st.session_state.authenticated = False
    st.session_state.user_role = None
    st.rerun()

st.sidebar.markdown("---")

st.title("Panel de Configuracion")
st.markdown("Administracion del sistema y recursos")

# Inicializacion de estado
if 'config_aulas' not in st.session_state:
    st.session_state.config_aulas = None
if 'config_docentes' not in st.session_state:
    st.session_state.config_docentes = None

loader = DataLoader()

# Tabs principales
tab1, tab2, tab3, tab4 = st.tabs([
    "Gestion Aulas", "Gestion Docentes", "Plantillas", "Sistema"
])

# =============================================================================
# TAB 1: GESTION DE AULAS
# =============================================================================
with tab1:
    st.subheader("Gestion de Aulas y Laboratorios")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if st.session_state.config_aulas is None:
            if st.button("Cargar aulas por defecto", use_container_width=True):
                st.session_state.config_aulas = loader.create_default_aulas(50)
                st.success("50 aulas cargadas")
        
        if st.session_state.config_aulas is not None:
            st.markdown("#### Catalogo de Aulas")
            
            edited_aulas = st.data_editor(
                st.session_state.config_aulas,
                num_rows="dynamic",
                use_container_width=True,
                height=400,
                column_config={
                    "id": st.column_config.NumberColumn("ID", disabled=True),
                    "nombre": st.column_config.TextColumn("Nombre", required=True),
                    "tipo": st.column_config.SelectboxColumn(
                        "Tipo",
                        options=["Aula", "Lab"],
                        required=True
                    ),
                    "capacidad": st.column_config.NumberColumn(
                        "Capacidad",
                        min_value=10,
                        max_value=200,
                        required=True
                    ),
                    "edificio": st.column_config.TextColumn("Edificio")
                },
                key="editor_aulas"
            )
            
            if st.button("Guardar cambios en aulas", type="primary"):
                edited_aulas['id'] = range(len(edited_aulas))
                st.session_state.config_aulas = edited_aulas
                st.success("Cambios guardados")
    
    with col2:
        st.markdown("#### Agregar Nueva Aula")
        
        with st.form("form_nueva_aula"):
            nombre = st.text_input("Nombre", placeholder="LAB-10")
            tipo = st.selectbox("Tipo", ["Aula", "Lab"])
            capacidad = st.number_input("Capacidad", min_value=10, max_value=200, value=30)
            edificio = st.text_input("Edificio", placeholder="Edificio Principal")
            
            if st.form_submit_button("Agregar", use_container_width=True):
                if nombre:
                    if st.session_state.config_aulas is None:
                        st.session_state.config_aulas = pd.DataFrame(columns=['id', 'nombre', 'tipo', 'capacidad', 'edificio'])
                    
                    new_id = len(st.session_state.config_aulas)
                    nueva_aula = pd.DataFrame([{
                        'id': new_id,
                        'nombre': nombre,
                        'tipo': tipo,
                        'capacidad': capacidad,
                        'edificio': edificio
                    }])
                    st.session_state.config_aulas = pd.concat([st.session_state.config_aulas, nueva_aula], ignore_index=True)
                    st.success(f"Aula '{nombre}' agregada")
                    st.rerun()
                else:
                    st.error("El nombre es requerido")
        
        st.markdown("---")
        
        if st.session_state.config_aulas is not None:
            st.markdown("#### Estadisticas")
            aulas = st.session_state.config_aulas
            
            total = len(aulas)
            labs = len(aulas[aulas['tipo'] == 'Lab'])
            aulas_count = len(aulas[aulas['tipo'] == 'Aula'])
            cap_promedio = aulas['capacidad'].mean()
            
            st.metric("Total espacios", total)
            st.metric("Laboratorios", labs)
            st.metric("Aulas", aulas_count)
            st.metric("Capacidad promedio", f"{cap_promedio:.0f}")

# =============================================================================
# TAB 2: GESTION DE DOCENTES
# =============================================================================
with tab2:
    st.subheader("Gestion de Docentes")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if st.session_state.config_docentes is None:
            materias_ejemplo = ['PROGRAMACION I', 'PROGRAMACION II', 'ANALISIS MATEMATICO I', 'FISICA I', 'BASE DE DATOS I']
            if st.button("Cargar docentes por defecto", use_container_width=True):
                st.session_state.config_docentes = loader.create_default_docentes(materias_ejemplo, 30)
                st.success("30 docentes cargados")
        
        if st.session_state.config_docentes is not None:
            st.markdown("#### Lista de Docentes")
            
            docentes = st.session_state.config_docentes.copy()
            
            if 'materias_puede_dictar' in docentes.columns:
                docentes['materias_str'] = docentes['materias_puede_dictar'].apply(
                    lambda x: ', '.join(x) if isinstance(x, list) else str(x)
                )
            
            st.dataframe(
                docentes[['id', 'nombre', 'materias_str']] if 'materias_str' in docentes.columns else docentes,
                use_container_width=True,
                height=400
            )
    
    with col2:
        st.markdown("#### Agregar Nuevo Docente")
        
        with st.form("form_nuevo_docente"):
            nombre_doc = st.text_input("Nombre completo", placeholder="Dr. Juan Perez")
            
            materias_disponibles = [
                'PROGRAMACION I', 'PROGRAMACION II', 'ANALISIS MATEMATICO I', 
                'FISICA I', 'ALGEBRA LINEAL', 'BASE DE DATOS I', 'BASE DE DATOS II',
                'INGENIERIA DE SOFTWARE', 'ESTRUCTURA DE DATOS', 'REDES',
                'SISTEMAS OPERATIVOS', 'INTELIGENCIA ARTIFICIAL'
            ]
            
            materias_doc = st.multiselect(
                "Materias que puede dictar",
                materias_disponibles
            )
            
            if st.form_submit_button("Agregar", use_container_width=True):
                if nombre_doc:
                    if st.session_state.config_docentes is None:
                        st.session_state.config_docentes = pd.DataFrame(columns=['id', 'nombre', 'materias_puede_dictar'])
                    
                    new_id = len(st.session_state.config_docentes)
                    nuevo_docente = pd.DataFrame([{
                        'id': new_id,
                        'nombre': nombre_doc,
                        'materias_puede_dictar': materias_doc
                    }])
                    st.session_state.config_docentes = pd.concat([st.session_state.config_docentes, nuevo_docente], ignore_index=True)
                    st.success(f"Docente '{nombre_doc}' agregado")
                    st.rerun()
                else:
                    st.error("El nombre es requerido")

# =============================================================================
# TAB 3: PLANTILLAS
# =============================================================================
with tab3:
    st.subheader("Plantillas Descargables")
    
    st.markdown("""
    Descarga las plantillas en formato Excel para cargar tus datos en el sistema.
    Completa las columnas segun las instrucciones y subelas en el modulo correspondiente.
    """)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### Plantilla de Clases")
        st.caption("Para carga de oferta/demanda")
        
        plantilla_clases = pd.DataFrame({
            'Paralelo': ['SI1-001', 'SI1-001', 'SI1-002'],
            'Asignatura': ['PROGRAMACION I', 'ANALISIS I', 'PROGRAMACION I'],
            'Nivel': ['PRIMERO', 'PRIMERO', 'PRIMERO'],
            'Estudiantes registrados': [25, 45, 30]
        })
        
        output_clases = io.BytesIO()
        with pd.ExcelWriter(output_clases, engine='openpyxl') as writer:
            plantilla_clases.to_excel(writer, sheet_name='Clases', index=False)
        
        st.download_button(
            "Descargar plantilla_clases.xlsx",
            output_clases.getvalue(),
            "plantilla_clases.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
        
        with st.expander("Ver estructura"):
            st.dataframe(plantilla_clases)
    
    with col2:
        st.markdown("#### Plantilla de Aulas")
        st.caption("Para catalogo de espacios")
        
        plantilla_aulas = pd.DataFrame({
            'nombre': ['LAB-01', 'LAB-02', 'AULA-101', 'AULA-102'],
            'tipo': ['Lab', 'Lab', 'Aula', 'Aula'],
            'capacidad': [25, 30, 40, 50],
            'edificio': ['Edificio A', 'Edificio A', 'Edificio B', 'Edificio B']
        })
        
        output_aulas = io.BytesIO()
        with pd.ExcelWriter(output_aulas, engine='openpyxl') as writer:
            plantilla_aulas.to_excel(writer, sheet_name='Aulas', index=False)
        
        st.download_button(
            "Descargar plantilla_aulas.xlsx",
            output_aulas.getvalue(),
            "plantilla_aulas.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
        
        with st.expander("Ver estructura"):
            st.dataframe(plantilla_aulas)
    
    with col3:
        st.markdown("#### Plantilla de Docentes")
        st.caption("Para registro de docentes")
        
        plantilla_docentes = pd.DataFrame({
            'nombre': ['Dr. Juan Perez', 'Ing. Maria Lopez', 'MSc. Carlos Garcia'],
            'materias': ['PROGRAMACION I, PROGRAMACION II', 'ANALISIS I, ALGEBRA', 'FISICA I, FISICA II']
        })
        
        output_docentes = io.BytesIO()
        with pd.ExcelWriter(output_docentes, engine='openpyxl') as writer:
            plantilla_docentes.to_excel(writer, sheet_name='Docentes', index=False)
        
        st.download_button(
            "Descargar plantilla_docentes.xlsx",
            output_docentes.getvalue(),
            "plantilla_docentes.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
        
        with st.expander("Ver estructura"):
            st.dataframe(plantilla_docentes)
    
    st.markdown("---")
    
    st.info("""
    **Instrucciones:**
    1. Descarga la plantilla correspondiente
    2. Abre el archivo en Excel
    3. Completa los datos siguiendo el formato de ejemplo
    4. Guarda el archivo
    5. Subelo en el modulo Profesional - Cargar Datos
    """)

# =============================================================================
# TAB 4: SISTEMA
# =============================================================================
with tab4:
    st.subheader("Configuracion del Sistema")
    
    if not is_admin:
        st.warning("Algunas opciones requieren rol de Administrador")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Parametros de Horario UCE")
        
        st.markdown("""
        | Parametro | Valor |
        |-----------|-------|
        | Bloques por dia (L-V) | 13 |
        | Bloques sabado | 6 |
        | Duracion bloque | 60 min |
        | Hora inicio | 07:00 |
        | Hora fin (L-V) | 20:00 |
        | Hora fin (Sab) | 13:00 |
        | Timeslots totales | 71 |
        """)
        
        st.markdown("---")
        
        st.markdown("#### Credenciales de Acceso")
        
        if is_admin:
            st.markdown("""
            | Rol | Contrasena |
            |-----|------------|
            | Profesional | admin123 |
            | Estudiante | estudiante123 |
            | Admin | superadmin123 |
            """)
        else:
            st.info("Solo visible para administradores")
    
    with col2:
        st.markdown("#### Estado del Sistema")
        
        st.markdown("**Sesion actual:**")
        st.write(f"- Usuario: {st.session_state.get('user_role', 'N/A')}")
        st.write(f"- Autenticado: {'Si' if st.session_state.get('authenticated') else 'No'}")
        
        st.markdown("---")
        
        st.markdown("**Datos en memoria:**")
        clases = st.session_state.get('clases_df')
        aulas = st.session_state.get('aulas_df')
        docentes = st.session_state.get('docentes_df')
        horario = st.session_state.get('horario_generado')
        
        st.write(f"- Clases cargadas: {len(clases) if clases is not None else 0}")
        st.write(f"- Aulas cargadas: {len(aulas) if aulas is not None else 0}")
        st.write(f"- Docentes cargados: {len(docentes) if docentes is not None else 0}")
        st.write(f"- Horario generado: {'Si' if horario is not None else 'No'}")
        
        st.markdown("---")
        
        if st.button("Limpiar todos los datos", type="secondary"):
            keys_to_clear = ['clases_df', 'aulas_df', 'docentes_df', 'horario_generado', 
                           'config_aulas', 'config_docentes', 'horario_estudiante']
            for key in keys_to_clear:
                if key in st.session_state:
                    st.session_state[key] = None
            st.success("Datos limpiados")
            st.rerun()
        
        st.markdown("---")
        
        st.markdown("#### Informacion del Sistema")
        st.caption("Optimizador de Horarios UCE v1.0")
        st.caption("Universidad Central del Ecuador")
        st.caption("Facultad de Ingenieria y Ciencias Aplicadas")
