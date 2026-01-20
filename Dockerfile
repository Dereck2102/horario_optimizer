FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    default-jre \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar aplicacion
COPY . .

# Crear directorio de datos
RUN mkdir -p /app/data

# Exponer puerto
EXPOSE 8501

# Variables de entorno
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true

# Healthcheck
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Comando de inicio
CMD ["streamlit", "run", "app.py"]
