import streamlit as st
import pandas as pd
import sys
import os

# Asegurar que el directorio raíz esté en el path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.optimizer import HorarioOptimizer
from core.data_loader import DataLoader
from core.validator import HorarioValidator
from core.exporter import HorarioExporter

st.set_page_config(page_title="Módulo Profesional", page_icon="🎓", layout="wide")

# Verificar autenticación
if not st.session_state.get('authenticated') or st.session_state.get('user_role') != 'Profesional':
    st.error("❌ Acceso denegado. Inicie sesión como Profesional.")
    st.stop()

st.title("🎓 Módulo Profesional")
st.markdown("Generación de horarios oficiales para la Facultad")

# Inicialización de estado
if 'horario_generado' not in st.session_state:
    st.session_state.horario_generado = None
if 'aulas_df' not in st.session_state:
    st.session_state.aulas_df = None
if 'docentes_df' not in st.session_state:
    st.session_state.docentes_df = None
if 'clases_df' not in st.session_state:
    st.session_state.clases_df = None

loader = DataLoader()

# Tabs principales
tab1, tab2, tab3 = st.tabs(["📥 Cargar Datos", "⚙️ Optimizar", "📤 Exportar"])

with tab1:
    st.subheader("Carga de Datos")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### Clases")
        if st.button("📚 Usar datos de ejemplo", use_container_width=True):
            st.session_state.clases_df = pd.DataFrame([
                {'id': 0, 'paralelo': 'SI1-001', 'materia': 'PROGRAMACION I', 'nivel': 'PRIMERO', 'inscritos': 26, 'duracion_bloques': 2, 'tipo_espacio': 'Lab'},
                {'id': 1, 'paralelo': 'SI1-001', 'materia': 'ANALISIS I', 'nivel': 'PRIMERO', 'inscritos': 48, 'duracion_bloques': 1, 'tipo_espacio': 'Aula'},
                {'id': 2, 'paralelo': 'SI1-002', 'materia': 'PROGRAMACION I', 'nivel': 'PRIMERO', 'inscritos': 58, 'duracion_bloques': 2, 'tipo_espacio': 'Lab'},
                {'id': 3, 'paralelo': 'SI1-002', 'materia': 'FISICA I', 'nivel': 'PRIMERO', 'inscritos': 35, 'duracion_bloques': 1, 'tipo_espacio': 'Aula'},
                {'id': 4, 'paralelo': 'SI2-001', 'materia': 'PROGRAMACION II', 'nivel': 'SEGUNDO', 'inscritos': 30, 'duracion_bloques': 2, 'tipo_espacio': 'Lab'},
            ])
            st.success("✅ 5 clases de ejemplo cargadas")
        
        if st.session_state.clases_df is not None:
            st.info(f"📊 {len(st.session_state.clases_df)} clases cargadas")
    
    with col2:
        st.markdown("#### Aulas")
        if st.button("🏛️ Generar aulas", use_container_width=True):
            st.session_state.aulas_df = loader.create_default_aulas(40)
            st.success("✅ 40 aulas generadas")
        
        if st.session_state.aulas_df is not None:
            labs = len(st.session_state.aulas_df[st.session_state.aulas_df['tipo'] == 'Lab'])
            aulas = len(st.session_state.aulas_df[st.session_state.aulas_df['tipo'] == 'Aula'])
            st.info(f"📊 {labs} labs + {aulas} aulas")
    
    with col3:
        st.markdown("#### Docentes")
        if st.button("👨‍🏫 Generar docentes", use_container_width=True):
            if st.session_state.clases_df is not None:
                materias = st.session_state.clases_df['materia'].unique().tolist()
                st.session_state.docentes_df = loader.create_default_docentes(materias, 20)
                st.success("✅ 20 docentes generados")
            else:
                st.warning("⚠️ Cargue las clases primero")
        
        if st.session_state.docentes_df is not None:
            st.info(f"📊 {len(st.session_state.docentes_df)} docentes")
    
    st.markdown("---")
    
    # Vista previa de datos
    if st.session_state.clases_df is not None:
        with st.expander("👀 Ver clases cargadas"):
            st.dataframe(st.session_state.clases_df, use_container_width=True)

with tab2:
    st.subheader("Optimización del Horario")
    
    # Estado de requisitos
    ready = all([
        st.session_state.clases_df is not None, 
        st.session_state.aulas_df is not None, 
        st.session_state.docentes_df is not None
    ])
    
    if not ready:
        st.warning("⚠️ Complete la carga de datos primero:")
        col1, col2, col3 = st.columns(3)
        with col1:
            status = "✅" if st.session_state.clases_df is not None else "❌"
            st.write(f"{status} Clases")
        with col2:
            status = "✅" if st.session_state.aulas_df is not None else "❌"
            st.write(f"{status} Aulas")
        with col3:
            status = "✅" if st.session_state.docentes_df is not None else "❌"
            st.write(f"{status} Docentes")
    else:
        st.success("✅ Datos listos para optimización")
        
        if st.button("🚀 Ejecutar Optimización", type="primary", use_container_width=True):
            with st.spinner("Optimizando horario... Esto puede tomar unos segundos."):
                try:
                    opt = HorarioOptimizer()
                    result = opt.optimize(
                        st.session_state.clases_df,
                        st.session_state.aulas_df,
                        st.session_state.docentes_df
                    )

                    if result['status'] == 'success':
                        st.session_state.horario_generado = result['schedule']
                        st.success("✅ ¡Horario generado exitosamente!")
                        
                        # Métricas
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Clases", result['metrics']['total_clases'])
                        with col2:
                            st.metric("Aulas usadas", result['metrics']['aulas_utilizadas'])
                        with col3:
                            st.metric("Docentes", result['metrics']['docentes_asignados'])
                        with col4:
                            st.metric("Ocupación", f"{result['metrics']['promedio_ocupacion']:.1f}%")
                        
                        # Stats del solver
                        with st.expander("📊 Estadísticas del solver"):
                            st.write(f"⏱️ Tiempo: {result['solver_stats']['wall_time']:.2f}s")
                            st.write(f"🔄 Conflictos: {result['solver_stats']['conflicts']}")
                            st.write(f"🌳 Ramas: {result['solver_stats']['branches']}")
                            st.write(f"✨ Solución óptima: {'Sí' if result['optimal'] else 'No (factible)'}")
                        
                        # Vista del horario
                        st.dataframe(result['schedule'], use_container_width=True)
                        
                        # Validación
                        validator = HorarioValidator()
                        validation = validator.validate_horario(result['schedule'])
                        if validation['valid']:
                            st.success("✅ Horario validado sin conflictos")
                        else:
                            st.error(f"❌ Conflictos detectados: {validation['errors']}")
                    else:
                        st.error(f"❌ Error: {result.get('reason', 'Desconocido')}")
                except Exception as e:
                    st.error(f"❌ Error durante la optimización: {e}")

with tab3:
    st.subheader("Exportar Horario")
    
    if st.session_state.horario_generado is not None:
        exporter = HorarioExporter()
        
        col1, col2 = st.columns(2)
        
        with col1:
            excel_data = exporter.export_to_excel(st.session_state.horario_generado)
            st.download_button(
                "📥 Descargar Excel", 
                excel_data, 
                "horario.xlsx", 
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
            st.caption("Incluye pestañas por paralelo y por docente")
        
        with col2:
            csv_data = exporter.export_to_csv(st.session_state.horario_generado)
            st.download_button(
                "📥 Descargar CSV", 
                csv_data, 
                "horario.csv", 
                "text/csv",
                use_container_width=True
            )
            st.caption("Formato simple para importar a otros sistemas")
        
        st.markdown("---")
        st.markdown("#### Vista previa")
        st.dataframe(st.session_state.horario_generado, use_container_width=True)
    else:
        st.warning("⚠️ Genere un horario primero en la pestaña 'Optimizar'")
