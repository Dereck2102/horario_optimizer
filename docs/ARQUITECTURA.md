# Arquitectura del Sistema

## Propósito

Sistema web de optimización de horarios académicos para la Universidad Central del Ecuador (Facultad de Ingeniería y Ciencias Aplicadas), usando Google OR-Tools CP-SAT Solver y Streamlit.

### Problema que Resuelve

- Generación manual de horarios toma semanas
- Conflictos frecuentes (docentes, aulas, sobrecupos)
- Subutilización de espacios físicos
- Falta de herramientas que consideren restricciones complejas de la UCE

---

## Stack Tecnológico

| Componente             | Tecnología                    |
| ---------------------- | ----------------------------- |
| Backend                | Python 3.11                   |
| Framework Web          | Streamlit                     |
| Motor de Optimización  | Google OR-Tools CP-SAT Solver |
| Procesamiento de Datos | pandas, openpyxl              |
| Importación PDF        | tabula-py (requiere Java)     |
| Despliegue             | Docker + docker-compose       |

---

## Módulos Principales

### 1. app.py (Dashboard Principal)

**Responsabilidad**: Punto de entrada con sistema de autenticación por roles

**Roles de Usuario**:

- **Profesional** (admin123): Genera horarios oficiales de la facultad
- **Estudiante** (estudiante123): Optimiza horario personal (en desarrollo)
- **Admin** (superadmin123): Configuración global (en desarrollo)

**Estado de Sesión** (st.session_state):

- `authenticated`: bool
- `user_role`: str (Profesional/Estudiante/Admin)
- `horario_generado`: DataFrame
- `clases_df`, `aulas_df`, `docentes_df`: DataFrames

---

### 2. core/optimizer.py (Motor de Optimización)

**Clase Principal**: `HorarioOptimizer`

**Algoritmo**: Constraint Programming - Satisfiability (CP-SAT) de Google OR-Tools

**Variables de Decisión** (por cada clase):

- `start`: Timeslot de inicio (0-70: L-V 13 bloques + Sáb 6 bloques)
- `room`: Índice del aula asignada (0 a num_aulas-1)
- `teacher`: Índice del docente asignado (0 a num_docentes-1)
- `interval`: Intervalo de tiempo (start, duration, end)

**Restricciones Duras** (DEBEN cumplirse):

1. **No-overlap de aulas**: Misma aula no puede tener 2 clases simultáneas
2. **No-overlap de docentes**: Mismo docente no puede dar 2 clases simultáneas
3. **Capacidad**: `inscritos <= capacidad_aula`
4. **Tipo de espacio**: Materias de laboratorio requieren espacios tipo "Lab"
5. **Elegibilidad docente**: Docente solo puede dictar materias en su lista

**Restricciones Blandas** (optimizar):

- Minimizar desperdicio de capacidad: `(capacidad - inscritos)`
- Peso configurable por objetivo

**Ventana Horaria UCE**:

- Lunes a Viernes: 07:00 - 20:00 (13 bloques de 60 min)
- Sábado: 07:00 - 13:00 (6 bloques de 60 min)
- Total: 71 timeslots semanales

**Método `optimize()`**:

```python
def optimize(clases: pd.DataFrame, aulas: pd.DataFrame, docentes: pd.DataFrame) -> Dict:
    # Retorna:
    {
        'status': 'success' | 'failed' | 'error',
        'optimal': bool,  # True si solución óptima
        'schedule': pd.DataFrame,  # Horario generado
        'metrics': {'total_clases', 'aulas_utilizadas', 'promedio_ocupacion'},
        'solver_stats': {'wall_time', 'conflicts', 'branches'}
    }
```

**Configuración**:

```python
config = {
    'weights': {
        'gaps': 10,                # Minimizar huecos en horarios
        'capacity_waste': 5,       # Optimizar uso de espacios
        'teacher_balance': 3,      # Balancear carga docente
        'building': 2              # Compactar por edificio
    },
    'time_limit_seconds': 120,
    'require_lab_for_practices': True
}
```

---

### 3. core/data_loader.py (Importadores)

**Clase Principal**: `DataLoader`

**Métodos Clave**:

1. **`load_oferta_demanda_excel(file_path)`**
   - Lee archivos Excel del SIIU (Sistema Integrado de Información Universitaria)
   - Columnas esperadas: Paralelo, Asignatura, Nivel, Estudiantes registrados
   - Infiere duración automáticamente:
     - Materias con "programacion", "lab", "algoritmo" → 2 bloques (120 min)
     - Resto → 1 bloque (60 min)
   - Infiere tipo de espacio: Lab o Aula

2. **`create_default_aulas(count=50)`**
   - Genera catálogo de espacios físicos
   - 12 laboratorios (LAB1-LAB12)
   - 38 aulas (A1-A38)
   - Capacidad default: 25 estudiantes
   - Distribución en 3 edificios

3. **`create_default_docentes(materias, count=30)`**
   - Genera 30 docentes ficticios
   - Asigna elegibilidad automática (cada docente puede dictar 1/3 de materias)

**DataFrames Generados**:

```python
# clases_df
columns = ['id', 'paralelo', 'materia', 'nivel', 'inscritos', 'duracion_bloques', 'tipo_espacio']

# aulas_df
columns = ['id', 'nombre', 'tipo', 'capacidad', 'edificio']

# docentes_df
columns = ['id', 'nombre', 'materias_puede_dictar']  # materias_puede_dictar es lista
```

---

### 4. core/validator.py (Validador)

**Clase**: `HorarioValidator`

**Método Principal**: `validate_horario(horario: pd.DataFrame)`

**Validaciones**:

1. Conflictos de aulas (mismo espacio, mismo día, superposición horaria)
2. Conflictos de docentes (mismo docente, mismo día, superposición)
3. Capacidad (inscritos > capacidad del aula)
4. Ventana horaria (clases fuera del rango permitido)
5. Carga docente (warnings si >40h o <10h semanales)

**Retorno**:

```python
{
    'valid': bool,
    'errors': ['error1', 'error2'],      # Errores críticos
    'warnings': ['warning1', 'warning2']  # Advertencias
}
```

---

### 5. core/exporter.py (Exportadores)

**Clase**: `HorarioExporter`

**Métodos**:

1. **`export_to_excel(horario)`**
   - Genera archivo .xlsx con múltiples pestañas:
     - "Horario Completo": Todas las clases
     - Una pestaña por paralelo (ej: "SI1-001")
     - Una pestaña por docente
   - Usa `openpyxl` engine

2. **`export_to_csv(horario)`**
   - Formato CSV simple para importar a otros sistemas

---

## Flujo de Datos

```
1. Usuario autenticado → app.py
2. Navega a Módulo Profesional → pages/1_🎓_Profesional.py
3. Carga/genera datos → DataLoader → st.session_state
4. Configura parámetros → config dict
5. Ejecuta optimización → HorarioOptimizer.optimize()
   ├── Crea variables CP-SAT
   ├── Añade restricciones
   └── Resuelve (CP-SAT Solver)
6. Valida resultado → HorarioValidator
7. Exporta → HorarioExporter
8. Usuario descarga Excel/CSV
```

---

## Datos de Entrada Esperados

### Formato Excel SIIU (Oferta/Demanda)

Columnas mínimas:

- **Paralelo**: Código (ej: SI1-001)
- **Asignatura**: Nombre materia (ej: PROGRAMACION I)
- **Nivel**: PRIMERO, SEGUNDO, etc.
- **Estudiantes registrados**: Número entero

El sistema infiere automáticamente:

- `duracion_bloques`: 1 o 2 según keywords en nombre
- `tipo_espacio`: Lab o Aula

---

## Dependencias Críticas

| Dependencia     | Versión  | Propósito                        |
| --------------- | -------- | -------------------------------- |
| ortools         | 9.8.3296 | Motor de optimización CP-SAT ⭐  |
| streamlit       | 1.31.0   | Framework web ⭐                 |
| pandas          | 2.2.0    | Manipulación de datos ⭐         |
| openpyxl        | 3.1.2    | Lectura/escritura Excel          |
| tabula-py       | 2.9.0    | Importación PDFs (requiere Java) |
| Pillow          | 10.2.0   | Procesamiento imágenes           |
| plotly          | 5.18.0   | Gráficos                         |
| python-dateutil | 2.8.2    | Manejo fechas                    |

---

## Preguntas Frecuentes

**Q: ¿Por qué usa CP-SAT y no otro algoritmo?**
A: CP-SAT es ideal para problemas de scheduling con restricciones duras/blandas. Es más eficiente que algoritmos genéticos para este dominio.

**Q: ¿Qué pasa si no hay solución factible?**
A: El solver retorna 'status': 'failed'. Causas comunes: muy pocas aulas, docentes sin materias asignables, capacidad insuficiente.

**Q: ¿Cómo se manejan materias de 3 horas?**
A: Se dividen en bloques de 60 min. Una materia de 3h puede ser 2h un día + 1h otro día (lo decide el solver).

**Q: ¿Se puede forzar que una materia sea en cierto horario?**
A: Actualmente no. Requeriría añadir restricciones de "pinning" al solver.

---

## Comandos de Depuración

```python
# Ver estado de sesión en Streamlit
import streamlit as st
st.write(st.session_state)

# Modo debug del solver
solver.parameters.log_search_progress = True

# Ver restricciones del modelo
print(model.Proto())
```

---

## Ampliaciones Futuras Sugeridas

1. Preferencias horarias docentes (upload Excel)
2. Base de datos SQLite/PostgreSQL
3. Restricciones pedagógicas (días libres, max horas seguidas)
4. Análisis comparativo de soluciones
5. API REST para integración con SIIU
6. Optimización multi-objetivo (Pareto front)
7. Visualización de horarios tipo calendario
8. Sistema de notificaciones (email a docentes)
