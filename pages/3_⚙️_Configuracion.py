import streamlit as st

st.set_page_config(page_title="Configuración", page_icon="⚙️", layout="wide")

# Verificar autenticación
if not st.session_state.get('authenticated'):
    st.error("❌ Acceso denegado. Inicie sesión primero.")
    st.stop()

if st.session_state.get('user_role') != 'Admin':
    st.warning("⚠️ Algunas funciones requieren rol de Administrador")

st.title("⚙️ Panel de Configuración")
st.markdown("Administración del sistema")

st.info("🚧 **Panel en construcción**")

st.markdown("""
### Próximamente podrás:

1. **Gestionar Aulas y Laboratorios**
   - Agregar/editar/eliminar espacios
   - Configurar capacidades
   - Asignar tipos (Aula/Lab)

2. **Administrar Docentes**
   - Registrar docentes
   - Asignar materias por docente
   - Configurar disponibilidad horaria

3. **Plantillas Descargables**
   - Formato para carga de clases
   - Formato para disponibilidad docente
   - Formato para catálogo de aulas

4. **Configuración Avanzada**
   - Parámetros del optimizador
   - Pesos de objetivos
   - Restricciones personalizadas

---

### Parámetros Actuales (solo lectura)

| Parámetro | Valor |
|-----------|-------|
| Bloques por día (L-V) | 13 |
| Bloques sábado | 6 |
| Duración bloque | 60 min |
| Hora inicio | 07:00 |
| Hora fin (L-V) | 20:00 |
| Hora fin (Sáb) | 13:00 |
""")

st.warning("⏳ Esta funcionalidad estará disponible próximamente.")
