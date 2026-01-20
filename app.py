"""
Sistema de Optimizacion de Horarios Academicos
Universidad Central del Ecuador

Version 4.0 - UI Polish, Dark/Light Mode, Strict Sidebar Logic
"""

import streamlit as st
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.database import (
    authenticate_user, get_stats, get_all_horarios
)

# Configuracion inicial
st.set_page_config(
    page_title="Horarios UCE",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estado de autenticacion inicial
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user_role = None
    st.session_state.username = None
    st.session_state.user_name = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'dashboard'

# =============================================================================
# CSS THEME & ESTILOS
# =============================================================================
st.markdown("""
<style>
    /* Ocultar elementos de Streamlit no deseados */
    [data-testid="stSidebarNav"], footer, #MainMenu { display: none; }
    
    /* Variables CSS para Modo Claro/Oscuro Adaptable */
    :root {
        --primary-color: #d32f2f;
        --primary-hover: #b71c1c;
        --bg-color: #ffffff;
        --text-color: #0f172a;
        --card-bg: #f8fafc;
        --border-color: #e2e8f0;
        --input-bg: #ffffff;
        --input-border: #cbd5e1;
    }
    
    @media (prefers-color-scheme: dark) {
        :root {
            --primary-color: #ef4444;
            --primary-hover: #dc2626;
            --bg-color: #0f172a;
            --text-color: #f8fafc;
            --card-bg: #1e293b;
            --border-color: #334155;
            --input-bg: #1e293b;
            --input-border: #475569;
        }
    }
    
    /* Aplicar variables generales */
    .stApp {
        background-color: var(--bg-color);
        color: var(--text-color);
    }
    
    h1, h2, h3, h4, h5, h6, p, span, div {
        color: var(--text-color);
    }
    
    /* Cards Genericas */
    .app-card {
        background-color: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    /* Login Styles */
    .login-container {
        max-width: 400px;
        margin: 10vh auto;
        padding: 2.5rem;
        background-color: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 16px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        text-align: center;
    }
    
    .login-logo {
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    
    .stTextInput > label {
        color: var(--text-color) !important;
        font-weight: 500;
        margin-bottom: 0.25rem;
    }
    
    .stTextInput > div > div > input {
        background-color: var(--input-bg) !important;
        color: var(--text-color) !important;
        border: 1px solid var(--input-border) !important;
        border-radius: 8px !important;
        padding: 0.75rem !important;
    }
    
    .stButton > button {
        background-color: var(--primary-color) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
        transition: all 0.2s;
    }
    
    .stButton > button:hover {
        background-color: var(--primary-hover) !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    }
    
    /* Sidebar Custom */
    [data-testid="stSidebar"] {
        background-color: var(--card-bg);
        border-right: 1px solid var(--border-color);
    }
    
    [data-testid="stSidebar"] .stButton > button {
        background: transparent !important;
        color: var(--text-color) !important;
        border: 1px solid transparent !important;
        text-align: left !important;
        justify-content: flex-start !important;
        box-shadow: none !important;
    }
    
    [data-testid="stSidebar"] .stButton > button:hover {
        background-color: rgba(128, 128, 128, 0.1) !important;
        border-color: var(--border-color) !important;
    }
    
    /* Grid de Horarios */
    .schedule-grid {
        width: 100%;
        border-collapse: collapse;
        margin-top: 1rem;
    }
    
    .schedule-grid th {
        background-color: var(--card-bg);
        color: var(--text-color);
        border: 1px solid var(--border-color);
        padding: 0.75rem;
        font-weight: 600;
    }
    
    .schedule-grid td {
        border: 1px solid var(--border-color);
        padding: 0.5rem;
        vertical-align: top;
        font-size: 0.85rem;
        height: 60px;
    }
    
    .schedule-grid .hour-cell {
        background-color: var(--card-bg);
        font-weight: 600;
        text-align: center;
        width: 80px;
    }
    
    .class-tag {
        display: block;
        padding: 4px 8px;
        border-radius: 4px;
        margin-bottom: 4px;
        font-size: 0.75rem;
        color: white;
        background-color: #3b82f6; /* Default Blue */
    }
    
    .class-tag.lab { background-color: #10b981; } /* Green */
    .class-tag.teoria { background-color: #3b82f6; } /* Blue */
</style>
""", unsafe_allow_html=True)

# Lógica para ocultar sidebar en Login
if not st.session_state.authenticated:
    st.markdown("""
    <style>
        [data-testid="stSidebar"] { display: none; }
        [data-testid="collapsedControl"] { display: none; }
    </style>
    """, unsafe_allow_html=True)

# =============================================================================
# FUNCIONES
# =============================================================================

def logout():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# =============================================================================
# LOGIN SCREEN
# =============================================================================

def show_login():
    col1, col2, col3 = st.columns([1, 1.2, 1])
    
    with col2:
        st.markdown("""
        <div class="login-container">
            <div class="login-logo">🏛️</div>
            <h2 style="margin-bottom:0.5rem;">Sistema de Horarios</h2>
            <p style="opacity:0.7; margin-bottom:2rem;">Universidad Central del Ecuador</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Formulario centrado usando columnas internas
        with st.container():
            c1, c2, c3 = st.columns([0.1, 0.8, 0.1])
            with c2:
                username = st.text_input("Usuario", placeholder="Ingrese su usuario")
                password = st.text_input("Contraseña", type="password", placeholder="Ingrese su contraseña")
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                if st.button("Ingresar al Sistema", use_container_width=True):
                    if username and password:
                        user = authenticate_user(username, password)
                        if user:
                            st.session_state.authenticated = True
                            st.session_state.user_role = user['role']
                            st.session_state.username = username
                            st.session_state.user_name = user['name']
                            st.session_state.current_page = 'dashboard'
                            st.rerun()
                        else:
                            st.error("Credenciales incorrectas")
                    else:
                        st.warning("Ingrese usuario y contraseña")
        
        st.markdown("<div style='text-align:center; margin-top:2rem; opacity:0.5; font-size:0.8rem;'>Facultad de Ingeniería y Ciencias Aplicadas</div>", unsafe_allow_html=True)

# =============================================================================
# SIDEBAR
# =============================================================================

def show_sidebar():
    role = st.session_state.user_role
    
    with st.sidebar:
        st.markdown(f"""
        <div style="padding: 1rem 0; text-align: center;">
            <div style="width: 60px; height: 60px; background-color: var(--primary-color); color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; margin: 0 auto 1rem auto;">
                {st.session_state.user_name[0].upper()}
            </div>
            <div style="font-weight: 600; font-size: 1.1rem;">{st.session_state.user_name}</div>
            <div style="opacity: 0.7; font-size: 0.9rem;">{role}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        if st.button("📊 Dashboard Principal", use_container_width=True):
            st.session_state.current_page = 'dashboard'
            st.rerun()
            
        if role == 'Admin':
            st.caption("ADMINISTRACIÓN")
            if st.button("📅 Generar Horarios", use_container_width=True):
                st.session_state.current_page = 'profesional'
                st.rerun()
            if st.button("👥 Gestionar Usuarios", use_container_width=True):
                st.session_state.current_page = 'usuarios'
                st.rerun()
            if st.button("📄 Plantillas de Datos", use_container_width=True):
                st.session_state.current_page = 'plantillas'
                st.rerun()
                
        elif role == 'Profesional':
            st.caption("DOCENTE")
            if st.button("📝 Mi Disponibilidad", use_container_width=True):
                st.session_state.current_page = 'disponibilidad'
                st.rerun()
            if st.button("📄 Plantillas", use_container_width=True):
                st.session_state.current_page = 'plantillas'
                st.rerun()
                
        elif role == 'Estudiante':
            st.caption("ESTUDIANTE")
            if st.button("📅 Mi Horario", use_container_width=True):
                st.session_state.current_page = 'mi_horario'
                st.rerun()
        
        st.markdown("---")
        if st.button("⚙️ Configuración", use_container_width=True):
            st.session_state.current_page = 'configuracion'
            st.rerun()
            
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            logout()

# =============================================================================
# ROUTER
# =============================================================================

def main():
    if not st.session_state.authenticated:
        show_login()
        return
    
    try:
        show_sidebar()
        
        page = st.session_state.current_page
        role = st.session_state.user_role
        
        if page == 'dashboard':
            from pages import dashboard
            dashboard.show()
        elif page == 'plantillas':
            from pages import plantillas
            plantillas.show()
        elif page == 'profesional' and role == 'Admin':
            from pages import profesional
            profesional.show()
        elif page == 'usuarios' and role == 'Admin':
            from pages import usuarios
            usuarios.show()
        elif page == 'disponibilidad' and role == 'Profesional':
            from pages import disponibilidad
            disponibilidad.show()
        elif page == 'mi_horario' and role == 'Estudiante':
            from pages import mi_horario
            mi_horario.show()
        elif page == 'configuracion':
            from pages import configuracion
            configuracion.show()
        else:
            from pages import dashboard
            dashboard.show()
            
    except Exception as e:
        st.error(f"Error cargando módulo: {e}")
        st.button("Volver al Inicio", on_click=lambda: setattr(st.session_state, 'current_page', 'dashboard'))

if __name__ == "__main__":
    main()
