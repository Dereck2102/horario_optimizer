"""
Modulo Disponibilidad (Profesores)
Version 3.0 - SQLite Integration
"""

import streamlit as st
import pandas as pd
from core.database import save_disponibilidad, get_disponibilidad

def show():
    if st.session_state.get('user_role') != 'Profesional':
        st.error("Acceso no autorizado")
        return

    st.markdown("## 📝 Mi Disponibilidad")
    st.info("Marca las horas en las que PUEDES impartir clases.")
    
    username = st.session_state.username
    
    # Cargar disponibilidad actual de la BD
    db_data = get_disponibilidad(username)
    
    # Estructura para el grid
    dias = ['Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes', 'Sabado']
    horas = list(range(7, 21))
    
    # Convertir DB data a formato grid para checkboxes
    current_grid = {d: {h: False for h in horas} for d in dias}
    for row in db_data:
        d, hi, hf = row['dia'], row['hora_inicio'], row['hora_fin']
        if d in dias:
            for h in range(hi, hf):
                if h in horas:
                    current_grid[d][h] = True
    
    # Interfaz GRID
    cols = st.columns([0.8] + [1 for _ in dias])
    cols[0].markdown("**Hora**")
    for i, d in enumerate(dias):
        cols[i+1].markdown(f"**{d[:3]}**")
    
    # Estado del form
    new_grid = {d: {} for d in dias}
    
    with st.form("disponibilidad_form"):
        for h in horas:
            cols = st.columns([0.8] + [1 for _ in dias])
            cols[0].write(f"{h}:00")
            for i, d in enumerate(dias):
                new_grid[d][h] = cols[i+1].checkbox(
                    "", 
                    value=current_grid[d][h],
                    key=f"{d}_{h}",
                    label_visibility="collapsed"
                )
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.form_submit_button("💾 Guardar Disponibilidad", type="primary", use_container_width=True):
            # Convertir grid a bloques compactos para BD
            bloques_to_save = []
            
            for d in dias:
                # Algoritmo simple para encontrar rangos continuos
                hours_active = sorted([h for h, active in new_grid[d].items() if active])
                if not hours_active:
                    continue
                
                start = hours_active[0]
                prev = start
                
                for h in hours_active[1:]:
                    if h == prev + 1:
                        prev = h
                    else:
                        bloques_to_save.append({'dia': d, 'hora_inicio': start, 'hora_fin': prev + 1})
                        start = h
                        prev = h
                bloques_to_save.append({'dia': d, 'hora_inicio': start, 'hora_fin': prev + 1})
            
            # Guardar en BD
            if save_disponibilidad(username, bloques_to_save):
                st.success("✅ Disponibilidad actualizada correctamente en la base de datos")
            else:
                st.error("Error al guardar en base de datos")
    
    # Resumen visual
    if db_data:
        st.markdown("### Resumen Actual")
        st.dataframe(pd.DataFrame(db_data), use_container_width=True)
