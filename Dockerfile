FROM python:3.11-slim

# Instalar dependencias del sistema necesarias para wkhtmltopdf
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    xvfb \
    libxrender1 \
    libxext6 \
    libfontconfig1 \
    libjpeg62-turbo \
    libx11-6 \
    ca-certificates \
    fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

# Descargar e instalar wkhtmltopdf manualmente (no está en repositorios de Debian Trixie)
RUN wget -q https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-3/wkhtmltox_0.12.6.1-3.bullseye_amd64.deb -O /tmp/wkhtmltopdf.deb && \
    apt-get update && \
    dpkg -i /tmp/wkhtmltopdf.deb || apt-get install -y -f && \
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
