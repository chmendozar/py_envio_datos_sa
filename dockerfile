# Archivo: Dockerfile
FROM python:3.11-slim

# Establecer variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    DEBIAN_FRONTEND=noninteractive

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    xvfb \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libxss1 \
    libxtst6 \
    xdg-utils \
    --no-install-recommends && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Instalar Google Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Establecer directorio de trabajo
WORKDIR /app

# Crear directorios necesarios
RUN mkdir -p /app/logs /app/cliente/input /app/cliente/output && \
    chmod -R 777 /app/logs /app/cliente

# Copiar requirements.txt primero para aprovechar el cache de Docker
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY . .

# Configurar Chrome para funcionar en modo headless
ENV CHROME_BIN=/usr/bin/google-chrome-stable
ENV CHROME_PATH=/usr/bin/google-chrome-stable
ENV DISPLAY=:99

# Crear script de inicio
RUN echo '#!/bin/bash\nXvfb :99 -screen 0 1024x768x16 &\npython main.py' > /app/start.sh && \
    chmod +x /app/start.sh

# Verificar la instalación
RUN python -c "import sys; print(f'Python {sys.version}')" && \
    python -c "import selenium; print(f'Selenium {selenium.__version__}')" && \
    google-chrome-stable --version

# Exponer puerto si es necesario (opcional)
# EXPOSE 8000

# Comando de inicio
CMD ["/app/start.sh"]