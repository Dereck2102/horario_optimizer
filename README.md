# Optimizador de Horarios Académicos UCE

Sistema de optimización de horarios académicos para la Universidad Central del Ecuador (Facultad de Ingeniería y Ciencias Aplicadas), usando Google OR-Tools CP-SAT Solver y Streamlit.

## 🚀 Inicio Rápido

### Requisitos

- Python 3.11+
- Java (para lectura de PDFs con tabula-py)

### Instalación

```bash
# Clonar o descargar el proyecto
cd horario_optimizer

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar
streamlit run app.py
```

Acceder en: http://localhost:8501

### Credenciales de Prueba

| Rol         | Contraseña      | Descripción                        |
| ----------- | --------------- | ---------------------------------- |
| Profesional | `admin123`      | Generación de horarios oficiales   |
| Estudiante  | `estudiante123` | Optimización personal (futuro)     |
| Admin       | `superadmin123` | Configuración del sistema (futuro) |

## 📁 Estructura del Proyecto

```
horario_optimizer/
├── app.py                 # Dashboard principal con autenticación
├── requirements.txt       # Dependencias Python
├── Dockerfile            # Imagen Docker
├── docker-compose.yml    # Orquestación
│
├── core/                 # Lógica de negocio
│   ├── __init__.py      # Exports del módulo
│   ├── optimizer.py     # Motor CP-SAT OR-Tools ⭐
│   ├── data_loader.py   # Importadores y generadores
│   ├── validator.py     # Validador de restricciones
│   └── exporter.py      # Exportadores Excel/CSV
│
├── pages/               # Interfaces Streamlit
│   ├── 1_🎓_Profesional.py   # Módulo generación oficial ⭐
│   ├── 2_👨‍🎓_Estudiantil.py  # Módulo personal (futuro)
│   └── 3_⚙️_Configuracion.py # Administración (futuro)
│
├── docs/                # Documentación
├── data/                # Archivos subidos
├── templates/           # Plantillas Excel
└── test/                # Tests unitarios
```

## 🧪 Prueba Rápida

1. Login como **Profesional** (admin123)
2. Ir al módulo **1_🎓_Profesional** en el menú lateral
3. Tab "Cargar Datos":
   - Clic "Usar datos de ejemplo"
   - Clic "Generar aulas"
   - Clic "Generar docentes"
4. Tab "Optimizar":
   - Clic "Ejecutar Optimización"
   - Esperar 10-30 segundos
5. Tab "Exportar":
   - Clic "Descargar Excel"

## 🐳 Docker

```bash
# Construir y ejecutar
docker-compose up -d

# Acceder
http://localhost:8501
```

## 📖 Documentación Técnica

Ver [docs/ARQUITECTURA.md](docs/ARQUITECTURA.md) para documentación detallada sobre:

- Arquitectura del sistema
- Algoritmo de optimización CP-SAT
- Restricciones y objetivos
- Flujo de datos

## ✅ Características Implementadas

- ✅ Autenticación por roles
- ✅ Motor CP-SAT con restricciones duras y blandas
- ✅ Ventana horaria UCE: L-V 07:00-20:00, Sáb 07:00-13:00
- ✅ Asignación automática de aulas según capacidad
- ✅ Asignación automática de docentes según elegibilidad
- ✅ Distinción Lab/Aula para materias prácticas
- ✅ Validación de conflictos
- ✅ Exportación Excel/CSV
- ✅ Dockerización completa

## ⚠️ Limitaciones Actuales

- Módulo Estudiantil: Solo placeholder
- Persistencia: Todo en memoria (session_state)
- Monousuario: Un usuario a la vez

## 📝 Licencia

Proyecto académico - Universidad Central del Ecuador
