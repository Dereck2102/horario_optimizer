import streamlit as st
import pandas as pd
import sys
import os

# Asegurar que el directorio raiz este en el path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.optimizer import HorarioOptimizer
from core.data_loader import DataLoader
from core.validator import HorarioValidator
from core.exporter import HorarioExporter
from core.calendar_view import create_calendar_view, create_heatmap_ocupacion, get_schedule_stats

st.set_page_config(page_title="Modulo Profesional", page_icon="graduation_cap", layout="wide")

# Verificar autenticacion
if not st.session_state.get('authenticated') or st.session_state.get('user_role') != 'Profesional':
    st.error("Acceso denegado. Inicie sesion como Profesional.")
    st.stop()

# Logout en sidebar
st.sidebar.markdown(f"**Sesion:** {st.session_state.get('user_role')}")
if st.sidebar.button("Cerrar Sesion", use_container_width=True):
    st.session_state.authenticated = False
    st.session_state.user_role = None
    st.rerun()

st.sidebar.markdown("---")

st.title("Modulo Profesional")
st.markdown("Generacion de horarios oficiales para la Facultad")

# Inicializacion de estado
for key in ['horario_generado', 'aulas_df', 'docentes_df', 'clases_df', 'optimizer_config']:
    if key not in st.session_state:
        st.session_state[key] = None

if st.session_state.optimizer_config is None:
    st.session_state.optimizer_config = {
        'weights': {'gaps': 10, 'capacity_waste': 5, 'teacher_balance': 3, 'building': 2},
        'time_limit_seconds': 300,
        'require_lab_for_practices': True
    }

loader = DataLoader()

# Tabs principales
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Cargar Datos", "Configurar", "Optimizar", "Visualizar", "Exportar"
])

# =============================================================================
# TAB 1: CARGAR DATOS
# =============================================================================
with tab1:
    st.subheader("Carga de Datos")
    
    col1, col2, col3 = st.columns(3)
    
    # --- CLASES ---
    with col1:
        st.markdown("#### Clases / Oferta-Demanda")
        
        clases_method = st.radio(
            "Metodo de carga:",
            ["Subir archivo Excel", "Datos de ejemplo"],
            key="clases_method",
            horizontal=True
        )
        
        if clases_method == "Subir archivo Excel":
            uploaded_clases = st.file_uploader(
                "Subir Excel de clases",
                type=['xlsx', 'xls'],
                key="upload_clases",
                help="Columnas: Paralelo, Asignatura, Nivel, Estudiantes registrados"
            )
            if uploaded_clases:
                try:
                    df = loader.load_oferta_demanda_excel(uploaded_clases)
                    st.session_state.clases_df = df
                    st.success(f"{len(df)} clases cargadas")
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            if st.button("Cargar datos de ejemplo", use_container_width=True, key="btn_clases_ejemplo"):
                # Datos basados en estructura real de UCE
                st.session_state.clases_df = pd.DataFrame([
                    {'id': 0, 'paralelo': 'SI1-001', 'materia': 'PROGRAMACION I', 'nivel': 'PRIMERO', 'inscritos': 26, 'duracion_bloques': 2, 'tipo_espacio': 'Lab'},
                    {'id': 1, 'paralelo': 'SI1-001', 'materia': 'ANALISIS MATEMATICO I', 'nivel': 'PRIMERO', 'inscritos': 48, 'duracion_bloques': 2, 'tipo_espacio': 'Aula'},
                    {'id': 2, 'paralelo': 'SI1-001', 'materia': 'FISICA I', 'nivel': 'PRIMERO', 'inscritos': 45, 'duracion_bloques': 2, 'tipo_espacio': 'Aula'},
                    {'id': 3, 'paralelo': 'SI1-002', 'materia': 'PROGRAMACION I', 'nivel': 'PRIMERO', 'inscritos': 30, 'duracion_bloques': 2, 'tipo_espacio': 'Lab'},
                    {'id': 4, 'paralelo': 'SI1-002', 'materia': 'ANALISIS MATEMATICO I', 'nivel': 'PRIMERO', 'inscritos': 52, 'duracion_bloques': 2, 'tipo_espacio': 'Aula'},
                    {'id': 5, 'paralelo': 'SI2-001', 'materia': 'PROGRAMACION II', 'nivel': 'SEGUNDO', 'inscritos': 28, 'duracion_bloques': 2, 'tipo_espacio': 'Lab'},
                    {'id': 6, 'paralelo': 'SI2-001', 'materia': 'ALGEBRA LINEAL', 'nivel': 'SEGUNDO', 'inscritos': 35, 'duracion_bloques': 2, 'tipo_espacio': 'Aula'},
                    {'id': 7, 'paralelo': 'SI3-001', 'materia': 'ESTRUCTURA DE DATOS', 'nivel': 'TERCERO', 'inscritos': 25, 'duracion_bloques': 2, 'tipo_espacio': 'Lab'},
                    {'id': 8, 'paralelo': 'SI3-001', 'materia': 'BASE DE DATOS I', 'nivel': 'TERCERO', 'inscritos': 30, 'duracion_bloques': 2, 'tipo_espacio': 'Lab'},
                ])
                st.success("9 clases de ejemplo cargadas")
        
        if st.session_state.clases_df is not None:
            st.info(f"{len(st.session_state.clases_df)} clases cargadas")
    
    # --- AULAS ---
    with col2:
        st.markdown("#### Aulas y Laboratorios")
        
        aulas_method = st.radio(
            "Metodo de carga:",
            ["Generar automatico", "Subir archivo Excel"],
            key="aulas_method",
            horizontal=True
        )
        
        if aulas_method == "Generar automatico":
            num_labs = st.number_input("Numero de laboratorios:", 5, 30, 12, key="num_labs")
            num_aulas = st.number_input("Numero de aulas:", 10, 50, 25, key="num_aulas")
            if st.button("Generar aulas", use_container_width=True, key="btn_aulas"):
                # Generar aulas con capacidades variadas
                aulas = []
                for i in range(1, num_labs + 1):
                    aulas.append({
                        'id': i - 1,
                        'nombre': f'LAB-{i:02d}',
                        'tipo': 'Lab',
                        'capacidad': 30,
                        'edificio': 'Edificio de Laboratorios'
                    })
                for i in range(1, num_aulas + 1):
                    aulas.append({
                        'id': num_labs + i - 1,
                        'nombre': f'AULA-{i:02d}',
                        'tipo': 'Aula',
                        'capacidad': 60,
                        'edificio': f'Edificio {(i-1)//10 + 1}'
                    })
                st.session_state.aulas_df = pd.DataFrame(aulas)
                st.success(f"{num_labs + num_aulas} espacios generados")
        else:
            uploaded_aulas = st.file_uploader(
                "Subir Excel de aulas",
                type=['xlsx', 'xls'],
                key="upload_aulas",
                help="Columnas: nombre, tipo (Aula/Lab), capacidad, edificio"
            )
            if uploaded_aulas:
                try:
                    df = loader.load_catalogo_aulas(uploaded_aulas)
                    st.session_state.aulas_df = df
                    st.success(f"{len(df)} aulas cargadas")
                except Exception as e:
                    st.error(f"Error: {e}")
        
        if st.session_state.aulas_df is not None:
            labs = len(st.session_state.aulas_df[st.session_state.aulas_df['tipo'] == 'Lab'])
            aulas = len(st.session_state.aulas_df[st.session_state.aulas_df['tipo'] == 'Aula'])
            st.info(f"{labs} labs + {aulas} aulas")
    
    # --- DOCENTES ---
    with col3:
        st.markdown("#### Docentes")
        
        docentes_method = st.radio(
            "Metodo de carga:",
            ["Generar automatico", "Subir archivo Excel"],
            key="docentes_method",
            horizontal=True
        )
        
        if docentes_method == "Generar automatico":
            num_docentes = st.number_input("Numero de docentes:", 10, 100, 30, key="num_docentes")
            if st.button("Generar docentes", use_container_width=True, key="btn_docentes"):
                if st.session_state.clases_df is not None:
                    materias = st.session_state.clases_df['materia'].unique().tolist()
                    st.session_state.docentes_df = loader.create_default_docentes(materias, num_docentes)
                    st.success(f"{num_docentes} docentes generados")
                else:
                    st.warning("Cargue las clases primero")
        else:
            uploaded_docentes = st.file_uploader(
                "Subir Excel de docentes",
                type=['xlsx', 'xls'],
                key="upload_docentes",
                help="Columnas: nombre, materias (separadas por coma)"
            )
            if uploaded_docentes:
                try:
                    df = loader.load_disponibilidad_docente(uploaded_docentes)
                    st.session_state.docentes_df = df
                    st.success(f"{len(df)} docentes cargados")
                except Exception as e:
                    st.error(f"Error: {e}")
        
        if st.session_state.docentes_df is not None:
            st.info(f"{len(st.session_state.docentes_df)} docentes")
    
    st.markdown("---")
    
    # Vista previa de datos
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.session_state.clases_df is not None:
            with st.expander("Ver clases"):
                st.dataframe(st.session_state.clases_df, use_container_width=True, height=300)
    
    with col2:
        if st.session_state.aulas_df is not None:
            with st.expander("Ver aulas"):
                st.dataframe(st.session_state.aulas_df, use_container_width=True, height=300)
    
    with col3:
        if st.session_state.docentes_df is not None:
            with st.expander("Ver docentes"):
                st.dataframe(st.session_state.docentes_df, use_container_width=True, height=300)

# =============================================================================
# TAB 2: CONFIGURAR
# =============================================================================
with tab2:
    st.subheader("Configuracion del Optimizador")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Pesos de Objetivos")
        st.caption("Mayor peso = mayor prioridad en la optimizacion")
        
        weight_gaps = st.slider(
            "Minimizar huecos en horarios",
            0, 20, st.session_state.optimizer_config['weights']['gaps'],
            help="Reduce espacios vacios entre clases"
        )
        
        weight_capacity = st.slider(
            "Optimizar uso de capacidad",
            0, 20, st.session_state.optimizer_config['weights']['capacity_waste'],
            help="Asigna aulas con capacidad cercana a inscritos"
        )
        
        weight_balance = st.slider(
            "Balancear carga docente",
            0, 20, st.session_state.optimizer_config['weights']['teacher_balance'],
            help="Distribuye clases equitativamente entre docentes"
        )
        
        weight_building = st.slider(
            "Compactar por edificio",
            0, 20, st.session_state.optimizer_config['weights']['building'],
            help="Agrupa clases del mismo paralelo en un edificio"
        )
    
    with col2:
        st.markdown("#### Parametros del Solver")
        
        time_limit = st.slider(
            "Tiempo limite (segundos)",
            60, 600, st.session_state.optimizer_config['time_limit_seconds'],
            help="Tiempo maximo de busqueda de solucion. Aumentar si no encuentra solucion."
        )
        
        require_lab = st.checkbox(
            "Requerir laboratorio para practicas",
            value=st.session_state.optimizer_config['require_lab_for_practices'],
            help="Materias de programacion/lab requieren espacio tipo Lab"
        )
        
        st.markdown("---")
        
        st.markdown("#### Resumen de Configuracion")
        st.json({
            'Peso huecos': weight_gaps,
            'Peso capacidad': weight_capacity,
            'Peso balance': weight_balance,
            'Peso edificio': weight_building,
            'Tiempo limite': f"{time_limit}s",
            'Requiere lab': require_lab
        })
    
    if st.button("Guardar Configuracion", type="primary", use_container_width=True):
        st.session_state.optimizer_config = {
            'weights': {
                'gaps': weight_gaps,
                'capacity_waste': weight_capacity,
                'teacher_balance': weight_balance,
                'building': weight_building
            },
            'time_limit_seconds': time_limit,
            'require_lab_for_practices': require_lab
        }
        st.success("Configuracion guardada")

# =============================================================================
# TAB 3: OPTIMIZAR
# =============================================================================
with tab3:
    st.subheader("Optimizacion del Horario")
    
    # Estado de requisitos
    ready = all([
        st.session_state.clases_df is not None, 
        st.session_state.aulas_df is not None, 
        st.session_state.docentes_df is not None
    ])
    
    if not ready:
        st.warning("Complete la carga de datos primero:")
        col1, col2, col3 = st.columns(3)
        with col1:
            status = "OK" if st.session_state.clases_df is not None else "Pendiente"
            st.write(f"Clases: {status}")
        with col2:
            status = "OK" if st.session_state.aulas_df is not None else "Pendiente"
            st.write(f"Aulas: {status}")
        with col3:
            status = "OK" if st.session_state.docentes_df is not None else "Pendiente"
            st.write(f"Docentes: {status}")
    else:
        st.success("Datos listos para optimizacion")
        
        # Mostrar resumen
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Clases a programar", len(st.session_state.clases_df))
        with col2:
            st.metric("Espacios disponibles", len(st.session_state.aulas_df))
        with col3:
            st.metric("Docentes disponibles", len(st.session_state.docentes_df))
        
        st.markdown("---")
        
        if st.button("Ejecutar Optimizacion", type="primary", use_container_width=True):
            progress_bar = st.progress(0, text="Inicializando...")
            
            try:
                progress_bar.progress(10, text="Creando modelo de optimizacion...")
                
                opt = HorarioOptimizer(st.session_state.optimizer_config)
                
                progress_bar.progress(30, text="Agregando restricciones...")
                
                result = opt.optimize(
                    st.session_state.clases_df,
                    st.session_state.aulas_df,
                    st.session_state.docentes_df
                )
                
                progress_bar.progress(90, text="Procesando resultados...")

                if result['status'] == 'success':
                    st.session_state.horario_generado = result['schedule']
                    progress_bar.progress(100, text="Completado")
                    
                    st.success("Horario generado exitosamente")
                    
                    # Metricas
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Clases asignadas", result['metrics']['total_clases'])
                    with col2:
                        st.metric("Aulas usadas", result['metrics']['aulas_utilizadas'])
                    with col3:
                        st.metric("Docentes asignados", result['metrics']['docentes_asignados'])
                    with col4:
                        st.metric("Ocupacion promedio", f"{result['metrics']['promedio_ocupacion']:.1f}%")
                    
                    # Stats del solver
                    with st.expander("Estadisticas del solver"):
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Tiempo", f"{result['solver_stats']['wall_time']:.2f}s")
                        with col2:
                            st.metric("Conflictos", result['solver_stats']['conflicts'])
                        with col3:
                            st.metric("Ramas", result['solver_stats']['branches'])
                        with col4:
                            st.metric("Optima", "Si" if result['optimal'] else "No")
                    
                    # Validacion
                    validator = HorarioValidator()
                    validation = validator.validate_horario(result['schedule'])
                    if validation['valid']:
                        st.success("Horario validado sin conflictos")
                    else:
                        st.error(f"Conflictos: {validation['errors']}")
                    
                    # Vista previa
                    st.markdown("#### Vista previa del horario")
                    st.dataframe(result['schedule'], use_container_width=True)
                else:
                    progress_bar.progress(100, text="Error")
                    st.error(f"No se pudo generar el horario: {result.get('reason', 'Desconocido')}")
                    st.warning("Sugerencias: Aumente el tiempo limite, agregue mas aulas/docentes, o reduzca las restricciones.")
                    
            except Exception as e:
                progress_bar.progress(100, text="Error")
                st.error(f"Error durante la optimizacion: {e}")

# =============================================================================
# TAB 4: VISUALIZAR
# =============================================================================
with tab4:
    st.subheader("Visualizacion del Horario")
    
    if st.session_state.horario_generado is not None:
        horario = st.session_state.horario_generado
        
        # Filtros
        col1, col2, col3 = st.columns(3)
        
        with col1:
            filter_paralelo = st.selectbox(
                "Filtrar por paralelo:",
                ["Todos"] + list(horario['paralelo'].unique()),
                key="filter_paralelo"
            )
        
        with col2:
            filter_docente = st.selectbox(
                "Filtrar por docente:",
                ["Todos"] + list(horario['docente'].unique()),
                key="filter_docente"
            )
        
        with col3:
            filter_aula = st.selectbox(
                "Filtrar por aula:",
                ["Todas"] + list(horario['aula'].unique()),
                key="filter_aula"
            )
        
        # Aplicar filtros
        df_filtered = horario.copy()
        if filter_paralelo != "Todos":
            df_filtered = df_filtered[df_filtered['paralelo'] == filter_paralelo]
        if filter_docente != "Todos":
            df_filtered = df_filtered[df_filtered['docente'] == filter_docente]
        if filter_aula != "Todas":
            df_filtered = df_filtered[df_filtered['aula'] == filter_aula]
        
        st.markdown("---")
        
        # Vista calendario
        st.markdown("#### Vista Calendario")
        
        try:
            fig_calendar = create_calendar_view(df_filtered)
            st.plotly_chart(fig_calendar, use_container_width=True)
        except Exception as e:
            st.warning(f"No se pudo generar el calendario: {e}")
            st.dataframe(df_filtered, use_container_width=True)
        
        # Mapa de ocupacion
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Mapa de Ocupacion")
            try:
                fig_heatmap = create_heatmap_ocupacion(df_filtered)
                st.plotly_chart(fig_heatmap, use_container_width=True)
            except Exception as e:
                st.warning(f"No se pudo generar el mapa: {e}")
        
        with col2:
            st.markdown("#### Estadisticas")
            stats = get_schedule_stats(df_filtered)
            
            st.metric("Total de clases", stats['total_clases'])
            st.metric("Total de horas", f"{stats['total_horas']}h")
            
            if stats['clases_por_dia']:
                st.markdown("**Clases por dia:**")
                for dia, count in stats['clases_por_dia'].items():
                    st.write(f"  - {dia}: {count}")
    else:
        st.warning("Genere un horario primero en la pestana 'Optimizar'")

# =============================================================================
# TAB 5: EXPORTAR
# =============================================================================
with tab5:
    st.subheader("Exportar Horario")
    
    if st.session_state.horario_generado is not None:
        exporter = HorarioExporter()
        horario = st.session_state.horario_generado
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Exportar a Excel")
            excel_data = exporter.export_to_excel(horario)
            st.download_button(
                "Descargar Excel Completo", 
                excel_data, 
                "horario_completo.xlsx", 
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
            st.caption("Incluye pestanas: Completo, por Paralelo, por Docente")
        
        with col2:
            st.markdown("#### Exportar a CSV")
            csv_data = exporter.export_to_csv(horario)
            st.download_button(
                "Descargar CSV", 
                csv_data, 
                "horario.csv", 
                "text/csv",
                use_container_width=True
            )
            st.caption("Formato simple para importar a otros sistemas")
        
        st.markdown("---")
        st.markdown("#### Vista previa")
        st.dataframe(horario, use_container_width=True)
    else:
        st.warning("Genere un horario primero en la pestana 'Optimizar'")
