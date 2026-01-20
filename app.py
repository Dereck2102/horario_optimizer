import streamlit as st

st.set_page_config(page_title="Optimizador Horarios UCE", page_icon="📅", layout="wide")

# Inicialización de estado de sesión
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user_role = None

def authenticate(role: str, password: str) -> bool:
    """Autentica al usuario según rol y contraseña."""
    passwords = {
        'Profesional': 'admin123', 
        'Estudiante': 'estudiante123', 
        'Admin': 'superadmin123'
    }
    return passwords.get(role) == password

# Pantalla de login
if not st.session_state.authenticated:
    st.title("🎓 Sistema de Optimización de Horarios")
    st.markdown("### Universidad Central del Ecuador")
    st.markdown("**Facultad de Ingeniería y Ciencias Aplicadas**")
    st.markdown("---")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.subheader("Iniciar Sesión")
        role = st.selectbox("Seleccione su rol", ["", "Profesional", "Estudiante", "Admin"])
        if role:
            password = st.text_input("Contraseña", type="password")
            if st.button("Ingresar", type="primary", use_container_width=True):
                if authenticate(role, password):
                    st.session_state.authenticated = True
                    st.session_state.user_role = role
                    st.rerun()
                else:
                    st.error("❌ Contraseña incorrecta")
            with st.expander("🔑 Credenciales de prueba"):
                creds = {'Profesional': 'admin123', 'Estudiante': 'estudiante123', 'Admin': 'superadmin123'}
                st.code(f"Usuario: {role}\nContraseña: {creds.get(role, '')}")

# Dashboard principal (usuario autenticado)
else:
    st.sidebar.success(f"✓ Sesión: {st.session_state.user_role}")
    if st.sidebar.button("🚪 Cerrar Sesión"):
        st.session_state.authenticated = False
        st.session_state.user_role = None
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.info("Navegue usando el menú lateral para acceder a los módulos")

    st.title("📅 Optimizador de Horarios Académicos")
    st.markdown("### Universidad Central del Ecuador")
    st.markdown("---")

    if st.session_state.user_role == "Profesional":
        st.success("🎓 **Modo Profesional**: Generación de horarios oficiales")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('''
            ### Funcionalidades:
            - ✅ Carga masiva de oferta/demanda
            - ✅ Gestión de disponibilidad docente
            - ✅ Configuración de aulas y labs
            - ✅ Generación optimizada
            - ✅ Exportación multi-formato
            ''')
        with col2:
            st.markdown('''
            ### Proceso:
            1. Configure aulas/labs
            2. Cargue disponibilidad docentes
            3. Importe oferta/demanda
            4. Ejecute optimización
            5. Exporte resultados
            ''')
        st.info("👈 Use **1_🎓_Profesional** en el menú lateral")

    elif st.session_state.user_role == "Estudiante":
        st.success("👨‍🎓 **Modo Estudiantil**: Optimización personal")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('''
            ### Funcionalidades:
            - ✅ Importar horario actual
            - ✅ Configurar preferencias
            - ✅ Optimizar sin conflictos
            - ✅ Comparar antes/después
            - ✅ Descargar recomendado
            ''')
        with col2:
            st.markdown('''
            ### Proceso:
            1. Descargue horario del SIIU
            2. Súbalo al sistema
            3. Configure preferencias
            4. Genere optimizado
            5. Descargue resultado
            ''')
        st.info("👈 Use **2_👨‍🎓_Estudiantil** en el menú lateral")

    else:
        st.success("⚙️ **Modo Administrador**: Configuración")
        st.markdown('''
        ### Panel:
        - ✅ Gestión aulas/labs
        - ✅ Administración docentes
        - ✅ Plantillas descargables
        - ✅ Configuración avanzada
        ''')
        st.info("👈 Use **3_⚙️_Configuracion** en el menú lateral")

    st.markdown("---")
    st.subheader("📊 Estado del Sistema")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Aulas", "50")
    with col2:
        st.metric("Labs", "12")
    with col3:
        st.metric("Docentes", "30")
    with col4:
        st.metric("Horarios", "15")
