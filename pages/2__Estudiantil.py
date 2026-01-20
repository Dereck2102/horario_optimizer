import streamlit as st
import pandas as pd
import sys
import os

# Asegurar que el directorio raiz este en el path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.calendar_view import create_calendar_view, get_schedule_stats

st.set_page_config(page_title="Modulo Estudiantil", page_icon="student", layout="wide")

# Verificar autenticacion
if not st.session_state.get('authenticated'):
    st.error("Acceso denegado. Inicie sesion primero.")
    st.stop()

# Logout en sidebar
st.sidebar.markdown(f"**Sesion:** {st.session_state.get('user_role')}")
if st.sidebar.button("Cerrar Sesion", use_container_width=True):
    st.session_state.authenticated = False
    st.session_state.user_role = None
    st.rerun()

st.sidebar.markdown("---")

st.title("Modulo Estudiantil")
st.markdown("Optimizacion y visualizacion de tu horario personal")

# Inicializacion de estado
if 'horario_estudiante' not in st.session_state:
    st.session_state.horario_estudiante = None
if 'preferencias_estudiante' not in st.session_state:
    st.session_state.preferencias_estudiante = {
        'dias_libres': [],
        'horario_preferido': 'Cualquiera',
        'max_horas_dia': 8,
        'min_descanso': 1
    }

# Tabs principales
tab1, tab2, tab3, tab4 = st.tabs([
    "Cargar Horario", "Preferencias", "Visualizar", "Analisis"
])

# =============================================================================
# TAB 1: CARGAR HORARIO
# =============================================================================
with tab1:
    st.subheader("Cargar tu Horario")
    
    st.markdown("""
    ### Instrucciones:
    1. Descarga tu horario desde el **SIIU** (Sistema Integrado de Informacion Universitaria)
    2. Sube el archivo Excel aqui
    3. El sistema analizara tu horario y te mostrara sugerencias de optimizacion
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Subir archivo")
        
        uploaded_file = st.file_uploader(
            "Sube tu horario (Excel)",
            type=['xlsx', 'xls'],
            key="upload_horario_estudiante",
            help="Formato del SIIU o cualquier Excel con columnas: Materia, Dia, Hora"
        )
        
        if uploaded_file:
            try:
                df = pd.read_excel(uploaded_file)
                
                # Intentar mapear columnas comunes
                column_mapping = {}
                for col in df.columns:
                    col_lower = col.lower()
                    if 'materia' in col_lower or 'asignatura' in col_lower:
                        column_mapping['materia'] = col
                    elif 'dia' in col_lower:
                        column_mapping['dia'] = col
                    elif 'hora' in col_lower and 'inicio' in col_lower:
                        column_mapping['hora_inicio'] = col
                    elif 'hora' in col_lower and 'fin' in col_lower:
                        column_mapping['hora_fin'] = col
                    elif 'aula' in col_lower or 'salon' in col_lower:
                        column_mapping['aula'] = col
                    elif 'docente' in col_lower or 'profesor' in col_lower:
                        column_mapping['docente'] = col
                    elif 'paralelo' in col_lower:
                        column_mapping['paralelo'] = col
                
                # Renombrar columnas
                df_renamed = df.rename(columns={v: k for k, v in column_mapping.items()})
                
                # Completar columnas faltantes
                if 'paralelo' not in df_renamed.columns:
                    df_renamed['paralelo'] = 'MI-HORARIO'
                if 'docente' not in df_renamed.columns:
                    df_renamed['docente'] = 'Por asignar'
                if 'aula' not in df_renamed.columns:
                    df_renamed['aula'] = 'Por asignar'
                if 'inscritos' not in df_renamed.columns:
                    df_renamed['inscritos'] = 30
                if 'capacidad_aula' not in df_renamed.columns:
                    df_renamed['capacidad_aula'] = 40
                
                st.session_state.horario_estudiante = df_renamed
                st.success(f"Horario cargado: {len(df_renamed)} clases")
                
            except Exception as e:
                st.error(f"Error al leer el archivo: {e}")
    
    with col2:
        st.markdown("#### Ingreso manual")
        
        if st.button("Usar horario de ejemplo", use_container_width=True):
            st.session_state.horario_estudiante = pd.DataFrame([
                {'materia': 'PROGRAMACION I', 'dia': 'Lunes', 'hora_inicio': '07:00', 'hora_fin': '09:00', 'aula': 'LAB-01', 'docente': 'Docente 1', 'paralelo': 'SI1-001', 'inscritos': 25, 'capacidad_aula': 30},
                {'materia': 'ANALISIS MATEMATICO I', 'dia': 'Lunes', 'hora_inicio': '11:00', 'hora_fin': '12:00', 'aula': 'AULA-15', 'docente': 'Docente 2', 'paralelo': 'SI1-001', 'inscritos': 45, 'capacidad_aula': 50},
                {'materia': 'FISICA I', 'dia': 'Martes', 'hora_inicio': '07:00', 'hora_fin': '08:00', 'aula': 'AULA-20', 'docente': 'Docente 3', 'paralelo': 'SI1-001', 'inscritos': 40, 'capacidad_aula': 50},
                {'materia': 'PROGRAMACION I', 'dia': 'Miercoles', 'hora_inicio': '09:00', 'hora_fin': '11:00', 'aula': 'LAB-01', 'docente': 'Docente 1', 'paralelo': 'SI1-001', 'inscritos': 25, 'capacidad_aula': 30},
                {'materia': 'ANALISIS MATEMATICO I', 'dia': 'Miercoles', 'hora_inicio': '14:00', 'hora_fin': '15:00', 'aula': 'AULA-15', 'docente': 'Docente 2', 'paralelo': 'SI1-001', 'inscritos': 45, 'capacidad_aula': 50},
                {'materia': 'INGLES I', 'dia': 'Jueves', 'hora_inicio': '07:00', 'hora_fin': '09:00', 'aula': 'AULA-10', 'docente': 'Docente 4', 'paralelo': 'SI1-001', 'inscritos': 30, 'capacidad_aula': 40},
                {'materia': 'FISICA I', 'dia': 'Jueves', 'hora_inicio': '15:00', 'hora_fin': '16:00', 'aula': 'AULA-20', 'docente': 'Docente 3', 'paralelo': 'SI1-001', 'inscritos': 40, 'capacidad_aula': 50},
                {'materia': 'METODOLOGIA', 'dia': 'Viernes', 'hora_inicio': '10:00', 'hora_fin': '12:00', 'aula': 'AULA-05', 'docente': 'Docente 5', 'paralelo': 'SI1-001', 'inscritos': 35, 'capacidad_aula': 40},
            ])
            st.success("Horario de ejemplo cargado")
    
    st.markdown("---")
    
    # Vista previa
    if st.session_state.horario_estudiante is not None:
        st.markdown("#### Tu horario cargado")
        st.dataframe(st.session_state.horario_estudiante, use_container_width=True)

# =============================================================================
# TAB 2: PREFERENCIAS
# =============================================================================
with tab2:
    st.subheader("Configura tus Preferencias")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Dias Preferidos")
        
        dias_libres = st.multiselect(
            "Selecciona los dias que prefieres tener libres:",
            ['Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes', 'Sabado'],
            default=st.session_state.preferencias_estudiante['dias_libres']
        )
        
        horario_pref = st.selectbox(
            "Horario preferido:",
            ['Cualquiera', 'Matutino (7:00-12:00)', 'Vespertino (12:00-18:00)', 'Nocturno (18:00-21:00)'],
            index=['Cualquiera', 'Matutino (7:00-12:00)', 'Vespertino (12:00-18:00)', 'Nocturno (18:00-21:00)'].index(
                st.session_state.preferencias_estudiante['horario_preferido']
            )
        )
    
    with col2:
        st.markdown("#### Limites de Tiempo")
        
        max_horas = st.slider(
            "Maximo de horas por dia:",
            4, 12, st.session_state.preferencias_estudiante['max_horas_dia']
        )
        
        min_descanso = st.slider(
            "Minimo de horas de descanso entre clases:",
            0, 3, st.session_state.preferencias_estudiante['min_descanso']
        )
    
    if st.button("Guardar Preferencias", type="primary", use_container_width=True):
        st.session_state.preferencias_estudiante = {
            'dias_libres': dias_libres,
            'horario_preferido': horario_pref,
            'max_horas_dia': max_horas,
            'min_descanso': min_descanso
        }
        st.success("Preferencias guardadas")
    
    st.markdown("---")
    
    st.markdown("#### Resumen de Preferencias")
    st.json(st.session_state.preferencias_estudiante)

# =============================================================================
# TAB 3: VISUALIZAR
# =============================================================================
with tab3:
    st.subheader("Visualizacion de tu Horario")
    
    if st.session_state.horario_estudiante is not None:
        horario = st.session_state.horario_estudiante
        
        # Vista calendario
        st.markdown("#### Vista Calendario")
        
        try:
            fig = create_calendar_view(horario)
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.warning(f"No se pudo generar el calendario visual: {e}")
            st.dataframe(horario, use_container_width=True)
        
        # Resumen por dia
        st.markdown("#### Resumen por Dia")
        
        dias = ['Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes', 'Sabado']
        cols = st.columns(6)
        
        for i, dia in enumerate(dias):
            with cols[i]:
                clases_dia = horario[horario['dia'] == dia]
                num_clases = len(clases_dia)
                
                if num_clases > 0:
                    st.metric(dia[:3], f"{num_clases} clases")
                    for _, clase in clases_dia.iterrows():
                        st.caption(f"- {clase['materia'][:15]}...")
                else:
                    st.metric(dia[:3], "Libre")
    else:
        st.warning("Carga tu horario primero en la pestana 'Cargar Horario'")

# =============================================================================
# TAB 4: ANALISIS
# =============================================================================
with tab4:
    st.subheader("Analisis de tu Horario")
    
    if st.session_state.horario_estudiante is not None:
        horario = st.session_state.horario_estudiante
        stats = get_schedule_stats(horario)
        
        # Metricas principales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Materias", horario['materia'].nunique())
        with col2:
            st.metric("Dias con clases", horario['dia'].nunique())
        with col3:
            st.metric("Horas semanales", f"{stats['total_horas']}h")
        with col4:
            promedio_dia = stats['total_horas'] / max(1, horario['dia'].nunique())
            st.metric("Promedio/dia", f"{promedio_dia:.1f}h")
        
        st.markdown("---")
        
        # Analisis de huecos
        st.markdown("#### Analisis de Huecos")
        
        huecos = []
        dias_unicos = horario['dia'].unique()
        
        for dia in dias_unicos:
            clases_dia = horario[horario['dia'] == dia].copy()
            if len(clases_dia) < 2:
                continue
            
            # Ordenar por hora de inicio
            clases_dia['hora_ini_num'] = clases_dia['hora_inicio'].apply(
                lambda x: int(x.split(':')[0]) if isinstance(x, str) else x.hour if hasattr(x, 'hour') else 0
            )
            clases_dia['hora_fin_num'] = clases_dia['hora_fin'].apply(
                lambda x: int(x.split(':')[0]) if isinstance(x, str) else x.hour if hasattr(x, 'hour') else 0
            )
            clases_dia = clases_dia.sort_values('hora_ini_num')
            
            for i in range(len(clases_dia) - 1):
                fin_actual = clases_dia.iloc[i]['hora_fin_num']
                inicio_siguiente = clases_dia.iloc[i + 1]['hora_ini_num']
                
                if inicio_siguiente > fin_actual:
                    hueco = inicio_siguiente - fin_actual
                    if hueco >= 2:
                        huecos.append({
                            'dia': dia,
                            'despues_de': clases_dia.iloc[i]['materia'],
                            'antes_de': clases_dia.iloc[i + 1]['materia'],
                            'duracion': hueco
                        })
        
        if huecos:
            st.warning(f"Se detectaron {len(huecos)} huecos significativos (2+ horas)")
            for h in huecos:
                st.write(f"  - **{h['dia']}**: {h['duracion']}h entre {h['despues_de']} y {h['antes_de']}")
        else:
            st.success("No se detectaron huecos significativos")
        
        st.markdown("---")
        
        # Sugerencias
        st.markdown("#### Sugerencias de Mejora")
        
        sugerencias = []
        pref = st.session_state.preferencias_estudiante
        
        for dia_libre in pref['dias_libres']:
            if dia_libre in dias_unicos:
                sugerencias.append(f"Tienes clases el {dia_libre}, pero preferias tenerlo libre")
        
        if sugerencias:
            for s in sugerencias:
                st.info(s)
        else:
            st.success("Tu horario cumple con todas tus preferencias")
    else:
        st.warning("Carga tu horario primero en la pestana 'Cargar Horario'")
