# Guía de Instalación

## Requisitos Previos

### Software Necesario

- **Python 3.11+** (recomendado 3.11.x)
- **Java 8+** (requerido por tabula-py para leer PDFs)
- **pip** (gestor de paquetes Python)

### Verificar Instalación

```bash
# Verificar Python
python --version
# Debería mostrar: Python 3.11.x

# Verificar Java
java -version
# Debería mostrar: java version "1.8.x" o superior

# Verificar pip
pip --version
```

---

## Instalación Local

### Paso 1: Obtener el Proyecto

```bash
# Opción A: Clonar repositorio
git clone <url-del-repositorio>
cd horario_optimizer

# Opción B: Descargar y descomprimir
# Descargar ZIP y extraer
cd horario_optimizer
```

### Paso 2: Crear Entorno Virtual (Recomendado)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

### Paso 3: Instalar Dependencias

```bash
pip install -r requirements.txt
```

### Paso 4: Ejecutar

```bash
streamlit run app.py
```

### Paso 5: Acceder

Abrir navegador en: http://localhost:8501

---

## Instalación con Docker

### Requisitos

- Docker Desktop instalado y corriendo

### Paso 1: Construir y Ejecutar

```bash
docker-compose up -d
```

### Paso 2: Acceder

Abrir navegador en: http://localhost:8501

### Comandos Útiles

```bash
# Ver logs
docker-compose logs -f

# Detener
docker-compose down

# Reconstruir
docker-compose up -d --build
```

---

## Solución de Problemas

### Error: "No module named 'ortools'"

```bash
pip install ortools==9.8.3296
```

### Error: "Java not found" (tabula-py)

1. Instalar Java JRE o JDK
2. Agregar Java al PATH del sistema
3. Reiniciar terminal

### Error: "ModuleNotFoundError: No module named 'core'"

Asegúrate de ejecutar desde la raíz del proyecto:

```bash
cd horario_optimizer
streamlit run app.py
```

### Error de puertos

Si el puerto 8501 está ocupado:

```bash
streamlit run app.py --server.port 8502
```

### Página en blanco después de login

1. Verificar que existen las páginas en `pages/`
2. Los nombres deben tener el formato `N_emoji_nombre.py`
3. Reiniciar Streamlit

---

## Checklist de Instalación

- [ ] Python 3.11+ instalado
- [ ] Java instalado (para PDFs)
- [ ] Dependencias instaladas (`pip install -r requirements.txt`)
- [ ] Sistema ejecutándose en http://localhost:8501
- [ ] Login exitoso con Profesional/admin123
- [ ] Generación de horario de ejemplo funciona
- [ ] Descarga de Excel funciona

---

## Estructura de Carpetas Requerida

Antes de ejecutar, verificar que existan estas carpetas:

```
horario_optimizer/
├── core/           # Debe contener los módulos Python
├── pages/          # Debe contener las páginas Streamlit
├── data/           # Para archivos subidos (puede estar vacía)
├── templates/      # Para plantillas (puede estar vacía)
└── docs/           # Documentación
```

Si faltan carpetas, créalas:

```bash
mkdir data templates test
```

---

## Verificación de Funcionamiento

1. **Login**: Usar credenciales `Profesional / admin123`
2. **Cargar datos**: En Módulo Profesional, usar datos de ejemplo
3. **Optimizar**: Ejecutar optimización
4. **Exportar**: Descargar Excel

Si todos estos pasos funcionan, la instalación está completa.
