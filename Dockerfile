FROM python:3.11-slim

# Instalar Java (para tabula-py si se necesita)
RUN apt-get update && apt-get install -y \
    default-jre \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Crear directorio para persistencia local
RUN mkdir -p /app/data

# Exponer Puerto 80 (Estándar HTTP para Cloudflare)
EXPOSE 80

# Comando de inicio en Puerto 80
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=80", "--server.address=0.0.0.0"]
