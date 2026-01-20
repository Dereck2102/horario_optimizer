# Horarios UCE - Sistema de Optimizacion

Sistema de gestion y optimizacion de horarios academicos para la Universidad Central del Ecuador.

## Caracteristicas

- **Generacion optimizada** de horarios usando OR-Tools
- **Roles diferenciados**: Admin, Profesor, Estudiante
- **Soporte PDF/Excel** para carga de datos
- **Dashboard** con estadisticas y graficas
- **Publicacion** de horarios oficiales

## Instalacion Local

```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/horarios-uce.git
cd horarios-uce

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar
streamlit run app.py
```

## Docker

```bash
# Construir y ejecutar
docker-compose up -d

# Acceder en http://localhost:8501
```

## Despliegue en AWS

### Opcion 1: ECS (Fargate)

1. Crear repositorio en ECR
2. Crear cluster en ECS
3. Configurar secretos en GitHub:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
4. Push a `main` para desplegar automaticamente

### Opcion 2: EC2

1. Crear instancia EC2 con Docker instalado
2. Configurar secretos en GitHub:
   - `EC2_HOST`
   - `EC2_USER`
   - `EC2_SSH_KEY`
3. Modificar workflow para usar `deploy-ec2`

## Configuracion CloudFlare

1. Agregar dominio en CloudFlare
2. Crear registro A apuntando a IP de AWS
3. Habilitar SSL/TLS (Full)
4. Opcionalmente habilitar proxy para CDN

## Credenciales por Defecto

| Usuario     | Contraseña | Rol        |
| ----------- | ---------- | ---------- |
| admin       | admin123   | Admin      |
| profesor1   | prof123    | Profesor   |
| estudiante1 | est123     | Estudiante |

**Importante**: Cambiar credenciales antes de produccion.

## Estructura

```
horarios-uce/
├── app.py              # Aplicacion principal
├── pages/              # Modulos de paginas
│   ├── profesional.py  # Generacion (Admin)
│   ├── usuarios.py     # Gestion usuarios (Admin)
│   ├── dashboard.py    # Estadisticas
│   ├── disponibilidad.py  # Disponibilidad (Profesor)
│   ├── mi_horario.py   # Horario (Estudiante)
│   └── configuracion.py
├── core/               # Logica de negocio
│   ├── optimizer.py    # Motor de optimizacion
│   ├── data_loader.py  # Carga de datos
│   └── ...
├── data/               # Datos persistentes (JSON)
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Licencia

MIT License
