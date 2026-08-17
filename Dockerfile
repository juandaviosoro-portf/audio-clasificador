FROM python:3.11-slim

# Instalar FFmpeg (requerido por Whisper)
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar requirements primero (para aprovechar cache de Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del proyecto
COPY . .

# Crear carpetas necesarias
RUN mkdir -p uploads database

EXPOSE 5000

CMD ["python", "app.py"]
