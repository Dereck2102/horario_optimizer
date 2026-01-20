"""
Modulo Usuarios
Version 4.0 - Clean Forms
"""
import streamlit as st
import pandas as pd
from core.database import get_all_users, create_user, delete_user, toggle_user_active

def show():
    if st.session_state.get('user_role') != 'Admin':
        st.error("Acceso denegado")
        return

    st.markdown("## 👥 Gestión de Usuarios")
    
    tab_list, tab_create = st.tabs(["📋 Listado de Usuarios", "➕ Nuevo Usuario"])
    
    # LISTADO
    with tab_list:
        users = get_all_users()
        if users:
            df = pd.DataFrame(users)
            df['Estado'] = df['active'].apply(lambda x: '🟢 Activo' if x else '🔴 Inactivo')
            
            st.dataframe(
                df[['username', 'name', 'role', 'Estado', 'created_at']],
                use_container_width=True,
                column_config={
                    "username": "Usuario",
                    "name": "Nombre",
                    "role": "Rol",
                    "created_at": "Fecha Creación"
                }
            )
            
            st.markdown("### Acciones Rápidas")
            c1, c2 = st.columns(2)
            with c1:
                user_sel = st.selectbox("Seleccionar Usuario", [u['username'] for u in users])
                if st.button("Cambiar Estado (Activo/Inactivo)"):
                    toggle_user_active(user_sel)
                    st.success("Estado actualizado")
                    st.rerun()
            
            with c2:
                if st.button("Eliminar Usuario Seleccionado", type="primary"):
                    if user_sel == 'admin':
                        st.error("No se puede eliminar al admin principal")
                    else:
                        delete_user(user_sel)
                        st.success("Usuario eliminado")
                        st.rerun()

    # CREACION
    with tab_create:
        st.markdown("### Registrar Nuevo Usuario")
        
        with st.form("create_user_form"):
            f_user = st.text_input("Nombre de Usuario (Login)", placeholder="ej. jperez")
            f_name = st.text_input("Nombre Completo", placeholder="ej. Juan Perez")
            f_pass = st.text_input("Contraseña Temporal", type="password")
            f_role = st.selectbox("Rol del Usuario", ["Estudiante", "Profesional", "Admin"])
            
            if st.form_submit_button("Guardar Usuario"):
                if f_user and f_name and f_pass:
                    if create_user(f_user, f_pass, f_name, f_role):
                        st.success(f"Usuario {f_user} creado correctamente")
                    else:
                        st.error("Error: El usuario ya existe")
                else:
                    st.warning("Todos los campos son obligatorios")
