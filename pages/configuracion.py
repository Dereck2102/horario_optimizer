"""
Modulo Configuracion (Ajustes y Cuenta)
Version 3.0 - SQLite Integration
"""

import streamlit as st
import pandas as pd
from core.database import update_user_password, get_user

def show():
    st.markdown("## ⚙️ Configuración")
    
    user_role = st.session_state.user_role
    username = st.session_state.username
    
    # Tab unico por ahora, mas simple
    st.markdown("### Mi Cuenta")
    
    user_data = get_user(username)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.05);padding:1rem;border-radius:10px;">
            <p><strong>Usuario:</strong> {username}</p>
            <p><strong>Nombre:</strong> {user_data['name']}</p>
            <p><strong>Rol:</strong> {user_data['role']}</p>
            <p><strong>Estado:</strong> {'Activo' if user_data['active'] else 'Inactivo'}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("#### Cambiar Contraseña")
        with st.form("change_pass_conf"):
            curr_pass = st.text_input("Contraseña Actual", type="password")
            new_pass = st.text_input("Nueva Contraseña", type="password")
            conf_pass = st.text_input("Confirmar Nueva", type="password")
            
            if st.form_submit_button("Actualizar", type="primary"):
                if curr_pass != user_data['password']:
                    st.error("Contraseña actual incorrecta")
                elif new_pass != conf_pass:
                    st.error("Las nuevas contraseñas no coinciden")
                elif not new_pass:
                    st.error("La contraseña no puede estar vacia")
                else:
                    if update_user_password(username, new_pass):
                        st.success("✅ Contraseña actualizada correctamente")
                    else:
                        st.error("Error al actualizar")

    st.markdown("---")
    st.markdown("### Sobre la Aplicación")
    st.markdown("""
    **Horarios UCE v3.0**
    
    Sistema de optimización de horarios para la Facultad de Ingeniería y Ciencias Aplicadas.
    Universidad Central del Ecuador.
    
    Desarrollado con:
    - Python (Streamlit)
    - Google OR-Tools (Motor de optimización)
    - SQLite (Base de datos)
    """)
