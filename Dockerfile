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
# Instalamos libssl1.1 desde Debian Bullseye (compatible) ya que wkhtmltopdf lo requiere
RUN echo "deb http://deb.debian.org/debian bullseye main" > /etc/apt/sources.list.d/bullseye.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends -t bullseye libssl1.1 && \
    wget -q https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-3/wkhtmltox_0.12.6.1-3.bullseye_amd64.deb -O /tmp/wkhtmltopdf.deb && \
    dpkg -i /tmp/wkhtmltopdf.deb && \
    rm /tmp/wkhtmltopdf.deb && \
    rm /etc/apt/sources.list.d/bullseye.list && \
    rm -rf /var/lib/apt/lists/* && \
    wkhtmltopdf --version

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=8080
EXPOSE 8080

CMD ["python", "app.py"]
