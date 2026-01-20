import streamlit as st

st.set_page_config(page_title="Módulo Estudiantil", page_icon="👨‍🎓", layout="wide")

# Verificar autenticación
if not st.session_state.get('authenticated'):
    st.error("❌ Acceso denegado. Inicie sesión primero.")
    st.stop()

st.title("👨‍🎓 Módulo Estudiantil")
st.markdown("Optimización de horario personal")

st.info("🚧 **Módulo en construcción**")

st.markdown("""
### Próximamente podrás:

1. **Importar tu horario actual** desde el SIIU
2. **Configurar tus preferencias**:
   - Días libres preferidos
   - Horarios matutinos/vespertinos
   - Máximo de horas seguidas
3. **Optimizar tu horario** sin conflictos
4. **Comparar antes/después** de la optimización
5. **Descargar** tu horario optimizado

---

### ¿Cómo funcionará?

```
1. Descarga tu horario del SIIU (PDF o Excel)
2. Súbelo a este sistema
3. Configura tus preferencias personales
4. El sistema generará un horario optimizado
5. Descarga el resultado
```
""")

st.warning("⏳ Esta funcionalidad estará disponible próximamente.")
