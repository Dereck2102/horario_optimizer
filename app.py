import streamlit as st

st.set_page_config(page_title="Optimizador Horarios UCE", page_icon="calendar", layout="wide")

# Inicializacion de estado de sesion
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user_role = None

def authenticate(role: str, password: str) -> bool:
    """Autentica al usuario segun rol y contrasena."""
    passwords = {
        'Profesional': 'admin123', 
        'Estudiante': 'estudiante123', 
        'Admin': 'superadmin123'
    }
    return passwords.get(role) == password

def logout():
    """Cierra la sesion del usuario."""
    st.session_state.authenticated = False
    st.session_state.user_role = None
    # Limpiar datos de sesion
    keys_to_clear = ['clases_df', 'aulas_df', 'docentes_df', 'horario_generado', 
                     'optimizer_config', 'horario_estudiante', 'preferencias_estudiante',
                     'config_aulas', 'config_docentes']
    for key in keys_to_clear:
        if key in st.session_state:
            st.session_state[key] = None

# Pantalla de login
if not st.session_state.authenticated:
    st.title("Sistema de Optimizacion de Horarios")
    st.markdown("### Universidad Central del Ecuador")
    st.markdown("**Facultad de Ingenieria y Ciencias Aplicadas**")
    st.markdown("---")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.subheader("Iniciar Sesion")
        role = st.selectbox("Seleccione su rol", ["", "Profesional", "Estudiante", "Admin"])
        if role:
            password = st.text_input("Contrasena", type="password")
            if st.button("Ingresar", type="primary", use_container_width=True):
                if authenticate(role, password):
                    st.session_state.authenticated = True
                    st.session_state.user_role = role
                    st.rerun()
                else:
                    st.error("Contrasena incorrecta")
            with st.expander("Credenciales de prueba"):
                creds = {'Profesional': 'admin123', 'Estudiante': 'estudiante123', 'Admin': 'superadmin123'}
                st.code(f"Usuario: {role}\nContrasena: {creds.get(role, '')}")

# Dashboard principal (usuario autenticado)
else:
    # Sidebar con informacion de sesion y logout
    st.sidebar.markdown(f"**Sesion:** {st.session_state.user_role}")
    if st.sidebar.button("Cerrar Sesion", use_container_width=True):
        logout()
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.info("Navegue usando el menu lateral para acceder a los modulos")

    st.title("Optimizador de Horarios Academicos")
    st.markdown("### Universidad Central del Ecuador")
    st.markdown("---")

    if st.session_state.user_role == "Profesional":
        st.success("**Modo Profesional**: Generacion de horarios oficiales")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('''
            ### Funcionalidades:
            - Carga masiva de oferta/demanda
            - Gestion de disponibilidad docente
            - Configuracion de aulas y labs
            - Generacion optimizada
            - Exportacion multi-formato
            ''')
        with col2:
            st.markdown('''
            ### Proceso:
            1. Configure aulas/labs
            2. Cargue disponibilidad docentes
            3. Importe oferta/demanda
            4. Ejecute optimizacion
            5. Exporte resultados
            ''')
        st.info("Use **1_Profesional** en el menu lateral")

    elif st.session_state.user_role == "Estudiante":
        st.success("**Modo Estudiantil**: Optimizacion personal")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('''
            ### Funcionalidades:
            - Importar horario actual
            - Configurar preferencias
            - Optimizar sin conflictos
            - Comparar antes/despues
            - Descargar recomendado
            ''')
        with col2:
            st.markdown('''
            ### Proceso:
            1. Descargue horario del SIIU
            2. Subalo al sistema
            3. Configure preferencias
            4. Genere optimizado
            5. Descargue resultado
            ''')
        st.info("Use **2_Estudiantil** en el menu lateral")

    else:
        st.success("**Modo Administrador**: Configuracion")
        st.markdown('''
        ### Panel:
        - Gestion aulas/labs
        - Administracion docentes
        - Plantillas descargables
        - Configuracion avanzada
        ''')
        st.info("Use **3_Configuracion** en el menu lateral")

    st.markdown("---")
    st.subheader("Estado del Sistema")
    col1, col2, col3, col4 = st.columns(4)
    
    # Mostrar datos reales si existen
    clases = st.session_state.get('clases_df')
    aulas = st.session_state.get('aulas_df')
    docentes = st.session_state.get('docentes_df')
    horario = st.session_state.get('horario_generado')
    
    with col1:
        count = len(aulas) if aulas is not None else 0
        st.metric("Aulas", count)
    with col2:
        count = len(aulas[aulas['tipo'] == 'Lab']) if aulas is not None and 'tipo' in aulas.columns else 0
        st.metric("Labs", count)
    with col3:
        count = len(docentes) if docentes is not None else 0
        st.metric("Docentes", count)
    with col4:
        count = len(horario) if horario is not None else 0
        st.metric("Clases programadas", count)
