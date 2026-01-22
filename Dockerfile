FROM python:3.11-slim

# Instalar dependencias del sistema necesarias para wkhtmltopdf
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    xvfb \
    libxrender1 \
    libxext6 \
    libfontconfig1 \
    fontconfig \
    libjpeg62-turbo \
    libx11-6 \
    ca-certificates \
    fonts-dejavu-core \
    xfonts-75dpi \
    xfonts-base \
    libssl3 \
    && rm -rf /var/lib/apt/lists/*

# Descargar e instalar wkhtmltopdf manualmente (no está en repositorios de Debian Trixie)
# Forzamos la instalación ignorando dependencias y creamos symlinks para compatibilidad
RUN wget -q https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-3/wkhtmltox_0.12.6.1-3.bullseye_amd64.deb -O /tmp/wkhtmltopdf.deb && \
    apt-get update && \
    dpkg --force-depends --force-all -i /tmp/wkhtmltopdf.deb || true && \
    # Crear symlink para libssl1.1 -> libssl3 (compatibilidad)
    mkdir -p /usr/lib/x86_64-linux-gnu && \
    (ln -sf /usr/lib/x86_64-linux-gnu/libssl.so.3 /usr/lib/x86_64-linux-gnu/libssl.so.1.1 || true) && \
    (ln -sf /usr/lib/x86_64-linux-gnu/libcrypto.so.3 /usr/lib/x86_64-linux-gnu/libcrypto.so.1.1 || true) && \
    # Marcar el paquete como instalado correctamente para evitar que apt-get lo elimine
    dpkg --configure -a || true && \
    rm /tmp/wkhtmltopdf.deb && \
    rm -rf /var/lib/apt/lists/* && \
    wkhtmltopdf --version

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=8080
EXPOSE 8080

CMD ["python", "app.py"]
